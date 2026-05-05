#!/usr/bin/env python3
"""
VISUAL_BROWSER_TEST_004 - Manual Browser + OS Screen Capture
User manually controls Chrome. Script only captures and analyzes visible screen.

NO Playwright, NO DOM access, NO browser control.
"""

import json
import csv
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw
import mss
import pytesseract

OUTPUT_DIR = Path("screenshots/manual_browser_004")
DATA_DIR = Path("data/manual_browser_004")


def capture_screen(filename):
    """Capture the entire screen using MSS."""
    print(f"📸 Capturing screen...")
    
    try:
        with mss.mss() as sct:
            # Capture primary monitor
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            
            # Save
            filepath = OUTPUT_DIR / filename
            img.save(filepath)
            
            print(f"   ✓ Saved: {filepath.name} ({screenshot.width}x{screenshot.height})")
            return filepath, img
    except Exception as e:
        print(f"   ✗ Screenshot failed: {e}")
        return None, None


def detect_card_regions(img, min_width=200, min_height=150):
    """
    Attempt to detect rectangular regions that might be listing cards.
    This is a simple heuristic - may need tuning per site.
    """
    print(f"   Detecting card regions...")
    
    # Convert to grayscale
    gray = img.convert('L')
    width, height = gray.size
    
    # Simple grid-based approach: divide screen into potential card regions
    # Most marketplaces use grid layouts
    cards = []
    
    # Try to detect cards by looking for roughly equal-sized regions
    # This is a placeholder - real implementation would use edge detection
    
    # For now, create a simple grid assuming cards are in rows/columns
    # Typical layouts: 3-4 cards per row, each ~300-400px wide
    
    card_width = 350
    card_height = 400
    margin = 20
    
    # Skip top 100px (navigation) and bottom 100px (footer)
    start_y = 100
    end_y = height - 100
    
    # Try to fit cards in grid
    x = margin
    y = start_y
    
    while y + card_height < end_y:
        x = margin
        row_cards = []
        
        while x + card_width < width:
            # Define card region
            box = (x, y, x + card_width, y + card_height)
            
            # Crop region
            card_img = img.crop(box)
            
            # Check if region has content (not blank)
            # Simple check: if >10% of pixels are not white/gray
            pixels = list(card_img.getdata())
            non_white = sum(1 for p in pixels if not (p[0] > 240 and p[1] > 240 and p[2] > 240))
            content_ratio = non_white / len(pixels)
            
            if content_ratio > 0.1:  # Has some content
                cards.append({
                    'box': box,
                    'img': card_img,
                    'x': x,
                    'y': y,
                    'width': card_width,
                    'height': card_height
                })
                row_cards.append(box)
            
            x += card_width + margin
        
        y += card_height + margin
        
        # If no cards found in this row, move down more
        if not row_cards:
            y += 100
    
    print(f"   Found {len(cards)} potential card regions")
    return cards


def ocr_card(card_img, psm_modes=[3, 6, 11]):
    """
    Run Tesseract OCR on a card image with multiple PSM modes.
    PSM 3 = Fully automatic page segmentation (default)
    PSM 6 = Assume a single uniform block of text
    PSM 11 = Sparse text. Find as much text as possible
    """
    results = []
    
    for psm in psm_modes:
        try:
            config = f'--psm {psm}'
            text = pytesseract.image_to_string(card_img, config=config)
            results.append({
                'psm': psm,
                'text': text,
                'length': len(text),
                'lines': len([l for l in text.split('\n') if l.strip()])
            })
        except Exception as e:
            results.append({
                'psm': psm,
                'error': str(e)
            })
    
    # Pick best result (most text found)
    best = max(results, key=lambda r: r.get('length', 0))
    return best.get('text', ''), results


def extract_price(text):
    """Extract price patterns from OCR text."""
    # Patterns
    patterns = [
        r'\$\s*\d+[\d,]*\.?\d*',  # $123.45, $1,234
        r'\d+[\d,]*\.?\d*\s*(?:USD|usd|\$)',  # 123 USD, 123$
    ]
    
    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up
            clean = re.sub(r'[^\d.]', '', match)
            if clean:
                try:
                    val = float(clean)
                    if 1 <= val <= 50000:  # Reasonable range
                        prices.append(f"${val:.2f}")
                except:
                    pass
    
    # Return most common or first found
    if prices:
        return prices[0]
    
    # Check for "Free" or "Contact" or similar
    text_lower = text.lower()
    if 'free' in text_lower:
        return 'Free'
    if 'contact' in text_lower or 'call' in text_lower:
        return 'Contact'
    
    return None


def extract_shipping(text):
    """Extract shipping info from OCR text."""
    text_lower = text.lower()
    
    if 'free shipping' in text_lower:
        return 'Free shipping'
    if 'shipping' in text_lower:
        # Try to find cost
        match = re.search(r'shipping[:\s]+\$?(\d+\.?\d*)', text_lower)
        if match:
            return f"${match.group(1)} shipping"
        return 'Shipping available'
    
    return None


def analyze_card(card_data, card_num, screenshot_name):
    """Analyze a single card region with OCR."""
    card_img = card_data['img']
    box = card_data['box']
    
    # Save card crop
    card_filename = f"card_{card_num:03d}.png"
    card_path = OUTPUT_DIR / card_filename
    card_img.save(card_path)
    
    # Run OCR
    text, ocr_results = ocr_card(card_img)
    
    # Extract data
    price = extract_price(text)
    shipping = extract_shipping(text)
    
    # Get title (first non-empty line that's not a price)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    title = None
    for line in lines:
        if len(line) > 10 and '$' not in line[:3]:  # Not just a price
            title = line[:100]  # Truncate
            break
    
    result = {
        'card_number': card_num,
        'screenshot': screenshot_name,
        'card_crop': card_filename,
        'box': box,
        'title': title,
        'price': price,
        'shipping': shipping,
        'ocr_text_length': len(text),
        'ocr_text_lines': len(lines),
        'ocr_text_sample': text[:300] if text else '',
        'status': 'parsed' if (title and price) else 'partial' if (title or price) else 'failed'
    }
    
    return result


def process_screenshot(screenshot_path, screenshot_num, site_name):
    """Process a single screenshot: detect cards, OCR, extract data."""
    print(f"\n📊 Processing screenshot {screenshot_num}...")
    
    img = Image.open(screenshot_path)
    
    # Detect card regions
    cards = detect_card_regions(img)
    
    if not cards:
        print(f"   ⚠️  No card regions detected")
        return [], "CARD_CROP_FAILED"
    
    # Analyze each card
    results = []
    for i, card in enumerate(cards, 1):
        card_num = (screenshot_num - 1) * 20 + i  # Unique number across screenshots
        result = analyze_card(card, card_num, screenshot_path.name)
        results.append(result)
        
        status_icon = "✓" if result['status'] == 'parsed' else "⚠️" if result['status'] == 'partial' else "✗"
        print(f"   {status_icon} Card {i}: {result['status']}")
        if result['title']:
            print(f"      Title: {result['title'][:60]}...")
        if result['price']:
            print(f"      Price: {result['price']}")
    
    # Determine overall status
    parsed_count = sum(1 for r in results if r['status'] == 'parsed')
    if parsed_count > 0:
        status = "SUCCESS"
    elif any(r['status'] == 'partial' for r in results):
        status = "PARTIAL_OCR"
    else:
        status = "OCR_FAILED"
    
    return results, status


def test_site(site_name, search_term, num_screenshots=3):
    """Test a single site with manual browser control."""
    print(f"\n{'='*80}")
    print(f"Testing: {site_name}")
    print(f"Search Term: {search_term}")
    print(f"{'='*80}\n")
    
    site_results = {
        'site': site_name,
        'search_term': search_term,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'screenshots': [],
        'cards_detected': 0,
        'cards_parsed': 0,
        'listings': [],
        'status': None,
        'error': None
    }
    
    print("📋 Instructions:")
    print(f"1. Open Chrome and go to {site_name}")
    print(f"2. Log in if needed")
    print(f"3. Search for: {search_term}")
    print(f"4. Position the browser window to show search results")
    print()
    
    input("Press Enter when ready for screenshot 1...")
    
    for i in range(1, num_screenshots + 1):
        print(f"\n--- Screenshot {i}/{num_screenshots} ---")
        
        # Capture screen
        filename = f"{site_name.lower().replace(' ', '_')}_screen_{i:02d}.png"
        filepath, img = capture_screen(filename)
        
        if not filepath:
            site_results['status'] = "SCREENSHOT_FAILED"
            site_results['error'] = "Could not capture screen"
            return site_results
        
        site_results['screenshots'].append(str(filepath))
        
        # Process screenshot
        cards, status = process_screenshot(filepath, i, site_name)
        
        site_results['cards_detected'] += len(cards)
        site_results['cards_parsed'] += sum(1 for c in cards if c['status'] == 'parsed')
        site_results['listings'].extend(cards)
        
        # Prompt for next screenshot
        if i < num_screenshots:
            print()
            response = input(f"Scroll down and press Enter for screenshot {i+1}, or 'q' to stop: ")
            if response.lower() == 'q':
                print("Stopping early per user request")
                break
            time.sleep(1)  # Brief pause
    
    # Determine overall status
    if site_results['cards_parsed'] >= 5:
        site_results['status'] = "SUCCESS"
    elif site_results['cards_parsed'] > 0:
        site_results['status'] = "PARTIAL_SUCCESS"
    elif site_results['cards_detected'] > 0:
        site_results['status'] = "OCR_FAILED"
    elif site_results['screenshots']:
        site_results['status'] = "CARD_CROP_FAILED"
    else:
        site_results['status'] = "SCREENSHOT_FAILED"
    
    return site_results


def generate_verdict(site_results):
    """Generate KEEP/DROP verdict based on results."""
    status = site_results['status']
    parsed = site_results['cards_parsed']
    detected = site_results['cards_detected']
    
    if status == "SUCCESS" and parsed >= 5:
        return "KEEP", "Successfully parsed multiple listings with title + price"
    elif status == "PARTIAL_SUCCESS" and parsed > 0:
        return "MAYBE", f"Parsed {parsed} cards but may need better cropping/OCR"
    elif status == "OCR_FAILED" and detected > 0:
        return "DROP", f"Detected {detected} cards but OCR failed to extract data"
    elif status == "CARD_CROP_FAILED":
        return "DROP", "Could not detect listing cards in screenshots"
    elif status == "SCREENSHOT_FAILED":
        return "DROP", "Screenshot capture failed"
    else:
        return "DROP", "Unknown error"


def main():
    print("="*80)
    print("VISUAL_BROWSER_TEST_004 - Manual Browser + OS Screen Capture")
    print("="*80)
    print()
    print("⚠️  VISUAL_CONTEXT_ONLY")
    print("⚠️  NEEDS_MANUAL_REVIEW")
    print()
    print("You control the browser. I only capture and analyze your screen.")
    print()
    
    # Create output dirs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test sites
    tests = [
        ("Facebook Marketplace", "vintage stereo"),
        ("Mercari", "vintage receiver"),
        ("Google Shopping", "Pioneer SX-1050"),
        ("Craigslist", "vintage stereo"),
    ]
    
    all_results = []
    verdicts = {}
    
    for site_name, search_term in tests:
        result = test_site(site_name, search_term, num_screenshots=3)
        all_results.append(result)
        
        verdict, reason = generate_verdict(result)
        verdicts[site_name] = {"verdict": verdict, "reason": reason}
        
        # Save individual site results
        site_file = DATA_DIR / f"{site_name.lower().replace(' ', '_')}_results.json"
        with open(site_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Saved: {site_file}")
    
    # Generate summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    for site_name, verdict_data in verdicts.items():
        verdict = verdict_data['verdict']
        reason = verdict_data['reason']
        
        symbol = "✓" if verdict == "KEEP" else "⚠️" if verdict == "MAYBE" else "✗"
        print(f"{symbol} {site_name}: {verdict}")
        print(f"   {reason}")
        
        # Find site results
        site_result = next((r for r in all_results if r['site'] == site_name), None)
        if site_result:
            print(f"   Screenshots: {len(site_result['screenshots'])}")
            print(f"   Cards detected: {site_result['cards_detected']}")
            print(f"   Cards parsed: {site_result['cards_parsed']}")
        print()
    
    # Save summary
    summary = {
        "test": "VISUAL_BROWSER_TEST_004",
        "date": datetime.now(timezone.utc).isoformat(),
        "method": "Manual browser control + OS screen capture + OCR",
        "sites_tested": len(tests),
        "verdicts": verdicts,
        "detailed_results": all_results
    }
    
    summary_file = DATA_DIR / "test_004_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Summary saved: {summary_file}")
    
    # Generate CSV of parsed listings
    all_listings = []
    for result in all_results:
        for listing in result['listings']:
            if listing['status'] in ['parsed', 'partial']:
                all_listings.append({
                    'site': result['site'],
                    'title': listing['title'],
                    'price': listing['price'],
                    'shipping': listing['shipping'],
                    'screenshot': listing['screenshot'],
                    'card_crop': listing['card_crop'],
                    'status': listing['status']
                })
    
    if all_listings:
        csv_file = DATA_DIR / "parsed_listings.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_listings[0].keys())
            writer.writeheader()
            writer.writerows(all_listings)
        print(f"✓ Parsed listings saved: {csv_file}")
        print(f"   Total listings extracted: {len(all_listings)}")
    
    print(f"\n{'='*80}")
    print("Test complete")
    print(f"{'='*80}")
    
    return verdicts, all_results


if __name__ == "__main__":
    main()
