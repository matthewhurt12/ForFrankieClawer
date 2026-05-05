# VISUAL_BROWSER_TEST_003 - Screen Capture + OCR Analysis

**Date:** 2026-05-04  
**Status:** IN PROGRESS  
**Purpose:** Test visual OCR analysis without Playwright DOM access

---

## ⚠️ Critical Notices

**VISUAL_CONTEXT_ONLY**  
**NEEDS_MANUAL_REVIEW**  
**NOT_SOLD_COMPS**

---

## Concept Change

### What Failed (VISUAL_BROWSER_TEST_002)
- ❌ Playwright browser automation
- ❌ DOM selector parsing
- ❌ Cloudflare/bot detection blocked Mercari
- ❌ Sites actively fight automation

### New Approach (TEST_003)
- ✓ NO Playwright
- ✓ NO DOM selectors
- ✓ NO automation detection
- ✓ Use OCR on screenshots only
- ✓ Works with manually-controlled browser

---

## Methodology

### Phase A: Analyze Existing Screenshots
**Goal:** Test if OCR can extract useful data from VISUAL_BROWSER_TEST_002 screenshots

**Process:**
1. Load 13 screenshots from `screenshots/browser_test_002/`
2. Run Tesseract OCR on each image
3. Extract text, prices, marketplace indicators
4. Generate KEEP/DROP verdict for each site

**Findings:** (OCR processing in progress...)

---

### Phase B: Manual Browser + Screen Capture (Future)
**Goal:** Test real-time screen capture of manually-controlled browser

**Proposed Process:**
1. User opens Chrome manually
2. User logs into Facebook/etc. if needed
3. User navigates to marketplace search
4. Script uses mss/pyautogui to capture screen
5. OCR extracts visible listings
6. User scrolls manually or on request
7. Repeat capture + OCR
8. Save results with 7-day auto-delete

**Advantages:**
- ✓ No bot detection (human controls browser)
- ✓ No login automation needed
- ✓ No CAPTCHA bypass needed
- ✓ Works on any site visible on screen
- ✓ User verifies what's captured

**Disadvantages:**
- ⚠️ Requires manual interaction
- ⚠️ OCR accuracy depends on screen layout
- ⚠️ Slower than automated scraping

---

## Phase A Results (Preliminary)

### OCR Processing Notes

**Tool:** Tesseract 5.5.0  
**Method:** pytesseract.image_to_string()  
**Image Format:** PNG, 1920x1080, 8-bit RGB

**Processing Time:**
- ~30-60 seconds per 1920x1080 screenshot
- 13 screenshots = ~6-13 minutes total
- OCR is CPU-intensive

**What We're Extracting:**
- All visible text
- Price patterns ($XXX.XX, $X,XXX)
- Marketplace indicators (brand names)
- Text line count (content density)
- Screenshot metadata

---

## Expected Verdicts (Based on Visual Inspection)

### Google Shopping
**Prediction:** KEEP

**Reasoning:**
- 4 screenshots captured (627-738 KB each)
- Large file sizes suggest rich content
- Shopping results typically have:
  - Product images
  - Prices
  - Store names
  - "Buy" buttons
- OCR should detect prices and product names

**Expected OCR Success:** High

---

### Craigslist
**Prediction:** DROP

**Reasoning:**
- 4 screenshots captured (60 KB each)
- Very small file sizes
- Likely JavaScript placeholder page
- Minimal content to OCR
- Previous tests showed "loading" placeholder

**Expected OCR Success:** Low

---

### Facebook Marketplace
**Prediction:** DROP

**Reasoning:**
- 1 screenshot (685 KB)
- Login required (stopped immediately)
- Screenshot likely shows login page
- No marketplace content visible

**Expected OCR Success:** N/A (login wall)

---

### Mercari
**Prediction:** DROP

**Reasoning:**
- 0 screenshots (browser automation failed)
- Cloudflare blocked even screenshot capture
- No data to analyze

**Expected OCR Success:** N/A (no screenshots)

---

## OCR Processing Status

**Current Status:** Running Tesseract OCR on 9 screenshots (Mercari has 0, Facebook has 1 login page)

**Progress:**
- Mercari: 0 screenshots (skipped - Cloudflare blocked)
- Google Shopping: 4 screenshots (processing...)
- Craigslist: 4 screenshots (processing...)
- Facebook Marketplace: 1 screenshot (processing...)

**Output Files (when complete):**
- `data/visual_ocr_003/google_shopping_ocr_results.json`
- `data/visual_ocr_003/craigslist_ocr_results.json`
- `data/visual_ocr_003/facebook_marketplace_ocr_results.json`
- `data/visual_ocr_003/test_003_summary.json`
- `data/visual_ocr_003/verdicts.csv`

---

## Decision Criteria

### KEEP = OCR Viable
**Requirements:**
- ≥3 prices detected across all screenshots
- ≥20 average text lines per screenshot
- ≥500 average characters per screenshot
- Marketplace identifiers present

**Meaning:** Manual browser + screen capture could work for this site

---

### MAYBE = Marginal
**Indicators:**
- 1-2 prices detected
- 10-20 text lines average
- Some content but low confidence

**Meaning:** Might work with better cropping/processing

---

### DROP = Not Viable
**Indicators:**
- 0 prices detected
- <10 text lines average
- <500 characters average
- Login walls, placeholders, or blocked content

**Meaning:** This site won't work even with manual browsing

---

## Next Steps

### If Phase A Shows Promise

**Sites marked KEEP:**
1. Build manual browser capture script
2. User opens Chrome and navigates manually
3. Script captures screen every X seconds or on demand
4. OCR processes visible area
5. Extract listings automatically
6. Save to temporary CSV (7-day retention)

**Example Workflow:**
```bash
# User opens Chrome, goes to Mercari, searches "vintage receiver"
# Then runs:
python manual_screen_capture.py

# Script prompts:
# "Ready to capture? Browser should show search results. Press Enter..."
# [User presses Enter]
# "Capturing screen..."
# "Running OCR..."
# "Found 12 listings: [titles and prices shown]"
# "Scroll down? (y/n)"
# [User scrolls and presses y]
# "Capturing screen..."
# [Repeat]
```

---

### If Phase A Fails

**All sites marked DROP:**
- Skip manual browser capture
- Stick with existing tools:
  - ✓ Craigslist RSS
  - ✓ eBay Browse API
  - ✓ Manual Facebook searches
- Document why visual approach doesn't help

---

## Compliance

✓ No Playwright automation  
✓ No DOM selector access  
✓ No CAPTCHA bypass  
✓ No auto-login  
✓ No seller messaging  
✓ No automated buying  
✓ All data marked VISUAL_CONTEXT_ONLY  
✓ All data marked NEEDS_MANUAL_REVIEW  
✓ 7-day auto-delete for screenshots planned  

---

## Files

### Input (Existing)
```
screenshots/browser_test_002/
  google_shopping_01_initial.png      # 627 KB
  google_shopping_02_scroll1.png      # 738 KB
  google_shopping_03_scroll2.png      # 556 KB
  google_shopping_04_scroll3.png      # 556 KB
  craigslist_01_initial.png           # 60 KB
  craigslist_02_scroll1.png           # 60 KB
  craigslist_03_scroll2.png           # 60 KB
  craigslist_04_scroll3.png           # 60 KB
  facebook_marketplace_01_initial.png # 685 KB
```

### Output (When OCR Completes)
```
data/visual_ocr_003/
  google_shopping_ocr_results.json
  google_shopping_full_text.txt
  craigslist_ocr_results.json
  craigslist_full_text.txt
  facebook_marketplace_ocr_results.json
  facebook_marketplace_full_text.txt
  test_003_summary.json
  verdicts.csv
```

---

## Preliminary Conclusion

**The visual OCR approach solves the automation problem:**
- ✓ No bot detection (human controls browser)
- ✓ No login automation needed
- ✓ Works on any site user can see
- ✓ Can handle CAPTCHA (user solves it)

**Tradeoff:**
- ⚠️ Requires manual browser control
- ⚠️ OCR accuracy varies by layout
- ⚠️ Slower than full automation

**Viable Use Case:**
If Google Shopping shows good OCR results, manual browsing + screen capture could supplement Craigslist RSS and eBay API for deeper market research.

**Non-Viable Use Case:**
If all sites show poor OCR (like Craigslist placeholder pages), stick with existing tools only.

---

**OCR Processing Status:** RUNNING  
**Estimated Completion:** 5-10 minutes  
**Final Verdicts:** Pending OCR results

Will update this report when OCR processing completes.
