#!/usr/bin/env python3
"""
Update persistent lead history from the current normalized marketplace CSVs.

This is the simple memory layer:
- first_seen / last_seen
- times_seen
- first / last / min / max price
- price-change events

It does not scrape anything. Run this after Mercari or Facebook CSVs are updated.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arbitrage_logic import Lead, load_all_leads, money  # noqa: E402


HISTORY_CSV = Path("data/lead_history.csv")
PRICE_EVENTS_CSV = Path("data/lead_price_events.csv")
REPORT_PATH = Path("reports/LEAD_HISTORY_UPDATE_001.md")


HISTORY_FIELDS = [
    "source",
    "listing_key",
    "title",
    "url",
    "location",
    "image_url",
    "first_seen",
    "last_seen",
    "times_seen",
    "first_price",
    "last_price",
    "min_price",
    "max_price",
    "last_review_status",
    "notes",
]

EVENT_FIELDS = [
    "event_time",
    "event_type",
    "source",
    "listing_key",
    "title",
    "url",
    "old_price",
    "new_price",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def listing_key(lead: Lead) -> str:
    raw = lead.url or lead.item_id or f"{lead.source}:{lead.title}:{lead.price}"
    return raw.strip().lower()


def price_text(price: float | None) -> str:
    if price is None:
        return ""
    return f"{price:.2f}"


def parse_price(value: str | None) -> float | None:
    if value in [None, ""]:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_history() -> dict[str, dict[str, str]]:
    if not HISTORY_CSV.exists():
        return {}
    with HISTORY_CSV.open("r", encoding="utf-8", newline="") as f:
        return {row["listing_key"]: row for row in csv.DictReader(f)}


def append_events(events: list[dict[str, str]]) -> None:
    if not events:
        return
    PRICE_EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    file_exists = PRICE_EVENTS_CSV.exists()
    with PRICE_EVENTS_CSV.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EVENT_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(events)


def write_history(rows: list[dict[str, str]]) -> None:
    HISTORY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def update_history(leads: list[Lead]) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    timestamp = now_iso()
    history = load_history()
    events: list[dict[str, str]] = []
    stats = {"current_leads": len(leads), "new": 0, "price_changes": 0, "seen_before": 0}

    for lead in leads:
        key = listing_key(lead)
        new_price = lead.price
        new_price_text = price_text(new_price)
        row = history.get(key)

        if row is None:
            stats["new"] += 1
            row = {
                "source": lead.source,
                "listing_key": key,
                "title": lead.title,
                "url": lead.url,
                "location": lead.location,
                "image_url": lead.image_url,
                "first_seen": timestamp,
                "last_seen": timestamp,
                "times_seen": "1",
                "first_price": new_price_text,
                "last_price": new_price_text,
                "min_price": new_price_text,
                "max_price": new_price_text,
                "last_review_status": lead.review_status,
                "notes": lead.notes,
            }
            events.append(
                {
                    "event_time": timestamp,
                    "event_type": "NEW",
                    "source": lead.source,
                    "listing_key": key,
                    "title": lead.title,
                    "url": lead.url,
                    "old_price": "",
                    "new_price": new_price_text,
                }
            )
            history[key] = row
            continue

        stats["seen_before"] += 1
        old_price = parse_price(row.get("last_price"))
        if new_price is not None and old_price is not None and abs(new_price - old_price) > 0.009:
            stats["price_changes"] += 1
            events.append(
                {
                    "event_time": timestamp,
                    "event_type": "PRICE_CHANGE",
                    "source": lead.source,
                    "listing_key": key,
                    "title": lead.title,
                    "url": lead.url,
                    "old_price": price_text(old_price),
                    "new_price": new_price_text,
                }
            )

        row["title"] = lead.title or row.get("title", "")
        row["url"] = lead.url or row.get("url", "")
        row["location"] = lead.location or row.get("location", "")
        row["image_url"] = lead.image_url or row.get("image_url", "")
        row["last_seen"] = timestamp
        row["times_seen"] = str(int(row.get("times_seen") or "0") + 1)
        row["last_price"] = new_price_text or row.get("last_price", "")
        row["last_review_status"] = lead.review_status or row.get("last_review_status", "")
        row["notes"] = lead.notes or row.get("notes", "")

        existing_prices = [
            p for p in [parse_price(row.get("min_price")), parse_price(row.get("max_price")), new_price] if p is not None
        ]
        if existing_prices:
            row["min_price"] = price_text(min(existing_prices))
            row["max_price"] = price_text(max(existing_prices))

    rows = sorted(history.values(), key=lambda item: item.get("last_seen", ""), reverse=True)
    return rows, events, stats


def write_report(stats: dict[str, int], events: list[dict[str, str]]) -> None:
    new_events = [event for event in events if event["event_type"] == "NEW"]
    price_events = [event for event in events if event["event_type"] == "PRICE_CHANGE"]
    price_drops = []
    for event in price_events:
        old_price = parse_price(event.get("old_price"))
        new_price = parse_price(event.get("new_price"))
        if old_price is not None and new_price is not None and new_price < old_price:
            price_drops.append((old_price - new_price, event))
    price_drops.sort(reverse=True, key=lambda item: item[0])

    lines = [
        "# Lead History Update 001",
        "",
        f"**Generated:** {now_iso()}",
        "",
        "## Summary",
        "",
        f"- **Current leads loaded:** {stats['current_leads']}",
        f"- **New listings:** {stats['new']}",
        f"- **Seen before:** {stats['seen_before']}",
        f"- **Price changes:** {stats['price_changes']}",
        "",
        "## Biggest Price Drops",
        "",
    ]

    if price_drops:
        for drop, event in price_drops[:10]:
            lines.append(f"- **Drop {money(drop)}:** {event['title'][:100]} ({event['old_price']} -> {event['new_price']})")
            if event.get("url"):
                lines.append(f"  URL: {event['url']}")
    else:
        lines.append("No price drops detected in this update.")
    lines.append("")

    lines.extend(["## New Listing Samples", ""])
    for event in new_events[:15]:
        lines.append(f"- **{event['source']} {event['new_price']}:** {event['title'][:100]}")
        if event.get("url"):
            lines.append(f"  URL: {event['url']}")
    if not new_events:
        lines.append("No new listings detected in this update.")
    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    leads = load_all_leads()
    rows, events, stats = update_history(leads)
    write_history(rows)
    append_events(events)
    write_report(stats, events)
    print(f"Current leads loaded: {stats['current_leads']}")
    print(f"New listings: {stats['new']}")
    print(f"Price changes: {stats['price_changes']}")
    print(f"History written: {HISTORY_CSV}")
    print(f"Price events written: {PRICE_EVENTS_CSV}")
    print(f"Report written: {REPORT_PATH}")


if __name__ == "__main__":
    main()
