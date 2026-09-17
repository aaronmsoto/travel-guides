# guide.json contract v1 — declarative travel guide

One `guides/<slug>/guide.json` per destination is the single source of truth. `tools/build.py`
renders it into a self-contained `guides/<slug>/index.html` (plus the root landing page).
Authors edit JSON, never the built HTML. Every factual field must be traceable to a source URL
listed in `sources` (official park pages first: nps.gov, recreation.gov, state DOT, etc.).

All prose fields are plain text unless noted `html:` (limited inline HTML allowed: <b>, <i>,
<a href target="_blank" rel="noopener">, <br>). Use US spelling. Dates as ISO "YYYY-MM-DD" or
"YYYY-MM". Distances in miles with km in parentheses is NOT needed — the renderer adds km.

```jsonc
{
  "schema": 1,
  "slug": "zion",                        // folder name
  "name": "Zion National Park",
  "shortName": "Zion",
  "state": "Utah",
  "tagline": "one-line hook (≤ 90 chars)",
  "lastVerified": "2026-09-17",          // date the research was checked against live sources
  "hero": { "image": "hero.jpg", "alt": "..." },   // file in guides/<slug>/img/, see images below

  "quickFacts": [                         // 6–9 items, shown as a strip under the hero
    { "label": "Entrance fee", "value": "$35/vehicle, 7 days", "note": "optional short qualifier" }
    // typical labels: Entrance fee, Best months, Nearest airport, Time zone, Elevation range,
    // Cell service, Park size, Annual visitors, Reservation needed?
  ],

  "overview": {
    "summary": "html: 2–3 short paragraphs (≤ 900 chars total) — what the place IS and why go.",
    "bestFor": ["Canyon hikes", "Photography", ...],          // 3–6 chips
    "dontMiss": ["Angels Landing at sunrise", ...],           // 3–5 one-liners
    "alerts": [                                               // current conditions that change plans; may be []
      { "level": "warn|info", "text": "html: ...", "sourceUrl": "https://..." }
    ]
  },

  "seasons": [                            // exactly 4 entries: Spring, Summer, Fall, Winter
    { "name": "Spring", "months": "Mar–May", "highs": "60–85°F", "lows": "35–55°F",
      "verdict": "Best|Good|Fair|Hard",   // one word
      "notes": "html: crowds, water, closures, what shines" }
  ],

  "logistics": {
    "gettingThere": [ { "from": "Las Vegas (LAS)", "how": "html: ~2h45m via I-15 N, UT-9 E", "miles": 160 } ],
    "gettingAround": "html: shuttle rules, parking reality, road closures",
    "fees": "html: entrance pass options incl. America the Beautiful",
    "permits": [ { "name": "Angels Landing permit", "required": true, "how": "html: lottery mechanics", "url": "https://..." } ],
    "reservations": "html: any timed-entry/reservation system or 'none'",
    "services": "html: fuel, food, water, visitor centers, cell/wifi reality"
  },

  "attractions": [                        // EXACTLY 10, ordered by rank 1..10 (most popular first)
    {
      "rank": 1, "id": "angels-landing",  // kebab-case
      "name": "Angels Landing",
      "type": "hike|viewpoint|scenic-drive|area|canyon|dunes",
      "difficulty": "easy|moderate|strenuous|extreme",  // per official rating where possible
      "stats": { "distance": "5.4 mi round trip", "elevationGain": "1,488 ft", "time": "4–5 hr", "trailheadOrParking": "The Grotto (shuttle stop 6)" },
      "permit": "none|required|lottery",  // + explain in `permitNote` if not none
      "permitNote": "html: ...",
      "bestTime": "Early morning; avoid midday heat",
      "seasonNote": "Chains section ices Dec–Feb",
      "summary": "html: 2–4 sentences — what it is and why it's popular (≤ 600 chars)",
      "tips": ["3–5 concrete, actionable tips (≤ 140 chars each)"],
      "accessibility": "optional: paved/wheelchair/strollers/kids note",
      "image": "angels-landing.jpg",     // file in img/; MUST exist in img/manifest.json
      "coords": [37.269, -112.9477],     // [lat, lng] of the viewpoint/trailhead — used by the map and to place photos
      "sources": ["https://www.nps.gov/..."]
    }
  ],

  "alsoConsider": [                       // 3–6 honorable mentions, one line each
    { "name": "Kolob Canyons", "why": "html: ...", "url": "https://..." }
  ],

  "stay": {
    "camping": [
      { "name": "Watchman Campground", "kind": "developed|primitive|dispersed|backcountry",
        "where": "html: just inside the South Entrance, walk to visitor center",
        "booking": "reservable|first-come|mixed|permit",
        "bookingDetail": "html: exact mechanics — window, site, lottery, fees, season",
        "sites": "176 sites", "cost": "$35–45/night", "season": "Year-round",
        "amenities": ["water", "flush toilets", "electric hookups (some)"],
        "goodFor": "Tents, RVs to 40 ft", "url": "https://www.recreation.gov/..." ,
        "sources": ["..."] }
    ],
    "lodging": [
      { "name": "Springdale, UT", "kind": "town|in-park lodge|nearby town",
        "distance": "At the South Entrance", "priceBand": "$$–$$$$",
        "summary": "html: ...", "examples": ["a few named, well-known properties — no prices"], "url": "https://..." }
    ]
  },

  "safety": [ { "title": "Heat", "body": "html: ≤ 400 chars, concrete numbers and rules", "level": "critical|important|note" } ],

  "itineraries": [
    { "title": "One perfect day", "days": 1, "plan": [ { "when": "6:30 am", "what": "html: ..." } ] },
    { "title": "Two days", "days": 2, "plan": [ { "when": "Day 1 AM", "what": "..." } ] }
  ],

  "faq": [ { "q": "...", "a": "html: ..." } ],          // 5–8 real questions travelers ask

  "sources": [ { "title": "NPS – Angels Landing Permits", "url": "https://..." } ],   // every URL used above
  "images": { "manifest": "img/manifest.json" }         // written by tools/fetch_images.py
}
```

## img/manifest.json (written by tools/fetch_images.py)
```jsonc
{ "angels-landing.jpg": { "title": "...", "author": "NPS", "license": "Public domain (US Gov)|CC BY 2.0|CC BY-SA 4.0|...",
    "licenseUrl": "...", "sourceUrl": "https://commons.wikimedia.org/wiki/File:...", "width": 1600, "height": 1067 } }
```
Only public-domain, CC0, CC BY, or CC BY-SA images. Credit is rendered under every image.

## `trip` — the specific upcoming trip this guide supports (schema 1.1)
Guides are invitations: they exist to share the plan for a real trip with people who might join.
`trip` renders as the FIRST tab ("The Trip") and as a banner on every other tab. There is NO
day-by-day schedule: the Top 10 attractions are rendered inside the trip tab as a teaser grid of
"what we might do", so the trip tab stays about logistics people can plan around plus the invitation.
```jsonc
"trip": {
  "title": "Zion, Thanksgiving week 2026",
  "start": "2026-11-21", "end": "2026-11-25",      // ISO dates, inclusive
  "status": "planning|confirmed",
  "host": "Aaron",                                  // first name shown in "Join" copy
  "pitch": "html: 1–2 sentences inviting people",
  "base": { "name": "Springdale, UT", "coords": [37.1889, -112.9986], "detail": "html: where exactly, what it's like, how far from the park",
            "mapUrl": "https://..." , "bookingNote": "html: optional — how joiners should book" },
  "arrival": "html: travel-in plan (airport, drive, first night)",
  "departure": "html: travel-out plan",
  "conditions": [ { "label": "Weather", "text": "html: ..." } ],   // 4–7 short blocks: temps, daylight, shuttle/permit status, closures, crowds
  "bring": ["packing list items specific to these dates"],
  "join": { "text": "html: why and how to join", "steps": ["1–4 concrete steps"] },
  "openQuestions": ["optional: things still undecided that joiners can weigh in on"]
}
```
Internal links: `<a href="#top10/angels-landing">` opens that attraction card (no target=_blank).

## Photos (optional) — `guides/<slug>/photos/photos.json`, written by tools/import_photos.py
```jsonc
{ "albums": [ { "title": "January 2025", "credit": "Aaron Soto",
    "items": [ { "file": "january-2025-5b046217.jpg", "w": 1600, "h": 1067, "taken": "2025-01-18T09:12" | null,
                 "lat": 36.42 | null, "lng": -116.81 | null,   // from EXIF when present
                 "place": "zabriskie-point",                   // attraction id (or "base"); used for the map when no GPS
                 "caption": "..." } ] } ] }
```
Renders as the "Photos & Map" tab: a grid with a lightbox, and a map (Leaflet + OpenStreetMap tiles, loaded only
when the map view is opened) showing photo pins, Top 10 pins (from `coords`), and the trip base.
