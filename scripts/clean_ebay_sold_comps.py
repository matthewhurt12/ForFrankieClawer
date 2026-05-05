#!/usr/bin/env python3
"""
Clean noisy eBay sold comp actor output.

Only FULL_UNIT rows should be used for resale value. Accessories, manuals,
parts, bulbs, cabinets, repair kits, and wrong-model rows are rejected.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys
from statistics import median
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arbitrage_logic import (  # noqa: E402
    CLEAN_SOLD_COMPS_CSV,
    HARD_REJECT_TERMS,
    MODEL_PRICE_FLOORS,
    contains_term,
    detect_exact_model,
    first_matching_term,
    money,
    parse_price,
)


DEFAULT_INPUT = Path("data/sold_comps/ebay_sold_test.json")
SUMMARY_REPORT = Path("reports/EBAY_SOLD_COMPS_CLEANING_001.md")


def load_items(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ["items", "results", "data"]:
            if isinstance(data.get(key), list):
                return [item for item in data[key] if isinstance(item, dict)]
    raise ValueError("Expected a JSON list or an object with items/results/data list")


def pick_first(item: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        if item.get(name) not in [None, ""]:
            return item.get(name)
    return ""


def extract_sold_price(item: dict[str, Any]) -> float | None:
    direct_fields = [
        "soldPrice",
        "sold_price",
        "price",
        "itemPrice",
        "currentPrice",
        "value",
        "finalPrice",
    ]
    for field in direct_fields:
        price = parse_price(item.get(field))
        if price is not None:
            # Some actors return cents.
            if field in ["price", "soldPrice", "sold_price"] and price > 100000:
                return price / 100
            return price

    nested = item.get("price")
    if isinstance(nested, dict):
        return parse_price(pick_first(nested, ["value", "amount", "price"]))
    return None


def item_url(item: dict[str, Any]) -> str:
    return str(
        pick_first(
            item,
            [
                "url",
                "itemUrl",
                "item_url",
                "link",
                "viewItemURL",
                "listingUrl",
            ],
        )
        or ""
    )


def classify_comp(item: dict[str, Any], required_model: str = "") -> dict[str, Any]:
    title = str(pick_first(item, ["title", "name", "itemTitle"]) or "")
    model = detect_exact_model(title)
    price = extract_sold_price(item)
    reject = first_matching_term(title, HARD_REJECT_TERMS)
    reason = ""
    classification = "FULL_UNIT"

    if not title:
        classification = "REJECT"
        reason = "Missing title"
    elif reject:
        classification = "REJECT"
        reason = f"Hard reject term: {reject}"
    elif not model.exact:
        classification = "REJECT"
        reason = "No exact model detected"
    elif required_model and model.name != required_model:
        classification = "REJECT"
        reason = f"Wrong model for requested search: detected {model.name}"
    elif price is None:
        classification = "REJECT"
        reason = "Missing sold price"
    else:
        floor = MODEL_PRICE_FLOORS.get(model.name, model.price_floor)
        if floor and price < floor:
            classification = "REJECT"
            reason = f"Below full-unit price floor for {model.name}: {money(price)} < {money(floor)}"

    if classification == "FULL_UNIT":
        reason = "Exact model, no hard reject terms, above price floor"

    return {
        "model": model.name,
        "brand": model.brand,
        "category": model.category,
        "title": title,
        "sold_price": price,
        "sold_date": pick_first(item, ["soldDate", "sold_date", "dateSold", "endDate", "endedAt"]),
        "condition": pick_first(item, ["condition", "itemCondition"]),
        "url": item_url(item),
        "comp_classification": classification,
        "reason": reason,
    }


def clean_items(items: list[dict[str, Any]], required_model: str = "") -> list[dict[str, Any]]:
    rows = [classify_comp(item, required_model=required_model) for item in items]
    return rows


def write_clean_csv(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
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
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(rows: list[dict[str, Any]], input_path: Path, output_csv: Path) -> None:
    valid_by_model: dict[str, list[float]] = defaultdict(list)
    reject_reasons = Counter()

    for row in rows:
        if row["comp_classification"] == "FULL_UNIT":
            price = parse_price(row.get("sold_price"))
            if row["model"] and price is not None:
                valid_by_model[row["model"]].append(price)
        else:
            reject_reasons[row["reason"]] += 1

    lines = [
        "# eBay Sold Comps Cleaning 001",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Input:** `{input_path}`",
        f"**Output:** `{output_csv}`",
        "",
        "Only rows classified as FULL_UNIT may be used for resale value.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Raw Rows:** {len(rows)}",
        f"- **Valid Full-Unit Rows:** {sum(len(v) for v in valid_by_model.values())}",
        f"- **Rejected Rows:** {sum(reject_reasons.values())}",
        "",
        "## Model Confidence",
        "",
        "| Model | Valid Full-Unit Comps | Median Sold | Range | Status |",
        "|---|---:|---:|---|---|",
    ]

    for model, prices in sorted(valid_by_model.items()):
        prices.sort()
        status = "VALID" if len(prices) >= 3 else "LOW_CONFIDENCE"
        lines.append(
            f"| {model} | {len(prices)} | {money(median(prices))} | {money(prices[0])} - {money(prices[-1])} | {status} |"
        )

    if not valid_by_model:
        lines.append("| None | 0 | n/a | n/a | LOW_CONFIDENCE |")

    lines.extend(["", "## Reject Reasons", ""])
    for reason, count in reject_reasons.most_common():
        lines.append(f"- **{count}:** {reason}")

    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- FULL_UNIT requires exact model detection.",
            "- Hard rejects include manuals, bulbs, kits, parts, knobs, faceplates, cabinets, cases, remotes, apparel, and related junk.",
            "- Below model/category price floor is rejected as likely accessory/parts/noisy result.",
            "- Fewer than 3 valid FULL_UNIT comps is LOW_CONFIDENCE.",
            "",
        ]
    )

    SUMMARY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean eBay sold comp actor output")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Raw Apify JSON output")
    parser.add_argument("--output", type=Path, default=CLEAN_SOLD_COMPS_CSV, help="Clean CSV output")
    parser.add_argument("--model", default="", help="Optional required exact model name")
    args = parser.parse_args()

    items = load_items(args.input)
    rows = clean_items(items, required_model=args.model)
    write_clean_csv(rows, args.output)
    write_summary(rows, args.input, args.output)

    valid = sum(1 for row in rows if row["comp_classification"] == "FULL_UNIT")
    print(f"Loaded raw sold comps: {len(items)}")
    print(f"Valid full-unit comps: {valid}")
    print(f"Clean CSV written: {args.output}")
    print(f"Summary report written: {SUMMARY_REPORT}")


if __name__ == "__main__":
    main()
