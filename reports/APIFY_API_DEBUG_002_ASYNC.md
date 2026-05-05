# Apify API Debug 002 - Async Run

**Date:** 2026-05-04

---

## Debug Log

```
================================================================================
APIFY API DEBUG 002 - ASYNC RUN
================================================================================

Input Configuration:
{
  "urls": [
    "https://www.mercari.com/us/category/84/"
  ],
  "max_items_per_url": 20,
  "ignore_url_failures": true,
  "proxy": {
    "useApifyProxy": false
  }
}

Starting async actor run...
Start Status: 201
✓ Run started
  Run ID: jQXLpVDB3pcQ1RHML
  Status: READY
  Dataset ID: xRgUclIv4C0odmZfx

Waiting for completion (max 3 minutes)...
  Status: RUNNING
  Status: SUCCEEDED

✓ Run succeeded
  Final Dataset ID: xRgUclIv4C0odmZfx

Fetching dataset items...
  Dataset Status: 200
  Items returned: 0

✗ Zero items in dataset

Checking dataset info...
Dataset Info:
{
  "data": {
    "id": "xRgUclIv4C0odmZfx",
    "name": null,
    "userId": "rrO7n3YnECjm5C8e5",
    "createdAt": "2026-05-04T15:38:21.716Z",
    "modifiedAt": "2026-05-04T15:38:21.716Z",
    "accessedAt": "2026-05-04T15:38:21.716Z",
    "itemCount": 0,
    "cleanItemCount": 0,
    "actId": "RRTyirrSSKzpsf1iN",
    "actRunId": "jQXLpVDB3pcQ1RHML",
    "schema": {
      "actorSpecification": 1,
      "fields": {},
      "views": {
        "overview": {
          "title": "Item",
          "transformation": {
            "fields": [
              "id",
              "name",
              "status",
              "shipping_payer",
              "photos",
              "seller",
              "price",
              "original_price",
              "item_decoration_circle",
              "item_decoration_rectangle",
              "promote_type",
              "promote_expire_time",
              "authentic_item_status",
              "country_source",
              "brand",
              "it

Checking key-value store...
  OUTPUT record status: 404

================================================================================
Debug Complete
================================================================================
```
