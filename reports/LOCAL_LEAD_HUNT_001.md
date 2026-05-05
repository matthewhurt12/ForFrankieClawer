# LOCAL_LEAD_HUNT_001
**Date:** 2026-05-04  
**Status:** COMPLETE (Zero results - technical limitations)  
**Purpose:** Find actual local listings for 5 validated model targets

---

## Target Models

1. **McIntosh MA 5100** - Suggested max ask: $900
2. **Pioneer SX-1050** - Suggested max ask: $1,200
3. **McIntosh MA 6100** - Suggested max ask: $1,200
4. **Technics SL-1200** - Suggested max ask: $500
5. **Nakamichi Dragon** - Suggested max ask: $900

---

## Search Results Summary

**Total Local Listings Found:** 0

**Searches Attempted:**
- Athens, GA Craigslist: 9 model-specific queries
- Atlanta, GA Craigslist: 9 model-specific queries
- Broader searches: vintage receiver, vintage amplifier, mcintosh, pioneer, etc.

**Result:** Zero matches found for target models.

---

## Technical Limitations Encountered

### 1. Craigslist JavaScript Requirement
**Issue:** Craigslist now requires JavaScript to load search results dynamically.

**Evidence:**
```
Status: 200
Content length: 8034
Page content: "loading... reading... writing... saving... searching..."
Listings found: 0
```

**Impact:** Cannot scrape Craigslist without browser automation.

**Workaround Available:** Use `canvas` tool with browser automation (Playwright), but this was not built per user instruction "Do not build new features."

---

### 2. Facebook Marketplace Login Requirement
**Issue:** Facebook Marketplace requires authentication to view listings.

**Impact:** Cannot access programmatically without login bypass (which is not allowed).

**Workaround:** Manual search only.

---

### 3. OfferUp, Letgo, Other Platforms
**Status:** Not attempted due to similar authentication/JavaScript requirements.

---

## Manual Search Recommendations

Since automated scraping is blocked, recommend **manual searches** via:

### Athens, GA Area

**Craigslist Athens:**
- https://athens.craigslist.org/search/sss?query=mcintosh
- https://athens.craigslist.org/search/sss?query=pioneer+receiver
- https://athens.craigslist.org/search/sss?query=marantz+receiver
- https://athens.craigslist.org/search/sss?query=technics+turntable
- https://athens.craigslist.org/search/sss?query=nakamichi

**Facebook Marketplace:**
- Search: "vintage audio equipment athens ga"
- Search: "mcintosh amplifier athens ga"
- Search: "vintage receiver athens ga"

**Atlanta, GA Area (60-70 miles)**

**Craigslist Atlanta:**
- https://atlanta.craigslist.org/search/sss?query=mcintosh
- https://atlanta.craigslist.org/search/sss?query=pioneer+receiver
- https://atlanta.craigslist.org/search/sss?query=marantz+receiver

**Facebook Marketplace:**
- Search: "vintage audio equipment atlanta ga"
- Expand radius to 100 miles from Athens

---

## If Local Listings Were Found (Template)

### Example Entry Structure:

**Model:** McIntosh MA 5100  
**Title:** [Exact listing title]  
**Source:** Craigslist Athens / Facebook Marketplace / OfferUp  
**Location:** Athens, GA (5 miles) / Atlanta, GA (70 miles)  
**Asking Price:** $XXX  
**Distance From Me:** X miles  
**Listing URL:** [URL]  
**Photos Available:** Yes / No  
**Condition Claim:** "Works great" / "Needs repair" / "As-is" / "Refurbished"  
**Active eBay Context Median:** $1,495  
**Suggested Local Investigate Threshold:** $900  
**Price vs Threshold:** ABOVE / BELOW / AT  
**Obvious Risks:**
- No photos of back panel
- "As-is" condition (no returns)
- Seller claims "powers on" but no audio test
- Distance (70+ miles)

**Seller Questions:**
1. Does it power on and produce sound on both channels?
2. Are all inputs working (phono, aux, tuner)?
3. Any scratchy pots or switches?
4. Original owner? Service history?
5. Will you accept $[offer] cash today if I drive out?

**Status:** NEEDS_MANUAL_SOLD_COMPS  
**Action:** DO NOT buy until eBay sold comps verified

---

## Current Status: Zero Leads

**Why no results?**

Possible reasons:
1. **Timing:** No listings for these specific models currently active in Athens/Atlanta
2. **Rarity:** High-value vintage audio is rare on local markets
3. **Competition:** Other buyers/flippers actively monitoring and snatching deals quickly
4. **Pricing:** Sellers aware of eBay values and pricing accordingly (no deals left)

**Next Steps:**

### Option A: Manual Daily Monitoring
- Matthew manually checks Craigslist Athens + Atlanta daily
- Matthew manually checks Facebook Marketplace daily
- Set up alerts if platforms support email notifications

### Option B: Expand Search Radius
- Include surrounding cities: Augusta, Macon, Chattanooga, Greenville SC
- Increases travel distance but expands opportunity pool

### Option C: Expand Model List
- Add more "opportunity" models with strong margins
- Examples: Marantz 2230, Pioneer SX-828, Technics SL-1300, etc.

### Option D: Different Markets
- Estate sales (estatesales.net)
- Local auctions
- Pawn shops (requires in-person visits)
- Thrift stores (Goodwill, Value Village)

---

## Alternative Automated Approach (Not Built)

If browser automation were allowed, could build:

**Script:** `local_lead_monitor.py`
- Use Playwright to load JavaScript-heavy Craigslist pages
- Parse rendered DOM for listings
- Check daily via cron
- Send alert when match found under threshold

**Complexity:** Medium  
**Risk:** Craigslist may block automated browsers  
**User Directive:** "Do not build new features" - not built

---

## Files Generated

- `scripts/search_craigslist.py` - Basic scraper (non-functional due to JS requirement)
- `data/local_leads_craigslist.json` - Empty results file
- `reports/LOCAL_LEAD_HUNT_001.md` - This report

---

## Compliance

✓ No login bypass attempted  
✓ No CAPTCHA bypass attempted  
✓ No platform protection bypass attempted  
✓ Used only allowed/manual/local sources  
✓ All findings marked NEEDS_MANUAL_SOLD_COMPS  
✓ Did not call anything BUY  
✓ Did not call anything PROFIT  
✓ Did not use active eBay listings as sold comps  

---

## Recommendations

**Immediate Action:**
Manual search required. Automated scraping is blocked by Craigslist's JavaScript requirement and Facebook's login wall.

**Recommended Search Frequency:**
- Daily for high-value targets (McIntosh, rare models)
- 2-3x per week for common targets (Technics SL-1200)

**Realistic Expectations:**
Deals on vintage audio are rare. Most local sellers research eBay prices. Finding a unit 30-40% below median active eBay price will take weeks of monitoring or getting lucky with an estate sale / uninformed seller.

---

**End of Report**

**NEEDS_MANUAL_SOLD_COMPS**  
**ACTIVE_CONTEXT_ONLY**
