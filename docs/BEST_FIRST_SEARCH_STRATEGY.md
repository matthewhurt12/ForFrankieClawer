# Best First Search Strategy

**Date:** 2026-05-04  
**Purpose:** Optimized search list for Facebook Marketplace and other platforms

---

## Core Search Terms

### Athens, GA (Local Priority)
1. **vintage stereo** - Broad catch-all for complete systems
2. **vintage receiver** - Target specific component type
3. **Technics SL-1200** - High-value turntable model
4. **McIntosh amplifier** - Premium brand

### Atlanta, GA (Secondary Market)
5. **vintage stereo** - Broader market search
6. **Technics SL-1200** - High-demand model
7. **McIntosh amplifier** - Premium equipment
8. **Marantz receiver** - Target brand

---

## Why These Terms

### "vintage stereo" + "vintage receiver"
**Coverage:** Broad enough to catch sellers who don't know exact model names  
**Quality:** Still filters out modern/new equipment  
**Volume:** High listing count for screening  

### Model-Specific (Technics SL-1200)
**Precision:** Known high-value target  
**Recognition:** Sellers know this model name  
**Demand:** Strong resale market  

### Brand-Specific (McIntosh, Marantz)
**Premium:** High-margin potential  
**Brand Recognition:** Sellers list by brand  
**Scarcity:** Less common, worth monitoring  

---

## What We Removed

### Too Specific
❌ "Marantz 2270" - Too narrow (also caught by "Marantz receiver")  
❌ "Pioneer SX-1050" - Too narrow (caught by "vintage receiver")  

### Geographic Redundancy
✓ Athens first (local pickup priority)  
✓ Atlanta second (drive-able for good deals)  

---

## Search Term Hierarchy

```
Level 1: Broad Category
  - "vintage stereo"
  - "vintage receiver"
  
Level 2: High-Value Model
  - "Technics SL-1200"
  
Level 3: Premium Brand
  - "McIntosh amplifier"
  - "Marantz receiver"
```

**Strategy:** Cast wide net (Level 1), catch known winners (Level 2), monitor premium (Level 3)

---

## Expected Results

### Athens Searches (4)
- **vintage stereo:** 50-100 listings
- **vintage receiver:** 30-60 listings
- **Technics SL-1200:** 0-10 listings (rare)
- **McIntosh amplifier:** 0-5 listings (very rare)

**Total Athens:** ~100-150 unique items

### Atlanta Searches (4)
- **vintage stereo:** 100-200 listings
- **Technics SL-1200:** 5-15 listings
- **McIntosh amplifier:** 2-8 listings
- **Marantz receiver:** 10-30 listings

**Total Atlanta:** ~150-250 unique items

### Combined Expected
**Raw:** 250-400 listings  
**After Dedup:** 200-300 unique  
**Quality Candidates:** 20-50  

---

## Expansion Strategy

### If Volume Too Low (<50 candidates)
**Add:**
- "Pioneer receiver"
- "Sansui receiver"
- "vintage turntable"
- "vintage amplifier"

### If Volume Too High (>500 candidates)
**Remove Broad Terms:**
- Drop "vintage stereo" (keep "vintage receiver")
- Focus on model/brand-specific only

### Geographic Expansion
**Phase 2:**
- Augusta, GA
- Macon, GA
- Chattanooga, TN
- Greenville, SC

---

## Cross-Platform Consistency

### Facebook Marketplace
✓ Use these 8 searches

### Mercari
✓ Use same search terms  
✓ Remove location prefix (Mercari is nationwide)

### Craigslist RSS
✓ Use same terms in RSS queries  
✓ Separate Athens/Atlanta feeds

---

## Quality Signals in Search Results

### Good Signs
✓ "vintage" + brand name (McIntosh, Marantz, Pioneer)  
✓ Model numbers in title  
✓ "working" or "tested"  
✓ Complete photos  

### Red Flags
❌ "parts only"  
❌ "repair" or "broken"  
❌ "untested"  
❌ Price too low (<$20 for receivers)  
❌ "LED kit", "bulbs", "capacitors"  

---

## Testing Results

### Run 001 (Athens/Atlanta, 6 searches)
**Retrieved:** 639 unique Facebook Marketplace listings  
**Cost:** $0.12  
**Time:** ~3 minutes  

### Expected with 8 Searches
**Estimated:** 700-850 unique listings  
**Cost:** ~$0.16  
**Within budget:** ✓ (<$0.50)  

---

## Monthly Usage

### Daily Scans
**Frequency:** Once per day  
**Cost:** $0.16 × 30 = $4.80/month  
**Fits:** Apify free tier ($5/month)  

### 2-3x Weekly
**Frequency:** Monday, Wednesday, Friday  
**Cost:** $0.16 × 12 = $1.92/month  
**Recommended:** ✓ Good balance  

---

## Success Metrics

### Volume Check
✓ 200-300 unique items per run  
✓ 20-50 quality candidates (<$1,500)  
✓ 10-20 worth underwriting  

### Quality Check
✓ At least 1 McIntosh/Marantz listing per week  
✓ At least 2-3 Technics SL-1200 per week  
✓ At least 5-10 "vintage receiver" candidates  

### Cost Efficiency
✓ Under $5/month for daily runs  
✓ Under $0.50 per run  

---

## Next Steps

1. **Run with 8 searches** - Test this best-first list
2. **Measure results** - Count quality candidates
3. **Adjust if needed** - Add/remove based on volume
4. **Expand markets** - Augusta, Macon if Athens/Atlanta productive

---

**Strategy:** Start tight, measure, then expand based on results.  
**Goal:** Maximum quality candidates, minimum API cost.
