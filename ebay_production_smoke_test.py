#!/usr/bin/env python3
"""
eBay Production Browse API Smoke Test
Searches for "McIntosh MA 5100" active listings.
Returns top 5 results only.

ACTIVE_LISTING_CONTEXT_ONLY
Do not use active listings as sold comps.
Do not persist eBay user data, orders, messages, or personal information.
"""

import json
import csv
import requests
import base64
from pathlib import Path
from datetime import datetime, timezone


def load_credentials(environment="production"):
    """Load eBay credentials from JSON file."""
    creds_path = Path(f"credentials/ebay-{environment}.json")
    with open(creds_path) as f:
        return json.load(f)


def get_application_token(app_id, cert_id, environment="production"):
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


def search_items(access_token, keyword, marketplace_id="EBAY_US", environment="production", limit=5):
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
        "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
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
    """
    Extract ONLY basic listing fields.
    Do NOT extract seller usernames, account data, or personal information.
    """
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
        "warning": "Do not use active listings as sold comps. Do not persist eBay user data.",
        "query": keyword,
        "environment": environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
    keyword = "McIntosh MA 5100"
    environment = "production"
    
    print("=" * 70)
    print("eBay PRODUCTION Browse API Smoke Test")
    print("=" * 70)
    print(f"Query: {keyword}")
    print(f"Environment: {environment.upper()}")
    print()
    
    # Load credentials and get token
    creds = load_credentials(environment)
    marketplace_id = creds.get("marketplace_id", "EBAY_US")
    
    try:
        print("Step 1: Getting OAuth application token...")
        token_response = get_application_token(
            creds['app_id'],
            creds['cert_id'],
            environment
        )
        access_token = token_response['access_token']
        print("✓ OAuth token acquired")
        print()
        
        # Search items
        print(f"Step 2: Searching active listings for '{keyword}'...")
        results = search_items(access_token, keyword, marketplace_id, environment, limit=5)
        
        if "itemSummaries" not in results or len(results["itemSummaries"]) == 0:
            print("✗ No items found")
            print()
            print("Note: This may be expected for niche items like 'McIntosh MA 5100'.")
            print("The API connection is working if you received this message.")
            return
        
        items = results["itemSummaries"]
        print(f"✓ Found {len(items)} items")
        print()
        
        # Extract data
        items_data = [extract_item_data(item) for item in items]
        
        # Display summary
        print("Step 3: Top 5 Results:")
        print("-" * 70)
        for i, item in enumerate(items_data, 1):
            price_str = f"${item['price_value']}" if item['price_value'] else "N/A"
            condition_str = item['condition'] or "N/A"
            print(f"{i}. {item['title'][:60]}")
            print(f"   Price: {price_str} | Condition: {condition_str}")
            print()
        
        # Save results
        print("Step 4: Saving results...")
        save_results(items_data, keyword, environment)
        
        print()
        print("=" * 70)
        print("✓ Smoke test completed successfully")
        print("=" * 70)
        print("⚠️  ACTIVE_LISTING_CONTEXT_ONLY")
        print("⚠️  Do not use as sold comps")
        print("⚠️  Do not persist eBay user data, orders, or messages")
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ API Error: {e}")
        if hasattr(e, 'response'):
            print(f"Status Code: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
