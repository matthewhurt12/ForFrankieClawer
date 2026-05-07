# Freebie Radar

Freebie Radar is a separate marketplace workflow for finding free, curb-alert,
pickup-only, and very cheap local tech listings around Athens / Atlanta.

It is intentionally not the same as the arbitrage Deal Desk:

- Deal Desk = resale underwriting with sold comps.
- Freebie Radar = fast local opportunity scan.

## Commands

Local-only from existing CSVs:

```powershell
python scripts\freebie_radar.py
```

Show what a paid run would do:

```powershell
python scripts\freebie_radar.py --collect --sources facebook --dry-run
```

Fresh paid Facebook scan:

```powershell
$env:APIFY_TOKEN = "token-goes-here"
python scripts\freebie_radar.py --collect --sources facebook
```

Optional Mercari cheap scan:

```powershell
python scripts\freebie_radar.py --collect --sources facebook mercari
```

## Main Files

- Config: `config/freebie_radar.json`
- Script: `scripts/freebie_radar.py`
- Skill: `skills/freebie-radar/SKILL.md`
- Latest report: `reports/FREEBIE_RADAR_LAST.md`
- Latest CSV: `data/freebie_radar/freebie_radar_latest.csv`
- Seen history: `data/freebie_radar/freebie_radar_history.csv`

## Important Filtering Behavior

- `$1` without free/pickup language is treated as price bait.
- Free/pickup wording gets priority.
- Junk terms suppress wanted posts, broken/parts-only items, clothes, mattresses,
  firewood, and similar non-target listings.
- Seller messages are drafted only. Nothing is sent automatically.
