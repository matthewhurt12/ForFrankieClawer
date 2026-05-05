# AI Scraper Integration

**Actor ID:** paOtbjvyUiNsr1Qms  
**Type:** AI-powered web scraper with natural language prompts  
**Status:** Ready for testing (awaiting Apify limit reset)

---

## What It Does

This actor uses AI to extract structured data from web pages based on natural language prompts. Instead of writing selectors, you describe what you want in plain English.

**Example:**
```
"Extract all product listings with their prices, titles, and seller names"
```

The AI figures out how to extract that data from the page.

---

## Potential Use Cases

### 1. Audiogon Listings
**URL:** https://www.audiogon.com/listings/solid-state  
**Prompt:**
```
Extract all vintage audio equipment listings from this page.
For each listing, extract:
- Item title/name
- Price (if shown)
- Condition
- Seller location (if shown)
- Listing URL
```

**Why:** Audiogon is a premium vintage audio marketplace. Manual scraping would be complex, but AI can handle it.

### 2. Craigslist Posts (Alternative to RSS)
**URL:** https://athens.craigslist.org/search/sss?query=vintage+stereo  
**Prompt:**
```
Extract all listings. For each one get:
- Title
- Price
- Location
- Posted date
- URL
```

**Why:** More flexible than RSS, can extract additional fields.

### 3. eBay Completed Listings (For Sold Comps)
**URL:** eBay sold listings search  
**Prompt:**
```
Extract all completed/sold items with:
- Title
- Final sold price
- Sold date
- Condition
- Number of bids
```

**Why:** Could replace manual sold comp verification.

### 4. Reverb.com (If Direct Actor Fails)
**URL:** https://reverb.com/marketplace?query=technics+sl-1200  
**Prompt:**
```
Extract all items with price, condition, seller rating, and listing URL
```

**Why:** Backup if dedicated Reverb actor doesn't work.

---

## Test Configuration

### Ultra Conservative Test
**Script:** `scripts/ai_scraper_test.py`

**Limits:**
- Single page only
- Max cost: $0.05
- Timeout: 2 minutes
- Test URL: Audiogon solid-state category

**Why Conservative:**
- AI scraping may use more credits than regular scraping
- Unknown cost per page
- Testing one page first to measure cost

---

## Advantages

### vs Regular Scrapers
✓ No need to write CSS/XPath selectors  
✓ Handles site changes automatically (AI adapts)  
✓ Works on sites with complex/dynamic layouts  
✓ Can extract relationships ("seller name for this item")  

### vs Manual Searches
✓ Automated  
✓ Structured data output  
✓ Can process multiple pages  

---

## Disadvantages

### Cost
❌ May be more expensive than traditional scrapers  
❌ AI processing adds overhead  

### Accuracy
❌ AI may misinterpret page content  
❌ Requires result validation  

### Speed
❌ Slower than selector-based scraping  
❌ AI processing takes time  

---

## Integration Plan

### Phase 1: Single Page Test (Now)
1. Test on one Audiogon page
2. Measure cost per page
3. Validate extraction accuracy
4. Compare to manual effort

### Phase 2: Small Batch (If Phase 1 Succeeds)
1. Test 5-10 pages
2. Measure total cost
3. Check consistency across pages
4. Calculate cost/benefit

### Phase 3: Production (If Phase 2 Succeeds)
1. Create production script
2. Set up automated runs
3. Integrate with lead pipeline
4. Monitor cost vs value

---

## When to Use This Actor

### Good Use Cases
✓ Sites without dedicated Apify actors  
✓ Complex page layouts (tables, grids, cards)  
✓ Sites that change frequently  
✓ When you need flexible extraction  

### Bad Use Cases
❌ When a dedicated actor exists (use that instead)  
❌ Simple pages (overkill, use web_fetch)  
❌ Cost-sensitive situations  
❌ Speed-critical workflows  

---

## Cost Estimates

**Unknown until tested**, but expect:
- **Per Page:** $0.01-0.05 (AI processing)
- **Per Run (10 pages):** $0.10-0.50
- **Monthly (daily 10-page runs):** $3-15

**Compare to:**
- Regular scrapers: $0.001-0.01/page
- Manual searches: Free but time-intensive

---

## Alternative Prompts to Test

### Minimal Extraction
```
Extract: title, price, URL
```
**Why:** Less AI work = lower cost

### Rich Extraction
```
Extract all details including item title, brand, model number, 
year, condition description, price, shipping cost, seller name, 
seller rating, listing date, photos count, and item location
```
**Why:** Maximum information capture

### Filtered Extraction
```
Extract only items priced between $100-$1000, marked as 
"excellent" or "very good" condition, with title, price, and URL
```
**Why:** Pre-filter results before downloading

---

## Production Script (When Ready)

### Audiogon Daily Scraper
```python
# Target pages
PAGES = [
    "solid-state",    # Receivers/amps
    "turntables",     # Turntables
    "tuner",          # Tuners
    "tape",           # Tape decks
]

# For each category
for page in PAGES:
    url = f"https://www.audiogon.com/listings/{page}"
    # Run AI scraper with prompt
    # Save to data/external_leads/audiogon_leads.csv
```

**Estimated Cost:** $0.20-0.40/day = $6-12/month

---

## Testing Checklist

When Apify limit resets:

- [ ] Run single page test
- [ ] Check extraction accuracy (manual comparison)
- [ ] Measure actual cost
- [ ] Validate JSON structure
- [ ] Test with different page types
- [ ] Compare to manual extraction time
- [ ] Decide: worth it vs manual?

---

## Files

```
scripts/
  ai_scraper_test.py           # Ultra conservative test (1 page)

docs/
  AI_SCRAPER_INTEGRATION.md    # This file

data/test_outputs/
  ai_scraper_test.json         # Test results (when run)
```

---

## Recommendation

**Wait for Apify limit reset, then:**

1. Run single-page test on Audiogon
2. If cost < $0.05 and accuracy > 90%: Good
3. If cost > $0.10 or accuracy < 70%: Skip
4. Compare to manual search time (5 min = $0 cost)

**Use If:**
- Extracts 20+ quality leads per run
- Saves 15+ minutes manual search time
- Cost < $0.25/run

**Skip If:**
- Manual is faster
- Cost too high
- Accuracy too low
- Dedicated actors work better

---

**Status:** Awaiting test  
**Priority:** Low (test after core scrapers working)  
**Blocked By:** Apify monthly limit
