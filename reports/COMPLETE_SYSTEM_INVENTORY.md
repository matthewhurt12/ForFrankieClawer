# Complete System Inventory - Vintage Audio Lead Generation

**Date:** 2026-05-04  
**Status:** Comprehensive system map

---

## 🎯 MISSION

Find and underwrite vintage audio equipment deals across multiple marketplaces with automated scraping, false-positive filtering, and margin analysis.

---

## ✅ CURRENTLY WORKING SYSTEMS

### 1. eBay Browse API (FREE - ACTIVE LISTINGS)
**Script:** `ebay_active_context.py`  
**Status:** ✓ WORKING  
**Cost:** FREE (official eBay API)  
**What It Does:**
- Searches eBay for specific models
- Returns ACTIVE listings (asking prices)
- Filters by price floors ($500+ McIntosh, $400+ Pioneer, etc.)
- Excludes false positives (parts, manuals, LEDs, bulbs)
- Used in lead underwriting for market context

**Credentials:**
- `credentials/ebay-production.json`
- App ID: matthewh-test-PRD-97b75c3f4-28a0682c

**Example Output:**
```
McIntosh MA 6100 - Active Listings:
  1. $1,200 (Excellent) - eBay
  2. $950 (Good) - eBay
  3. $800 (Fair) - eBay
  
Price Range: $800-1200
Median: $950
```

**Integration:** Used by `manual_lead_review.py` for every lead

---

### 2. Lead Intake System
**File:** `lead_intake.csv`  
**Script:** `manual_lead_review.py`  
**Status:** ✓ WORKING

**What It Does:**
- Central queue for all leads (manual + automated)
- Tracks: date, source, URL, model, price, location, condition, photos
- Status tracking: unreviewed → reviewed → pass/pursue

**Format:**
```csv
date_found,source,listing_url,model_guess,title,asking_price,location,seller_condition_claim,photos_available,notes,status
2026-05-04,Mercari,https://...,Technics SL-1200,Turntable,$450,Online,Good,yes,Mercari listing,unreviewed
```

**Sources Feed Into This:**
- Manual entries
- Mercari scraper (auto-adds top 10)
- Facebook Marketplace (auto-adds top 10)
- Future: Reverb, Craigslist RSS

---

### 3. Lead Review & Underwriting
**Script:** `manual_lead_review.py`  
**Status:** ✓ WORKING

**What It Does:**
1. Loads unreviewed leads from `lead_intake.csv`
2. Identifies model from title (McIntosh MA 6100, Technics SL-1200, etc.)
3. Runs eBay Browse API for market context
4. Calculates margin potential (asking vs eBay active range)
5. Generates detailed underwriting report
6. Flags: NEEDS_MANUAL_REVIEW, NEEDS_MANUAL_SOLD_COMPS

**Report Includes:**
- eBay active context (current market)
- Price comparison
- Margin analysis
- Seller questions to ask
- Photos checklist
- Risk factors

**Output:** `reports/lead_XXXX_review.md`

---

### 4. Target Models & Price Floors
**File:** `target_models.txt`  
**System:** Category-based price floors

**Target Models:**
- McIntosh MA 5100 ($500 floor)
- McIntosh MA 6100 ($500 floor)
- Pioneer SX-1250 ($400 floor)
- Pioneer SX-1050 ($400 floor)
- Marantz 2270 ($400 floor)
- Marantz 2275 ($400 floor)
- Technics SL-1200 ($300 floor)
- Nakamichi Dragon ($75 floor)
- Sansui receivers ($400 floor)

**False Positive Filters:**
- LED kits, bulbs, lamps
- Manuals, service guides
- Parts only, repair kits
- Faceplates, knobs, capacitors
- Rebuild kits, restoration parts

---

## ✅ WORKING APIFY INTEGRATIONS

### 5. Mercari Scraper
**Actor ID:** stealth_mode~mercari-product-search-scraper  
**Status:** ✓ WORKING  
**Cost:** ~$0.12/run (8 searches)  
**Data Collected:** 142 unique items

**What It Does:**
- Searches Mercari nationwide
- 8 vintage audio keywords
- 50 items per search
- Deduplicates by item_id
- Auto-adds top 10 to lead_intake.csv

**Key Learning:** Requires `useApifyProxy: true` to bypass bot detection

**Script:** `scripts/mercari_production_run_001.py`

**Output:**
- `data/external_leads/mercari_leads.csv` (142 items)
- `data/external_leads/mercari_raw_run_001.json`

**Search Terms:**
1. McIntosh MA 5100
2. McIntosh MA 6100
3. Pioneer SX-1250
4. Pioneer SX-1050
5. Marantz 2270
6. Marantz 2275
7. Technics SL-1200
8. Nakamichi Dragon

---

### 6. Facebook Marketplace Scraper
**Actor ID:** apify~facebook-marketplace-scraper  
**Status:** ✓ WORKING  
**Cost:** ~$0.12-0.16/run (6-8 searches)  
**Data Collected:** 639 unique Athens/Atlanta listings

**What It Does:**
- Searches Facebook Marketplace by location
- Athens, GA + Atlanta, GA focus
- Vintage audio searches
- Deduplicates by listing URL
- Auto-adds top 10 to lead_intake.csv

**Scripts:**
- `scripts/facebook_marketplace_run_001.py` (6 searches)
- `scripts/facebook_marketplace_run_002.py` (8 searches, better filtering)

**Output:**
- `data/external_leads/facebook_marketplace_leads.csv` (639 items)
- `data/external_leads/facebook_marketplace_raw_run_001.json`

**Search Terms (Best First List):**
**Athens:**
1. vintage stereo
2. vintage receiver
3. Technics SL-1200
4. McIntosh amplifier

**Atlanta:**
5. vintage stereo
6. Technics SL-1200
7. McIntosh amplifier
8. Marantz receiver

**Improvements in v2:**
- Min price filter ($50+) to skip parts
- Keyword filtering (excludes "parts", "repair", "broken")
- Better quality candidates

---

## ⏳ READY TO TEST (WHEN APIFY RESETS)

### 7. eBay Sold Comps Scraper ⭐⭐⭐ HIGH PRIORITY
**Actor ID:** oTtB3VgfuE9GtxQt2  
**Status:** Ready to test  
**Cost:** ~$0.05-0.10 (test)  
**Priority:** HIGHEST VALUE

**What It Will Do:**
- Get ACTUAL sold prices (not asking prices)
- Last 30 days of completed sales
- Calculate median/average/range
- Validate margins with REAL data
- Eliminate manual eBay sold searches

**Why Critical:**
- Currently all leads marked NEEDS_MANUAL_SOLD_COMPS
- Manual sold search takes 3-5 minutes per lead
- This automates it in seconds
- Highest ROI: saves 2-4 hours/week

**Script:** `scripts/ebay_sold_comps_test.py`

**Test Config:**
- 2 models (Technics SL-1200, McIntosh MA 6100)
- 10 sold items per model
- Max cost: $0.05

**Integration Plan:**
Will plug directly into `manual_lead_review.py`:
```python
# Auto-run for every lead
sold_data = get_ebay_sold_comps(model)
asking_price = 600
median_sold = sold_data['median_price']  # e.g., $950

margin = median_sold - asking_price  # $350
if margin > 200:
    flag = "EXCELLENT_MARGIN"
```

---

### 8. Reverb.com Scraper ⭐⭐ MEDIUM PRIORITY
**Actor ID:** RenntKrxUtdZQl1jH  
**Status:** Ready to test  
**Cost:** ~$0.06-0.10 (test)  
**Priority:** MEDIUM

**What It Will Do:**
- Search Reverb.com (music equipment marketplace)
- Vintage synths, turntables, tape decks
- Nationwide searches
- Expand beyond local markets

**Script:** `scripts/reverb_test_limited.py`

**Test Keywords (Conservative):**
1. Technics SL-1200
2. Nakamichi Dragon
3. Moog synthesizer

**Full Keyword List (Production):**
1. Technics SL-1200
2. Technics SL-1200MK2
3. Nakamichi Dragon
4. Nakamichi cassette deck
5. Tascam cassette deck
6. TEAC reel to reel
7. Revox reel to reel
8. vintage synthesizer
9. Roland Juno
10. Moog synthesizer
11. Fender Rhodes

**Test Config:**
- 3 keywords × 10 items = 30 items max
- Max cost: $0.10

---

### 9. AI Scraper (Natural Language) ⭐ LOW PRIORITY
**Actor ID:** paOtbjvyUiNsr1Qms  
**Status:** Ready to test  
**Cost:** ~$0.05-0.10 (single page test)  
**Priority:** LOW (experimental)

**What It Will Do:**
- Use AI to extract data from any page
- No CSS selectors needed
- Describe what you want in plain English
- Handles complex/dynamic layouts

**Potential Use Cases:**
1. Audiogon listings (premium marketplace)
2. Complex Craigslist posts
3. Sites without dedicated actors

**Script:** `scripts/ai_scraper_test.py`

**Test Config:**
- Single page: Audiogon solid-state category
- Prompt: "Extract all vintage audio listings with title, price, condition, URL"
- Max cost: $0.05

**Decision Factors:**
- Cost per page vs manual effort
- Accuracy vs dedicated scrapers
- Speed vs Browse API

---

## ❌ TESTED & DIDN'T WORK

### 10. eBay Active Listings Scraper #1
**Actor ID:** PBSxkfoBWghbE2set  
**Status:** ❌ REQUIRES PAID RENTAL  
**Test Date:** 2026-05-04

**What Happened:**
```json
{
  "error": {
    "type": "actor-is-not-rented",
    "message": "You must rent a paid Actor"
  }
}
```

**Why It Doesn't Matter:**
- We already have eBay Browse API (FREE)
- This would cost rental fee + usage
- No advantage over Browse API

**Decision:** SKIP - not worth paying when free alternative exists

---

### 11. eBay Active Listings Scraper #2
**Actor ID:** 8bXnzCF4JVgMMA5cM  
**Status:** ❌ RETURNED 0 ITEMS  
**Test Date:** 2026-05-04

**What Happened:**
- Ran successfully (201 status)
- Returned empty array: `[]`
- No items extracted

**Test Input:**
```json
{
  "listingUrls": [
    "https://www.ebay.com/sch/i.html?_nkw=technics+sl-1200"
  ]
}
```

**Why It Doesn't Work:**
- Doesn't handle general search URLs
- May be designed for specific listing pages only
- Not useful for our use case

**Decision:** SKIP - doesn't work for market searches

---

## 📊 DATA SUMMARY

### Collected So Far
| Source | Items | Status |
|--------|-------|--------|
| Mercari | 142 | ✓ Collected |
| Facebook Marketplace | 639 | ✓ Collected |
| **Total** | **781** | **Ready for review** |

### In Lead Intake Queue
- 20+ leads added to `lead_intake.csv`
- Status: Unreviewed
- Ready for: `python3 manual_lead_review.py`

---

## 🔧 SUPPORTING SYSTEMS

### Craigslist RSS Feeds
**Status:** Mentioned in docs (MANUAL_ALERT_SETUP.md)  
**Type:** RSS/email alerts  
**Cost:** FREE  
**Coverage:** Athens, Atlanta, Augusta, etc.

**Not automated scraping, but:**
- Email notifications for new posts
- Manual follow-up required
- Documented setup process

---

### File Cleanup System
**Script:** `ebay_cleanup_temp.py`  
**What It Does:**
- Auto-deletes temporary files older than 7 days
- Keeps workspace clean
- Runs periodically

---

### Validation Runs
**Script:** `scripts/run_lead_validation.sh`  
**Report:** `reports/LEAD_VALIDATION_RUN_001.md`

**What It Did:**
- Baseline test of 12 target models
- Validated eBay Browse API works for each
- Established price floor effectiveness
- Tested false-positive filtering

---

## 📋 COMPLIANCE & DATA RULES

### What We Store
✓ Item titles  
✓ Prices  
✓ Listing URLs  
✓ Photo URLs  
✓ Locations  
✓ Conditions  
✓ Source platforms  
✓ Scraped timestamps  

### What We DON'T Store
❌ Seller names  
❌ Seller IDs  
❌ Messages  
❌ Personal data  
❌ Buyer information  
❌ Order details  

### Markings on All Data
- MERCARI_ACTIVE_CONTEXT_ONLY
- FACEBOOK_ACTIVE_CONTEXT_ONLY
- NEEDS_MANUAL_REVIEW
- NEEDS_MANUAL_SOLD_COMPS
- NOT_SOLD_COMPS (for active listings)

---

## 💰 COST BREAKDOWN

### Current Costs (Working Systems)
| System | Cost |
|--------|------|
| eBay Browse API | FREE |
| Lead Review Script | FREE |
| Mercari Scraper | $0.12/run |
| Facebook Scraper | $0.12-0.16/run |
| Craigslist RSS | FREE |

### Test Costs (When Reset)
| Test | Estimated Cost |
|------|---------------|
| eBay Sold Comps | $0.05 |
| Reverb Scraper | $0.10 |
| AI Scraper | $0.10 |
| **Total Tests** | **$0.25** |

### Production Costs (Projected)
**Daily Runs:**
- Facebook: $0.16/day
- Mercari: $0.12/day (every other day)
- eBay Sold Comps: $0.10/day (5 leads)
- **Total:** ~$3-4/month (fits free tier)

**Weekly Runs:**
- Facebook: $0.32/week
- Mercari: $0.12/week
- Reverb: $0.10/week
- eBay Sold Comps: as needed
- **Total:** ~$2/month (comfortably under free tier)

---

## 🎯 INTEGRATION ROADMAP

### Phase 1: ✅ COMPLETE
- [x] eBay Browse API integration
- [x] Lead intake system
- [x] Manual lead review with eBay context
- [x] False-positive filtering
- [x] Price floor validation
- [x] Mercari scraper
- [x] Facebook Marketplace scraper

### Phase 2: ⏳ BLOCKED (APIFY LIMIT)
- [ ] Test eBay Sold Comps (HIGH PRIORITY)
- [ ] Test Reverb scraper (MEDIUM)
- [ ] Test AI scraper (LOW)

### Phase 3: 🔮 FUTURE
- [ ] Integrate sold comps into lead review
- [ ] Automated daily runs
- [ ] Expand to more markets (Augusta, Macon, etc.)
- [ ] Add Audiogon scraping (if AI scraper works)
- [ ] Build profit tracking system

---

## 📂 FILE STRUCTURE

```
~/.openclaw/workspace/

Core Scripts:
  ebay_active_context.py              ✓ Active listings (FREE API)
  manual_lead_review.py               ✓ Lead underwriting
  ebay_cleanup_temp.py                ✓ File cleanup
  target_models.txt                   ✓ Model list

Apify Integration Scripts:
  scripts/
    mercari_production_run_001.py     ✓ Mercari scraper
    facebook_marketplace_run_001.py   ✓ FB Marketplace
    facebook_marketplace_run_002.py   ✓ FB Marketplace v2
    ebay_sold_comps_test.py           ⏳ Sold comps (ready)
    reverb_test_limited.py            ⏳ Reverb (ready)
    ai_scraper_test.py                ⏳ AI scraper (ready)
    ebay_active_scraper_test.py       ❌ Requires rental
    ebay_active_minimal_test.py       ❌ Requires rental
    ebay_active_listing_urls_test.py  ❌ Returns 0 items

Data:
  lead_intake.csv                     ✓ Lead queue (20+ leads)
  
  data/external_leads/
    mercari_leads.csv                 ✓ 142 items
    mercari_raw_run_001.json
    facebook_marketplace_leads.csv    ✓ 639 items
    facebook_marketplace_raw_run_001.json

  data/ebay_active_search/
    [model]_production_[timestamp].json  ✓ eBay searches

Reports:
  reports/
    lead_XXXX_review.md               ✓ Underwriting reports
    LEAD_VALIDATION_RUN_001.md        ✓ Baseline validation
    MERCARI_APIFY_RUN_001.md          ✓ Mercari results
    FACEBOOK_MARKETPLACE_RUN_001_COMPLETE.md  ✓ FB results
    APIFY_INTEGRATION_SUMMARY.md      ✓ Integration status
    APIFY_LIMIT_EXCEEDED.md           ✓ Current blocker
    EBAY_ACTIVE_VS_SOLD_CLARIFICATION.md  ✓ Active/sold explained

Docs:
  docs/
    BEST_FIRST_SEARCH_STRATEGY.md     ✓ Search optimization
    EBAY_SOLD_COMPS_INTEGRATION.md    ✓ Sold comps plan
    AI_SCRAPER_INTEGRATION.md         ✓ AI scraper plan
    EBAY_ACTIVE_SCRAPER.md            ✓ Active scraper docs
    APIFY_TESTING_PRIORITY.md         ✓ Test priority order
    MANUAL_ALERT_SETUP.md             ✓ Craigslist/FB manual
    APIFY_MERCARI_INTEGRATION.md      ✓ Mercari setup

Credentials:
  credentials/
    ebay-production.json              ✓ eBay API credentials
    ebay-sandbox.json                 ✓ eBay test credentials
```

---

## 🚀 QUICK COMMANDS

### See Active Listings Now
```bash
python3 ebay_active_context.py
```

### Review Collected Leads
```bash
python3 manual_lead_review.py
```

### Check What We Have
```bash
wc -l lead_intake.csv
wc -l data/external_leads/*.csv
ls reports/lead_*_review.md
```

### When Apify Resets
```bash
# Test sold comps FIRST (highest value)
export APIFY_TOKEN='your-token'
python3 scripts/ebay_sold_comps_test.py

# Then Reverb
python3 scripts/reverb_test_limited.py

# Then AI scraper (if budget)
python3 scripts/ai_scraper_test.py
```

---

## 📊 CURRENT STATUS

### Working Right Now
✅ eBay Browse API (active listings - FREE)  
✅ Lead intake system  
✅ Lead underwriting with eBay context  
✅ Mercari scraper (142 items collected)  
✅ Facebook Marketplace (639 items collected)  
✅ 781 total leads ready for review  

### Blocked
⛔ Apify monthly limit exceeded (~$0.74 used of $5 free tier)  
⏳ 3 high-value actors ready to test when limit resets  

### Failed/Skipped
❌ 2 eBay active listing actors (one requires rental, one returns 0 items)  
✓ But we don't need them - Browse API works fine  

---

## 🎯 NEXT ACTIONS

### Immediate (No Apify Needed)
1. Run `python3 manual_lead_review.py` on 781 collected leads
2. Review generated underwriting reports
3. Evaluate lead quality
4. Decide which leads to pursue

### When Apify Resets
1. **Test eBay Sold Comps first** (highest ROI)
2. If good: integrate into lead review immediately
3. Test Reverb second (expand sources)
4. Test AI scraper last (experimental)

### Long Term
- Set up automated daily/weekly runs
- Expand to more markets
- Build profit tracking
- Scale based on lead quality

---

**System Status:** Operational  
**Integrations Working:** 4 (eBay API, Mercari, Facebook, Lead Review)  
**Integrations Ready:** 3 (Sold Comps, Reverb, AI Scraper)  
**Total Leads Collected:** 781  
**Awaiting:** Apify limit reset for high-value sold comps integration
