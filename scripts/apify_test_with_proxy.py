#!/usr/bin/env python3
"""
Test Apify actor with Apify Proxy enabled
"""

import os
import json
import requests
import time

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"

print("="*80)
print("APIFY TEST - WITH PROXY ENABLED")
print("="*80)
print()

# Try with Apify proxy enabled (may help avoid bot detection)
actor_input = {
    "urls": ["https://www.mercari.com/us/category/84/"],
    "max_items_per_url": 20,
    "ignore_url_failures": True,
    "proxy": {
        "useApifyProxy": True  # ENABLE PROXY
    }
}

print("Configuration:")
print(json.dumps(actor_input, indent=2))
print()
print("Starting actor run with Apify proxy enabled...")
print()

# Start async run
run_endpoint = f"{API_BASE}/acts/{ACTOR_ID}/runs"

try:
    response = requests.post(
        run_endpoint,
        headers={
            "Authorization": f"Bearer {APIFY_TOKEN}",
            "Content-Type": "application/json"
        },
        json=actor_input
    )
    
    if response.status_code != 201:
        print(f"✗ Failed to start: {response.status_code}")
        print(response.text[:500])
        exit(1)
    
    run_data = response.json()
    run_id = run_data['data']['id']
    
    print(f"✓ Run started: {run_id}")
    print()
    print("Waiting for completion (max 3 minutes)...")
    print()
    
    # Wait for completion
    max_wait = 180
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        time.sleep(5)
        
        status_response = requests.get(
            f"{API_BASE}/actor-runs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            current_status = status_data['data']['status']
            
            print(f"  Status: {current_status}")
            
            if current_status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
                break
    
    print()
    
    if current_status != 'SUCCEEDED':
        print(f"✗ Run failed: {current_status}")
        
        # Get logs
        log_response = requests.get(
            f"{API_BASE}/logs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
        )
        if log_response.status_code == 200:
            print()
            print("Logs:")
            print("-" * 80)
            print(log_response.text[-1000:])  # Last 1000 chars
        exit(1)
    
    print("✓ Run succeeded")
    print()
    
    # Get dataset
    dataset_id = status_data['data'].get('defaultDatasetId')
    print(f"Fetching dataset: {dataset_id}")
    
    dataset_response = requests.get(
        f"{API_BASE}/datasets/{dataset_id}/items",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    if dataset_response.status_code == 200:
        items = dataset_response.json()
        print(f"Items returned: {len(items)}")
        print()
        
        if items:
            print("✓✓✓ SUCCESS! Data retrieved!")
            print()
            print("First 3 items:")
            for i, item in enumerate(items[:3], 1):
                print(f"{i}. {item.get('name', 'N/A')}")
                print(f"   Price: ${item.get('price', 0) / 100:.2f}")
                print(f"   Status: {item.get('status', 'N/A')}")
                print()
            
            # Save results
            with open("data/mercari_test_results.json", "w") as f:
                json.dump(items, f, indent=2)
            print("✓ Saved to: data/mercari_test_results.json")
        else:
            print("✗ Still zero items")
            
            # Check logs
            print()
            print("Checking logs...")
            log_response = requests.get(
                f"{API_BASE}/logs/{run_id}",
                headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
            )
            if log_response.status_code == 200:
                print()
                print("Logs:")
                print("-" * 80)
                print(log_response.text)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
