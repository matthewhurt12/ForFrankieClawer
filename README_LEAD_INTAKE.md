# Lead Intake System - Quick Start

## What This Does

When you find a vintage audio listing on Craigslist, Facebook Marketplace, or estate sales, you can quickly underwrite it by:

1. Adding one line to `lead_intake.csv`
2. Running `python manual_lead_review.py`
3. Getting an instant underwriting report with:
   - Active eBay market context
   - Margin analysis
   - Risk flags
   - Seller questions to ask
   - Buy/pass recommendation

---

## How to Use

### Step 1: Find a Lead

Example: You see a Craigslist listing:
- Title: "McIntosh MA5100 Integrated Amp"
- Price: $750
- Location: Athens, GA
- URL: https://athens.craigslist.org/ele/d/mcintosh-ma5100/12345.html

### Step 2: Add to lead_intake.csv

Open `lead_intake.csv` and add a new row:

```csv
2026-05-04,Craigslist Athens,https://athens.craigslist.org/ele/d/mcintosh-ma5100/12345.html,screenshots/lead_001.png,McIntosh MA 5100,McIntosh MA5100 Integrated Amp,750,Athens GA,works great,yes,clean photos,unreviewed
```

**Fields:**
```
date_found,source,listing_url,screenshot_path,model_guess,title,asking_price,location,seller_condition_claim,photos_available,notes,status
```

**Tips:**
- `model_guess`: Best guess of the model (e.g., "McIntosh MA 5100")
- `asking_price`: Just the number, no $ sign (e.g., 750)
- `photos_available`: yes / no / partial
- `status`: Always start with "unreviewed"

### Step 3: Run the Review Script

```bash
cd ~/.openclaw/workspace
python manual_lead_review.py
```

This will:
- Identify the model from your title/guess
- Run eBay active context search
- Filter out parts/accessories/manuals
- Calculate margin potential
- Generate seller questions
- Create a detailed report in `reports/lead_XXXX_review.md`

### Step 4: Review the Report

Open `reports/lead_0001_review.md` and check:

- **Discount vs Median Active:** Is it 30%+ below market?
- **Risk Flags:** Any red flags (suspiciously low price, no photos, etc.)?
- **Recommendation:** INVESTIGATE / CAUTION / PASS

### Step 5: Contact Seller (If Promising)

Use the generated seller questions from the report:

1. Does it power on and produce sound on both channels?
2. Are all inputs/outputs working?
3. Any scratchy pots, switches, or controls?
4. Original owner? Service history?
5. Are the blue meters working? (McIntosh specific)

### Step 6: Manual Sold Comps

**⚠️ CRITICAL:** Before buying, manually verify sold comps via:
- eBay Advanced Search → Sold Items
- eBay Product Research (paid tool)
- Terapeak (paid tool)

**Active listings are NOT sold comps.**

---

## Command Options

### Process All Unreviewed Leads
```bash
python manual_lead_review.py
```

### Review Specific Lead
```bash
python manual_lead_review.py --lead-id 1
```

### Re-Process All Leads
```bash
python manual_lead_review.py --all
```

---

## Example Workflow

**Morning Routine (5 minutes):**

1. Check Craigslist RSS feed
2. Check Facebook Marketplace saved searches
3. Find lead: "Pioneer SX-1050 receiver $800 Atlanta"

**Add to CSV:**
```csv
2026-05-04,FB Marketplace,https://facebook.com/marketplace/item/12345,screenshots/lead_002.png,Pioneer SX-1050,Pioneer SX-1050 receiver,800,Atlanta GA,excellent condition,yes,looks clean,unreviewed
```

**Run Review:**
```bash
python manual_lead_review.py
```

**Output:**
```
LEAD #2 - MANUAL UNDERWRITING
================================================================================

Identified Model: Pioneer SX-1050
Category: pioneer
Price Floor: $400

Step 1: Fetching active market context...
  Running eBay active context search for: Pioneer SX-1050

Step 2: Analyzing lead...
  Source: FB Marketplace
  Asking Price: $800
  Location: Atlanta GA

Step 3: Active Market Context (eBay)
  Active Listings: 8
  Median Active Price: $1,925.00
  Filter Status: VALID

Step 4: Margin Potential
  Discount vs Median Active: 58%
  ✓ STRONG margin potential

Step 5: Seller Questions
  1. Does it power on and produce sound on both channels?
  2. Does the tuner work and pull in stations?
  ...

UNDERWRITING VERDICT
================================================================================

⚠️  NEEDS_MANUAL_SOLD_COMPS

✓ INVESTIGATE - Strong margin potential if sold comps confirm
```

**Next Steps:**
1. Message seller with questions
2. Verify eBay sold comps (not just active listings)
3. Schedule inspection if seller responses are good

---

## Files Created

- `lead_intake.csv` - Main intake spreadsheet
- `manual_lead_review.py` - Underwriting script
- `reports/lead_XXXX_review.md` - Detailed reports for each lead
- `reports/MANUAL_LEAD_REVIEW_TEMPLATE.md` - Template for manual editing
- `docs/MANUAL_ALERT_SETUP.md` - How to set up daily alerts

---

## Important Warnings

⚠️ **NEEDS_MANUAL_SOLD_COMPS**  
⚠️ **ACTIVE_LISTING_CONTEXT_ONLY**  
⚠️ **NOT_SOLD_COMPS**

**DO NOT:**
- Call anything a BUY based on active listings alone
- Use active eBay listings as sold comps
- Skip in-person inspection for high-value items
- Ignore obvious risk flags

**DO:**
- Verify sold comps manually before buying
- Ask all seller questions
- Inspect in person or via video call
- Walk away if something feels off

---

## Quick Reference

**Model Price Floors (Parts Filter):**
- McIntosh: $500 minimum
- Pioneer: $400 minimum
- Marantz: $400 minimum
- Sansui: $400 minimum
- Technics SL-1200: $300 minimum
- Nakamichi: $75 minimum

**Margin Targets:**
- 40%+ below median active = Strong deal
- 25-40% below median active = Moderate deal
- <25% below median active = Thin margin, pass

**Target Models (Priority):**
1. McIntosh MA 5100 (max $900)
2. McIntosh MA 6100 (max $1,200)
3. Pioneer SX-1250 (max $2,500)
4. Pioneer SX-1050 (max $1,200)
5. Technics SL-1200 (max $500)

---

## Troubleshooting

**"No eBay data available"**
- The model might not be in our search history yet
- Script will still generate report, but you'll need to manually research active market

**"Filter status: FILTER_FAILURE_REVIEW_NEEDED"**
- The price filter leaked false positives (parts, accessories)
- Median price is suspiciously low
- Trust your judgment more than the automated metrics

**"Unable to calculate margin"**
- Missing asking price or eBay median
- Check `lead_intake.csv` for correct price format (no $ sign, just number)

---

## Next Steps

1. Read `docs/MANUAL_ALERT_SETUP.md` to set up daily alerts
2. Add your first test lead to `lead_intake.csv`
3. Run `python manual_lead_review.py` to see the system in action
4. When you find real leads, follow the workflow above

**Goal:** Find 1-2 qualified leads per week worth investigating.
