# OpenClaw Arbitrage Runbook

This is the simple operating guide for Frankie/OpenClaw.

## Mission

Find possible resale/arbitrage leads for retro tech and vintage audio. Produce
only action-quality recommendations:

- INVESTIGATE
- WATCH
- SKIP

Never say BUY. Never invent profit.

## One Safe Command

Use this first:

```powershell
python scripts\run_arbitrage_pipeline.py
```

This is local-only. It does not spend Apify money. It refreshes the current
reports from whatever CSV data already exists.

Outputs:

- `reports/DEAL_DESK_REVIEW_001.md`
- `reports/PHOTO_VERIFICATION_QUEUE_001.md`
- `reports/LEAD_HISTORY_UPDATE_001.md`
- `reports/PIPELINE_RUN_LAST.md`

## Fresh Marketplace Collection

Only run this when Matthew explicitly wants a fresh paid pull:

```powershell
$env:APIFY_TOKEN = "token-goes-here"
python scripts\run_arbitrage_pipeline.py --collect
```

What this does:

1. Runs Mercari and Facebook Marketplace actors in parallel.
2. Updates lead history.
3. Regenerates Deal Desk.
4. Regenerates Photo Verification Queue.

Do not run two Mercari jobs at the same time. Do not run two Facebook jobs at
the same time. They overwrite their current CSV outputs.

## Sold Comps

Only run sold comps after the Deal Desk has an exact model candidate.

Good:

```powershell
python scripts\run_ebay_sold_comps.py --keywords "Kenwood KR-4600" "Nintendo GameCube" --clean --merge --refresh-reports
```

Bad:

```powershell
python scripts\run_ebay_sold_comps.py --keywords "Pioneer receiver"
```

The sold-comps runner will refuse broad searches by default.

Rules:

- Max 6 keywords per run.
- Exact model only.
- Use `--clean --merge --refresh-reports` for the normal workflow.
- If fewer than 3 clean full-unit comps survive, mark LOW_CONFIDENCE.
- If comp prices are wildly dispersed, do not calculate max buy.

## Report Reading Order

1. `reports/PHOTO_VERIFICATION_QUEUE_001.md`
   - Best operational view.
   - Check `READY_FOR_SELLER_MESSAGE` first.
   - Then check `NEEDS_SOLD_COMPS`.
   - Then check `NEEDS_EXACT_MODEL`.

2. `reports/DEAL_DESK_REVIEW_001.md`
   - Top 5 immediate review leads.
   - Top 10 watchlist.
   - Skip reasons.

3. `reports/LEAD_HISTORY_UPDATE_001.md`
   - New listings, repeat listings, price changes.

## Source Roles

- Mercari: national buy-side leads.
- Facebook Marketplace: local Athens / Atlanta buy-side leads.
- eBay sold comps: true resale proof.

Active listings are not resale proof.

## Current Target Lanes

- Vintage stereo receivers, cassette decks, turntables
- RadioShack / Realistic stereo gear
- Nintendo Wii, Wii U, GameCube, N64, NES/SNES
- PlayStation 2/3, Sega Dreamcast, Genesis, original Xbox / Xbox 360
- Old Apple gear: iMac G3/G4/G5, Power Mac G4, Macintosh Classic/SE/Plus, Apple II
- Portable retro audio: iPod Classic/Mini, Walkman, Discman, MiniDisc

## Hard Rejects

Skip parts/accessories/noise:

- manuals, brochures, catalogs
- LED kits, lamps, bulbs
- parts, repair, rebuild, for parts
- knobs, faceplates, decals, stickers
- case-only, cabinet-only, box-only
- controller-only, remote-only, charger-only, adapter-only
- shirts, posters, pins, logos
- modern AV/home theater receivers unless Matthew overrides

## Seller Messaging

Use the exact seller message generated in the reports.

Do not automate seller messaging yet. Matthew contacts sellers manually.

## Cost Discipline

The main loop is small on purpose.

- Do not add more sources right now.
- Do not run sold comps for the whole pool.
- Do not use broad keywords.
- Do not scrape more just because the list feels small.

The win condition is: "Here are a few leads worth opening today."
