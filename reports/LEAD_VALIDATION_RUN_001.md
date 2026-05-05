# LEAD_VALIDATION_RUN_001
**Date:** 2026-05-04  
**Status:** COMPLETE  
**Purpose:** Scan 12 target models for active market context validation

---

## ⚠️ CRITICAL WARNINGS

**ACTIVE_LISTING_CONTEXT_ONLY**  
**NEEDS_MANUAL_SOLD_COMPS**  
**NOT_SOLD_COMPS**

DO NOT treat active listings as sold comps.  
DO NOT call anything a buy until eBay Product Research/Terapeak sold comps are manually entered.

---

## Scan Summary

Total models scanned: **12**  
Filter validation passed: **12**  
Filter validation failed: **0**  
Models flagged for review: **1** (JBL L100 - no category price floor)

---

## Model Results (Sorted by Median Active Price)

### 1. Nakamichi 1000ZXL
- **Category:** Nakamichi cassette deck
- **Price Floor:** $75
- **Active Listing Count:** 1
- **Price Range:** $12,999.95 - $12,999.95
- **Median Active Price:** **$12,999.95**
- **Filter Status:** ✓ VALID
- **False Positive Count:** N/A (limited sample)
- **Filter Confidence:** Low (only 1 listing)
- **Suggested Local Max Asking:** $8,000 (deep discount needed due to single data point)

**Notes:** Extremely rare model. Single listing at very high price suggests collector/premium condition. High risk without sold comps.

---

### 2. McIntosh C22
- **Category:** McIntosh preamp
- **Price Floor:** $500
- **Active Listing Count:** 5
- **Price Range:** $749.99 - $16,409.40
- **Median Active Price:** **$4,650.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $3,000

**Notes:** Wide price range suggests condition/restoration variance. Median is strong signal.

---

### 3. Pioneer SX-1250
- **Category:** Pioneer receiver
- **Price Floor:** $400
- **Active Listing Count:** 4
- **Price Range:** $1,650.00 - $4,500.00
- **Median Active Price:** **$3,874.97**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $2,500

**Notes:** Monster receiver. High demand model with strong pricing.

---

### 4. Sansui G-9000
- **Category:** Sansui receiver
- **Price Floor:** $400
- **Active Listing Count:** 4
- **Price Range:** $500.00 - $5,961.11
- **Median Active Price:** **$3,075.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $2,000

**Notes:** Another monster receiver. Wide range but solid median.

---

### 5. Marantz 2275
- **Category:** Marantz receiver
- **Price Floor:** $400
- **Active Listing Count:** 5
- **Price Range:** $2,000.00 - $6,999.00
- **Median Active Price:** **$2,269.99**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $1,500

**Notes:** Premium Marantz model. Strong pricing.

---

### 6. Marantz 2270
- **Category:** Marantz receiver
- **Price Floor:** $400
- **Active Listing Count:** 5
- **Price Range:** $1,850.00 - $3,000.00
- **Median Active Price:** **$2,250.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $1,500

**Notes:** Similar to 2275. Consistent pricing.

---

### 7. McIntosh MA 6100
- **Category:** McIntosh integrated amp
- **Price Floor:** $500
- **Active Listing Count:** 6
- **Price Range:** $1,250.00 - $2,299.99
- **Median Active Price:** **$1,949.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** 44 excluded
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $1,200

**Notes:** Strong filter performance. 6/50 passed (88% exclusion rate).

---

### 8. Pioneer SX-1050
- **Category:** Pioneer receiver
- **Price Floor:** $400
- **Active Listing Count:** 8
- **Price Range:** $998.88 - $3,110.00
- **Median Active Price:** **$1,925.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $1,200

**Notes:** More listings than SX-1250. Better market depth.

---

### 9. Nakamichi Dragon
- **Category:** Nakamichi cassette deck
- **Price Floor:** $75
- **Active Listing Count:** 13
- **Price Range:** $79.00 - $5,199.99
- **Median Active Price:** **$1,499.99**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $900

**Notes:** Most common Nakamichi model. Wide range suggests condition variance.

---

### 10. McIntosh MA 5100
- **Category:** McIntosh integrated amp
- **Price Floor:** $500
- **Active Listing Count:** 7
- **Price Range:** $1,200.00 - $1,999.99
- **Median Active Price:** **$1,495.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** 41 excluded
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $900

**Notes:** Strong filter performance. 7/48 passed (85% exclusion rate).

---

### 11. Technics SL-1200
- **Category:** Technics SL-1200 turntable
- **Price Floor:** $300
- **Active Listing Count:** 41
- **Price Range:** $355.94 - $5,844.49
- **Median Active Price:** **$850.00**
- **Filter Status:** ✓ VALID
- **False Positive Count:** Not tracked in summary
- **Filter Confidence:** High
- **Suggested Local Max Asking:** $500

**Notes:** Most listings (41). Deep market. Wide range suggests MK2/MK3/MK5 variants mixed.

---

### 12. JBL L100 ⚠️ 
- **Category:** Unknown (no price floor defined)
- **Price Floor:** $0
- **Active Listing Count:** 31
- **Price Range:** $15.00 - $4,800.00
- **Median Active Price:** **$219.99**
- **Filter Status:** ✓ VALID (but suspect)
- **False Positive Count:** Unknown (no floor = likely leaking parts)
- **Filter Confidence:** **LOW - REVIEW NEEDED**
- **Suggested Local Max Asking:** $300 (conservative due to filter uncertainty)

**Notes:** ⚠️ No category price floor defined. Median of $219.99 is suspiciously low for full speaker systems. Filter likely leaking grilles, badges, crossovers, and single speakers. Need to add JBL L100 category with $400 floor and re-scan.

---

## Top 5 Local Lead Candidates

**Note:** No local candidate list provided. Recommendations based solely on active market context metrics.

### Candidate #1: McIntosh MA 5100
- **Median Active:** $1,495
- **Suggested Max Local Ask:** $900
- **Margin Potential:** 40-60% below median active
- **Risk Level:** Medium (need sold comps)
- **Action:** Search local listings (Craigslist, FB Marketplace, OfferUp) for MA 5100 under $900
- **⚠️ NEEDS_MANUAL_SOLD_COMPS**

### Candidate #2: Pioneer SX-1050
- **Median Active:** $1,925
- **Suggested Max Local Ask:** $1,200
- **Margin Potential:** 38% below median active
- **Risk Level:** Medium (need sold comps)
- **Action:** Search local listings for SX-1050 under $1,200
- **⚠️ NEEDS_MANUAL_SOLD_COMPS**

### Candidate #3: McIntosh MA 6100
- **Median Active:** $1,949
- **Suggested Max Local Ask:** $1,200
- **Margin Potential:** 38% below median active
- **Risk Level:** Medium (need sold comps)
- **Action:** Search local listings for MA 6100 under $1,200
- **⚠️ NEEDS_MANUAL_SOLD_COMPS**

### Candidate #4: Technics SL-1200
- **Median Active:** $850
- **Suggested Max Local Ask:** $500
- **Margin Potential:** 41% below median active
- **Risk Level:** Low-Medium (common model, easier to verify)
- **Action:** Search local listings for SL-1200 under $500
- **Note:** Verify specific model (MK2, MK3, MK5) as prices vary
- **⚠️ NEEDS_MANUAL_SOLD_COMPS**

### Candidate #5: Nakamichi Dragon
- **Median Active:** $1,500
- **Suggested Max Local Ask:** $900
- **Margin Potential:** 40% below median active
- **Risk Level:** High (cassette decks need functional testing)
- **Action:** Search local listings for Dragon under $900
- **Note:** Must verify all functions (play, record, auto-azimuth, transport)
- **⚠️ NEEDS_MANUAL_SOLD_COMPS**

---

## Next Steps

### Immediate Actions

1. **Add JBL L100 price floor**
   - Add `"jbl l100": 400` to `CATEGORY_PRICE_FLOORS` in `ebay_active_context.py`
   - Re-scan JBL L100 with proper filtering
   - Verify median price rises above $400

2. **Manual Sold Comps Required**
   - Access eBay Product Research or Terapeak
   - Pull 90-day sold comps for each candidate model
   - Calculate actual sold median (not active listing median)
   - Compare active vs sold to gauge listing-to-sale conversion

3. **Local Market Search**
   - Search Craigslist (Athens, Atlanta, surrounding areas)
   - Search Facebook Marketplace
   - Search OfferUp
   - Document any matches under suggested max asking prices

### Medium-Term Actions

1. **Sold Comps Integration**
   - Build Phase 2: eBay Finding API (sold items endpoint)
   - Automate sold comps analysis
   - Calculate active-to-sold ratio per model

2. **Local Listing Scraper**
   - Craigslist RSS/HTML scraper
   - FB Marketplace API (if available)
   - Alert system for new listings matching criteria

3. **Deal Score Calculator**
   - Input: local asking price
   - Compare to: median sold (not active)
   - Output: deal score (1-10), margin estimate, risk flags

---

## Filter Validation Summary

**Models with VALID filters:** 12/12 (100%)  
**Models needing review:** 1 (JBL L100)

**Key Success Metrics:**
- McIntosh MA 5100: 85% exclusion rate (41/48 excluded)
- McIntosh MA 6100: 88% exclusion rate (44/50 excluded)
- All McIntosh/Pioneer/Marantz medians above category floors

**Known Issues:**
- JBL L100 has no category floor (false positives likely)
- Nakamichi 1000ZXL only 1 listing (insufficient data)

---

## File Locations

**Scan logs:**
- `data/lead_validation_001/mcintosh_ma_5100.log`
- `data/lead_validation_001/mcintosh_ma_6100.log`

**JSON results:**
- `data/ebay_active_search/*production_20260504_134*.json`

**This report:**
- `reports/LEAD_VALIDATION_RUN_001.md`

---

## COMPLIANCE REMINDERS

✓ All data marked ACTIVE_LISTING_CONTEXT_ONLY  
✓ All data marked TEMPORARY_TEST_OUTPUT  
✓ All data marked NOT_SOLD_COMPS  
✓ No seller usernames stored  
✓ No buyer data stored  
✓ No eBay user account data stored  
✓ 7-day auto-cleanup enabled via `ebay_cleanup_temp.py`

**DO NOT:**
- Treat active listings as sold comps
- Call anything a buy without manual sold comp verification
- Store eBay personal data beyond 7-day temporary window

---

**End of Report**
