#!/usr/bin/env python3
"""
Manual Lead Review - Underwrite manually-entered leads from lead_intake.csv

Usage:
  python manual_lead_review.py               # Process all unreviewed leads
  python manual_lead_review.py --lead-id 5   # Process specific lead by row number
  python manual_lead_review.py --all         # Re-process all leads
"""

import csv
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timezone


# Category price floors (copied from ebay_active_context.py)
CATEGORY_PRICE_FLOORS = {
    "mcintosh": 500,
    "pioneer": 400,
    "marantz": 400,
    "sansui": 400,
    "technics sl-1200": 300,
    "nakamichi": 75,
}


def detect_model(model_guess, title):
    """Try to identify specific model from title or model_guess."""
    text = f"{model_guess} {title}".lower()
    
    # McIntosh models
    if "ma 5100" in text or "ma5100" in text:
        return "McIntosh MA 5100", "mcintosh", 500
    if "ma 6100" in text or "ma6100" in text:
        return "McIntosh MA 6100", "mcintosh", 500
    if "c22" in text or "c 22" in text:
        return "McIntosh C22", "mcintosh", 500
    
    # Pioneer models
    if "sx-1250" in text or "sx 1250" in text:
        return "Pioneer SX-1250", "pioneer", 400
    if "sx-1050" in text or "sx 1050" in text:
        return "Pioneer SX-1050", "pioneer", 400
    
    # Marantz models
    if "2270" in text:
        return "Marantz 2270", "marantz", 400
    if "2275" in text:
        return "Marantz 2275", "marantz", 400
    
    # Sansui models
    if "g-9000" in text or "g9000" in text:
        return "Sansui G-9000", "sansui", 400
    if "9090" in text:
        return "Sansui 9090", "sansui", 400
    
    # Technics
    if "sl-1200" in text or "sl 1200" in text:
        return "Technics SL-1200", "technics sl-1200", 300
    
    # Nakamichi
    if "dragon" in text:
        return "Nakamichi Dragon", "nakamichi", 75
    if "1000zxl" in text or "1000 zxl" in text:
        return "Nakamichi 1000ZXL", "nakamichi", 75
    
    # Generic fallbacks
    if "mcintosh" in text:
        return "McIntosh (model unknown)", "mcintosh", 500
    if "pioneer" in text:
        return "Pioneer (model unknown)", "pioneer", 400
    if "marantz" in text:
        return "Marantz (model unknown)", "marantz", 400
    
    return "Unknown model", "unknown", 0


def is_exact_model(model):
    """Return True only when the detected model is specific enough for research."""
    if not model:
        return False
    lowered = model.lower()
    return "unknown" not in lowered and "(model unknown)" not in lowered


def run_ebay_search(model):
    """Run eBay active context search for the model."""
    print(f"  Running eBay active context search for: {model}")
    
    try:
        result = subprocess.run(
            ["python3", "ebay_active_context.py", model, "--max-results", "50", "--env", "production"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse output for key metrics
        output = result.stdout
        
        metrics = {
            "full_unit_count": None,
            "median_price": None,
            "price_range": None,
            "filter_status": None
        }
        
        for line in output.split('\n'):
            if "Full Unit Count:" in line:
                metrics["full_unit_count"] = line.split(":")[-1].strip()
            elif "Median Price:" in line:
                metrics["median_price"] = line.split(":")[-1].strip()
            elif "Price Range:" in line:
                metrics["price_range"] = line.split(":")[-1].strip()
            elif "Filter Status:" in line:
                metrics["filter_status"] = line.split(":")[-1].strip()
        
        # Find the most recent JSON output file for this model
        safe_model = model.lower().replace(" ", "_").replace('"', '')
        json_files = sorted(Path("data/ebay_active_search").glob(f"{safe_model}_production_*.json"), reverse=True)
        
        if json_files:
            with open(json_files[0]) as f:
                full_data = json.load(f)
                metrics["json_path"] = str(json_files[0])
                metrics["full_data"] = full_data
        
        return metrics
    except subprocess.TimeoutExpired:
        print("  ⚠️  Search timed out")
        return None
    except Exception as e:
        print(f"  ⚠️  Search failed: {e}")
        return None


def generate_seller_questions(model, asking_price, condition_claim):
    """Generate relevant questions to ask the seller."""
    questions = []
    
    # Universal questions
    questions.append("Does it power on and produce sound on both channels?")
    questions.append("Are all inputs/outputs working?")
    questions.append("Any scratchy pots, switches, or controls?")
    questions.append("Original owner? Service history?")
    questions.append("Why are you selling it?")
    
    # Model-specific questions
    if "mcintosh" in model.lower():
        questions.append("Are the blue meters working and lighting up?")
        questions.append("Any cabinet damage or veneer issues?")
    
    if "receiver" in model.lower() or "sx" in model.lower() or "marantz" in model.lower():
        questions.append("Does the tuner work and pull in stations?")
        questions.append("Are all speaker outputs working?")
    
    if "turntable" in model.lower() or "sl-1200" in model.lower():
        questions.append("Does the motor spin consistently?")
        questions.append("Is the tone arm and headshell included?")
        questions.append("Any wobble or speed issues?")
    
    if "nakamichi" in model.lower() or "cassette" in model.lower():
        questions.append("Does it play and record on both decks (if dual)?")
        questions.append("Have the belts been replaced recently?")
        questions.append("Is auto-azimuth working (if Dragon)?")
        questions.append("Any transport issues (eating tapes, speed problems)?")
    
    # Condition-based questions
    if condition_claim and "as-is" in condition_claim.lower():
        questions.append("What specifically is not working or needs repair?")
    
    if condition_claim and "recap" in condition_claim.lower():
        questions.append("Who did the recap work? Do you have documentation?")
    
    return questions


def calculate_margin_potential(asking_price, median_active, category_floor):
    """Calculate margin potential and risk flags."""
    try:
        asking = float(str(asking_price).replace('$', '').replace(',', ''))
    except:
        return None, []
    
    if not median_active:
        return None, ["No active market data available"]
    
    try:
        median = float(str(median_active).replace('$', '').replace(',', ''))
    except:
        return None, ["Could not parse median price"]
    
    discount_pct = ((median - asking) / median) * 100
    
    risk_flags = []
    
    if asking > median:
        risk_flags.append(f"ABOVE MARKET: Asking ${asking:.0f} vs median ${median:.0f}")
    elif discount_pct < 20:
        risk_flags.append(f"THIN MARGIN: Only {discount_pct:.0f}% below market")
    
    if category_floor > 0 and asking < category_floor:
        risk_flags.append(f"SUSPICIOUSLY LOW: Below ${category_floor} floor (likely parts/broken)")
    
    return discount_pct, risk_flags


def generate_report(lead, lead_id):
    """Generate underwriting report for a lead."""
    print(f"\n{'='*80}")
    print(f"LEAD #{lead_id} - MANUAL UNDERWRITING")
    print(f"{'='*80}")
    print()
    
    # Identify model
    model, category, category_floor = detect_model(lead.get("model_guess", ""), lead.get("title", ""))
    print(f"Identified Model: {model}")
    print(f"Category: {category}")
    print(f"Price Floor: ${category_floor}")
    print()
    
    exact_model = is_exact_model(model)

    # Run eBay active context only for exact models. Active listings are never
    # used as proof of resale value.
    print("Step 1: Active market context gate...")
    if exact_model:
        ebay_metrics = run_ebay_search(model)
        if not ebay_metrics:
            print("  Could not fetch eBay active context. Manual research optional.")
            ebay_metrics = {}
    else:
        print("  Skipped active context: exact model is not identified.")
        ebay_metrics = {}
    
    print()
    print("Step 2: Analyzing lead...")
    print(f"  Source: {lead.get('source', 'N/A')}")
    print(f"  Title: {lead.get('title', 'N/A')}")
    print(f"  Asking Price: ${lead.get('asking_price', 'N/A')}")
    print(f"  Location: {lead.get('location', 'N/A')}")
    print(f"  Condition Claim: {lead.get('seller_condition_claim', 'N/A')}")
    print(f"  Photos: {lead.get('photos_available', 'N/A')}")
    print()
    
    # Active market context
    print("Step 3: Active Market Context (eBay)")
    print("-" * 80)
    if ebay_metrics.get("full_unit_count"):
        print(f"  Active Listings: {ebay_metrics['full_unit_count']}")
        print(f"  Median Active Price: {ebay_metrics['median_price']}")
        print(f"  Price Range: {ebay_metrics['price_range']}")
        print(f"  Filter Status: {ebay_metrics['filter_status']}")
    else:
        print("  No data available")
    print()
    
    # Sold comp gate
    print("Step 4: Sold Comp Gate")
    print("-" * 80)
    discount_pct = None
    risk_flags = []
    print("  No profit or max-buy estimate generated from active listings.")
    print("  Required before pricing: exact model, full-unit photo verification, and at least 3 clean sold comps.")
    if not exact_model:
        risk_flags.append("Exact model is missing; do not run broad sold comps or active median math.")
    print()
    
    # Seller questions
    print("Step 5: Seller Questions")
    print("-" * 80)
    questions = generate_seller_questions(model, lead.get("asking_price"), lead.get("seller_condition_claim"))
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print()
    
    # Final verdict
    print("=" * 80)
    print("UNDERWRITING VERDICT")
    print("=" * 80)
    print()
    print("⚠️  NEEDS_MANUAL_SOLD_COMPS")
    print("⚠️  ACTIVE_LISTING_CONTEXT_ONLY")
    print()
    print("DO NOT BUY until:")
    print("  1. Manual eBay sold comps verified (Product Research / Terapeak)")
    print("  2. Seller questions answered satisfactorily")
    print("  3. Photos reviewed (especially back panel, condition)")
    print("  4. In-person inspection or video call demo if high value")
    print()
    
    if exact_model and not risk_flags:
        print("INVESTIGATE - Exact model found; verify full-unit photos and run sold comps")
    elif exact_model:
        print("WATCH - Exact model found, but risk flags must be resolved first")
    else:
        print("SKIP/WATCH - Exact model required before underwriting")
    
    print()
    print("=" * 80)
    print()
    
    # Save detailed report
    report_path = Path(f"reports/lead_{lead_id:04d}_review.md")
    save_detailed_report(lead, lead_id, model, category, category_floor, ebay_metrics, discount_pct, risk_flags, questions, report_path)
    print(f"Detailed report saved: {report_path}")
    print()


def save_detailed_report(lead, lead_id, model, category, category_floor, ebay_metrics, discount_pct, risk_flags, questions, report_path):
    """Save detailed markdown report."""
    
    with open(report_path, "w") as f:
        f.write(f"# Lead #{lead_id:04d} - Manual Underwriting\n")
        f.write(f"**Date Found:** {lead.get('date_found', 'N/A')}\n")
        f.write(f"**Status:** {lead.get('status', 'unreviewed')}\n\n")
        f.write("---\n\n")
        
        f.write("## Lead Details\n\n")
        f.write(f"- **Source:** {lead.get('source', 'N/A')}\n")
        f.write(f"- **Listing URL:** {lead.get('listing_url', 'N/A')}\n")
        f.write(f"- **Screenshot:** {lead.get('screenshot_path', 'N/A')}\n")
        f.write(f"- **Title:** {lead.get('title', 'N/A')}\n")
        f.write(f"- **Model Guess:** {lead.get('model_guess', 'N/A')}\n")
        f.write(f"- **Asking Price:** ${lead.get('asking_price', 'N/A')}\n")
        f.write(f"- **Location:** {lead.get('location', 'N/A')}\n")
        f.write(f"- **Condition Claim:** {lead.get('seller_condition_claim', 'N/A')}\n")
        f.write(f"- **Photos Available:** {lead.get('photos_available', 'N/A')}\n")
        f.write(f"- **Notes:** {lead.get('notes', 'N/A')}\n\n")
        
        f.write("---\n\n")
        f.write("## Model Identification\n\n")
        f.write(f"- **Identified Model:** {model}\n")
        f.write(f"- **Category:** {category}\n")
        f.write(f"- **Category Price Floor:** ${category_floor}\n\n")
        
        f.write("---\n\n")
        f.write("## Active Market Context (eBay)\n\n")
        f.write("⚠️ **ACTIVE_LISTING_CONTEXT_ONLY** - Not sold comps\n\n")
        
        if ebay_metrics.get("full_unit_count"):
            f.write(f"- **Active Listings:** {ebay_metrics['full_unit_count']}\n")
            f.write(f"- **Median Active Price:** {ebay_metrics['median_price']}\n")
            f.write(f"- **Price Range:** {ebay_metrics['price_range']}\n")
            f.write(f"- **Filter Status:** {ebay_metrics['filter_status']}\n\n")
            
            if ebay_metrics.get("json_path"):
                f.write(f"**Data Source:** `{ebay_metrics['json_path']}`\n\n")
        else:
            f.write("No active market data available.\n\n")
        
        f.write("---\n\n")
        f.write("## Sold Comp Gate\n\n")
        f.write("No profit or max-buy estimate generated from active listings.\n\n")
        f.write("Required before pricing:\n\n")
        f.write("1. Exact model confirmed\n")
        f.write("2. Photos verify complete equipment, not parts/accessories\n")
        f.write("3. At least 3 clean eBay sold comps available\n")
        f.write("4. Fees, shipping, repair reserve, return reserve, and required profit included\n\n")
        
        if risk_flags:
            f.write("### Risk Flags\n\n")
            for flag in risk_flags:
                f.write(f"- {flag}\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## Seller Questions\n\n")
        for i, q in enumerate(questions, 1):
            f.write(f"{i}. {q}\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write("## Underwriting Verdict\n\n")
        f.write("⚠️ **NEEDS_MANUAL_SOLD_COMPS**\n\n")
        f.write("**DO NOT BUY until:**\n\n")
        f.write("1. Manual eBay sold comps verified (Product Research / Terapeak)\n")
        f.write("2. Seller questions answered satisfactorily\n")
        f.write("3. Photos reviewed (especially back panel, condition)\n")
        f.write("4. In-person inspection or video call demo if high value\n\n")
        
        exact_model = is_exact_model(model)
        if exact_model and not risk_flags:
            f.write("### Recommendation: INVESTIGATE\n\n")
            f.write("Exact model found. Verify full-unit photos and run clean sold comps before any price estimate.\n\n")
        elif exact_model:
            f.write("### Recommendation: WATCH\n\n")
            f.write("Exact model found, but risk flags must be resolved before seller action.\n\n")
        else:
            f.write("### Recommendation: SKIP/WATCH\n\n")
            f.write("Exact model required before underwriting. Do not use broad active listings.\n\n")


def main():
    parser = argparse.ArgumentParser(description="Manual Lead Review - Underwrite leads from lead_intake.csv")
    parser.add_argument("--lead-id", type=int, help="Review specific lead by row number")
    parser.add_argument("--all", action="store_true", help="Re-process all leads")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("MANUAL LEAD REVIEW - Lead Underwriting System")
    print("=" * 80)
    print()
    
    # Read CSV
    csv_path = Path("lead_intake.csv")
    if not csv_path.exists():
        print("✗ lead_intake.csv not found")
        return
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    if not leads:
        print("No leads in lead_intake.csv")
        return
    
    print(f"Loaded {len(leads)} lead(s) from lead_intake.csv")
    print()
    
    # Filter leads to process
    if args.lead_id:
        if args.lead_id < 1 or args.lead_id > len(leads):
            print(f"✗ Invalid lead ID. Must be 1-{len(leads)}")
            return
        leads_to_process = [(args.lead_id - 1, leads[args.lead_id - 1])]
    elif args.all:
        leads_to_process = list(enumerate(leads))
    else:
        # Process only unreviewed
        leads_to_process = [(i, lead) for i, lead in enumerate(leads) if lead.get("status") != "reviewed"]
    
    if not leads_to_process:
        print("No unreviewed leads. Use --all to re-process.")
        return
    
    print(f"Processing {len(leads_to_process)} lead(s)...")
    print()
    
    for i, lead in leads_to_process:
        generate_report(lead, i + 1)
        
        # Update status in CSV
        leads[i]["status"] = "reviewed"
    
    # Save updated CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)
    
    print("✓ All leads processed")
    print("✓ lead_intake.csv updated")


if __name__ == "__main__":
    main()
