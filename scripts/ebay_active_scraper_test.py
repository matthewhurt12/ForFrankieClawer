#!/usr/bin/env python3
"""
eBay Active Listings Scraper Test - DO NOT RUN YET
Alternative to eBay Browse API for active listings
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

# ULTRA CONSERVATIVE TEST
TEST_URLS = [
    "https://www.ebay.com/sch/i.html?_nkw=technics+sl-1200&_sop=10",  # Price: lowest first
    "https://www.ebay.com/sch/i.html?_nkw=mcintosh+ma+6100&_sop=10",
]

MAX_ITEMS_PER_URL = 10  # Very low
MAX_COST_LIMIT = 0.10

print("="*80)
print("EBAY ACTIVE LISTINGS SCRAPER - DO NOT RUN YET")
print("="*80)
print()
print("⚠️  DO NOT RUN - APIFY LIMIT EXCEEDED")
print()
print("Purpose: Alternative to eBay Browse API for active listings")
print("Use: Scrape current eBay listings (not sold items)")
print()
print(f"Test URLs: {len(TEST_URLS)}")
for i, url in enumerate(TEST_URLS, 1):
    print(f"  {i}. {url}")
print()
print(f"Max Items Per URL: {MAX_ITEMS_PER_URL}")
print(f"Max Cost Limit: ${MAX_COST_LIMIT}")
print()

# Actor input following the example
actor_input = {
    "startUrls": [{"url": url} for url in TEST_URLS],
    "maxItems": MAX_ITEMS_PER_URL,
    "proxyConfig": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"],
        "apifyProxyCountry": "US"  # Changed to US for our market
    }
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

print("="*80)
print("⚠️  DO NOT RUN THIS SCRIPT YET")
print("="*80)
print()
print("Reasons:")
print("  1. Apify monthly limit already exceeded")
print("  2. We already have eBay Browse API working")
print("  3. This is a backup/alternative method")
print()
print("When to Use This:")
print("  • If eBay Browse API stops working")
print("  • If you need more data fields")
print("  • If Browse API rate limits hit")
print()
print("Test Priority: LOW")
print("  - Test eBay Sold Comps first (higher value)")
print("  - Test Reverb second (new lead source)")
print("  - Test this only if Browse API fails")
print()
print("Ready to run when needed:")
print("  export APIFY_TOKEN='your-token'")
print("  python3 scripts/ebay_active_scraper_test.py --actually-run")
print()

# Check for --actually-run flag
import sys
if "--actually-run" not in sys.argv:
    print("Exiting without running (safety check).")
    print("Add --actually-run flag to execute.")
    exit(0)

# Actual execution code (only runs with flag)
endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print()
print("Starting actor run...")
print("(This will use Apify credits)")
print()

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
        print()
        
        if items:
            # Save output
            output_path = "data/test_outputs/ebay_active_scraper_test.json"
            os.makedirs("data/test_outputs", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            # Show first item structure
            print("First Item Structure:")
            print("-" * 80)
            print(json.dumps(items[0], indent=2)[:1500])
            print()
            
            # Compare to Browse API data
            print("Comparison to eBay Browse API:")
            print("  Browse API: Free, fast, official")
            print("  This Actor: Uses credits, more fields(?)")
            print()
            print("Decide: Is this better than Browse API?")
            
        else:
            print("⚠️  No items returned")
            
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"✗ Error: {e}")
