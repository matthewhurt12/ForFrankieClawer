# eBay Sold Comps Cleaning 001

**Generated:** 2026-05-05 04:14 UTC
**Input:** `data\sold_comps\ebay_sold_audio_retest_2026-05-05.json`
**Output:** `data\sold_comps\ebay_sold_audio_retest_2026-05-05_clean.csv`

Only rows classified as FULL_UNIT may be used for resale value.

---

## Summary

- **Raw Rows:** 30
- **Valid Full-Unit Rows:** 12
- **Rejected Rows:** 18

## Model Confidence

| Model | Valid Full-Unit Comps | Median Sold | Range | Status |
|---|---:|---:|---|---|
| Kenwood KR-2600 | 1 | $138 | $138 - $138 | LOW_CONFIDENCE |
| Kenwood KR-3010 | 1 | $150 | $150 - $150 | LOW_CONFIDENCE |
| Kenwood KR-3090 | 1 | $145 | $145 - $145 | LOW_CONFIDENCE |
| Kenwood KR-4070 | 2 | $312 | $250 - $375 | LOW_CONFIDENCE |
| Kenwood KR-5030 | 1 | $102 | $102 - $102 | LOW_CONFIDENCE |
| Kenwood KR-6050 | 1 | $255 | $255 - $255 | LOW_CONFIDENCE |
| Marantz 2226B | 1 | $531 | $531 - $531 | LOW_CONFIDENCE |
| Pioneer SX-636 | 2 | $48 | $14 - $83 | LOW_CONFIDENCE |
| Technics SA-400 | 1 | $299 | $299 - $299 | LOW_CONFIDENCE |
| Technics SA-600 | 1 | $300 | $300 - $300 | LOW_CONFIDENCE |

## Reject Reasons

- **4:** Hard reject term: parts
- **3:** Hard reject term: knob
- **2:** Hard reject term: kit
- **2:** Hard reject term: led
- **1:** Hard reject term: feet
- **1:** Hard reject term: board
- **1:** Hard reject term: dial
- **1:** Hard reject term: lamp
- **1:** No exact model detected
- **1:** Below full-unit price floor for Marantz 2226B: $50 < $250
- **1:** Hard reject term: meter

## Rules

- FULL_UNIT requires exact model detection.
- Hard rejects include manuals, bulbs, kits, parts, knobs, faceplates, cabinets, cases, remotes, apparel, and related junk.
- Below model/category price floor is rejected as likely accessory/parts/noisy result.
- Fewer than 3 valid FULL_UNIT comps is LOW_CONFIDENCE.
