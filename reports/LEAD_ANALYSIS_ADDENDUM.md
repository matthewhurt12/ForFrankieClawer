# Lead Analysis Addendum - Critical Findings

**Date:** 2026-05-04  
**Reference:** CURRENT_LEAD_ANALYSIS_001.md

---

## ⚠️ CRITICAL ISSUE: False Positives in Top Leads

### Problem Identified

The top-ranked leads include many **NON-EQUIPMENT items** that slipped through filtering:

**Examples from Top 20:**
1. "Nakamichi Dragon Turntable Logo Tee" - **T-SHIRT** (not equipment)
2. "Limited Marantz 2270 Champagne Pin" - **PIN** (not equipment)
3. "Marantz 2270 2245 2230 4230 4240 4270 + Others Volume Function" - **PARTS** (not complete unit)
4. "Nakamichi Dragon Graphic Black Tee" - **T-SHIRT** (not equipment)

### Why This Happened

**Scoring Logic Issue:**
- Model names in title → matched as target model
- Low price → high score (thinking it's underpriced equipment)
- But actual item = apparel, accessories, parts

**Current Filters Miss:**
- T-shirts with model names
- Pins and badges
- Individual parts/components (not "parts only" but specific part names)

---

## 🔧 Improved Filtering Needed

### Add to Junk Keywords
```
't-shirt', 'tshirt', 'tee shirt', 'graphic tee',
'pin', 'badge', 'enamel pin',
'volume', 'function', 'switch', 'button', 'control',
'logo', 'graphic', 'design',
'poster', 'print', 'art',
'shirt', 'apparel', 'clothing'
```

### Require Equipment Keywords
For high-value models, require one of:
- 'receiver', 'amplifier', 'amp', 'integrated'
- 'turntable', 'deck', 'player'
- 'stereo', 'system', 'unit'

**Exception:** If price > $200, likely actual equipment (shirts aren't that expensive)

---

## 📊 Corrected Lead Assessment

### Actual Equipment in Top 50 (Manual Review)

**High Priority Equipment (Actual Receivers/Amps):**

1. **Pioneer SX-1050 Receiver Wood Case Cabinet**
   - Price: $259
   - Source: Facebook Marketplace, Atlanta
   - Category: Pioneer SX-1050 (target model)
   - URL: https://www.facebook.com/marketplace/item/34065518946424677
   - **Decision:** INVESTIGATE ⭐⭐⭐
   - **Why:** Actual SX-1050, price well below $400 floor, local pickup available

2. **Vintage Pioneer SX-650 working**
   - Price: $300
   - Source: Facebook Marketplace, Atlanta
   - Category: Pioneer receiver
   - **Decision:** WATCH ⭐⭐
   - **Why:** Working condition confirmed, price reasonable but need sold comps

3. **McIntosh MA 5100 integrated amp**
   - Price: $1,300
   - Source: Mercari
   - Category: McIntosh MA 5100 (target model)
   - **Decision:** WATCH ⭐⭐
   - **Why:** At expected value, need sold comps to verify if market is higher

4. **Vintage Pioneer SX-770 Receiver and Pioneer CS-99 Speakers**
   - Price: $700
   - Source: Facebook Marketplace, Atlanta
   - Category: Pioneer receiver + speakers
   - **Decision:** WATCH ⭐⭐
   - **Why:** Combo deal, need to price out separately

5. **Pioneer SX 550 Receiver**
   - Price: $675
   - Source: Facebook Marketplace, Atlanta
   - Category: Pioneer receiver
   - **Decision:** WATCH ⭐⭐
   - **Why:** Mid-tier model, need sold comps for accurate margin

---

## 🎯 REVISED NEXT ACTIONS

### Step 1: Re-Filter Lead Pool
Run analysis script again with improved junk filters:
- Add apparel keywords
- Add accessory keywords
- Require equipment context words for target models

### Step 2: Manual Review of Top 50
Scan titles manually to identify:
- ✓ Actual equipment (receivers, amps, turntables)
- ❌ Apparel (t-shirts, clothing)
- ❌ Accessories (pins, badges, stickers)
- ❌ Parts only (individual components)

### Step 3: Prioritize Real Equipment
Focus sold comp research on:
1. Pioneer SX-1050 @ $259 (LOCAL, below floor)
2. McIntosh MA 5100 @ $1,300 (target model)
3. Pioneer SX-650 @ $300 (working, confirmed)
4. Pioneer receiver combos (evaluate bundle vs individual)

### Step 4: Update Scoring Algorithm
**New Rules:**
- If price < $50: Likely accessory/part, score = 0 unless "receiver" or "amplifier" in title
- If model name + apparel keyword: score = 0
- If "function", "volume", "switch" in title: Likely parts, score = 0
- Boost local pickup (Facebook) more heavily
- Require "working", "tested", or "excellent" for high scores

---

## 📋 ACTUAL TOP 10 EQUIPMENT LEADS

After manual filtering of apparel/accessories:

### 1. Pioneer SX-1050 Receiver Wood Case - $259 ⭐⭐⭐
- **Location:** Atlanta, GA (local)
- **Floor:** $400
- **Potential Margin:** High
- **Action:** INVESTIGATE - Contact seller, verify condition, check sold comps
- **URL:** facebook.com/marketplace/item/34065518946424677

### 2. Vintage Pioneer SX-650 working - $300 ⭐⭐
- **Location:** Atlanta, GA (local)
- **Status:** Working confirmed
- **Action:** WATCH - Get sold comps, verify model value

### 3. Pioneer SX 550 Receiver - $675 ⭐
- **Location:** Atlanta, GA (local)
- **Floor:** $150-200 (mid-tier)
- **Action:** SKIP - Likely overpriced for model

### 4. Vintage Pioneer SX-770 Receiver + Speakers - $700 ⭐⭐
- **Location:** Atlanta, GA (local)
- **Bundle:** Receiver + CS-99 speakers
- **Action:** WATCH - Price out separately, verify working

### 5. McIntosh MA 5100 integrated amp - $1,300 ⭐⭐
- **Location:** Online (Mercari)
- **Floor:** $500 (well above)
- **Action:** WATCH - At market rate, need sold comps to see if sells higher

### 6-10. (See full report for additional equipment)

---

## ⚠️ UPDATED WARNINGS

**The current analysis has limited accuracy due to:**
1. Apparel/accessories not filtered
2. Parts listings included
3. Scoring doesn't account for item type

**Before acting on ANY lead:**
1. ✓ Verify it's actual equipment (not shirt/pin/part)
2. ✓ Check photos to confirm condition
3. ✓ Run eBay sold comps
4. ✓ Calculate fees + shipping
5. ✓ Contact seller with detailed questions

**Do NOT contact sellers based on score alone** - many high-scoring items are not equipment.

---

## 🔧 Script Improvements Needed

### Filter Enhancements Required
```python
# Add to junk keywords
APPAREL_KEYWORDS = ['t-shirt', 'tshirt', 'shirt', 'tee', 'graphic tee', 'logo tee']
ACCESSORY_KEYWORDS = ['pin', 'badge', 'enamel', 'sticker', 'poster', 'print']
PARTS_KEYWORDS = ['volume', 'function', 'switch', 'button', 'control', 'dial']

# Require equipment context for target models
EQUIPMENT_CONTEXT = ['receiver', 'amplifier', 'amp', 'integrated', 'turntable', 'deck', 'stereo']

# Score logic
if price < 50 and not any(eq_word in title.lower() for eq_word in EQUIPMENT_CONTEXT):
    score = 0  # Likely accessory
```

---

## ✅ CORRECTED SUMMARY

**After manual review:**

- **Actual Equipment Leads:** ~200-300 (estimated)
- **Apparel/Accessories:** ~100-150
- **Parts Only:** ~50-100
- **Junk/Unrelated:** ~100-200

**High Priority Real Equipment:**
- 10-20 leads worth investigating
- Mostly Pioneer receivers in Atlanta
- Few McIntosh items (high price range)
- Technics turntables (mixed condition)

**Next Action:**
1. Update filtering script
2. Re-run analysis
3. Generate clean top 20 (equipment only)
4. Run sold comps on top 5 actual equipment leads

---

**Critical Takeaway:** Always manually verify lead type before investigation. Automated scoring caught model names but not item types.
