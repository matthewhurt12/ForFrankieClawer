# VISUAL_BROWSER_TEST_004 - Manual Browser + OS Screen Capture

**Date:** 2026-05-04  
**Status:** READY TO RUN  
**Purpose:** Test visual screen capture + OCR with manually-controlled Chrome browser

---

## ⚠️ Critical Notices

**VISUAL_CONTEXT_ONLY**  
**NEEDS_MANUAL_REVIEW**  
**NOT_SOLD_COMPS**

---

## Method: Manual Browser Control + Screen Capture

### What This Test Does

**USER Controls:**
- ✓ Opens Chrome manually
- ✓ Logs into sites if needed
- ✓ Navigates to marketplace
- ✓ Searches for items
- ✓ Scrolls through results
- ✓ Verifies what's visible on screen

**SCRIPT Observes:**
- ✓ Captures OS-level screenshots
- ✓ Detects listing card regions
- ✓ Crops individual cards
- ✓ Runs Tesseract OCR
- ✓ Extracts titles, prices, shipping
- ✓ Saves results to CSV/JSON

**SCRIPT Does NOT:**
- ❌ Control the browser
- ❌ Use Playwright/Selenium
- ❌ Access DOM
- ❌ Bypass CAPTCHA
- ❌ Auto-login
- ❌ Message sellers
- ❌ Click buy buttons

---

## Test Sites

1. **Facebook Marketplace** - "vintage stereo"
2. **Mercari** - "vintage receiver"
3. **Google Shopping** - "Pioneer SX-1050"
4. **Craigslist** - "vintage stereo"

---

## Workflow

### User Preparation
```
1. Open Chrome browser
2. Navigate to marketplace site
3. Log in if required (Facebook)
4. Search for target term
5. Wait for results to load
6. Position browser window to show listings
7. Run script
```

### Script Process
```
1. Prompt user: "Press Enter when ready"
2. Capture full screen using mss
3. Save screenshot (1920x1080 PNG)
4. Detect card regions (grid heuristics)
5. Crop each detected card
6. Run Tesseract OCR with multiple PSM modes
7. Extract price patterns ($XXX, Free, etc.)
8. Extract titles (first non-price line)
9. Extract shipping info
10. Save card crop + OCR results
11. Prompt user to scroll
12. Repeat for 3 screenshots per site
```

### OCR Strategy
```python
# PSM Modes tried:
PSM 3: Fully automatic page segmentation (default)
PSM 6: Assume single uniform text block
PSM 11: Sparse text (find as much as possible)

# Pick best result (most text found)
```

---

## Failure Categories

### PAGE_NOT_VISIBLE
**Definition:** Chrome showed no listings (login wall, error page, blank page)  
**User Action:** Navigate manually until listings visible  
**Script Action:** Capture what user sees, report failure

### SCREENSHOT_FAILED
**Definition:** mss failed to capture screen  
**Possible Causes:** Display issues, permissions, WSL2 X11 problems  
**Script Action:** Report technical error

### CARD_CROP_FAILED
**Definition:** Screenshots captured but no card regions detected  
**Possible Causes:**
- Listings not in grid layout
- Cards too small/large for detection heuristic
- Single-column layout (mobile view)
- No listings visible in viewport

**Script Action:** Report crop failure, save full screenshots for manual review

### OCR_FAILED
**Definition:** Cards detected and cropped but OCR extracted no useful text  
**Possible Causes:**
- Low contrast images
- Overlapping text
- Non-standard fonts
- Text on images (not HTML text)

**Script Action:** Report OCR failure, save crops for manual review

### PRICE_PARSE_FAILED
**Definition:** OCR worked but no price patterns found  
**Possible Causes:**
- Prices displayed as "Contact for price"
- Auction format (no fixed price)
- OCR misread numbers
- Price in image, not text

**Script Action:** Mark as partial parse, save for review

### MODEL_CLASSIFY_FAILED
**Definition:** Title extracted but can't identify specific model  
**Possible Causes:**
- Generic titles ("Vintage Receiver")
- Model not in our target list
- OCR misread model number

**Script Action:** Mark as unclassified, save for manual review

---

## Expected Results

### Facebook Marketplace
**Prediction:** KEEP (if logged in)

**Reasoning:**
- ✓ Grid layout with cards
- ✓ Clear prices visible
- ✓ Images + text
- ✓ Consistent layout
- ⚠️ Requires login

**Expected Failure Mode:** PAGE_NOT_VISIBLE if not logged in

---

### Mercari
**Prediction:** KEEP

**Reasoning:**
- ✓ Grid layout
- ✓ Product card design
- ✓ Clear prices
- ✓ No login required for browsing
- ✓ Clean modern layout

**Expected Failure Mode:** None if manually opened

---

### Google Shopping
**Prediction:** KEEP

**Reasoning:**
- ✓ Grid layout
- ✓ Product images + prices
- ✓ Store names visible
- ✓ No login required
- ✓ Consistent Google design

**Expected Failure Mode:** None if manually opened

---

### Craigslist
**Prediction:** MAYBE

**Reasoning:**
- ⚠️ List layout (not grid)
- ⚠️ Minimal styling
- ⚠️ Prices in various formats
- ✓ No login required
- ⚠️ JavaScript-heavy

**Expected Failure Mode:** CARD_CROP_FAILED (list layout) or OCR_FAILED (minimal text)

---

## Success Criteria

### KEEP Verdict
**Requirements:**
- ≥5 cards parsed with title + price
- ≥50% OCR success rate on detected cards
- Clear listings visible in screenshots
- Reproducible across multiple scrolls

**Meaning:** This site works for manual browser + screen capture

---

### MAYBE Verdict
**Requirements:**
- 1-4 cards parsed
- 20-49% OCR success rate
- Some listings extracted but low confidence

**Meaning:** Might work with better card detection or OCR tuning

---

### DROP Verdict
**Indicators:**
- 0 cards parsed
- PAGE_NOT_VISIBLE (login walls, no results)
- CARD_CROP_FAILED consistently
- OCR_FAILED on all cards

**Meaning:** This site won't work even with manual browsing

---

## Running the Test

### Prerequisites
```bash
# Installed:
pip3 install mss pillow pytesseract

# Tesseract OCR installed:
sudo apt install tesseract-ocr  # If not already installed

# X11 display:
export DISPLAY=:0  # For WSL2
```

### Command
```bash
cd ~/.openclaw/workspace
python3 scripts/manual_screen_capture_004.py
```

### During Test
```
1. Script prompts: "Press Enter when ready for screenshot 1..."
2. You ensure Chrome shows listings
3. You press Enter
4. Script captures screen, processes, shows results
5. Script prompts: "Scroll down and press Enter for screenshot 2..."
6. You scroll manually
7. You press Enter
8. Repeat for 3 screenshots per site
9. Move to next site
```

---

## Output Files

### Screenshots
```
screenshots/manual_browser_004/
  facebook_marketplace_screen_01.png
  facebook_marketplace_screen_02.png
  facebook_marketplace_screen_03.png
  mercari_screen_01.png
  ... (3 per site x 4 sites = 12 screenshots)
```

### Card Crops
```
screenshots/manual_browser_004/
  card_001.png  # First card from screenshot 1
  card_002.png  # Second card from screenshot 1
  ... (10-50 cards per site)
```

### Data
```
data/manual_browser_004/
  facebook_marketplace_results.json  # Per-site results
  mercari_results.json
  google_shopping_results.json
  craigslist_results.json
  test_004_summary.json              # Overall summary
  parsed_listings.csv                # All extracted listings
```

---

## After Test: Next Steps

### If Multiple Sites = KEEP

**Build Production Tool:**
```python
# manual_marketplace_scanner.py
# 1. User opens Chrome to any marketplace
# 2. Searches manually
# 3. Runs script
# 4. Script captures screens as user scrolls
# 5. Extracts all visible listings
# 6. Saves to lead_intake.csv
# 7. Runs manual_lead_review.py automatically
```

**Use Cases:**
- Quick scan of Facebook Marketplace
- Check Mercari for new listings
- Supplement Craigslist RSS feeds
- One-off deep searches

---

### If All Sites = DROP

**Stick with Existing Tools:**
- ✓ Craigslist RSS feeds
- ✓ eBay Browse API
- ✓ Manual searches (no automation)

---

## Advantages of This Method

### vs Playwright Automation
- ✓ No bot detection (human controls browser)
- ✓ No CAPTCHA challenges
- ✓ No login automation needed
- ✓ Works on any site user can see
- ✓ User verifies what's captured
- ✓ No Terms of Service concerns

### vs HTTP Scraping
- ✓ Works on JavaScript-heavy sites
- ✓ Sees exactly what user sees
- ✓ No need to parse HTML/DOM
- ✓ No selector maintenance

### vs Full Manual Search
- ✓ Faster data extraction
- ✓ Structured output (CSV)
- ✓ Can process multiple screens quickly
- ✓ Consistent price/title extraction

---

## Limitations

### Still Requires
- ⚠️ User to manually open sites
- ⚠️ User to manually log in
- ⚠️ User to manually scroll
- ⚠️ User to verify listings visible

### OCR Limitations
- ⚠️ May misread text
- ⚠️ May miss prices in images
- ⚠️ May fail on unusual fonts
- ⚠️ Requires good contrast

### Not Automated
- ⚠️ Can't run 24/7
- ⚠️ Can't check multiple sites simultaneously
- ⚠️ Slower than full automation

---

## Compliance

✓ No browser automation  
✓ No CAPTCHA bypass  
✓ No auto-login  
✓ No seller messaging  
✓ No automated buying  
✓ User controls all navigation  
✓ Script only observes visible screen  
✓ All data marked VISUAL_CONTEXT_ONLY  
✓ All data marked NEEDS_MANUAL_REVIEW  
✓ 7-day screenshot retention planned  

---

## Ready to Run

**Status:** Script created and ready  
**User Action Required:** Open Chrome, navigate to first site, run script  
**Estimated Time:** 5-10 minutes per site (40 minutes total)

**Command:**
```bash
cd ~/.openclaw/workspace
python3 scripts/manual_screen_capture_004.py
```

---

**Will update this report with actual results after test run.**
