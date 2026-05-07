# Frankie Handoff

This is the short version for Frankie/OpenClaw after pulling the repo.

## First Command

Run this before doing project work:

```powershell
python scripts\frankie_start.py
```

That command is local-only. It checks the workspace, prints the skill list, and
shows the safe arbitrage commands. It does not call Apify or spend money.

If the startup check fails, open:

- `reports/WORKSPACE_HEALTH_LAST.md`
- `START_HERE.md`
- `COMMANDS.md`

Fix navigation or safety issues before running paid collection.

## What This Workspace Is

This workspace has two main jobs:

1. Keep Frankie oriented through memory, skills, commands, and project notes.
2. Run Matthew's retro tech arbitrage Deal Desk.

Start with these files:

- `START_HERE.md` - main map
- `COMMANDS.md` - slash command and workflow router
- `skills/manifest.json` - machine-readable skill index
- `skills/<name>/SKILL.md` - detailed skill instructions
- `projects/` - durable project cards
- `reports/OPENCLAW_ARBITRAGE_RUNBOOK.md` - arbitrage operating manual

## Skills To Recognize

- `/signals` -> `skills/signals/SKILL.md`
- `/radar` -> `skills/radar/SKILL.md`
- `/bigpic` -> `skills/bigpic/SKILL.md`
- `/ideas` -> `skills/ideas/SKILL.md`
- Athens food, where should I eat, restaurant, cuisine, random restaurant
  -> `skills/athens-food/SKILL.md`
- Voice file, read it to me, ElevenLabs, TTS, `sag`, narrate, storytime
  -> `skills/voice-output/SKILL.md`
- Arbitrage, deal desk, resale, Mercari, Facebook Marketplace, eBay sold comps
  -> `skills/arbitrage-deal-desk/SKILL.md`
- Freebie radar, free Facebook Marketplace, curb alert, free pickup, cheap
  local listings -> `skills/freebie-radar/SKILL.md`
- Browser/page automation -> `skills/page-map/SKILL.md`
- SmartCore invoices, billing PDFs, billing email, quotes/proposals
  -> `skills/smartcore-billing/SKILL.md`
- Apify actors, scraper choices, generic website scraping
  -> `skills/apify-actors/SKILL.md`

Do not say a skill is missing until `COMMANDS.md`, `skills/manifest.json`, and
`skills/*/SKILL.md` have been checked.

## Arbitrage Default Workflow

When Matthew asks for current recommendations from existing data:

```powershell
python scripts\run_arbitrage_pipeline.py
```

Open:

- `reports/DEAL_DESK_REVIEW_001.md`
- `reports/PHOTO_VERIFICATION_QUEUE_001.md`
- `reports/PIPELINE_RUN_LAST.md`

When Matthew explicitly approves a fresh paid collection:

```powershell
$env:APIFY_TOKEN = "real-token-from-environment-or-user"
python scripts\run_arbitrage_pipeline.py --collect
```

Do not print the token. Do not commit the token.

When a specific exact model needs sold comps:

```powershell
python scripts\run_ebay_sold_comps.py --keywords "Kenwood KR-4600" --clean --merge --refresh-reports
```

Sold comp searches must be exact-model searches. Do not use broad searches such
as `Pioneer receiver`, `turntable`, or `vintage stereo`.

## Decision Rules

Allowed verdicts:

- `INVESTIGATE`
- `WATCH`
- `SKIP`

Never output `BUY`.

Never estimate profit from active listings.

Only calculate max buy price when clean sold comps exist and condition risk is
included.

Seller messages are drafts for Matthew only. Do not automate seller contact.

## Athens Food Workflow

When Matthew asks where to eat in Athens:

```powershell
python scripts\athens_food.py recommend
```

For a spontaneous pick:

```powershell
python scripts\athens_food.py random
```

To refresh/expand the list before future improvements:

```powershell
python scripts\refresh_athens_restaurants.py
python scripts\test_athens_food_filters.py
```

The refresh keeps Matthew's spreadsheet-style rows and adds public directory
records as lower-confidence `Directory Import` rows. Do not treat imported rows
as Matthew's personal ratings. Always run the filter test after a refresh.

For moods or cuisines:

```powershell
python scripts\athens_food.py recommend --mood "cheap quick"
python scripts\athens_food.py recommend --mood "date night"
python scripts\athens_food.py recommend --cuisine mexican
```

Open `reports/ATHENS_FOOD_LAST.md` and answer with the top pick plus a few
backup options. The spreadsheet is a reference list from someone online, not
confirmed Matthew taste data. If he asks about current hours, menus, closures,
or today-specific availability, verify online before answering.

For "go now" recommendations, use the verified final-answer command:

```powershell
python scripts\athens_food_go_now.py --mood "lunch hot fresh" --no-fast-food --no-bar-food
```

That command checks the final candidates with the Apify Google actor and rejects
closed places plus condition mismatches. If Matthew says no fast food, that also
means no fast casual, quick-service, or counter-service wording.

Athens food supports exclusions:

```powershell
python scripts\athens_food.py recommend --mood "cheap quick" --exclude-cuisine brewery
python scripts\athens_food.py random --exclude-cuisine breakfast --exclude-area dt
```

For hot/lunch/weather-style context, include it in the mood:

```powershell
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --exclude-cuisine burgers --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco --exclude burger
python scripts\athens_food.py recommend --mood "lunch hot quick fresh" --no-fast-food --no-bar-food --exclude-cuisine mexican --exclude-cuisine japanese --exclude-cuisine poke --exclude sushi --exclude taco
```

Future review/menu enrichment notes live in `docs/ATHENS_FOOD_ROADMAP.md`.
If the top pick might be closed, verify online before recommending it.

Current open/closed verification command:

```powershell
python scripts\athens_food_google_check.py "Birdies" "Maepole" "Daily Grocery"
python scripts\athens_food_google_check.py "Maepole" --no-fast-food --no-bar-food
```

This uses the Apify Google search actor and requires `APIFY_TOKEN`. Pick the
first candidate that does not come back closed/closed-now or as a condition
mismatch.

## Voice Output Workflow

When Matthew asks for a voice file or audio version:

```powershell
Get-Command sag -ErrorAction SilentlyContinue
```

If available, open `skills/voice-output/SKILL.md`, run `sag --help`, and save
generated files under `data/voice_outputs/`. If not available, say the local
ElevenLabs helper is not on PATH and provide a voice-ready script instead.

## Freebie Radar Workflow

When Matthew asks for free Marketplace finds, curb alerts, pickup-only items, or
cheap local listings:

```powershell
python scripts\freebie_radar.py
```

Open:

- `reports/FREEBIE_RADAR_LAST.md`
- `data/freebie_radar/freebie_radar_latest.csv`
- `data/freebie_radar/freebie_radar_history.csv`

The default is local-only. A fresh paid Facebook scan requires explicit approval:

```powershell
$env:APIFY_TOKEN = "real-token-from-environment-or-user"
python scripts\freebie_radar.py --collect --sources facebook
```

Treat `$1` listings as price bait unless the title clearly says free, curb
alert, pickup only, or similar. Mercari is optional and should be included only
when Matthew asks for cheap online listings too.

## SmartCore Billing Workflow

When Matthew asks for SmartCore invoices or monthly billing:

```powershell
python scripts\smartcore_billing.py validate
```

Preview before writing files:

```powershell
python scripts\smartcore_billing.py plan --invoice-date YYYY-MM-DD --service-months YYYY-MM --start-number N
```

Generate PDFs, HTML previews, and email draft packages:

```powershell
python scripts\smartcore_billing.py generate --invoice-date YYYY-MM-DD --service-months YYYY-MM --start-number N
```

Generated billing packages are local-only and go under
`data/smartcore_billing/generated/`. Do not send invoice emails until Matthew
confirms recipients and attachments.

## Apify Actor Workflow

When Matthew asks what actors Frankie can use or wants a generic website
scraper, open:

```text
skills/apify-actors/SKILL.md
docs/APIFY_ACTOR_CATALOG.md
config/apify_actor_catalog.json
```

Account-specific rented/plan actors require `APIFY_TOKEN` access. Do not guess
account ownership from public Apify Store pages.

## If You Are Lost

Run:

```powershell
python scripts\frankie_start.py
```

Then read:

1. `START_HERE.md`
2. `COMMANDS.md`
3. The matching skill file
4. The matching project card in `projects/`

Keep the answer to Matthew action-focused: what changed, what to open, and what
needs his decision.
