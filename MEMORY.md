# MEMORY.md - Long-Term Memory

## Profile

**Name:** Matthew  
**Age:** 24  
**Location:** Athens, GA  
**Education:** UGA grad (Anthropology + Entrepreneurship)

### Companies
- [[Alert Pro]] - School safety/security systems
- [[SmartCore]] - GPS fleet tracking + IoT monitoring
- [[Bulldawg Connected Solutions]] - WISP/wireless ISP in Athens
- [[Teton Telecom]] - FTTH deployment consulting with [[Mark Metcalf]]

### Tech Stack
Node.js, Next.js, Supabase, Firebase, Python, Google BigQuery, Raspberry Pi, Flipper Zero, Linux/WSL2. Builds real systems, not demos. Loves hardware tinkering and networking.

### Interests
- Algorithmic trading (FreqTrade, Pine Script/TradingView)
- Crypto, prediction markets (Kalshi, Polymarket)
- Personal development / habit systems
- Running and working out
- Building dashboards, voice assistants, surveillance tools, IoT projects

### People
- [[Laura]] - Girlfriend. Runs Shopify stores for custom printing/merch.
- [[Hannah]] - Sister. Artist in Aspen.
- [[Mark Metcalf]] - Senior colleague at Teton Telecom.

---

## Preferences

### Communication Style
- Casual, direct. Competent colleague, not customer service rep. #preference
- No em dashes. No fluff. No filler. #preference
- Push back when he's wrong. #preference
- Don't stack up clarifying questions. Just do the thing. #preference
- Polished tone for client-facing deliverables (emails, docs, proposals). #preference
- His own voice when it's his own writing. #preference

### Working Style
- Prefers action over planning
- Values real systems over toy demos

### Workspace Navigation #decision
- If Matthew asks for a skill, slash command, or "that thing we built," Frankie should check `START_HERE.md`, `COMMANDS.md`, and `skills/manifest.json` before saying it cannot find it.
- Local skill folders now include `arbitrage-deal-desk`, `page-map`, `signals`, `radar`, `bigpic`, and `ideas`.
- Signal Engine reports live in `C:\Users\matth\Documents\openclaw-vault\signals`.
- The arbitrage Deal Desk safe command is `python scripts\run_arbitrage_pipeline.py`; paid Apify collection requires explicit `--collect`.

---

## Current Projects

See detailed journals in `projects/`:
- [[Alert Pro]] - School safety systems #project/alert-pro
- [[SmartCore]] - Fleet tracking + IoT #project/smartcore
- [[Teton Telecom]] - FTTH consulting #project/teton-telecom
- [[Laura Art]] - Laura's Shopify stores #project/laura-art
- [[MET]] - Dating app #project/met
- [[Arbitrage Deal Desk]] - Retro tech resale lead pipeline #project/arbitrage
- [[Signal Engine]] - Current signals, radar, big-picture, ideas #project/signals
- [[Frankie Mind]] - Navigation, memory, and skills organization #project/frankie-mind

---

## Concerns

_(What's on Matthew's mind right now)_

---

## Patterns

_(Behaviors noticed over time)_

---

## Decisions

### 2026-04-21: WSL2 for OpenClaw #decision
- Running OpenClaw in WSL2 Ubuntu after native Windows install hit unfixable EPERM errors. Don't go back to native Windows.
- OpenClaw CLI commands hang when gateway is in certain states. Prefer direct config edits at `~/.openclaw/openclaw.json` and process kills (`pkill -f openclaw-gateway` then `openclaw gateway start`) over `openclaw gateway restart`.
- Elevated commands (sudo) are enabled for Telegram. Use responsibly.

### 2026-04-21: Browser automation approach #decision
- Native browser tool has empty default profiles, so not included in "coding" profile. Agent profile is set to "full" to fix this.
- MCP Playwright doesn't work with the Anthropic harness. Skip that path entirely.
- OpenClaw's native browser tool is flaky on WSL2 with snap Chromium, but direct Playwright scripts work reliably.
- Working pattern: Write Node script using Playwright, launch Chromium at `/snap/bin/chromium`, save artifacts to `/tmp`. For headed/visible mode, set `DISPLAY=:0` and `headless: false`, use `slowMo: 500-800` for watchable demos.
- Use DuckDuckGo for search automation. Google throws reCAPTCHA at scripted browsers. #preference
- Reach for the browser only when needed (apps, forms, dashboards, dynamic content screenshots). Use `web_fetch` for reading articles and pulling page content — faster, no bot detection.
