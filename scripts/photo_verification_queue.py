#!/usr/bin/env python3
"""
Photo Verification Queue
Classify top leads by what information is missing
No profit estimates until model + sold comps confirmed
"""

import csv
from pathlib import Path
from collections import defaultdict

# Input files
MERCARI_CSV = Path("data/external_leads/mercari_leads.csv")
FACEBOOK_CSV = Path("data/external_leads/facebook_marketplace_leads.csv")

# Output
OUTPUT_REPORT = Path("reports/PHOTO_VERIFICATION_QUEUE_001.md")

# Known target models with clear identifiers
TARGET_MODELS = {
    'McIntosh MA 6100': ['ma 6100', 'ma6100', 'ma-6100'],
    'McIntosh MA 5100': ['ma 5100', 'ma5100', 'ma-5100'],
    'McIntosh MC 2300': ['mc 2300', 'mc2300', 'mc-2300'],
    'Pioneer SX-1250': ['sx-1250', 'sx 1250', 'sx1250'],
    'Pioneer SX-1050': ['sx-1050', 'sx 1050', 'sx1050'],
    'Pioneer SX-950': ['sx-950', 'sx 950', 'sx950'],
    'Pioneer SX-850': ['sx-850', 'sx 850', 'sx850'],
    'Pioneer SX-770': ['sx-770', 'sx 770', 'sx770'],
    'Pioneer SX-650': ['sx-650', 'sx 650', 'sx650'],
    'Marantz 2270': ['2270'],
    'Marantz 2275': ['2275'],
    'Marantz 2245': ['2245'],
    'Technics SL-1200': ['sl-1200', 'sl 1200', 'sl1200'],
    'Nakamichi Dragon': ['dragon'],
}

# Generic equipment indicators
EQUIPMENT_TYPES = {
    'receiver': ['receiver', 'stereo receiver', 'am/fm'],
    'amplifier': ['amplifier', 'amp', 'integrated'],
    'turntable': ['turntable', 'record player', 'direct drive'],
    'tape_deck': ['tape deck', 'cassette deck', 'dual cassette'],
    'tuner': ['tuner', 'am/fm tuner'],
}


def load_all_leads():
    """Load all leads from both sources."""
    leads = []
    
    if MERCARI_CSV.exists():
        with open(MERCARI_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append({
                    'source': 'Mercari',
                    'title': row.get('title', ''),
                    'price': row.get('price_usd', ''),
                    'url': row.get('listing_url', ''),
                    'location': 'Online',
                })
    
    if FACEBOOK_CSV.exists():
        with open(FACEBOOK_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append({
                    'source': 'Facebook Marketplace',
                    'title': row.get('title', ''),
                    'price': row.get('price', ''),
                    'url': row.get('listing_url', ''),
                    'location': row.get('location', ''),
                })
    
    return leads


def identify_model(title):
    """Try to identify exact model from title."""
    if not title:
        return None, None, None
    
    title_lower = title.lower()
    
    # Check target models
    for model, identifiers in TARGET_MODELS.items():
        if any(ident in title_lower for ident in identifiers):
            # Check it's likely equipment, not accessory
            if any(word in title_lower for word in ['working', 'tested', 'receiver', 'amplifier', 'turntable', 'deck']):
                return model, model.split()[0], 'TARGET'  # Model, Brand, Type
            else:
                return model, model.split()[0], 'UNCERTAIN'  # Could be part/accessory
    
    # Generic brand + equipment type
    brands = ['pioneer', 'marantz', 'mcintosh', 'technics', 'nakamichi', 'sansui', 'yamaha', 'sony']
    for brand in brands:
        if brand in title_lower:
            for eq_type, indicators in EQUIPMENT_TYPES.items():
                if any(ind in title_lower for ind in indicators):
                    return None, brand.capitalize(), eq_type  # No specific model, but know type
    
    return None, None, None


def classify_lead(lead):
    """
    Classify lead by what's missing.
    
    A. NEEDS_PHOTO_CHECK - has model, need to verify from photos
    B. NEEDS_EXACT_MODEL - know it's equipment but need specific model
    C. NEEDS_SOLD_COMPS - have model, ready for sold comp research
    D. SKIP - clearly not worth pursuing
    E. READY_FOR_SELLER_MESSAGE - all info available
    """
    title = lead['title']
    title_lower = title.lower()
    
    # Skip indicators
    skip_words = ['t-shirt', 'pin', 'sticker', 'manual', 'catalog', 'parts only', 
                  'for parts', 'broken', 'not working', 'as-is']
    if any(word in title_lower for word in skip_words):
        return 'SKIP', "Clearly not full equipment"
    
    # Too cheap to be equipment
    try:
        price = float(lead['price'])
        if price < 20:
            return 'SKIP', "Too cheap to be full equipment"
    except:
        pass
    
    # Identify what we know
    model, brand, eq_type = identify_model(title)
    
    # Has specific target model
    if model and eq_type == 'TARGET':
        # Need to verify it's actually equipment, not part
        if 'working' in title_lower or 'tested' in title_lower or 'serviced' in title_lower:
            return 'NEEDS_SOLD_COMPS', f"Have model ({model}), confirmed working, need sold comps"
        else:
            return 'NEEDS_PHOTO_CHECK', f"Have model ({model}), verify condition/completeness"
    
    # Has model but uncertain if full equipment
    elif model and eq_type == 'UNCERTAIN':
        return 'NEEDS_PHOTO_CHECK', f"Suspected {model} but title unclear, verify not part/accessory"
    
    # Has brand + equipment type, need exact model
    elif brand and eq_type:
        return 'NEEDS_EXACT_MODEL', f"{brand} {eq_type} but no model number in title"
    
    # Not enough info
    else:
        return 'SKIP', "Cannot identify brand or equipment type"


def generate_verification_notes(lead, classification, reason):
    """Generate what to verify and what to ask."""
    title_lower = lead['title'].lower()
    model, brand, eq_type = identify_model(lead['title'])
    
    notes = {
        'suspected_model': model or f"{brand} {eq_type}" if brand and eq_type else "Unknown",
        'why_matters': "",
        'junk_risk': "",
        'photo_check': "",
        'seller_question': ""
    }
    
    # Why it might matter
    if model:
        if 'sx-1250' in model.lower() or 'sx-1050' in model.lower():
            notes['why_matters'] = f"{model} is a high-value vintage receiver ($400-800 typical resale)"
        elif 'mcintosh' in model.lower():
            notes['why_matters'] = f"{model} is premium vintage audio ($500-2000+ typical resale)"
        elif 'marantz' in model.lower() and any(x in model for x in ['2270', '2275', '2245']):
            notes['why_matters'] = f"{model} is sought-after vintage receiver ($400-600 typical resale)"
        elif 'sl-1200' in model.lower():
            notes['why_matters'] = "Technics SL-1200 is iconic DJ turntable ($300-600 typical resale)"
        else:
            notes['why_matters'] = f"{model} is vintage audio equipment, potential resale value"
    elif brand:
        notes['why_matters'] = f"{brand} vintage audio, resale depends on specific model"
    else:
        notes['why_matters'] = "Cannot assess value without more information"
    
    # What could make it junk
    if 'working' not in title_lower and 'tested' not in title_lower:
        notes['junk_risk'] = "Condition unknown - could be broken/untested"
    
    if classification == 'NEEDS_EXACT_MODEL':
        notes['junk_risk'] += " | Generic title - could be low-value model"
    
    if 'as-is' in title_lower or 'repair' in title_lower:
        notes['junk_risk'] += " | Needs repair/restoration"
    
    # What to verify in photos
    if classification == 'NEEDS_PHOTO_CHECK':
        notes['photo_check'] = "Verify: Complete unit (not parts), front panel intact, all knobs/switches present, back panel connections visible"
    elif classification == 'NEEDS_EXACT_MODEL':
        notes['photo_check'] = "Look for: Model number on front panel or back, serial number plate, clear view of all labels"
    elif classification == 'NEEDS_SOLD_COMPS':
        notes['photo_check'] = "Verify: Overall condition, cosmetic damage, meter condition (if applicable), speaker terminals"
    
    # What to ask seller
    if classification == 'NEEDS_PHOTO_CHECK':
        notes['seller_question'] = "What's the exact model number? Is this the complete unit or just a component? Does it power on?"
    elif classification == 'NEEDS_EXACT_MODEL':
        notes['seller_question'] = "Can you send a photo of the model number plate? What's the exact model number on the front or back panel?"
    elif classification == 'NEEDS_SOLD_COMPS':
        notes['seller_question'] = "Is it currently working? When was it last tested? Any known issues? Can I test it in person?"
    
    return notes


def main():
    print("="*80)
    print("PHOTO VERIFICATION QUEUE")
    print("="*80)
    print()
    
    # Load all leads
    print("Loading leads...")
    all_leads = load_all_leads()
    print(f"✓ Total leads: {len(all_leads)}")
    print()
    
    # Filter to equipment only (basic filter)
    equipment_leads = []
    for lead in all_leads:
        title_lower = lead['title'].lower() if lead['title'] else ''
        
        # Has equipment indicator
        has_equipment = any(word in title_lower for word in 
                           ['receiver', 'amplifier', 'amp', 'turntable', 'deck', 'tuner', 'stereo'])
        
        # Not obviously junk
        not_junk = not any(word in title_lower for word in 
                          ['t-shirt', 'pin', 'sticker', 'manual', 'catalog', 'parts only', 'shirt'])
        
        if has_equipment and not_junk:
            equipment_leads.append(lead)
    
    print(f"✓ Equipment leads: {len(equipment_leads)}")
    print()
    
    # Classify top 25
    print("Classifying top 25 leads...")
    
    # Sort by price (low to high)
    equipment_leads.sort(key=lambda x: float(x['price']) if x['price'] else 9999)
    
    classified = {
        'NEEDS_PHOTO_CHECK': [],
        'NEEDS_EXACT_MODEL': [],
        'NEEDS_SOLD_COMPS': [],
        'SKIP': [],
        'READY_FOR_SELLER_MESSAGE': []
    }
    
    for lead in equipment_leads[:50]:  # Check more to get 25 good ones
        classification, reason = classify_lead(lead)
        
        if classification != 'SKIP':
            notes = generate_verification_notes(lead, classification, reason)
            lead['classification'] = classification
            lead['reason'] = reason
            lead['notes'] = notes
            classified[classification].append(lead)
    
    # Take top 25 non-skip
    non_skip = []
    for cat in ['NEEDS_SOLD_COMPS', 'NEEDS_PHOTO_CHECK', 'NEEDS_EXACT_MODEL', 'READY_FOR_SELLER_MESSAGE']:
        non_skip.extend(classified[cat])
    
    top_25 = non_skip[:25]
    
    print(f"  NEEDS_PHOTO_CHECK: {len(classified['NEEDS_PHOTO_CHECK'])}")
    print(f"  NEEDS_EXACT_MODEL: {len(classified['NEEDS_EXACT_MODEL'])}")
    print(f"  NEEDS_SOLD_COMPS: {len(classified['NEEDS_SOLD_COMPS'])}")
    print(f"  SKIP: {len(classified['SKIP'])}")
    print()
    
    # Generate report
    print("Generating report...")
    
    report = []
    report.append("# Photo Verification Queue 001")
    report.append("")
    report.append("**Date:** 2026-05-04")
    report.append("**Purpose:** Classify top leads by missing information")
    report.append("")
    report.append("---")
    report.append("")
    
    # Summary
    report.append("## 📊 SUMMARY")
    report.append("")
    report.append("**Top 25 Leads Classified:**")
    report.append(f"- **NEEDS_PHOTO_CHECK:** {len([l for l in top_25 if l['classification'] == 'NEEDS_PHOTO_CHECK'])}")
    report.append(f"- **NEEDS_EXACT_MODEL:** {len([l for l in top_25 if l['classification'] == 'NEEDS_EXACT_MODEL'])}")
    report.append(f"- **NEEDS_SOLD_COMPS:** {len([l for l in top_25 if l['classification'] == 'NEEDS_SOLD_COMPS'])}")
    report.append(f"- **READY_FOR_SELLER_MESSAGE:** {len([l for l in top_25 if l['classification'] == 'READY_FOR_SELLER_MESSAGE'])}")
    report.append("")
    report.append("⚠️ **NO profit estimates until model + sold comps confirmed**")
    report.append("")
    
    # Group by classification
    for classification in ['NEEDS_SOLD_COMPS', 'NEEDS_PHOTO_CHECK', 'NEEDS_EXACT_MODEL', 'READY_FOR_SELLER_MESSAGE']:
        category_leads = [l for l in top_25 if l['classification'] == classification]
        
        if not category_leads:
            continue
        
        report.append(f"## {classification.replace('_', ' ')}")
        report.append("")
        
        if classification == 'NEEDS_SOLD_COMPS':
            report.append("*Have exact model, ready for eBay sold comp research*")
        elif classification == 'NEEDS_PHOTO_CHECK':
            report.append("*Need to verify from photos if this is complete equipment*")
        elif classification == 'NEEDS_EXACT_MODEL':
            report.append("*Know it's equipment, need specific model number*")
        elif classification == 'READY_FOR_SELLER_MESSAGE':
            report.append("*All info confirmed, ready to contact seller*")
        
        report.append("")
        
        for i, lead in enumerate(category_leads, 1):
            notes = lead['notes']
            
            report.append(f"### {i}. {lead['title'][:80]}")
            report.append("")
            report.append(f"**Source:** {lead['source']}")
            report.append(f"**Price:** ${lead['price']}")
            report.append(f"**Location:** {lead['location']}")
            if lead.get('url'):
                report.append(f"**URL:** {lead['url'][:100]}")
            report.append("")
            
            report.append(f"**Suspected Model:** {notes['suspected_model']}")
            report.append("")
            
            report.append(f"**Why It Might Matter:**")
            report.append(f"{notes['why_matters']}")
            report.append("")
            
            if notes['junk_risk']:
                report.append(f"**What Could Make It Junk:**")
                report.append(f"{notes['junk_risk']}")
                report.append("")
            
            if notes['photo_check']:
                report.append(f"**Verify In Photos:**")
                report.append(f"{notes['photo_check']}")
                report.append("")
            
            if notes['seller_question']:
                report.append(f"**Question For Seller:**")
                report.append(f"```")
                report.append(f"{notes['seller_question']}")
                report.append(f"```")
                report.append("")
            
            report.append("---")
            report.append("")
    
    # Next actions
    report.append("## 🎯 NEXT ACTIONS")
    report.append("")
    report.append("### Step 1: NEEDS_SOLD_COMPS Leads")
    sold_comp_leads = [l for l in top_25 if l['classification'] == 'NEEDS_SOLD_COMPS']
    if sold_comp_leads:
        report.append(f"**Count:** {len(sold_comp_leads)}")
        report.append("")
        report.append("**Action:** Run eBay sold comps for these specific models:")
        for lead in sold_comp_leads[:5]:
            report.append(f"- {lead['notes']['suspected_model']} (${lead['price']})")
        report.append("")
    else:
        report.append("*(None ready for sold comp research yet)*")
        report.append("")
    
    report.append("### Step 2: NEEDS_PHOTO_CHECK Leads")
    photo_leads = [l for l in top_25 if l['classification'] == 'NEEDS_PHOTO_CHECK']
    if photo_leads:
        report.append(f"**Count:** {len(photo_leads)}")
        report.append("**Action:** Review listing photos, verify complete equipment, not parts")
        report.append("")
    
    report.append("### Step 3: NEEDS_EXACT_MODEL Leads")
    model_leads = [l for l in top_25 if l['classification'] == 'NEEDS_EXACT_MODEL']
    if model_leads:
        report.append(f"**Count:** {len(model_leads)}")
        report.append("**Action:** Message seller asking for exact model number")
        report.append("")
    
    # Critical warnings
    report.append("## ⚠️ CRITICAL RULES")
    report.append("")
    report.append("**DO NOT estimate profit until:**")
    report.append("1. ✓ Exact model confirmed")
    report.append("2. ✓ Photos verify complete equipment (not parts)")
    report.append("3. ✓ At least 3 clean eBay sold comps available")
    report.append("4. ✓ Fees + shipping + risk factored in")
    report.append("")
    report.append("**DO NOT:**")
    report.append("- ❌ Use broad eBay searches like \"Pioneer receiver\" for resale estimates")
    report.append("- ❌ Call anything BUY without sold comps")
    report.append("- ❌ Call anything PROFIT without sold comps")
    report.append("- ❌ Trust generic receiver to sell for target model prices")
    report.append("")
    report.append("**REMEMBER:**")
    report.append("- A $25 Pioneer SX-312 ≠ $549 (that's the median of ALL Pioneer receivers)")
    report.append("- A $30 Pioneer tuner ≠ full receiver resale value")
    report.append("- A $40 tape deck ≠ receiver resale value")
    report.append("- Verify EXACT MODEL before any profit estimate")
    report.append("")
    
    # Write report
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ Report generated: {OUTPUT_REPORT}")
    print()
    print("Summary:")
    print(f"  Needs sold comps: {len(sold_comp_leads)}")
    print(f"  Needs photo check: {len(photo_leads)}")
    print(f"  Needs exact model: {len(model_leads)}")
    print()
    print("Next: Review photos, confirm models, then run sold comps")
    print()


if __name__ == "__main__":
    main()
