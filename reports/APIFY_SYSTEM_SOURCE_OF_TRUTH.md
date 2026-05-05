# Apify System - Source of Truth

**Date:** 2026-05-04  
**Version:** 2.0  
**Status:** Active

---

## 🎯 MISSION STATEMENT

Automated vintage audio lead generation and underwriting using Apify for data collection and OpenClaw for analysis.

**Goal:** Find underpriced vintage audio equipment, validate with real sold comps, generate actionable investigation reports.

**Not Goal:** Make buy decisions. Output is INVESTIGATE / WATCH / SKIP only.

---

## 🏗️ ARCHITECTURE

### Layer 1: Data Collection (Apify)
Apify actors scrape marketplaces and return structured datasets.

### Layer 2: Normalization (OpenClaw)
Python scripts normalize Apify output into standard CSV format.

### Layer 3: Analysis (OpenClaw)
- Deduplicate listings
- Filter false positives
- Check eBay active context
- Validate with sold comps
- Calculate margin potential

### Layer 4: Underwriting (OpenClaw)
Generate investigation reports with seller questions, risk factors, and recommendations.

**Output:** INVESTIGATE / WATCH / SKIP (never BUY)

---

## ✅ CURRENTLY WORKING ACTORS

### 1. Mercari Scraper
**Actor ID:** `stealth_mode~mercari-product-search-scraper`  
**Script:** `scripts/mercari_production_run_001.py`  
**Status:** ✓ WORKING  
**Cost:** ~$0.12 per run (8 searches × 50 items)  

**What It Does:**
- Searches Mercari nationwide for vintage audio
- 8 target models (McIntosh, Technics, Marantz, etc.)
- Returns: title, price, condition, URL, photo, shipping
- Deduplicates by item_id
- Adds top 10 candidates to lead_intake.csv

**Key Requirement:** Must use `useApifyProxy: true` to bypass bot detection

**Data Collected:** 142 items (run 001)  
**Output:** `data/external_leads/mercari_leads.csv`

---

### 2. Facebook Marketplace Scraper
**Actor ID:** `apify~facebook-marketplace-scraper`  
**Script:** `scripts/facebook_marketplace_run_002.py`  
**Status:** ✓ WORKING  
**Cost:** ~$0.16 per run (8 searches × 25 items)  

**What It Does:**
- Searches Facebook Marketplace Athens, GA + Atlanta, GA
- Broad terms (vintage stereo, vintage receiver) + specific models
- Returns: title, price, location, URL, photo
- Deduplicates by listing URL
- Filters: min $50, excludes "parts", "repair", "broken"
- Adds top 10 candidates to lead_intake.csv

**Search Terms:**
- Athens: vintage stereo, vintage receiver, Technics SL-1200, McIntosh amplifier
- Atlanta: vintage stereo, Technics SL-1200, McIntosh amplifier, Marantz receiver

**Data Collected:** 639 items (run 001)  
**Output:** `data/external_leads/facebook_marketplace_leads.csv`

---

## ⏳ READY TO TEST (AWAITING APIFY LIMIT RESET)

### 3. eBay Sold Comps Actor ⭐⭐⭐ HIGH PRIORITY
**Actor ID:** `oTtB3VgfuE9GtxQt2`  
**Script:** `scripts/ebay_sold_comps_test.py`  
**Status:** Ready to test  
**Cost:** ~$0.05 per test run  

**What It Will Do:**
- Get ACTUAL sold prices from eBay (not asking prices)
- Last 30 days of completed sales
- Returns: title, final price, sold date, condition, bids
- Calculate median/average/range for margin validation

**Why Critical:**
Currently every lead is marked NEEDS_MANUAL_SOLD_COMPS. This automates that validation step and eliminates 3-5 minutes of manual work per lead.

**Test Configuration:**
- 2 models (Technics SL-1200, McIntosh MA 6100)
- 10 sold items per model
- Max cost: $0.05

**Integration Plan:**
Will plug directly into `manual_lead_review.py` to auto-calculate real margins based on sold data, not asking prices.

---

### 4. Reverb Scraper ⭐⭐ MEDIUM PRIORITY
**Actor ID:** `RenntKrxUtdZQl1jH`  
**Script:** `scripts/reverb_test_limited.py`  
**Status:** Ready to test  
**Cost:** ~$0.10 per test run  

**What It Will Do:**
- Search Reverb.com (music equipment marketplace)
- Nationwide vintage audio/synth listings
- Target: turntables, tape decks, synths, keyboards

**Test Keywords:**
- Technics SL-1200
- Nakamichi Dragon
- Moog synthesizer

**Full Production Keywords (11 terms):**
Technics SL-1200, SL-1200MK2, Nakamichi Dragon, Nakamichi cassette deck, Tascam cassette deck, TEAC reel to reel, Revox reel to reel, vintage synthesizer, Roland Juno, Moog synthesizer, Fender Rhodes

**Test Configuration:**
- 3 keywords × 10 items = 30 max
- Max cost: $0.10

---

### 5. AI Scraper ⭐ LOW PRIORITY
**Actor ID:** `paOtbjvyUiNsr1Qms`  
**Script:** `scripts/ai_scraper_test.py`  
**Status:** Ready to test  
**Cost:** ~$0.05-0.10 per page  

**What It Will Do:**
- Use natural language prompts to extract data
- No CSS selectors needed
- Works on complex/dynamic pages
- Fallback for sites without dedicated actors

**Potential Use Cases:**
- Audiogon premium listings
- One-off marketplaces
- Complex Craigslist posts (if RSS insufficient)

**Test Configuration:**
- Single page: Audiogon solid-state category
- Prompt: "Extract all vintage audio listings with title, price, condition, URL"
- Max cost: $0.05

**Decision Criteria:**
Only use if cost per page < manual search time value and accuracy > 80%.

---

## ❌ ARCHIVED / IGNORE

### Old Approach (No Longer Used)
- ❌ Playwright browser automation
- ❌ OCR screen capture
- ❌ Direct scraping from Raspberry Pi
- ❌ Visual browser tests
- ❌ Craigslist RSS as primary strategy

**Why Archived:**
- Browser automation blocked by Cloudflare/bot detection
- OCR unreliable for structured data
- Apify handles scraping better with residential proxies
- Pi better suited for analysis, not scraping

**Status:** Scripts remain in repo for reference but are not part of active workflow.

---

### Failed Apify Actors (Tested, Don't Use)
**eBay Active Listings Actor #1:**
- Actor: PBSxkfoBWghbE2set
- Status: Requires paid rental (not free tier)
- Reason: We have free eBay Browse API, don't need this

**eBay Active Listings Actor #2:**
- Actor: 8bXnzCF4JVgMMA5cM
- Status: Returns 0 items
- Reason: Doesn't work for our search URLs

**Decision:** Ignore both. eBay Browse API (free, official) is sufficient for active listings.

---

## 📊 CURRENT DATA FLOW

```
┌─────────────────────┐
│   APIFY ACTORS      │
│  (Data Collection)  │
└──────────┬──────────┘
           │
           ├─► Mercari (142 items)
           ├─► Facebook Marketplace (639 items)
           └─► [Future: Reverb, eBay Sold Comps]
           │
           ▼
┌─────────────────────┐
│  NORMALIZATION      │
│  (Python Scripts)   │
└──────────┬──────────┘
           │
           ├─► Parse Apify JSON
           ├─► Convert to standard CSV
           ├─► Extract: title, price, URL, photo, location
           └─► Mark: NEEDS_MANUAL_REVIEW, NEEDS_MANUAL_SOLD_COMPS
           │
           ▼
┌─────────────────────┐
│  DEDUPLICATION      │
│  & FILTERING        │
└──────────┬──────────┘
           │
           ├─► Dedupe by item_id/URL
           ├─► Filter: min price ($50-500 depending on category)
           ├─► Exclude: "parts", "repair", "broken", "manual"
           └─► Sort by price (lowest first)
           │
           ▼
┌─────────────────────┐
│  LEAD INTAKE        │
│  lead_intake.csv    │
└──────────┬──────────┘
           │
           ├─► Add top 10 candidates per source
           ├─► Status: unreviewed
           └─► Manual additions allowed
           │
           ▼
┌─────────────────────┐
│  UNDERWRITING       │
│ manual_lead_review  │
└──────────┬──────────┘
           │
           ├─► Identify model from title
           ├─► Run eBay Browse API (active context)
           ├─► [Future: Run eBay Sold Comps]
           ├─► Calculate margin potential
           ├─► Generate seller questions
           └─► Flag risk factors
           │
           ▼
┌─────────────────────┐
│  OUTPUT REPORT      │
│ INVESTIGATE/WATCH/  │
│      SKIP           │
└─────────────────────┘
```

---

## 💰 COST LIMITS

### Per-Run Limits
| Actor | Max Items | Max Cost |
|-------|-----------|----------|
| Mercari | 50 per search | $0.15 |
| Facebook Marketplace | 25 per URL | $0.20 |
| eBay Sold Comps (test) | 10 per model | $0.10 |
| Reverb (test) | 10 per keyword | $0.15 |
| AI Scraper (test) | 1 page | $0.10 |

### Daily Budget
**Max:** $0.50 per day (automated runs)

**Breakdown:**
- Facebook Marketplace: $0.16
- Mercari (every other day): $0.06 average
- eBay Sold Comps (5 leads): $0.10
- Buffer: $0.18

**Monthly:** ~$15 if run daily, ~$5-8 if run 2-3x/week

### Free Tier Strategy
**Apify Free Tier:** $5/month

**Recommended Schedule:**
- Facebook Marketplace: 2x/week ($0.32/week = $1.28/month)
- Mercari: 1x/week ($0.12/week = $0.48/month)
- eBay Sold Comps: As needed ($0.10-0.30/week = $0.40-1.20/month)
- Reverb (if tested & good): 1x/week ($0.10/week = $0.40/month)

**Total:** $2.50-3.50/month (fits free tier)

---

## 🛡️ LEAD FILTERING RULES

### Price Floors by Category
- McIntosh amplifiers: $500 minimum
- Pioneer SX-series receivers: $400 minimum
- Marantz 2200/2300 series: $400 minimum
- Technics SL-1200: $300 minimum
- Sansui receivers: $400 minimum
- Nakamichi decks: $75 minimum

**Items below floor:** Flagged for manual review (may be parts/broken)

### Hard Exclusions (Keyword Filtering)
Exclude titles containing:
- "parts only", "for parts"
- "repair", "broken", "not working", "as-is"
- "manual", "service manual"
- "LED kit", "bulb", "lamp"
- "capacitor", "rebuild kit"
- "faceplate", "knob", "dial"
- "remote only", "cover only"

### Minimum Prices
- Mercari: $10 floor (skip free/very cheap items)
- Facebook: $50 floor (skip junk/parts)
- Reverb: $50 floor
- eBay context: $100 floor for receivers, $50 for accessories

---

## 📋 SOLD COMP RULES

### When to Run Sold Comps
✓ Every lead before marking INVESTIGATE  
✓ When asking price seems too good (verify it's real)  
✓ When unfamiliar model (establish market value)  
✓ Before any purchase decision  

### Never Skip Sold Comps
❌ Never call something a "deal" without sold comps  
❌ Never calculate margins from active listings only  
❌ Never recommend purchase without sold data  

### Sold Comp Analysis
**Minimum:** 5 sold items in last 30 days  
**Ideal:** 10+ sold items  

**Calculate:**
- Median sold price (most reliable)
- Average sold price
- Range (min to max)
- Sold frequency (demand indicator)

**Margin Calculation:**
```
Gross Margin = Median Sold Price - Asking Price - Estimated Fees - Estimated Shipping

eBay Fees: ~13% (10% final value + 3% payment)
Shipping: $20-50 (receivers), $15-30 (turntables)

Example:
  Asking: $600
  Median Sold: $950
  Fees: $950 × 0.13 = $123
  Shipping: $30
  Net: $950 - $600 - $123 - $30 = $197
  
  If Net > $200: INVESTIGATE
  If Net $100-200: WATCH
  If Net < $100: SKIP
```

---

## 🚦 OUTPUT DECISION RULES

### INVESTIGATE
✓ Net margin > $200 after fees/shipping  
✓ Sold comps show consistent demand (5+ sales/month)  
✓ Condition appears good from photos  
✓ Seller responsive to questions  
✓ Local pickup available (for heavy items)  

**Action:** Contact seller, ask detailed questions, request in-person inspection or more photos.

---

### WATCH
✓ Net margin $100-200  
✓ Some risk factors (untested, no returns)  
✓ Photos unclear  
✓ Seller unresponsive  
✓ Shipping required on heavy item  

**Action:** Monitor listing, wait for price drop or better photos. Set alert for similar items.

---

### SKIP
❌ Net margin < $100  
❌ Parts only, broken, or "as-is"  
❌ No sold comps (unknown market)  
❌ Overpriced vs sold data  
❌ Too many red flags  

**Action:** Move on. Time better spent on higher-quality leads.

---

### NEVER: BUY
❌ **Never output "BUY" as a recommendation**  
❌ **Never say "this is a good deal" without sold comps**  
❌ **Never calculate profit without fees/shipping**  

**Why:** Too many variables (condition, authenticity, functionality, shipping damage, return policies). Human must make final purchase decision after investigation.

---

## 🎯 NEXT 3 STEPS

### Step 1: Review Existing Leads
**Action:** Run `python3 manual_lead_review.py` on 781 collected leads  
**Purpose:** Generate underwriting reports for Mercari + Facebook data  
**Output:** `reports/lead_XXXX_review.md` for each candidate  
**Decision:** Evaluate lead quality before scaling  

**No Apify needed - use existing data**

---

### Step 2: Test eBay Sold Comps (When Apify Resets)
**Action:** Run `python3 scripts/ebay_sold_comps_test.py`  
**Purpose:** Validate sold comp automation works  
**Test:** 2 models × 10 sold items = $0.05 cost  
**Decision Criteria:**
- Returns accurate sold prices? ✓/✗
- Data includes date, condition, price? ✓/✗
- Cost < $0.10 for 20 items? ✓/✗

**If successful:** Integrate into `manual_lead_review.py` immediately

---

### Step 3: Decide Production Schedule
**Based on Step 1 results:**

**If lead quality is high (20%+ INVESTIGATE):**
- Run Facebook 2x/week
- Run Mercari 1x/week
- Use sold comps for all leads
- Expand to more markets (Augusta, Macon)

**If lead quality is medium (10-20% INVESTIGATE):**
- Run Facebook 1x/week
- Run Mercari biweekly
- Use sold comps for top candidates only
- Test Reverb integration

**If lead quality is low (<10% INVESTIGATE):**
- Run Facebook 2x/month
- Skip Mercari (too much noise)
- Focus on manual searches
- Don't scale Apify

---

## 📁 FILE STRUCTURE

### Core System
```
ebay_active_context.py              ✓ Active listings (FREE Browse API)
manual_lead_review.py               ✓ Lead underwriting
lead_intake.csv                     ✓ Lead queue (20+ entries)
target_models.txt                   ✓ Model list with price floors
```

### Apify Integration Scripts
```
scripts/
  mercari_production_run_001.py        ✓ Working
  facebook_marketplace_run_002.py      ✓ Working
  ebay_sold_comps_test.py              ⏳ Ready to test
  reverb_test_limited.py               ⏳ Ready to test
  ai_scraper_test.py                   ⏳ Ready to test
```

### Data
```
data/external_leads/
  mercari_leads.csv                 ✓ 142 items
  facebook_marketplace_leads.csv    ✓ 639 items
  
reports/
  lead_XXXX_review.md               ✓ Underwriting reports
  APIFY_SYSTEM_SOURCE_OF_TRUTH.md   ✓ This file
```

### Archived (Reference Only)
```
scripts/
  visual_browser_test*.py           ❌ Archived
  manual_screen_capture*.py         ❌ Archived
  simple_browser_test.sh            ❌ Archived
```

---

## 🔐 DATA PRIVACY RULES

### What We Store
✓ Item titles  
✓ Prices  
✓ Listing URLs  
✓ Photo URLs  
✓ General locations (city/state)  
✓ Item conditions  
✓ Source platform  

### What We DON'T Store
❌ Seller names  
❌ Seller IDs  
❌ Messages  
❌ Personal contact info  
❌ Buyer information  
❌ Account details  

### All Data Marked
- `[SOURCE]_ACTIVE_CONTEXT_ONLY` (e.g., MERCARI_ACTIVE_CONTEXT_ONLY)
- `NEEDS_MANUAL_REVIEW`
- `NEEDS_MANUAL_SOLD_COMPS`
- Auto-delete after 7 days (temporary test data)

---

## ✅ CURRENT STATUS

**Working:**
- 2 Apify actors (Mercari, Facebook)
- 781 leads collected
- Lead intake system operational
- eBay Browse API for active context

**Blocked:**
- Apify monthly limit exceeded (~$0.74 used of $5)
- 3 actors ready to test when reset

**Next Action:**
- Review 781 existing leads (no Apify needed)
- Wait for Apify reset
- Test eBay Sold Comps first when available

---

**Version:** 2.0  
**Last Updated:** 2026-05-04  
**Strategy:** Apify for data, OpenClaw for analysis  
**Output:** INVESTIGATE / WATCH / SKIP only (never BUY)
