# Frankie Mind

## Purpose

Keep Frankie/OpenClaw navigable, memorable, and easy to operate across sessions.

## Start Points

- `START_HERE.md`
- `COMMANDS.md`
- `AGENTS.md`
- `TOOLS.md`
- `MEMORY.md`
- `skills/manifest.json`

## Current Setup

- Skills live under `skills/<name>/SKILL.md`.
- Slash-command routing lives in `COMMANDS.md`.
- Machine-readable skill index lives in `skills/manifest.json`.
- OpenClaw-facing copy lives in `.openclaw/skill-manifest.json`.
- Daily memory lives in `memory/YYYY-MM-DD.md`.
- Long-term memory lives in `MEMORY.md`.

## Maintenance Rule

When a new workflow becomes important, add:

1. A skill folder if it is reusable.
2. A row in `COMMANDS.md` if it has a short command or trigger phrase.
3. An entry in `skills/manifest.json`.
4. A project card in `projects/` if it is ongoing.
5. A short note in `memory/YYYY-MM-DD.md`.

## Current Problem Solved

Frankie previously missed `/signals` and `/bigpic` because they existed as
memory/workflow notes, not as strongly indexed skills. The new routing files
should reduce that.
