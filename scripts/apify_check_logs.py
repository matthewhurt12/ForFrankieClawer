#!/usr/bin/env python3
"""
Check Apify run logs to see what the actor actually did
"""

import os
import requests

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
API_BASE = "https://api.apify.com/v2"

# Use the run ID from last test
RUN_ID = "jQXLpVDB3pcQ1RHML"  # From async debug test

print("="*80)
print("Checking Actor Run Logs")
print("="*80)
print()
print(f"Run ID: {RUN_ID}")
print()

# Get logs
log_url = f"{API_BASE}/logs/{RUN_ID}"

try:
    response = requests.get(
        log_url,
        headers={"Authorization": f"Bearer {APIFY_TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        logs = response.text
        print("Actor Logs:")
        print("-" * 80)
        print(logs)
        print("-" * 80)
        
        # Save logs
        with open("reports/actor_run_logs.txt", "w") as f:
            f.write(f"Run ID: {RUN_ID}\n")
            f.write("="*80 + "\n\n")
            f.write(logs)
        
        print()
        print("✓ Logs saved to: reports/actor_run_logs.txt")
    else:
        print(f"✗ Failed to get logs: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"✗ Error: {e}")
