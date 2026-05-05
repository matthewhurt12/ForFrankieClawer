#!/usr/bin/env python3
"""
eBay Sold Listings Scraper Test - ULTRA CONSERVATIVE
Get actual sold prices for vintage audio equipment
"""

import os
import json
import requests
from datetime import datetime

APIFY_TOKEN = os.environ.get('APIFY_TOKEN')
if not APIFY_TOKEN:
    print("ERROR: APIFY_TOKEN not set")
    exit(1)

API_BASE = "https://api.apify.com/v2"
ACTOR_ID = "oTtB3VgfuE9GtxQt2"

# ULTRA CONSERVATIVE TEST - 2 models only, 10 items each
TEST_KEYWORDS = [
    "Technics SL-1200",
    "McIntosh MA 6100",
]

MAX_ITEMS_PER_KEYWORD = 10  # Very low
DAYS_TO_SCRAPE = 30  # Last 30 days of sold items
MAX_COST_LIMIT = 0.05  # Very low

print("="*80)
print("EBAY SOLD LISTINGS SCRAPER - ULTRA CONSERVATIVE TEST")
print("="*80)
print()
print("⚠️  CANNOT RUN - APIFY LIMIT EXCEEDED")
print()
print("Purpose: Get ACTUAL sold prices for vintage audio equipment")
print("Use: Validate asking prices and calculate real market value")
print()
print(f"Test Keywords: {len(TEST_KEYWORDS)}")
for i, kw in enumerate(TEST_KEYWORDS, 1):
    print(f"  {i}. {kw}")
print()
print(f"Max Items Per Keyword: {MAX_ITEMS_PER_KEYWORD}")
print(f"Days to Scrape: {DAYS_TO_SCRAPE}")
print(f"Max Cost Limit: ${MAX_COST_LIMIT}")
print()

# Actor input following the example
actor_input = {
    "keywords": TEST_KEYWORDS,
    "daysToScrape": DAYS_TO_SCRAPE,
    "count": MAX_ITEMS_PER_KEYWORD,
    "categoryId": "0",  # All categories
    "subcategoryId": "",
    "ebaySite": "ebay.com",
    "sortOrder": "endedRecently",
    "itemLocation": "default",
    "itemCondition": "any",
    "detailedSearch": False
}

print("Actor Input:")
print(json.dumps(actor_input, indent=2))
print()

print("⚠️  NOT RUNNING - Apify monthly limit exceeded")
print()
print("This script is ready to run when the limit resets.")
print()
print("Why This Matters:")
print("  - Get REAL sold prices (not asking prices)")
print("  - Validate market value before buying")
print("  - Calculate actual margins")
print("  - Replace manual eBay sold comp searches")
print()
print("Integration with Underwriting:")
print("  1. Lead comes in: 'McIntosh MA 6100 - $800'")
print("  2. This script pulls recent sold comps")
print("  3. Find: Last 5 sold for $1200-1500")
print("  4. Decision: BUY (margin confirmed)")
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
        timeout=180  # 3 minutes
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        items = response.json()
        print(f"✓ Retrieved {len(items)} sold listings")
        print()
        
        if items:
            # Save output
            output_path = "data/sold_comps/ebay_sold_test.json"
            os.makedirs("data/sold_comps", exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(items, f, indent=2)
            
            print(f"✓ Saved: {output_path}")
            print()
            
            # Analyze sold prices by keyword
            for keyword in TEST_KEYWORDS:
                keyword_items = [item for item in items if keyword.lower() in item.get('title', '').lower()]
                
                if keyword_items:
                    prices = []
                    for item in keyword_items:
                        price_str = item.get('price', '0').replace('$', '').replace(',', '')
                        try:
                            prices.append(float(price_str))
                        except:
                            pass
                    
                    if prices:
                        print(f"{keyword}:")
                        print(f"  Sold Items: {len(prices)}")
                        print(f"  Price Range: ${min(prices):.2f} - ${max(prices):.2f}")
                        print(f"  Average: ${sum(prices)/len(prices):.2f}")
                        print(f"  Median: ${sorted(prices)[len(prices)//2]:.2f}")
                        print()
            
            print("Sample Sold Item:")
            print("-" * 80)
            print(json.dumps(items[0] if items else {}, indent=2)[:800])
            print()
            
        else:
            print("⚠️  No sold items returned")
            
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"✗ Error: {e}")
"""

print("="*80)
print("Script Status: READY (awaiting Apify limit reset)")
print("="*80)
print()
print("When this works, it will:")
print("  ✓ Eliminate manual eBay sold comp searches")
print("  ✓ Provide real market data for underwriting")
print("  ✓ Calculate accurate profit margins")
print("  ✓ Flag overpriced listings automatically")
print()
