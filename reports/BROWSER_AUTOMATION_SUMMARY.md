# Browser Automation Tests - Summary

**Date:** 2026-05-04  
**Tests Completed:** 2 (HTTP + Visual Browser)

---

## Quick Results

| Site | HTTP Test | Browser Test | Viable? |
|------|-----------|--------------|---------|
| Mercari | ❌ JS-only | ❌ Cloudflare blocked | ❌ No |
| Google Shopping | ❌ Blocked | ⚠️ Loaded but can't parse | ⚠️ Maybe |
| Craigslist | ❌ JS-only | ⚠️ Loaded but can't parse | ✓ Use RSS |
| Facebook | ❌ Login wall | ❌ Login required | ❌ Manual only |
| eBay | ❌ Blocked | N/A | ✓ Use API |

---

## What Actually Works

### ✓ Craigslist RSS Feeds
- No browser needed
- No JavaScript needed
- Email alerts via IFTTT
- **Status:** Ready to use

### ✓ eBay Browse API
- Official API
- Already working
- Phase 1 complete
- **Status:** In production

### ✓ Manual Searches
- Facebook Marketplace (when logged in)
- Estate sales websites
- Local auction sites
- **Status:** Documented in MANUAL_ALERT_SETUP.md

---

## What Doesn't Work

### ❌ Mercari
- Cloudflare bot detection
- Browser automation fails
- Not worth bypassing

### ❌ Google Shopping
- Aggressive bot detection
- CAPTCHA challenges
- Selectors outdated

### ❌ Facebook Marketplace Automation
- Requires login
- Account ban risk
- Manual only

---

## Test Reports

1. **VISUAL_BROWSER_TEST_001.md** - HTTP request test (all failed)
2. **VISUAL_BROWSER_TEST_002.md** - Playwright automation (partial success)

**Screenshots:** 13 PNG files in `screenshots/browser_test_002/`

---

## Recommendation

**Stick with what works:**
- Craigslist RSS feeds
- eBay Browse API
- Manual Facebook searches

**Do not build:**
- Mercari scraper (blocked)
- Google Shopping scraper (too risky)
- Facebook automation (ban risk)

Browser automation works technically but sites actively block it. Not worth the maintenance.

---

**Verdict:** Use existing tools. Skip browser automation for now.
