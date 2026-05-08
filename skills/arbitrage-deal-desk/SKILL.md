# arbitrage-deal-desk

Use this skill when Matthew asks about the retro tech arbitrage system, Apify
marketplace scrapes, Mercari, Facebook Marketplace with resale intent, eBay
sold comps, deal recommendations, photo verification, flipping, profit, or the
Deal Desk.

## Mission

Help Matthew find resale/arbitrage leads for retro tech and vintage audio.
Optimize for action quality, not lead count.

If Matthew only asks for Athens/local/free/cheap marketplace finds without
resale language, route to `freebie-radar` first. If he asks whether something is
worth flipping, route here.

Allowed verdicts:

- INVESTIGATE
- WATCH
- SKIP

Never output BUY. Never estimate profit from active listings.

## First File To Read

`reports/OPENCLAW_ARBITRAGE_RUNBOOK.md`

## Safe Default Command

Run this to refresh reports without spending Apify money:

```powershell
python scripts\run_arbitrage_pipeline.py
```

This updates history, Deal Desk, and Photo Verification Queue from existing CSVs.

## Fresh Paid Collection

Only if Matthew explicitly asks for a fresh run:

```powershell
$env:APIFY_TOKEN = "token-goes-here"
python scripts\run_arbitrage_pipeline.py --collect
```

Mercari and Facebook are safe to run in parallel through this command. Do not
start duplicate source jobs manually.

## Sold Comps

Only exact model keywords:

```powershell
python scripts\run_ebay_sold_comps.py --keywords "Kenwood KR-4600" "Nintendo GameCube" --clean --merge --refresh-reports
```

The runner refuses broad searches like `Pioneer receiver`.

## Report Order

1. `reports/PHOTO_VERIFICATION_QUEUE_001.md`
2. `reports/DEAL_DESK_REVIEW_001.md`
3. `reports/LEAD_HISTORY_UPDATE_001.md`
4. `reports/PIPELINE_RUN_LAST.md`

## Security

Never print or commit tokens. Never commit `.env`, credentials, or raw JSON
dumps. Use `APIFY_TOKEN` from the environment.
