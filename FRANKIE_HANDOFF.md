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
- Arbitrage, deal desk, resale, Mercari, Facebook Marketplace, eBay sold comps
  -> `skills/arbitrage-deal-desk/SKILL.md`
- Browser/page automation -> `skills/page-map/SKILL.md`

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
