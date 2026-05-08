# Command Router

When Matthew uses a slash command or a short workflow name, route it here first.

## Intent Router First

Before inventing a new approach, classify Matthew's intent and check whether an
existing skill already covers the job.

```powershell
python scripts\intent_router.py "Matthew's exact request"
```

If the router returns a skill, open that `SKILL.md` and use its existing
workflow. Browser/search/manual scraping is a fallback, not the first move.

## Slash Commands

| Command | Skill | File | Output |
|---|---|---|---|
| `/signals` | `signals` | `skills/signals/SKILL.md` | Full Signal Engine report |
| `/radar` | `radar` | `skills/radar/SKILL.md` | Quick current signal scan |
| `/bigpic` | `bigpic` | `skills/bigpic/SKILL.md` | Strategic synthesis |
| `/ideas` | `ideas` | `skills/ideas/SKILL.md` | Practical build and business ideas |

## Workflow Triggers

| User Says | Use | File |
|---|---|---|
| unclear request, use your skills/tools, what skill should handle this, route this | `intent-router` | `skills/intent-router/SKILL.md` |
| where should I eat, Athens food, restaurant, cuisine, food mood, random restaurant, spontaneous restaurant | `athens-food` | `skills/athens-food/SKILL.md` |
| voice file, audio file, read it to me, ElevenLabs, Eleven Labs, TTS, sag, narrate, storytime | `voice-output` | `skills/voice-output/SKILL.md` |
| arbitrage, deal desk, resale leads, resale marketplace, flip, profit, Mercari, Facebook Marketplace with sold comps | `arbitrage-deal-desk` | `skills/arbitrage-deal-desk/SKILL.md` |
| Athens marketplace, marketplace near me, marketplace in my area, local marketplace, local deals, good deals in my area, freebie radar, free Facebook Marketplace, curb alert, free pickup, cheap local listings, daily free scan | `freebie-radar` | `skills/freebie-radar/SKILL.md` |
| SmartCore billing, invoices, billing email, vehicle tracking bill, asset tracking bill, building monitoring bill, quote, proposal | `smartcore-billing` | `skills/smartcore-billing/SKILL.md` |
| Apify actors, scrapers, generic scraper, website scraper, actor catalog | `apify-actors` | `skills/apify-actors/SKILL.md` |
| Overwatch, WiFi surveillance, WiFi monitor, RF monitoring, local signal environment, daily Overwatch check | `overwatch-rf` | `skills/overwatch-rf/SKILL.md` |
| map this page, browser automation, find buttons, inspect site | `page-map` | `skills/page-map/SKILL.md` |
| signal report, signals, current tech signals | `signals` | `skills/signals/SKILL.md` |
| big picture, thesis, strategic shift | `bigpic` | `skills/bigpic/SKILL.md` |
| radar, what happened, quick scan | `radar` | `skills/radar/SKILL.md` |
| ideas, opportunities, what should I build | `ideas` | `skills/ideas/SKILL.md` |

## Default Behavior

If a command is not recognized:

1. Search `skills/manifest.json`.
2. Search `skills/*/SKILL.md`.
3. Search `memory/` for older workflow notes.
4. Only then tell Matthew it is missing.

If the command is close to a known command, use the likely skill and mention the
match briefly.

Terminal helper:

```powershell
python scripts\list_skills.py
```

## Maintenance Commands

| Command | Purpose |
|---|---|
| `python scripts\workspace_doctor.py` | Check navigation files, skill manifests, active Python scripts, `.gitignore`, and token-shaped strings |
| `python scripts\intent_router.py "Athens marketplace good deals in my area"` | Route an ambiguous Matthew request to the best existing skill |
| `python scripts\intent_router.py --self-test` | Verify common prompt intents map to the correct skills |
| `python scripts\athens_food.py recommend` | Recommend an Athens restaurant from Matthew's list |
| `python scripts\athens_food.py random` | Pick a spontaneous Athens restaurant from Matthew's list |
| `python scripts\athens_food_go_now.py --mood "lunch hot fresh" --no-fast-food --no-bar-food` | Pick a restaurant only after Google open/closed and condition checks |
| `python scripts\refresh_athens_restaurants.py` | Refresh the Athens restaurant CSV from public directory sources |
| `python scripts\test_athens_food_filters.py` | Verify the expanded restaurant list still filters cleanly |
| `Get-Command sag -ErrorAction SilentlyContinue` | Check whether the local ElevenLabs voice helper is available |
| `python scripts\smartcore_billing.py validate` | Check SmartCore billing config without generating or sending anything |
| `python scripts\smartcore_billing.py plan --invoice-date YYYY-MM-DD --service-months YYYY-MM --start-number N` | Preview SmartCore invoices before creating PDFs |
| `python scripts\run_arbitrage_pipeline.py --dry-run` | Show the local arbitrage pipeline steps without calling paid actors |
| `python scripts\run_arbitrage_pipeline.py` | Refresh local-only lead history and reports |
| `python scripts\freebie_radar.py` | Refresh local-only free/cheap marketplace radar from existing CSVs |
| `python scripts\freebie_radar.py --collect --sources facebook --dry-run` | Preview a paid Facebook freebie scan without running it |
| `python scripts\overwatch_daily.py status` | Check that Frankie can find the real Overwatch WiFi monitor repo |
| `python scripts\overwatch_daily.py --no-write --json` | Generate a private Overwatch daily summary without writing a report |
