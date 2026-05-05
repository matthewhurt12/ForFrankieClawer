#!/usr/bin/env python3
"""
VISUAL_BROWSER_TEST_003 - Screen Capture + OCR Analysis
Analyzes existing screenshots from VISUAL_BROWSER_TEST_002 using OCR
No Playwright, no DOM access, just visual analysis
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import pytesseract

# Screenshots from previous test
SCREENSHOT_DIR = Path("screenshots/browser_test_002")
OUTPUT_DIR = Path("data/visual_ocr_003")
REPORT_DIR = Path("reports")


def extract_price_patterns(text):
    """Extract price patterns from OCR text."""
    # Common price patterns
    patterns = [
        r'\$\s*\d+[\d,]*\.?\d*',  # $123.45, $1,234
        r'\d+[\d,]*\.?\d*\s*(?:USD|usd)',  # 123 USD
    ]
    
    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up the price
            clean_price = re.sub(r'[^\d.]', '', match)
            if clean_price:
                try:
                    price_val = float(clean_price)
                    if 10 <= price_val <= 50000:  # Reasonable range
                        prices.append(f"${price_val:.2f}")
                except:
                    pass
    
    return list(set(prices))  # Unique prices


def analyze_screenshot(image_path):
    """Run OCR on a screenshot and extract text."""
    print(f"\nAnalyzing: {image_path.name}")
    
    try:
        # Open image
        img = Image.open(image_path)
        width, height = img.size
        print(f"  Image size: {width}x{height}")
        
        # Run OCR
        print(f"  Running OCR...")
        text = pytesseract.image_to_string(img)
        
        # Extract prices
        prices = extract_price_patterns(text)
        
        # Count lines (rough estimate of content)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Look for common marketplace indicators
        marketplace_indicators = {
            'mercari': text.lower().count('mercari'),
            'google': text.lower().count('google') or text.lower().count('shopping'),
            'craigslist': text.lower().count('craigslist'),
            'facebook': text.lower().count('facebook') or text.lower().count('marketplace'),
            'ebay': text.lower().count('ebay'),
        }
        
        detected_marketplace = max(marketplace_indicators, key=marketplace_indicators.get)
        
        result = {
            "screenshot": str(image_path),
            "filename": image_path.name,
            "image_size": f"{width}x{height}",
            "text_lines": len(lines),
            "total_chars": len(text),
            "prices_found": prices,
            "price_count": len(prices),
            "detected_marketplace": detected_marketplace if marketplace_indicators[detected_marketplace] > 0 else "unknown",
            "text_sample": text[:500] if text else "",  # First 500 chars
            "full_text_available": True
        }
        
        print(f"  ✓ OCR complete")
        print(f"    Lines: {len(lines)}")
        print(f"    Prices found: {len(prices)}")
        if prices:
            print(f"    Sample prices: {prices[:5]}")
        print(f"    Marketplace: {result['detected_marketplace']}")
        
        return result, text
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {
            "screenshot": str(image_path),
            "filename": image_path.name,
            "error": str(e)
        }, ""


def analyze_site_screenshots(site_pattern):
    """Analyze all screenshots for a specific site."""
    screenshots = sorted(SCREENSHOT_DIR.glob(f"{site_pattern}*.png"))
    
    if not screenshots:
        return [], []
    
    print(f"\n{'='*80}")
    print(f"Analyzing {site_pattern.upper()} screenshots ({len(screenshots)} files)")
    print(f"{'='*80}")
    
    results = []
    all_text = []
    
    for screenshot in screenshots:
        result, text = analyze_screenshot(screenshot)
        results.append(result)
        all_text.append(text)
    
    # Aggregate analysis
    total_prices = sum(r.get('price_count', 0) for r in results)
    avg_lines = sum(r.get('text_lines', 0) for r in results) / len(results) if results else 0
    
    print(f"\n{site_pattern.upper()} Summary:")
    print(f"  Total screenshots: {len(screenshots)}")
    print(f"  Total prices detected: {total_prices}")
    print(f"  Avg text lines per screenshot: {avg_lines:.1f}")
    
    return results, all_text


def generate_verdict(site_name, results):
    """Generate KEEP/DROP verdict for a site."""
    if not results:
        return "DROP", "No screenshots available"
    
    total_prices = sum(r.get('price_count', 0) for r in results)
    avg_lines = sum(r.get('text_lines', 0) for r in results) / len(results)
    avg_chars = sum(r.get('total_chars', 0) for r in results) / len(results)
    
    # Decision criteria
    reasons = []
    
    if total_prices == 0:
        reasons.append("No prices detected in OCR")
    
    if avg_lines < 10:
        reasons.append(f"Very low text content (avg {avg_lines:.0f} lines)")
    
    if avg_chars < 500:
        reasons.append(f"Minimal text extracted (avg {avg_chars:.0f} chars)")
    
    # Verdict
    if total_prices >= 3 and avg_lines >= 20:
        return "KEEP", "Prices and content detected - OCR viable"
    elif total_prices >= 1:
        return "MAYBE", "Some prices detected but low confidence"
    else:
        return "DROP", " | ".join(reasons)


def main():
    print("="*80)
    print("VISUAL_BROWSER_TEST_003 - Screen Capture + OCR Analysis")
    print("="*80)
    print()
    print("⚠️  VISUAL_CONTEXT_ONLY")
    print("⚠️  NEEDS_MANUAL_REVIEW")
    print()
    print("Analyzing existing screenshots from VISUAL_BROWSER_TEST_002")
    print()
    
    # Create output dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test sites
    sites = [
        ("mercari", "Mercari"),
        ("google_shopping", "Google Shopping"),
        ("craigslist", "Craigslist"),
        ("facebook_marketplace", "Facebook Marketplace"),
    ]
    
    all_site_results = {}
    verdicts = {}
    
    for pattern, site_name in sites:
        results, texts = analyze_site_screenshots(pattern)
        all_site_results[site_name] = results
        
        # Generate verdict
        verdict, reason = generate_verdict(site_name, results)
        verdicts[site_name] = {"verdict": verdict, "reason": reason}
        
        # Save individual site results
        if results:
            site_json = OUTPUT_DIR / f"{pattern}_ocr_results.json"
            with open(site_json, "w") as f:
                json.dump(results, f, indent=2)
            print(f"  ✓ Saved: {site_json}")
            
            # Save full text for manual review
            if texts:
                text_file = OUTPUT_DIR / f"{pattern}_full_text.txt"
                with open(text_file, "w") as f:
                    for i, text in enumerate(texts, 1):
                        f.write(f"{'='*80}\n")
                        f.write(f"Screenshot {i}\n")
                        f.write(f"{'='*80}\n")
                        f.write(text)
                        f.write("\n\n")
    
    # Generate summary
    print(f"\n{'='*80}")
    print("VERDICTS")
    print(f"{'='*80}\n")
    
    for site_name, verdict_data in verdicts.items():
        verdict = verdict_data["verdict"]
        reason = verdict_data["reason"]
        
        symbol = "✓" if verdict == "KEEP" else "⚠️" if verdict == "MAYBE" else "✗"
        print(f"{symbol} {site_name}: {verdict}")
        print(f"   Reason: {reason}")
        print()
    
    # Save summary
    summary = {
        "test": "VISUAL_BROWSER_TEST_003",
        "date": datetime.now(timezone.utc).isoformat(),
        "method": "OCR analysis of existing screenshots (no Playwright)",
        "sites_tested": len(sites),
        "verdicts": verdicts,
        "detailed_results": all_site_results
    }
    
    summary_path = OUTPUT_DIR / "test_003_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Summary saved: {summary_path}")
    
    # Generate CSV
    csv_path = OUTPUT_DIR / "verdicts.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "verdict", "reason"])
        writer.writeheader()
        for site_name, verdict_data in verdicts.items():
            writer.writerow({
                "site": site_name,
                "verdict": verdict_data["verdict"],
                "reason": verdict_data["reason"]
            })
    print(f"✓ Verdicts saved: {csv_path}")
    
    print(f"\n{'='*80}")
    print("Analysis complete")
    print(f"{'='*80}")
    
    return verdicts, all_site_results


if __name__ == "__main__":
    main()
