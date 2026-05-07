# Arbitrage Deal Desk

## Purpose

Find practical resale/arbitrage leads for retro tech and vintage audio. Output
only INVESTIGATE / WATCH / SKIP.

## Skill

`skills/arbitrage-deal-desk/SKILL.md`

## Main Runbook

`reports/OPENCLAW_ARBITRAGE_RUNBOOK.md`

## Safe Command

```powershell
python scripts\run_arbitrage_pipeline.py
```

## Paid Collection

Only when Matthew explicitly asks:

```powershell
python scripts\run_arbitrage_pipeline.py --collect
```

## Sold Comps

Exact model only:

```powershell
python scripts\run_ebay_sold_comps.py --keywords "Exact Model" --clean --merge --refresh-reports
```

## Main Reports

- `reports/PHOTO_VERIFICATION_QUEUE_001.md`
- `reports/DEAL_DESK_REVIEW_001.md`
- `reports/LEAD_HISTORY_UPDATE_001.md`
- `reports/PIPELINE_RUN_LAST.md`

## Adjacent Workflow

Freebie Radar is separate from underwriting:

```powershell
python scripts\freebie_radar.py
```

Use it for free, curb-alert, pickup-only, and very cheap local tech listings.
Report: `reports/FREEBIE_RADAR_LAST.md`.

## Hard Rules

- Never say BUY.
- Never estimate profit from active listings.
- Never run broad sold-comp searches.
- Never automate seller contact.
- Never commit tokens or raw actor JSON.
