#!/usr/bin/env python3
"""
eBay Active Listings Scraper - MINIMAL TEST
Single search, 5 items max
"""

import os
import json
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "PBSxkfoBWghbE2set"

# MINIMAL TEST - 1 search only
TEST_URL = "https://www.ebay.com/sch/i.html?_nkw=technics+sl-1200&_sop=10"  # Price: lowest first
MAX_ITEMS = 5  # Very small

print("="*80)
print("EBAY ACTIVE LISTINGS - MINIMAL TEST")
print("="*80)
print()
print("Test: 1 search, 5 items max")
print(f"URL: {TEST_URL}")
print()

# Actor input
actor_input = {
    "startUrls": [{"url": TEST_URL}],
    "maxItems": MAX_ITEMS,
    "proxyConfig": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
        "apifyProxyCountry": "US"
    }
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print("Starting minimal test run...")
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
            output_path = "data/test_outputs/ebay_active_minimal.json"
            os.makedirs("data/test_outputs", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            # Show sample items
            print("Retrieved Items:")
            print("-" * 80)
            for i, item in enumerate(items[:5], 1):
                title = item.get('title', 'N/A')[:60]
                price = item.get('price', 'N/A')
                print(f"{i}. {title}")
                print(f"   Price: {price}")
            print()
            
            # Show data structure
            print("First Item Full Structure:")
            print("-" * 80)
            print(json.dumps(items[0], indent=2))
            print()
            
            print("="*80)
            print("TEST SUCCESSFUL")
            print("="*80)
            print()
            print(f"Items retrieved: {len(items)}")
            print(f"Estimated cost: ~$0.02-0.05")
            print()
            print("Compare to eBay Browse API:")
            print("  Browse API: FREE")
            print("  This Actor: Uses credits")
            print()
            print("Recommendation: Use Browse API unless this has critical data")
            
        else:
            print("⚠️  No items returned (but no error)")
            
    elif response.status_code == 403:
        print(f"✗ Error 403: Monthly limit exceeded")
        print()
        print(response.text[:500])
        print()
        print("Cannot test - wait for Apify limit reset")
        
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
