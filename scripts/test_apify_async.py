#!/usr/bin/env python3
"""
Test Apify Mercari Actor - Async approach
"""

import os
import json
import time
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"
API_BASE = "https://api.apify.com/v2"

test_query = "iphone"

print("="*80)
print("Apify Mercari Actor - Async Test")
print("="*80)
print()

# Build input
search_url = f"https://www.mercari.com/search/?keyword={test_query}"

actor_input = {
    "startUrls": [{"url": search_url}],
    "maxItems": 10
}

print(f"1. Starting actor run...")
print(f"   Actor: {ACTOR_ID}")
print(f"   Query: {test_query}")
print()

# Start actor run (async)
run_url = f"{API_BASE}/acts/{ACTOR_ID}/runs"

try:
    response = requests.post(
        run_url,
        params={"token": APIFY_TOKEN},
        json=actor_input
    )
    
    response.raise_for_status()
    run_data = response.json()
    
    run_id = run_data['data']['id']
    status = run_data['data']['status']
    
    print(f"✓ Run started")
    print(f"   Run ID: {run_id}")
    print(f"   Status: {status}")
    print()
    
    # Wait for completion
    print(f"2. Waiting for completion...")
    
    max_wait = 120  # 2 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        # Check status
        status_url = f"{API_BASE}/actor-runs/{run_id}"
        status_response = requests.get(status_url, params={"token": APIFY_TOKEN})
        status_data = status_response.json()
        
        current_status = status_data['data']['status']
        print(f"   Status: {current_status}")
        
        if current_status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
            break
        
        time.sleep(5)
    
    print()
    
    if current_status == 'SUCCEEDED':
        print(f"✓ Run succeeded")
        print()
        
        # Get dataset
        dataset_id = status_data['data']['defaultDatasetId']
        print(f"3. Fetching dataset...")
        print(f"   Dataset ID: {dataset_id}")
        
        dataset_url = f"{API_BASE}/datasets/{dataset_id}/items"
        dataset_response = requests.get(dataset_url, params={"token": APIFY_TOKEN})
        
        items = dataset_response.json()
        print(f"   Items: {len(items)}")
        print()
        
        if items:
            print("Sample item:")
            print(json.dumps(items[0], indent=2)[:500])
        else:
            print("No items in dataset")
    else:
        print(f"✗ Run status: {current_status}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
