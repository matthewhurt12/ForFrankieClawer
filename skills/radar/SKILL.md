# radar

Generate the Signal Engine radar scan. Use this when Matthew says `/radar`,
"radar", "what happened", or asks for a quick current scan.

## Purpose

Produce a short, source-backed briefing on what changed recently in AI, agents,
tech, telecom, security, and relevant business infrastructure. Radar is for
awareness and triage, not deep forecasting.

## Files

- Source list: `C:\Users\matth\Documents\openclaw-vault\signals\sources.md`
- Radar reports: `C:\Users\matth\Documents\openclaw-vault\signals\radar\YYYY-MM-DD.md`

## Workflow

1. Read `signals/sources.md`.
2. Fetch current sources. Use publish dates.
3. Pull the most relevant items only:
   - Pots and Pans: last 2-3 posts by date.
   - Hacker News: top/front-page items filtered for relevance.
   - Simon Willison, OpenAI, Anthropic, Latent Space, One Useful Thing, TLDR,
     and free Stratechery when accessible.
4. Skip dead, paywalled, or login-only pages. Note skipped sources at bottom.
5. Write the radar report to today's dated file.

## Output Shape

```markdown
# Tech Radar - YYYY-MM-DD

## WHAT HAPPENED

- **Item title** - one or two sentences with source link.

## WHY IT MATTERS

- Explain the pattern or consequence. Avoid generic "this is important."

## WHAT TO WATCH

- Short list of follow-up indicators.

## WHAT TO DO NEXT

- Practical next moves for Matthew, if any.

---

**Sources fetched:** ...
**Sources skipped or failed:** ...
```

## Judgment Rules

- Radar should be concise. Prefer 6-10 strong items over 30 weak ones.
- Do not include random news unless it changes a decision, tool, business, or
  worldview Matthew cares about.
- Business tie-ins are optional. Mention SmartCore, Alert Pro, Bulldawg, or
  Teton only when naturally relevant.
- No unsourced current claims.

## Final Reply

Return the saved report path plus the top 3 radar items.
