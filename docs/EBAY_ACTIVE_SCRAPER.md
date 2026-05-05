# eBay Active Listings Scraper

**Actor ID:** PBSxkfoBWghbE2set  
**Type:** eBay active listings scraper (alternative to Browse API)  
**Status:** Prepared, DO NOT TEST YET  
**Priority:** LOW (we already have eBay Browse API working)

---

## What It Does

Scrapes active eBay listings from search result pages.

**Input:**
```json
{
  "startUrls": [
    {"url": "https://www.ebay.com/sch/i.html?_nkw=technics+sl-1200"}
  ],
  "maxItems": 10,
  "proxyConfig": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"],
    "apifyProxyCountry": "US"
  }
}
```

**Output:** Active eBay listings with titles, prices, conditions, etc.

---

## Why We Have This

### Backup for eBay Browse API

We already have **eBay Browse API** working:
- ✓ Free (no Apify credits)
- ✓ Fast
- ✓ Official eBay API
- ✓ Working in `ebay_active_context.py`

**This actor is a backup** in case:
- Browse API stops working
- Rate limits hit
- Need additional data fields
- Browse API access revoked

---

## When to Use

### Use eBay Browse API (Current)
✓ It's free  
✓ It's working  
✓ It's official  
✓ No credit usage  

### Use This Actor Only If
❌ Browse API breaks  
❌ Need data Browse API doesn't provide  
❌ Browse API rate limits become issue  

---

## Cost Comparison

### eBay Browse API
- **Cost:** $0 (free)
- **Rate Limit:** 5000 calls/day (free tier)
- **Current Usage:** ~5-20 calls/day
- **We're Fine:** Not hitting limits

### This Apify Actor
- **Cost:** ~$0.02-0.05 per search (estimated)
- **Rate Limit:** Depends on Apify plan
- **Monthly Cost:** $0.60-1.50 if used daily

**Verdict:** Stick with free Browse API unless it breaks.

---

## Test Plan (When Needed)

### Only Test If Browse API Fails

**Test:**
```bash
export APIFY_TOKEN='your-token'
python3 scripts/ebay_active_scraper_test.py --actually-run
```

**Note:** Script requires `--actually-run` flag (safety check).

**Validate:**
1. Compare data to Browse API results
2. Check if additional useful fields exist
3. Measure actual cost
4. Decide if worth switching

---

## Data Fields

### eBay Browse API Provides
✓ Title  
✓ Price  
✓ Condition  
✓ Item URL  
✓ Image URL  
✓ Seller info  
✓ Location  

### This Actor Might Add
? Bid count  
? Watchers count  
? Shipping cost details  
? Return policy  
? Item specifics  

**Unknown until tested.**

---

## Integration

### Current (Browse API)
```python
# In ebay_active_context.py
results = search_ebay(model_name)
# Free, fast, working
```

### If Switched to This Actor
```python
# Would need rewrite
results = apify_ebay_search(model_name)
# Costs credits, may have more data
```

**Decision:** Don't switch unless Browse API fails.

---

## Test Priority

### Priority Order (When Apify Resets)

1. **eBay Sold Comps** ⭐⭐⭐ (HIGH)
   - Automates manual work
   - High ROI
   - No free alternative

2. **Reverb Scraper** ⭐⭐ (MEDIUM)
   - New lead source
   - No free alternative
   - Worth testing

3. **AI Scraper** ⭐ (LOW)
   - Experimental
   - Expensive
   - Test if budget

4. **eBay Active Scraper** (SKIP)
   - Browse API already works
   - Free alternative exists
   - Only test if Browse API breaks

---

## Files

```
scripts/
  ebay_active_scraper_test.py      # Prepared, do not run yet

docs/
  EBAY_ACTIVE_SCRAPER.md           # This file
```

---

## Recommendation

**DO NOT TEST THIS YET**

Reasons:
1. eBay Browse API already working (free)
2. Apify limit already hit
3. Higher priority tests waiting (Sold Comps, Reverb)
4. This is a backup, not a replacement

**Test Only If:**
- Browse API stops working
- Need specific data fields Browse API lacks
- Have excess Apify budget after other tests

---

## Safety Feature

Script includes safety check:
```python
if "--actually-run" not in sys.argv:
    print("Exiting without running (safety check).")
    exit(0)
```

**Prevents accidental execution.**

To actually run (when needed):
```bash
python3 scripts/ebay_active_scraper_test.py --actually-run
```

---

**Status:** Prepared but not needed  
**Priority:** Skip unless Browse API fails  
**Recommendation:** Keep Browse API, save Apify credits for Sold Comps
