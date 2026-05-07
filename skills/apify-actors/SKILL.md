# Apify Actors Skill

Use this skill when Matthew asks what Apify actors Frankie can use, wants to add
scrapers, wants a generic website scraper, asks what is safe to run, or wants to
test actors.

## First Files

- `config/apify_actor_catalog.json`
- `docs/APIFY_ACTOR_CATALOG.md`
- `config/marketplace_sources.json`
- `reports/APIFY_ACTOR_SMOKE_TEST_2026-05-05.md`

## Safety Rules

- Do not print `APIFY_TOKEN`.
- Paid actor runs require Matthew's explicit approval.
- Prefer actor dry-runs, plans, and tiny test inputs.
- Use specialized actors before generic scrapers.
- Use active listings only as context. Sold comps are the proof layer.

## Actor Selection

For marketplace arbitrage:

1. Mercari Product Search Scraper for buy-side leads.
2. Facebook Marketplace Scraper for local buy-side leads.
3. eBay Sold Listings for exact-model sold comps.

For generic sites:

1. `apify/website-content-crawler` for text/Markdown research.
2. `apify/cheerio-scraper` for cheap static HTML.
3. `apify/web-scraper` for dynamic pages.
4. `apify/puppeteer-scraper` or `apify/playwright-scraper` only when custom
   browser control is needed.

## If Matthew Asks What Is On His Plan

Check whether `APIFY_TOKEN` exists. If it does not, say token access is needed
to inspect rented/account-specific actors. Do not guess account ownership from
the public store.

## Output

When suggesting actors, include:

- Actor ID
- Why it helps
- Whether it is core/candidate/generic
- Cost posture
- Safe first test
- Whether output can be used for buy-side leads, active context, or sold comps
