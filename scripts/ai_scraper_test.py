#!/usr/bin/env python3
"""
Apify AI Scraper Test - ULTRA CONSERVATIVE
Extract vintage audio listings from a single page using AI prompts
"""

import os
import json
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "paOtbjvyUiNsr1Qms"

# ULTRA CONSERVATIVE - Single page test only
TEST_URL = "https://www.audiogon.com/listings/solid-state"
PROMPT = """
Extract all vintage audio equipment listings from this page.
For each listing, extract:
- Item title/name
- Price (if shown)
- Condition
- Seller location (if shown)
- Listing URL

Return as JSON array.
"""

MAX_COST_LIMIT = 0.05  # Very low limit

print("="*80)
print("APIFY AI SCRAPER - ULTRA CONSERVATIVE TEST")
print("="*80)
print()
print("⚠️  SINGLE PAGE TEST ONLY")
print("⚠️  CANNOT RUN - APIFY LIMIT EXCEEDED")
print()
print(f"Test URL: {TEST_URL}")
print(f"Max Cost Limit: ${MAX_COST_LIMIT}")
print()

# Actor input
actor_input = {
    "startUrls": [
        {"url": TEST_URL}
    ],
    "prompt": PROMPT
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

print("⚠️  NOT RUNNING - Apify monthly limit exceeded")
print()
print("This script is ready to run when the limit resets.")
print()
print("To run manually:")
print(f"  export APIFY_TOKEN='your-token'")
print(f"  python3 scripts/ai_scraper_test.py")
print()

# Commented out until limit resets
"""
endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print("Starting actor run...")
print()

try:
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {APIFY_TOKEN}",
            "Content-Type": "application/json"
        },
        json=actor_input,
        timeout=120  # 2 minutes max
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        items = response.json()
        print(f"✓ Retrieved {len(items)} items")
        print()
        
        if items:
            # Save output
            output_path = "data/test_outputs/ai_scraper_test.json"
            os.makedirs("data/test_outputs", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            print("Sample Results:")
            print("-" * 80)
            print(json.dumps(items[0] if items else {}, indent=2)[:800])
            print()
            
        else:
            print("⚠️  No items returned")
            
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"✗ Error: {e}")
"""

print("="*80)
print("Script Status: READY (awaiting Apify limit reset)")
print("="*80)
