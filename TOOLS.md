# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Skill Discovery

If Matthew asks for a skill, workflow, or slash command, start here:

1. `START_HERE.md`
2. `COMMANDS.md`
3. `skills/manifest.json`
4. `skills/<name>/SKILL.md`

Quick terminal helper:

```powershell
python scripts\list_skills.py
```

Workspace health check:

```powershell
python scripts\workspace_doctor.py
```

Current local skills:

- `athens-food` - Athens restaurant recommendations from Matthew's spreadsheet.
- `voice-output` - ElevenLabs / `sag` voice-file navigation.
- `arbitrage-deal-desk` - retro tech arbitrage pipeline and Deal Desk.
- `page-map` - browser/page element map before automation.
- `signals` - `/signals`, full Signal Engine report.
- `radar` - `/radar`, quick current scan.
- `bigpic` - `/bigpic`, strategic synthesis.
- `ideas` - `/ideas`, build and opportunity report.

Important: slash commands are not magic unless the runtime recognizes them.
If `/bigpic` or `/signals` is not auto-routed, open `COMMANDS.md` manually and
then the matching `SKILL.md`.

---

## Voice / ElevenLabs

When Matthew asks for a voice file, audio version, narration, storytime, or
ElevenLabs/TTS output:

1. Open `skills/voice-output/SKILL.md`.
2. Check availability:

```powershell
Get-Command sag -ErrorAction SilentlyContinue
sag --help
```

3. Save generated local audio under `data/voice_outputs/`.

Current note: `sag` may not be on the Windows PowerShell PATH. If it is missing,
say so and prepare a voice-ready script instead of claiming a file exists.

---

## Memory System

**Current workspace:** `C:\Users\matth\Frankie Mind`

**Signal Engine vault:** `C:\Users\matth\Documents\openclaw-vault`

**Older WSL vault path:** `/home/matthew/openclaw-vault`

### Obsidian Integration
Memory files use [[wiki links]] and #tags for Obsidian compatibility.

**Tag system:**
- `#concern` - Things on Matthew's mind
- `#decision` - Choices made with context
- `#preference` - How Matthew likes things done
- `#pattern` - Behaviors noticed over time
- `#win` - Successes worth remembering
- `#blocker` - Things blocking progress
- Project tags: `#project/alert-pro`, `#project/smartcore`, `#project/teton-telecom`, `#project/laura-art`, `#project/met`

### Automatic Behavior
- **Proactive writing:** When Matthew mentions a preference, concern, decision, or relationship detail, write to the daily file immediately. Note it briefly.
- **Memory-first answers:** Before answering questions about Matthew's life, projects, or preferences, do `memory_search` first.

### Evening Reflection Journal

**Schedule:** Daily at 9 PM (cron: `0 21 * * *`)

**Questions:**
1. What did you learn today?
2. What are you grateful for?
3. One thing you want to do differently tomorrow?

**Journal location:** `journal/YYYY-MM-DD.md`

**Pattern:** When Matthew replies to the evening reflection prompt, save his answers to `journal/YYYY-MM-DD.md` in this format:

```markdown
# YYYY-MM-DD - Evening Reflection

## What I learned today
[answer]

## What I'm grateful for
[answer]

## One thing I want to do differently tomorrow
[answer]
```

### Weekly Review

**Schedule:** Every Sunday at 7 PM (cron: `0 19 * * 0`)

**Process:** Read the week's daily files, pull notable patterns/decisions/concerns into MEMORY.md or project journals, send Matthew a summary of what was noticed.

---

## Phone Calls

**Script:** `~/scripts/call-me.sh "message"`

**Use for urgent alerts only:**
- Time-sensitive emergencies
- Scheduled wake-up alerts
- When Matthew explicitly asks to be called

**Don't use for:**
- Routine notifications (use Telegram)
- Regular updates

---

Add whatever helps you do your job. This is your cheat sheet.
