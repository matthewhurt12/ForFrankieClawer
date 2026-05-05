# Apify Mercari Integration - Test Results

**Date:** 2026-05-04  
**Status:** ACTOR RUNS BUT RETURNS ZERO ITEMS  
**Actor:** stealth_mode/mercari-product-search-scraper

---

## Test Summary

### What We Tested

✓ Apify API authentication - **WORKING**  
✓ Actor execution - **WORKING**  
✓ Run completion - **WORKING**  
✗ Data extraction - **RETURNS ZERO ITEMS**

### Test Results

**Sync API Test:**
```
Status: 201 Created
Items Returned: 0
Query: "iphone" (very common search term)
```

**Async API Test:**
```
Run Status: SUCCEEDED
Dataset Created: Yes
Items in Dataset: 0
```

---

## Issue Analysis

### Actor Runs Successfully But Returns No Data

**Observations:**
1. Actor accepts input and runs without errors
2. Run completes with `SUCCEEDED` status
3. Dataset is created but contains 0 items
4. Same result for multiple different search terms

**Possible Causes:**

1. **Incorrect Input Format**
   - Actor may expect different input structure
   - `startUrls` format might be wrong
   - May need specific parameters we're not providing

2. **Actor Configuration Issue**
   - Actor might be outdated or broken
   - May require specific proxy settings
   - Could need additional authentication

3. **Mercari Changes**
   - Mercari website structure may have changed
   - Actor selectors might be outdated
   - Site may be blocking scraping

---

## Alternative Approaches

### Option 1: Try Different Apify Mercari Actors

Search Apify Store for other Mercari scrapers:
- `apify/mercari-scraper`
- Other community Mercari actors
- Verified/official actors preferred

### Option 2: Build Custom Mercari Scraper

Use proven approach:
1. Manual browser (Chrome)
2. OS-level screenshots (VISUAL_BROWSER_TEST_004)
3. OCR extraction
4. Works but requires manual control

### Option 3: Use Existing Working Tools

**What's Already Working:**
- ✓ Craigslist RSS feeds
- ✓ eBay Browse API
- ✓ Manual Facebook Marketplace searches

**Recommendation:** Focus on these proven methods

---

## Cost Analysis

### Apify Costs Incurred

**Test Runs:**
- 9 actor runs (8 vintage audio + 1 iPhone test)
- Status: All SUCCEEDED
- Cost: ~$0.05-0.10 (estimated)

**Free Tier Status:**
- $5 monthly credit available
- Minimal usage so far
- Still have budget for more tests

---

## Next Steps

### Immediate Actions

**1. Check Actor Documentation**
Visit: https://apify.com/stealth_mode/mercari-product-search-scraper
- Review input schema
- Check example runs
- Look for known issues

**2. Contact Actor Developer**
- Report zero results issue
- Request updated documentation
- Ask for example working configuration

**3. Try Alternative Actors**
Search Apify Store:
```
"mercari scraper"
"mercari product"
"mercari search"
```

### If Actor Can't Be Fixed

**Recommended: Stick With Working Methods**

1. **Craigslist RSS Feeds**
   - Status: Working
   - Setup: Complete
   - Cost: Free
   - Effort: Low

2. **eBay Browse API**
   - Status: Working
   - Integration: Complete
   - Cost: Free
   - Effort: None

3. **Manual Searches**
   - Facebook Marketplace (when logged in)
   - Mercari (manual browsing)
   - Estate sales
   - Status: Always works
   - Cost: Free
   - Effort: 10 min/day

---

## Technical Details

### API Endpoints Tested

**Sync Run:**
```
POST https://api.apify.com/v2/acts/stealth_mode~mercari-product-search-scraper/run-sync-get-dataset-items
Response: 201 Created
Body: []
```

**Async Run:**
```
POST https://api.apify.com/v2/acts/stealth_mode~mercari-product-search-scraper/runs
Status: SUCCEEDED
Dataset Items: 0
```

### Input Format Used

```json
{
  "startUrls": [
    {"url": "https://www.mercari.com/search/?keyword=iphone"}
  ],
  "maxItems": 10,
  "proxy": {
    "useApifyProxy": true
  }
}
```

---

## Files Created

```
scripts/
  mercari_apify_scraper.py        # Main script (ready but returns 0 items)
  test_apify_mercari.py           # Debug test (sync)
  test_apify_async.py             # Debug test (async)

docs/
  APIFY_MERCARI_INTEGRATION.md    # Full documentation

reports/
  APIFY_MERCARI_READY.md          # Quick start guide
  APIFY_MERCARI_TEST_RESULTS.md   # This report
```

---

## Recommendation

### Short Term (This Week)

**DO:**
- ✓ Continue using Craigslist RSS
- ✓ Continue using eBay API
- ✓ Manual Facebook/Mercari searches

**DON'T:**
- ❌ Spend more time debugging this actor
- ❌ Try to build custom Mercari automation

### Medium Term (This Month)

**IF** you find working Apify Mercari actor:
- Test with our integration script
- Add to daily workflow

**IF NOT:**
- Focus on proven methods
- Mercari manual searches sufficient

---

## Verdict

**Apify Integration:** ⚠️ **ON HOLD**  
**Reason:** Actor returns zero items despite successful runs  
**Action:** Use existing working tools instead

**Working Tools:**
1. ✓ Craigslist RSS feeds
2. ✓ eBay Browse API
3. ✓ Manual searches

These three methods provide sufficient lead volume without the complexity of fixing a broken Apify actor.

---

**Test Date:** 2026-05-04  
**Apify Token:** Configured and working  
**API Access:** Verified  
**Actor Status:** Runs but returns no data  
**Next Action:** Continue with proven methods
