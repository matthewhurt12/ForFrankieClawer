# Three-Source Smoke Test - 2026-05-05

**Purpose:** Simplify the system around Mercari, Facebook Marketplace, and eBay sold comps.

---

## Result

The three-source plan works when the actors are configured conservatively.

| Source | Test | Result | Reported Usage | Decision |
|---|---|---|---:|---|
| Mercari | 1 search, 2 max items | Succeeded, returned 2 rows | ~$0.003 | Use |
| Facebook Marketplace | 1 Athens search, `resultsLimit: 2` | Succeeded, returned 2 rows | $0.00 reported | Use carefully |
| eBay Sold Comps | 1 exact model, 3 rows | Succeeded, returned sold rows | ~$0.012 | Use for top candidates |

---

## Important Fix

The Facebook actor should use:

```json
{
  "resultsLimit": 2
}
```

Do not use `maxItems` for this actor. The earlier smoke test used `maxItems`, timed out, and reported about `$3.10` usage.

---

## Mercari Test Rows

Search:

`Realistic receiver`

Returned examples:

- Realistic STA-820 AM FM Stereo Receiver Working
- Realistic 455 CB base station, for parts only

This proves the Mercari actor works now that it has been rented, and it also proves the hard reject filter matters.

---

## Facebook Test Rows

Search:

`Athens vintage receiver`

Returned examples:

- Kenwood KR-7600 Vintage Receiver - $250
- Harmon Kardon hk385i Linear Phase Stereo Receiver - $80

This is exactly the kind of local lead source we want.

---

## eBay Sold Comp Test

Search:

`Technics SL-1200`

Cleaner result:

- 3 raw rows
- 2 valid full-unit rows
- 1 rejected plinth/accessory row
- Status: LOW_CONFIDENCE because fewer than 3 full-unit comps survived

This confirms the underwriting gate is working.

---

## Simple Flow

1. Run Mercari or Facebook in small batches.
2. Update lead history.
3. Run Deal Desk.
4. For only the top exact-model candidates, run eBay sold comps.
5. Clean sold comps.
6. Rerun Deal Desk.

Commands:

```bash
python scripts/mercari_production_run_001.py
python scripts/update_lead_history.py
python scripts/deal_desk_review.py
```

```bash
python scripts/facebook_marketplace_run_002.py
python scripts/update_lead_history.py
python scripts/deal_desk_review.py
```

```bash
python scripts/clean_ebay_sold_comps.py --input data/sold_comps/latest.json
python scripts/deal_desk_review.py
```
