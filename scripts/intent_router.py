#!/usr/bin/env python3
"""
Route Matthew's request to the best existing Frankie skill before inventing a plan.

This is deliberately simple and local-only. It is a guardrail for OpenClaw:
look for intent, choose an existing skill/runbook, and only fall back after the
router and manifests have been checked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills" / "manifest.json"


@dataclass(frozen=True)
class RouteRule:
    skill: str
    weight: int
    phrases: tuple[str, ...]
    reason: str
    prefer_when: str


RULES: tuple[RouteRule, ...] = (
    RouteRule(
        "freebie-radar",
        8,
        (
            "athens marketplace",
            "marketplace near me",
            "marketplace in my area",
            "local marketplace",
            "facebook marketplace near me",
            "facebook marketplace athens",
            "good deals in my area",
            "local deals",
            "cheap local listings",
            "free listings",
            "curb alert",
            "free pickup",
            "pickup deals",
            "what's new on marketplace",
            "whats new on marketplace",
        ),
        "Local marketplace deal hunting should use the freebie radar first, not direct browser Facebook.",
        "Use when Matthew wants local Athens/Georgia marketplace listings, free/cheap pickup items, or casual deal browsing.",
    ),
    RouteRule(
        "arbitrage-deal-desk",
        9,
        (
            "arbitrage",
            "resale",
            "flip",
            "profit",
            "sold comps",
            "ebay sold",
            "deal desk",
            "photo verification",
            "mercari",
            "facebook marketplace",
            "good deal right now",
            "recommendations for what to get",
            "worth buying",
        ),
        "Resale underwriting belongs in the Deal Desk, with sold comps before any profit estimate.",
        "Use when Matthew wants INVESTIGATE/WATCH/SKIP resale recommendations, not just free local pickup scanning.",
    ),
    RouteRule(
        "athens-food",
        9,
        (
            "where should i eat",
            "restaurant",
            "restaurants",
            "food",
            "lunch",
            "dinner",
            "cuisine",
            "random restaurant",
            "spontaneous restaurant",
            "athens food",
            "no bar food",
            "no fast food",
        ),
        "Food and restaurant choices should use the Athens food picker and its filters.",
        "Use for restaurant recommendations, cuisine filters, open/closed checks, and food mood prompts.",
    ),
    RouteRule(
        "smartcore-billing",
        10,
        (
            "smartcore",
            "invoice",
            "invoices",
            "billing",
            "billing email",
            "vehicle tracking bill",
            "asset tracking bill",
            "building monitoring bill",
            "quote",
            "proposal",
        ),
        "SmartCore billing has a dedicated generator and should not be rebuilt from scratch.",
        "Use for invoice PDFs, previews, billing drafts, and quote/proposal generation.",
    ),
    RouteRule(
        "voice-output",
        9,
        (
            "voice file",
            "audio file",
            "read it to me",
            "elevenlabs",
            "eleven labs",
            "tts",
            "sag",
            "narrate",
            "storytime",
        ),
        "Voice requests should route to the local ElevenLabs/sag notes.",
        "Use when Matthew wants spoken audio output or narration.",
    ),
    RouteRule(
        "overwatch-rf",
        9,
        (
            "overwatch",
            "wifi surveillance",
            "wifi monitor",
            "rf monitoring",
            "local signal environment",
            "daily overwatch check",
            "device registry",
        ),
        "Overwatch lives in its own repo and has a wrapper skill here.",
        "Use for passive WiFi/RF environment review and daily Overwatch summaries.",
    ),
    RouteRule(
        "apify-actors",
        7,
        (
            "apify actor",
            "apify actors",
            "actor catalog",
            "scraper",
            "scrapers",
            "generic scraper",
            "website scraper",
            "apify store",
        ),
        "Actor selection should use the Apify catalog before adding new scraping paths.",
        "Use when Matthew asks what scrapers/actors to add or how to collect data.",
    ),
    RouteRule(
        "page-map",
        7,
        (
            "map this page",
            "browser automation",
            "find buttons",
            "inspect site",
            "click around",
            "web page controls",
        ),
        "Browser automation should map the page before clicking around.",
        "Use for page inspection and browser control tasks.",
    ),
    RouteRule(
        "signals",
        8,
        ("signals", "signal report", "full signal report", "/signals"),
        "Signal Engine has an existing report workflow.",
        "Use for the full Signal Engine report.",
    ),
    RouteRule(
        "radar",
        8,
        ("radar", "what happened", "quick scan", "/radar"),
        "Radar has an existing quick scan workflow.",
        "Use for short current scans.",
    ),
    RouteRule(
        "bigpic",
        8,
        ("bigpic", "big picture", "strategic synthesis", "core thesis", "/bigpic"),
        "Big-picture synthesis has an existing skill.",
        "Use for strategy synthesis and core thesis prompts.",
    ),
    RouteRule(
        "ideas",
        8,
        ("ideas", "opportunities", "what should i build", "/ideas"),
        "Idea generation has an existing skill.",
        "Use for opportunity and build-idea prompts.",
    ),
)

BLOCK_BROWSER_PHRASES = (
    "facebook marketplace",
    "marketplace near me",
    "athens marketplace",
    "local deals",
    "free listings",
)


def normalize(text: str) -> str:
    text = text.lower().replace("’", "'")
    text = re.sub(r"[^a-z0-9$/' -]+", " ", text)
    text = re.sub(r"\bmarket\s+place\b", "marketplace", text)
    return re.sub(r"\s+", " ", text).strip()


def load_manifest() -> dict[str, dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {skill["name"]: skill for skill in data.get("skills", [])}


def score_rules(query: str) -> list[dict]:
    q = normalize(query)
    manifest = load_manifest()
    matches: dict[str, dict] = {}

    for rule in RULES:
        hit_phrases = [phrase for phrase in rule.phrases if phrase in q]
        if not hit_phrases:
            continue
        score = rule.weight * len(hit_phrases)
        current = matches.setdefault(
            rule.skill,
            {
                "skill": rule.skill,
                "score": 0,
                "matches": [],
                "reason": rule.reason,
                "prefer_when": rule.prefer_when,
                "path": manifest.get(rule.skill, {}).get("path", ""),
                "safe_default": manifest.get(rule.skill, {}).get("safe_default", ""),
            },
        )
        current["score"] += score
        current["matches"].extend(hit_phrases)

    if "facebook marketplace" in q and any(word in q for word in ("profit", "resale", "flip", "arbitrage", "sold")):
        matches.setdefault("arbitrage-deal-desk", {
            "skill": "arbitrage-deal-desk",
            "score": 0,
            "matches": [],
            "reason": "Facebook Marketplace plus resale language means Deal Desk underwriting.",
            "prefer_when": "Use when resale/profit/sold-comps intent is present.",
            "path": manifest.get("arbitrage-deal-desk", {}).get("path", ""),
            "safe_default": manifest.get("arbitrage-deal-desk", {}).get("safe_default", ""),
        })["score"] += 15
    elif "marketplace" in q and any(word in q for word in ("athens", "local", "near me", "area", "free", "cheap", "pickup", "deals")):
        matches.setdefault("freebie-radar", {
            "skill": "freebie-radar",
            "score": 0,
            "matches": [],
            "reason": "Marketplace plus local/cheap/free language means Freebie Radar first.",
            "prefer_when": "Use for local deal browsing before browser Facebook.",
            "path": manifest.get("freebie-radar", {}).get("path", ""),
            "safe_default": manifest.get("freebie-radar", {}).get("safe_default", ""),
        })["score"] += 15

    result = sorted(matches.values(), key=lambda item: (-item["score"], item["skill"]))
    return result


def route(query: str) -> dict:
    matches = score_rules(query)
    primary = matches[0] if matches else None
    q = normalize(query)
    browser_warning = any(phrase in q for phrase in BLOCK_BROWSER_PHRASES)

    return {
        "query": query,
        "primary": primary,
        "alternates": matches[1:4],
        "browser_warning": browser_warning,
        "fallback": {
            "instruction": "If no primary route fits, read COMMANDS.md, skills/manifest.json, .openclaw/skill-manifest.json, then search skills/*/SKILL.md before inventing a new workflow.",
        },
    }


def print_human(data: dict) -> None:
    primary = data["primary"]
    if not primary:
        print("No confident route.")
        print(data["fallback"]["instruction"])
        return

    print(f"Primary skill: {primary['skill']} (score {primary['score']})")
    print(f"Open: {primary['path']}")
    if primary.get("safe_default"):
        print(f"Safe default: {primary['safe_default']}")
    print(f"Why: {primary['reason']}")
    print(f"Matched: {', '.join(sorted(set(primary['matches'])))}")
    if data["browser_warning"]:
        print("Browser warning: check this skill before direct browser/Facebook/Craigslist work.")
    if data["alternates"]:
        print("Alternates:")
        for alt in data["alternates"]:
            print(f"- {alt['skill']} (score {alt['score']}): {alt['path']}")


def self_test() -> int:
    cases = {
        "show me Athens marketplace good deals in my area": "freebie-radar",
        "show me the listing for Athens market place in my area and good deals": "freebie-radar",
        "is this Facebook Marketplace stereo worth flipping for profit": "arbitrage-deal-desk",
        "no bar food no pizza where should I eat": "athens-food",
        "make the SmartCore invoices": "smartcore-billing",
        "run an Overwatch daily check": "overwatch-rf",
    }
    failed = []
    for query, expected in cases.items():
        actual = route(query)["primary"]
        actual_name = actual["skill"] if actual else ""
        if actual_name != expected:
            failed.append(f"{query!r}: expected {expected}, got {actual_name or 'none'}")
    if failed:
        print("Intent router self-test failed:")
        for item in failed:
            print(f"- {item}")
        return 1
    print("Intent router self-test OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route a Matthew prompt to an existing Frankie skill.")
    parser.add_argument("query", nargs="*", help="Prompt text to route")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument("--self-test", action="store_true", help="Run route regression checks")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    query = " ".join(args.query).strip()
    if not query:
        print("Usage: python scripts\\intent_router.py \"show me Athens marketplace good deals\"")
        return 2

    data = route(query)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_human(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
