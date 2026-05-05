#!/usr/bin/env python3
"""
Deal Desk Review - action cards only.

This report deliberately does not use broad active eBay listing medians as
profit proof. It ranks leads for human action and only prints a max buy price
when clean sold comps are attached.
"""

from __future__ import annotations

from collections import Counter, defaultdict
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


OUTPUT_REPORT = Path("reports/DEAL_DESK_REVIEW_001.md")
PHOTO_QUEUE_REPORT = Path("reports/PHOTO_VERIFICATION_QUEUE_001.md")


def assessment_summary_line(item: LeadAssessment) -> str:
    lead = item.lead
    model = item.model.name or "Unknown"
    return (
        f"- **{lead.title[:90]}** | {lead.source} | {lead.location or 'unknown location'} | "
        f"{money(lead.price)} | {model} | {item.classification} | Score {item.score}"
    )


def terminal_safe(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def lead_card(item: LeadAssessment, rank: int) -> list[str]:
    lead = item.lead
    model = item.model.name or "Unknown"
    max_buy = "Not estimated - clean sold comps required"
    if item.max_buy_price is not None:
        max_buy = money(item.max_buy_price)

    lines = [
        f"### {rank}. {lead.title[:110]}",
        "",
        f"- **Title:** {lead.title}",
        f"- **Source:** {lead.source}",
        f"- **Location:** {lead.location or 'Unknown'}",
        f"- **Asking Price:** {money(lead.price)}",
        f"- **Listing URL:** {lead.url or 'Missing'}",
        f"- **Suspected Exact Model:** {model}",
        f"- **Model Confidence:** {item.model.confidence}/100 - {item.model.reason or 'No model signal'}",
        f"- **Lead Confidence Score:** {item.score}/100",
        f"- **What Makes It Interesting:** {item.interesting}",
        f"- **What Could Make It Junk:** {item.junk_risk}",
        f"- **Photo/Model Verification Needed:** {item.photo_verification}",
        f"- **Sold Comp Status:** {item.sold_comp_status}",
        f"- **Active Context Status:** {item.active_context_status}",
        f"- **Condition Risk:** {item.condition_risk}",
        f"- **Fraud/Scam Risk:** {item.fraud_risk}",
        f"- **Estimated Max Buy Price:** {max_buy}",
        f"- **Verdict:** {item.verdict}",
        "",
    ]

    if item.underwriting_notes:
        lines.append("**Underwriting Notes:**")
        for note in item.underwriting_notes:
            lines.append(f"- {note}")
        lines.append("")

    lines.extend(
        [
            "**Exact Seller Message:**",
            "```text",
            item.seller_message,
            "```",
            "",
            "---",
            "",
        ]
    )
    return lines


def build_photo_queue_report(assessments: list[LeadAssessment]) -> None:
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
        has_positive_underwriting = (
            item.max_buy_price is not None
            and item.lead.price is not None
            and item.max_buy_price > item.lead.price
        )
        if item.verdict == "SKIP":
            grouped["SKIP"].append(item)
        elif (
            item.classification == "NEEDS_SOLD_COMPS"
            and item.sold_comp_status == "VALID_SOLD_COMPS_ATTACHED"
            and has_positive_underwriting
        ):
            grouped["READY_FOR_SELLER_MESSAGE"].append(item)
        elif item.sold_comp_status == "VALID_SOLD_COMPS_ATTACHED" and not has_positive_underwriting:
            grouped["WATCH"].append(item)
        elif item.classification in ["NEEDS_PHOTO_CHECK", "NEEDS_EXACT_MODEL", "NEEDS_SOLD_COMPS"]:
            grouped[item.classification].append(item)
        else:
            grouped["WATCH"].append(item)

    lines = [
        "# Photo Verification Queue 001",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Purpose:** Open only the listings that need visual/model confirmation before sold-comp work.",
        "",
        "No profit estimates appear here unless clean sold comps have already been attached.",
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

        limit = 15 if category != "SKIP" else 20
        lines.extend([f"## {category}", ""])
        if category == "READY_FOR_SELLER_MESSAGE":
            lines.append("Exact model, valid sold comps, and positive max-buy room are present. Seller message is allowed.")
        elif category == "NEEDS_PHOTO_CHECK":
            lines.append("Exact model token exists, but the listing must be opened to prove it is a full unit.")
        elif category == "NEEDS_EXACT_MODEL":
            lines.append("Looks like equipment, but value work is blocked until the model number is known.")
        elif category == "NEEDS_SOLD_COMPS":
            lines.append("Exact model and likely full-unit status exist. Run sold comps before underwriting.")
        elif category == "WATCH":
            lines.append("Keep these around, but do not spend deep research time yet.")
        elif category == "SKIP":
            lines.append("Rejected or low-signal leads with reasons.")
        lines.append("")

        for i, item in enumerate(items[:limit], 1):
            lead = item.lead
            lines.extend(
                [
                    f"### {i}. {lead.title[:100]}",
                    f"- **Source:** {lead.source}",
                    f"- **Price:** {money(lead.price)}",
                    f"- **Location:** {lead.location or 'Unknown'}",
                    f"- **URL:** {lead.url or 'Missing'}",
                    f"- **Suspected Model:** {item.model.name or 'Unknown'}",
                    f"- **Confidence:** {item.score}/100",
                    f"- **Why It Matters:** {item.interesting}",
                    f"- **Junk Risk:** {item.junk_risk}",
                    f"- **Photo Check:** {item.photo_verification}",
                    f"- **Sold Comp Status:** {item.sold_comp_status}",
                    f"- **Verdict:** {item.verdict}",
                    "",
                    "**Seller Message:**",
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
            "## Operating Rules",
            "",
            "1. Do not estimate profit from active listings.",
            "2. Do not run sold comps on generic searches like `Pioneer receiver`.",
            "3. Use sold comps only after exact model and full-unit status are confirmed.",
            "4. Fewer than 3 clean full-unit sold comps means LOW_CONFIDENCE.",
            "5. Verdict vocabulary is limited to INVESTIGATE / WATCH / SKIP.",
            "",
        ]
    )

    PHOTO_QUEUE_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PHOTO_QUEUE_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("=" * 80)
    print("DEAL DESK REVIEW - ACTIONABLE LEADS ONLY")
    print("=" * 80)
    print()

    sold_comp_index = load_clean_sold_comp_index()
    leads = load_all_leads()
    print(f"Loaded unique leads: {len(leads)}")
    print(f"Models with clean sold comp summaries: {len(sold_comp_index)}")

    assessments = [assess_lead(lead, sold_comp_index) for lead in leads]
    assessments.sort(key=lead_sort_key, reverse=True)

    immediate = [a for a in assessments if a.verdict == "INVESTIGATE"][:5]
    watchlist = [a for a in assessments if a.verdict == "WATCH"][:10]
    skipped = [a for a in assessments if a.verdict == "SKIP"]

    class_counts = Counter(a.classification for a in assessments)
    verdict_counts = Counter(a.verdict for a in assessments)
    skip_reasons = Counter(a.reject_reason or a.junk_risk for a in skipped)

    lines = [
        "# Deal Desk Review 001",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Purpose:** Top action recommendations for retro tech and vintage audio arbitrage leads.",
        "",
        "This report does not use active listing medians as resale proof. Profit and max-buy math only appear when clean sold comps are attached.",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Unique Leads Loaded:** {len(leads)}",
        f"- **Top Immediate Review Leads:** {len(immediate)}",
        f"- **Watchlist Leads:** {len(watchlist)}",
        f"- **Skipped Leads:** {len(skipped)}",
        f"- **Clean Sold Comp Models Available:** {len(sold_comp_index)}",
        "",
        "### Verdict Breakdown",
        "",
    ]

    for verdict in ["INVESTIGATE", "WATCH", "SKIP"]:
        lines.append(f"- **{verdict}:** {verdict_counts.get(verdict, 0)}")
    lines.extend(["", "### Classification Breakdown", ""])
    for classification, count in class_counts.most_common():
        lines.append(f"- **{classification}:** {count}")
    lines.append("")

    lines.extend(["## Top 5 Immediate Review Leads", ""])
    if immediate:
        for i, item in enumerate(immediate, 1):
            lines.extend(lead_card(item, i))
    else:
        lines.append("No leads currently qualify for immediate review. That is acceptable; action quality beats lead volume.")
        lines.append("")

    lines.extend(["## Top 10 Watchlist Leads", ""])
    if watchlist:
        for i, item in enumerate(watchlist, 1):
            lines.extend(lead_card(item, i))
    else:
        lines.append("No watchlist leads after filtering.")
        lines.append("")

    lines.extend(["## Skipped Leads With Reasons", ""])
    lines.append(f"**Total Skipped:** {len(skipped)}")
    lines.append("")
    lines.append("### Common Skip Reasons")
    lines.append("")
    for reason, count in skip_reasons.most_common(12):
        lines.append(f"- **{count}:** {reason}")
    lines.append("")

    if skipped:
        lines.append("### Sample Skips")
        lines.append("")
        for item in skipped[:25]:
            lines.append(assessment_summary_line(item))
            lines.append(f"  Reason: {item.reject_reason or item.junk_risk}")
        lines.append("")

    lines.extend(
        [
            "## Hard Rules For Frankie",
            "",
            "- Never output BUY.",
            "- Never output PROFIT unless sold comp status is VALID_SOLD_COMPS_ATTACHED.",
            "- Never use active eBay listing medians as resale value.",
            "- Never run sold comps on generic phrases such as `Pioneer receiver`, `Marantz stereo`, or `Technics turntable`.",
            "- Exact model plus full-unit evidence comes before sold comps.",
            "- Fewer than 3 valid full-unit sold comps means LOW_CONFIDENCE.",
            "",
            "## Suggested Command Flow",
            "",
            "```bash",
            "python scripts/clean_ebay_sold_comps.py --input data/sold_comps/ebay_sold_test.json",
            "python scripts/deal_desk_review.py",
            "```",
            "",
        ]
    )

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    build_photo_queue_report(assessments)

    print(f"Report generated: {OUTPUT_REPORT}")
    print(f"Photo queue generated: {PHOTO_QUEUE_REPORT}")
    print()
    print("Top immediate leads:")
    for i, item in enumerate(immediate, 1):
        title = terminal_safe(item.lead.title[:72])
        print(f"  {i}. {title} | {money(item.lead.price)} | {item.model.name}")
    print()


if __name__ == "__main__":
    main()
