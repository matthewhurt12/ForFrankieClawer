# Vintage Audio Flipping System - Quick Start

**Status:** ✓ READY FOR DAILY USE  
**Date:** 2026-05-04

---

## What You Have

A complete lead intake and underwriting system for vintage audio equipment flipping.

**Phase 1:** eBay active market context (✓ complete)  
**Phase 2:** Manual lead intake and underwriting (✓ complete)  
**Phase 3:** Sold comps analysis (not built - requires manual verification)

---

## Daily Workflow (10 minutes)

### 1. Check for New Listings (5 min)

- Craigslist RSS feed alerts (email)
- Facebook Marketplace saved searches
- OfferUp app notifications

### 2. Add Leads (30 seconds per lead)

When you find something promising:

```bash
# Open lead_intake.csv and add one line:
2026-05-04,Craigslist Athens,URL,screenshots/001.png,McIntosh MA 5100,McIntosh MA5100 Amp,750,Athens GA,works great,yes,notes,unreviewed
```

### 3. Run Underwriting (2 min)

```bash
cd ~/.openclaw/workspace
python manual_lead_review.py
```

### 4. Review Reports (2 min)

Check `reports/lead_XXXX_review.md` for:
- ✓ INVESTIGATE (50%+ below market, no red flags)
- ⚠️ CAUTION (margin exists but risks present)
- ✗ PASS (thin margin or above market)

### 5. Contact Seller (If Promising)

Use the generated seller questions from the report.

---

## Target Models (Priority)

| Model | Suggested Max Ask | Active Median | Margin Target |
|-------|-------------------|---------------|---------------|
| McIntosh MA 5100 | $900 | $1,495 | 40%+ |
| McIntosh MA 6100 | $1,200 | $1,949 | 38%+ |
| Pioneer SX-1250 | $2,500 | $3,875 | 35%+ |
| Pioneer SX-1050 | $1,200 | $1,925 | 38%+ |
| Marantz 2270 | $1,500 | $2,250 | 33%+ |
| Marantz 2275 | $1,500 | $2,270 | 34%+ |
| Technics SL-1200 | $500 | $850 | 41%+ |
| Nakamichi Dragon | $900 | $1,500 | 40%+ |

---

## Files & Commands

### Main Files
```
lead_intake.csv              # Add leads here (one line per lead)
manual_lead_review.py        # Run this to underwrite leads
reports/lead_XXXX_review.md  # Generated underwriting reports
```

### Main Commands
```bash
# Process all unreviewed leads
python manual_lead_review.py

# Review specific lead by row number
python manual_lead_review.py --lead-id 1

# Re-process all leads
python manual_lead_review.py --all
```

### Documentation
```
README_LEAD_INTAKE.md                    # Detailed how-to guide
docs/MANUAL_ALERT_SETUP.md               # Set up daily alerts
reports/MANUAL_LEAD_INTAKE_001_SUMMARY.md # System overview
reports/LEAD_VALIDATION_RUN_001.md       # Market baseline data
```

---

## Set Up Alerts (One-Time, 20 Minutes)

**Read:** `docs/MANUAL_ALERT_SETUP.md`

**Quick setup:**

1. **Craigslist RSS → Email** (10 min)
   - Sign up: https://ifttt.com
   - Create: "RSS feed → Email"
   - Paste RSS URLs from alert guide

2. **Facebook Marketplace** (5 min)
   - Save searches for each model
   - Enable browser notifications

3. **EstateSales.net** (2 min)
   - Sign up for email alerts
   - Zip: 30606 (Athens) or 30301 (Atlanta)

4. **OfferUp App** (3 min)
   - Download app
   - Save searches
   - Enable push notifications

---

## Example: End-to-End

**Morning: You see this on Craigslist Athens:**

> "McIntosh MA5100 Integrated Amplifier - $750"
> "Works great, all meters functional"
> Location: Athens, GA
> Photos: Yes (clean, shows back panel)

**Step 1:** Add to `lead_intake.csv`
```csv
2026-05-04,Craigslist Athens,https://...,screenshots/001.png,McIntosh MA 5100,McIntosh MA5100 Integrated Amplifier,750,Athens GA,works great,yes,clean photos,unreviewed
```

**Step 2:** Run underwriting
```bash
python manual_lead_review.py
```

**Step 3:** Review report (reports/lead_0001_review.md)
```
Identified Model: McIntosh MA 5100
Active Median: $1,495
Asking Price: $750
Discount: 50%

Verdict: ✓ INVESTIGATE - Strong margin potential
```

**Step 4:** Contact seller
```
Hi, is the McIntosh MA5100 still available?

Quick questions:
1. Does it power on and produce sound on both channels?
2. Are all inputs working?
3. Any scratchy pots or switches?
4. Original owner?
5. Are the blue meters lighting up properly?

I can come see it today if it checks out. Would $700 work?
```

**Step 5:** If seller responds well, verify eBay sold comps
- Go to eBay → Advanced Search → Sold Items
- Search "McIntosh MA 5100"
- Check last 90 days of actual sold prices
- Confirm median sold is similar to median active ($1,400-$1,600)

**Step 6:** Inspect in person
- Test all functions
- Check condition
- Negotiate if issues found

**Step 7:** Buy (or pass)
- If it works and looks good: Buy at $700-750
- If issues found: Negotiate lower or pass
- Expected flip price: $1,200-1,400 (after cleaning/testing)

---

## Critical Warnings

⚠️ **ACTIVE_LISTING_CONTEXT_ONLY**  
The system shows active eBay listings, not sold comps. You must manually verify sold prices before buying.

⚠️ **NEEDS_MANUAL_SOLD_COMPS**  
Every lead report says this. It's not optional. Active listings ≠ sold prices.

⚠️ **NOT_SOLD_COMPS**  
Repeating for emphasis: Do not use active listings as sold comps.

**Why this matters:**
- Active listings can sit unsold for months
- Sellers often overprice
- Sold comps show what people actually paid
- 30-50% of listings never sell at asking price

---

## Realistic Expectations

**Lead Volume:**
- 1-2 qualified leads per week (if you check daily)
- Most weeks: zero leads
- Estate sales are your best source

**Success Rate:**
- 20% of leads worth contacting
- 10% of contacts respond
- 50% of responses have hidden issues
- 1-2 purchases per month if you're aggressive

**Profit Per Flip:**
- $300-800 per unit (after fees, shipping, repairs)
- 3-6 hours work per unit (cleaning, testing, listing, shipping)
- Effective hourly: $50-150/hr (if you're good)

**Timeline:**
- First purchase: 2-4 weeks (if lucky)
- First successful flip: 4-8 weeks
- Consistent income: 3-6 months of daily monitoring

---

## Next Steps

**Today:**
1. Read `docs/MANUAL_ALERT_SETUP.md`
2. Set up Craigslist RSS feeds
3. Save Facebook Marketplace searches
4. Sign up for EstateSales.net alerts

**Tomorrow:**
1. Check alerts (5 min)
2. Add any leads to CSV
3. Run underwriting script
4. Contact promising sellers

**This Week:**
1. Find your first lead
2. Run the underwriting
3. See the system in action
4. Get comfortable with the workflow

**This Month:**
1. Find 1-2 units worth buying
2. Verify sold comps
3. Inspect in person
4. Make your first purchase

---

## Support

**Questions about the system:**
- Read `README_LEAD_INTAKE.md` for detailed workflow
- Read `reports/LEAD_VALIDATION_RUN_001.md` for market baseline
- Read `docs/MANUAL_ALERT_SETUP.md` for alert setup

**Questions about models/pricing:**
- Check `reports/LEAD_VALIDATION_RUN_001.md` for all 12 target models
- Run `python ebay_active_context.py "Model Name"` for updated context

**Troubleshooting:**
- "No eBay data": Model not cached, manual research needed
- "Filter failure": Price floor leaked false positives, trust your judgment
- "Unable to calculate": Check CSV format (no $ in price field)

---

**System Ready. Start monitoring tomorrow morning.**
