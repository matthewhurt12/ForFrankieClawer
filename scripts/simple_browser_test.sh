#!/bin/bash
# Simple visual browser test using basic tools

SCREENSHOT_DIR="screenshots/browser_test_001"
DATA_DIR="data/browser_test_001"

mkdir -p "$SCREENSHOT_DIR" "$DATA_DIR"

echo "========================================"
echo "VISUAL BROWSER TEST 001 - Simple Version"
echo "========================================"
echo ""

# Test function
test_site() {
    local site_name="$1"
    local url="$2"
    local output_file="$3"
    
    echo "Testing: $site_name"
    echo "URL: $url"
    echo "----------------------------------------"
    
    # Fetch page
    curl -A "Mozilla/5.0" -s "$url" > "$output_file"
    local size=$(wc -c < "$output_file")
    
    echo "  Response size: $size bytes"
    
    # Check for common patterns
    if grep -qi "sign in\|log in\|login" "$output_file"; then
        echo "  ⚠️  Login wall detected"
    fi
    
    if grep -qi "captcha\|unusual traffic" "$output_file"; then
        echo "  ⚠️  CAPTCHA detected"
    fi
    
    if grep -qi "loading\|reading\|writing" "$output_file" && [ $size -lt 10000 ]; then
        echo "  ⚠️  JavaScript-only page (placeholder)"
    fi
    
    # Try to find price patterns
    local price_count=$(grep -oE '\$[0-9,]+' "$output_file" | wc -l)
    echo "  Prices found: $price_count"
    
    echo ""
}

# Test Mercari
test_site "Mercari" \
    "https://www.mercari.com/search/?keyword=vintage+receiver" \
    "$DATA_DIR/mercari.html"

# Test Google Shopping
test_site "Google Shopping" \
    "https://www.google.com/search?q=Pioneer+SX-1050&tbm=shop" \
    "$DATA_DIR/google_shopping.html"

# Test Craigslist
test_site "Craigslist Athens" \
    "https://athens.craigslist.org/search/sss?query=vintage+stereo" \
    "$DATA_DIR/craigslist.html"

# Test eBay (bonus)
test_site "eBay" \
    "https://www.ebay.com/sch/i.html?_nkw=vintage+receiver" \
    "$DATA_DIR/ebay.html"

echo "========================================"
echo "Test complete"
echo "HTML files saved to: $DATA_DIR"
echo "========================================"
