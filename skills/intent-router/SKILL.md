# intent-router

Use this skill at the start of every Matthew request when the intent is not
already obvious from a slash command or direct skill name. The goal is to
recognize what Matthew means, find the existing skill/tool that already handles
it, and route there before inventing a new plan.

## First Move

Classify the request before acting:

```powershell
python scripts\intent_router.py "Matthew's exact request here"
```

Then open the returned `skills/<name>/SKILL.md` and follow that workflow.

## Non-Negotiable Rule

Do not recreate a new strategy when a skill already exists.

If Matthew asks for "Athens marketplace good deals," do not open Facebook in a
browser. Route to `freebie-radar` first. If the request clearly includes resale,
profit, sold comps, or flipping, route to `arbitrage-deal-desk`.

## Intent Map

- Local marketplace / Athens deals / free pickup / cheap nearby listings:
  `freebie-radar`
- Resale / arbitrage / profit / sold comps / Mercari / Facebook underwriting:
  `arbitrage-deal-desk`
- Restaurants / food mood / cuisine / lunch / dinner:
  `athens-food`
- SmartCore invoices / billing / quotes / proposals:
  `smartcore-billing`
- Voice files / read it aloud / ElevenLabs / sag:
  `voice-output`
- Overwatch / WiFi monitor / RF environment:
  `overwatch-rf`
- Apify actors / scrapers / actor catalog:
  `apify-actors`
- Browser/page controls / buttons / inspect site:
  `page-map`
- `/signals`, `/radar`, `/bigpic`, `/ideas`:
  matching slash-command skill

## Ambiguous Marketplace Rule

When Matthew says "marketplace" without perfect wording:

1. If the words are local, Athens, nearby, area, free, cheap, pickup, or deals:
   use `freebie-radar`.
2. If the words are resale, arbitrage, profit, flip, sold comps, or worth buying:
   use `arbitrage-deal-desk`.
3. Ask one short clarifying question only if both are equally likely.

## Fallback

If no route fits:

1. Read `COMMANDS.md`.
2. Read `skills/manifest.json`.
3. Read `.openclaw/skill-manifest.json`.
4. Search `skills/*/SKILL.md`.
5. Only then say the workflow is missing or propose a new one.

## Response Style

When routing matters, say the route briefly:

```text
This sounds like local marketplace deal hunting, so I am using freebie-radar first.
```

Then do the work. Do not over-explain the router unless Matthew asks.
