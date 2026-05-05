# Apify Mercari Integration

**Actor:** stealth_mode/mercari-product-search-scraper  
**Status:** Integrated  
**Purpose:** Scrape Mercari listings without browser automation

---

## Setup

### 1. Get Apify API Token

1. Sign up at https://apify.com
2. Go to Settings → Integrations → API tokens
3. Copy your API token

### 2. Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export APIFY_TOKEN='[REDACTED_APIFY_TOKEN]'

# Or set temporarily:
export APIFY_TOKEN='your-token-here'
```

### 3. Verify Setup

```bash
echo $APIFY_TOKEN
# Should show your token
```

---

## Usage

### Basic Search

```bash
cd ~/.openclaw/workspace
python3 scripts/mercari_apify_scraper.py
```

This searches for all default target models:
- McIntosh MA 5100
- McIntosh MA 6100
- Pioneer SX-1250
- Pioneer SX-1050
- Marantz 2270
- Marantz 2275
- Technics SL-1200
- Nakamichi Dragon

### Custom Search

Edit `scripts/mercari_apify_scraper.py`:

```python
DEFAULT_SEARCHES = [
    "Your Custom Search",
    "Another Search",
]
```

---

## What It Does

### 1. Runs Apify Actor

- Sends search queries to Mercari via Apify
- Uses Apify proxies to avoid blocking
- Returns up to 50 items per search
- Synchronous API call (waits for results)

### 2. Normalizes Data

Converts Apify results to our schema:
```csv
source,site,item_id,title,status,price_cents,price_usd,url,image_url,condition,shipping_payer,category_title,query,scraped_at,review_status,notes
```

**Key Conversions:**
- `price` (cents) → `price_usd` (dollars)
- `name` → `title`
- `itemCondition` → `condition`
- Adds `scraped_at` timestamp
- Marks as `MERCARI_ACTIVE_CONTEXT_ONLY`

### 3. Deduplicates

- Removes duplicate items by `item_id`
- Keeps first occurrence

### 4. Saves Results

**All Items:**
- `data/external_leads/mercari_leads.csv` (CSV)
- `data/external_leads/mercari_leads.json` (JSON)

**Top Candidates:**
- Filters items under $1,500
- Adds top 10 to `lead_intake.csv`
- Ready for `manual_lead_review.py`

---

## Output Format

### mercari_leads.csv

```csv
source,site,item_id,title,status,price_cents,price_usd,url,image_url,condition,shipping_payer,category_title,query,scraped_at,review_status,notes
apify,mercari,m12345678,McIntosh MA5100 Integrated Amplifier,on_sale,75000,750.00,https://...,https://...,Good,seller,Electronics,McIntosh MA 5100,2026-05-04T14:30:00Z,MERCARI_ACTIVE_CONTEXT_ONLY,NEEDS_MANUAL_REVIEW
```

### lead_intake.csv (Top Candidates)

Automatically appends top candidates to existing lead intake system:

```csv
date_found,source,listing_url,screenshot_path,model_guess,title,asking_price,location,seller_condition_claim,photos_available,notes,status
2026-05-04,Mercari (Apify),https://...,,"McIntosh MA 5100",McIntosh MA5100 Amplifier,750.00,Online,Good,yes,"Mercari listing. Condition: Good. Shipping: seller",unreviewed
```

---

## Integration with Lead Review

After scraping, run:

```bash
python3 manual_lead_review.py
```

This will:
1. Load new Mercari leads from `lead_intake.csv`
2. Run eBay active context search for each
3. Calculate margin potential
4. Generate seller questions
5. Create detailed underwriting reports
6. Mark as `NEEDS_MANUAL_SOLD_COMPS`

---

## Compliance

### What We Store
✓ Item ID  
✓ Title  
✓ Price  
✓ URL  
✓ Image URL  
✓ Condition  
✓ Shipping info  
✓ Category  

### What We Do NOT Store
❌ Seller names  
❌ Seller IDs  
❌ Seller messages  
❌ Buyer information  
❌ Account details  
❌ Personal data  

### Warnings
⚠️ **MERCARI_ACTIVE_CONTEXT_ONLY**  
⚠️ **NEEDS_MANUAL_REVIEW**  
⚠️ **NOT_SOLD_COMPS**  

All items are marked as active context only. Do not treat as sold comps. Manual eBay sold comp verification required before buying.

---

## Pricing

### Apify Free Tier
- $5 free credit per month
- ~500-1000 Mercari searches
- Runs on Apify platform (no local resources)

### Paid Tiers
- Pay-as-you-go: ~$0.005-0.01 per search
- Platform handles proxies, captchas, scaling

---

## Advantages

### vs Browser Automation
✓ No Cloudflare blocking  
✓ No bot detection  
✓ Professional proxy infrastructure  
✓ No local browser needed  
✓ Scalable (run 100s of searches)  

### vs Manual Search
✓ Automated data extraction  
✓ Structured CSV output  
✓ Batch multiple searches  
✓ Consistent formatting  

---

## Workflow

### Daily Routine

**Morning:**
```bash
# 1. Run Mercari scraper
export APIFY_TOKEN='your-token'
python3 scripts/mercari_apify_scraper.py

# 2. Review top candidates
python3 manual_lead_review.py

# 3. Check reports
cat reports/lead_*_review.md
```

**Result:** Top Mercari listings automatically added to your lead pipeline

---

## Troubleshooting

### "APIFY_TOKEN not set"
```bash
export APIFY_TOKEN='your-token-here'
```

### "Actor timeout"
- Actor took >5 minutes
- Apify may be slow or down
- Try again later
- Check Apify dashboard for actor status

### "No items found"
- Search returned 0 results
- Try different search terms
- Check Mercari.com manually to verify items exist

### "API Error: 401"
- Invalid or expired token
- Get new token from Apify dashboard

### "API Error: 429"
- Rate limit exceeded
- Wait a few minutes
- Upgrade Apify plan if needed

---

## Example Output

```
================================================================================
Mercari Apify Scraper
================================================================================

⚠️  MERCARI_ACTIVE_CONTEXT_ONLY
⚠️  NEEDS_MANUAL_REVIEW
⚠️  NOT_SOLD_COMPS

✓ Apify token found (length: 32)

================================================================================
Searching Mercari: McIntosh MA 5100
================================================================================

Starting Apify Actor...
Max items: 50

✓ Actor completed
✓ Items returned: 12

✓ McIntosh MA 5100: 12 items

[... more searches ...]

================================================================================
Processing Results
================================================================================

Total items before dedup: 87
Unique items after dedup: 85

✓ Saved: data/external_leads/mercari_leads.csv
  Total items: 85
✓ Saved: data/external_leads/mercari_leads.json

================================================================================
Top Candidates (Price < $1500)
================================================================================

Found 8 candidates under $1500:

1. McIntosh MA5100 Integrated Amplifier Vintage
   Price: $750.00
   Query: McIntosh MA 5100
   Condition: Good
   URL: https://www.mercari.com/us/item/...

[... more candidates ...]

✓ Added top 8 candidates to lead_intake.csv

Run manual_lead_review.py to underwrite these leads:
  python manual_lead_review.py

================================================================================
Complete
================================================================================

⚠️  All items marked MERCARI_ACTIVE_CONTEXT_ONLY
⚠️  All items marked NEEDS_MANUAL_REVIEW
⚠️  Do not call anything a deal until sold comps verified
```

---

## Files Created

```
scripts/
  mercari_apify_scraper.py         # Main scraper script

data/external_leads/
  mercari_leads.csv                # All scraped items
  mercari_leads.json               # JSON format

lead_intake.csv                    # Top candidates appended here

reports/
  lead_XXXX_review.md              # Generated by manual_lead_review.py
```

---

## Next Steps

1. Set `APIFY_TOKEN` environment variable
2. Run `python3 scripts/mercari_apify_scraper.py`
3. Review `data/external_leads/mercari_leads.csv`
4. Run `python3 manual_lead_review.py` for top candidates
5. Check `reports/lead_*_review.md` for underwriting

---

**Integrated:** 2026-05-04  
**Status:** Ready for production use  
**Recommendation:** Run daily or weekly to catch new listings
