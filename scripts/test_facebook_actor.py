#!/usr/bin/env python3
"""Test Facebook Marketplace actor"""

import os
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
API_BASE = "https://api.apify.com/v2"

# Try different actor ID formats
actor_ids = [
    "apify/facebook-marketplace-scraper",
    "facebook-marketplace-scraper",
    "apify~facebook-marketplace-scraper",
]

print("Testing Facebook Marketplace actor IDs...")
print()

for actor_id in actor_ids:
    endpoint = f"{API_BASE}/acts/{actor_id}"
    
    response = requests.get(
        endpoint,
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    print(f"Actor ID: {actor_id}")
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        actor_data = response.json()
        print(f"  ✓ Found!")
        print(f"  Name: {actor_data['data'].get('name')}")
        print(f"  Default Run Options:")
        print(f"    Build: {actor_data['data'].get('defaultRunOptions', {}).get('build')}")
    else:
        print(f"  ✗ Not found")
    
    print()
