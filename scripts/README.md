# Scripts Index

Use this file before guessing which script to run.

## Active Entry Points

- `frankie_start.py`
  - First command after pulling the repo.
  - Runs workspace health, skill listing, and safe pipeline dry run.

- `run_arbitrage_pipeline.py`
  - Safe default arbitrage pipeline.
  - Local-only unless `--collect` is passed.

- `run_ebay_sold_comps.py`
  - Exact-model eBay sold comps runner.
  - Refuses broad keywords.

- `list_skills.py`
  - Prints the local skill manifest.

- `workspace_doctor.py`
  - Checks navigation, manifests, active scripts, gitignore, and possible token
    leaks.

## Active Support Modules

- `arbitrage_logic.py`
- `deal_desk_review.py`
- `photo_verification_queue.py`
- `update_lead_history.py`
- `clean_ebay_sold_comps.py`
- `mercari_production_run_001.py`
- `facebook_marketplace_run_002.py`

## Legacy / Reference Scripts

The older browser/OCR/direct scraping experiments are kept for history, but they
are not the current workflow:

- `visual_browser_test*.py`
- `visual_ocr_test_003.py`
- `search_craigslist.py`
- `reverb_test_limited.py`
- `ai_scraper_test.py`
- `facebook_marketplace_run_001.py`
- `mercari_apify_scraper.py`
- `ebay_*_test.py`
- `apify_*debug*.py`

Do not run legacy scripts unless Matthew explicitly asks to revisit that path.
