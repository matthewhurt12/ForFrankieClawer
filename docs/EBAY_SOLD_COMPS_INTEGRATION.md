# eBay Sold Comps Integration

**Actor ID:** oTtB3VgfuE9GtxQt2  
**Type:** eBay sold/completed listings scraper  
**Status:** Ready for testing (awaiting Apify limit reset)  
**Priority:** HIGH - Critical for underwriting accuracy

---

## Why This Matters

### Current Problem
Every lead is marked: **NEEDS_MANUAL_SOLD_COMPS**

You have to manually:
1. Search eBay for "[model] sold"
2. Switch to "Sold Items" filter
3. Check last 5-10 sold prices
4. Calculate average/range
5. Compare to asking price

**Time per lead:** 3-5 minutes  
**Error prone:** Manual data entry, missed listings

### This Solution
**Automated sold comp lookup in seconds.**

---

## How It Works

### Input
```json
{
  "keywords": ["Technics SL-1200", "McIntosh MA 6100"],
  "daysToScrape": 30,
  "count": 10,
  "sortOrder": "endedRecently"
}
```

### Output
For each keyword, get last 10 sold items with:
- Title
- Final sold price
- Sold date
- Condition
- Number of bids
- Seller info
- Item URL

### Analysis
```
Technics SL-1200:
  Sold Items: 8
  Price Range: $450 - $850
  Average: $625
  Median: $600
```

---

## Integration with Underwriting

### Current Flow
1. Lead: "Technics SL-1200 - $400"
2. ❌ Marked NEEDS_MANUAL_SOLD_COMPS
3. Manual eBay search (3-5 minutes)
4. Note sold prices
5. Calculate margin
6. Decision

### New Flow
1. Lead: "Technics SL-1200 - $400"
2. ✓ Auto-run sold comp scraper
3. Get: Last 10 sold for $450-850 (avg $625)
4. Calculate: Buy $400, Sell $600 = $200 margin
5. ✓ Auto-mark: GOOD_MARGIN or TIGHT_MARGIN
6. Decision

**Time saved:** 3-5 minutes per lead  
**Accuracy:** Consistent, data-driven

---

## Use Cases

### 1. Lead Underwriting (Primary)
When a new lead comes in:
```python
# Automatically pull sold comps
model = "McIntosh MA 6100"
sold_data = get_ebay_sold_comps(model, last_30_days=True, count=10)

# Calculate market value
median_price = calculate_median(sold_data)
asking_price = 800

# Margin check
if asking_price < median_price * 0.7:
    print("✓ GOOD MARGIN - Worth pursuing")
```

### 2. Pricing Validation
Check if a Facebook/Mercari listing is actually a "deal":
```python
asking = 500
recent_sold = get_sold_comps(model)

if asking < min(recent_sold):
    print("🔥 EXCEPTIONAL DEAL")
elif asking < median(recent_sold):
    print("✓ GOOD DEAL")
else:
    print("❌ OVERPRICED")
```

### 3. Resale Price Research
Before buying, know what you can sell for:
```python
buy_price = 600
sold_comps = get_sold_comps(model, last_14_days=True)

# Worst case: sell at lowest recent price
worst_case = min(sold_comps) - 50  # eBay fees
margin = worst_case - buy_price

if margin > 200:
    print("✓ Safe buy")
```

---

## Target Models for Testing

### High Priority (Test First)
1. **Technics SL-1200** - High volume, known market
2. **McIntosh MA 6100** - Premium, good margins
3. **Marantz 2270** - Popular receiver, steady sales

### Medium Priority
4. Pioneer SX-1250
5. Nakamichi Dragon
6. Sansui AU-717

### Why Start Small
- Test accuracy with known models
- Validate price extraction
- Measure cost per keyword
- Confirm data quality before scaling

---

## Cost Estimates

### Per Keyword
**Unknown until tested**, likely:
- $0.01-0.03 per keyword
- 10 items per keyword

### Test Run (3 keywords × 10 items)
- Estimated: $0.03-0.09
- Max limit: $0.10

### Production Use

**Daily Underwriting (5 leads/day):**
- 5 models × $0.02 = $0.10/day
- Monthly: $3/month

**Weekly Batch (20 leads):**
- 20 models × $0.02 = $0.40/week
- Monthly: $1.60/month

**Very affordable for the value.**

---

## Data Fields to Extract

### Critical Fields
✓ Title (full item description)  
✓ Final sold price  
✓ Sold date  
✓ Item condition  

### Useful Fields
✓ Number of bids (demand indicator)  
✓ Item location (shipping considerations)  
✓ Seller feedback (quality proxy)  

### Optional Fields
- Shipping cost
- Return policy
- Item specifics (year, model variant)

---

## Integration Script Flow

### Standalone Function
```python
def get_ebay_sold_comps(model_name, days=30, count=10):
    """
    Get recent eBay sold comps for a model.
    
    Returns:
    {
        'model': 'Technics SL-1200',
        'sold_count': 8,
        'price_range': (450, 850),
        'median_price': 600,
        'average_price': 625,
        'recent_sales': [
            {'price': 600, 'date': '2024-04-15', 'condition': 'Used'},
            ...
        ]
    }
    """
```

### Lead Review Integration
```python
# In manual_lead_review.py

# After eBay active context check:
if model_identified:
    # Get sold comps
    sold_data = get_ebay_sold_comps(model)
    
    # Compare
    asking = lead['asking_price']
    median_sold = sold_data['median_price']
    
    # Flag
    if asking < median_sold * 0.7:
        lead['margin_flag'] = 'EXCELLENT'
    elif asking < median_sold * 0.85:
        lead['margin_flag'] = 'GOOD'
    else:
        lead['margin_flag'] = 'TIGHT'
```

---

## Advantages

### vs Manual Sold Comp Search
✓ **Speed:** 5 seconds vs 5 minutes  
✓ **Consistency:** Same data every time  
✓ **Scalability:** Handle 100 leads as easily as 1  
✓ **Data Quality:** Structured JSON output  

### vs eBay Browse API (Active Listings)
✓ **Real prices:** Sold vs asking  
✓ **Market validation:** What actually sells  
✓ **Accurate margins:** Based on completed sales  

---

## Testing Checklist

When Apify limit resets:

- [ ] Test 2 known models (SL-1200, MA 6100)
- [ ] Verify price extraction accuracy
- [ ] Check date range (30 days)
- [ ] Validate sold vs active flag
- [ ] Measure cost per keyword
- [ ] Compare to manual search (time & accuracy)
- [ ] Test edge cases (rare models, low volume)
- [ ] Integrate with lead_review script

---

## Production Implementation

### Phase 1: Manual Trigger
```bash
# Run sold comps for specific model
python3 scripts/get_sold_comps.py "Technics SL-1200"
```

### Phase 2: Batch Processing
```bash
# Run for all unreviewed leads
python3 scripts/batch_sold_comps.py
```

### Phase 3: Auto-Integration
```python
# Built into manual_lead_review.py
# Automatic for every lead
```

---

## Cost-Benefit Analysis

### Cost
- Test: $0.05-0.10 (one-time)
- Daily use: $0.10/day = $3/month
- Weekly use: $0.40/week = $1.60/month

### Benefit
**Time Saved:**
- 5 leads/day × 4 minutes = 20 min/day
- 140 min/week = 2.3 hours/week
- 9.3 hours/month

**Value:**
- At $50/hour: $465/month saved
- At $25/hour: $232/month saved
- At $15/hour: $140/month saved

**ROI:** 40x-150x return on investment

### Quality Improvement
- Better buy decisions
- Fewer overpriced purchases
- More accurate margin calculations
- Reduced risk

---

## Alternative: Manual Process

**If you don't use this actor:**

For each lead:
1. Open eBay
2. Search "[model name]"
3. Click "Advanced" → "Sold Items"
4. Manually note last 5-10 prices
5. Calculate average in head/calculator
6. Return to underwriting sheet
7. Enter data manually

**Time:** 3-5 minutes  
**Errors:** Typos, missed listings, wrong calculations  
**Scalability:** Can't handle 50+ leads/day

---

## Files

```
scripts/
  ebay_sold_comps_test.py          # Ultra conservative test (2 models)
  get_sold_comps.py                # Production script (when ready)

docs/
  EBAY_SOLD_COMPS_INTEGRATION.md   # This file

data/sold_comps/
  ebay_sold_test.json              # Test results (when run)
```

---

## Recommendation

**Test Priority:** HIGH

This is the most valuable Apify actor for your workflow:
1. Saves 2-4 hours/week
2. Improves underwriting accuracy
3. Low cost ($2-3/month)
4. Direct ROI (better buy decisions)

**When limit resets:**
1. Test this FIRST (before Reverb, AI scraper)
2. Validate with 2-3 known models
3. If accurate: integrate immediately
4. Use for every lead

---

**Status:** Awaiting test  
**Priority:** HIGH (test first when limit resets)  
**Expected ROI:** 40-150x
