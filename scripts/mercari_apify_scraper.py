#!/usr/bin/env python3
"""
Mercari Apify Scraper - Uses Apify Actor to scrape Mercari product search
Actor: stealth_mode/mercari-product-search-scraper
"""

import os
import json
import csv
import requests
from pathlib import Path
from datetime import datetime, timezone

# Apify configuration
APIFY_API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"

# Output
OUTPUT_DIR = Path("data/external_leads")
OUTPUT_CSV = OUTPUT_DIR / "mercari_leads.csv"

# Search queries
DEFAULT_SEARCHES = [
    "McIntosh MA 5100",
    "McIntosh MA 6100", 
    "Pioneer SX-1250",
    "Pioneer SX-1050",
    "Marantz 2270",
    "Marantz 2275",
    "Technics SL-1200",
    "Nakamichi Dragon",
]


def get_apify_token():
    """Get Apify token from environment."""
    token = os.environ.get('APIFY_TOKEN')
    if not token:
        raise ValueError("APIFY_TOKEN not set in environment")
    return token


def run_mercari_search(query, max_items=50):
    """
    Run Mercari product search via Apify Actor.
    Returns list of items.
    """
    print(f"\n{'='*80}")
    print(f"Searching Mercari: {query}")
    print(f"{'='*80}\n")
    
    token = get_apify_token()
    
    # Build Mercari search URL
    search_url = f"https://www.mercari.com/search/?keyword={query.replace(' ', '+')}"
    
    # Actor input (use correct field names from working test)
    actor_input = {
        "urls": [search_url],
        "max_items_per_url": max_items,
        "ignore_url_failures": True,
        "proxy": {
            "useApifyProxy": True  # REQUIRED - prevents bot detection
        }
    }
    
    # API endpoint
    url = f"{APIFY_API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"
    
    print(f"Starting Apify Actor...")
    print(f"Max items: {max_items}")
    print()
    
    try:
        # Run actor synchronously
        response = requests.post(
            url,
            params={"token": token},
            json=actor_input,
            timeout=300  # 5 minutes max
        )
        
        response.raise_for_status()
        
        items = response.json()
        
        print(f"✓ Actor completed")
        print(f"✓ Items returned: {len(items)}")
        print()
        
        return items
        
    except requests.exceptions.Timeout:
        print(f"✗ Actor timeout (>5 minutes)")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"✗ API Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text[:500]}")
        return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def normalize_item(item, query):
    """
    Normalize Apify result to our schema.
    Do NOT store seller names, IDs, or personal data.
    """
    # Price conversion (cents to USD)
    price_cents = item.get('price')
    price_usd = None
    if price_cents:
        try:
            price_usd = float(price_cents) / 100
        except:
            pass
    
    # Normalize fields
    normalized = {
        'source': 'apify',
        'site': 'mercari',
        'item_id': item.get('id') or item.get('itemId') or item.get('productId'),
        'title': item.get('name') or item.get('title'),
        'status': item.get('status'),
        'price_cents': price_cents,
        'price_usd': f"{price_usd:.2f}" if price_usd else None,
        'url': item.get('url') or item.get('itemUrl'),
        'image_url': item.get('thumbnails', [None])[0] if item.get('thumbnails') else None,
        'condition': item.get('itemCondition') or item.get('condition'),
        'shipping_payer': item.get('shippingPayer'),
        'category_title': item.get('categoryTitle'),
        'query': query,
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'review_status': 'MERCARI_ACTIVE_CONTEXT_ONLY',
        'notes': 'NEEDS_MANUAL_REVIEW'
    }
    
    return normalized


def deduplicate_items(items):
    """Deduplicate items by item_id."""
    seen = set()
    unique = []
    
    for item in items:
        item_id = item.get('item_id')
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique.append(item)
    
    return unique


def save_to_csv(items, output_path):
    """Save normalized items to CSV."""
    if not items:
        print("No items to save")
        return
    
    # Ensure output dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define field order
    fieldnames = [
        'source', 'site', 'item_id', 'title', 'status', 
        'price_cents', 'price_usd', 'url', 'image_url',
        'condition', 'shipping_payer', 'category_title',
        'query', 'scraped_at', 'review_status', 'notes'
    ]
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    print(f"✓ Saved: {output_path}")
    print(f"  Total items: {len(items)}")


def filter_candidates(items, price_max=None):
    """Filter items that might be good candidates."""
    candidates = []
    
    for item in items:
        # Skip if no price
        if not item.get('price_usd'):
            continue
        
        try:
            price = float(item['price_usd'])
        except:
            continue
        
        # Apply price filter if specified
        if price_max and price > price_max:
            continue
        
        # Must have title
        if not item.get('title'):
            continue
        
        # Add to candidates
        candidates.append(item)
    
    # Sort by price (ascending)
    candidates.sort(key=lambda x: float(x.get('price_usd', 999999)))
    
    return candidates


def convert_to_lead_intake_format(item):
    """Convert normalized item to lead_intake.csv format."""
    return {
        'date_found': datetime.now().strftime('%Y-%m-%d'),
        'source': 'Mercari (Apify)',
        'listing_url': item.get('url', ''),
        'screenshot_path': '',
        'model_guess': item.get('query', ''),
        'title': item.get('title', '')[:200],  # Truncate if too long
        'asking_price': item.get('price_usd', ''),
        'location': 'Online',
        'seller_condition_claim': item.get('condition', ''),
        'photos_available': 'yes' if item.get('image_url') else 'no',
        'notes': f"Mercari listing. Condition: {item.get('condition')}. Shipping: {item.get('shipping_payer')}",
        'status': 'unreviewed'
    }


def main():
    print("="*80)
    print("Mercari Apify Scraper")
    print("="*80)
    print()
    print("⚠️  MERCARI_ACTIVE_CONTEXT_ONLY")
    print("⚠️  NEEDS_MANUAL_REVIEW")
    print("⚠️  NOT_SOLD_COMPS")
    print()
    
    # Check for token
    try:
        token = get_apify_token()
        print(f"✓ Apify token found (length: {len(token)})")
        print()
    except ValueError as e:
        print(f"✗ {e}")
        print()
        print("Set APIFY_TOKEN environment variable:")
        print("  export APIFY_TOKEN='your-token-here'")
        return
    
    # Run searches
    all_items = []
    
    for query in DEFAULT_SEARCHES:
        items = run_mercari_search(query, max_items=50)
        
        # Normalize items
        for item in items:
            normalized = normalize_item(item, query)
            all_items.append(normalized)
        
        print(f"✓ {query}: {len(items)} items\n")
    
    if not all_items:
        print("✗ No items found")
        return
    
    print(f"\n{'='*80}")
    print("Processing Results")
    print(f"{'='*80}\n")
    
    # Deduplicate
    print(f"Total items before dedup: {len(all_items)}")
    unique_items = deduplicate_items(all_items)
    print(f"Unique items after dedup: {len(unique_items)}")
    print()
    
    # Save all items
    save_to_csv(unique_items, OUTPUT_CSV)
    
    # Also save as JSON for reference
    json_path = OUTPUT_DIR / "mercari_leads.json"
    with open(json_path, 'w') as f:
        json.dump(unique_items, f, indent=2)
    print(f"✓ Saved: {json_path}")
    print()
    
    # Filter top candidates (under $1500 for McIntosh, etc.)
    print(f"{'='*80}")
    print("Top Candidates (Price < $1500)")
    print(f"{'='*80}\n")
    
    candidates = filter_candidates(unique_items, price_max=1500)
    
    if candidates:
        print(f"Found {len(candidates)} candidates under $1500:\n")
        
        for i, item in enumerate(candidates[:10], 1):
            print(f"{i}. {item['title'][:60]}")
            print(f"   Price: ${item['price_usd']}")
            print(f"   Query: {item['query']}")
            print(f"   Condition: {item['condition']}")
            print(f"   URL: {item['url'][:80]}...")
            print()
        
        # Save top candidates to lead_intake.csv
        lead_intake_path = Path("lead_intake.csv")
        
        # Check if file exists
        file_exists = lead_intake_path.exists()
        
        # Convert to lead intake format
        lead_rows = [convert_to_lead_intake_format(item) for item in candidates[:10]]
        
        # Append to lead_intake.csv
        with open(lead_intake_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = lead_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(lead_rows)
        
        print(f"✓ Added top {len(lead_rows)} candidates to lead_intake.csv")
        print()
        print("Run manual_lead_review.py to underwrite these leads:")
        print("  python manual_lead_review.py")
        
    else:
        print("No candidates found under $1500")
    
    print(f"\n{'='*80}")
    print("Complete")
    print(f"{'='*80}")
    print()
    print("⚠️  All items marked MERCARI_ACTIVE_CONTEXT_ONLY")
    print("⚠️  All items marked NEEDS_MANUAL_REVIEW")
    print("⚠️  Do not call anything a deal until sold comps verified")


if __name__ == "__main__":
    main()
