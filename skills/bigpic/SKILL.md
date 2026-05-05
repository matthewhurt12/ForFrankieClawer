# bigpic

Generate the Big Picture Signal Engine report. Use this when Matthew says
`/bigpic`, "big picture", or asks for the strategic synthesis without the full
radar and ideas report.

## Purpose

Find the main pattern underneath current AI, tech, telecom, agent, and business
signals. This is not a news recap. It should answer: what is shifting, why does
it matter, who wins, who loses, and what should Matthew learn or build next?

## Files

- Source list: `C:\Users\matth\Documents\openclaw-vault\signals\sources.md`
- Bigpic reports: `C:\Users\matth\Documents\openclaw-vault\signals\bigpic\YYYY-MM-DD.md`
- Optional current radar/full context:
  - `C:\Users\matth\Documents\openclaw-vault\signals\radar\YYYY-MM-DD.md`
  - `C:\Users\matth\Documents\openclaw-vault\signals\full\YYYY-MM-DD.md`
- Big-picture visuals: `C:\Users\matth\Pictures\signals\YYYY-MM-DD-bigpic.png`

## Workflow

1. Read `signals/sources.md`.
2. If today's radar or full report exists, use it as context.
3. Fetch current sources as needed. Verify publish dates and source links.
4. Pick one core thesis. If there is no real unifying thesis, say so instead of
   forcing one.
5. Write the big-picture report.
6. Generate the editorial concept visual only when the thesis is strong enough.

## Output Shape

```markdown
# Big Picture - YYYY-MM-DD

## CORE SHIFT

One clear thesis paragraph.

## PLAIN ENGLISH EXPLANATION

Explain the shift without assuming Matthew already knows the topic.

## WHAT'S NOISE VS SIGNAL

**Overhyped:**
- ...

**Under-covered:**
- ...

## WHERE THIS GOES (6-18 MONTH FORECAST)

Name likely winners, losers, and timeline.

## WHAT MATTHEW SHOULD LEARN/BUILD

**Learn:**
- ...

**Build:**
- ...

---

**Sources fetched:** ...
**Sources skipped or failed:** ...
```

## Visual Rule

Create one editorial concept image when there is a real thesis:

- Medium quality, 1536x1024 landscape.
- Save to `C:\Users\matth\Pictures\signals\YYYY-MM-DD-bigpic.png`.
- Style: clean flat vector, navy plus orange accent, white background, minimal
  labels, no decorative people, readable in 3 seconds on a phone.
- Pick one metaphor: shift, pressure, scale, network, timeline, or map.

Skip the image if the report is mostly factual updates. Use exactly:

`No big-picture visual today - today's signal is mostly discrete updates without a unifying pattern.`

## Judgment Rules

- Do not make this a giant list.
- Do not force business tie-ins.
- Include sources for factual claims.
- Use direct language. The value is synthesis, not polish.

## Final Reply

Return the saved report path, the core shift in one sentence, and the visual path
or skipped-visual reason.
