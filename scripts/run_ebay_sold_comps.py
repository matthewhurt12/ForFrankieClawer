#!/usr/bin/env python3
"""
Run the eBay sold listings Apify actor for exact model candidates only.

This script intentionally refuses broad keywords. Sold comps cost money and are
only useful after the Deal Desk has identified exact models.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arbitrage_logic import CLEAN_SOLD_COMPS_CSV, detect_exact_model  # noqa: E402
from clean_ebay_sold_comps import clean_items, write_clean_csv, write_summary  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "marketplace_sources.json"
RAW_DIR = ROOT / "data" / "sold_comps"
RUN_REPORT = ROOT / "reports" / "EBAY_SOLD_COMPS_RUN_LAST.md"
API_BASE = "https://api.apify.com/v2"

SAFE_FIELDS = [
    "title",
    "soldPrice",
    "soldCurrency",
    "shippingPrice",
    "shippingCurrency",
    "totalPrice",
    "endedAt",
    "itemId",
    "url",
    "keyword",
    "categoryId",
    "category",
    "shippingType",
    "scrapedAt",
    "updatedAt",
]

GENERIC_BLOCKLIST = {
    "receiver",
    "stereo",
    "vintage stereo",
    "vintage receiver",
    "pioneer receiver",
    "marantz receiver",
    "marantz stereo",
    "technics turntable",
    "cassette deck",
    "turntable",
    "record player",
    "vintage computer",
    "game console",
    "nintendo",
    "apple computer",
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("ebay_sold_comps", {})


def normalize_keywords(args: argparse.Namespace) -> list[str]:
    keywords = list(args.keywords or [])
    if args.keyword_file:
        lines = args.keyword_file.read_text(encoding="utf-8-sig").splitlines()
        keywords.extend(line.strip() for line in lines if line.strip() and not line.strip().startswith("#"))

    normalized: list[str] = []
    seen = set()
    for keyword in keywords:
        clean = " ".join(keyword.split())
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key)
            normalized.append(clean)
    return normalized


def validate_keywords(keywords: list[str], allow_low_confidence: bool) -> None:
    if not keywords:
        raise ValueError("Provide at least one exact model keyword.")
    if len(keywords) > 6:
        raise ValueError("The eBay sold comps actor accepts at most 6 keywords per run.")

    rejected: list[str] = []
    for keyword in keywords:
        model = detect_exact_model(keyword)
        if keyword.lower() in GENERIC_BLOCKLIST:
            rejected.append(f"{keyword} (generic broad search)")
        elif not model.exact and not allow_low_confidence:
            rejected.append(f"{keyword} (no exact model detected)")

    if rejected:
        detail = "\n".join(f"- {item}" for item in rejected)
        raise ValueError(
            "Refusing broad or non-exact sold-comp keywords.\n"
            f"{detail}\n"
            "Use exact models only, or pass --allow-low-confidence if Matthew explicitly approves."
        )


def actor_input(keywords: list[str], actor_config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "keywords": keywords,
        "daysToScrape": args.days or int(actor_config.get("days_to_scrape", 30)),
        "count": args.count or int(actor_config.get("count_per_keyword", 5)),
        "categoryId": "0",
        "subcategoryId": "",
        "ebaySite": "ebay.com",
        "sortOrder": "endedRecently",
        "itemLocation": "default",
        "itemCondition": "any",
        "detailedSearch": False,
    }


def sanitize_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{field: item.get(field) for field in SAFE_FIELDS if field in item} for item in items]


def run_actor(payload: dict[str, Any], actor_id: str, token: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    start = requests.post(f"{API_BASE}/acts/{actor_id}/runs", headers=headers, json=payload, timeout=60)
    if start.status_code not in [200, 201]:
        raise RuntimeError(f"Actor start failed: {start.status_code} {start.text[:500]}")

    run = start.json()["data"]
    run_id = run["id"]
    terminal = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}
    while True:
        info = requests.get(f"{API_BASE}/actor-runs/{run_id}", headers=headers, timeout=30)
        info.raise_for_status()
        run = info.json()["data"]
        status = run["status"]
        print(f"Status: {status}")
        if status in terminal:
            break
        time.sleep(10)

    items: list[dict[str, Any]] = []
    dataset_id = run.get("defaultDatasetId")
    if dataset_id:
        data = requests.get(f"{API_BASE}/datasets/{dataset_id}/items?clean=true", headers=headers, timeout=60)
        data.raise_for_status()
        items = data.json()
    return run, items


def clean_output(raw_path: Path, clean_path: Path) -> tuple[int, int]:
    raw_items = json.loads(raw_path.read_text(encoding="utf-8-sig"))
    rows = clean_items(raw_items)
    write_clean_csv(rows, clean_path)
    write_summary(rows, raw_path, clean_path)
    valid = sum(1 for row in rows if row.get("comp_classification") == "FULL_UNIT")
    return len(rows), valid


def merge_clean_csv(input_csv: Path, target_csv: Path = ROOT / CLEAN_SOLD_COMPS_CSV) -> tuple[int, int]:
    fields = [
        "model",
        "brand",
        "category",
        "title",
        "sold_price",
        "sold_date",
        "condition",
        "url",
        "comp_classification",
        "reason",
    ]
    rows: list[dict[str, str]] = []
    seen = set()

    for path in [target_csv, input_csv]:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                fixed = {(key or "").replace("\ufeff", "").strip('"'): value for key, value in row.items()}
                key = tuple(fixed.get(field, "") for field in ["model", "title", "sold_price", "url", "comp_classification"])
                if key in seen:
                    continue
                seen.add(key)
                rows.append({field: fixed.get(field, "") for field in fields})

    target_csv.parent.mkdir(parents=True, exist_ok=True)
    with target_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    valid = sum(1 for row in rows if row.get("comp_classification") == "FULL_UNIT")
    return len(rows), valid


def write_run_report(
    keywords: list[str],
    payload: dict[str, Any],
    run: dict[str, Any],
    raw_path: Path,
    clean_path: Path | None,
    merged_counts: tuple[int, int] | None,
) -> None:
    usage = run.get("usageTotalUsd") or run.get("usageUsd") or (run.get("usage") or {}).get("totalUsd")
    lines = [
        "# eBay Sold Comps Run",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Actor Status:** {run.get('status')}",
        f"**Reported Usage USD:** {usage if usage is not None else 'not reported'}",
        "",
        "## Keywords",
        "",
    ]
    lines.extend(f"- `{keyword}`" for keyword in keywords)
    lines.extend(
        [
            "",
            "## Settings",
            "",
            f"- **Days:** {payload.get('daysToScrape')}",
            f"- **Count Per Keyword:** {payload.get('count')}",
            "",
            "## Outputs",
            "",
            f"- Sanitized raw JSON: `{raw_path.relative_to(ROOT)}`",
        ]
    )
    if clean_path:
        lines.append(f"- Clean CSV: `{clean_path.relative_to(ROOT)}`")
    if merged_counts:
        rows, valid = merged_counts
        lines.append(f"- Main clean comp table: `{CLEAN_SOLD_COMPS_CSV}` ({rows} rows, {valid} valid full-unit rows)")
    lines.append("")
    RUN_REPORT.parent.mkdir(parents=True, exist_ok=True)
    RUN_REPORT.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run eBay sold comps for exact model keywords.")
    parser.add_argument("--keywords", nargs="*", help="Exact model keywords, max 6.")
    parser.add_argument("--keyword-file", type=Path, help="Optional newline-delimited exact model keywords.")
    parser.add_argument("--days", type=int, help="Days to scrape. Defaults to config.")
    parser.add_argument("--count", type=int, help="Items per keyword. Defaults to config.")
    parser.add_argument("--clean", action="store_true", help="Clean the raw actor output after the run.")
    parser.add_argument("--merge", action="store_true", help="Merge cleaned comps into data/ebay_sold_comps_clean.csv.")
    parser.add_argument("--refresh-reports", action="store_true", help="Regenerate Deal Desk and photo queue after merge.")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow non-exact keyword runs when Matthew explicitly approves.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print actor input without calling Apify.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actor_config = load_config()
    actor_id = actor_config.get("actor_id", "oTtB3VgfuE9GtxQt2")
    keywords = normalize_keywords(args)

    try:
        validate_keywords(keywords, args.allow_low_confidence)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    payload = actor_input(keywords, actor_config, args)
    print("eBay sold comps request:")
    print(json.dumps({**payload, "keywords": keywords}, indent=2))

    if args.dry_run:
        print("Dry run only. No Apify actor was called.")
        return 0

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("ERROR: APIFY_TOKEN is required.")
        return 2

    run, items = run_actor(payload, actor_id, token)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"ebay_sold_{timestamp}.json"
    raw_path.write_text(json.dumps(sanitize_items(items), indent=2), encoding="utf-8")

    print(f"Actor status: {run.get('status')}")
    print(f"Dataset items: {len(items)}")
    print(f"Sanitized raw output: {raw_path.relative_to(ROOT)}")

    clean_path: Path | None = None
    merged_counts: tuple[int, int] | None = None
    if args.clean or args.merge:
        clean_path = raw_path.with_name(f"{raw_path.stem}_clean.csv")
        raw_count, valid_count = clean_output(raw_path, clean_path)
        print(f"Clean CSV: {clean_path.relative_to(ROOT)}")
        print(f"Clean rows: {raw_count}; valid full-unit rows: {valid_count}")

    if args.merge:
        if clean_path is None:
            print("ERROR: --merge requires clean output.")
            return 2
        merged_counts = merge_clean_csv(clean_path)
        print(f"Merged main comp table: {merged_counts[0]} rows; {merged_counts[1]} valid full-unit rows")

    if args.refresh_reports:
        subprocess.run([sys.executable, "scripts/deal_desk_review.py"], cwd=ROOT, check=False)
        subprocess.run([sys.executable, "scripts/photo_verification_queue.py"], cwd=ROOT, check=False)

    write_run_report(keywords, payload, run, raw_path, clean_path, merged_counts)
    print(f"Run report: {RUN_REPORT.relative_to(ROOT)}")
    return 0 if run.get("status") == "SUCCEEDED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
