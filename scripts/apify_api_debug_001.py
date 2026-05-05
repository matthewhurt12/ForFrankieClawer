#!/usr/bin/env python3
"""
Apify API Debug - Proper testing with known-good configuration
"""

import os
import json
import requests
import time

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "stealth_mode~mercari-product-search-scraper"

# Debug output
debug_log = []

def log(msg):
    print(msg)
    debug_log.append(msg)

log("="*80)
log("APIFY API DEBUG 001")
log("="*80)
log("")

# Step 1: Verify token
log("Step 1: Verify API Token")
log("-" * 80)

try:
    response = requests.get(
        f"{API_BASE}/users/me",
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    log(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        username = user_data['data'].get('username', 'unknown')
        log(f"✓ Token valid")
        log(f"  Username: {username}")
    else:
        log(f"✗ Token invalid")
        log(f"  Response: {response.text[:200]}")
        exit(1)
except Exception as e:
    log(f"✗ Error: {e}")
    exit(1)

log("")

# Step 2: Test with known-good category URL
log("Step 2: Test Actor with Category URL (Known Working)")
log("-" * 80)
log("URL: https://www.mercari.com/us/category/84/")
log("")

# Exact configuration from user
actor_input = {
    "urls": ["https://www.mercari.com/us/category/84/"],
    "max_items_per_url": 20,
    "ignore_url_failures": True,
    "proxy": {
        "useApifyProxy": False
    }
}

log("Request Body:")
log(json.dumps(actor_input, indent=2))
log("")

endpoint = f"{API_BASE}/acts/{ACTOR_ID}/run-sync-get-dataset-items"
log(f"Endpoint: {endpoint}")
log("")

log("Sending request...")
log("")

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
    
    log(f"HTTP Status: {response.status_code}")
    log("")
    
    if response.status_code == 200 or response.status_code == 201:
        items = response.json()
        
        log(f"✓ Request succeeded")
        log(f"  Items returned: {len(items)}")
        log("")
        
        if items:
            log("First Item:")
            first = items[0]
            log(f"  Name: {first.get('name', 'N/A')}")
            log(f"  Price: ${first.get('price', 0) / 100:.2f}")
            log(f"  Status: {first.get('status', 'N/A')}")
            log(f"  ID: {first.get('id', 'N/A')}")
            log("")
            
            log("Sample of first item structure:")
            log(json.dumps(first, indent=2)[:500])
        else:
            log("✗ Zero items returned")
            log("")
            log("Response body:")
            log(response.text[:1000])
            
    else:
        log(f"✗ Request failed")
        log(f"  Status: {response.status_code}")
        log(f"  Response: {response.text[:1000]}")
        
except requests.exceptions.Timeout:
    log("✗ Request timeout (>3 minutes)")
except Exception as e:
    log(f"✗ Error: {e}")
    import traceback
    log(traceback.format_exc())

log("")

# Step 3: If category worked, test search URL
if len(items) > 0:
    log("="*80)
    log("Step 3: Test with Search URL")
    log("-" * 80)
    log("URL: https://www.mercari.com/search/?keyword=Technics%20SL-1200")
    log("")
    
    search_input = {
        "urls": ["https://www.mercari.com/search/?keyword=Technics%20SL-1200"],
        "max_items_per_url": 20,
        "ignore_url_failures": True,
        "proxy": {
            "useApifyProxy": False
        }
    }
    
    log("Request Body:")
    log(json.dumps(search_input, indent=2))
    log("")
    
    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {APIFY_TOKEN}",
                "Content-Type": "application/json"
            },
            json=search_input,
            timeout=180
        )
        
        log(f"HTTP Status: {response.status_code}")
        log("")
        
        if response.status_code in [200, 201]:
            search_items = response.json()
            
            log(f"Items returned: {len(search_items)}")
            log("")
            
            if search_items:
                log("✓ Search URL works")
                log("")
                log("First Item:")
                first = search_items[0]
                log(f"  Name: {first.get('name', 'N/A')}")
                log(f"  Price: ${first.get('price', 0) / 100:.2f}")
                log(f"  Status: {first.get('status', 'N/A')}")
            else:
                log("⚠️  Search URL returned zero items")
                log("  Issue: Search URL format or no results for this query")
        else:
            log(f"✗ Request failed: {response.status_code}")
            log(response.text[:500])
            
    except Exception as e:
        log(f"✗ Error: {e}")

log("")
log("="*80)
log("Debug Complete")
log("="*80)

# Save debug log
with open("reports/APIFY_API_DEBUG_001.md", "w") as f:
    f.write("# Apify API Debug 001\n\n")
    f.write("**Date:** 2026-05-04\n\n")
    f.write("---\n\n")
    f.write("## Debug Log\n\n")
    f.write("```\n")
    for line in debug_log:
        f.write(line + "\n")
    f.write("```\n")

print("")
print("✓ Debug log saved: reports/APIFY_API_DEBUG_001.md")
