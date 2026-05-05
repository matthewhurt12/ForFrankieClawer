#!/usr/bin/env python3
"""
Facebook Marketplace Apify Production Run 001
Athens/Atlanta vintage audio searches
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
ACTOR_ID = "apify~facebook-marketplace-scraper"

# Production settings
MAX_ITEMS_PER_URL = 25
MAX_COST = 0.50

# Output paths
OUTPUT_DIR = Path("data/external_leads")
RAW_OUTPUT = OUTPUT_DIR / "facebook_marketplace_raw_run_001.json"
CSV_OUTPUT = OUTPUT_DIR / "facebook_marketplace_leads.csv"
LEAD_INTAKE = Path("lead_intake.csv")

# Athens/Atlanta search URLs - Best First List
SEARCH_URLS = [
    "https://www.facebook.com/marketplace/athens-ga/search/?query=vintage%20stereo",
    "https://www.facebook.com/marketplace/athens-ga/search/?query=vintage%20receiver",
    "https://www.facebook.com/marketplace/athens-ga/search/?query=technics%20sl-1200",
    "https://www.facebook.com/marketplace/athens-ga/search/?query=mcintosh%20amplifier",
    "https://www.facebook.com/marketplace/atlanta/search/?query=vintage%20stereo",
    "https://www.facebook.com/marketplace/atlanta/search/?query=technics%20sl-1200",
    "https://www.facebook.com/marketplace/atlanta/search/?query=mcintosh%20amplifier",
    "https://www.facebook.com/marketplace/atlanta/search/?query=marantz%20receiver",
]


def run_scraper():
    """Run Facebook Marketplace scraper via Apify."""
    print("="*80)
    print("FACEBOOK MARKETPLACE APIFY RUN 001")
    print("="*80)
    print()
    print("⚠️  FACEBOOK_ACTIVE_CONTEXT_ONLY")
    print("⚠️  NEEDS_MANUAL_REVIEW")
    print()
    print(f"Settings:")
    print(f"  Max items per URL: {MAX_ITEMS_PER_URL}")
    print(f"  Max cost: ${MAX_COST}")
    print(f"  URLs: {len(SEARCH_URLS)}")
    print()
    
    # Actor input
    actor_input = {
        "startUrls": [{"url": url} for url in SEARCH_URLS],
        "maxItems": MAX_ITEMS_PER_URL,
        "extendOutputFunction": "",
        "proxyConfiguration": {
            "useApifyProxy": True
        }
    }
    
    print("Search URLs:")
    for i, url in enumerate(SEARCH_URLS, 1):
        print(f"  {i}. {url}")
    print()
    
    endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"
    
    print("Starting actor run...")
    print("(This may take 2-3 minutes)")
    print()
    
    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {APIFY_TOKEN}",
                "Content-Type": "application/json"
            },
            json=actor_input,
            timeout=300  # 5 minutes
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            items = response.json()
            print(f"✓ Retrieved {len(items)} items")
            return items
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text[:500])
            return []
            
    except requests.exceptions.Timeout:
        print("✗ Timeout (>5 minutes)")
        return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def normalize_item(item):
    """
    Normalize Facebook Marketplace item.
    Store ONLY: title, price, listing URL, photo URL, location, source, scraped_at
    DO NOT store seller personal data.
    """
    # Extract price from listing_price object
    price = None
    listing_price = item.get('listing_price')
    if listing_price:
        try:
            price = float(listing_price.get('amount', 0))
        except:
            pass
    
    # Get title
    title = item.get('marketplace_listing_title') or item.get('custom_title')
    
    # Get photo URL
    photo_url = None
    photo = item.get('primary_listing_photo')
    if photo:
        photo_url = photo.get('photo_image_url')
    
    # Get location from search URL
    location = None
    fb_url = item.get('facebookUrl', '')
    if 'athens-ga' in fb_url or 'athens' in fb_url.lower():
        location = "Athens, GA"
    elif 'atlanta' in fb_url.lower():
        location = "Atlanta, GA"
    
    return {
        'source': 'facebook_marketplace_apify',
        'title': title,
        'price': f"{price:.2f}" if price else None,
        'listing_url': item.get('listingUrl'),
        'photo_url': photo_url,
        'location': location,
        'search_url': fb_url,
        'scraped_at': datetime.now(timezone.utc).isoformat(),
        'review_status': 'FACEBOOK_ACTIVE_CONTEXT_ONLY',
        'notes': 'NEEDS_MANUAL_REVIEW | NEEDS_MANUAL_SOLD_COMPS'
    }


def deduplicate(items):
    """Deduplicate by listing_url."""
    seen = set()
    unique = []
    
    for item in items:
        url = item.get('listing_url')
        if url and url not in seen:
            seen.add(url)
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
        if not item.get('price'):
            continue
        
        try:
            price = float(item['price'])
        except:
            continue
        
        if price > max_price or price < 10:  # Skip free/very cheap items
            continue
        
        if not item.get('title'):
            continue
        
        candidates.append(item)
    
    # Sort by price ascending
    candidates.sort(key=lambda x: float(x.get('price', 999999)))
    
    return candidates


def add_to_lead_intake(items):
    """Add top candidates to lead_intake.csv."""
    if not items:
        return
    
    lead_rows = []
    
    for item in items[:10]:  # Top 10 only
        lead_rows.append({
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Facebook Marketplace (Apify)',
            'listing_url': item.get('listing_url', ''),
            'screenshot_path': '',
            'model_guess': '',  # Will be classified by manual_lead_review.py
            'title': item.get('title', '')[:200],
            'asking_price': item.get('price', ''),
            'location': item.get('location', 'GA'),
            'seller_condition_claim': '',
            'photos_available': 'yes' if item.get('photo_url') else 'no',
            'notes': f"Facebook Marketplace. Location: {item.get('location', 'GA')}",
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
    # Run scraper
    raw_items = run_scraper()
    
    if not raw_items:
        print()
        print("✗ No items retrieved")
        return
    
    print()
    print("="*80)
    print("Processing Results")
    print("="*80)
    print()
    
    # Save raw output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(RAW_OUTPUT, 'w') as f:
        json.dump(raw_items, f, indent=2)
    print(f"✓ Raw output: {RAW_OUTPUT}")
    print(f"  Total raw items: {len(raw_items)}")
    print()
    
    # Normalize
    normalized = [normalize_item(item) for item in raw_items]
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
            print(f"   ${item['price']} | {item['location']}")
        print()
        
        # Add to lead intake
        add_to_lead_intake(candidates)
        print()
    
    # Estimate cost
    estimated_cost = len(SEARCH_URLS) * 0.02  # ~$0.02 per search
    print("="*80)
    print("Run Complete")
    print("="*80)
    print()
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print(f"Within budget: {'✓' if estimated_cost <= MAX_COST else '✗'}")
    print()
    print("Next step:")
    print("  python3 manual_lead_review.py")
    print()


if __name__ == "__main__":
    main()
