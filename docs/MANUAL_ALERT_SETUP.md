# Manual Alert Setup Guide

**Goal:** Get notified when new vintage audio listings appear.

---

## Craigslist Search Alerts

Craigslist supports **RSS feeds** for saved searches.

### Saved Searches

For **Athens, GA:**

1. **McIntosh**
   - URL: https://athens.craigslist.org/search/sss?query=mcintosh
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=mcintosh

2. **Pioneer Receivers**
   - URL: https://athens.craigslist.org/search/sss?query=pioneer+receiver
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=pioneer+receiver

3. **Marantz Receivers**
   - URL: https://athens.craigslist.org/search/sss?query=marantz+receiver
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=marantz+receiver

4. **Technics SL-1200**
   - URL: https://athens.craigslist.org/search/sss?query=technics+sl-1200
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=technics+sl-1200

5. **Nakamichi**
   - URL: https://athens.craigslist.org/search/sss?query=nakamichi
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=nakamichi

6. **Vintage Receiver (broader)**
   - URL: https://athens.craigslist.org/search/sss?query=vintage+receiver
   - RSS: https://athens.craigslist.org/search/sss?format=rss&query=vintage+receiver

For **Atlanta, GA:**
- Replace `athens.craigslist.org` with `atlanta.craigslist.org` in all URLs above

### RSS Reader Options

**Option A: Email Alerts via IFTTT**
1. Sign up: https://ifttt.com
2. Create applet: "If RSS feed has new item, then send me an email"
3. Paste RSS URLs above

**Option B: RSS Reader App**
- iOS: Reeder, NetNewsWire
- Android: Feedly, Inoreader
- Desktop: Thunderbird RSS, FreshRSS

**Option C: Browser Extension**
- Chrome: RSS Feed Reader
- Firefox: Feedbro

---

## Facebook Marketplace Alerts

Facebook Marketplace does **not** support RSS or email alerts directly.

### Manual Daily Check (Recommended)

**Saved Searches:**

1. **McIntosh** - https://www.facebook.com/marketplace/athens/search?query=mcintosh
2. **Pioneer SX** - https://www.facebook.com/marketplace/athens/search?query=pioneer%20sx
3. **Marantz receiver** - https://www.facebook.com/marketplace/athens/search?query=marantz%20receiver
4. **Technics turntable** - https://www.facebook.com/marketplace/athens/search?query=technics%20turntable
5. **Nakamichi** - https://www.facebook.com/marketplace/athens/search?query=nakamichi
6. **Vintage stereo** - https://www.facebook.com/marketplace/athens/search?query=vintage%20stereo

**Tip:** Bookmark these URLs and check daily (takes 5 minutes).

### Workaround: Browser Automation

Facebook Marketplace can send browser notifications if you "Save Search" within the app.

1. Visit a search URL above
2. Click "Save Search" (if logged in)
3. Enable browser notifications for Facebook.com
4. You'll get alerts when new listings match

---

## EstateSales.net Alerts

**Email Alerts Available:** Yes (built-in feature)

1. Visit: https://www.estatesales.net
2. Enter zip code: **30606** (Athens, GA) or **30301** (Atlanta, GA)
3. Set radius: 50-100 miles
4. Browse upcoming sales
5. Sign up for email alerts: https://www.estatesales.net/EmailAlerts

**Keywords to watch:**
- Audio equipment
- Stereo system
- Vintage electronics
- Hi-Fi equipment

**Tip:** Check "Detailed" view when browsing to see if listings mention brand names.

---

## AuctionZip Alerts

**Email Alerts Available:** Yes (built-in feature)

1. Visit: https://www.auctionzip.com
2. Enter zip code: **30606** (Athens) or **30301** (Atlanta)
3. Category: "Electronics" or "Antiques"
4. Sign up for email alerts

**Limitation:** Most listings don't have detailed photos until auction day.

---

## OfferUp

**Mobile App Only** - No RSS or email alerts

**Recommended:**
1. Download OfferUp app (iOS/Android)
2. Set location: Athens, GA
3. Search: "vintage receiver" / "mcintosh" / "pioneer" / "marantz"
4. Enable push notifications for saved searches

---

## Recommended Workflow

### Daily Routine (5-10 minutes)

**Morning:**
1. Check Craigslist RSS feed (via email or reader)
2. Check Facebook Marketplace (5 saved searches)
3. Check OfferUp app notifications

**Weekly:**
1. Browse EstateSales.net for upcoming Athens/Atlanta sales (Thursday-Sunday)
2. Check AuctionZip for upcoming auctions

### When You Find a Lead

1. Take screenshot
2. Copy listing URL
3. Add to `lead_intake.csv`:
   ```csv
   2026-05-04,Craigslist Athens,https://...,screenshots/lead_001.png,McIntosh MA 5100,McIntosh MA5100 Integrated Amp,750,Athens GA,"works great",yes,"clean photos, blue meters visible",unreviewed
   ```
4. Run: `python manual_lead_review.py`
5. Review generated report in `reports/lead_XXXX_review.md`

---

## Target Models (Priority Order)

High-value targets to watch closely:

1. **McIntosh MA 5100** - Alert on anything under $1,000
2. **McIntosh MA 6100** - Alert on anything under $1,200
3. **Pioneer SX-1250** - Alert on anything under $2,500
4. **Marantz 2270/2275** - Alert on anything under $1,500
5. **Technics SL-1200** - Alert on anything under $500
6. **Nakamichi Dragon** - Alert on anything under $900

---

## Search Query Templates

**Copy/paste these into each platform:**

### Exact Model Searches
```
McIntosh MA5100
McIntosh MA 5100
McIntosh MA6100
Pioneer SX-1050
Pioneer SX-1250
Marantz 2270
Marantz 2275
Sansui 9090
Technics SL-1200
Nakamichi Dragon
```

### Broader Searches (more results, more noise)
```
McIntosh
vintage receiver
stereo receiver
vintage stereo
Pioneer SX
Marantz receiver
turntable
Nakamichi cassette
```

---

## Tips for Better Results

1. **Search variations:** "MA5100" vs "MA 5100" vs "MA-5100"
2. **Check daily:** Best deals go fast (hours, not days)
3. **Expand radius:** Consider 100-mile radius for high-value items
4. **Estate sales:** Friday mornings are best (before crowds)
5. **Be first:** Contact seller within 30 minutes of listing going live
6. **Generic searches:** "vintage receiver" catches sellers who don't know brands

---

## Next Steps

1. Set up Craigslist RSS feeds today (takes 10 minutes)
2. Save Facebook Marketplace searches (takes 5 minutes)
3. Sign up for EstateSales.net email alerts (takes 2 minutes)
4. Download OfferUp app and set up saved searches (takes 5 minutes)
5. Run your first manual search tomorrow morning
6. When you find a lead, follow the workflow above

---

**Goal:** Find 5 qualified leads per month worth investigating.

**Reality check:** Most local markets are picked over. High-value vintage audio is rare. Deals exist but require patience and daily monitoring.
