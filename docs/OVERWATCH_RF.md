# Overwatch WiFi Monitoring

Overwatch is Matthew's local WiFi/RF environment monitoring lane. Signal Engine
watches external news and signals; Overwatch watches local passive WiFi metadata
from the monitoring station.

## Active Code

The real code is now in its own repo:

```text
C:\Users\matth\overwatch-wifi-monitor
```

GitHub:

```text
https://github.com/matthewhurt12/overwatch-wifi-monitor
```

Frankie-facing guide:

```text
C:\Users\matth\overwatch-wifi-monitor\docs\FRANKIE_OVERWATCH.md
```

## Frankie Entry Point

From Frankie Mind:

```powershell
python scripts\overwatch_daily.py status
python scripts\overwatch_daily.py --no-write --json
```

The wrapper delegates to:

```text
C:\Users\matth\overwatch-wifi-monitor\overwatch_daily.py
```

## Daily Review

Use the daily review when Matthew asks what changed, what looked unusual, or
whether Overwatch needs attention.

Check:

- database presence and freshness
- total events versus previous window
- close-signal alerts
- packet bursts
- new AP volume
- top vendors
- strongest devices
- recurring devices that may need labels

## API

When the FastAPI server is running:

- `GET /devices`
- `GET /api/timeline?hours=24`
- `GET /api/timeline/{mac}?hours=24`
- `GET /api/daily-summary?hours=24`
- `WS /ws`

## Operating Rules

- Passive monitoring only.
- No deauth, cracking, credential capture, payload capture, or interference.
- No protected/private/cellular/voice decoding.
- Raw scan data, databases, reports, and captures stay out of Git.
- MACs are private local data; use redacted output by default.
