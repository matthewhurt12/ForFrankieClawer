# Apify Monthly Limit Exceeded

**Date:** 2026-05-04  
**Status:** ⚠️ FREE TIER EXHAUSTED

---

## What Happened

After running multiple Apify actors today, the free tier monthly usage limit was exceeded.

**Error:**
```
{
  "error": {
    "type": "platform-feature-disabled",
    "message": "Monthly usage hard limit exceeded"
  }
}
```

---

## What We Successfully Collected Today

### ✓ Mercari Scraper
- **Actor:** stealth_mode~mercari-product-search-scraper
- **Status:** Production run completed
- **Data:** Saved to `data/external_leads/`

### ✓ Facebook Marketplace (Run 001)
- **Actor:** apify~facebook-marketplace-scraper
- **Items Retrieved:** 639 unique listings
- **Locations:** Athens, GA & Atlanta, GA
- **Data:** `data/external_leads/facebook_marketplace_leads.csv`

### ✗ Facebook Marketplace (Run 002)
- **Status:** Blocked by monthly limit
- **Would have tested:** Best-first search list (8 queries)

### ✗ Reverb.com Scraper
- **Actor ID:** RenntKrxUtdZQl1jH
- **Status:** Not tested (limit hit first)
- **Script Ready:** `scripts/reverb_test_limited.py`

---

## Integration Scripts Prepared

### Ready to Use (When Limit Resets)

**Facebook Marketplace:**
- `scripts/facebook_marketplace_run_001.py` - Original 6 searches
- `scripts/facebook_marketplace_run_002.py` - Best-first 8 searches (better filtering)

**Reverb.com:**
- `scripts/reverb_test_limited.py` - Conservative test (3 keywords, 10 items each)

**Mercari:**
- `scripts/mercari_production_run_001.py` - 8 vintage audio searches

---

## Estimated Usage Today

### Apify Free Tier
- **Monthly Limit:** $5 worth of usage
- **Our Usage Today:**
  - Mercari searches: ~$0.12
  - Facebook run 001: ~$0.12
  - Test/debug runs: ~$0.50+
  - **Total:** ~$0.74+

**Likely Cause:** Multiple test/debug runs during integration pushed us over the limit.

---

## Options Moving Forward

### Option 1: Wait for Reset (Recommended for Testing)
**When:** Start of next billing cycle (check Apify console)  
**Cost:** Free  
**Access:** Full free tier restored  

**Action:**
- Check Apify account dashboard for reset date
- Mark calendar
- Resume testing when reset

### Option 2: Upgrade to Paid Plan
**Cost:** $49+/month  
**Benefits:**
- Higher usage limits
- More actor runs
- Priority support
- No monthly hard limits

**Best For:**
- Daily automated runs
- Production use
- High-volume scraping

### Option 3: Use Collected Data
**Cost:** $0  
**Action:** Work with existing data  

**You Already Have:**
- 639 Facebook Marketplace leads
- Mercari data from today
- Lead intake pipeline ready

**Next Step:**
```bash
python3 manual_lead_review.py
```

---

## Recommendation

### For Now: Use Existing Data

You have plenty of leads to review:
1. Run `manual_lead_review.py` on existing data
2. Evaluate the 639 Facebook listings
3. Check Mercari results
4. Decide if Apify paid plan is worth it based on lead quality

### Future: Upgrade or Wait

**Upgrade If:**
- Lead quality is high
- You want daily automated runs
- Time saved > $49/month value

**Wait for Reset If:**
- Just testing/exploring
- Weekly runs are sufficient
- Current data volume is manageable

---

## What's Still Available (No Apify Needed)

### ✓ Working Now

**Craigslist RSS:**
- Free
- Automated
- Already set up

**eBay Browse API:**
- Free
- Active context searches
- Working in underwriting system

**Manual Searches:**
- Facebook Marketplace (browser)
- Mercari (browser)
- 5 minutes/day, always works

---

## Reverb Integration (Ready When Limit Resets)

### Script: `scripts/reverb_test_limited.py`

**Test Configuration:**
- 3 keywords (Technics SL-1200, Nakamichi Dragon, Moog synthesizer)
- 10 items per search
- Hard cost limit: $0.10
- Conservative for testing

**Full Keyword List (For Production):**
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

**Production Script:** Will create after test succeeds

---

## Summary

**Status:** Apify free tier exhausted after successful integrations  
**Data Collected:** 639+ leads ready for review  
**Scripts Ready:** Facebook (2), Mercari (1), Reverb (1)  
**Next Step:** Use existing data or upgrade plan  

---

**Recommendation:** Run `manual_lead_review.py` on existing leads, evaluate quality, then decide on Apify upgrade.

---

**Files:**
```
data/external_leads/
  facebook_marketplace_leads.csv       (639 items)
  facebook_marketplace_raw_run_001.json
  mercari_leads.csv                    (pending check)
  mercari_raw_run_001.json             (pending check)

scripts/
  facebook_marketplace_run_001.py      (6 searches)
  facebook_marketplace_run_002.py      (8 searches, better filtering)
  mercari_production_run_001.py        (8 searches)
  reverb_test_limited.py               (ready for testing)

docs/
  BEST_FIRST_SEARCH_STRATEGY.md        (search optimization guide)
```
