# page-map

Dump the accessibility tree of any web page as structured JSON. Use this before interacting with a site so you know every clickable element, form field, link, and label without guessing selectors.

## When to use

- About to interact with a new site (signup, login, click a button) and you don't know the selectors
- Site has dynamic content where HTML inspection fails
- Want a reliable inventory of buttons/inputs/links without parsing brittle HTML
- Faster than vision-based approaches, more reliable than guessing CSS selectors

## How to use

```bash
node ~/.openclaw/workspace/skills/page-map/page-map.mjs <url> [output.json]
```

Examples:
```bash
node ~/.openclaw/workspace/skills/page-map/page-map.mjs https://news.ycombinator.com/login
node ~/.openclaw/workspace/skills/page-map/page-map.mjs https://www.reddit.com/register /tmp/reddit-map.json
```

Output is a JSON tree of accessibility nodes with role, name, value, and child nodes. Reason over this instead of guessing selectors.

## What you get back

- `role` - button, link, textbox, checkbox, etc.
- `name` - the accessible label (what a screen reader would say)
- `value` - current value for inputs
- `children` - nested nodes
- `selectors` - hint selectors derived from name/role for use with Playwright

Use the structured tree to plan your interaction, then execute via direct Playwright with the discovered selectors.

## Notes

- Uses persistent profile at ~/siro-browser-profile (preserves any session cookies)
- Headless by default; pass `--headed` to see the browser
- Saves a screenshot alongside the JSON for visual context
