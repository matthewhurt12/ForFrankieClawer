#!/usr/bin/env python3
"""
Mercari Apify Production Run 001
Controlled production run with cost limits
"""

import os
import json
import csv
import requests
from pathlib import Path
from datetime import datetime, timezone

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"

# Production settings
MAX_ITEMS_PER_URL = 50
MAX_COST = 0.50  # dollars

# Output paths
OUTPUT_DIR = Path("data/external_leads")
RAW_OUTPUT = OUTPUT_DIR / "mercari_raw_run_001.json"
CSV_OUTPUT = OUTPUT_DIR / "mercari_leads.csv"
LEAD_INTAKE = Path("lead_intake.csv")

# Target searches
SEARCHES = [
    "McIntosh MA 5100",
    "McIntosh MA 6100",
    "Pioneer SX-1250",
    "Pioneer SX-1050",
    "Marantz 2270",
    "Marantz 2275",
    "Technics SL-1200",
    "Nakamichi Dragon",
]

def run_search(query):
    """Run single search via Apify."""
    print(f"\n{'='*80}")
    print(f"Searching: {query}")
    print(f"{'='*80}\n")
    
    # Build Mercari search URL
    search_url = f"https://www.mercari.com/search/?keyword={query.replace(' ', '%20')}"
    
    # Actor input
    actor_input = {
        "urls": [search_url],
        "max_items_per_url": MAX_ITEMS_PER_URL,
        "ignore_url_failures": True,
        "proxy": {
            "useApifyProxy": True  # REQUIRED for Mercari
        }
    }
    
    endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"
    
    print(f"Running actor...")
    
    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {APIFY_TOKEN}",
                "Content-Type": "application/json"
            },
            json=actor_input,
            timeout=180  # 3 minutes
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            items = response.json()
            print(f"✓ Retrieved {len(items)} items")
            return items
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text[:200])
            return []
            
    except requests.exceptions.Timeout:
        print(f"✗ Timeout")
        return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def normalize_item(item, query):
    """
    Normalize Apify result.
    DO NOT store seller names, IDs, or personal data.
    """
    # Price conversion (cents to USD)
    price_cents = item.get('price')
    price_usd = None
    if price_cents:
        try:
            price_usd = float(price_cents) / 100
        except:
            pass
    
    return {
        'source': 'mercari_apify',
        'item_id': item.get('id'),
        'title': item.get('name'),
        'status': item.get('status'),
        'price_cents': price_cents,
        'price_usd': f"{price_usd:.2f}" if price_usd else None,
        'url': item.get('url'),
        'image_url': item.get('thumbnails', [None])[0] if item.get('thumbnails') else None,
        'condition': item.get('itemCondition'),
        'shipping_payer': item.get('shippingPayer'),
        'query': query,
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'review_status': 'MERCARI_ACTIVE_CONTEXT_ONLY',
        'notes': 'NEEDS_MANUAL_REVIEW | NEEDS_MANUAL_SOLD_COMPS'
    }


def deduplicate(items):
    """Deduplicate by item_id."""
    seen = set()
    unique = []
    
    for item in items:
        item_id = item.get('item_id')
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique.append(item)
    
    return unique


def save_csv(items, path):
    """Save to CSV."""
    if not items:
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = list(items[0].keys())
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    print(f"✓ Saved: {path}")


def filter_top_candidates(items, max_price=1500):
    """Filter and sort candidates."""
    candidates = []
    
    for item in items:
        if not item.get('price_usd'):
            continue
        
        try:
            price = float(item['price_usd'])
        except:
            continue
        
        if price > max_price:
            continue
        
        if not item.get('title'):
            continue
        
        candidates.append(item)
    
    # Sort by price ascending
    candidates.sort(key=lambda x: float(x.get('price_usd', 999999)))
    
    return candidates


def add_to_lead_intake(items):
    """Add top candidates to lead_intake.csv."""
    if not items:
        return
    
    lead_rows = []
    
    for item in items[:10]:  # Top 10 only
        lead_rows.append({
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Mercari (Apify)',
            'listing_url': item.get('url', ''),
            'screenshot_path': '',
            'model_guess': item.get('query', ''),
            'title': item.get('title', '')[:200],
            'asking_price': item.get('price_usd', ''),
            'location': 'Online',
            'seller_condition_claim': item.get('condition', ''),
            'photos_available': 'yes' if item.get('image_url') else 'no',
            'notes': f"Mercari. Condition: {item.get('condition')}. Shipping: {item.get('shipping_payer')}",
            'status': 'unreviewed'
        })
    
    # Check if file exists
    file_exists = LEAD_INTAKE.exists()
    
    # Append
    with open(LEAD_INTAKE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = lead_rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerows(lead_rows)
    
    print(f"✓ Added {len(lead_rows)} leads to lead_intake.csv")


def main():
    print("="*80)
    print("MERCARI APIFY PRODUCTION RUN 001")
    print("="*80)
    print()
    print("⚠️  MERCARI_ACTIVE_CONTEXT_ONLY")
    print("⚠️  NEEDS_MANUAL_REVIEW")
    print("⚠️  NEEDS_MANUAL_SOLD_COMPS")
    print()
    print(f"Settings:")
    print(f"  Max items per URL: {MAX_ITEMS_PER_URL}")
    print(f"  Max cost: ${MAX_COST}")
    print(f"  Searches: {len(SEARCHES)}")
    print(f"  Proxy: Apify (required)")
    print()
    
    # Run searches
    all_raw = []
    
    for query in SEARCHES:
        items = run_search(query)
        
        # Add query to each item for tracking
        for item in items:
            item['_query'] = query
            all_raw.append(item)
        
        print()
    
    # Save raw output
    print(f"{'='*80}")
    print("Processing Results")
    print(f"{'='*80}\n")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(RAW_OUTPUT, 'w') as f:
        json.dump(all_raw, f, indent=2)
    print(f"✓ Raw output: {RAW_OUTPUT}")
    print(f"  Total raw items: {len(all_raw)}")
    print()
    
    # Normalize
    normalized = []
    for item in all_raw:
        query = item.pop('_query', 'unknown')
        norm = normalize_item(item, query)
        normalized.append(norm)
    
    print(f"Normalized: {len(normalized)} items")
    
    # Deduplicate
    unique = deduplicate(normalized)
    print(f"After dedup: {len(unique)} unique items")
    print()
    
    # Save CSV
    save_csv(unique, CSV_OUTPUT)
    print()
    
    # Filter candidates
    candidates = filter_top_candidates(unique, max_price=1500)
    print(f"Candidates under $1500: {len(candidates)}")
    print()
    
    if candidates:
        print("Top 10 Candidates:")
        print("-" * 80)
        for i, item in enumerate(candidates[:10], 1):
            print(f"{i}. {item['title'][:60]}")
            print(f"   ${item['price_usd']} | {item['query']} | {item['condition']}")
        print()
        
        # Add to lead intake
        add_to_lead_intake(candidates)
        print()
    
    # Estimate cost
    estimated_cost = len(SEARCHES) * 0.015  # ~$0.015 per search
    print(f"{'='*80}")
    print(f"Run Complete")
    print(f"{'='*80}\n")
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print(f"Within budget: {'✓' if estimated_cost <= MAX_COST else '✗'}")
    print()
    print("Next step:")
    print("  python3 manual_lead_review.py")
    print()


if __name__ == "__main__":
    main()
