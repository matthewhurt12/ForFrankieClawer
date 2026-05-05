#!/usr/bin/env python3
"""
Apify API Debug 002 - Try async run to compare with sync
"""

import os
import json
import requests
import time

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"

debug_log = []

def log(msg):
    print(msg)
    debug_log.append(msg)

log("="*80)
log("APIFY API DEBUG 002 - ASYNC RUN")
log("="*80)
log("")

# Same input as works in console
actor_input = {
    "urls": ["https://www.mercari.com/us/category/84/"],
    "max_items_per_url": 20,
    "ignore_url_failures": True,
    "proxy": {
        "useApifyProxy": False
    }
}

log("Input Configuration:")
log(json.dumps(actor_input, indent=2))
log("")

# Start async run
log("Starting async actor run...")
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
    
    log(f"Start Status: {response.status_code}")
    
    if response.status_code != 201:
        log(f"✗ Failed to start run")
        log(response.text[:500])
        exit(1)
    
    run_data = response.json()
    run_id = run_data['data']['id']
    status = run_data['data']['status']
    dataset_id = run_data['data'].get('defaultDatasetId')
    
    log(f"✓ Run started")
    log(f"  Run ID: {run_id}")
    log(f"  Status: {status}")
    log(f"  Dataset ID: {dataset_id}")
    log("")
    
    # Wait for completion
    log("Waiting for completion (max 3 minutes)...")
    
    max_wait = 180
    start_time = time.time()
    last_status = status
    
    while time.time() - start_time < max_wait:
        time.sleep(5)
        
        # Check run status
        status_response = requests.get(
            f"{API_BASE}/actor-runs/{run_id}",
            headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            current_status = status_data['data']['status']
            
            if current_status != last_status:
                log(f"  Status: {current_status}")
                last_status = current_status
            
            if current_status in ['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT']:
                break
    
    log("")
    
    if current_status != 'SUCCEEDED':
        log(f"✗ Run did not succeed: {current_status}")
        exit(1)
    
    log(f"✓ Run succeeded")
    
    # Get final dataset ID
    final_dataset_id = status_data['data'].get('defaultDatasetId')
    log(f"  Final Dataset ID: {final_dataset_id}")
    log("")
    
    # Fetch dataset items
    log("Fetching dataset items...")
    dataset_response = requests.get(
        f"{API_BASE}/datasets/{final_dataset_id}/items",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    log(f"  Dataset Status: {dataset_response.status_code}")
    
    if dataset_response.status_code == 200:
        items = dataset_response.json()
        log(f"  Items returned: {len(items)}")
        log("")
        
        if items:
            log("✓ Data found!")
            log("")
            log("First Item:")
            first = items[0]
            log(f"  Name: {first.get('name', 'N/A')}")
            log(f"  Price: ${first.get('price', 0) / 100:.2f}")
            log(f"  Status: {first.get('status', 'N/A')}")
            log(f"  ID: {first.get('id', 'N/A')}")
            log("")
            
            log("Full first item:")
            log(json.dumps(first, indent=2))
        else:
            log("✗ Zero items in dataset")
            log("")
            log("Checking dataset info...")
            
            # Get dataset info
            dataset_info_response = requests.get(
                f"{API_BASE}/datasets/{final_dataset_id}",
                headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
            )
            
            if dataset_info_response.status_code == 200:
                dataset_info = dataset_info_response.json()
                log("Dataset Info:")
                log(json.dumps(dataset_info, indent=2)[:1000])
            
            # Check KV store for any other data
            log("")
            log("Checking key-value store...")
            kv_store_id = status_data['data'].get('defaultKeyValueStoreId')
            if kv_store_id:
                kv_response = requests.get(
                    f"{API_BASE}/key-value-stores/{kv_store_id}/records/OUTPUT",
                    headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
                )
                log(f"  OUTPUT record status: {kv_response.status_code}")
                if kv_response.status_code == 200:
                    log(f"  OUTPUT content: {kv_response.text[:500]}")
    
    else:
        log(f"✗ Failed to fetch dataset: {dataset_response.status_code}")
        log(dataset_response.text[:500])
        
except Exception as e:
    log(f"✗ Error: {e}")
    import traceback
    log(traceback.format_exc())

log("")
log("="*80)
log("Debug Complete")
log("="*80)

# Save log
with open("reports/APIFY_API_DEBUG_002_ASYNC.md", "w") as f:
    f.write("# Apify API Debug 002 - Async Run\n\n")
    f.write("**Date:** 2026-05-04\n\n")
    f.write("---\n\n")
    f.write("## Debug Log\n\n")
    f.write("```\n")
    for line in debug_log:
        f.write(line + "\n")
    f.write("```\n")

print("")
print("✓ Debug log saved: reports/APIFY_API_DEBUG_002_ASYNC.md")
