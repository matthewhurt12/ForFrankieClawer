# MANUAL_LEAD_INTAKE_001 - System Complete

**Date:** 2026-05-04  
**Status:** READY FOR USE  
**Purpose:** Make it easy to manually underwrite local vintage audio leads

---

## ✓ What Was Built

### 1. Lead Intake CSV
**File:** `lead_intake.csv`

Simple spreadsheet to paste leads you find:
```csv
date_found,source,listing_url,screenshot_path,model_guess,title,asking_price,location,seller_condition_claim,photos_available,notes,status
```

**One line per lead.** That's it.

---

### 2. Automated Underwriting Script
**File:** `manual_lead_review.py`

Processes leads from CSV and generates full underwriting reports.

**What it does:**
1. ✓ Identifies model from title/guess
2. ✓ Runs eBay active context search automatically
3. ✓ Filters accessories/parts/manuals using price floors
4. ✓ Shows active market range (median, low, high)
5. ✓ Calculates margin potential (% below median)
6. ✓ Flags risks (above market, thin margin, suspiciously low, etc.)
7. ✓ Generates seller questions (model-specific)
8. ✓ Marks as NEEDS_MANUAL_SOLD_COMPS
9. ✓ Does NOT say BUY until manual sold comps entered
10. ✓ Saves detailed report to `reports/lead_XXXX_review.md`

**Usage:**
```bash
# Process all unreviewed leads
python manual_lead_review.py

# Review specific lead
python manual_lead_review.py --lead-id 1

# Re-process all leads
python manual_lead_review.py --all
```

---

### 3. Report Template
**File:** `reports/MANUAL_LEAD_REVIEW_TEMPLATE.md`

Clean markdown template for manual editing if you want to track additional notes, action logs, or follow-ups.

---

### 4. Manual Alert Setup Guide
**File:** `docs/MANUAL_ALERT_SETUP.md`

Complete guide for setting up daily alerts via:
- ✓ Craigslist RSS feeds (email alerts via IFTTT)
- ✓ Facebook Marketplace saved searches
- ✓ EstateSales.net email alerts
- ✓ AuctionZip alerts
- ✓ OfferUp app notifications

**Saved search queries included:**
- McIntosh MA5100 / MA 5100 / MA6100
- Pioneer SX-1050 / SX-1250
- Marantz 2270 / 2275 / receiver
- Sansui 9090 / G-9000
- Technics SL-1200
- Nakamichi Dragon / cassette
- Vintage receiver / stereo / turntable

---

### 5. Quick Start Guide
**File:** `README_LEAD_INTAKE.md`

Step-by-step workflow:
1. Find lead on Craigslist/FB Marketplace
2. Add one line to `lead_intake.csv`
3. Run `python manual_lead_review.py`
4. Review generated report
5. Contact seller if promising
6. Verify sold comps before buying

---

## Test Run Results

**Test Lead:** McIntosh MA 5100 - $750 asking (Athens, GA)

**Underwriting Results:**
```
Identified Model: McIntosh MA 5100
Category: mcintosh
Price Floor: $500

Active Market Context:
  Active Listings: 7
  Median Active Price: $1,495.00
  Price Range: $1,200 - $1,999

Margin Analysis:
  Discount vs Median Active: 50%
  ✓ STRONG margin potential

Seller Questions Generated:
  1. Does it power on and produce sound on both channels?
  2. Are all inputs/outputs working?
  3. Any scratchy pots, switches, or controls?
  4. Original owner? Service history?
  5. Why are you selling it?
  6. Are the blue meters working and lighting up?
  7. Any cabinet damage or veneer issues?

Verdict: ✓ INVESTIGATE - Strong margin potential if sold comps confirm
```

**Report saved:** `reports/lead_0001_review.md`

---

## Files Created

```
lead_intake.csv                          # Main intake spreadsheet
manual_lead_review.py                    # Underwriting script ⭐
reports/MANUAL_LEAD_REVIEW_TEMPLATE.md   # Report template
docs/MANUAL_ALERT_SETUP.md               # Alert setup guide
README_LEAD_INTAKE.md                    # Quick start guide
reports/lead_XXXX_review.md              # Generated reports (per lead)
reports/MANUAL_LEAD_INTAKE_001_SUMMARY.md # This file
```

---

## How to Use (Quick Reference)

### Daily Routine (5 minutes)

**Morning:**
1. Check Craigslist RSS feed alerts
2. Check Facebook Marketplace saved searches
3. Check OfferUp app notifications

**When you find a lead:**

1. **Add to CSV:**
   ```csv
   2026-05-04,Craigslist Athens,https://...,screenshots/lead_001.png,McIntosh MA 5100,McIntosh MA5100 Amp,750,Athens GA,works great,yes,clean photos,unreviewed
   ```

2. **Run review:**
   ```bash
   python manual_lead_review.py
   ```

3. **Check report:**
   - Open `reports/lead_0001_review.md`
   - Look for: ✓ INVESTIGATE / ⚠️ CAUTION / ✗ PASS

4. **Contact seller (if promising):**
   - Use generated seller questions
   - Ask about condition, function, history

5. **Verify sold comps:**
   - eBay Advanced Search → Sold Items
   - eBay Product Research (paid)
   - Terapeak (paid)

6. **Decide:**
   - BUY (if sold comps confirm + good condition)
   - PASS (if margin too thin or red flags)

---

## Model Recognition

Script auto-detects these models from title/guess:

**McIntosh:**
- MA 5100 / MA5100
- MA 6100 / MA6100
- C22 / C 22

**Pioneer:**
- SX-1250 / SX 1250
- SX-1050 / SX 1050

**Marantz:**
- 2270
- 2275

**Sansui:**
- G-9000 / G9000
- 9090

**Technics:**
- SL-1200 / SL 1200

**Nakamichi:**
- Dragon
- 1000ZXL / 1000 ZXL

**Generic fallbacks:**
- "McIntosh" → McIntosh (model unknown), $500 floor
- "Pioneer" → Pioneer (model unknown), $400 floor
- "Marantz" → Marantz (model unknown), $400 floor

---

## Margin Analysis Thresholds

**Strong Deal:** 40%+ below median active  
**Moderate Deal:** 25-40% below median active  
**Weak Deal:** <25% below median active

**Risk Flags:**
- ABOVE MARKET: Asking price exceeds median
- THIN MARGIN: Less than 20% discount
- SUSPICIOUSLY LOW: Below category price floor (likely parts)
- NO PHOTOS: Cannot verify condition
- AS-IS SALE: No returns, high risk
- DISTANCE: 70+ miles, difficult to inspect

---

## Important Warnings

⚠️ **NEEDS_MANUAL_SOLD_COMPS**  
⚠️ **ACTIVE_LISTING_CONTEXT_ONLY**  
⚠️ **NOT_SOLD_COMPS**

**The script does NOT:**
- Pull sold comps (only active listings)
- Make buy decisions for you
- Guarantee profit
- Replace due diligence

**You must still:**
- Verify eBay sold comps manually
- Ask seller questions
- Inspect in person or via video
- Trust your gut on condition/risk

---

## Next Steps

### Immediate (Today)

1. ✓ Read `docs/MANUAL_ALERT_SETUP.md`
2. ✓ Set up Craigslist RSS feeds (10 min)
3. ✓ Save Facebook Marketplace searches (5 min)
4. ✓ Sign up for EstateSales.net alerts (2 min)

### Daily (5-10 min)

1. Check RSS feed alerts
2. Check Facebook Marketplace
3. Check OfferUp app
4. Add any leads to `lead_intake.csv`
5. Run `python manual_lead_review.py`

### Weekly

1. Browse EstateSales.net for upcoming sales
2. Check AuctionZip for auctions
3. Review any pending leads in your intake CSV

---

## Realistic Expectations

**Lead Volume:**
- Expect 1-2 qualified leads per week (if lucky)
- Most local markets are picked over
- High-value vintage audio is rare

**Conversion Rate:**
- 10-20% of leads are worth contacting
- 10% of contacted sellers respond
- 10% of responses turn into inspections
- 50% of inspections reveal condition issues

**Timeline:**
- Finding a deal takes weeks/months of daily monitoring
- Estate sales are your best bet (uninformed sellers)
- Craigslist/FB Marketplace are competitive (other flippers watching)

**Goal:**
Find 1-2 legitimate undervalued units per month worth buying.

---

## Compliance

✓ All leads marked NEEDS_MANUAL_SOLD_COMPS  
✓ All context marked ACTIVE_LISTING_CONTEXT_ONLY  
✓ Script does not say BUY without manual verification  
✓ No automatic purchasing  
✓ No eBay user data stored  
✓ 7-day temp file cleanup applies to eBay searches  

---

## Support Files

**Already built (from previous phases):**
- `ebay_active_context.py` - eBay active listing search with filtering
- `target_models.txt` - List of 12 priority models
- `reports/LEAD_VALIDATION_RUN_001.md` - Active market baseline
- `reports/LOCAL_LEAD_HUNT_001.md` - Local search attempt (no results)

**Integration:**
The manual lead review script calls `ebay_active_context.py` automatically to fetch live market data for each lead.

---

**System Status: ✓ READY FOR DAILY USE**

Start monitoring local listings tomorrow. When you find a lead, you're now 30 seconds away from a full underwriting report.
