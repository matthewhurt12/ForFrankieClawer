# 2026-05-06 - Athens Food Google Actor

Matthew corrected the Athens food workflow: the spreadsheet is from someone
online and should be treated as a reference point, not Matthew's own trusted
opinion. For "go now" recommendations, current open/closed status must be
checked.

Added:

- `scripts/athens_food_google_check.py`

Actor:

- `nFJndFXA5zjCTuudP`

Use:

```powershell
python scripts\athens_food_google_check.py "Birdies" "Maepole" "Daily Grocery"
```

Rule: generate candidates from the spreadsheet, then verify the top few through
the Google actor before giving a final current recommendation.

Test result: Birdies came back with Google actor organic result text containing
`BIRDIES - CLOSED` and a result saying Birdies Market was closing/closed.
Maepole was the first checked candidate with open/hour signals after Birdies was
filtered out.
