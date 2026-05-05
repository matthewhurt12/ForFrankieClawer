# Apify Mercari Integration - Ready

**Date:** 2026-05-04  
**Status:** READY TO USE  
**Actor:** stealth_mode/mercari-product-search-scraper

---

## Quick Start

### 1. Set API Token
```bash
export APIFY_TOKEN='your-apify-token-here'
```

### 2. Run Scraper
```bash
python3 scripts/mercari_apify_scraper.py
```

### 3. Review Leads
```bash
python3 manual_lead_review.py
```

---

## What This Solves

**Problem:** Mercari blocks browser automation (Cloudflare)  
**Solution:** Use Apify's professional scraping infrastructure

**Benefits:**
- ✓ No Cloudflare blocking
- ✓ No bot detection
- ✓ Professional proxies
- ✓ Structured data output
- ✓ Integrates with existing lead pipeline

---

## Output

**All Items:** `data/external_leads/mercari_leads.csv`  
**Top Candidates:** Added to `lead_intake.csv`  
**Underwriting Reports:** `reports/lead_XXXX_review.md`

---

## Compliance

⚠️ **MERCARI_ACTIVE_CONTEXT_ONLY**  
⚠️ **NEEDS_MANUAL_REVIEW**  
⚠️ **NOT_SOLD_COMPS**

✓ No seller personal data stored  
✓ Deduplication by item_id  
✓ Manual sold comp verification required  

---

## Pricing

**Apify Free Tier:** $5/month credit  
**Cost Per Search:** ~$0.005-0.01  
**Monthly Capacity:** 500-1000 searches

---

Ready to use. Set `APIFY_TOKEN` and run.

See `docs/APIFY_MERCARI_INTEGRATION.md` for full documentation.
