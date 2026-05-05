# Simple Three-Source Arbitrage Plan

**Goal:** Keep Frankie focused on the three sources that matter right now.

1. Mercari = national buy-side leads
2. Facebook Marketplace = local Athens / Atlanta buy-side leads
3. eBay sold comps = resale proof

Everything else is optional later.

---

## Daily Mental Model

Do not think "scrape everything."

Think:

1. Find a small batch of possible buys.
2. Save/update listing history.
3. Filter junk.
4. Pick only the best few.
5. Run sold comps only on exact model candidates.
6. Output INVESTIGATE / WATCH / SKIP.

---

## Source Roles

### Mercari

Use for national buy-side leads.

Run conservative searches from:

`config/marketplace_sources.json`

Default search lanes:

- vintage stereo receiver
- Realistic receiver
- cassette deck
- Nintendo Wii console
- Nintendo GameCube console
- Nintendo 64 console
- Apple iMac G3
- Apple Power Mac G4
- iPod classic

Output:

`data/external_leads/mercari_leads.csv`

Then update history:

```bash
python scripts/update_lead_history.py
```

### Facebook Marketplace

Use for local Athens / Atlanta leads only.

Important: use `resultsLimit`, not `maxItems`.

Output:

`data/external_leads/facebook_marketplace_leads.csv`

Then update history:

```bash
python scripts/update_lead_history.py
```

### eBay Sold Comps

Use only for exact model candidates from the top few leads.

Do not run this on broad searches like:

- Pioneer receiver
- Marantz stereo
- Technics turntable

Good searches:

- Pioneer SX-650
- Marantz 2270
- Technics SL-1200 MK2
- Realistic STA-820
- Nintendo GameCube
- Nintendo Wii U
- Nintendo 64
- iMac G3
- Power Mac G4 Cube
- iPod Classic

After sold comps:

```bash
python scripts/run_ebay_sold_comps.py --keywords "Exact Model Here" --clean --merge --refresh-reports
```

---

## Historical List

The history layer is worth keeping.

It creates:

- `data/lead_history.csv`
- `data/lead_price_events.csv`
- `reports/LEAD_HISTORY_UPDATE_001.md`

This lets Frankie notice:

- new listings
- repeat listings
- price drops
- stale listings
- items that keep reappearing

This is useful because the money is usually in "new today" and "price dropped since last run."

---

## Simple Command Flow

Preferred safe refresh, no paid Apify run:

```bash
python scripts/run_arbitrage_pipeline.py
```

Fresh paid marketplace run, only when Matthew asks:

```bash
python scripts/run_arbitrage_pipeline.py --collect
```

Exact-model sold comps:

```bash
python scripts/run_ebay_sold_comps.py --keywords "Kenwood KR-4600" "Apple Power Mac G4" --clean --merge --refresh-reports
```

The older individual scripts still work, but Frankie should prefer the commands
above because they run the steps in the right order and include guardrails.

### Manual Fallback

Mercari run:

```bash
python scripts/mercari_production_run_001.py
python scripts/update_lead_history.py
python scripts/deal_desk_review.py
```

Facebook run:

```bash
python scripts/facebook_marketplace_run_002.py
python scripts/update_lead_history.py
python scripts/deal_desk_review.py
```

After a top lead has an exact model:

```bash
python scripts/clean_ebay_sold_comps.py --input data/sold_comps/latest.json
python scripts/deal_desk_review.py
```

---

## Target Lanes

Keep the system broad enough to find fun deals, but not so broad that it becomes junk.

Current lanes:

- Vintage stereo receivers, cassette decks, turntables
- RadioShack / Realistic stereo gear
- Nintendo Wii, Wii U, GameCube, N64, NES/SNES
- PlayStation 2/3, Sega Dreamcast, Genesis, original Xbox / Xbox 360
- Old Apple gear: iMac G3/G4/G5, Power Mac G4, Macintosh Classic/SE/Plus, Apple II
- Portable retro audio: iPod Classic/Mini, Walkman, Discman, MiniDisc

Avoid:

- single game discs unless manually requested
- empty boxes
- manuals
- controller-only listings
- cables, chargers, adapters
- replacement shells and parts lots

---

## Parallel Runs

Frankie may run Mercari and Facebook at the same time because they write separate source CSVs.

Safe pattern:

1. Start Mercari actor.
2. Start Facebook actor.
3. Wait for both to finish.
4. Then run `python scripts/update_lead_history.py`.
5. Then run `python scripts/deal_desk_review.py`.

Do not run two Mercari jobs or two Facebook jobs at the same time, because they overwrite the same CSV.

Do not run Deal Desk while source CSVs are still being written.

---

## Hard Rules

- Never call anything BUY.
- Never estimate profit from active listings.
- Never run sold comps on generic searches.
- Never commit tokens, `.env`, credentials, or raw JSON dumps.
- Only calculate max buy price when 3+ clean full-unit sold comps exist.
- Keep actor runs small until their real cost is proven.

---

## Later, Not Now

Google Shopping can be useful later for retail/new/refurb price context, but it is not a good replacement for local used marketplaces. It is not part of the core workflow yet.

Reverb can stay optional for music gear active context, but it should not be in the main loop right now.
