#!/usr/bin/env python3
"""
Verify Athens restaurant candidates with the Apify Google search actor.

This is intentionally separate from athens_food.py. The spreadsheet gives a
shortlist; this script checks current web signals such as open/closed wording,
hours, ratings, reviews, menu links, and likely official/Google result URLs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "restaurants" / "enrichment"
REPORT_PATH = ROOT / "reports" / "ATHENS_FOOD_GOOGLE_CHECK_LAST.md"
ACTOR_ID = "nFJndFXA5zjCTuudP"
API_BASE = "https://api.apify.com/v2"


OPEN_PATTERNS = [
    r"\bopen now\b",
    r"\bopen today\b",
    r"\bopens?\s+(?:mon|tue|wed|thu|fri|sat|sun|today|tomorrow|\d)",
    r"\bcloses?\s+(?:at\s+)?\d",
]
CLOSED_PATTERNS = [
    r"\bpermanently closed\b",
    r"\btemporarily closed\b",
    r"\bclosed now\b",
    r"\bopens?\s+tomorrow\b",
    r"\bclosed\b",
]
MENU_PATTERNS = [r"\bmenu\b", r"\border\b", r"\btoasttab\b"]
FAST_FOOD_PATTERNS = [
    r"\bfast food\b",
    r"\bfast casual\b",
    r"\bfast-casual\b",
    r"\bquick service\b",
    r"\bquick-service\b",
    r"\bcounter service\b",
    r"\bcounter-service\b",
]
BAR_FOOD_PATTERNS = [
    r"\bbar food\b",
    r"\bsports bar\b",
    r"\bcocktail bar\b",
    r"\bbrewery\b",
    r"\bgastropub\b",
    r"\btaproom\b",
]
RATING_RE = re.compile(r"\b([1-5](?:\.\d)?)\s*(?:stars?|★|\bout of 5\b)")
REVIEWS_RE = re.compile(r"\b([0-9][0-9,]{1,})\s+reviews?\b")


@dataclass
class CheckResult:
    name: str
    query: str
    status: str
    confidence: int
    reasons: list[str]
    rating: str = ""
    reviews: str = ""
    urls: list[str] | None = None
    disqualifiers: list[str] | None = None
    raw_items: int = 0

    @property
    def eligible(self) -> bool:
        if self.status in {"CLOSED_OR_INACTIVE", "CLOSED_NOW", "LIKELY_CLOSED_NOW", "NO_RESULTS"}:
            return False
        return not self.disqualifiers


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


SKIP_TEXT_KEYS = {
    "#debug",
    "url",
    "loadedUrl",
    "searchQuery",
    "relatedQueries",
    "paidResults",
    "paidProducts",
    "serpProviderCode",
}


def flatten_text(value: Any, depth: int = 0) -> str:
    if depth > 5:
        return ""
    if isinstance(value, dict):
        parts: list[str] = []
        for key, child in value.items():
            if key in SKIP_TEXT_KEYS:
                continue
            parts.append(flatten_text(child, depth + 1))
        return " ".join(parts)
    if isinstance(value, list):
        return " ".join(flatten_text(v, depth + 1) for v in value)
    if isinstance(value, (str, int, float, bool)):
        return normalize(value)
    return ""


def collect_urls(value: Any, urls: list[str] | None = None, depth: int = 0) -> list[str]:
    urls = urls or []
    if depth > 5:
        return urls
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and ("url" in key.lower() or child.startswith("http")):
                if child.startswith("http") and child not in urls:
                    urls.append(child)
            else:
                collect_urls(child, urls, depth + 1)
    elif isinstance(value, list):
        for child in value:
            collect_urls(child, urls, depth + 1)
    return urls


def actor_input(queries: list[str]) -> dict[str, Any]:
    return {
        "queries": "\n".join(queries),
        "resultsPerPage": 5,
        "maxPagesPerQuery": 1,
        "disableGoogleSearchResults": False,
        "aiModeSearch": {"enableAiMode": False},
        "perplexitySearch": {"enablePerplexity": False, "returnImages": False, "returnRelatedQuestions": False},
        "chatGptSearch": {"enableChatGpt": False},
        "copilotSearch": {"enableCopilot": False},
        "maximumLeadsEnrichmentRecords": 0,
        "focusOnPaidAds": False,
        "countryCode": "us",
        "searchLanguage": "en",
        "languageCode": "en",
        "forceExactMatch": False,
        "mobileResults": True,
        "includeUnfilteredResults": False,
        "saveHtml": False,
        "saveHtmlToKeyValueStore": False,
        "includeIcons": False,
    }


def run_actor(names: list[str]) -> list[dict[str, Any]]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN is required")
    queries = [f"{name} Athens GA hours open now Google reviews menu" for name in names]
    endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"
    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=actor_input(queries),
        timeout=360,
    )
    response.raise_for_status()
    items = response.json()
    save_raw(items)
    return items


def save_raw(items: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    (DATA_DIR / f"google_search_check_{stamp}.json").write_text(json.dumps(items, indent=2), encoding="utf-8")


def group_items_by_name(names: list[str], items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped = {name: [] for name in names}
    for item in items:
        query = normalize(item.get("query") or item.get("searchQuery") or item.get("q")).lower()
        if query:
            for name in names:
                if name.lower() in query:
                    grouped[name].append(item)
                    break
            continue

        text = flatten_text(item).lower()
        for name in names:
            name_l = name.lower()
            if name_l in text:
                grouped[name].append(item)
                break
    return grouped


def analyze(name: str, items: list[dict[str, Any]], args: argparse.Namespace) -> CheckResult:
    blob = " ".join(flatten_text(item) for item in items)
    text = blob.lower()
    urls = []
    for item in items:
        urls.extend(collect_urls(item))
    urls = unique(urls)[:8]

    closed_hits = first_patterns(text, CLOSED_PATTERNS)
    open_hits = first_patterns(text, OPEN_PATTERNS)
    menu_hits = first_patterns(text, MENU_PATTERNS)
    rating_match = RATING_RE.search(blob)
    reviews_match = REVIEWS_RE.search(blob)
    disqualifiers = condition_disqualifiers(text, args)

    reasons: list[str] = []
    status = "UNKNOWN"
    confidence = 30
    if any("permanently closed" in hit or "temporarily closed" in hit for hit in closed_hits):
        status = "CLOSED_OR_INACTIVE"
        confidence = 90
        reasons.extend(closed_hits)
    elif any("closed now" in hit for hit in closed_hits):
        status = "CLOSED_NOW"
        confidence = 80
        reasons.extend(closed_hits)
    elif closed_hits:
        status = "LIKELY_CLOSED_NOW"
        confidence = 75
        reasons.extend(closed_hits)
    elif open_hits:
        status = "LIKELY_OPEN_OR_HAS_HOURS"
        confidence = 60
        reasons.extend(open_hits)
    else:
        reasons.append("No clear open/closed wording found in actor output")

    if disqualifiers and status not in {"CLOSED_OR_INACTIVE", "CLOSED_NOW", "LIKELY_CLOSED_NOW", "NO_RESULTS"}:
        status = "CONDITION_MISMATCH"
        confidence = max(confidence, 80)
        reasons.extend(disqualifiers)

    if menu_hits:
        reasons.append("menu/order signal found")
    if not items:
        status = "NO_RESULTS"
        confidence = 0
        reasons = ["No actor results were grouped to this restaurant"]

    return CheckResult(
        name=name,
        query=f"{name} Athens GA hours open now Google reviews menu",
        status=status,
        confidence=confidence,
        reasons=unique(reasons)[:8],
        rating=rating_match.group(1) if rating_match else "",
        reviews=reviews_match.group(1) if reviews_match else "",
        urls=urls,
        disqualifiers=unique(disqualifiers)[:8],
        raw_items=len(items),
    )


def condition_disqualifiers(text: str, args: argparse.Namespace) -> list[str]:
    disqualifiers: list[str] = []
    if getattr(args, "no_fast_food", False):
        hits = first_patterns(text, FAST_FOOD_PATTERNS)
        disqualifiers.extend(f"blocked by no-fast-food: {hit}" for hit in hits)
    if getattr(args, "no_bar_food", False):
        hits = first_patterns(text, BAR_FOOD_PATTERNS)
        disqualifiers.extend(f"blocked by no-bar-food: {hit}" for hit in hits)
    for term in arg_terms(getattr(args, "exclude", [])):
        if term in text:
            disqualifiers.append(f"blocked by exclude term: {term}")
    return unique(disqualifiers)


def first_patterns(text: str, patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.I):
            hit = normalize(match.group(0)).lower()
            if hit not in hits:
                hits.append(hit)
            if len(hits) >= 4:
                return hits
    return hits


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        item = normalize(item)
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def arg_terms(values: list[str] | None) -> list[str]:
    terms: list[str] = []
    for value in values or []:
        terms.extend(part.strip().lower() for part in value.split(","))
    return unique(terms)


def write_report(results: list[CheckResult]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Athens Food Google Check",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Actor:** `{ACTOR_ID}`",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.name}",
                "",
                f"- **Status:** {result.status}",
                f"- **Eligible For Final Pick:** {'yes' if result.eligible else 'no'}",
                f"- **Confidence:** {result.confidence}/100",
                f"- **Actor Items:** {result.raw_items}",
                f"- **Rating Signal:** {result.rating or 'not found'}",
                f"- **Review Count Signal:** {result.reviews or 'not found'}",
                f"- **Query:** `{result.query}`",
                f"- **Reasons:** {', '.join(result.reasons)}",
                f"- **Condition Blocks:** {', '.join(result.disqualifiers or []) if result.disqualifiers else 'none'}",
                "",
            ]
        )
        if result.urls:
            lines.append("**URLs:**")
            for url in result.urls[:5]:
                lines.append(f"- {url}")
            lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check restaurant open/closed signals with Apify Google search actor.")
    parser.add_argument("names", nargs="+", help="Restaurant names to check.")
    parser.add_argument("--no-fast-food", action="store_true", help="Reject Google results that describe the place as fast food, fast casual, quick service, or counter service.")
    parser.add_argument("--no-bar-food", action="store_true", help="Reject Google results that describe the place as a bar, pub, brewery, taproom, or bar-food spot.")
    parser.add_argument("--exclude", action="append", default=[], help="Reject Google results containing this word/phrase; comma-separated or repeated.")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    names = [normalize(name) for name in args.names if normalize(name)]
    items = run_actor(names)
    grouped = group_items_by_name(names, items)
    results = [analyze(name, grouped.get(name, []), args) for name in names]
    write_report(results)
    for result in results:
        print(f"{result.name}: {result.status} ({result.confidence}/100)")
        print("  " + "; ".join(result.reasons[:4]))
        if result.disqualifiers:
            print("  blocked: " + "; ".join(result.disqualifiers[:4]))
        if result.rating or result.reviews:
            print(f"  rating={result.rating or '?'} reviews={result.reviews or '?'}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
