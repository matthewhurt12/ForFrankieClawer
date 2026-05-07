# 2026-05-06 - Athens Food Test

Matthew tested the Athens food system with a realistic prompt:

- lunchtime
- hot out
- no burgers
- no tacos
- no sushi

Updated the recommender to recognize `lunch` and `hot` as mood context. Added
`docs/ATHENS_FOOD_ROADMAP.md` for future Apify review/menu enrichment.

When excluding sushi, also consider excluding `poke` because it may feel too
close to sushi for the intent.

Follow-up: Matthew added no fast food and no bar food, and asked that top picks
not be closed. The test exposed The Grit as a stale top pick because the sheet
notes say "I MISS IT SO MUCH." Closed/inactive notes should suppress rows by
default, and top picks should be verified online when closure/current status
matters.
