# ideas

Generate the Signal Engine ideas and opportunities report. Use this when Matthew
says `/ideas`, "ideas", "opportunities", or asks what to build from the current
signals.

## Purpose

Convert current signals into practical builds, business angles, and first steps.
This is the most action-oriented Signal Engine mode.

## Files

- Source list: `C:\Users\matth\Documents\openclaw-vault\signals\sources.md`
- Ideas reports: `C:\Users\matth\Documents\openclaw-vault\signals\ideas\YYYY-MM-DD.md`
- Optional current radar/full context:
  - `C:\Users\matth\Documents\openclaw-vault\signals\radar\YYYY-MM-DD.md`
  - `C:\Users\matth\Documents\openclaw-vault\signals\full\YYYY-MM-DD.md`

## Business Focus Rules

For `/ideas`, tie business ideas primarily to SmartCore Solutions.

- SmartCore: primary business focus.
- Alert Pro Solutions: do not suggest unless Matthew explicitly asks.
- Bulldawg Connected Solutions: only if the idea is obviously telecom/ISP
  relevant.
- Teton Telecom: work-adjacent; mention only if genuinely perfect.

Do not force every idea into a business. Some ideas can be personal
productivity, learning, or tooling.

## Workflow

1. Read `signals/sources.md`.
2. If today's radar or full report exists, use it as context.
3. Fetch current sources only as needed to verify claims.
4. Generate a short list of practical opportunities.
5. Every idea must include a first step that can be done without a huge setup.
6. Save the dated report.

## Output Shape

```markdown
# Ideas + Opportunities - YYYY-MM-DD

## BUILD IDEAS

**1. Idea name**
Source links.
Why it matters for Matthew.
**First step:** A concrete next action.

## SIDE PROJECTS WORTH EXPLORING

## BUSINESS ANGLES

## WHAT TO DO NEXT

Pick one build idea and one business validation move.

---

**Sources fetched:** ...
**Sources skipped or failed:** ...
```

## Judgment Rules

- Favor boring, shippable ideas over clever abstractions.
- Each idea should have an owner-like next step, not a vague recommendation.
- Do not propose dashboards, cron jobs, or extra automation unless the idea
  directly benefits from them.
- If an idea has appeared repeatedly without action, call that out once and
  either sharpen the first step or recommend dropping it.
- No fake urgency.

## Final Reply

Return the saved report path, the top 3 ideas, and the single best next action.
