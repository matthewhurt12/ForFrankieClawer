#!/usr/bin/env python3
"""
Visual Browser Test - Test marketplace scraping via visible browser
"""

import asyncio
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Test sites and searches
TESTS = [
    {
        "site": "Mercari",
        "url": "https://www.mercari.com/search/?keyword=vintage+receiver",
        "search_term": "vintage receiver"
    },
    {
        "site": "Google Shopping",
        "url": "https://www.google.com/search?q=Pioneer+SX-1050&tbm=shop",
        "search_term": "Pioneer SX-1050"
    },
    {
        "site": "Craigslist",
        "url": "https://athens.craigslist.org/search/sss?query=vintage+stereo",
        "search_term": "vintage stereo"
    }
]

OUTPUT_DIR = Path("screenshots/browser_test_001")
DATA_DIR = Path("data/browser_test_001")


async def test_site(browser, test_config):
    """Test a single site."""
    site_name = test_config["site"]
    url = test_config["url"]
    search_term = test_config["search_term"]
    
    print(f"\n{'='*80}")
    print(f"Testing: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*80}\n")
    
    results = {
        "site": site_name,
        "url": url,
        "search_term": search_term,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": None,
        "error": None,
        "screenshots": [],
        "items_found": [],
        "notes": []
    }
    
    try:
        # Create new page
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"1. Navigating to {url}...")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)  # Let page settle
        
        # Take initial screenshot
        screenshot_path = OUTPUT_DIR / f"{site_name.lower().replace(' ', '_')}_01_initial.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)
        results["screenshots"].append(str(screenshot_path))
        print(f"   ✓ Screenshot saved: {screenshot_path}")
        
        # Check for login/CAPTCHA walls
        page_text = await page.inner_text("body")
        
        if "sign in" in page_text.lower() and "continue" in page_text.lower():
            results["status"] = "login_required"
            results["notes"].append("Login wall detected - cannot proceed")
            print("   ⚠️  Login wall detected")
            await page.close()
            return results
        
        if "captcha" in page_text.lower() or "unusual traffic" in page_text.lower():
            results["status"] = "captcha"
            results["notes"].append("CAPTCHA detected - cannot proceed")
            print("   ⚠️  CAPTCHA detected")
            await page.close()
            return results
        
        # Try to parse results (site-specific selectors)
        print(f"2. Attempting to parse results...")
        
        items = []
        
        if site_name == "Mercari":
            # Mercari uses React - try common selectors
            item_selectors = [
                '[data-testid="ItemCard"]',
                '[data-testid="SearchItem"]',
                '.sc-eCImPb',
                'div[class*="Item"]',
            ]
            
            for selector in item_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"   Found {len(elements)} items with selector: {selector}")
                        for i, elem in enumerate(elements[:10]):  # First 10 only
                            try:
                                text = await elem.inner_text()
                                items.append({
                                    "selector": selector,
                                    "index": i,
                                    "text": text[:200]  # Truncate
                                })
                            except:
                                pass
                        break
                except:
                    continue
        
        elif site_name == "Google Shopping":
            # Google Shopping product cards
            item_selectors = [
                'div.sh-dgr__content',
                'div[data-docid]',
                '.sh-dlr__list-result',
            ]
            
            for selector in item_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"   Found {len(elements)} items with selector: {selector}")
                        for i, elem in enumerate(elements[:10]):
                            try:
                                text = await elem.inner_text()
                                items.append({
                                    "selector": selector,
                                    "index": i,
                                    "text": text[:200]
                                })
                            except:
                                pass
                        break
                except:
                    continue
        
        elif site_name == "Craigslist":
            # Craigslist - check if JavaScript-only
            if "loading" in page_text.lower() and len(page_text) < 500:
                results["status"] = "javascript_only"
                results["notes"].append("Craigslist requires JavaScript - page is placeholder")
                print("   ⚠️  JavaScript-only page (loading placeholder)")
            else:
                # Try to find result items
                item_selectors = [
                    'li.cl-search-result',
                    'li.result-row',
                    'div.result',
                ]
                
                for selector in item_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"   Found {len(elements)} items with selector: {selector}")
                            for i, elem in enumerate(elements[:10]):
                                try:
                                    text = await elem.inner_text()
                                    items.append({
                                        "selector": selector,
                                        "index": i,
                                        "text": text[:200]
                                    })
                                except:
                                    pass
                            break
                    except:
                        continue
        
        results["items_found"] = items
        
        if items:
            print(f"   ✓ Successfully parsed {len(items)} items")
            results["status"] = "success"
        else:
            print(f"   ⚠️  No items parsed (selectors may need updating)")
            results["status"] = "no_items"
            results["notes"].append("Could not find items with known selectors")
        
        # Scroll and take more screenshots
        print(f"3. Scrolling through results...")
        for scroll_num in range(1, 3):  # 2 scrolls
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(2)
            
            screenshot_path = OUTPUT_DIR / f"{site_name.lower().replace(' ', '_')}_0{scroll_num + 1}_scroll.png"
            await page.screenshot(path=str(screenshot_path), full_page=False)
            results["screenshots"].append(str(screenshot_path))
            print(f"   ✓ Screenshot {scroll_num + 1} saved")
        
        await page.close()
        
    except asyncio.TimeoutError:
        results["status"] = "timeout"
        results["error"] = "Page load timeout"
        print(f"   ✗ Timeout loading page")
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"   ✗ Error: {e}")
    
    return results


async def main():
    print("="*80)
    print("VISUAL BROWSER TEST 001")
    print("="*80)
    print()
    print("Testing visual browser scraping on marketplace sites")
    print()
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    all_results = []
    
    async with async_playwright() as p:
        # Launch visible browser
        print("Launching visible Chrome browser...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000,  # Slow down for visibility
            args=['--start-maximized']
        )
        
        print("✓ Browser launched\n")
        
        # Test each site
        for test_config in TESTS:
            result = await test_site(browser, test_config)
            all_results.append(result)
            await asyncio.sleep(2)  # Pause between sites
        
        print("\n" + "="*80)
        print("Closing browser...")
        await browser.close()
    
    # Save results
    json_path = DATA_DIR / "visual_test_results.json"
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"✓ Results saved: {json_path}")
    
    # Create CSV summary
    csv_path = DATA_DIR / "visual_test_summary.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "status", "items_parsed", "screenshots", "notes"])
        writer.writeheader()
        
        for result in all_results:
            writer.writerow({
                "site": result["site"],
                "status": result["status"],
                "items_parsed": len(result["items_found"]),
                "screenshots": len(result["screenshots"]),
                "notes": " | ".join(result["notes"]) if result["notes"] else ""
            })
    
    print(f"✓ Summary saved: {csv_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print()
    
    for result in all_results:
        print(f"{result['site']}:")
        print(f"  Status: {result['status']}")
        print(f"  Items Parsed: {len(result['items_found'])}")
        print(f"  Screenshots: {len(result['screenshots'])}")
        if result['notes']:
            print(f"  Notes: {', '.join(result['notes'])}")
        print()
    
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
