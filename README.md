# Retro Tech Arbitrage Deal Desk

Apify collects a small batch of marketplace leads. Local Python scripts dedupe,
filter, detect exact models, clean eBay sold comps, and produce action reports.

The system is built for Matthew and Frankie/OpenClaw. It optimizes for action
quality, not lead volume.

## Start Here

If you are Frankie/OpenClaw after pulling this repo, run:

```powershell
python scripts\frankie_start.py
```

Then read `FRANKIE_HANDOFF.md`.

Use the one-command runner:

```powershell
python scripts\run_arbitrage_pipeline.py
```

That default command is local-only. It does not call paid Apify actors. It
updates history and regenerates:

- `reports/DEAL_DESK_REVIEW_001.md`
- `reports/PHOTO_VERIFICATION_QUEUE_001.md`
- `reports/LEAD_HISTORY_UPDATE_001.md`
- `reports/PIPELINE_RUN_LAST.md`

To collect fresh marketplace leads, Matthew must explicitly approve a paid run:

```powershell
$env:APIFY_TOKEN = "your-token"
python scripts\run_arbitrage_pipeline.py --collect
```

Mercari and Facebook are run in parallel when `--collect` is used. Do not run
two Mercari jobs or two Facebook jobs at the same time.

## What It Looks For

Current lanes:

- Vintage stereo receivers, cassette decks, turntables
- RadioShack / Realistic stereo gear
- Nintendo Wii, Wii U, GameCube, N64, NES/SNES
- PlayStation 2/3, Sega Dreamcast, Genesis, original Xbox / Xbox 360
- Old Apple gear: iMac G3/G4/G5, Power Mac G4, Macintosh Classic/SE/Plus, Apple II
- Portable retro audio: iPod Classic/Mini, Walkman, Discman, MiniDisc

Avoid:

- Parts, manuals, bulbs, LED kits, decals, faceplates
- Single game discs unless Matthew asks
- Empty boxes, case-only listings, controller-only listings
- Cables, chargers, adapters, remotes-only
- Broad sold-comp searches like `Pioneer receiver`

## Sold Comps

Sold comps are the resale proof layer. Active listings are context only.

Run sold comps only for exact model candidates:

```powershell
$env:APIFY_TOKEN = "your-token"
python scripts\run_ebay_sold_comps.py --keywords "Kenwood KR-4600" "Apple Power Mac G4" --clean --merge --refresh-reports
```

Safety rules built into the runner:

- Max 6 keywords per actor run
- Refuses generic broad searches
- Sanitizes raw actor output before saving
- Cleans noisy sold comps before underwriting
- Merges clean rows into `data/ebay_sold_comps_clean.csv`

## Verdict Rules

The only allowed lead verdicts are:

- `INVESTIGATE`
- `WATCH`
- `SKIP`

Never output `BUY`. Never estimate profit from active listings. Only calculate
max buy price when clean sold comps are valid enough for underwriting.

## Key Files

- `reports/OPENCLAW_ARBITRAGE_RUNBOOK.md` - handoff guide for Frankie
- `config/marketplace_sources.json` - actor IDs, limits, and search terms
- `scripts/run_arbitrage_pipeline.py` - safe one-command pipeline
- `scripts/run_ebay_sold_comps.py` - exact-model sold comp actor runner
- `scripts/arbitrage_logic.py` - shared filtering, model detection, scoring, underwriting
- `reports/DEAL_DESK_REVIEW_001.md` - top recommendations
- `reports/PHOTO_VERIFICATION_QUEUE_001.md` - next proof needed by lead

## Security

Do not commit:

- `.env`
- credentials
- tokens
- raw Apify JSON
- `data/raw`

Use `APIFY_TOKEN` as an environment variable. If a token is pasted into chat or
logs, rotate it.

## More Detail

Read:

- `reports/SIMPLE_THREE_SOURCE_PLAN.md`
- `reports/THREE_SOURCE_SMOKE_TEST_2026-05-05.md`
- `reports/APIFY_ACTOR_SMOKE_TEST_2026-05-05.md`
