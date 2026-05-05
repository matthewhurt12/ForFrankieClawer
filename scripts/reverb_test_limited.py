#!/usr/bin/env python3
"""
Reverb.com Scraper - LIMITED TEST RUN
CONSERVATIVE LIMITS to avoid burning credits
"""

import os
import json
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "RenntKrxUtdZQl1jH"

# CONSERVATIVE TEST LIMITS
TEST_KEYWORDS = [
    "Technics SL-1200",
    "Nakamichi Dragon",
    "Moog synthesizer"
]

MAX_LISTINGS_PER_SEARCH = 10  # Very low for testing
ESTIMATED_COST_PER_SEARCH = 0.02  # Rough estimate
MAX_TOTAL_COST = 0.10  # Hard limit for test

print("="*80)
print("REVERB.COM SCRAPER - LIMITED TEST")
print("="*80)
print()
print("⚠️  TEST MODE - CONSERVATIVE LIMITS")
print()
print(f"Test Keywords: {len(TEST_KEYWORDS)}")
for i, kw in enumerate(TEST_KEYWORDS, 1):
    print(f"  {i}. {kw}")
print()
print(f"Max Listings Per Search: {MAX_LISTINGS_PER_SEARCH}")
print(f"Estimated Cost: ${ESTIMATED_COST_PER_SEARCH * len(TEST_KEYWORDS):.2f}")
print(f"Max Total Cost Limit: ${MAX_TOTAL_COST}")
print()

if (ESTIMATED_COST_PER_SEARCH * len(TEST_KEYWORDS)) > MAX_TOTAL_COST:
    print(f"✗ ABORTED: Estimated cost exceeds limit!")
    print(f"  Reduce number of keywords or max listings")
    exit(1)

print("Proceeding with test...")
print()

# Actor input - following the API example
actor_input = {
    "searchQueries": TEST_KEYWORDS,
    "maxListings": MAX_LISTINGS_PER_SEARCH,
    "condition": "all",
    "proxyConfiguration": {
        "useApifyProxy": True
    }
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

# Run actor (sync endpoint for simplicity)
endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print("Starting actor run...")
print("(Max wait: 3 minutes)")
print()

try:
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {APIFY_TOKEN}",
            "Content-Type": "application/json"
        },
        json=actor_input,
        timeout=180  # 3 minutes max
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        items = response.json()
        print(f"✓ Retrieved {len(items)} items")
        print()
        
        if items:
            # Save raw output
            output_path = "data/external_leads/reverb_test_raw.json"
            os.makedirs("data/external_leads", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            # Show first item structure
            print("First Item Structure:")
            print("-" * 80)
            print(json.dumps(items[0], indent=2)[:1500])
            print()
            
            # Summary
            print("="*80)
            print("TEST COMPLETE")
            print("="*80)
            print()
            print(f"Items retrieved: {len(items)}")
            print(f"Estimated cost: ${ESTIMATED_COST_PER_SEARCH * len(TEST_KEYWORDS):.2f}")
            print()
            print("✓ Actor works!")
            print()
            print("Next: Review data structure and create production script")
            
        else:
            print("⚠️  No items returned (but no error)")
            print()
            print("Possible reasons:")
            print("  - No listings for these search terms")
            print("  - Actor needs different input format")
            print("  - Reverb blocking requests")
            
    else:
        print(f"✗ Error: {response.status_code}")
        print()
        print("Response:")
        print(response.text[:1000])
        
except requests.exceptions.Timeout:
    print("✗ Timeout (>3 minutes)")
    print()
    print("Actor may need more time or there's an issue")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
