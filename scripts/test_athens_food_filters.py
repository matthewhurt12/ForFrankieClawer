#!/usr/bin/env python3
"""
Regression checks for the expanded Athens food recommender.

This is intentionally local-only. It does not call Apify or Google; it checks
that the large CSV still filters predictably before live verification.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import athens_food


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "ATHENS_FOOD_FILTER_TEST_LAST.md"


@dataclass
class TestResult:
    name: str
    ok: bool
    detail: str


def args_for(**overrides: object) -> argparse.Namespace:
    base = {
        "command": "recommend",
        "mood": "",
        "query": "",
        "cuisine": "",
        "area": "",
        "speed": "",
        "exclude_cuisine": [],
        "exclude_area": [],
        "exclude_speed": [],
        "exclude_tag": [],
        "exclude": [],
        "max_price": None,
        "min_rating": None,
        "limit": 8,
        "include_to_go": False,
        "include_closed": False,
        "no_bar_food": False,
        "no_fast_food": False,
        "random": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def norm(value: str) -> str:
    value = re.sub(r"['’]s\b", "s", value.lower())
    value = re.sub(r"[^a-z0-9]+", "", value)
    if value.endswith("bar") and len(value) > 6:
        value = value[:-3]
    return value


def check_row_volume() -> TestResult:
    rows = athens_food.load_restaurants()
    imports = [r for r in rows if r.category == "Directory Import"]
    ok = len(rows) >= 400 and len(imports) >= 250
    return TestResult("expanded row volume", ok, f"{len(rows)} rows, {len(imports)} directory imports")


def check_duplicate_pressure() -> TestResult:
    rows = athens_food.load_restaurants()
    counts: dict[str, int] = {}
    names: dict[str, list[str]] = {}
    for row in rows:
        key = norm(row.name)
        counts[key] = counts.get(key, 0) + 1
        names.setdefault(key, []).append(row.name)
    duplicates = {key: value for key, value in counts.items() if value > 1}
    allowed = {"paloma", "worldfamous", "buvez"}
    unexpected = {key: names[key] for key in duplicates if key not in allowed}
    ok = not unexpected
    detail = "none" if ok else "; ".join(f"{key}: {', '.join(value)}" for key, value in sorted(unexpected.items())[:8])
    return TestResult("duplicate pressure", ok, detail)


def check_default_prefers_rated() -> TestResult:
    matches = athens_food.recommend(args_for(limit=5))
    top = matches[0].restaurant if matches else None
    ok = bool(top and top.rating is not None and top.category != "Directory Import")
    detail = f"{top.name} ({top.category})" if top else "no matches"
    return TestResult("default prefers rated rows", ok, detail)


def check_no_fast_no_bar() -> TestResult:
    matches = athens_food.recommend(
        args_for(
            mood="lunch hot fresh",
            no_fast_food=True,
            no_bar_food=True,
            exclude=["taco", "sushi"],
            limit=12,
        )
    )
    bad = []
    blocked_names = {"maepole", "birdies", "last resort"}
    for match in matches:
        r = match.restaurant
        text = r.text
        if athens_food.is_fast_food_like(r) or athens_food.is_bar_food_like(r):
            bad.append(f"{r.name}: fast/bar-like")
        if "taco" in text or "sushi" in text:
            bad.append(f"{r.name}: excluded text")
        if r.name.lower() in blocked_names:
            bad.append(f"{r.name}: known bad fit for this scenario")
    ok = bool(matches) and not bad
    detail = f"top={matches[0].restaurant.name if matches else 'none'}; " + ("; ".join(bad) if bad else "all checked")
    return TestResult("strict lunch filters", ok, detail)


def check_query_precision() -> TestResult:
    matches = athens_food.recommend(args_for(query="korean bbq", limit=8))
    bad = [m.restaurant.name for m in matches if "korean" not in m.restaurant.text or "bbq" not in m.restaurant.text]
    ok = bool(matches) and not bad
    detail = f"matches={', '.join(m.restaurant.name for m in matches[:5])}" if ok else f"bad={', '.join(bad)}"
    return TestResult("specific query precision", ok, detail)


def check_closed_suppressed() -> TestResult:
    blocked = ["birdies", "grit", "home.made", "weaver d's"]
    leaked = []
    for name in blocked:
        matches = athens_food.recommend(args_for(query=name, limit=3))
        if matches:
            leaked.append(name)
    ok = not leaked
    return TestResult("closed rows suppressed", ok, "none leaked" if ok else ", ".join(leaked))


def run_checks() -> list[TestResult]:
    return [
        check_row_volume(),
        check_duplicate_pressure(),
        check_default_prefers_rated(),
        check_no_fast_no_bar(),
        check_query_precision(),
        check_closed_suppressed(),
    ]


def write_report(results: list[TestResult]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Athens Food Filter Test",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]
    for result in results:
        lines.append(f"- **{'OK' if result.ok else 'FAIL'}:** {result.name} - {result.detail}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    results = run_checks()
    write_report(results)
    for result in results:
        print(f"{'OK' if result.ok else 'FAIL'}: {result.name} - {result.detail}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
