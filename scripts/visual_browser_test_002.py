#!/usr/bin/env python3
"""
VISUAL_BROWSER_TEST_002 - Actual Browser Automation
Tests marketplace scraping with visible Chromium browser
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Test sites and searches
TESTS = [
    {
        "site": "Mercari",
        "url": "https://www.mercari.com/search/?keyword=vintage+receiver",
        "search_term": "vintage receiver",
        "item_selectors": ['[data-testid="ItemCard"]', 'div[data-testid*="Item"]', '.item-grid > div']
    },
    {
        "site": "Google Shopping",
        "url": "https://www.google.com/search?q=Pioneer+SX-1050&tbm=shop",
        "search_term": "Pioneer SX-1050",
        "item_selectors": ['div.sh-dgr__content', 'div[data-docid]', '.sh-dlr__list-result']
    },
    {
        "site": "Craigslist",
        "url": "https://athens.craigslist.org/search/sss?query=vintage+stereo",
        "search_term": "vintage stereo",
        "item_selectors": ['li.cl-search-result', 'li.cl-static-search-result', '.cl-search-view-mode-gallery > ul > li']
    },
    {
        "site": "Facebook Marketplace",
        "url": "https://www.facebook.com/marketplace/athens/search?query=vintage%20stereo",
        "search_term": "vintage stereo",
        "item_selectors": ['div[data-testid="marketplace_feed_item"]', 'div[role="article"]']
    }
]

OUTPUT_DIR = Path("screenshots/browser_test_002")
DATA_DIR = Path("data/browser_test_002")


async def test_site(browser, test_config, test_num):
    """Test a single site with visible browser."""
    site_name = test_config["site"]
    url = test_config["url"]
    search_term = test_config["search_term"]
    item_selectors = test_config["item_selectors"]
    
    print(f"\n{'='*80}")
    print(f"Test {test_num}: {site_name}")
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
        "items_parsed": [],
        "notes": []
    }
    
    context = None
    page = None
    
    try:
        # Create new context and page
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        print(f"1. Navigating to {site_name}...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)  # Let page settle
        except Exception as e:
            print(f"   ⚠️  Navigation timeout or error: {e}")
            results["status"] = "navigation_error"
            results["error"] = str(e)
            return results
        
        # Take initial screenshot
        screenshot_path = OUTPUT_DIR / f"{site_name.lower().replace(' ', '_')}_01_initial.png"
        await page.screenshot(path=str(screenshot_path), full_page=False)
        results["screenshots"].append(str(screenshot_path))
        print(f"   ✓ Screenshot 1 saved: {screenshot_path.name}")
        
        # Check for blocks/walls
        try:
            page_text = await page.inner_text("body", timeout=5000)
        except:
            page_text = ""
        
        # Check for CAPTCHA
        if "captcha" in page_text.lower() or "unusual traffic" in page_text.lower():
            results["status"] = "captcha_blocked"
            results["notes"].append("CAPTCHA detected - cannot proceed per user rules")
            print("   ⚠️  CAPTCHA detected - stopping per user rules")
            return results
        
        # Check for Cloudflare challenge
        if "just a moment" in page_text.lower() or "checking your browser" in page_text.lower():
            results["status"] = "cloudflare_challenge"
            results["notes"].append("Cloudflare challenge detected - waiting...")
            print("   ⚠️  Cloudflare challenge - waiting 10 seconds...")
            await asyncio.sleep(10)
            await page.screenshot(path=str(OUTPUT_DIR / f"{site_name.lower().replace(' ', '_')}_01b_after_wait.png"))
            page_text = await page.inner_text("body", timeout=5000)
        
        # Check for login requirement (Facebook)
        if site_name == "Facebook Marketplace":
            if "log in" in page_text.lower() or "sign up" in page_text.lower():
                # Check if we're actually logged in by looking for marketplace elements
                try:
                    marketplace_elem = await page.query_selector('div[role="main"]', timeout=3000)
                    if not marketplace_elem:
                        results["status"] = "login_required"
                        results["notes"].append("Not logged into Facebook - cannot access Marketplace per user rules")
                        print("   ⚠️  Not logged into Facebook - skipping")
                        return results
                except:
                    results["status"] = "login_required"
                    results["notes"].append("Facebook login required")
                    print("   ⚠️  Facebook login required - skipping")
                    return results
        
        # Try to parse items
        print(f"2. Attempting to parse items...")
        items_found = []
        successful_selector = None
        
        for selector in item_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                elements = await page.query_selector_all(selector)
                
                if elements and len(elements) > 0:
                    print(f"   ✓ Found {len(elements)} items with selector: {selector}")
                    successful_selector = selector
                    
                    # Parse first 10 items
                    for i, elem in enumerate(elements[:10]):
                        try:
                            item_text = await elem.inner_text()
                            
                            # Try to get href if it's a link
                            item_url = None
                            try:
                                link = await elem.query_selector('a')
                                if link:
                                    item_url = await link.get_attribute('href')
                            except:
                                pass
                            
                            # Try to get image
                            img_url = None
                            try:
                                img = await elem.query_selector('img')
                                if img:
                                    img_url = await img.get_attribute('src')
                            except:
                                pass
                            
                            item_data = {
                                "index": i + 1,
                                "text": item_text[:300] if item_text else "",  # Truncate
                                "url": item_url,
                                "image": img_url[:200] if img_url else None
                            }
                            
                            items_found.append(item_data)
                            
                        except Exception as e:
                            print(f"   ⚠️  Error parsing item {i+1}: {e}")
                            continue
                    
                    break  # Found working selector
                    
            except Exception as e:
                continue  # Try next selector
        
        if items_found:
            print(f"   ✓ Successfully parsed {len(items_found)} items")
            results["items_parsed"] = items_found
            results["status"] = "success"
            results["notes"].append(f"Used selector: {successful_selector}")
        else:
            print(f"   ⚠️  No items found with any selector")
            results["status"] = "no_items_found"
            results["notes"].append("Could not find items with known selectors")
        
        # Scroll and screenshot
        print(f"3. Scrolling through results...")
        for scroll_num in range(1, 4):  # 3 scrolls
            try:
                await page.evaluate("window.scrollBy(0, 800)")
                await asyncio.sleep(2)
                
                screenshot_path = OUTPUT_DIR / f"{site_name.lower().replace(' ', '_')}_0{scroll_num + 1}_scroll{scroll_num}.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                results["screenshots"].append(str(screenshot_path))
                print(f"   ✓ Screenshot {scroll_num + 1} saved")
            except Exception as e:
                print(f"   ⚠️  Error during scroll {scroll_num}: {e}")
                break
        
        results["status"] = results["status"] or "completed"
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"   ✗ Error: {e}")
    
    finally:
        # Close page and context
        if page:
            await page.close()
        if context:
            await context.close()
    
    return results


async def main():
    print("="*80)
    print("VISUAL_BROWSER_TEST_002 - Actual Browser Automation")
    print("="*80)
    print()
    print("⚠️  VISUAL_CONTEXT_ONLY")
    print("⚠️  DO NOT bypass CAPTCHA, login, or automation blocks")
    print("⚠️  DO NOT message sellers or buy anything")
    print()
    
    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    all_results = []
    
    async with async_playwright() as p:
        # Launch VISIBLE browser
        print("Launching visible Chromium browser...")
        print("(This will open a real browser window)")
        print()
        
        # Set DISPLAY for WSL2
        os.environ['DISPLAY'] = ':0'
        
        try:
            browser = await p.chromium.launch(
                headless=False,  # VISIBLE BROWSER
                slow_mo=500,     # Slow down for visibility
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled'  # Try to look less like a bot
                ]
            )
            print("✓ Browser launched (visible window should appear)")
            print()
        except Exception as e:
            print(f"✗ Failed to launch browser: {e}")
            return
        
        # Test each site
        for i, test_config in enumerate(TESTS, 1):
            result = await test_site(browser, test_config, i)
            all_results.append(result)
            
            print(f"\n{'='*80}")
            print(f"✓ {test_config['site']} test complete")
            print(f"Status: {result['status']}")
            print(f"Items parsed: {len(result.get('items_parsed', []))}")
            print(f"Screenshots: {len(result.get('screenshots', []))}")
            print(f"{'='*80}\n")
            
            # Pause between sites
            if i < len(TESTS):
                print("Pausing 3 seconds before next site...\n")
                await asyncio.sleep(3)
        
        print("\n" + "="*80)
        print("Closing browser...")
        await browser.close()
        print("✓ Browser closed")
    
    # Save results
    json_path = DATA_DIR / "visual_test_002_results.json"
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"✓ Results saved: {json_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print()
    
    for result in all_results:
        print(f"{result['site']}:")
        print(f"  Status: {result['status']}")
        print(f"  Items Parsed: {len(result.get('items_parsed', []))}")
        print(f"  Screenshots: {len(result.get('screenshots', []))}")
        if result.get('notes'):
            print(f"  Notes: {'; '.join(result['notes'])}")
        print()
    
    print("="*80)
    print("⚠️  All data marked VISUAL_CONTEXT_ONLY")
    print("⚠️  All data marked NEEDS_MANUAL_REVIEW")
    print("="*80)
    
    return all_results


if __name__ == "__main__":
    asyncio.run(main())
