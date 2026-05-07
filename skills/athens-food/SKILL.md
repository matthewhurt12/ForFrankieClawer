# athens-food

Use this skill when Matthew asks where to eat in Athens, wants a random
restaurant pick, asks for a cuisine/mood recommendation, or mentions being in
the mood for food.

Source of truth:

- `data/restaurants/athens_restaurants.csv`

Important: this spreadsheet came from an online Athens list. Treat it as a
reference shortlist, not Matthew's personal taste gospel.

## Safe Commands

Ranked default:

```powershell
python scripts\athens_food.py recommend
```

Spontaneous random pick:

```powershell
python scripts\athens_food.py random
```

Mood/cuisine examples:

```powershell
python scripts\athens_food.py recommend --mood "date night"
python scripts\athens_food.py recommend --mood "cheap quick"
python scripts\athens_food.py recommend --mood "vegetarian patio"
python scripts\athens_food.py recommend --cuisine mexican
python scripts\athens_food.py recommend --area "five points" --min-rating 4
```

Exclude things Matthew does not want:

```powershell
python scripts\athens_food.py recommend --mood "cheap quick" --exclude-cuisine brewery
python scripts\athens_food.py recommend --mood "date night" --exclude-area dt
python scripts\athens_food.py recommend --cuisine mexican --exclude "downtown" --exclude-tag bar
python scripts\athens_food.py random --exclude-cuisine breakfast --exclude-cuisine brewery
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --exclude-cuisine burgers --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco --exclude burger
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --no-fast-food --no-bar-food --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco
```

Discovery:

```powershell
python scripts\athens_food.py list cuisines
python scripts\athens_food.py list areas
python scripts\athens_food.py list moods
```

Refresh the restaurant list:

```powershell
python scripts\refresh_athens_restaurants.py
python scripts\test_athens_food_filters.py
```

This pulls public OpenStreetMap/Overpass and Visit Athens directory records,
preserves the original spreadsheet-derived rows, and adds new places as
`Directory Import` / `directory-import` rows. Treat imported rows as discovery
candidates until Matthew tries or rates them. After every refresh, run the filter
test before trusting recommendations.

Current open/closed verification through the Apify Google search actor:

```powershell
python scripts\athens_food_google_check.py "Birdies" "Maepole" "Daily Grocery"
python scripts\athens_food_google_check.py "Maepole" --no-fast-food --no-bar-food
python scripts\athens_food_go_now.py --mood "lunch hot fresh" --no-fast-food --no-bar-food --exclude taco --exclude sushi
```

Use this before presenting a "go now" top pick when Matthew asks about lunch,
dinner, today, open now, hours, or says a prior recommendation is closed.

Go-now workflow:

1. Generate 5-8 candidates from the sheet.
2. Prefer `athens_food_go_now.py` when the pick is for right now.
3. Reject `CLOSED_OR_INACTIVE`, `CLOSED_NOW`, `LIKELY_CLOSED_NOW`, and
   `CONDITION_MISMATCH`.
4. If Matthew says no fast food, treat that as no fast food, no fast casual,
   no counter service, and no quick-service wording.
5. Recommend the first remaining candidate and mention the verification signal.

## Output

The script writes:

- `reports/ATHENS_FOOD_LAST.md`

Use the top pick plus a few backup picks. Keep the response fun and human, but
do not bury the actual recommendation.

Good style:

- Name the pick first.
- Say why it fits the mood.
- Include rating, cuisine, area, speed, price, and Matthew's previous order.
- Give 2-4 backups when helpful.
- Honor exclusions such as cuisine, area, speed, tag, or general text.
- Closed/inactive restaurants are excluded by default when the sheet notes that
  they are closed, catering-only, or missed. Use `--include-closed` only for
  history/list maintenance.
- Directory imports are useful for discovery, but they are not Matthew-rated
  favorites. Prefer rated rows unless the user's filters point at an imported
  candidate, then verify current details before presenting it.

## Common Mood Words

- `random`, `spontaneous`
- `cheap`, `budget`
- `quick`, `fast`, `takeout`
- `date night`, `fancy`
- `vegetarian`, `veggie`, `healthy`
- `breakfast`, `brunch`, `coffee`
- `dessert`, `sweet`
- `drinks`, `bar`, `beer`
- `patio`, `outside`
- `lunch`, `hot`
- `classic`, `local`, `vibes`

## Rules

- This is local recommendation help, not a live web search.
- If Matthew asks for current hours, closures, menus, or today-specific info,
  verify online before answering.
- For current-hours checks, use `scripts/athens_food_google_check.py` with the
  top few candidates and choose the first candidate that is not closed/closed
  now.
- For final "go now" answers, use `scripts/athens_food_go_now.py` so the last
  step checks both open/closed status and Matthew's conditions against Google
  snippets before presenting the pick.
- When Matthew says no fast food, do not recommend places Google describes as
  fast food, fast casual, quick service, or counter service.
- If the top pick may be closed or the sheet hints it is inactive, verify before
  recommending it.
- If the list has no match, say so and offer the closest alternatives.
- For review/menu enrichment ideas, read `docs/ATHENS_FOOD_ROADMAP.md`.
