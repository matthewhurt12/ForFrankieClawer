# Athens Restaurants

`athens_restaurants.csv` started as Matthew's spreadsheet export:

`C:\Users\matth\Downloads\athens_restaurant_list.xlsx`

The CSV now also includes public directory imports from OpenStreetMap/Overpass
and Visit Athens. Imported rows are marked `Directory Import` and
`directory-import`; they are discovery candidates, not Matthew-rated favorites.

The CSV adds derived `tags` so Frankie can recommend restaurants by mood,
cuisine, area, speed, price, source confidence, or random pick.

Primary command:

```powershell
python scripts\athens_food.py recommend
```

Random pick:

```powershell
python scripts\athens_food.py random
```

Exclude categories:

```powershell
python scripts\athens_food.py recommend --mood "cheap quick" --exclude-cuisine brewery
python scripts\athens_food.py random --exclude-cuisine breakfast --exclude-area dt
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --no-fast-food --no-bar-food
```

Restaurants marked closed/inactive in notes are suppressed by default.

Refresh/expand the list:

```powershell
python scripts\refresh_athens_restaurants.py
```

Latest refresh report:

`reports/ATHENS_RESTAURANT_REFRESH_001.md`

Roadmap for future review/menu enrichment:

`docs/ATHENS_FOOD_ROADMAP.md`
