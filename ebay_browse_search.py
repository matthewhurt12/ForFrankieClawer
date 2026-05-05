#!/usr/bin/env python3
"""
eBay Browse API Search - Active Listings Only
Usage: python ebay_browse_search.py "search query"

ACTIVE_LISTING_CONTEXT_ONLY
This pulls current active listings. Do not use as sold comps.
"""

import json
import csv
import sys
import requests
import base64
from pathlib import Path
from datetime import datetime


def load_credentials():
    """Load eBay credentials from JSON file."""
    creds_path = Path("credentials/ebay-sandbox.json")
    with open(creds_path) as f:
        return json.load(f)


def get_application_token(app_id, cert_id, environment="sandbox"):
    """Get application access token using client credentials flow."""
    if environment == "sandbox":
        token_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    else:
        token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    credentials = f"{app_id}:{cert_id}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_credentials}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    
    return response.json()


def search_items(access_token, keyword, environment="sandbox", limit=10):
    """
    Search for items using Browse API.
    Returns active listings only.
    """
    if environment == "sandbox":
        api_base = "https://api.sandbox.ebay.com"
    else:
        api_base = "https://api.ebay.com"
    
    url = f"{api_base}/buy/browse/v1/item_summary/search"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        "Content-Type": "application/json"
    }
    
    params = {
        "q": keyword,
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()


def extract_item_data(item):
    """Extract relevant fields from an item."""
    # Price
    price_value = None
    price_currency = None
    if "price" in item:
        price_value = item["price"].get("value")
        price_currency = item["price"].get("currency")
    
    # Shipping cost
    shipping_cost = None
    if "shippingOptions" in item and len(item["shippingOptions"]) > 0:
        shipping_option = item["shippingOptions"][0]
        if "shippingCost" in shipping_option:
            shipping_cost = shipping_option["shippingCost"].get("value")
    
    # Seller
    seller_username = item.get("seller", {}).get("username")
    seller_feedback_percentage = item.get("seller", {}).get("feedbackPercentage")
    
    # Image
    image_url = None
    if "image" in item:
        image_url = item["image"].get("imageUrl")
    elif "thumbnailImages" in item and len(item["thumbnailImages"]) > 0:
        image_url = item["thumbnailImages"][0].get("imageUrl")
    
    # Buying options
    buying_options = ", ".join(item.get("buyingOptions", []))
    
    return {
        "item_id": item.get("itemId"),
        "title": item.get("title"),
        "price_value": price_value,
        "price_currency": price_currency,
        "shipping_cost": shipping_cost,
        "condition": item.get("condition"),
        "buying_options": buying_options,
        "seller_username": seller_username,
        "seller_feedback_percentage": seller_feedback_percentage,
        "item_web_url": item.get("itemWebUrl"),
        "image_url": image_url
    }


def save_results(items_data, keyword, environment):
    """Save results to JSON and CSV."""
    # Create output directory
    output_dir = Path("data/ebay_active_search")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize keyword for filename
    safe_keyword = keyword.lower().replace(" ", "_").replace('"', '')
    
    # Add metadata
    output_data = {
        "context": "ACTIVE_LISTING_CONTEXT_ONLY",
        "warning": "Do not use active listings as sold comps",
        "query": keyword,
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "count": len(items_data),
        "items": items_data
    }
    
    # Save JSON
    json_path = output_dir / f"{safe_keyword}_{environment}.json"
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"✓ Saved JSON: {json_path}")
    
    # Save CSV
    csv_path = output_dir / f"{safe_keyword}_{environment}.csv"
    if items_data:
        fieldnames = list(items_data[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items_data)
        print(f"✓ Saved CSV: {csv_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python ebay_browse_search.py \"search query\"")
        print("Example: python ebay_browse_search.py \"McIntosh MA 5100\"")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print("=" * 70)
    print("eBay Browse API Search - ACTIVE_LISTING_CONTEXT_ONLY")
    print("=" * 70)
    print(f"Query: {keyword}")
    print()
    
    # Load credentials and get token
    creds = load_credentials()
    print(f"Environment: {creds['environment']}")
    
    try:
        token_response = get_application_token(
            creds['app_id'],
            creds['cert_id'],
            creds['environment']
        )
        access_token = token_response['access_token']
        print("✓ OAuth token acquired")
        
        # Search items
        results = search_items(access_token, keyword, creds['environment'], limit=10)
        
        if "itemSummaries" not in results or len(results["itemSummaries"]) == 0:
            print("✗ No items found")
            return
        
        items = results["itemSummaries"]
        print(f"✓ Found {len(items)} items")
        print()
        
        # Extract data
        items_data = [extract_item_data(item) for item in items]
        
        # Display summary
        print("Top Results:")
        print("-" * 70)
        for i, item in enumerate(items_data[:5], 1):
            price_str = f"${item['price_value']}" if item['price_value'] else "N/A"
            condition_str = item['condition'] or "N/A"
            print(f"{i}. {item['title'][:60]}")
            print(f"   Price: {price_str} | Condition: {condition_str}")
            print()
        
        # Save results
        save_results(items_data, keyword, creds['environment'])
        
        print()
        print("⚠️  ACTIVE_LISTING_CONTEXT_ONLY - Do not use as sold comps")
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ API Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
