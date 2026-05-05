# Data Index

Do not commit raw marketplace dumps or credentials. Use this directory as local
working state.

## Current Working Files

- `external_leads/mercari_leads.csv`
  - Current normalized Mercari leads.

- `external_leads/facebook_marketplace_leads.csv`
  - Current normalized Facebook Marketplace leads.

- `lead_history.csv`
  - Persistent listing history.

- `lead_price_events.csv`
  - Price/new-listing events.

- `ebay_sold_comps_clean.csv`
  - Main cleaned sold-comp table used for underwriting.

## Raw / Temporary Data

Raw JSON actor outputs should stay local and ignored by git:

- `external_leads/*raw*.json`
- `sold_comps/*.json`
- `raw/`

Clean CSVs can be kept when useful. Do not store seller personal data unless it
is truly needed for the workflow.
