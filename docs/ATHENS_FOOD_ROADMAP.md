# Athens Food Roadmap

Future ideas for the Athens food skill. Keep the current recommender simple and
spreadsheet-first; add these only when Matthew asks to enrich the list.

## Current System

- Source of truth: `data/restaurants/athens_restaurants.csv`
- Recommender: `scripts/athens_food.py`
- Refresh/import: `scripts/refresh_athens_restaurants.py`
- Skill: `skills/athens-food/SKILL.md`
- Last output: `reports/ATHENS_FOOD_LAST.md`

## Context Improvements

Add optional context flags later:

- time of day: breakfast / lunch / dinner / late-night
- weather: hot, rainy, cold, patio-friendly
- season: summer lighter picks, winter comfort picks
- group mode: solo, date, friends, family
- travel mode: downtown walking, five points, near home, avoid parking pain

Current workaround:

```powershell
python scripts\athens_food.py recommend --mood "lunch hot quick fresh"
```

Current-hours verification:

```powershell
python scripts\athens_food_google_check.py "Birdies" "Maepole" "Daily Grocery"
python scripts\athens_food_go_now.py --mood "lunch hot fresh" --no-fast-food --no-bar-food
```

No fast food / no bar food example:

```powershell
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --no-fast-food --no-bar-food
```

Directory refresh:

```powershell
python scripts\refresh_athens_restaurants.py
python scripts\test_athens_food_filters.py
```

This adds public OpenStreetMap/Overpass and Visit Athens records as
lower-confidence imports. It should be run occasionally, not every food pick.
Run the filter test after each refresh before trusting the larger list.

## Apify Review / Menu Enrichment

Potential actors to test later:

- Google Maps places/details actors for ratings, review counts, hours, photos,
  and place metadata.
- Google Maps reviews actors for recent review text and sentiment.
- TripAdvisor reviews actors for richer restaurant review history.
- Generic website crawler for restaurant websites and menu pages.

Candidate Apify actors found during research:

- `nFJndFXA5zjCTuudP`
  - Google Search Results / AI Search actor currently used for lightweight
    restaurant status checks, snippets, reviews, and menu discovery.
- `automation-lab/google-maps-reviews-scraper`
  - Google Maps review extraction with optional sentiment/topic analysis.
- `scrapemint/google-maps-scraper`
  - Place rows with ratings, reviews, contact data, and optional review/image
    enrichment.
- `kaix/google-maps-places-scraper`
  - Google Maps place data with review summary and image/menu categories.
- `web_wanderer/tripadvisor-reviews-scraper`
  - TripAdvisor review URLs or location IDs with review caps and filters.

## Safe Test Plan

1. Add stable restaurant IDs / Google Maps URLs to the CSV manually for 5-10
   favorite restaurants.
2. Run a tiny Apify test, max 5 restaurants and max 5-10 reviews each.
3. Save enriched data separately under `data/restaurants/enrichment/`.
4. Summarize only useful fields:
   - current rating
   - review count
   - recent review themes
   - common complaints
   - hours/open-now if reliable
   - menu URL if found
5. Do not let web reviews override Matthew's own ratings; use them as context.

## Menu Plan

Menus are messier than reviews. Best first step is not full menu scraping. Use:

- official website menu URL if available
- Google Maps menu link if available
- short manual notes for favorites

Only scrape full menus if Matthew wants a nutrition/menu-aware recommender.

## Rules

- Use Matthew's sheet first.
- Treat the current spreadsheet as a reference list from someone online, not
  confirmed Matthew taste data.
- Browse or scrape only for current hours, closures, reviews, menu URLs, or
  specific live details.
- Closed/inactive restaurants should stay suppressed by default.
- For "go now" answers, run the final Google condition gate and reject places
  described as fast food, fast casual, quick service, or counter service when
  Matthew asked for no fast food.
- Keep Apify runs small and capped.
- Do not store reviewer personal data unless it is truly needed.
