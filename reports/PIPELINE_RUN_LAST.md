# Arbitrage Pipeline Run

**Generated:** 2026-05-05 22:58 UTC
**Mode:** local reports only
**Sources:** mercari, facebook

## Step Results

### Update lead history

- **Status:** OK
- **Command:** `C:\Users\matth\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe scripts/update_lead_history.py`

```text
Current leads loaded: 258
New listings: 0
Price changes: 0
History written: data\lead_history.csv
Price events written: data\lead_price_events.csv
Report written: reports\LEAD_HISTORY_UPDATE_001.md
```

### Generate Deal Desk

- **Status:** OK
- **Command:** `C:\Users\matth\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe scripts/deal_desk_review.py`

```text
================================================================================
DEAL DESK REVIEW - ACTIONABLE LEADS ONLY
================================================================================

Loaded unique leads: 258
Models with clean sold comp summaries: 24
Report generated: reports\DEAL_DESK_REVIEW_001.md
Photo queue generated: reports\PHOTO_VERIFICATION_QUEUE_001.md

Top immediate leads:
  1. Apple iMac G4 "Sunflower" Vintage Computer - Fully Working | $150 | Apple iMac G4
  2. Sony Walkman Cassette Player FM/AM | $20 | Sony Walkman
  3. Realistic STA-82 Vintage Receiver circa 1975-76 both channels working | $80 | Realistic STA-82
  4. Nintendo 64 complete and in great working condition | $120 | Nintendo 64
  5. Vintage Apple Macintosh Classic Computer GCC UltraDrive 45 Lot | $145 | Macintosh Classic

```

### Generate Photo Verification Queue

- **Status:** OK
- **Command:** `C:\Users\matth\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe scripts/photo_verification_queue.py`

```text
================================================================================
PHOTO VERIFICATION QUEUE
================================================================================
Report generated: reports\PHOTO_VERIFICATION_QUEUE_001.md
```

## Outputs

- Deal Desk: `reports\DEAL_DESK_REVIEW_001.md`
- Photo Queue: `reports\PHOTO_VERIFICATION_QUEUE_001.md`
- Lead History: `reports\LEAD_HISTORY_UPDATE_001.md`

## Rules

- INVESTIGATE / WATCH / SKIP only.
- No profit estimate without clean sold comps.
- Paid Apify runs require `--collect`.
- eBay sold comps should be run separately with exact model keywords only.
