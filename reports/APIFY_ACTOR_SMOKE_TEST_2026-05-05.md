# Apify Actor Smoke Test - 2026-05-05

**Purpose:** Verify the existing OpenClaw/Frankie Apify actors with tiny, cost-controlled runs.

**Security note:** Do not store Apify tokens in repo files. The token used for this test was supplied interactively and should be rotated because it was pasted into chat.

---

## Results

| Actor | Repo Purpose | Tiny Test Input | Status | Apify Usage | Decision |
|---|---|---|---|---:|---|
| `stealth_mode~mercari-product-search-scraper` | Mercari buy-side leads | 1 Mercari URL, 2 max items | Failed: actor rental required | $0.00 | Do not run until rented or replaced |
| `apify~facebook-marketplace-scraper` | Facebook local buy-side leads | 1 Athens search, 2 max items | Timed out, but produced sample rows | ~$3.10 | Pause; too expensive/risky as configured |
| `oTtB3VgfuE9GtxQt2` | eBay sold comps | 1 keyword, 14 days, 3 sold rows | Succeeded | ~$0.012 | Keep; core valuation actor |
| `RenntKrxUtdZQl1jH` | Reverb active context | 1 keyword, 2 listings | Succeeded | ~$0.009 | Keep as optional active context |
| `YJCnS9qogi9XxDgLB` | Generic Puppeteer scraper | 3 public pages, max 3 pages | Succeeded overall, weak data; Reverb blocked, EstateSales timed out | ~$0.006 | Not recommended for marketplace scraping |

---

## What Worked

### eBay Sold Comps

The sold-comps actor ran successfully and returned 3 sold rows for `Technics SL-1200`.

The cleaner wrote:

- `data/ebay_sold_comps_clean.csv`
- `reports/EBAY_SOLD_COMPS_CLEANING_001.md`

Cleaner result:

- 3 raw rows
- 2 valid full-unit rows
- 1 rejected row: `plinth`
- Model status: `LOW_CONFIDENCE` because fewer than 3 full-unit comps survived

This is the correct behavior. The system did not calculate max buy price because confidence was too low.

### Reverb

The Reverb actor ran quickly and cheaply. It returned active listings, but the first result was an accessory cable, so Reverb needs the same hard reject filter before it is trusted.

Use Reverb only as active context, not resale proof.

---

## What Failed Or Needs Caution

### Facebook Marketplace

The Facebook actor is dangerous at the moment.

Even with:

- 1 Athens search URL
- `maxItems: 2`
- 240 second timeout

It timed out and Apify reported about `$3.10` usage. It did return sample rows, but the cost/risk profile is not acceptable for frequent runs.

Recommendation:

- Do not run broad Facebook production jobs until the cost behavior is understood.
- If used, run one search at a time with an explicit manual approval step.
- Prefer existing saved CSV data for local pipeline testing.

### Mercari

The Mercari actor now returns:

`actor-is-not-rented`

So Mercari cannot run from this account unless that paid actor is rented or replaced with another working actor.

### Generic Puppeteer Scraper

The generic actor is not a good marketplace scraper:

- Craigslist returned only weak page-level data
- Reverb produced a 403
- EstateSales.net timed out
- A browser-mode attempt hit memory pressure at 512 MB

Recommendation:

- Do not use it for core lead generation.
- Keep only as a one-off fallback after dedicated actors fail.

---

## System Run

After the actor tests:

```bash
python scripts/clean_ebay_sold_comps.py --input %TEMP%\\ebay_sold_comps_smoke_20260505.json
python scripts/deal_desk_review.py
python scripts/photo_verification_queue.py
```

Output:

- `reports/DEAL_DESK_REVIEW_001.md`
- `reports/PHOTO_VERIFICATION_QUEUE_001.md`
- `reports/EBAY_SOLD_COMPS_CLEANING_001.md`
- `data/ebay_sold_comps_clean.csv`

Deal Desk loaded:

- 842 unique leads
- 1 model with some clean sold comp data
- 0 valid max-buy calculations, because the only sold-comp model had fewer than 3 clean full-unit comps

This confirms the safety gate works.

---

## Recommended Actor Set

Use now:

1. eBay Sold Comps actor for exact verified model candidates.
2. Reverb actor for active music/audio context only.
3. Existing local Mercari/Facebook CSVs for analysis while actor cost/rental issues are sorted.

Pause:

1. Facebook actor until cost is under control.
2. Mercari actor until actor rental/replacement is decided.
3. Generic Puppeteer/AI scrapers except one-off fallback tests.

---

## Safe Operating Rule

For Apify runs, Frankie should default to:

- one actor
- one search URL or keyword
- max 2-3 items
- no raw JSON committed
- stop immediately if usage exceeds expected pennies
- run Deal Desk only after normalized data and sold-comp cleaning
