# freebie-radar

Use this skill when Matthew asks for Facebook Marketplace free listings, curb
alerts, free pickup finds, very cheap local listings, or a daily local scan.

This is separate from `arbitrage-deal-desk`. The Deal Desk is for resale
underwriting. Freebie Radar is for fast pickup opportunities and cheap local
finds.

## Safe Default Command

Local-only, no paid actor call:

```powershell
python scripts\freebie_radar.py
```

This reads existing normalized marketplace CSVs and regenerates:

- `reports/FREEBIE_RADAR_LAST.md`
- `data/freebie_radar/freebie_radar_latest.csv`
- `data/freebie_radar/freebie_radar_history.csv`

## Fresh Paid Facebook Scan

Only run when Matthew explicitly asks for a fresh scan:

```powershell
$env:APIFY_TOKEN = "token-goes-here"
python scripts\freebie_radar.py --collect --sources facebook
```

The search list and cost caps live in `config/freebie_radar.json`.

## Optional Mercari Cheap Scan

Mercari is not local pickup and is not freebie-first. Use it only when Matthew
asks to include Mercari:

```powershell
python scripts\freebie_radar.py --collect --sources facebook mercari
```

## Price-Bait Rule

Many Facebook listings use `$1` only to get attention. Treat `$1` as suspicious
unless the title/query has free/pickup language such as `free`, `curb alert`,
`come pick up`, `pickup only`, or `must pick up`.

## Output Priority

Read this report first:

```powershell
reports\FREEBIE_RADAR_LAST.md
```

Sections:

1. New Free / Pickup Leads
2. New Cheap Watch Leads
3. Best Seen-Before Leads
4. Skipped / Suppressed Examples

## Safety

- Never send seller messages automatically.
- Never send deposits.
- Prefer in-person pickup in public/safe conditions.
- Do not print or commit tokens.
- Raw Apify JSON goes under `data/freebie_radar/raw/` and is ignored.
