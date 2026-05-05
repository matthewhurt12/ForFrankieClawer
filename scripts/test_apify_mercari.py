#!/usr/bin/env python3
"""
Test Apify Mercari Actor - Debug version
"""

import os
import json
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"
API_BASE = "https://api.apify.com/v2"

# Test with a very common search
test_query = "iphone"

print("="*80)
print("Apify Mercari Actor Debug Test")
print("="*80)
print()
print(f"Actor: {ACTOR_ID}")
print(f"Query: {test_query}")
print(f"Token: {APIFY_TOKEN[:20]}..." if APIFY_TOKEN else "NOT SET")
print()

# Build search URL
search_url = f"https://www.mercari.com/search/?keyword={test_query}"
print(f"Search URL: {search_url}")
print()

# Actor input
actor_input = {
    "startUrls": [{"url": search_url}],
    "maxItems": 10,
    "proxy": {
        "useApifyProxy": True
    }
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

# Try to run actor
url = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"

print(f"API Endpoint: {url}")
print()
print("Running actor...")
print()

try:
    response = requests.post(
        url,
        params={"token": APIFY_TOKEN},
        json=actor_input,
        timeout=120
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        items = response.json()
        print(f"✓ Success!")
        print(f"Items returned: {len(items)}")
        print()
        
        if items:
            print("First item:")
            print(json.dumps(items[0], indent=2))
        else:
            print("No items returned (empty array)")
    else:
        print(f"✗ Error Response:")
        print(response.text[:1000])
        
except Exception as e:
    print(f"✗ Exception: {e}")
