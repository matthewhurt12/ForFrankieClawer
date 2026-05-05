# Apify Testing Priority - When Limit Resets

**Current Status:** Monthly limit exceeded (used ~$0.74+ of $5 free tier)  
**What Worked:** Mercari + Facebook Marketplace (781 leads collected)  
**What's Ready:** 3 actors prepared and waiting for testing

---

## Test Priority Order

### 1. eBay Sold Comps (HIGH PRIORITY) ⭐⭐⭐
**Actor:** oTtB3VgfuE9GtxQt2  
**Script:** `scripts/ebay_sold_comps_test.py`  
**Cost:** $0.05 (test)  
**Why First:** Highest value - eliminates manual sold comp searches

**Test:**
```bash
export APIFY_TOKEN='your-token'
python3 scripts/ebay_sold_comps_test.py
```

**Success Criteria:**
- Returns 8-10 sold items per model
- Prices look accurate (compare to manual eBay check)
- Cost < $0.10
- Data includes: title, price, sold date, condition

**If Successful:**
- Integrate into `manual_lead_review.py` immediately
- Use for all future leads
- Saves 2-4 hours/week

---

### 2. Reverb.com Scraper (MEDIUM PRIORITY) ⭐⭐
**Actor:** RenntKrxUtdZQl1jH  
**Script:** `scripts/reverb_test_limited.py`  
**Cost:** $0.06-0.10 (test)  
**Why Second:** Expands lead sources, music equipment focus

**Test:**
```bash
export APIFY_TOKEN='your-token'
python3 scripts/reverb_test_limited.py
```

**Success Criteria:**
- Returns 20-30 items (3 keywords × 10 items)
- Items are vintage audio (not guitars/drums)
- Prices extracted correctly
- Cost < $0.15

**If Successful:**
- Create production script with full keyword list (11 terms)
- Run weekly
- Add to `data/external_leads/reverb_leads.csv`

---

### 3. AI Scraper (LOW PRIORITY) ⭐
**Actor:** paOtbjvyUiNsr1Qms  
**Script:** `scripts/ai_scraper_test.py`  
**Cost:** $0.05-0.10 (single page test)  
**Why Last:** Experimental, cost uncertain, manual alternatives exist

**Test:**
```bash
export APIFY_TOKEN='your-token'
python3 scripts/ai_scraper_test.py
```

**Success Criteria:**
- Extracts 10-20 items from Audiogon page
- Data structure is usable (title, price, URL)
- Cost < $0.10
- Accuracy > 80% (manual validation)

**If Successful:**
- Test on 5-10 pages to measure scale cost
- Decide if worth using vs manual search

**If Cost > $0.20/page:**
- Skip - too expensive for value

---

## Testing Budget

### Free Tier Remaining
- Monthly limit: $5
- Used today: ~$0.74+
- Remaining: ~$4.25

### Test Allocation
| Actor | Est Cost | Priority |
|-------|----------|----------|
| eBay Sold Comps | $0.05 | HIGH |
| Reverb Scraper | $0.10 | MEDIUM |
| AI Scraper | $0.10 | LOW |
| **Total Tests** | **$0.25** | |
| **Buffer for retests** | $0.25 | |
| **Production runs** | $3.75 | |

**Safe to test all three and still have budget for regular runs.**

---

## What to Skip

### Don't Test Again
- ✓ Mercari: Already working
- ✓ Facebook Marketplace: Already working

### Don't Bother If
- Manual alternative is faster
- Cost exceeds time value
- Data quality is poor
- Dedicated actors exist and work

---

## Post-Test Actions

### After eBay Sold Comps Test

**If Good:**
```python
# Add to manual_lead_review.py
def get_sold_comps(model):
    # Call Apify actor
    # Return median price, range, sample count
    pass

# Use in underwriting
asking_price = 600
sold_data = get_sold_comps(model)
margin = sold_data['median'] - asking_price

if margin > 200:
    print("✓ GOOD MARGIN")
```

**If Bad:**
- Continue manual eBay sold searches
- Document issues for future reference

### After Reverb Test

**If Good:**
- Create production script with full 11 keywords
- Schedule weekly runs
- Add to lead pipeline

**If Bad:**
- Skip Reverb
- Focus on Facebook + Mercari

### After AI Scraper Test

**If Good AND Cost-Effective:**
- Target Audiogon (premium marketplace)
- Test other sites without dedicated actors

**If Expensive:**
- Skip
- Use web_fetch or manual searches instead

---

## Production Schedule (After Testing)

### Daily Runs
**Cost:** ~$0.15/day = $4.50/month

**Run:**
- Facebook Marketplace (8 searches) - $0.16
- eBay Sold Comps (5 leads) - $0.10

**Skip on weekends** → $3.15/month (fits free tier)

### Weekly Runs
**Cost:** ~$0.60/week = $2.40/month

**Monday/Thursday:**
- Facebook Marketplace - $0.16
- Reverb (if tested good) - $0.10
- eBay Sold Comps as needed - $0.10

**Fits free tier comfortably**

---

## Reset Date

**Check Apify Console:**
1. Go to https://console.apify.com
2. Settings → Usage & Billing
3. Find "Current billing period" or "Next reset"
4. Mark calendar

**Typical:** Resets monthly (1st of month or signup anniversary)

---

## Testing Day Checklist

When limit resets:

**Morning:**
- [ ] Confirm Apify limit reset (check console)
- [ ] Test eBay Sold Comps first
- [ ] If good: integrate into lead_review.py
- [ ] If bad: document why

**Afternoon:**
- [ ] Test Reverb scraper
- [ ] Validate data quality
- [ ] Measure actual cost

**Evening (if budget allows):**
- [ ] Test AI scraper
- [ ] Compare to manual effort
- [ ] Decide keep/skip

**Next Day:**
- [ ] Review all test results
- [ ] Decide production schedule
- [ ] Set up automation (if worth it)

---

## Quick Reference

### Already Working
```
✓ Mercari (142 items collected)
✓ Facebook Marketplace (639 items collected)
✓ eBay Browse API (active listings context)
✓ Craigslist RSS (ongoing)
```

### Ready to Test
```
⏳ eBay Sold Comps (HIGH PRIORITY)
⏳ Reverb Scraper (MEDIUM PRIORITY)
⏳ AI Scraper (LOW PRIORITY)
```

### Existing Leads to Review
```
📊 781 leads from Mercari + Facebook
📋 20+ in lead_intake.csv
🔍 Run: python3 manual_lead_review.py
```

---

**Bottom Line:**  
Test eBay Sold Comps first - it has the highest ROI and saves the most time. Then Reverb if budget allows. Skip AI scraper unless you have specific use case and budget left over.
