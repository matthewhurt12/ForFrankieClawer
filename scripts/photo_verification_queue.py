#!/usr/bin/env python3
"""
Photo Verification Queue.

Compatibility entrypoint for Frankie/OpenClaw. Uses the same conservative
assessment logic as the Deal Desk so the agent sees one navigation pattern.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arbitrage_logic import (  # noqa: E402
    LeadAssessment,
    assess_lead,
    lead_sort_key,
    load_all_leads,
    load_clean_sold_comp_index,
    money,
)


OUTPUT_REPORT = Path("reports/PHOTO_VERIFICATION_QUEUE_001.md")


def bucket_for(item: LeadAssessment) -> str:
    if item.verdict == "SKIP":
        return "SKIP"
    has_positive_underwriting = (
        item.max_buy_price is not None
        and item.lead.price is not None
        and item.max_buy_price > item.lead.price
    )
    if (
        item.classification == "NEEDS_SOLD_COMPS"
        and item.sold_comp_status == "VALID_SOLD_COMPS_ATTACHED"
        and has_positive_underwriting
    ):
        return "READY_FOR_SELLER_MESSAGE"
    if item.sold_comp_status == "VALID_SOLD_COMPS_ATTACHED" and not has_positive_underwriting:
        return "WATCH"
    if item.classification in {"NEEDS_PHOTO_CHECK", "NEEDS_EXACT_MODEL", "NEEDS_SOLD_COMPS"}:
        return item.classification
    return "WATCH"


def write_report(assessments: list[LeadAssessment]) -> None:
    categories = [
        "READY_FOR_SELLER_MESSAGE",
        "NEEDS_PHOTO_CHECK",
        "NEEDS_EXACT_MODEL",
        "NEEDS_SOLD_COMPS",
        "WATCH",
        "SKIP",
    ]
    grouped: dict[str, list[LeadAssessment]] = defaultdict(list)
    for item in assessments:
        grouped[bucket_for(item)].append(item)

    lines = [
        "# Photo Verification Queue 001",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Purpose:** Sort leads by the next missing proof: photo check, exact model, sold comps, watch, or skip.",
        "",
        "No active listing median is used here. No profit estimate is allowed without clean sold comps.",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    for category in categories:
        lines.append(f"- **{category}:** {len(grouped[category])}")
    lines.append("")

    for category in categories:
        items = grouped[category]
        if not items:
            continue
        limit = 20 if category != "SKIP" else 30
        lines.extend([f"## {category}", ""])
        for i, item in enumerate(items[:limit], 1):
            lead = item.lead
            lines.extend(
                [
                    f"### {i}. {lead.title[:100]}",
                    f"- **Source:** {lead.source}",
                    f"- **Price:** {money(lead.price)}",
                    f"- **Location:** {lead.location or 'Unknown'}",
                    f"- **URL:** {lead.url or 'Missing'}",
                    f"- **Suspected Exact Model:** {item.model.name or 'Unknown'}",
                    f"- **Model Confidence:** {item.model.confidence}/100",
                    f"- **Verdict:** {item.verdict}",
                    f"- **Sold Comp Status:** {item.sold_comp_status}",
                    f"- **Why It Might Matter:** {item.interesting}",
                    f"- **What Could Make It Junk:** {item.junk_risk}",
                    f"- **Photo/Model Verification Needed:** {item.photo_verification}",
                    f"- **Condition Risk:** {item.condition_risk}",
                    f"- **Fraud/Scam Risk:** {item.fraud_risk}",
                    "",
                    "**Exact Seller Message:**",
                    "```text",
                    item.seller_message,
                    "```",
                    "",
                    "---",
                    "",
                ]
            )

    lines.extend(
        [
            "## Rules For Frankie",
            "",
            "1. READY_FOR_SELLER_MESSAGE requires clean sold comps plus positive max-buy room.",
            "2. NEEDS_PHOTO_CHECK means open listing photos before researching value.",
            "3. NEEDS_EXACT_MODEL means ask for or find the model plate first.",
            "4. NEEDS_SOLD_COMPS means run exact-model sold comps only.",
            "5. SKIP means do not spend more attention unless Matthew overrides.",
            "",
        ]
    )

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("=" * 80)
    print("PHOTO VERIFICATION QUEUE")
    print("=" * 80)
    sold_comp_index = load_clean_sold_comp_index()
    assessments = [assess_lead(lead, sold_comp_index) for lead in load_all_leads()]
    assessments.sort(key=lead_sort_key, reverse=True)
    write_report(assessments)
    print(f"Report generated: {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
