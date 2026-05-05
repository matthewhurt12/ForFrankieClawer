#!/usr/bin/env python3
"""
Equipment-Only Lead Analysis
Clean the lead pool by filtering out apparel, parts, accessories
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

# Input files
MERCARI_CSV = Path("data/external_leads/mercari_leads.csv")
FACEBOOK_CSV = Path("data/external_leads/facebook_marketplace_leads.csv")

# Output
OUTPUT_REPORT = Path("reports/EQUIPMENT_ONLY_LEAD_REVIEW_001.md")

# Hard reject keywords (immediate disqualification)
REJECT_KEYWORDS = [
    # Apparel
    'shirt', 't-shirt', 'tee', 'hoodie', 'hat', 'cap', 'clothing', 'apparel',
    # Accessories
    'sticker', 'decal', 'pin', 'enamel', 'badge', 'poster', 'sign', 'art', 'print',
    # Paper goods
    'manual', 'catalog', 'brochure', 'service manual', 'pdf', 'book', 'magazine',
    # Repair/parts
    'lamp', 'led', 'bulb', 'kit', 'recap', 'repair kit', 'rebuild kit',
    'switch', 'knob', 'faceplate', 'glass', 'dial', 'meter', 'button',
    'cabinet only', 'case only', 'wood case only', 'remote only', 'remote control only',
    'feet', 'cord', 'cable', 'plug', 'jumper',
    'capacitor', 'transistor', 'fuse', 'relay', 'board',
    'parts', 'for parts', 'parts only', 'part only', 'as-is',
    # Non-audio
    'folder', 'file', 'anime', 'manga', 'card', 'baseball', 'sports'
]

# Equipment-positive keywords (strong indicators of real equipment)
EQUIPMENT_KEYWORDS = [
    'receiver', 'stereo receiver', 'am/fm receiver',
    'integrated amplifier', 'amplifier', 'amp', 'power amp',
    'turntable', 'record player', 'direct drive',
    'cassette deck', 'tape deck', 'dual cassette',
    'reel to reel', 'reel-to-reel',
    'speakers', 'speaker pair', 'speaker system',
    'preamp', 'preamplifier', 'phono preamp',
    'tuner', 'am/fm tuner',
    'equalizer', 'eq',
    'cd player', 'compact disc'
]

# Equipment context words (supporting evidence)
EQUIPMENT_CONTEXT = [
    'working', 'tested', 'serviced', 'recapped', 'restored',
    'excellent condition', 'mint', 'near mint',
    'watts', 'wpc', 'channels',
    'vintage stereo', 'vintage audio', 'hi-fi', 'hifi'
]

# Target models with price floors
TARGET_MODELS = {
    'McIntosh MA 6100': {'keywords': ['mcintosh', 'ma', '6100'], 'floor': 500},
    'McIntosh MA 5100': {'keywords': ['mcintosh', 'ma', '5100'], 'floor': 500},
    'McIntosh MC 2300': {'keywords': ['mcintosh', 'mc', '2300'], 'floor': 800},
    'Pioneer SX-1250': {'keywords': ['pioneer', 'sx-1250', 'sx 1250'], 'floor': 800},
    'Pioneer SX-1050': {'keywords': ['pioneer', 'sx-1050', 'sx 1050'], 'floor': 400},
    'Pioneer SX-950': {'keywords': ['pioneer', 'sx-950', 'sx 950'], 'floor': 350},
    'Pioneer SX-850': {'keywords': ['pioneer', 'sx-850', 'sx 850'], 'floor': 300},
    'Pioneer SX-770': {'keywords': ['pioneer', 'sx-770', 'sx 770'], 'floor': 250},
    'Pioneer SX-650': {'keywords': ['pioneer', 'sx-650', 'sx 650'], 'floor': 200},
    'Marantz 2270': {'keywords': ['marantz', '2270'], 'floor': 400},
    'Marantz 2275': {'keywords': ['marantz', '2275'], 'floor': 500},
    'Marantz 2245': {'keywords': ['marantz', '2245'], 'floor': 300},
    'Technics SL-1200': {'keywords': ['technics', 'sl-1200', 'sl 1200'], 'floor': 300},
    'Nakamichi Dragon': {'keywords': ['nakamichi', 'dragon'], 'floor': 1000},
    'Sansui G-9000': {'keywords': ['sansui', 'g-9000', 'g 9000'], 'floor': 400},
}

# Generic categories
GENERIC_CATEGORIES = {
    'McIntosh amplifier': {'keywords': ['mcintosh', 'amp'], 'floor': 300},
    'Marantz receiver': {'keywords': ['marantz', 'receiver'], 'floor': 200},
    'Pioneer receiver': {'keywords': ['pioneer', 'receiver'], 'floor': 150},
    'Technics turntable': {'keywords': ['technics', 'turntable'], 'floor': 100},
    'Nakamichi deck': {'keywords': ['nakamichi', 'deck'], 'floor': 200},
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
                'location': 'Online',
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
                'location': row.get('location', ''),
                'item_id': row.get('listing_url', ''),
            })
    return leads


def classify_item(title):
    """
    Classify item type.
    Returns: (classification, equipment_type, floor)
    """
    if not title:
        return 'UNKNOWN', None, 0
    
    title_lower = title.lower()
    
    # Check hard rejects first
    for keyword in REJECT_KEYWORDS:
        if keyword in title_lower:
            # Determine reject category
            if keyword in ['shirt', 't-shirt', 'tee', 'hoodie', 'hat']:
                return 'APPAREL', None, 0
            elif keyword in ['manual', 'catalog', 'brochure', 'pdf', 'book']:
                return 'PAPER_GOODS', None, 0
            elif keyword in ['sticker', 'decal', 'pin', 'poster', 'sign']:
                return 'ACCESSORY', None, 0
            else:
                return 'PARTS_REPAIR', None, 0
    
    # Check for equipment-positive keywords
    has_equipment_keyword = any(kw in title_lower for kw in EQUIPMENT_KEYWORDS)
    has_equipment_context = any(kw in title_lower for kw in EQUIPMENT_CONTEXT)
    
    # Check target models
    for model, data in TARGET_MODELS.items():
        if all(kw in title_lower for kw in data['keywords']):
            if has_equipment_keyword or 'working' in title_lower or 'tested' in title_lower:
                return 'FULL_EQUIPMENT', model, data['floor']
            elif len(title_lower) > 50 or has_equipment_context:
                # Longer titles more likely to be equipment
                return 'LIKELY_EQUIPMENT', model, data['floor']
            else:
                # Model name but no equipment context - could be part/accessory
                return 'UNKNOWN', model, data['floor']
    
    # Check generic categories
    for category, data in GENERIC_CATEGORIES.items():
        if all(kw in title_lower for kw in data['keywords']):
            if has_equipment_keyword:
                return 'FULL_EQUIPMENT', category, data['floor']
            else:
                return 'LIKELY_EQUIPMENT', category, data['floor']
    
    # Has equipment keyword but no specific model
    if has_equipment_keyword:
        if 'receiver' in title_lower:
            return 'LIKELY_EQUIPMENT', 'Generic receiver', 100
        elif 'amplifier' in title_lower or 'amp' in title_lower:
            return 'LIKELY_EQUIPMENT', 'Generic amplifier', 100
        elif 'turntable' in title_lower:
            return 'LIKELY_EQUIPMENT', 'Generic turntable', 50
        else:
            return 'LIKELY_EQUIPMENT', 'Generic equipment', 50
    
    return 'UNKNOWN', None, 0


def calculate_score(lead, classification, equipment_type, floor):
    """Calculate opportunity score for EQUIPMENT only."""
    if classification not in ['FULL_EQUIPMENT', 'LIKELY_EQUIPMENT']:
        return 0
    
    try:
        price = float(lead['price'])
    except:
        return 0
    
    if price < 10 or price > 10000:
        return 0
    
    # Base score from price vs floor
    if floor > 0 and price < floor:
        # Below expected value - high opportunity
        percent_below = (floor - price) / floor
        base_score = percent_below * 100
    else:
        # At or above floor
        if price < 200:
            base_score = 30
        elif price < 500:
            base_score = 20
        else:
            base_score = 10
    
    # Multipliers
    if classification == 'FULL_EQUIPMENT':
        base_score *= 1.5
    
    # Target model bonus
    if equipment_type and equipment_type in TARGET_MODELS:
        base_score *= 2
    
    # Local pickup bonus
    if lead['source'] == 'Facebook Marketplace':
        base_score *= 1.3
    
    # Working condition bonus
    title_lower = lead['title'].lower()
    if any(kw in title_lower for kw in ['working', 'tested', 'serviced', 'excellent']):
        base_score *= 1.2
    
    return round(base_score, 1)


def main():
    print("="*80)
    print("EQUIPMENT-ONLY LEAD ANALYSIS")
    print("="*80)
    print()
    
    # Load data
    print("Loading raw leads...")
    mercari_leads = load_mercari()
    facebook_leads = load_facebook()
    all_leads = mercari_leads + facebook_leads
    
    print(f"✓ Mercari: {len(mercari_leads)}")
    print(f"✓ Facebook: {len(facebook_leads)}")
    print(f"✓ Total raw: {len(all_leads)}")
    print()
    
    # Deduplicate
    print("Deduplicating...")
    seen = set()
    unique = []
    for lead in all_leads:
        item_id = lead.get('item_id') or lead.get('url')
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique.append(lead)
    
    print(f"✓ Unique: {len(unique)}")
    print()
    
    # Classify all leads
    print("Classifying items...")
    classified = {
        'FULL_EQUIPMENT': [],
        'LIKELY_EQUIPMENT': [],
        'ACCESSORY': [],
        'APPAREL': [],
        'PAPER_GOODS': [],
        'PARTS_REPAIR': [],
        'UNKNOWN': []
    }
    
    for lead in unique:
        classification, equipment_type, floor = classify_item(lead['title'])
        score = calculate_score(lead, classification, equipment_type, floor)
        
        lead['classification'] = classification
        lead['equipment_type'] = equipment_type
        lead['price_floor'] = floor
        lead['score'] = score
        
        classified[classification].append(lead)
    
    # Stats
    for cat, items in classified.items():
        print(f"  {cat}: {len(items)}")
    print()
    
    # Equipment only (FULL + LIKELY)
    equipment_leads = classified['FULL_EQUIPMENT'] + classified['LIKELY_EQUIPMENT']
    equipment_leads.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Clean equipment leads: {len(equipment_leads)}")
    print(f"False positives removed: {len(unique) - len(equipment_leads)}")
    print()
    
    # Generate report
    print("Generating report...")
    
    report = []
    report.append("# Equipment-Only Lead Review 001")
    report.append("")
    report.append("**Date:** 2026-05-04")
    report.append("**Purpose:** Clean lead pool by removing apparel, parts, accessories")
    report.append("")
    report.append("---")
    report.append("")
    
    # Summary
    report.append("## 📊 SUMMARY")
    report.append("")
    report.append(f"**Total Raw Leads:** {len(all_leads)}")
    report.append(f"**After Deduplication:** {len(unique)}")
    report.append(f"**Clean Equipment Leads:** {len(equipment_leads)}")
    report.append(f"**False Positives Removed:** {len(unique) - len(equipment_leads)}")
    report.append("")
    
    # Classification breakdown
    report.append("## 🗂️ CLASSIFICATION BREAKDOWN")
    report.append("")
    report.append("| Classification | Count | Description |")
    report.append("|----------------|-------|-------------|")
    report.append(f"| FULL_EQUIPMENT | {len(classified['FULL_EQUIPMENT'])} | Confirmed receivers/amps/turntables |")
    report.append(f"| LIKELY_EQUIPMENT | {len(classified['LIKELY_EQUIPMENT'])} | Probable equipment, needs verification |")
    report.append(f"| APPAREL | {len(classified['APPAREL'])} | T-shirts, hoodies, hats |")
    report.append(f"| ACCESSORY | {len(classified['ACCESSORY'])} | Pins, stickers, posters |")
    report.append(f"| PAPER_GOODS | {len(classified['PAPER_GOODS'])} | Manuals, catalogs, brochures |")
    report.append(f"| PARTS_REPAIR | {len(classified['PARTS_REPAIR'])} | Parts, switches, knobs |")
    report.append(f"| UNKNOWN | {len(classified['UNKNOWN'])} | Uncategorized |")
    report.append("")
    
    # By source
    equipment_by_source = defaultdict(int)
    for lead in equipment_leads:
        equipment_by_source[lead['source']] += 1
    
    report.append("### Equipment by Source")
    for source, count in sorted(equipment_by_source.items()):
        report.append(f"- {source}: {count} leads")
    report.append("")
    
    # Top 25 equipment
    report.append("## 🔥 TOP 25 EQUIPMENT LEADS")
    report.append("")
    report.append("Ranked by opportunity score (EQUIPMENT ONLY).")
    report.append("")
    
    for i, lead in enumerate(equipment_leads[:25], 1):
        report.append(f"### {i}. {lead['title'][:100]}")
        report.append("")
        report.append(f"**Classification:** {lead['classification']}")
        report.append(f"**Equipment Type:** {lead['equipment_type'] or 'Generic'}")
        report.append(f"**Price:** ${lead['price']}")
        report.append(f"**Source:** {lead['source']}")
        report.append(f"**Location:** {lead['location']}")
        report.append(f"**Score:** {lead['score']}")
        report.append("")
        
        if lead['url']:
            report.append(f"**URL:** {lead['url']}")
            report.append("")
        
        # Decision
        score = lead['score']
        price = float(lead['price']) if lead['price'] else 0
        
        if score > 80 and price < 500:
            decision = "**INVESTIGATE** ⭐⭐⭐"
            reason = "High score, below expected value, likely strong opportunity"
        elif score > 50:
            decision = "**WATCH** ⭐⭐"
            reason = "Good score, needs sold comp verification"
        else:
            decision = "**SKIP** ⭐"
            reason = "Lower priority, investigate only if local and can inspect"
        
        report.append(f"**Preliminary Decision:** {decision}")
        report.append(f"**Reason:** {reason}")
        report.append("")
        report.append("⚠️ **NEEDS_SOLD_COMPS** - Do not proceed without eBay sold comp verification")
        report.append("")
        report.append("---")
        report.append("")
    
    # Top 5 urgent manual checks
    report.append("## ⚡ TOP 5 URGENT MANUAL CHECKS")
    report.append("")
    report.append("Highest opportunity equipment requiring immediate attention:")
    report.append("")
    
    urgent = [l for l in equipment_leads[:10] if l['score'] > 80][:5]
    
    for i, lead in enumerate(urgent, 1):
        report.append(f"### {i}. {lead['equipment_type']} - ${lead['price']}")
        report.append(f"**Title:** {lead['title'][:80]}")
        report.append(f"**Location:** {lead['location']}")
        report.append(f"**Score:** {lead['score']}")
        if lead['url']:
            report.append(f"**URL:** {lead['url'][:80]}")
        report.append("")
        report.append("**Action Items:**")
        report.append("1. Run eBay sold comps immediately")
        report.append("2. Verify condition from photos")
        report.append("3. If margin >$200: Contact seller with questions")
        report.append("4. If local: Schedule inspection ASAP")
        report.append("")
    
    if not urgent:
        report.append("*(No leads scored above 80 - review top 10 manually)*")
        report.append("")
    
    # Category stats
    report.append("## 📈 EQUIPMENT CATEGORY BREAKDOWN")
    report.append("")
    
    equipment_by_type = defaultdict(lambda: {'count': 0, 'total_score': 0, 'avg_price': []})
    for lead in equipment_leads:
        etype = lead['equipment_type'] or 'Other'
        equipment_by_type[etype]['count'] += 1
        equipment_by_type[etype]['total_score'] += lead['score']
        try:
            equipment_by_type[etype]['avg_price'].append(float(lead['price']))
        except:
            pass
    
    report.append("| Equipment Type | Count | Avg Score | Avg Price |")
    report.append("|----------------|-------|-----------|-----------|")
    
    for etype in sorted(equipment_by_type.keys(), key=lambda x: equipment_by_type[x]['count'], reverse=True)[:15]:
        stats = equipment_by_type[etype]
        avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        avg_price = sum(stats['avg_price']) / len(stats['avg_price']) if stats['avg_price'] else 0
        report.append(f"| {etype} | {stats['count']} | {avg_score:.1f} | ${avg_price:.0f} |")
    
    report.append("")
    
    # Next actions
    report.append("## 🎯 NEXT ACTIONS")
    report.append("")
    report.append("### Immediate (Top 5 Urgent)")
    report.append("1. Run eBay sold comps for top 5 leads")
    report.append("2. Contact sellers for photos/questions")
    report.append("3. Schedule local inspections if applicable")
    report.append("")
    report.append("### High Priority (Score >80)")
    high_pri = [l for l in equipment_leads if l['score'] > 80]
    report.append(f"**Count:** {len(high_pri)}")
    report.append("**Action:** Run sold comps, verify condition, calculate margins")
    report.append("")
    report.append("### Medium Priority (Score 50-80)")
    med_pri = [l for l in equipment_leads if 50 <= l['score'] <= 80]
    report.append(f"**Count:** {len(med_pri)}")
    report.append("**Action:** Quick eBay check, watch for price drops")
    report.append("")
    report.append("### Low Priority (Score <50)")
    low_pri = [l for l in equipment_leads if l['score'] < 50]
    report.append(f"**Count:** {len(low_pri)}")
    report.append("**Action:** Skip unless local and can inspect easily")
    report.append("")
    
    # Warnings
    report.append("## ⚠️ CRITICAL WARNINGS")
    report.append("")
    report.append("**ALL LEADS MARKED NEEDS_SOLD_COMPS**")
    report.append("")
    report.append("**DO NOT:**")
    report.append("- ❌ Call anything a \"BUY\" without sold comps + condition verification")
    report.append("- ❌ Calculate margins from active listings only")
    report.append("- ❌ Contact seller without verified sold comps")
    report.append("- ❌ Trust scoring alone - always verify item type manually")
    report.append("")
    report.append("**DO:**")
    report.append("- ✓ Run eBay sold comps for every lead before action")
    report.append("- ✓ Verify actual equipment (not parts/apparel) from photos")
    report.append("- ✓ Calculate fees ($123 = 13% of $950) + shipping ($20-50)")
    report.append("- ✓ Output INVESTIGATE / WATCH / SKIP only (never BUY)")
    report.append("")
    
    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ Report generated: {OUTPUT_REPORT}")
    print()
    print("Summary:")
    print(f"  Clean equipment: {len(equipment_leads)}")
    print(f"  High priority (>80): {len(high_pri)}")
    print(f"  Medium priority (50-80): {len(med_pri)}")
    print(f"  Low priority (<50): {len(low_pri)}")
    print()
    if equipment_leads:
        print(f"Top lead: {equipment_leads[0]['title'][:60]}")
        print(f"  Price: ${equipment_leads[0]['price']}")
        print(f"  Score: {equipment_leads[0]['score']}")
    print()


if __name__ == "__main__":
    main()
