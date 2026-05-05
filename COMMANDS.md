# Command Router

When Matthew uses a slash command or a short workflow name, route it here first.

## Slash Commands

| Command | Skill | File | Output |
|---|---|---|---|
| `/signals` | `signals` | `skills/signals/SKILL.md` | Full Signal Engine report |
| `/radar` | `radar` | `skills/radar/SKILL.md` | Quick current signal scan |
| `/bigpic` | `bigpic` | `skills/bigpic/SKILL.md` | Strategic synthesis |
| `/ideas` | `ideas` | `skills/ideas/SKILL.md` | Practical build and business ideas |

## Workflow Triggers

| User Says | Use | File |
|---|---|---|
| arbitrage, deal desk, resale leads, Mercari, Facebook Marketplace, eBay sold comps | `arbitrage-deal-desk` | `skills/arbitrage-deal-desk/SKILL.md` |
| map this page, browser automation, find buttons, inspect site | `page-map` | `skills/page-map/SKILL.md` |
| signal report, signals, current tech signals | `signals` | `skills/signals/SKILL.md` |
| big picture, thesis, strategic shift | `bigpic` | `skills/bigpic/SKILL.md` |
| radar, what happened, quick scan | `radar` | `skills/radar/SKILL.md` |
| ideas, opportunities, what should I build | `ideas` | `skills/ideas/SKILL.md` |

## Default Behavior

If a command is not recognized:

1. Search `skills/manifest.json`.
2. Search `skills/*/SKILL.md`.
3. Search `memory/` for older workflow notes.
4. Only then tell Matthew it is missing.

If the command is close to a known command, use the likely skill and mention the
match briefly.

Terminal helper:

```powershell
python scripts\list_skills.py
```

## Maintenance Commands

| Command | Purpose |
|---|---|
| `python scripts\workspace_doctor.py` | Check navigation files, skill manifests, active Python scripts, `.gitignore`, and token-shaped strings |
| `python scripts\run_arbitrage_pipeline.py --dry-run` | Show the local arbitrage pipeline steps without calling paid actors |
| `python scripts\run_arbitrage_pipeline.py` | Refresh local-only lead history and reports |
