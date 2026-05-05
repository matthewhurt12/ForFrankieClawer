# Frankie Start Here

This is the navigation map for Frankie/OpenClaw. If you feel lost, read this
file before searching the whole workspace.

## Fast Rule

After pulling this repo, run:

```powershell
python scripts\frankie_start.py
```

When Matthew asks for a workflow, tool, slash command, or recurring capability:

1. Check `COMMANDS.md`.
2. Check `skills/manifest.json`.
3. Open the matching `skills/<name>/SKILL.md`.
4. Use the linked runbook or command.

Quick terminal helper:

```powershell
python scripts\list_skills.py
```

Workspace self-test:

```powershell
python scripts\workspace_doctor.py
```

Do not say a skill does not exist until you have checked those files.

## Main Indexes

- `COMMANDS.md` - slash command and trigger phrase router.
- `FRANKIE_HANDOFF.md` - exact pull-and-start handoff for Frankie/OpenClaw.
- `skills/README.md` - human-readable skill list.
- `skills/manifest.json` - machine-readable skill list.
- `.openclaw/skill-manifest.json` - OpenClaw-facing copy of the skill manifest.
- `scripts/list_skills.py` - terminal printout of available skills.
- `scripts/frankie_start.py` - first command after pull; runs health check,
  skill list, and safe pipeline dry run.
- `scripts/workspace_doctor.py` - local health check for navigation, manifests,
  active scripts, `.gitignore`, and token-shaped strings.
- `scripts/README.md` - which scripts are active vs. legacy.
- `reports/README.md` - which reports are current vs. historical.
- `docs/README.md` - docs index.
- `data/README.md` - data file map and raw-output rules.
- `TOOLS.md` - local environment notes.
- `MEMORY.md` - curated long-term memory.
- `memory/YYYY-MM-DD.md` - daily working memory.

## Current Important Skills

- `skills/arbitrage-deal-desk/SKILL.md`
  - Retro tech and vintage audio arbitrage.
  - Safe local command: `python scripts\run_arbitrage_pipeline.py`

- `skills/page-map/SKILL.md`
  - Browser/page element mapping before automation.

- `skills/signals/SKILL.md`
  - `/signals`, full Signal Engine report.

- `skills/radar/SKILL.md`
  - `/radar`, quick current scan.

- `skills/bigpic/SKILL.md`
  - `/bigpic`, strategic synthesis.

- `skills/ideas/SKILL.md`
  - `/ideas`, practical opportunity report.

## Current Important Projects

- Arbitrage Deal Desk:
  - `projects/arbitrage-deal-desk.md`
  - `README.md`
  - `reports/OPENCLAW_ARBITRAGE_RUNBOOK.md`
  - `reports/PHOTO_VERIFICATION_QUEUE_001.md`
  - `reports/DEAL_DESK_REVIEW_001.md`

- Signal Engine:
  - `projects/signal-engine.md`
  - `C:\Users\matth\Documents\openclaw-vault\signals\sources.md`
  - `C:\Users\matth\Documents\openclaw-vault\signals\full`
  - `C:\Users\matth\Documents\openclaw-vault\signals\radar`
  - `C:\Users\matth\Documents\openclaw-vault\signals\bigpic`
  - `C:\Users\matth\Documents\openclaw-vault\signals\ideas`

- Frankie Mind navigation:
  - `projects/frankie-mind.md`
  - `START_HERE.md`
  - `COMMANDS.md`
  - `skills/manifest.json`

## Memory Rules

- Save daily facts to `memory/YYYY-MM-DD.md`.
- Save durable lessons and preferences to `MEMORY.md`.
- Save project-specific notes under `projects/`.
- Do not store secrets, tokens, passwords, or private keys in memory.

## Security Rules

- Never print or commit tokens.
- Never commit `.env`, credentials, raw Apify JSON, or secret files.
- Paid Apify collection requires Matthew's explicit ask.
- Seller messages are generated for Matthew. Do not automate seller contact yet.
