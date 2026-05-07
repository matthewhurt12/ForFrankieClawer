#!/usr/bin/env python3
"""
Facebook/Mercari freebie radar for Matthew.

This is intentionally separate from the arbitrage Deal Desk. The Deal Desk is
for resale underwriting. This radar is for fast local pickup opportunities:
free, curb-alert, pickup-only, and very cheap retro tech / electronics listings.

Default mode is local-only and reads existing normalized CSVs. Use --collect
only when Matthew explicitly wants a fresh paid Apify run.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import requests

from arbitrage_logic import detect_equipment_category, detect_exact_model, normalize_space


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "freebie_radar.json"
FACEBOOK_CSV = ROOT / "data" / "external_leads" / "facebook_marketplace_leads.csv"
MERCARI_CSV = ROOT / "data" / "external_leads" / "mercari_leads.csv"
DATA_DIR = ROOT / "data" / "freebie_radar"
RAW_DIR = DATA_DIR / "raw"
LATEST_CSV = DATA_DIR / "freebie_radar_latest.csv"
HISTORY_CSV = DATA_DIR / "freebie_radar_history.csv"
REPORT_PATH = ROOT / "reports" / "FREEBIE_RADAR_LAST.md"
API_BASE = "https://api.apify.com/v2"


@dataclass
class RadarItem:
    source: str
    title: str
    price: float | None
    url: str
    location: str
    image_url: str = ""
    query: str = ""
    scraped_at: str = ""
    notes: str = ""


@dataclass
class RadarAssessment:
    item: RadarItem
    status: str
    verdict: str
    score: int
    reason: str
    category: str
    model: str
    model_confidence: int
    price_signal: str
    risk: str
    seller_message: str
    new_status: str = "UNKNOWN"
    matched_terms: list[str] = field(default_factory=list)


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_price(value: Any) -> float | None:
    text = normalize_space(value).lower()
    if not text:
        return None
    if text in {"free", "$free"} or "free" in text:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace("$", "").replace(",", ""))
    if not match:
        return None
    try:
        price = float(match.group(0))
    except ValueError:
        return None
    if price < 0:
        return None
    return price


def money(price: float | None) -> str:
    if price is None:
        return "unknown"
    if price == 0:
        return "free"
    if price == int(price):
        return f"${int(price)}"
    return f"${price:.2f}"


def contains_term(text: str, term: str) -> bool:
    term = term.lower()
    if " " in term or "-" in term:
        return term in text
    return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) is not None


def matching_terms(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if contains_term(lowered, term)]


def price_from_facebook_item(item: dict[str, Any]) -> float | None:
    listing_price = item.get("listing_price")
    if isinstance(listing_price, dict):
        amount = listing_price.get("amount")
        if amount is not None:
            return parse_price(amount)
    return parse_price(item.get("price") or item.get("formattedPrice"))


def normalize_facebook_item(item: dict[str, Any], fallback_query: str = "") -> RadarItem:
    title = normalize_space(item.get("marketplace_listing_title") or item.get("custom_title") or item.get("title"))
    fb_url = normalize_space(item.get("facebookUrl") or fallback_query)
    listing_url = normalize_space(item.get("listingUrl") or item.get("url"))
    location = normalize_space(item.get("location"))
    if not location:
        haystack = f"{fb_url} {listing_url}".lower()
        if "athens" in haystack:
            location = "Athens, GA"
        elif "atlanta" in haystack:
            location = "Atlanta, GA"
        else:
            location = "Georgia"

    photo_url = ""
    photo = item.get("primary_listing_photo")
    if isinstance(photo, dict):
        photo_url = normalize_space(photo.get("photo_image_url"))

    return RadarItem(
        source="Facebook Marketplace",
        title=title,
        price=price_from_facebook_item(item),
        url=listing_url,
        location=location,
        image_url=photo_url,
        query=fb_url,
        scraped_at=datetime.now(timezone.utc).isoformat(),
        notes="FACEBOOK_FREEBIE_RADAR",
    )


def normalize_mercari_item(item: dict[str, Any], query: str) -> RadarItem:
    price = parse_price(item.get("price_usd"))
    if price is None:
        cents = parse_price(item.get("price"))
        price = cents / 100 if cents is not None and cents > 100 else cents
    item_id = normalize_space(item.get("id") or item.get("item_id"))
    url = normalize_space(item.get("url") or item.get("itemUrl"))
    if not url and item_id:
        url = f"https://www.mercari.com/us/item/{item_id}/"

    thumbnails = item.get("thumbnails")
    image_url = ""
    if isinstance(thumbnails, list) and thumbnails:
        image_url = normalize_space(thumbnails[0])
    else:
        image_url = normalize_space(item.get("image_url"))

    return RadarItem(
        source="Mercari",
        title=normalize_space(item.get("name") or item.get("title")),
        price=price,
        url=url,
        location="Online",
        image_url=image_url,
        query=query,
        scraped_at=datetime.now(timezone.utc).isoformat(),
        notes="MERCARI_CHEAP_RADAR",
    )


def load_existing_items(sources: list[str]) -> list[RadarItem]:
    items: list[RadarItem] = []
    if "facebook" in sources and FACEBOOK_CSV.exists():
        with FACEBOOK_CSV.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                items.append(
                    RadarItem(
                        source="Facebook Marketplace",
                        title=normalize_space(row.get("title")),
                        price=parse_price(row.get("price")),
                        url=normalize_space(row.get("listing_url") or row.get("url")),
                        location=normalize_space(row.get("location")) or "Georgia",
                        image_url=normalize_space(row.get("photo_url") or row.get("image_url")),
                        query=normalize_space(row.get("search_url") or row.get("query")),
                        scraped_at=normalize_space(row.get("scraped_at")),
                        notes=normalize_space(row.get("notes")),
                    )
                )

    if "mercari" in sources and MERCARI_CSV.exists():
        with MERCARI_CSV.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                items.append(
                    RadarItem(
                        source="Mercari",
                        title=normalize_space(row.get("title")),
                        price=parse_price(row.get("price_usd")),
                        url=normalize_space(row.get("url") or row.get("listing_url")),
                        location="Online",
                        image_url=normalize_space(row.get("image_url")),
                        query=normalize_space(row.get("query")),
                        scraped_at=normalize_space(row.get("scraped_at")),
                        notes=normalize_space(row.get("notes")),
                    )
                )

    return dedupe_items(items)


def dedupe_items(items: list[RadarItem]) -> list[RadarItem]:
    seen: set[str] = set()
    unique: list[RadarItem] = []
    for item in items:
        key = (item.url or f"{item.source}:{item.title}:{item.price}").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def run_facebook_collection(config: dict[str, Any], limit_searches: int | None = None) -> list[RadarItem]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN is required for --collect")

    fb = config.get("facebook_marketplace", {})
    actor_id = fb.get("actor_id", "apify~facebook-marketplace-scraper")
    urls = list(fb.get("search_urls", []))
    if limit_searches:
        urls = urls[:limit_searches]
    results_limit = int(fb.get("results_limit_per_url", 6))
    estimated_cost = len(urls) * float(fb.get("estimated_cost_per_url", 0.02))
    max_cost = float(fb.get("max_estimated_cost", 0.35))
    if estimated_cost > max_cost:
        raise RuntimeError(f"Estimated Facebook cost ${estimated_cost:.2f} exceeds cap ${max_cost:.2f}")

    actor_input = {
        "startUrls": [{"url": url} for url in urls],
        "resultsLimit": results_limit,
        "extendOutputFunction": "",
        "proxyConfiguration": {"useApifyProxy": True},
    }
    endpoint = f"{API_BASE}/acts/{actor_id}/run-sync-get-dataset-items"
    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=actor_input,
        timeout=300,
    )
    response.raise_for_status()
    raw_items = response.json()
    save_raw("facebook", raw_items)
    return [normalize_facebook_item(item) for item in raw_items]


def run_mercari_collection(config: dict[str, Any], limit_searches: int | None = None) -> list[RadarItem]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN is required for --collect")

    mercari = config.get("mercari", {})
    actor_id = mercari.get("actor_id", "stealth_mode~mercari-product-search-scraper")
    searches = list(mercari.get("search_terms", []))
    if limit_searches:
        searches = searches[:limit_searches]
    max_items = int(mercari.get("max_items_per_url", 5))
    estimated_cost = len(searches) * float(mercari.get("estimated_cost_per_search", 0.015))
    max_cost = float(mercari.get("max_estimated_cost", 0.15))
    if estimated_cost > max_cost:
        raise RuntimeError(f"Estimated Mercari cost ${estimated_cost:.2f} exceeds cap ${max_cost:.2f}")

    all_items: list[RadarItem] = []
    all_raw: list[dict[str, Any]] = []
    endpoint = f"{API_BASE}/acts/{actor_id}/run-sync-get-dataset-items"
    for query in searches:
        search_url = f"https://www.mercari.com/search/?keyword={quote_plus(query)}"
        actor_input = {
            "urls": [search_url],
            "max_items_per_url": max_items,
            "ignore_url_failures": True,
            "proxy": {"useApifyProxy": True},
        }
        response = requests.post(
            endpoint,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=actor_input,
            timeout=180,
        )
        response.raise_for_status()
        raw_items = response.json()
        all_raw.extend(raw_items)
        all_items.extend(normalize_mercari_item(item, query) for item in raw_items)
    save_raw("mercari", all_raw)
    return all_items


def save_raw(source: str, items: list[dict[str, Any]]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    (RAW_DIR / f"{source}_{stamp}.json").write_text(json.dumps(items, indent=2), encoding="utf-8")


def collect_items(config: dict[str, Any], sources: list[str], limit_searches: int | None) -> list[RadarItem]:
    items: list[RadarItem] = []
    if "facebook" in sources:
        print("Running Facebook freebie collection...")
        items.extend(run_facebook_collection(config, limit_searches))
    if "mercari" in sources:
        print("Running Mercari cheap-deal collection...")
        items.extend(run_mercari_collection(config, limit_searches))
    return dedupe_items(items)


def assess_item(item: RadarItem, config: dict[str, Any]) -> RadarAssessment:
    title = normalize_space(item.title)
    title_text = title.lower()
    free_terms = matching_terms(title_text, config.get("free_terms", []))
    bait_terms = matching_terms(title_text, config.get("price_bait_terms", []))
    interest_terms = matching_terms(title_text, config.get("interest_terms", []))
    junk_terms = matching_terms(title_text, config.get("junk_terms", []))
    cheap_max = float(config.get("cheap_max_price", 25))
    model = detect_exact_model(title)
    category = model.category or detect_equipment_category(title) or ("electronics" if "electronics" in interest_terms else "")

    price = item.price
    is_free = price == 0 or bool(free_terms)
    is_cheap = price is not None and 0 < price <= cheap_max
    is_one_dollar_bait = price == 1 and not free_terms

    score = 0
    reasons: list[str] = []
    price_signal = "NO_PRICE_SIGNAL"
    verdict = "SKIP"
    status = "SKIP"
    risk = "Manual review required before pickup."

    if junk_terms:
        return RadarAssessment(
            item=item,
            status="SKIP",
            verdict="SKIP",
            score=0,
            reason=f"Rejected by junk term: {junk_terms[0]}",
            category=category,
            model=model.name,
            model_confidence=model.confidence,
            price_signal="JUNK_OR_NOT_TARGET",
            risk="Likely not the kind of pickup Matthew wants.",
            seller_message="",
            matched_terms=junk_terms,
        )

    if is_free:
        score += 75
        price_signal = "FREE_OR_PICKUP_SIGNAL"
        status = "FREE_PICKUP_CANDIDATE"
        verdict = "INVESTIGATE"
        reasons.append("free/pickup language found")
    elif is_cheap:
        score += 35
        price_signal = "CHEAP_LOCAL_SIGNAL"
        status = "CHEAP_WATCH_CANDIDATE"
        verdict = "WATCH"
        reasons.append(f"price is at or under {money(cheap_max)}")

    if is_one_dollar_bait:
        score -= 35
        price_signal = "PRICE_BAIT_REVIEW"
        status = "PRICE_BAIT_REVIEW"
        verdict = "WATCH"
        reasons.append("$1 listing without free/pickup wording")

    if model.name:
        score += min(30, model.confidence // 3)
        reasons.append(f"model/category signal: {model.name}")
    elif category:
        score += 15
        reasons.append(f"category signal: {category}")

    if interest_terms:
        score += min(20, len(interest_terms) * 4)
        reasons.append("matches Matthew interest terms: " + ", ".join(interest_terms[:4]))

    if not interest_terms and not model.name and not category:
        score -= 50
        status = "SKIP"
        verdict = "SKIP"
        reasons.append("no useful retro tech/electronics signal")

    if price is None and not free_terms:
        score -= 10
        reasons.append("price is unknown")

    if item.source == "Mercari" and verdict == "INVESTIGATE":
        verdict = "WATCH"
        status = "MERCARI_CHEAP_WATCH"
        reasons.append("Mercari is not local pickup; watch only until shipping/fees are checked")

    score = max(0, min(100, score))
    if verdict == "INVESTIGATE":
        risk = "Free pickup can disappear quickly; verify it is not broken junk and do not send deposits."
    elif verdict == "WATCH":
        risk = "Check title/photos because cheap listings are often price bait, incomplete, or broken."

    return RadarAssessment(
        item=item,
        status=status,
        verdict=verdict,
        score=score,
        reason="; ".join(reasons) if reasons else "No strong signal",
        category=category or "unknown",
        model=model.name,
        model_confidence=model.confidence,
        price_signal=price_signal,
        risk=risk,
        seller_message=seller_message(item, model.name or category, is_free),
        matched_terms=free_terms + bait_terms + interest_terms,
    )


def seller_message(item: RadarItem, label: str, is_free: bool) -> str:
    target = label or "item"
    if is_free:
        return (
            f"Hi, is the {target} still available? I can pick it up locally. "
            "Is it complete enough to take as-is, and is there a porch/curb pickup window that works?"
        )
    return (
        f"Hi, is the {target} still available? Is the listed price the real price, "
        "and does it power on or include the needed cables/accessories?"
    )


def load_seen() -> dict[str, dict[str, str]]:
    if not HISTORY_CSV.exists():
        return {}
    with HISTORY_CSV.open("r", encoding="utf-8", newline="") as f:
        return {
            row.get("url", ""): row
            for row in csv.DictReader(f)
            if row.get("url") and row.get("verdict") != "SKIP"
        }


def mark_new_and_update_history(assessments: list[RadarAssessment], update: bool = True) -> None:
    seen = load_seen()
    now = datetime.now(timezone.utc).isoformat()
    rows_by_url = dict(seen)

    for assessment in assessments:
        url = assessment.item.url
        if assessment.verdict == "SKIP":
            assessment.new_status = "SKIP"
            continue
        if not url:
            assessment.new_status = "NO_URL"
            continue
        prior = seen.get(url)
        assessment.new_status = "SEEN_BEFORE" if prior else "NEW"
        if not update:
            continue
        count = int(prior.get("seen_count", "0")) + 1 if prior else 1
        rows_by_url[url] = {
            "url": url,
            "first_seen": prior.get("first_seen", now) if prior else now,
            "last_seen": now,
            "seen_count": str(count),
            "source": assessment.item.source,
            "title": assessment.item.title,
            "price": money(assessment.item.price),
            "location": assessment.item.location,
            "verdict": assessment.verdict,
            "status": assessment.status,
            "score": str(assessment.score),
        }

    if update:
        write_history(rows_by_url.values())


def write_history(rows: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "url",
        "first_seen",
        "last_seen",
        "seen_count",
        "source",
        "title",
        "price",
        "location",
        "verdict",
        "status",
        "score",
    ]
    with HISTORY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row.get("last_seen", ""), reverse=True))


def write_latest_csv(assessments: list[RadarAssessment]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "new_status",
        "verdict",
        "status",
        "score",
        "source",
        "title",
        "price",
        "location",
        "url",
        "image_url",
        "category",
        "model",
        "model_confidence",
        "price_signal",
        "reason",
        "risk",
        "seller_message",
        "scraped_at",
    ]
    with LATEST_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for assessment in assessments:
            item = assessment.item
            writer.writerow(
                {
                    "new_status": assessment.new_status,
                    "verdict": assessment.verdict,
                    "status": assessment.status,
                    "score": assessment.score,
                    "source": item.source,
                    "title": item.title,
                    "price": money(item.price),
                    "location": item.location,
                    "url": item.url,
                    "image_url": item.image_url,
                    "category": assessment.category,
                    "model": assessment.model,
                    "model_confidence": assessment.model_confidence,
                    "price_signal": assessment.price_signal,
                    "reason": assessment.reason,
                    "risk": assessment.risk,
                    "seller_message": assessment.seller_message,
                    "scraped_at": item.scraped_at,
                }
            )


def sort_key(assessment: RadarAssessment) -> tuple[int, int, int, float]:
    verdict_rank = {"INVESTIGATE": 3, "WATCH": 2, "SKIP": 1}.get(assessment.verdict, 0)
    new_rank = 1 if assessment.new_status == "NEW" else 0
    price = assessment.item.price if assessment.item.price is not None else 999999.0
    return (verdict_rank, new_rank, assessment.score, -price)


def write_report(assessments: list[RadarAssessment], args: argparse.Namespace) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    active = [a for a in assessments if a.verdict != "SKIP"]
    new_active = [a for a in active if a.new_status == "NEW"]
    free_new = [a for a in new_active if a.status == "FREE_PICKUP_CANDIDATE"]
    watch_new = [a for a in new_active if a.verdict == "WATCH"]
    skipped = [a for a in assessments if a.verdict == "SKIP"]
    top_limit = int(load_config().get("top_limit", 12))

    lines = [
        "# Freebie Radar",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Mode:** {'paid collection + radar' if args.collect else 'local CSV radar only'}",
        f"**Sources:** {', '.join(args.sources)}",
        "",
        "Purpose: catch new local free/curb-alert/very-cheap tech listings without mixing them into the resale Deal Desk.",
        "",
        "## Summary",
        "",
        f"- **Items scanned:** {len(assessments)}",
        f"- **New active leads:** {len(new_active)}",
        f"- **New free/pickup leads:** {len(free_new)}",
        f"- **New cheap/watch leads:** {len(watch_new)}",
        f"- **Skipped:** {len(skipped)}",
        "",
    ]

    lines.extend(render_section("New Free / Pickup Leads", free_new[:top_limit]))
    lines.extend(render_section("New Cheap Watch Leads", watch_new[:top_limit]))
    lines.extend(render_section("Best Seen-Before Leads", [a for a in active if a.new_status != "NEW"][:top_limit]))
    lines.extend(render_skips(skipped[:20]))
    lines.extend(
        [
            "## Output Files",
            "",
            f"- Latest CSV: `{rel(LATEST_CSV)}`",
            f"- History CSV: `{rel(HISTORY_CSV)}`",
            "",
            "## Operating Rules",
            "",
            "- Free/pickup wording beats price alone.",
            "- `$1` listings without free/pickup wording are treated as price-bait review, not urgent wins.",
            "- No seller messages are sent automatically.",
            "- `--collect` calls paid Apify actors and requires `APIFY_TOKEN`.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def render_section(title: str, assessments: list[RadarAssessment]) -> list[str]:
    lines = [f"## {title}", ""]
    if not assessments:
        return lines + ["No matching leads in this run.", ""]
    for index, assessment in enumerate(assessments, 1):
        item = assessment.item
        lines.extend(
            [
                f"### {index}. {item.title}",
                "",
                f"- **Verdict:** {assessment.verdict}",
                f"- **Status:** {assessment.status}",
                f"- **Score:** {assessment.score}/100",
                f"- **Source:** {item.source}",
                f"- **Location:** {item.location}",
                f"- **Price:** {money(item.price)}",
                f"- **URL:** {item.url}",
                f"- **Category/Model:** {assessment.model or assessment.category}",
                f"- **Signal:** {assessment.price_signal}",
                f"- **Why It Matched:** {assessment.reason}",
                f"- **Risk:** {assessment.risk}",
                "",
                "**Message:**",
                "```text",
                assessment.seller_message,
                "```",
                "",
                "---",
                "",
            ]
        )
    return lines


def render_skips(assessments: list[RadarAssessment]) -> list[str]:
    lines = ["## Skipped / Suppressed Examples", ""]
    if not assessments:
        return lines + ["No skipped examples.", ""]
    for assessment in assessments:
        lines.append(f"- **{assessment.item.title}** - {assessment.reason}")
    lines.append("")
    return lines


def parse_args() -> argparse.Namespace:
    config = load_config()
    parser = argparse.ArgumentParser(description="Run the local free/cheap marketplace radar.")
    parser.add_argument("--collect", action="store_true", help="Run paid Apify collection before filtering.")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["facebook", "mercari"],
        default=config.get("default_sources", ["facebook"]),
        help="Sources to scan. Facebook is the default; Mercari is optional.",
    )
    parser.add_argument("--limit-searches", type=int, help="Use only the first N configured searches per source.")
    parser.add_argument("--no-history-update", action="store_true", help="Do not update the persistent seen-history CSV.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned external collection and exit.")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    config = load_config()
    if args.dry_run:
        fb_count = len(config.get("facebook_marketplace", {}).get("search_urls", []))
        mercari_count = len(config.get("mercari", {}).get("search_terms", []))
        if args.limit_searches:
            fb_count = min(fb_count, args.limit_searches)
            mercari_count = min(mercari_count, args.limit_searches)
        print("Freebie radar dry run")
        print(f"Mode: {'paid collection + radar' if args.collect else 'local CSV radar only'}")
        print(f"Sources: {', '.join(args.sources)}")
        if args.collect:
            if "facebook" in args.sources:
                print(f"Facebook searches: {fb_count}")
            if "mercari" in args.sources:
                print(f"Mercari searches: {mercari_count}")
            print("APIFY_TOKEN required for collection; token value is never printed.")
        print(f"Report: {rel(REPORT_PATH)}")
        return 0

    if args.collect:
        items = collect_items(config, args.sources, args.limit_searches)
    else:
        items = load_existing_items(args.sources)

    assessments = [assess_item(item, config) for item in items if item.title]
    assessments.sort(key=sort_key, reverse=True)
    mark_new_and_update_history(assessments, update=not args.no_history_update)
    assessments.sort(key=sort_key, reverse=True)
    write_latest_csv(assessments)
    write_report(assessments, args)

    active = [a for a in assessments if a.verdict != "SKIP"]
    new_active = [a for a in active if a.new_status == "NEW"]
    print("Freebie radar complete")
    print(f"Items scanned: {len(assessments)}")
    print(f"Active leads: {len(active)}")
    print(f"New active leads: {len(new_active)}")
    print(f"Report: {rel(REPORT_PATH)}")
    print(f"Latest CSV: {rel(LATEST_CSV)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
