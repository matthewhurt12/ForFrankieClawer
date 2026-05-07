# Athens Food Skill

Frankie can recommend restaurants from Matthew's Athens restaurant spreadsheet.
The spreadsheet is a reference list from someone online, not confirmed Matthew
ratings.

## Files

- Skill: `skills/athens-food/SKILL.md`
- Script: `scripts/athens_food.py`
- Verified go-now script: `scripts/athens_food_go_now.py`
- Refresh script: `scripts/refresh_athens_restaurants.py`
- Filter test script: `scripts/test_athens_food_filters.py`
- Data: `data/restaurants/athens_restaurants.csv`
- Last report: `reports/ATHENS_FOOD_LAST.md`

## Commands

```powershell
python scripts\athens_food.py recommend
python scripts\athens_food.py random
python scripts\athens_food.py recommend --mood "vegetarian patio"
python scripts\athens_food.py recommend --cuisine mexican
python scripts\athens_food.py recommend --mood "cheap quick" --exclude-cuisine brewery
python scripts\athens_food.py random --exclude-cuisine breakfast --exclude-area dt
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --exclude-cuisine burgers --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco --exclude burger
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --no-fast-food --no-bar-food --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco
python scripts\athens_food.py list cuisines
python scripts\athens_food_google_check.py "Birdies" "Maepole" "Daily Grocery"
python scripts\athens_food_google_check.py "Maepole" --no-fast-food --no-bar-food
python scripts\athens_food_go_now.py --mood "lunch hot fresh" --no-fast-food --no-bar-food --exclude taco --exclude sushi
python scripts\refresh_athens_restaurants.py
python scripts\test_athens_food_filters.py
```

## How It Picks

The recommender uses:

- Matthew's star ratings
- cuisine
- speed
- average price
- area
- what Matthew got
- notes
- derived mood tags
- optional exclusions for cuisines, areas, speeds, tags, or general text
- default suppression of sheet-marked closed/inactive restaurants
- optional Apify Google search actor verification for current hours/open-now
  checks
- lower-confidence `Directory Import` rows from public directory refreshes

For "right now" recommendations, do not stop at the spreadsheet rank. Verify the
top candidates and choose the first one that is not closed/closed-now and does
not violate the stated conditions.

Use `athens_food_go_now.py` for final answers when Matthew asks for a place to
go now. It runs the spreadsheet ranking, then a Google actor check, then rejects
closed restaurants and condition mismatches like "fast food" or "fast casual"
when `--no-fast-food` is requested.

`refresh_athens_restaurants.py` expands the list from OpenStreetMap/Overpass and
Visit Athens. Imported rows are discovery candidates, not Matthew's ratings.

Run `test_athens_food_filters.py` after refreshing. It catches the main large
list failure modes: imported rows drowning out rated rows, duplicate pressure,
strict filter leakage, imprecise query matches, and closed-row leaks.

Random mode is weighted, not totally blind. It still favors stronger fits and
higher-rated places, but leaves room for spontaneous picks.

## Roadmap

See `ATHENS_FOOD_ROADMAP.md` for future Apify review/menu enrichment ideas.
