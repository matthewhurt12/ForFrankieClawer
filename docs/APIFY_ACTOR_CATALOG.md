# Apify Actor Catalog For Frankie

This is a working memory list of actors Frankie can consider. It does not prove
what is rented on Matthew's Apify account. To know that, Frankie needs
`APIFY_TOKEN` in the environment and should check the Apify Console/API without
printing the token.

## Rule

Use specialized actors first. Use generic actors only for one-off research or
sites that do not have a reliable dedicated actor. Paid actor runs require
Matthew's explicit approval.

## Core Actors

- `stealth_mode/mercari-product-search-scraper`
  - Current config ID: `stealth_mode~mercari-product-search-scraper`
  - Use for Mercari buy-side leads.
  - Active listing context only.

- `apify/facebook-marketplace-scraper`
  - Current config ID: `apify~facebook-marketplace-scraper`
  - Use for Athens/Atlanta local buy-side leads.
  - Active listing context only.

- `caffein.dev/ebay-sold-listings`
  - Current config ID: `oTtB3VgfuE9GtxQt2`
  - Use for sold comps on exact model candidates.
  - Never run on broad searches like `Pioneer receiver`.

## General Website Scrapers

- `apify/website-content-crawler`
  - Best first generic actor for turning one-off websites into clean text or
    Markdown for research.

- `apify/cheerio-scraper`
  - Cheap/fast static HTML scraper.
  - Try this before a full browser when the page does not require JavaScript.

- `apify/web-scraper`
  - General full-browser scraper for dynamic websites.
  - Safer than writing custom browser logic for quick tests.

- `apify/puppeteer-scraper`
  - More control for browser scraping.
  - Higher cost/risk; use after a small proof test.

- `apify/playwright-scraper`
  - Similar role to Puppeteer Scraper, useful when Playwright behavior matters.

## Candidate Actors To Add Later

- `parseforge/craigslist-scraper`
  - Potential Athens/Atlanta local deal source.
  - Add only after the cost guard exists.

- `solidcode/google-shopping-scraper`
  - Active retail context only.
  - Helpful for sanity checking, not resale proof.

## Safe Generic Scraper Defaults

For a one-off generic scrape:

- Max pages: 1-5
- Max concurrency: 1-3
- No media downloads unless needed
- Respect robots where practical
- Save minimal output
- Do not store private user data
- Write a report explaining whether the actor is worth promoting

## Current Sources

- Apify docs say Web Scraper, Puppeteer Scraper, and Cheerio Scraper are
  configurable actors/tasks for scraping webpages.
- Apify's Cheerio Scraper page describes it as a fast raw-HTTP HTML scraper and
  notes it can be much faster than a full browser when JavaScript is not needed.
- Apify's Website Content Crawler is described for extracting website text
  content for AI/RAG-style workflows.
