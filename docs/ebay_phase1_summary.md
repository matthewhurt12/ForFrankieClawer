# eBay API Phase 1 - Active Market Context

**Status:** Complete  
**Environment:** Production API enabled  
**Compliance:** Marketplace Account Deletion notifications exemption granted

## What Was Built

### 1. Authentication & Credentials
- **Sandbox credentials:** `credentials/ebay-sandbox.json`
- **Production credentials:** `credentials/ebay-production.json`
- OAuth client credentials flow (application access tokens)
- 2-hour token expiry, auto-refresh on each run

### 2. Core Scripts

#### `ebay_token_test.py`
Simple OAuth token test. Prints only:
- Token received status
- Expires in (seconds/hours)
- Token type

**Never prints:** Client secrets or full access tokens

#### `ebay_production_smoke_test.py`
Quick production API connectivity test:
- Searches for "McIntosh MA 5100"
- Returns top 5 results
- Saves to timestamped JSON/CSV
- Marks output as TEMPORARY_TEST_OUTPUT

#### `ebay_active_context.py` ⭐ Main Tool
Advanced active listing search with filtering and metrics.

**Input:**
```bash
python ebay_active_context.py "McIntosh MA 5100" [options]
  --max-results 50         # Default: 50
  --price-min 500          # Minimum price filter
  --price-max 3000         # Maximum price filter
  --condition USED         # NEW, USED, LIKE_NEW, etc.
  --env production         # production or sandbox
```

**Features:**
- False-positive filtering (parts, accessories, manuals, LED kits, etc.)
- Summary metrics calculation
- Timestamped output
- Proper compliance warnings

**Output Fields:**
- `item_id` - eBay item identifier
- `title` - Listing title
- `price_value` - Price (numeric)
- `price_currency` - Usually USD
- `shipping_cost` - Shipping cost
- `condition` - NEW, USED, etc.
- `buying_options` - FIXED_PRICE, BEST_OFFER, AUCTION
- `item_web_url` - Direct eBay listing URL
- `image_url` - Primary image URL

**Summary Metrics:**
- `active_listing_count` - Number of real listings (after filtering)
- `lowest_active_price` - Minimum price
- `median_active_price` - Median price
- `highest_active_price` - Maximum price
- `shipping_range` - Min/max shipping costs
- `condition_counts` - Breakdown by condition
- `accessory_false_positive_count` - Number of filtered items
- `false_positive_reasons` - Breakdown of why items were filtered

#### `ebay_cleanup_temp.py`
Auto-cleanup for temporary test output.

**Usage:**
```bash
# Dry run (show what would be deleted)
python ebay_cleanup_temp.py --dry-run

# Delete files older than 7 days
python ebay_cleanup_temp.py --max-age 7

# Delete files older than 3 days
python ebay_cleanup_temp.py --max-age 3
```

**Purpose:** Maintains compliance with "we do not persist eBay data" statement by auto-cleaning old test files.

### 3. False Positive Filtering

Automatically excludes:
- LED kits, bulbs, lamps
- Manuals, brochures, service manuals
- Faceplates, glass, knobs
- Parts only, for parts
- Capacitors, rebuild kits, recap kits
- Stickers, decals
- Cabinet only, case only
- Power cords, cables
- Instructions
- Remote controls
- Upgrade kits
- Replacement parts

**Test Results:**
- Search: "McIntosh MA 5100" (30 results)
- Real listings: 11
- False positives: 19 (LED lamps, manuals, rebuild kits, faceplates, capacitors, parts)
- Accuracy: Excellent (manual spot-check confirmed)

### 4. Compliance & Warnings

All output files include:
```
"context": "ACTIVE_LISTING_CONTEXT_ONLY"
"status": "TEMPORARY_TEST_OUTPUT"
"warning": "NOT_SOLD_COMPS - Do not use active listings as sold comps. Do not persist eBay user data."
```

**What We DO NOT Store:**
- Seller usernames
- Seller account data
- Buyer information
- Messages
- Orders
- Personal account details
- Long-term production archives

**What We DO Store (Temporarily):**
- Item title
- Price
- Shipping cost
- Condition
- Item URL
- Image URL
- Item ID
- Buying options

**Retention:** 7 days (auto-cleanup via `ebay_cleanup_temp.py`)

## Example Output

```json
{
  "context": "ACTIVE_LISTING_CONTEXT_ONLY",
  "status": "TEMPORARY_TEST_OUTPUT",
  "summary_metrics": {
    "active_listing_count": 11,
    "lowest_active_price": 9.99,
    "median_active_price": 145.0,
    "highest_active_price": 1999.99,
    "shipping_range": {
      "min": 0.0,
      "max": 125.0
    },
    "condition_counts": {
      "Used": 9,
      "New": 2
    }
  },
  "accessory_false_positive_count": 19,
  "false_positive_reasons": {
    "faceplate": 1,
    "rebuild kit": 2,
    "manual": 5,
    "capacitor": 3,
    "parts_condition": 2,
    "led lamp": 4,
    "lamp kit": 1,
    "power cord": 1
  },
  "real_listings": [...]
}
```

## Output Location

All temporary test files saved to:
```
data/ebay_active_search/
  mcintosh_ma_5100_production_YYYYMMDD_HHMMSS.json
  mcintosh_ma_5100_production_YYYYMMDD_HHMMSS.csv
```

## Next Steps (Not Built Yet)

Phase 1 is complete. Future phases might include:
- Sold item analysis (requires different API endpoints)
- Price trend tracking
- Automated scheduled searches
- Webhook notifications for new listings

**Important:** Any future work must maintain compliance with the exemption statement and avoid persisting eBay user data.

## Quick Start

```bash
# Test OAuth token
python ebay_token_test.py

# Production smoke test
python ebay_production_smoke_test.py

# Advanced search with filtering
python ebay_active_context.py "McIntosh MA 5100" --max-results 50

# With price filters
python ebay_active_context.py "McIntosh MA 5100" --price-min 500 --price-max 3000

# Cleanup old files (dry run)
python ebay_cleanup_temp.py --dry-run

# Cleanup old files (live)
python ebay_cleanup_temp.py --max-age 7
```

## Files Created

```
credentials/
  ebay-sandbox.json          # Sandbox API credentials (600 permissions)
  ebay-production.json       # Production API credentials (600 permissions)

ebay_token_test.py           # OAuth token test
ebay_production_smoke_test.py # Quick production test
ebay_active_context.py       # Main active listing search tool ⭐
ebay_cleanup_temp.py         # Auto-cleanup for old files

data/ebay_active_search/     # Temporary output directory
  *.json                     # JSON results (timestamped)
  *.csv                      # CSV results (timestamped)

docs/
  ebay_phase1_summary.md     # This file
```
