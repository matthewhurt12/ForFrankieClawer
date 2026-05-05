#!/usr/bin/env python3
"""
eBay Active Market Context - Phase 1 (Improved Filtering)
Searches active listings with strict false-positive filtering and category-aware price floors.

ACTIVE_LISTING_CONTEXT_ONLY
TEMPORARY_TEST_OUTPUT
NOT_SOLD_COMPS

Do not store seller usernames, buyer data, messages, orders, or personal account data.
"""

import json
import csv
import sys
import argparse
import requests
import base64
import re
from pathlib import Path
from datetime import datetime, timezone
from statistics import median


# Category price floors (minimum price for a full working unit)
CATEGORY_PRICE_FLOORS = {
    "mcintosh": 500,  # McIntosh integrated amps
    "pioneer": 400,   # Pioneer receivers
    "marantz": 400,   # Marantz receivers
    "sansui": 400,    # Sansui receivers
    "technics sl-1200": 300,  # Technics SL-1200 turntables
    "nakamichi": 75,  # Nakamichi cassette decks
}


# Hard exclude keywords (must not appear in title)
HARD_EXCLUDE_KEYWORDS = [
    "manual", "service manual", "owners manual", "owner's manual", "users manual",
    "brochure", "catalog", "catalogue",
    "lamp", "lamps", "bulb", "bulbs", "led",
    "kit", "rebuild kit", "recap kit", "repair kit", "restoration kit", "upgrade kit",
    "parts", "parts only", "for parts", "part only",
    "repair", "service", "restoration",
    "knob", "knobs",
    "faceplate", "face plate", "glass", "front panel glass",
    "dial", "dial lamp",
    "feet", "foot", "rubber feet",
    "cord", "power cord", "cable",
    "remote", "remote control",
    "copy", "pdf", "digital copy",
    "schematic", "schematics",
    "ad", "advertisement", "print ad",
    "potentiometer", "pot", "volume pot",
    "capacitor", "capacitors", "cap", "caps",
    "transistor", "tube", "tubes",
    "board", "circuit board", "pcb",
    "switch", "switches",
    "meter", "vu meter", "dial meter",
]


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


def search_items(access_token, keyword, marketplace_id="EBAY_US", environment="production", 
                 limit=50, price_min=None, price_max=None, condition=None):
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
    
    # Build filter string
    filters = []
    if price_min is not None:
        filters.append(f"price:[{price_min}..]")
    if price_max is not None:
        if price_min is not None:
            filters[-1] = f"price:[{price_min}..{price_max}]"
        else:
            filters.append(f"price:[..{price_max}]")
    if condition:
        filters.append(f"conditions:{{{condition}}}")
    
    if filters:
        params["filter"] = ",".join(filters)
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()


def detect_category(query):
    """Detect product category from search query to apply appropriate price floor."""
    query_lower = query.lower()
    
    if "mcintosh" in query_lower:
        return "mcintosh", CATEGORY_PRICE_FLOORS["mcintosh"]
    elif "pioneer" in query_lower:
        return "pioneer", CATEGORY_PRICE_FLOORS["pioneer"]
    elif "marantz" in query_lower:
        return "marantz", CATEGORY_PRICE_FLOORS["marantz"]
    elif "sansui" in query_lower:
        return "sansui", CATEGORY_PRICE_FLOORS["sansui"]
    elif "technics" in query_lower and "sl-1200" in query_lower:
        return "technics sl-1200", CATEGORY_PRICE_FLOORS["technics sl-1200"]
    elif "nakamichi" in query_lower:
        return "nakamichi", CATEGORY_PRICE_FLOORS["nakamichi"]
    
    return "unknown", 0  # No price floor for unknown categories


def classify_result(title, price_value, condition, query, category_floor):
    """
    Classify result type and determine if it should be included.
    
    Returns: (result_type, should_include, exclusion_reason)
    
    Result types:
    - EXACT_FULL_UNIT: The exact product being searched for, full working unit
    - SIMILAR_FULL_UNIT: Similar full unit (different model but same category)
    - ACCESSORY: Accessory or add-on part
    - PARTS_REPAIR: Parts, repair components, or non-functional unit
    - WRONG_MODEL: Different model/product entirely
    - UNKNOWN: Cannot classify
    """
    title_lower = title.lower()
    
    # Hard exclude keywords - absolute no-go
    for keyword in HARD_EXCLUDE_KEYWORDS:
        if keyword in title_lower:
            return "PARTS_REPAIR", False, f"hard_exclude:{keyword}"
    
    # Parts condition
    if condition and "parts" in condition.lower():
        return "PARTS_REPAIR", False, "parts_condition"
    
    # Price floor check (if category detected)
    if category_floor > 0 and price_value is not None:
        if price_value < category_floor:
            return "ACCESSORY", False, f"below_price_floor:${price_value}<${category_floor}"
    
    # If it passed all exclusions and has reasonable price, assume it's a full unit
    if price_value and price_value >= category_floor:
        return "EXACT_FULL_UNIT", True, None
    
    # Price present but no floor defined - assume full unit
    if price_value and category_floor == 0:
        return "EXACT_FULL_UNIT", True, None
    
    # No price or edge case
    return "UNKNOWN", False, "no_price_or_edge_case"


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
    
    condition = item.get("condition")
    
    return {
        "item_id": item.get("itemId"),
        "title": item.get("title"),
        "price_value": float(price_value) if price_value else None,
        "price_currency": price_currency,
        "shipping_cost": float(shipping_cost) if shipping_cost else None,
        "condition": condition,
        "buying_options": buying_options,
        "item_web_url": item.get("itemWebUrl"),
        "image_url": image_url
    }


def calculate_metrics(items, category_floor):
    """Calculate summary metrics for full unit listings only."""
    if not items:
        return {
            "active_listing_count": 0,
            "lowest_active_price": None,
            "median_active_price": None,
            "highest_active_price": None,
            "shipping_range": None,
            "condition_counts": {},
            "filter_status": "NO_RESULTS"
        }
    
    prices = [item["price_value"] for item in items if item["price_value"] is not None]
    shipping_costs = [item["shipping_cost"] for item in items if item["shipping_cost"] is not None]
    
    # Condition counts
    condition_counts = {}
    for item in items:
        condition = item.get("condition", "Unknown")
        condition_counts[condition] = condition_counts.get(condition, 0) + 1
    
    median_price = median(prices) if prices else None
    
    # Validate filter quality
    filter_status = "VALID"
    if category_floor > 0 and median_price is not None:
        if median_price < category_floor:
            filter_status = "FILTER_FAILURE_REVIEW_NEEDED"
    
    metrics = {
        "active_listing_count": len(items),
        "lowest_active_price": min(prices) if prices else None,
        "median_active_price": median_price,
        "highest_active_price": max(prices) if prices else None,
        "shipping_range": {
            "min": min(shipping_costs) if shipping_costs else None,
            "max": max(shipping_costs) if shipping_costs else None
        },
        "condition_counts": condition_counts,
        "filter_status": filter_status
    }
    
    return metrics


def save_results(full_units, excluded_items, metrics, keyword, environment, filters_used, category, category_floor):
    """Save results to JSON and CSV with temporary test output marking."""
    # Create output directory
    output_dir = Path("data/ebay_active_search")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize keyword for filename
    safe_keyword = keyword.lower().replace(" ", "_").replace('"', '')
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    # Count exclusion reasons
    exclusion_breakdown = {}
    result_type_counts = {}
    
    for item in excluded_items:
        exclusion_reason = item.get("exclusion_reason", "unknown")
        result_type = item.get("result_type", "UNKNOWN")
        
        exclusion_breakdown[exclusion_reason] = exclusion_breakdown.get(exclusion_reason, 0) + 1
        result_type_counts[result_type] = result_type_counts.get(result_type, 0) + 1
    
    # Add metadata
    output_data = {
        "context": "ACTIVE_LISTING_CONTEXT_ONLY",
        "status": "TEMPORARY_TEST_OUTPUT",
        "warning": "NOT_SOLD_COMPS - Do not use active listings as sold comps. Do not persist eBay user data.",
        "query": keyword,
        "environment": environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category_detected": category,
        "category_price_floor": category_floor,
        "filters_applied": filters_used,
        "summary_metrics": metrics,
        "full_unit_count": len(full_units),
        "excluded_count": len(excluded_items),
        "exclusion_breakdown": exclusion_breakdown,
        "result_type_counts": result_type_counts,
        "full_units": full_units,
        "excluded_items": excluded_items
    }
    
    # Save JSON
    json_path = output_dir / f"{safe_keyword}_{environment}_{timestamp_str}.json"
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"✓ Saved JSON: {json_path}")
    
    # Save CSV (full units only)
    csv_path = output_dir / f"{safe_keyword}_{environment}_{timestamp_str}.csv"
    if full_units:
        fieldnames = list(full_units[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(full_units)
        print(f"✓ Saved CSV: {csv_path}")
    
    return json_path


def main():
    parser = argparse.ArgumentParser(
        description="eBay Active Market Context - Phase 1 (Improved Filtering)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ebay_active_context.py "McIntosh MA 5100"
  python ebay_active_context.py "McIntosh MA 5100" --max-results 100
  python ebay_active_context.py "McIntosh MA 5100" --price-min 500 --price-max 3000
  python ebay_active_context.py "McIntosh MA 5100" --condition USED

Conditions: NEW, LIKE_NEW, USED, VERY_GOOD, GOOD, ACCEPTABLE, FOR_PARTS_OR_NOT_WORKING
        """
    )
    
    parser.add_argument("keyword", help="Search keyword")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results to fetch (default: 50)")
    parser.add_argument("--price-min", type=float, help="Minimum price filter")
    parser.add_argument("--price-max", type=float, help="Maximum price filter")
    parser.add_argument("--condition", help="Condition filter (NEW, USED, etc.)")
    parser.add_argument("--env", default="production", choices=["production", "sandbox"], help="Environment")
    
    args = parser.parse_args()
    
    # Detect category and price floor
    category, category_floor = detect_category(args.keyword)
    
    print("=" * 80)
    print("eBay Active Market Context - Phase 1 (Improved Filtering)")
    print("ACTIVE_LISTING_CONTEXT_ONLY | TEMPORARY_TEST_OUTPUT | NOT_SOLD_COMPS")
    print("=" * 80)
    print(f"Query: {args.keyword}")
    print(f"Category: {category}")
    print(f"Price Floor: ${category_floor} (minimum for full working unit)")
    print(f"Environment: {args.env.upper()}")
    
    filters_used = {}
    if args.price_min:
        print(f"Price Min: ${args.price_min}")
        filters_used["price_min"] = args.price_min
    if args.price_max:
        print(f"Price Max: ${args.price_max}")
        filters_used["price_max"] = args.price_max
    if args.condition:
        print(f"Condition: {args.condition}")
        filters_used["condition"] = args.condition
    print()
    
    # Load credentials and get token
    creds = load_credentials(args.env)
    marketplace_id = creds.get("marketplace_id", "EBAY_US")
    
    try:
        print("Step 1: Getting OAuth application token...")
        token_response = get_application_token(
            creds['app_id'],
            creds['cert_id'],
            args.env
        )
        access_token = token_response['access_token']
        print("✓ OAuth token acquired")
        print()
        
        # Search items
        print(f"Step 2: Searching active listings (max {args.max_results})...")
        results = search_items(
            access_token, 
            args.keyword, 
            marketplace_id, 
            args.env, 
            limit=args.max_results,
            price_min=args.price_min,
            price_max=args.price_max,
            condition=args.condition
        )
        
        if "itemSummaries" not in results or len(results["itemSummaries"]) == 0:
            print("✗ No items found")
            return
        
        items = results["itemSummaries"]
        print(f"✓ Found {len(items)} total results")
        print()
        
        # Extract and classify
        print("Step 3: Classifying and filtering results...")
        full_units = []
        excluded_items = []
        
        for item in items:
            item_data = extract_item_data(item)
            result_type, should_include, exclusion_reason = classify_result(
                item_data["title"],
                item_data["price_value"],
                item_data["condition"],
                args.keyword,
                category_floor
            )
            
            item_data["result_type"] = result_type
            
            if should_include:
                full_units.append(item_data)
            else:
                item_data["exclusion_reason"] = exclusion_reason
                excluded_items.append(item_data)
        
        print(f"✓ Full working units (EXACT/SIMILAR): {len(full_units)}")
        print(f"✓ Excluded (parts/accessories/wrong model): {len(excluded_items)}")
        print()
        
        # Calculate metrics (full units only)
        print("Step 4: Calculating summary metrics (full units only)...")
        metrics = calculate_metrics(full_units, category_floor)
        
        print(f"Full Unit Count: {metrics['active_listing_count']}")
        if metrics['lowest_active_price']:
            print(f"Price Range: ${metrics['lowest_active_price']:.2f} - ${metrics['highest_active_price']:.2f}")
            print(f"Median Price: ${metrics['median_active_price']:.2f}")
        if metrics['shipping_range']['min'] is not None:
            print(f"Shipping Range: ${metrics['shipping_range']['min']:.2f} - ${metrics['shipping_range']['max']:.2f}")
        
        print(f"\nFilter Status: {metrics['filter_status']}")
        
        if metrics['filter_status'] == "FILTER_FAILURE_REVIEW_NEEDED":
            print(f"⚠️  WARNING: Median price ${metrics['median_active_price']:.2f} is below category floor ${category_floor}")
            print("⚠️  Filter is likely leaking false positives. Review needed.")
        
        print("\nCondition Breakdown:")
        for condition, count in sorted(metrics['condition_counts'].items()):
            print(f"  {condition}: {count}")
        print()
        
        # Display sample full units
        if full_units:
            print("Sample Full Working Units (top 5):")
            print("-" * 80)
            for i, item in enumerate(full_units[:5], 1):
                price_str = f"${item['price_value']:.2f}" if item['price_value'] else "N/A"
                condition_str = item['condition'] or "N/A"
                print(f"{i}. {item['title'][:65]}")
                print(f"   Price: {price_str} | Condition: {condition_str} | Type: {item['result_type']}")
                print()
        
        # Save results
        print("Step 5: Saving temporary test output...")
        output_path = save_results(
            full_units, 
            excluded_items, 
            metrics, 
            args.keyword, 
            args.env, 
            filters_used,
            category,
            category_floor
        )
        
        print()
        print("=" * 80)
        
        if metrics['filter_status'] == "VALID":
            print("✓ FILTER VALIDATION PASSED")
        else:
            print("✗ FILTER VALIDATION FAILED")
            print("  Market context is NOT valid until filter is fixed")
        
        print("=" * 80)
        print("⚠️  ACTIVE_LISTING_CONTEXT_ONLY")
        print("⚠️  TEMPORARY_TEST_OUTPUT")
        print("⚠️  NOT_SOLD_COMPS")
        print()
        print(f"Output: {output_path}")
        
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
