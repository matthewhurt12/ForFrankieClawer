# signals

Generate the full Signal Engine report. Use this when Matthew says `/signals`,
"signals", "signal report", or asks for the full radar plus big-picture plus
ideas synthesis.

## Purpose

Turn current tech, AI, telecom, and business news into a concise strategic
brief for Matthew. Do not just summarize links. Find the pattern, explain why
it matters, and convert it into practical next moves.

## Files

- Source list: `C:\Users\matth\Documents\openclaw-vault\signals\sources.md`
- Full reports: `C:\Users\matth\Documents\openclaw-vault\signals\full\YYYY-MM-DD.md`
- Big-picture visuals: `C:\Users\matth\Pictures\signals\YYYY-MM-DD-bigpic.png`

WSL equivalents may be used when running under Linux:

- `/mnt/c/Users/matth/Documents/openclaw-vault/signals/sources.md`
- `/mnt/c/Users/matth/Documents/openclaw-vault/signals/full/YYYY-MM-DD.md`
- `/home/matthew/Pictures/signals/YYYY-MM-DD-bigpic.png`

## Source Rules

Read `signals/sources.md` first. Fetch current sources instead of relying on
memory. Use publish dates and include source links.

Default source pull:

- Pots and Pans by CCG: last 2-3 posts by date. This is primary for telecom,
  fiber, RF, carrier, and broadband context.
- Hacker News: front page/top items, filtered for AI, agents, dev tools,
  telecom, security, automation, regulation, and useful weirdness.
- Simon Willison: recent AI/dev/tooling posts.
- One Useful Thing: AI plus business/education when accessible.
- TLDR: quick scan when accessible.
- Stratechery: free posts only.
- Latent Space: recent AI agent/tooling items when accessible.
- Anthropic blog and OpenAI news: recent official model/tool/product posts.

Skip paywalled, login-only, dead, or unreachable sources. Do not fail the whole
report because one source is unavailable. List skipped/failed sources at the
bottom.

## Output Shape

Write one markdown file with this shape:

```markdown
# Full Signal Report - YYYY-MM-DD

---

# RADAR

## WHAT HAPPENED
## WHY IT MATTERS
## WHAT TO WATCH
## WHAT TO DO NEXT

---

# BIG PICTURE

## CORE SHIFT
## PLAIN ENGLISH EXPLANATION
## WHAT'S NOISE VS SIGNAL
## WHERE THIS GOES (6-18 MONTH FORECAST)
## WHAT MATTHEW SHOULD LEARN/BUILD

---

# IDEAS + OPPORTUNITIES

## PERSONAL PRODUCTIVITY
## AI + AUTOMATION LEVERAGE
## SMARTCORE IDEAS
## SIDE PROJECTS / LEARNING BUILDS
## WHAT TO DO NEXT

---

## IN PLAIN ENGLISH

---

**Sources fetched:** ...
**Sources skipped or failed:** ...
```

## Visual Rule

After drafting BIG PICTURE, identify the core thesis in one sentence. If the
thesis is synthesizing a pattern, generate one editorial concept image:

- Medium quality, 1536x1024 landscape.
- Save as `YYYY-MM-DD-bigpic.png` in the Pictures/signals folder.
- Style: clean flat vector, navy plus orange accent, white background, minimal
  labels, no decorative people, readable in 3 seconds on a phone.
- Use one visual metaphor:
  - Shift/transition: split before/after composition
  - Pressure/tension: centered object with forces converging
  - Scale/comparison: side-by-side scale comparison
  - Network/relationship: node-and-edge graph
  - Timeline/sequence: horizontal flow with arrows
  - Map/spread: simplified geo visualization

If the report is mostly discrete updates without a unifying thesis, do not make
an image. Add: `No big-picture visual today - today's signal is mostly discrete
updates without a unifying pattern.`

## Judgment Rules

- Never invent current events, dates, posts, or claims.
- Explain jargon in plain English the first time it matters.
- Keep the report useful, not exhaustive.
- Business tie-ins are optional for `/signals`; do not force them.
- If mentioning Matthew's businesses, prioritize practical action over hype.
- For SmartCore, repeated blockers or stale priorities may be called out
  directly, but do not nag if the facts changed.

## Final Reply

After writing the file, reply with:

- report path
- top 3 signals
- top 1 next action
- visual path or skipped-visual reason
