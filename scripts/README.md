# Scripts Index

Use this file before guessing which script to run.

## Active Entry Points

- `intent_router.py`
  - Routes Matthew's exact request to the best existing skill before Frankie
    invents a new strategy.
  - Use `python scripts\intent_router.py "Athens marketplace good deals in my area"`.
  - Use `--self-test` to verify common intent mappings.

- `frankie_start.py`
  - First command after pulling the repo.
  - Runs workspace health, skill listing, and safe pipeline dry run.

- `athens_food.py`
  - Recommends Athens restaurants from Matthew's spreadsheet-derived CSV.
  - Supports mood, cuisine, area, price, speed, exclusions, and random picks.

- `athens_food_google_check.py`
  - Uses Apify Google search actor for current restaurant open/closed, review,
    and menu signals.

- `athens_food_go_now.py`
  - Safer final-answer restaurant picker.
  - Ranks local candidates, then verifies open/closed and condition mismatches
    through the Google actor before picking.

- `refresh_athens_restaurants.py`
  - Refreshes `data/restaurants/athens_restaurants.csv` from public Athens food
    directories.
  - Preserves spreadsheet rows and adds new places as lower-confidence
    `directory-import` entries.

- `test_athens_food_filters.py`
  - Local regression checks for the expanded restaurant list.
  - Confirms imports do not swamp rated rows, strict filters still work, and
    closed rows stay suppressed.

- `smartcore_billing.py`
  - Generates SmartCore invoice PDFs, HTML previews, and email draft packages.
  - Never sends email.

- `run_arbitrage_pipeline.py`
  - Safe default arbitrage pipeline.
  - Local-only unless `--collect` is passed.

- `freebie_radar.py`
  - Separate Facebook/Mercari free and cheap local listing radar.
  - Local-only unless `--collect` is passed.

- `overwatch_daily.py`
  - Wrapper for the real Overwatch WiFi monitor repo at
    `C:\Users\matth\overwatch-wifi-monitor`.
  - Use `status` first, then `--no-write --json` for daily review.

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
- `athens_food.py`
- `athens_food_google_check.py`
- `athens_food_go_now.py`
- `refresh_athens_restaurants.py`
- `test_athens_food_filters.py`
- `deal_desk_review.py`
- `photo_verification_queue.py`
- `update_lead_history.py`
- `freebie_radar.py`
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
