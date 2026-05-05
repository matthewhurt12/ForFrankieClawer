#!/usr/bin/env python3
"""
Deal Desk Review - Top Actionable Leads Only
Deep research on 5-10 leads worth immediate attention
"""

import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Input files
EQUIPMENT_LEADS = Path("data/external_leads/equipment_only_leads.json")
MERCARI_CSV = Path("data/external_leads/mercari_leads.csv")
FACEBOOK_CSV = Path("data/external_leads/facebook_marketplace_leads.csv")

# Output
OUTPUT_REPORT = Path("reports/DEAL_DESK_REVIEW_001.md")

# Manual verification - titles that are definitely NOT full equipment
MANUAL_REJECTS = [
    'volume function', 'volume control', 'switch', 'knob', 'button',
    'hinge mount plates', 'hinge plates', 'mount plates',
    'bias button', 'level button', 'function button',
    'catalog', 'manual', 'brochure', 'jumper plug',
    'relay', 'feet', 'wood case only', 'cabinet only',
    't-shirt', 'tee', 'pin', 'enamel', 'logo',
]


def load_equipment_leads():
    """Load the equipment-only filtered leads."""
    # Load from CSVs since we just generated them
    mercari = []
    facebook = []
    
    if MERCARI_CSV.exists():
        with open(MERCARI_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mercari.append({
                    'source': 'Mercari',
                    'title': row.get('title', ''),
                    'price': row.get('price_usd', ''),
                    'url': row.get('listing_url', '') or row.get('url', ''),
                    'location': 'Online',
                })
    
    if FACEBOOK_CSV.exists():
        with open(FACEBOOK_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                facebook.append({
                    'source': 'Facebook Marketplace',
                    'title': row.get('title', ''),
                    'price': row.get('price', ''),
                    'url': row.get('listing_url', '') or row.get('url', ''),
                    'location': row.get('location', ''),
                })
    
    return mercari + facebook


def is_full_equipment(title):
    """Manual verification if title is full equipment."""
    if not title:
        return False
    
    title_lower = title.lower()
    
    # Reject known parts/accessories
    for reject in MANUAL_REJECTS:
        if reject in title_lower:
            return False
    
    # Must have equipment indicators
    equipment_words = ['receiver', 'amplifier', 'amp', 'turntable', 'deck', 'stereo']
    has_equipment = any(word in title_lower for word in equipment_words)
    
    # Working/tested is strong signal
    working_words = ['working', 'tested', 'serviced', 'excellent']
    has_working = any(word in title_lower for word in working_words)
    
    return has_equipment or has_working


def classify_model(title):
    """Identify specific model from title."""
    title_lower = title.lower()
    
    # Target models
    if 'mcintosh' in title_lower:
        if 'ma 6100' in title_lower or 'ma6100' in title_lower:
            return 'McIntosh MA 6100', 'mcintosh ma 6100'
        elif 'ma 5100' in title_lower or 'ma5100' in title_lower:
            return 'McIntosh MA 5100', 'mcintosh ma 5100'
        elif 'mc 2300' in title_lower or 'mc2300' in title_lower:
            return 'McIntosh MC 2300', 'mcintosh mc 2300'
        else:
            return 'McIntosh (other)', 'mcintosh amplifier'
    
    if 'pioneer' in title_lower:
        if 'sx-1250' in title_lower or 'sx 1250' in title_lower:
            return 'Pioneer SX-1250', 'pioneer sx-1250'
        elif 'sx-1050' in title_lower or 'sx 1050' in title_lower:
            return 'Pioneer SX-1050', 'pioneer sx-1050'
        elif 'sx-950' in title_lower or 'sx 950' in title_lower:
            return 'Pioneer SX-950', 'pioneer sx-950'
        elif 'sx-850' in title_lower or 'sx 850' in title_lower:
            return 'Pioneer SX-850', 'pioneer sx-850'
        elif 'sx-770' in title_lower or 'sx 770' in title_lower:
            return 'Pioneer SX-770', 'pioneer sx-770'
        elif 'sx-650' in title_lower or 'sx 650' in title_lower:
            return 'Pioneer SX-650', 'pioneer sx-650'
        else:
            return 'Pioneer receiver', 'pioneer receiver'
    
    if 'marantz' in title_lower:
        if '2270' in title_lower:
            return 'Marantz 2270', 'marantz 2270'
        elif '2275' in title_lower:
            return 'Marantz 2275', 'marantz 2275'
        elif '2245' in title_lower:
            return 'Marantz 2245', 'marantz 2245'
        else:
            return 'Marantz receiver', 'marantz receiver'
    
    if 'technics' in title_lower and ('sl-1200' in title_lower or 'sl 1200' in title_lower):
        return 'Technics SL-1200', 'technics sl-1200'
    
    if 'nakamichi' in title_lower and 'dragon' in title_lower:
        return 'Nakamichi Dragon', 'nakamichi dragon'
    
    return None, None


def get_ebay_active_context(search_term):
    """Get eBay active listings using the existing script."""
    try:
        # Run ebay_active_context.py
        result = subprocess.run(
            ['python3', 'ebay_active_context.py', search_term],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path.cwd())
        )
        
        # Parse output for price range
        output = result.stdout
        
        # Look for price info in output
        prices = []
        for line in output.split('\n'):
            if '$' in line and any(word in line.lower() for word in ['price', 'range', 'median']):
                # Extract numbers
                import re
                nums = re.findall(r'\$([0-9,]+(?:\.[0-9]{2})?)', line)
                prices.extend([float(n.replace(',', '')) for n in nums])
        
        if prices:
            return {
                'min': min(prices),
                'max': max(prices),
                'median': sorted(prices)[len(prices)//2] if prices else 0,
                'count': len(prices)
            }
        
        # Fallback - no data
        return {'min': 0, 'max': 0, 'median': 0, 'count': 0}
        
    except Exception as e:
        print(f"  eBay lookup failed for {search_term}: {e}")
        return {'min': 0, 'max': 0, 'median': 0, 'count': 0}


def calculate_deal_metrics(lead, model_name, search_term):
    """Calculate all deal metrics with eBay context."""
    try:
        asking_price = float(lead['price'])
    except:
        return None
    
    # Get eBay active context
    print(f"  Looking up eBay context for: {search_term}")
    ebay_data = get_ebay_active_context(search_term)
    
    # Estimate fees and shipping
    # eBay: 13% (10% FVF + 3% payment)
    # Shipping: $20-50 depending on item
    if 'turntable' in search_term:
        shipping_cost = 25
    elif 'receiver' in search_term or 'amplifier' in search_term:
        shipping_cost = 35
    else:
        shipping_cost = 30
    
    # Local pickup (Facebook) = no shipping
    if lead['source'] == 'Facebook Marketplace':
        shipping_cost = 0
    
    # Calculate net profit at different sell prices
    if ebay_data['median'] > 0:
        sell_price = ebay_data['median']
    elif ebay_data['max'] > 0:
        sell_price = ebay_data['max'] * 0.8  # Conservative
    else:
        sell_price = asking_price * 1.5  # Guess
    
    fees = sell_price * 0.13
    net_profit = sell_price - asking_price - fees - shipping_cost
    
    # Max buy price (work backwards from $200 min profit)
    min_profit = 200
    max_buy = sell_price - min_profit - fees - shipping_cost
    
    return {
        'asking_price': asking_price,
        'ebay_min': ebay_data['min'],
        'ebay_max': ebay_data['max'],
        'ebay_median': ebay_data['median'],
        'ebay_count': ebay_data['count'],
        'estimated_sell': sell_price,
        'fees': fees,
        'shipping': shipping_cost,
        'net_profit': net_profit,
        'max_buy_price': max(max_buy, asking_price * 0.7),  # At least 30% off
        'roi_percent': (net_profit / asking_price * 100) if asking_price > 0 else 0
    }


def generate_seller_message(lead, model_name):
    """Generate exact message to send seller."""
    if lead['source'] == 'Facebook Marketplace':
        return f"""Hi! I'm interested in the {model_name}. A few questions:

1. Is it currently working? Have you tested all functions?
2. Are there any issues (crackling, hum, dead channels, etc.)?
3. Can you send more photos of the front panel, back panel, and inside if possible?
4. Is the price firm or is there any flexibility?
5. Would you be open to me testing it in person before purchasing?

Looking forward to hearing from you!"""
    else:  # Mercari
        return f"""Hi! Interested in the {model_name}. Can you confirm:

1. Does it power on and work properly?
2. Any cosmetic or functional issues?
3. Do you have more photos of all sides?
4. Would you accept [OFFER_PRICE]?

Thanks!"""


def main():
    print("="*80)
    print("DEAL DESK REVIEW - TOP ACTIONABLE LEADS")
    print("="*80)
    print()
    
    # Load leads
    print("Loading equipment leads...")
    all_leads = load_equipment_leads()
    print(f"✓ Loaded {len(all_leads)} leads")
    print()
    
    # Filter to equipment only
    print("Manual verification of top leads...")
    verified_leads = []
    
    for lead in all_leads:
        if is_full_equipment(lead['title']):
            model_name, search_term = classify_model(lead['title'])
            if model_name:
                lead['model_name'] = model_name
                lead['search_term'] = search_term
                verified_leads.append(lead)
    
    print(f"✓ {len(verified_leads)} verified equipment leads")
    print()
    
    # Sort by price (lowest first for opportunity)
    verified_leads.sort(key=lambda x: float(x['price']) if x['price'] else 9999)
    
    # Deep research on top 15 leads
    print("Researching top 15 leads...")
    print()
    
    researched = []
    for i, lead in enumerate(verified_leads[:15], 1):
        print(f"{i}. {lead['title'][:60]}")
        print(f"   ${lead['price']} | {lead['source']}")
        
        metrics = calculate_deal_metrics(lead, lead['model_name'], lead['search_term'])
        
        if metrics:
            lead['metrics'] = metrics
            researched.append(lead)
            print(f"   ✓ Est. profit: ${metrics['net_profit']:.0f}")
        else:
            print(f"   ✗ Could not calculate metrics")
        
        print()
    
    # Rank by actionability
    # Priority: High profit + local + known model + eBay data available
    def actionability_score(lead):
        m = lead.get('metrics', {})
        score = 0
        
        # Profit potential
        score += min(m.get('net_profit', 0), 500)  # Cap at 500
        
        # Local pickup bonus
        if lead['source'] == 'Facebook Marketplace':
            score += 100
        
        # eBay data available
        if m.get('ebay_count', 0) > 0:
            score += 50
        
        # Known target model
        if lead.get('model_name') in ['Pioneer SX-1050', 'Pioneer SX-1250', 'McIntosh MA 6100', 
                                       'Marantz 2270', 'Technics SL-1200']:
            score += 75
        
        return score
    
    researched.sort(key=actionability_score, reverse=True)
    
    # Generate report
    print("Generating deal desk report...")
    print()
    
    report = []
    report.append("# Deal Desk Review 001")
    report.append("")
    report.append("**Date:** 2026-05-04")
    report.append("**Purpose:** Top 5-10 actionable leads with full research")
    report.append("")
    report.append("---")
    report.append("")
    
    # Summary
    report.append("## 📊 EXECUTIVE SUMMARY")
    report.append("")
    report.append(f"**Leads Analyzed:** {len(researched)}")
    report.append(f"**Immediate Review:** {min(5, len([l for l in researched if l.get('metrics', {}).get('net_profit', 0) > 150]))}")
    report.append(f"**Watchlist:** {min(10, len([l for l in researched if 50 < l.get('metrics', {}).get('net_profit', 0) <= 150]))}")
    report.append("")
    
    # Top 5 immediate review
    report.append("## 🔥 TOP 5 IMMEDIATE REVIEW LEADS")
    report.append("")
    report.append("Leads worth contacting seller TODAY.")
    report.append("")
    
    immediate = [l for l in researched if l.get('metrics', {}).get('net_profit', 0) > 150][:5]
    
    for i, lead in enumerate(immediate, 1):
        m = lead['metrics']
        
        report.append(f"### {i}. {lead['model_name']} - ${lead['price']}")
        report.append("")
        report.append(f"**Full Title:** {lead['title']}")
        report.append(f"**Source:** {lead['source']}")
        report.append(f"**Location:** {lead['location']}")
        if lead.get('url'):
            report.append(f"**URL:** {lead['url'][:100]}")
        report.append("")
        
        # Market data
        report.append("**Market Research:**")
        if m['ebay_count'] > 0:
            report.append(f"- eBay Active Listings: {m['ebay_count']} found")
            report.append(f"- Price Range: ${m['ebay_min']:.0f} - ${m['ebay_max']:.0f}")
            report.append(f"- Median: ${m['ebay_median']:.0f}")
            report.append(f"- Comp Confidence: {'HIGH' if m['ebay_count'] >= 5 else 'MEDIUM'}")
        else:
            report.append("- ⚠️ **NEEDS_SOLD_COMPS** - No eBay active data found")
        report.append("")
        
        # Financial analysis
        report.append("**Financial Analysis:**")
        report.append(f"- Asking Price: ${m['asking_price']:.2f}")
        report.append(f"- Estimated Resale: ${m['estimated_sell']:.2f}")
        report.append(f"- eBay Fees (13%): ${m['fees']:.2f}")
        report.append(f"- Shipping/Pickup: ${m['shipping']:.2f}")
        report.append(f"- **Estimated Net Profit: ${m['net_profit']:.2f}**")
        report.append(f"- ROI: {m['roi_percent']:.0f}%")
        report.append(f"- **Max Buy Price: ${m['max_buy_price']:.2f}**")
        report.append("")
        
        # Risks
        report.append("**Risk Assessment:**")
        risks = []
        
        if 'working' not in lead['title'].lower() and 'tested' not in lead['title'].lower():
            risks.append("❌ **Condition Unknown** - Not confirmed working")
        
        if m['ebay_count'] == 0:
            risks.append("⚠️ **No Market Data** - Must get sold comps before action")
        
        if lead['source'] == 'Mercari':
            risks.append("⚠️ **Shipping Risk** - Cannot test before purchase")
        
        if m['net_profit'] < 200:
            risks.append("⚠️ **Thin Margins** - Little room for repair costs")
        
        if not risks:
            report.append("- ✓ Low risk (local, confirmed working, market data available)")
        else:
            for risk in risks:
                report.append(f"- {risk}")
        
        report.append("")
        
        # Verdict
        if m['net_profit'] > 300 and lead['source'] == 'Facebook Marketplace':
            verdict = "**INVESTIGATE** ⭐⭐⭐"
            action = "Contact seller immediately, schedule inspection"
        elif m['net_profit'] > 200:
            verdict = "**INVESTIGATE** ⭐⭐"
            action = "Contact seller, verify condition before committing"
        else:
            verdict = "**WATCH** ⭐"
            action = "Monitor for price drop or better photos"
        
        report.append(f"**Verdict:** {verdict}")
        report.append(f"**Next Action:** {action}")
        report.append("")
        
        # Exact message to send
        if verdict.startswith("**INVESTIGATE**"):
            report.append("**Exact Message to Send:**")
            report.append("```")
            message = generate_seller_message(lead, lead['model_name'])
            # Add offer price
            offer_price = min(m['max_buy_price'], m['asking_price'] * 0.85)
            message = message.replace('[OFFER_PRICE]', f"${offer_price:.0f}")
            report.append(message)
            report.append("```")
            report.append("")
        
        report.append("---")
        report.append("")
    
    if not immediate:
        report.append("*(No leads met immediate review criteria - see watchlist)*")
        report.append("")
    
    # Watchlist
    report.append("## 👀 WATCHLIST LEADS (Next 5)")
    report.append("")
    report.append("Monitor these for price drops or better information.")
    report.append("")
    
    watchlist = [l for l in researched if 50 < l.get('metrics', {}).get('net_profit', 0) <= 150][:5]
    
    for i, lead in enumerate(watchlist, 1):
        m = lead['metrics']
        report.append(f"### {i}. {lead['model_name']} - ${lead['price']}")
        report.append(f"- Location: {lead['location']}")
        report.append(f"- Est. Profit: ${m['net_profit']:.0f}")
        report.append(f"- Why Watch: {'Thin margins' if m['net_profit'] < 100 else 'Need sold comps' if m['ebay_count'] == 0 else 'Verify condition'}")
        if lead.get('url'):
            report.append(f"- URL: {lead['url'][:80]}")
        report.append("")
    
    # Skipped
    skipped = [l for l in researched if l.get('metrics', {}).get('net_profit', 0) <= 50]
    if skipped:
        report.append("## ⏭️ SKIPPED LEADS")
        report.append("")
        report.append(f"**Count:** {len(skipped)}")
        report.append("")
        report.append("**Common Reasons:**")
        report.append("- Net profit < $50")
        report.append("- Overpriced vs market")
        report.append("- Unknown condition + shipping risk")
        report.append("- No eBay comps available")
        report.append("")
    
    # Critical notes
    report.append("## ⚠️ CRITICAL NOTES")
    report.append("")
    report.append("**ALL profit estimates are PRELIMINARY**")
    report.append("")
    report.append("**Before ANY purchase:**")
    report.append("1. ✓ Run eBay sold comps (actual sold prices, not asking)")
    report.append("2. ✓ Verify condition with photos/inspection")
    report.append("3. ✓ Test functionality in person if possible")
    report.append("4. ✓ Negotiate based on condition issues found")
    report.append("5. ✓ Factor in repair costs for non-working items")
    report.append("")
    report.append("**DO NOT:**")
    report.append("- ❌ Call any of these \"BUY\" without sold comp verification")
    report.append("- ❌ Trust profit estimates without actual sold prices")
    report.append("- ❌ Purchase untested items without discount for risk")
    report.append("- ❌ Skip in-person testing for local items")
    report.append("")
    
    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ Report generated: {OUTPUT_REPORT}")
    print()
    print("Top Immediate Leads:")
    for i, lead in enumerate(immediate[:5], 1):
        m = lead.get('metrics', {})
        print(f"  {i}. {lead['model_name']} - ${lead['price']} (profit: ${m.get('net_profit', 0):.0f})")
    print()


if __name__ == "__main__":
    main()
