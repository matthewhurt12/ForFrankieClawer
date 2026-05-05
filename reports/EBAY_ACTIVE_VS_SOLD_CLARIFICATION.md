# eBay Active vs Sold Listings - Clarification

**Date:** 2026-05-04  
**Status:** Clearing up confusion

---

## What We Currently Have

### ✓ ACTIVE Listings (Working Now)
**Script:** `ebay_active_context.py`  
**API:** eBay Browse API (official, free)  
**Shows:** Current listings people are ASKING for items

**Example:**
```
McIntosh MA 6100 - Active Listings:
  1. $1,200 (Excellent condition)
  2. $950 (Good condition) 
  3. $800 (Fair condition)
  4. $1,500 (Mint)
```

These are **asking prices** - what sellers want.

---

### ⏳ SOLD Listings (Not Tested Yet)
**Actor:** eBay Sold Comps (oTtB3VgfuE9GtxQt2)  
**Shows:** What items ACTUALLY sold for (completed sales)

**Example:**
```
McIntosh MA 6100 - Sold Listings:
  1. $950 (sold 3 days ago)
  2. $1,100 (sold 1 week ago)
  3. $875 (sold 2 weeks ago)
```

These are **real prices** - what buyers paid.

**Status:** Ready to test when Apify limit resets

---

## Test Result: Actor 8bXnzCF4JVgMMA5cM

**Tested:** Yes (just now)  
**Result:** ❌ Returned 0 items (doesn't work for our use case)

**Input:**
```json
{
  "listingUrls": [
    "https://www.ebay.com/sch/i.html?_nkw=technics+sl-1200"
  ]
}
```

**Output:** Empty array `[]`

**Verdict:** This actor doesn't work for general eBay searches. Skip it.

---

## What You Probably Want

Based on "i want to see the active listing our tool rn only shows the sold ones":

**I think you might be confused about what we have:**

### We DO Have Active Listings
✓ `ebay_active_context.py` shows **ACTIVE** listings  
✓ Used in lead underwriting to check market context  
✓ These are current asking prices  

### We DON'T Have Sold Listings Yet
❌ Haven't tested sold comps actor yet  
❌ Apify limit hit before we could test  
❌ Sold comps are HIGH PRIORITY when limit resets  

---

## How to See Active Listings Now

### Test the Active Listings Script
```bash
cd ~/.openclaw/workspace
export EBAY_APP_ID='your-app-id'
python3 ebay_active_context.py
```

This will show you current eBay active listings for any model.

### Check Underwriting Reports
When you run `manual_lead_review.py`, it automatically pulls active listings:

```bash
python3 manual_lead_review.py
```

The generated reports show eBay active context:
```
eBay Active Listings for McIntosh MA 6100:
  - $1,200 (Excellent)
  - $950 (Good)
  - $800 (Fair)

Your Lead: $600
Margin Potential: $200-350
```

---

## What We Need (When Apify Resets)

### eBay Sold Comps - HIGH PRIORITY ⭐⭐⭐
**Why:** Validate margins with REAL sold prices, not asking prices

**Current Problem:**
- You see active asking prices ($1,200)
- But don't know if they actually sell at that price
- Items might sit unsold for months

**Solution:**
- Test eBay Sold Comps actor (oTtB3VgfuE9GtxQt2)
- Get last 30 days of SOLD prices
- Know what items ACTUALLY sell for
- Calculate real margins

---

## Summary

| Type | Status | Tool | Shows |
|------|--------|------|-------|
| **Active Listings** | ✓ Working | eBay Browse API | Asking prices (current) |
| **Sold Listings** | ⏳ Ready to test | eBay Sold Comps actor | Real sold prices |

### You Have Active Listings Already
Run this to see:
```bash
python3 ebay_active_context.py
# or
python3 manual_lead_review.py
```

### You Need Sold Listings
Test when Apify limit resets:
```bash
python3 scripts/ebay_sold_comps_test.py
```

---

## Files to Check

### For Active Listings (Working Now)
```bash
# Check the script
cat ebay_active_context.py

# Run it directly
python3 ebay_active_context.py

# Or use in lead review
python3 manual_lead_review.py
```

### Review Past Reports
```bash
# See what active context looks like
cat reports/lead_*_review.md
```

---

## Bottom Line

**You DO have active listings** - they're in `ebay_active_context.py` using the free Browse API.

**You DON'T have sold listings yet** - that's the eBay Sold Comps actor we need to test.

The actor you just asked to test (8bXnzCF4JVgMMA5cM) returned 0 items and isn't useful for us.

**Next Step:** When Apify resets, test eBay Sold Comps (oTtB3VgfuE9GtxQt2) to get real sold prices.

---

**Clarified:** 2026-05-04  
**Active Listings:** ✓ Working (Browse API)  
**Sold Listings:** ⏳ Ready to test (when limit resets)
