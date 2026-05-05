#!/usr/bin/env python3
"""
Analyze Current Lead Pool
Generate comprehensive analysis report
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

# Input files
MERCARI_CSV = Path("data/external_leads/mercari_leads.csv")
FACEBOOK_CSV = Path("data/external_leads/facebook_marketplace_leads.csv")
LEAD_INTAKE_CSV = Path("lead_intake.csv")

# Output
OUTPUT_REPORT = Path("reports/CURRENT_LEAD_ANALYSIS_001.md")

# Junk keywords
JUNK_KEYWORDS = [
    'parts only', 'for parts', 'repair', 'broken', 'not working', 'as-is',
    'manual', 'service manual', 'led kit', 'bulb', 'lamp', 'light',
    'capacitor', 'rebuild kit', 'faceplate', 'knob', 'dial',
    'remote only', 'cover only', 'cabinet only', 'case only',
    'vintage tape', 'cassette tape', 'clear file', 'folder', 'sticker',
    'poster', 'magazine', 'book', 'cd', 'vinyl record', 'album'
]

# Target models (high-value)
TARGET_MODELS = {
    'McIntosh MA 6100': {'keywords': ['mcintosh', 'ma 6100', 'ma6100', 'ma-6100'], 'floor': 500},
    'McIntosh MA 5100': {'keywords': ['mcintosh', 'ma 5100', 'ma5100', 'ma-5100'], 'floor': 500},
    'McIntosh MC 2300': {'keywords': ['mcintosh', 'mc 2300', 'mc2300', 'mc-2300'], 'floor': 800},
    'Pioneer SX-1250': {'keywords': ['pioneer', 'sx-1250', 'sx 1250', 'sx1250'], 'floor': 400},
    'Pioneer SX-1050': {'keywords': ['pioneer', 'sx-1050', 'sx 1050', 'sx1050'], 'floor': 400},
    'Marantz 2270': {'keywords': ['marantz', '2270'], 'floor': 400},
    'Marantz 2275': {'keywords': ['marantz', '2275'], 'floor': 400},
    'Technics SL-1200': {'keywords': ['technics', 'sl-1200', 'sl 1200', 'sl1200'], 'floor': 300},
    'Nakamichi Dragon': {'keywords': ['nakamichi', 'dragon'], 'floor': 1000},
    'Sansui G-9000': {'keywords': ['sansui', 'g-9000', 'g 9000', 'g9000'], 'floor': 400},
}

# Generic categories
CATEGORIES = {
    'McIntosh (other)': {'keywords': ['mcintosh'], 'floor': 300},
    'Marantz receiver': {'keywords': ['marantz', 'receiver'], 'floor': 200},
    'Pioneer receiver': {'keywords': ['pioneer', 'receiver'], 'floor': 150},
    'Technics turntable': {'keywords': ['technics', 'turntable'], 'floor': 100},
    'Vintage receiver': {'keywords': ['receiver', 'vintage'], 'floor': 100},
    'Vintage stereo': {'keywords': ['stereo', 'vintage'], 'floor': 50},
}


def load_mercari():
    """Load Mercari leads."""
    leads = []
    if not MERCARI_CSV.exists():
        return leads
    
    with open(MERCARI_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({
                'source': 'Mercari',
                'title': row.get('title', ''),
                'price': row.get('price_usd', ''),
                'url': row.get('listing_url', ''),
                'photo': row.get('image_url', ''),
                'location': 'Online',
                'condition': row.get('condition', ''),
                'item_id': row.get('item_id', ''),
            })
    return leads


def load_facebook():
    """Load Facebook Marketplace leads."""
    leads = []
    if not FACEBOOK_CSV.exists():
        return leads
    
    with open(FACEBOOK_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({
                'source': 'Facebook Marketplace',
                'title': row.get('title', ''),
                'price': row.get('price', ''),
                'url': row.get('listing_url', ''),
                'photo': row.get('photo_url', ''),
                'location': row.get('location', ''),
                'condition': '',
                'item_id': row.get('listing_url', ''),  # Use URL as ID
            })
    return leads


def is_junk(title):
    """Check if title contains junk keywords."""
    if not title:
        return True
    
    title_lower = title.lower()
    return any(kw in title_lower for kw in JUNK_KEYWORDS)


def classify_item(title):
    """Classify item by model/category."""
    if not title:
        return None, 0
    
    title_lower = title.lower()
    
    # Check target models first (high priority)
    for model, data in TARGET_MODELS.items():
        if all(kw in title_lower for kw in data['keywords']):
            return model, data['floor']
    
    # Check generic categories
    for category, data in CATEGORIES.items():
        if all(kw in title_lower for kw in data['keywords']):
            return category, data['floor']
    
    return 'Other', 0


def calculate_score(lead, category, floor):
    """Calculate preliminary opportunity score."""
    try:
        price = float(lead['price'])
    except:
        return 0
    
    # Skip if price is 0 or too low
    if price < 10:
        return 0
    
    # Base score: inverse of price (lower price = higher score)
    if floor > 0:
        # For known categories, score based on below floor
        if price < floor:
            score = (floor - price) / floor * 100
        else:
            score = 0
    else:
        # For unknown, score lower prices higher
        if price < 100:
            score = 50
        elif price < 300:
            score = 30
        else:
            score = 10
    
    # Boost for target models
    if category in TARGET_MODELS:
        score *= 2
    
    # Boost for local (Facebook)
    if lead['source'] == 'Facebook Marketplace':
        score *= 1.2
    
    return round(score, 1)


def main():
    print("="*80)
    print("ANALYZING CURRENT LEAD POOL")
    print("="*80)
    print()
    
    # Load all leads
    print("Loading data...")
    mercari_leads = load_mercari()
    facebook_leads = load_facebook()
    
    print(f"✓ Mercari: {len(mercari_leads)} leads")
    print(f"✓ Facebook: {len(facebook_leads)} leads")
    print()
    
    # Combine
    all_leads = mercari_leads + facebook_leads
    print(f"Total raw leads: {len(all_leads)}")
    print()
    
    # Deduplicate
    print("Deduplicating...")
    seen_ids = set()
    unique_leads = []
    
    for lead in all_leads:
        item_id = lead.get('item_id') or lead.get('url')
        if item_id and item_id not in seen_ids:
            seen_ids.add(item_id)
            unique_leads.append(lead)
    
    print(f"✓ After dedup: {len(unique_leads)} unique leads")
    print()
    
    # Remove junk
    print("Filtering junk categories...")
    filtered_leads = [lead for lead in unique_leads if not is_junk(lead['title'])]
    junk_count = len(unique_leads) - len(filtered_leads)
    print(f"✓ Removed {junk_count} junk items")
    print(f"✓ Clean leads: {len(filtered_leads)}")
    print()
    
    # Classify and score
    print("Classifying items...")
    for lead in filtered_leads:
        category, floor = classify_item(lead['title'])
        score = calculate_score(lead, category, floor)
        
        lead['category'] = category
        lead['price_floor'] = floor
        lead['score'] = score
    
    # Sort by score
    filtered_leads.sort(key=lambda x: x['score'], reverse=True)
    
    # Stats by category
    category_stats = defaultdict(lambda: {'count': 0, 'total_score': 0})
    for lead in filtered_leads:
        cat = lead['category']
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_score'] += lead['score']
    
    # Stats by source
    source_stats = defaultdict(int)
    for lead in filtered_leads:
        source_stats[lead['source']] += 1
    
    # Generate report
    print("Generating report...")
    
    report = []
    report.append("# Current Lead Analysis 001")
    report.append("")
    report.append("**Date:** 2026-05-04")
    report.append("**Status:** Initial analysis of Mercari + Facebook Marketplace data")
    report.append("")
    report.append("---")
    report.append("")
    
    # Summary
    report.append("## 📊 SUMMARY")
    report.append("")
    report.append(f"**Total Raw Leads:** {len(all_leads)}")
    report.append(f"**After Deduplication:** {len(unique_leads)}")
    report.append(f"**Junk Removed:** {junk_count}")
    report.append(f"**Clean Leads:** {len(filtered_leads)}")
    report.append("")
    report.append("### By Source")
    for source, count in sorted(source_stats.items()):
        report.append(f"- {source}: {count} leads")
    report.append("")
    
    # Category breakdown
    report.append("## 🎯 CATEGORY BREAKDOWN")
    report.append("")
    report.append("| Category | Count | Avg Score |")
    report.append("|----------|-------|-----------|")
    
    for cat in sorted(category_stats.keys(), key=lambda x: category_stats[x]['count'], reverse=True):
        stats = category_stats[cat]
        avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        report.append(f"| {cat} | {stats['count']} | {avg_score:.1f} |")
    
    report.append("")
    
    # Top 20 leads
    report.append("## 🔥 TOP 20 LEADS")
    report.append("")
    report.append("Ranked by preliminary opportunity score (price vs expected value).")
    report.append("")
    
    for i, lead in enumerate(filtered_leads[:20], 1):
        report.append(f"### {i}. {lead['title'][:80]}")
        report.append("")
        report.append(f"**Category:** {lead['category']}")
        report.append(f"**Price:** ${lead['price']}")
        report.append(f"**Source:** {lead['source']}")
        report.append(f"**Location:** {lead['location']}")
        report.append(f"**Score:** {lead['score']}")
        report.append("")
        report.append(f"**URL:** {lead['url']}")
        report.append("")
        
        # Decision
        score = lead['score']
        if score > 50:
            decision = "**INVESTIGATE** ⭐⭐⭐"
            reason = "High opportunity score, well below expected value"
        elif score > 25:
            decision = "**WATCH** ⭐⭐"
            reason = "Moderate opportunity, needs sold comp verification"
        else:
            decision = "**SKIP** ⭐"
            reason = "Low score or insufficient data"
        
        report.append(f"**Preliminary Decision:** {decision}")
        report.append(f"**Reason:** {reason}")
        report.append("")
        report.append("⚠️ **NEEDS_SOLD_COMPS** - Do not proceed without eBay sold comp verification")
        report.append("")
        report.append("---")
        report.append("")
    
    # Next actions
    report.append("## 🎯 NEXT ACTIONS")
    report.append("")
    report.append("### High Priority (Score >50)")
    high_priority = [l for l in filtered_leads if l['score'] > 50]
    report.append(f"**Count:** {len(high_priority)}")
    report.append("")
    report.append("**Action:** Run eBay sold comps for each. If median sold > asking price + $200, mark INVESTIGATE.")
    report.append("")
    
    report.append("### Medium Priority (Score 25-50)")
    medium_priority = [l for l in filtered_leads if 25 < l['score'] <= 50]
    report.append(f"**Count:** {len(medium_priority)}")
    report.append("")
    report.append("**Action:** Quick eBay check. If promising, run sold comps. Otherwise WATCH.")
    report.append("")
    
    report.append("### Low Priority (Score <25)")
    low_priority = [l for l in filtered_leads if l['score'] <= 25]
    report.append(f"**Count:** {len(low_priority)}")
    report.append("")
    report.append("**Action:** SKIP most. Only investigate if local and can inspect in person.")
    report.append("")
    
    # Warnings
    report.append("## ⚠️ IMPORTANT WARNINGS")
    report.append("")
    report.append("**ALL leads marked NEEDS_SOLD_COMPS**")
    report.append("")
    report.append("DO NOT:")
    report.append("- ❌ Call anything a \"BUY\" without sold comps")
    report.append("- ❌ Calculate margins from active listings only")
    report.append("- ❌ Contact seller without verified sold comps")
    report.append("- ❌ Make purchase decisions from this report alone")
    report.append("")
    report.append("DO:")
    report.append("- ✓ Run eBay sold comps for top 20 leads")
    report.append("- ✓ Verify condition with photos")
    report.append("- ✓ Calculate fees + shipping before margin estimate")
    report.append("- ✓ Output INVESTIGATE / WATCH / SKIP only")
    report.append("")
    
    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ Report generated: {OUTPUT_REPORT}")
    print()
    print("Summary:")
    print(f"  Total clean leads: {len(filtered_leads)}")
    print(f"  High priority (>50): {len(high_priority)}")
    print(f"  Medium priority (25-50): {len(medium_priority)}")
    print(f"  Low priority (<25): {len(low_priority)}")
    print()
    print(f"Top lead: {filtered_leads[0]['title'][:60]} (score: {filtered_leads[0]['score']})")
    print()


if __name__ == "__main__":
    main()
