# Critique report — Zion & Death Valley trip guides (v1 draft)

Three adversarial reviewers on fresh contexts, 2026-09-17: a **prospective traveler** (31 findings),
a **UI/UX designer** (32 findings, measured in-browser at 390/1200 px, dark, print, keyboard), and a
**product innovator** (30 findings + scorecard). Full reports: `critique-traveler.md`,
`critique-ux.md`, `critique-product.md`. This file is the synthesis and the fix plan; the
implementation log at the bottom records what changed.

## Consensus verdict

All three agree on the same shape: **the content is excellent and the invitation is missing.**
Every reviewer independently praised the research depth (exact permit mechanics, booking windows,
fees, all traceable to dated NPS/recreation.gov notes; the product reviewer spot-checked three
claims and found all accurate), the Trip-first information architecture, the Top 10 card model, and
the Photos & Map tab. All three would go to Death Valley; two of three would go to Zion.

What nearly stopped them, in every report:

1. **No way to say yes.** "Tell Aaron you are in" with no mailto, chat link, or form anywhere.
2. **The Zion night count is wrong.** "Four nights in Springdale" — night one is in Las Vegas, so a
   joiner following "book early" books a wrong Thanksgiving-week night. The validator never looks at
   `trip`, which is how it shipped.
3. **No cost, no capacity, no deadline.** The only Zion prices are $6 and $35. Death Valley's binding
   constraint (12 people / 3 vehicles) is a clause mid-paragraph.
4. **Death Valley contradicts itself about vehicles** (Trip: "a careful SUV or crossover"; Stay: "8 in
   clearance, 4WD"; FAQ: "usually 4x4"), and buries "rental agreements forbid unpaved roads."
5. **The shared link is broken as an object.** Relative `og:image`, guide-flavored title, description
   truncated mid-word, no `og:url`; deep links land under the sticky header (a literal `\n` in
   theme.css silently killed the scroll-margin rule); the "Add to my trip" shortlist can't be sent.
6. **Date-blind sections.** Safety leads with July heat for a November trip and the summer "10 am
   rule" for a January camping trip; itineraries are generic 1–2 day plans; Zion's photos are a
   summer 2012 album captioned "what the trip actually looks like."

Product scorecard: job-to-be-done 3/5 · content trust 4/5 · showing-off 3/5 · share/response loop
**1/5** · pipeline 3/5.

## Cross-cutting themes

| Theme | Raised by | Representative findings |
|---|---|---|
| Response loop absent (reply path, RSVP, capacity, roster, calendar) | all three | T1, T7, T17 · U5 · P3, P9, P10, P11 |
| Wrong or missing numbers a joiner acts on (nights, cost, 160 vs 170 mi) | all three | T2, T8, T19 · P4, P5 |
| Vehicle / camp-life clarity for Death Valley | traveler, product | T3, T4, T10 |
| Trip-relevance of generic sections (safety, alerts, itineraries, photos lede, FAQ) | all three | T14, T15, T16, T21 · U14, U18 · P6, P7, P19, P26 |
| Deep links and mobile layout bugs | UX, product | U1 (horizontal scroll at 390), U2/P13 (`\n` bug), U15 (193 px header), U3 ("Duness") |
| Share surface (OG tags, hosting, base URL) | product | P1, P2, P29 |
| Accessibility (contrast on accent fills, live regions, focus ring, reduced motion, unit toggle name) | UX | U4, U12, U17, U21, U25 |
| Dev-speak leaking to readers | traveler, product | "Tips from the research", landing footer `guide.json` line |
| Image use (Top 10 ships 6 MB full-res; 5 MB fetched but unused while Stay has no photo; card crops) | UX, product | U7 · P14, P20 |
| Print (prints all 9 tabs, strips URLs) | UX, product | U10, U11 · P15 |
| Personal photos: relevance and consent for identifiable minors on a forwardable link | product | P12 |

## Fix plan

### Fixed in this pass (v1.1)
- **Numbers:** Zion night count everywhere (banner shows "4 nights · 3 in Springdale + 1 in Las
  Vegas"); Las Vegas distance unified to the NPS figure; Angels Landing stat strings shortened.
- **Response loop:** `trip.contact` in the schema; a primary **"I'm in"** action on the Join card and
  the trip bar that opens a prefilled email when a `mailto` is configured, otherwise copies a
  prefilled RSVP (nights, headcount, vehicle, picks) to paste into the chat the link came from;
  shortlist renamed **My picks**, shareable via URL (`#trip/picks=…`) and included in the RSVP;
  per-guide `trip.ics` with "Add to calendar"; capacity meter for Death Valley (12 people /
  3 vehicles); a **cost** card using only sourced figures and honest "varies" lines; Status card
  replaced, host/draft note moved to a byline.
- **Death Valley clarity:** one authoritative "Can my car get to camp?" block (E1's first mile vs the
  deeper sites), the rental-car warning moved into the Join card, a plain-English "Camp life: water,
  toilets, trash" block, "wag bags" and "dispersed" explained, the "weekend" wording fixed.
- **Trip relevance:** safety entries carry `seasons` and the tab opens with "For our dates"; alerts
  carry `affectsTrip` and the trip tab shows "Affects our dates"; a trip FAQ (cost, one day only,
  must I camp, kids, car, fitness) under the Join card; Zion trip conditions now mention the
  cyanobacteria advisory and acknowledge November is past the "best months"; Zion photo lede says
  "the place, not the season"; generic itineraries re-labeled "if you only have a day"; key dates
  strip ("day-before lottery: apply Fri Nov 20", "Furnace Creek window opened Jul 15").
- **Share surface:** `site.json` base URL; absolute `og:image`/`og:url`, trip-flavored `og:title`,
  word-boundary description, `twitter:card`; landing page rewritten as an invitation set sorted by
  trip date with host byline, real CTA, no dev-speak.
- **Bugs:** hero `width:100%` (horizontal scroll at 390 px); literal `\n` in theme.css; deep-link
  scroll offset computed from the real sticky stack; `.tripbar[hidden]`; "Duness"; unit-toggle
  label/name; bad hash self-corrects.
- **Accessibility:** `--on-accent` token (Death Valley light accent darkened to pass 4.5:1); live
  regions for filter count, picks, and copy feedback; themed focus ring on links; reduced-motion
  support; lightbox scroll lock; credit moved out of the image into the card footer (fixes tab order).
- **Layout:** attraction photos no longer stretched (4:3, sticky); `grid3` no longer stretches short
  cards; base card full width; mobile masthead compacted and tab strip gets an edge fade; filters
  sticky on mobile as one scrollable row; stats grid tolerates uneven lengths; tripbar separators
  vanish at wrap; card borders visible; photo captions always visible.
- **Images:** Top 10 uses a 960 px tier with `srcset` (Zion tab 6 MB → ~1.5 MB); Stay and "Also
  consider" render images (Springdale, Watchman, Kolob, Titus, Racetrack…); four fetched-but-unused
  images pruned so the credits list matches the page; "≈ N mi from base" (straight line) on cards.
- **Print:** picks print only the picks; URLs printed after links; countdown and banner suppressed.
- **Pipeline:** `validate.py` now checks `trip` (required fields, date order, base coords, night
  count vs. pitch), photo `place` resolution, attraction coords, source traceability, and warns when
  `lastVerified` is stale; client-side staleness tier on the alerts box.
- **Copy:** "Tips from the research" → "Good to know"; jargon expanded on first use on the Trip tab.

### Deliberately not done (and why)
- **Day-by-day schedule** (T16, P7): the owner explicitly asked for no day-by-day; the Top 10 tiles
  and "open questions" carry the "what might we do" role. Revisit if joiners ask which day is the big
  hike.
- **Host email on the page** (T1, P3): the mechanism is built, but publishing a personal address or
  chat link is the owner's call — set `trip.contact` in each guide.json.
- **Photo curation / `private` flag** (P12): the `private: true` flag is implemented in the importer
  and build (excluded from the page, kept in the repo), but no photo was hidden — which family photos
  go on a forwardable link is the owner's decision.
- **Roster / "who's in"** (P11): `trip.roster` is supported but empty; fill as people say yes.
- **Prices we can't source** (T8, P5): no Springdale nightly rate or gear-rental price is stated;
  the cost card says "varies" with the reason rather than an invented number.
- **Faceted-filter dead ends, map clustering, per-attraction drive times** (U28, U22, P30): next
  version; drive times need a sourced figure per attraction.

### Next version
Trip-dated deadlines computed from the trip (P8), map promoted with clustering and SRI (P16, U22),
interactive bring list with a "N of 9 packed" counter (P28, T27), share-card image at 1200×630 (P1),
"what changed since you last looked" strip (P30), GitHub Pages deploy with a rebuild-and-diff check
(P29).

## Implementation log (v1.1, 2026-09-17)
- Rewrote `tools/build.py` (v2), `shared/engine.js`, `shared/theme.css`; added `site.json`,
  `tools/validate.py` trip/photo/coords/traceability checks, schema 1.2 notes in `tools/schema.md`.
- Data: both `guide.json` files gained `trip.contact/cost/capacity/keyDates/faq`, `base.kind/image`,
  `nightsNote` (Zion), rewritten `conditions` (Death Valley: "Can my car get to camp?", "Camp life"),
  `safety[].seasons`, `alerts[].affectsTrip`, `stay.*.ours/image`, `alsoConsider[].image`, shortened
  stat strings, a new "Cold nights at low elevation" safety entry (Death Valley), darker light-mode
  accent (Death Valley), Zabriskie sunrise as the Death Valley hero.
- Images: pruned 4 unused files; generated a 960 px `mid-` tier for `srcset`.
- Verified in-browser: no horizontal scroll at 390 px; deep links land below the sticky stack;
  picks → RSVP text includes the pick list and a `#trip/picks=` link; dark-mode buttons readable.
- Left for the owner: set `trip.contact.email` or `chatUrl`; decide which personal photos stay
  public (`private: true`); fill `trip.roster` and `capacity.peopleTaken` as people say yes.
