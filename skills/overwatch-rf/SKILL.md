# overwatch-rf

Use this skill when Matthew says Overwatch, WiFi surveillance, WiFi monitor,
RF monitoring, local signal environment, daily Overwatch check, or asks what
changed around the monitoring station.

## Real Repo

The active Overwatch code lives outside Frankie Mind:

```text
C:\Users\matth\overwatch-wifi-monitor
```

GitHub:

```text
https://github.com/matthewhurt12/overwatch-wifi-monitor
```

Open the repo guide before deeper work:

```text
C:\Users\matth\overwatch-wifi-monitor\docs\FRANKIE_OVERWATCH.md
```

## Safe Commands

Check that Frankie can find the repo:

```powershell
python scripts\overwatch_daily.py status
```

Run the private daily review without writing a report:

```powershell
python scripts\overwatch_daily.py --no-write
```

Get JSON for analysis:

```powershell
python scripts\overwatch_daily.py --no-write --json
```

Review a longer window:

```powershell
python scripts\overwatch_daily.py --hours 72 --no-write
```

On the Raspberry Pi, the server command is:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

## What To Report

When Matthew asks for an Overwatch check, answer these first:

- Is the scanner/server healthy?
- Is the database present and current?
- How many events happened in the last day?
- Did close-signal alerts, packet bursts, or new APs spike?
- Which devices are recurring enough to label?
- What should Matthew check next?

Keep the answer practical and calm. Lead with what changed.

## Data Rules

- Treat MAC addresses, probe requests, reports, and event logs as private local data.
- Daily reports redact MAC addresses by default.
- Do not commit raw scan data, databases, reports, or captures.
- Keep Overwatch passive. Do not add deauth, cracking, credential capture,
  packet payload capture, or anything that interferes with other networks.
- Do not decode protected, encrypted, cellular, voice, or private traffic.

## Environment Variables

The real repo supports:

- `OVERWATCH_REPO` - alternate local checkout path for this wrapper
- `OVERWATCH_CSV_FILE` - airodump-ng CSV path
- `OVERWATCH_DB` - SQLite registry path
- `OVERWATCH_DATA_DIR` - default data directory
- `OVERWATCH_EVENT_RETENTION_DAYS` - event retention window
- `OVERWATCH_REPORT_DIR` - daily report output directory
- `OVERWATCH_REPORT_FULL_MAC=1` - disable MAC redaction for private local review only
