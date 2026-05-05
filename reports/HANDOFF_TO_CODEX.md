# Handoff to Codex - Vintage Audio Arbitrage System

**Date:** 2026-05-04  
**Status:** Functional MVP with data collection and analysis  
**Next Owner:** Codex / GitHub repository

---

## 🎯 PROJECT PURPOSE

Automated lead generation and underwriting system for vintage audio equipment flipping.

**Goal:** Find underpriced vintage audio on Mercari, Facebook Marketplace, and other platforms. Use eBay sold comps to validate resale value. Generate actionable investigation reports.

**Not Goal:** Make automatic buy decisions. System outputs INVESTIGATE / WATCH / SKIP recommendations only.

---

## 🏗️ ARCHITECTURE

**Layer 1: Data Collection (Apify)**
- Apify actors scrape marketplaces
- Return structured JSON datasets
- Cost-controlled with strict limits

**Layer 2: Normalization (Python)**
- Parse Apify output
- Deduplicate listings
- Filter false positives (parts, apparel, accessories)
- Classify equipment types

**Layer 3: Analysis (Python + eBay API)**
- eBay Browse API for active listing context (FREE)
- eBay sold comps for actual resale validation (planned)
- Calculate margins with fees + shipping
- Risk assessment

**Layer 4: Output (Markdown Reports)**
- No large lead lists
- Only actionable top 5-10 leads
- Seller message templates included
- Photo verification queues

---

## ✅ CURRENTLY WORKING SCRIPTS

### Data Collection (Apify)
**`scripts/mercari_production_run_001.py`**
- Scrapes Mercari nationwide
- 8 target model searches
- Requires `useApifyProxy: true`
- Cost: ~$0.12/run
- Output: `data/external_leads/mercari_leads.csv`

**`scripts/facebook_marketplace_run_002.py`**
- Scrapes Facebook Marketplace Athens/Atlanta
- 8 vintage audio searches (broad + specific)
- Min price filter ($50+)
- Excludes parts/repair keywords
- Cost: ~$0.16/run
- Output: `data/external_leads/facebook_marketplace_leads.csv`

### eBay Context (FREE API)
**`ebay_active_context.py`**
- eBay Browse API (official, free)
- Get active listing prices for specific models
- Price floors by category
- False-positive filtering built-in
- Credentials: `credentials/ebay-production.json`

### Lead Analysis
**`scripts/equipment_only_analysis.py`**
- Filters raw leads to equipment only
- Removes apparel, parts, accessories, manuals
- Classification: FULL_EQUIPMENT, LIKELY_EQUIPMENT, etc.
- Scores by opportunity (price vs expected value)
- Output: `reports/EQUIPMENT_ONLY_LEAD_REVIEW_001.md`

**`scripts/photo_verification_queue.py`**
- Classifies leads by missing information
- Categories: NEEDS_PHOTO_CHECK, NEEDS_EXACT_MODEL, NEEDS_SOLD_COMPS
- No profit estimates until model confirmed
- Seller question templates
- Output: `reports/PHOTO_VERIFICATION_QUEUE_001.md`

### Lead Intake
**`manual_lead_review.py`**
- Processes `lead_intake.csv`
- Runs eBay context for each lead
- Generates underwriting reports
- Output: `reports/lead_XXXX_review.md`

---

## 🤖 APIFY ACTORS INTEGRATED

### Working (Tested & Deployed)
1. **Mercari Scraper**
   - Actor: `stealth_mode~mercari-product-search-scraper`
   - Status: ✓ Working
   - Requires Apify proxies
   - Data: 142 items collected

2. **Facebook Marketplace Scraper**
   - Actor: `apify~facebook-marketplace-scraper`
   - Status: ✓ Working
   - Data: 639 items collected

### Ready to Test (When Apify Limit Resets)
3. **eBay Sold Comps** ⭐⭐⭐ HIGH PRIORITY
   - Actor: `oTtB3VgfuE9GtxQt2`
   - Script: `scripts/ebay_sold_comps_test.py`
   - Purpose: Get REAL sold prices for margin validation
   - WHY CRITICAL: Eliminates manual sold comp searches (saves 3-5 min/lead)

4. **Reverb Scraper**
   - Actor: `RenntKrxUtdZQl1jH`
   - Script: `scripts/reverb_test_limited.py`
   - Purpose: Music equipment marketplace

5. **AI Scraper**
   - Actor: `paOtbjvyUiNsr1Qms`
   - Script: `scripts/ai_scraper_test.py`
   - Purpose: Scrape any page with natural language prompts

### Skipped (Tested, Don't Work)
- eBay Active Listings actors (2) - one requires rental, one returns 0 items
- We use free eBay Browse API instead

---

## 📁 FILE STRUCTURE

```
~/.openclaw/workspace/

Core Scripts:
  ebay_active_context.py              ✓ Active listings (FREE API)
  manual_lead_review.py               ✓ Lead underwriting
  lead_intake.csv                     ✓ Lead queue
  target_models.txt                   ✓ Model list

Apify Integration:
  scripts/
    mercari_production_run_001.py     ✓ Mercari scraper
    facebook_marketplace_run_002.py   ✓ FB Marketplace (best version)
    ebay_sold_comps_test.py           ⏳ Ready to test
    reverb_test_limited.py            ⏳ Ready to test
    ai_scraper_test.py                ⏳ Ready to test
    
    equipment_only_analysis.py        ✓ Filter equipment from junk
    photo_verification_queue.py       ✓ Classify by missing info
    deal_desk_review.py               ⚠️ Needs improvement (see below)

Data:
  data/external_leads/
    mercari_leads.csv                 ✓ 142 items
    facebook_marketplace_leads.csv    ✓ 639 items
  
  data/ebay_active_search/
    [model]_production_[timestamp].csv  ✓ eBay searches

Reports:
  reports/
    APIFY_SYSTEM_SOURCE_OF_TRUTH.md   ✓ System overview
    EQUIPMENT_ONLY_LEAD_REVIEW_001.md ✓ Equipment filtering
    PHOTO_VERIFICATION_QUEUE_001.md   ✓ Lead classification
    
Documentation:
  docs/
    BEST_FIRST_SEARCH_STRATEGY.md     ✓ Search optimization
    EBAY_SOLD_COMPS_INTEGRATION.md    ✓ Sold comps plan
    APIFY_TESTING_PRIORITY.md         ✓ Test priority order

Credentials (NOT in git):
  credentials/
    ebay-production.json              ✓ eBay API credentials
    ebay-sandbox.json                 ✓ eBay test credentials
```

---

## 🚀 COMMANDS TO RUN

### Data Collection (When Apify Limit Resets)
```bash
# Set Apify token
export APIFY_TOKEN='your-token-here'

# Run Facebook Marketplace scraper
python3 scripts/facebook_marketplace_run_002.py

# Run Mercari scraper
python3 scripts/mercari_production_run_001.py
```

### Lead Analysis
```bash
# Filter equipment from junk
python3 scripts/equipment_only_analysis.py

# Classify by missing information
python3 scripts/photo_verification_queue.py

# Review specific lead
python3 manual_lead_review.py
```

### eBay Context
```bash
# Get active listings for model
python3 ebay_active_context.py "pioneer sx-1050"
```

### When Sold Comps Actor is Available
```bash
# Test eBay sold comps
python3 scripts/ebay_sold_comps_test.py

# Then integrate into manual_lead_review.py
```

---

## ⚠️ CURRENT PROBLEMS

### 1. Deal Desk Review is Not Actionable
**File:** `scripts/deal_desk_review.py`

**Problem:**
- Uses broad eBay searches like "Pioneer receiver" 
- Returns median of ALL Pioneer receivers ($549)
- Estimates profit on a $25 generic Pioneer = $450+ (wrong!)
- A $25 Pioneer SX-312 ≠ $549 resale value

**Why It Fails:**
- No exact model verification
- Treats all Pioneers/Marantz/etc as equal value
- Tuners/tape decks classified as receivers
- No sold comp validation

**Current Workaround:**
- `photo_verification_queue.py` classifies leads properly
- NO profit estimates until model confirmed
- Forces manual verification before any action

### 2. No Automated Sold Comp Integration
**Missing:** eBay Sold Comps actor integration

**Impact:**
- Every lead marked NEEDS_MANUAL_SOLD_COMPS
- Manual eBay sold search takes 3-5 minutes per lead
- Cannot validate margins automatically

**Solution:** Test `scripts/ebay_sold_comps_test.py` when Apify resets

### 3. Lead Scoring Still Needs Work
**Current Scoring Issues:**
- Price-based only (low price = high score)
- Doesn't factor in model rarity
- Doesn't weight local vs shipping
- Doesn't account for working/tested status enough

**Better Scoring Would Consider:**
- Target model bonus (SX-1250 > SX-650)
- Local pickup bonus (Facebook > Mercari)
- Working condition bonus ("tested" in title)
- Sold comp availability (known models > generic)
- Brand premium (McIntosh > Sony)

---

## 🎯 NEXT DESIRED TASK

**Improve Lead Scoring and Deal Desk Review**

### Requirements:
1. **Model-Specific Scoring**
   - Different score multipliers per target model
   - Pioneer SX-1250 = 2.0x
   - Pioneer SX-650 = 1.2x
   - Generic Pioneer = 0.5x

2. **Working Condition Weight**
   - "working" or "tested" in title = 1.5x
   - "serviced" or "recapped" = 2.0x
   - No mention of condition = 0.8x
   - "as-is" or "repair" = 0.3x

3. **Sold Comp Availability**
   - Known target model with active comps = 1.5x
   - Generic model with few comps = 0.5x
   - Unknown model = skip entirely

4. **Location Bonus**
   - Facebook Marketplace (local) = 1.3x
   - Mercari (shipping required) = 1.0x
   - Heavy item (receiver/amp) + shipping = 0.7x

5. **Photo Quality Indicator**
   - Multiple clear photos = 1.2x
   - Stock photo or unclear = 0.8x
   - No photos = 0.5x

6. **Final Score Formula**
```python
base_score = (price_floor - asking_price) / price_floor * 100

final_score = base_score * model_multiplier * condition_weight 
              * comp_availability * location_bonus * photo_quality

if final_score > 100: "INVESTIGATE"
elif final_score > 50: "WATCH"
else: "SKIP"
```

7. **Deal Desk Output**
   - Top 5 leads only
   - Each must have:
     - Exact model (not "Pioneer receiver")
     - Estimated resale from THAT MODEL's sold comps
     - Realistic risk assessment
     - Max buy price calculated
     - Seller message template
   - No profit estimate without sold comps

### Acceptance Criteria:
- ✓ No more "$450 profit" on generic $25 receivers
- ✓ Exact model required before profit calculation
- ✓ Sold comps used for resale value (not active listings)
- ✓ Risk factors clearly stated
- ✓ Only show leads worth actual investigation

---

## 💰 COST LIMITS

**Apify Free Tier:** $5/month

**Current Usage:** ~$0.74 (limit exceeded)

**Recommended Schedule (When Reset):**
- Facebook Marketplace: 2x/week ($0.32/week)
- Mercari: 1x/week ($0.12/week)
- eBay Sold Comps: As needed ($0.10-0.30/week)
- **Total:** ~$2-3/month (fits free tier)

---

## 🛡️ DATA PRIVACY RULES

**What We Store:**
✓ Item titles, prices, URLs, photos, locations, conditions

**What We DON'T Store:**
❌ Seller names, seller IDs, messages, personal contact info

**All Data Marked:**
- `[SOURCE]_ACTIVE_CONTEXT_ONLY`
- `NEEDS_MANUAL_REVIEW`
- `NEEDS_MANUAL_SOLD_COMPS`

---

## 🔐 CREDENTIALS & SETUP

### eBay API (Required)
1. Get credentials from eBay Developer Portal
2. Store in `credentials/ebay-production.json`
3. Format:
```json
{
  "app_id": "your-app-id",
  "cert_id": "your-cert-id",
  "dev_id": "your-dev-id"
}
```

### Apify (Required for Scraping)
1. Sign up at apify.com
2. Get API token from account settings
3. Set environment variable:
```bash
export APIFY_TOKEN='apify_api_...'
```

**DO NOT commit credentials to git**

---

## 📋 TESTING CHECKLIST

### When Apify Limit Resets:
- [ ] Test eBay Sold Comps actor (HIGH PRIORITY)
- [ ] Validate sold comp data quality
- [ ] Integrate into manual_lead_review.py
- [ ] Test Reverb scraper (MEDIUM)
- [ ] Test AI scraper (LOW)

### Before Production Use:
- [ ] Verify false-positive filtering
- [ ] Test model identification accuracy
- [ ] Validate sold comp integration
- [ ] Improve lead scoring algorithm
- [ ] Generate deal desk review with real data

---

## 📚 KEY DOCUMENTATION

**System Overview:**
- `reports/APIFY_SYSTEM_SOURCE_OF_TRUTH.md` - Architecture & strategy

**Integration Guides:**
- `docs/EBAY_SOLD_COMPS_INTEGRATION.md` - Sold comps plan
- `docs/BEST_FIRST_SEARCH_STRATEGY.md` - Search optimization
- `docs/APIFY_TESTING_PRIORITY.md` - Test order

**Analysis Reports:**
- `reports/EQUIPMENT_ONLY_LEAD_REVIEW_001.md` - Equipment filtering
- `reports/PHOTO_VERIFICATION_QUEUE_001.md` - Lead classification

---

## ⚡ QUICK START

```bash
# 1. Clone repository
git clone [repository-url]
cd workspace

# 2. Set up credentials
mkdir -p credentials
# Add ebay-production.json

# 3. Set Apify token
export APIFY_TOKEN='your-token'

# 4. Run data collection
python3 scripts/facebook_marketplace_run_002.py

# 5. Analyze leads
python3 scripts/equipment_only_analysis.py
python3 scripts/photo_verification_queue.py

# 6. Review top leads
cat reports/PHOTO_VERIFICATION_QUEUE_001.md
```

---

## 🎓 LESSONS LEARNED

1. **Don't trust Apify actors blindly**
   - Test with minimal data first
   - Some actors require proxies
   - Some actors require rental
   - Some actors just don't work

2. **False positives are 50% of raw data**
   - T-shirts with model names
   - Enamel pins
   - Parts/switches/knobs
   - Manuals and catalogs
   - Must filter aggressively

3. **Active listings ≠ sold prices**
   - Asking $549 doesn't mean selling for $549
   - Need actual sold comps
   - eBay Browse API only shows active (asking) prices
   - Must use sold comps actor for real data

4. **Generic titles are useless**
   - "Pioneer Receiver" could be $50 or $800 model
   - Must get exact model before any estimate
   - Photo verification is critical

5. **Start tight, expand later**
   - Better to have 10 quality leads than 500 junk
   - Local pickup > shipping for heavy items
   - Working/tested > untested (obvious but critical)

---

## 🚨 CRITICAL WARNINGS

**DO NOT:**
- ❌ Commit API keys or credentials
- ❌ Commit raw data dumps (privacy + size)
- ❌ Estimate profit without sold comps
- ❌ Use broad eBay searches for resale value
- ❌ Call anything "BUY" from automated analysis
- ❌ Trust generic receiver = target model price

**DO:**
- ✓ Verify exact model before any action
- ✓ Use sold comps for resale validation
- ✓ Factor in fees ($123 = 13% of $950)
- ✓ Factor in shipping ($20-50 for receivers)
- ✓ Test equipment in person if local
- ✓ Output INVESTIGATE / WATCH / SKIP only

---

## 🔄 VERSION INFO

**Created:** 2026-05-04  
**Status:** Functional MVP  
**Python:** 3.10+  
**Platform:** Linux/WSL2  
**Dependencies:** requests, csv, json, subprocess  

**No external dependencies required** (uses standard library + eBay API)

---

## 🤝 HANDOFF NOTES

**Current State:**
- Data collection working (Mercari, Facebook)
- Basic filtering working (equipment vs junk)
- Lead classification working (photo queue)
- eBay active context working (free API)

**Needs Work:**
- Lead scoring algorithm (see NEXT DESIRED TASK above)
- Sold comp integration (actor ready, needs testing)
- Deal desk review (currently broken, needs rewrite)

**For Next Developer:**
Focus on improving lead scoring and integrating eBay sold comps. Everything else is functional. The scoring algorithm and deal desk are the weakest parts of the system right now.

**Questions?**
See `reports/APIFY_SYSTEM_SOURCE_OF_TRUTH.md` for full system overview.

---

**Ready for Codex/GitHub handoff.**
