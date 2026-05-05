#!/usr/bin/env python3
"""
eBay Active Listings Scraper (URL-based) - MINIMAL TEST
Test if this shows active listings (not sold)
"""

import os
import json
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "8bXnzCF4JVgMMA5cM"

# MINIMAL TEST - 1 search URL
# eBay search for Technics SL-1200, sorted by lowest price
TEST_URL = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=technics+sl-1200&_sop=15"

print("="*80)
print("EBAY ACTIVE LISTINGS (URL-BASED) - MINIMAL TEST")
print("="*80)
print()
print("Purpose: Show ACTIVE listings (not sold)")
print("Test: 1 search URL, minimal items")
print()
print(f"URL: {TEST_URL}")
print()

# Actor input - uses "listingUrls" not "startUrls"
actor_input = {
    "listingUrls": [TEST_URL]
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print("Starting test run...")
print()

try:
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {APIFY_TOKEN}",
            "Content-Type": "application/json"
        },
        json=actor_input,
        timeout=120  # 2 minutes
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        items = response.json()
        print(f"✓ Retrieved {len(items)} items")
        print()
        
        if items:
            # Save output
            output_path = "data/test_outputs/ebay_active_urls_test.json"
            os.makedirs("data/test_outputs", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            # Show sample items
            print("Retrieved Items (ACTIVE LISTINGS):")
            print("-" * 80)
            for i, item in enumerate(items[:10], 1):
                title = item.get('title', item.get('name', 'N/A'))[:60]
                price = item.get('price', item.get('currentPrice', 'N/A'))
                condition = item.get('condition', 'N/A')
                print(f"{i}. {title}")
                print(f"   Price: {price} | Condition: {condition}")
            print()
            
            # Show data structure
            print("First Item Structure:")
            print("-" * 80)
            print(json.dumps(items[0], indent=2)[:1500])
            print()
            
            print("="*80)
            print("TEST SUCCESSFUL - ACTIVE LISTINGS RETRIEVED")
            print("="*80)
            print()
            print(f"Items retrieved: {len(items)}")
            print()
            print("Comparison:")
            print("  eBay Browse API: Free, official, working")
            print("  This Actor: Uses Apify credits")
            print()
            print("Decide: Does this have data Browse API lacks?")
            
        else:
            print("⚠️  No items returned (but no error)")
            
    elif response.status_code == 403:
        error_data = response.json()
        error_type = error_data.get('error', {}).get('type', '')
        
        if 'actor-is-not-rented' in error_type:
            print(f"✗ Error: This actor requires RENTAL (not free tier)")
            print()
            print(error_data)
            print()
            print("Decision: SKIP - requires paid rental")
        elif 'platform-feature-disabled' in error_type:
            print(f"✗ Error: Monthly limit exceeded")
            print()
            print(error_data)
            print()
            print("Cannot test - wait for Apify limit reset")
        else:
            print(f"✗ Error 403:")
            print(response.text[:500])
        
    else:
        print(f"✗ Error: {response.status_code}")
        print()
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("✗ Timeout")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
