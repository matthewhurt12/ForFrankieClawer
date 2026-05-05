# Vintage Audio Arbitrage System

Automated lead generation and underwriting for vintage audio equipment flipping.

## 🚀 Quick Start

**Read this first:** [`reports/HANDOFF_TO_CODEX.md`](reports/HANDOFF_TO_CODEX.md)

## 📊 Current Status

- **Data Collection:** Mercari + Facebook Marketplace (working)
- **Lead Analysis:** Equipment filtering + photo verification (working)
- **eBay Context:** Active listings via Browse API (working, free)
- **Sold Comps:** Ready to test when Apify limit resets (HIGH PRIORITY)

**Leads Collected:** 842 raw → 419 equipment → classified by missing info

## 🎯 Purpose

Find underpriced vintage audio on marketplaces. Validate with eBay sold comps. Generate actionable investigation reports.

**Output:** INVESTIGATE / WATCH / SKIP (never automatic BUY)

## 📁 Key Files

- **Handoff:** [`reports/HANDOFF_TO_CODEX.md`](reports/HANDOFF_TO_CODEX.md) - START HERE
- **System:** [`reports/APIFY_SYSTEM_SOURCE_OF_TRUTH.md`](reports/APIFY_SYSTEM_SOURCE_OF_TRUTH.md)
- **Leads:** [`reports/PHOTO_VERIFICATION_QUEUE_001.md`](reports/PHOTO_VERIFICATION_QUEUE_001.md)

## 🛠️ Setup

```bash
# 1. Set up eBay credentials
mkdir -p credentials
# Add ebay-production.json with your API keys

# 2. Set Apify token
export APIFY_TOKEN='your-token'

# 3. Run data collection
python3 scripts/facebook_marketplace_run_002.py

# 4. Analyze leads
python3 scripts/equipment_only_analysis.py
python3 scripts/photo_verification_queue.py
```

## 🎓 Architecture

**Layer 1:** Apify actors scrape marketplaces  
**Layer 2:** Python normalizes and deduplicates  
**Layer 3:** eBay API validates market value  
**Layer 4:** Markdown reports with actionable leads

## ⚠️ Critical Rules

- ❌ NO profit estimates without sold comps
- ❌ NO automatic buy decisions
- ✓ Exact model required before estimates
- ✓ Verify from photos (not parts/accessories)
- ✓ Factor in fees + shipping + risk

## 🎯 Next Tasks

1. **Test eBay Sold Comps actor** (HIGH PRIORITY)
2. **Improve lead scoring algorithm** (see handoff doc)
3. **Integrate sold comps into underwriting**

## 📚 Documentation

- [`docs/EBAY_SOLD_COMPS_INTEGRATION.md`](docs/EBAY_SOLD_COMPS_INTEGRATION.md) - Sold comps plan
- [`docs/BEST_FIRST_SEARCH_STRATEGY.md`](docs/BEST_FIRST_SEARCH_STRATEGY.md) - Search optimization
- [`docs/APIFY_TESTING_PRIORITY.md`](docs/APIFY_TESTING_PRIORITY.md) - Test priority order

## 💰 Cost

**Apify Free Tier:** $5/month  
**Recommended:** 2-3x/week runs = $2-3/month

## 🤝 Contributing

See [`reports/HANDOFF_TO_CODEX.md`](reports/HANDOFF_TO_CODEX.md) for full context.

## 📝 License

Private project - not for public distribution.

---

**Status:** Functional MVP, ready for sold comp integration + improved scoring
