#!/usr/bin/env python3
"""
Verified "go now" Athens restaurant picker.

This is the safer final-answer path for live recommendations. It first gets
spreadsheet candidates, then uses the Apify Google search actor to reject
closed places and restaurants that violate Matthew's conditions.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import athens_food
import athens_food_google_check as google_check


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "ATHENS_FOOD_GO_NOW_LAST.md"
CLOSED_STATUSES = {"CLOSED_OR_INACTIVE", "CLOSED_NOW", "LIKELY_CLOSED_NOW", "NO_RESULTS"}


def build_food_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        command="recommend",
        mood=args.mood,
        query=args.query,
        cuisine=args.cuisine,
        area=args.area,
        speed=args.speed,
        max_price=args.max_price,
        min_rating=args.min_rating,
        exclude_cuisine=args.exclude_cuisine,
        exclude_area=args.exclude_area,
        exclude_speed=args.exclude_speed,
        exclude_tag=args.exclude_tag,
        exclude=args.exclude,
        limit=args.check_limit,
        include_to_go=args.include_to_go,
        include_closed=False,
        no_bar_food=args.no_bar_food,
        no_fast_food=args.no_fast_food,
        random=False,
    )


def verified_pick(
    matches: list[athens_food.Match],
    results: dict[str, google_check.CheckResult],
) -> tuple[athens_food.Match | None, str]:
    for match in matches:
        result = results.get(match.restaurant.name)
        if result and result.eligible and result.status == "LIKELY_OPEN_OR_HAS_HOURS":
            return match, "verified_open"
    for match in matches:
        result = results.get(match.restaurant.name)
        if result and result.eligible and result.status == "UNKNOWN":
            return match, "needs_manual_hours_check"
    return None, "none"


def render_report(
    matches: list[athens_food.Match],
    results: dict[str, google_check.CheckResult],
    pick: athens_food.Match | None,
    pick_status: str,
    args: argparse.Namespace,
) -> str:
    lines = [
        "# Athens Food Go-Now Check",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Mood:** {args.mood or 'any'}",
        f"**Final Conditions:** no_fast_food={args.no_fast_food}, no_bar_food={args.no_bar_food}, excludes={', '.join(google_check.arg_terms(args.exclude)) or 'none'}",
        "",
    ]
    if pick:
        r = pick.restaurant
        check = results.get(r.name)
        lines.extend(
            [
                f"## Verified Pick: {r.name}",
                "",
                f"- **Cuisine / Area:** {r.cuisine or 'unknown'} / {r.area or 'unknown'}",
                f"- **Price / Speed:** {athens_food.money(r.price)} / {r.speed or 'unknown'}",
                f"- **Sheet Rating:** {athens_food.rating_text(r.rating)}",
                f"- **Google Status:** {check.status if check else 'not checked'}",
                f"- **Verification:** {pick_status}",
                f"- **Why:** {', '.join(pick.reasons[:6])}.",
                f"- **Order idea:** {r.got or 'not listed'}",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## No Verified Pick",
                "",
                "Every checked candidate was closed, uncertain, or violated the final conditions.",
                "",
            ]
        )

    lines.extend(["## Checked Candidates", ""])
    for match in matches:
        r = match.restaurant
        check = results.get(r.name)
        status = check.status if check else "NOT_CHECKED"
        blocks = ", ".join(check.disqualifiers or []) if check and check.disqualifiers else "none"
        eligible = "yes" if check and check.eligible else "no"
        if status in CLOSED_STATUSES:
            reason = "closed/inactive signal"
        elif blocks != "none":
            reason = blocks
        elif check and check.eligible:
            reason = "passes final conditions"
        else:
            reason = "not enough verification"
        lines.extend(
            [
                f"### {r.name}",
                "",
                f"- **Google Status:** {status}",
                f"- **Eligible:** {eligible}",
                f"- **Reason:** {reason}",
                f"- **Local Fit:** {r.cuisine or 'unknown'} / {r.area or 'unknown'} / {athens_food.money(r.price)}",
                "",
            ]
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pick an Athens restaurant after Google condition verification.")
    parser.add_argument("--mood", default="", help="Mood like lunch hot fresh, date night, vegetarian.")
    parser.add_argument("--query", default="", help="Free-text search across notes, order, tags, and cuisine.")
    parser.add_argument("--cuisine", default="", help="Cuisine filter.")
    parser.add_argument("--area", default="", help="Area filter.")
    parser.add_argument("--speed", default="", help="Speed filter.")
    parser.add_argument("--exclude-cuisine", action="append", default=[], help="Exclude cuisine(s), comma-separated or repeated.")
    parser.add_argument("--exclude-area", action="append", default=[], help="Exclude area(s), comma-separated or repeated.")
    parser.add_argument("--exclude-speed", action="append", default=[], help="Exclude speed(s), comma-separated or repeated.")
    parser.add_argument("--exclude-tag", action="append", default=[], help="Exclude derived tag(s), comma-separated or repeated.")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude text locally and in the Google final check.")
    parser.add_argument("--no-bar-food", action="store_true", help="Exclude bar/pub/brewery locally and through Google final check.")
    parser.add_argument("--no-fast-food", action="store_true", help="Exclude fast food, fast casual, chain, counter-service, and fast/quick-service rows.")
    parser.add_argument("--max-price", type=float, help="Maximum average price per meal.")
    parser.add_argument("--min-rating", type=float, help="Minimum star rating.")
    parser.add_argument("--include-to-go", action="store_true", help="Include unrated to-go/try-list rows.")
    parser.add_argument("--check-limit", type=int, default=8, help="Number of local candidates to verify online.")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    food_args = build_food_args(args)
    matches = athens_food.recommend(food_args)
    if not matches:
        print("No local candidates matched those conditions.")
        return 1

    names = [match.restaurant.name for match in matches]
    items = google_check.run_actor(names)
    grouped = google_check.group_items_by_name(names, items)
    check_args = argparse.Namespace(no_fast_food=args.no_fast_food, no_bar_food=args.no_bar_food, exclude=args.exclude)
    checks = [google_check.analyze(name, grouped.get(name, []), check_args) for name in names]
    results = {result.name: result for result in checks}
    pick, pick_status = verified_pick(matches, results)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(matches, results, pick, pick_status, args), encoding="utf-8")
    if pick:
        print(f"Verified pick: {pick.restaurant.name} ({pick_status})")
    else:
        print("No verified pick after final Google condition check.")
    for result in checks:
        blocks = f" blocked={'; '.join(result.disqualifiers)}" if result.disqualifiers else ""
        print(f"{result.name}: {result.status} eligible={'yes' if result.eligible else 'no'}{blocks}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0 if pick else 2


if __name__ == "__main__":
    raise SystemExit(main())
