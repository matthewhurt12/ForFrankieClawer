# Facebook Marketplace Apify Run 001

**Date:** 2026-05-04  
**Status:** IN PROGRESS  
**Actor:** apify~facebook-marketplace-scraper

---

## Run Configuration

**Settings:**
- Max items per URL: 25
- Max cost per run: $0.50
- Search URLs: 6 (Athens & Atlanta)
- Proxy: Apify proxies

**Search URLs:**
1. Athens, GA - vintage stereo
2. Athens, GA - technics sl-1200  
3. Athens, GA - mcintosh amplifier
4. Atlanta, GA - vintage receiver
5. Atlanta, GA - marantz 2270
6. Atlanta, GA - pioneer sx-1050

---

## Data Collection Rules

### Collected (Compliant)
✓ Title  
✓ Price  
✓ Listing URL  
✓ Photo URL  
✓ Location (Athens/Atlanta)  
✓ Source  
✓ Scraped timestamp  

### NOT Collected (Privacy)
❌ Seller names  
❌ Seller IDs  
❌ Messages  
❌ Personal data  

---

## Processing

✓ Deduplication by listing URL  
✓ Price filtering (<$1,500, >$10)  
✓ Top 10 candidates to lead_intake.csv  
✓ Marked FACEBOOK_ACTIVE_CONTEXT_ONLY  
✓ Marked NEEDS_MANUAL_REVIEW  

---

## Output Files

```
data/external_leads/
  facebook_marketplace_raw_run_001.json    # Raw Apify output
  facebook_marketplace_leads.csv           # Normalized

lead_intake.csv                            # Top 10 added
```

---

## Expected Cost

**Estimate:**
- 6 searches × $0.02 = ~$0.12
- Within budget: ✓ ($0.50 limit)

---

## Next Steps

1. **Wait for completion** (2-3 minutes)
2. **Review results:**
   ```bash
   cat data/external_leads/facebook_marketplace_leads.csv
   ```
3. **Run underwriting:**
   ```bash
   python3 manual_lead_review.py
   ```

---

## Compliance

⚠️ **FACEBOOK_ACTIVE_CONTEXT_ONLY**  
⚠️ **NEEDS_MANUAL_REVIEW**  
⚠️ **NEEDS_MANUAL_SOLD_COMPS**

All items marked with these warnings.

---

## Status

**Currently:** Running Facebook Marketplace scraper...  
**Estimated time:** 2-3 minutes  
**Will update when complete.**
