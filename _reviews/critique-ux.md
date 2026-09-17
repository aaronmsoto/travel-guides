# UX / UI critique — Zion + Death Valley guides and the landing page

Reviewer: senior UI/UX designer, adversarial pass. Reviewed the **rendered** pages
(`guides/zion/index.html`, `guides/death-valley/index.html`, `index.html`) at 1200 px and 390 px,
in light and dark, with print emulation, keyboard, and Playwright instrumentation.
Screenshots referenced below live in the session scratchpad as `rv-ux-*.png`.

---

## Verdict

The bones are genuinely good. The trip-first IA (a **The Trip** tab ahead of the reference
material, a persistent date/countdown banner, a "Join this trip" CTA) is the right call for a page
whose job is recruiting friends, and it reads as one product across both parks and the landing page.
The Top 10 card model — rank badge, type/difficulty/permit tags, official stats, collapsible tips,
sources on every card — is more honest and more useful than most commercial park guides. The Photos
& Map tab is a real differentiator: lazily-loaded Leaflet, photo pins grouped by location, an
explicit "near" disclosure for approximated positions, and a correct offline fallback. Resilience is
good: blocking `localStorage` throws nothing and the page still renders.

**The three biggest usability risks:**

1. **The page is broken at phone width on the tab most people will land on.** The Overview hero
   forces the document to 529 px inside a 390 px viewport — the whole page scrolls sideways, on both
   guides (#1). That, plus a 193 px sticky header (23% of the viewport) and a tab bar that hides 53%
   of itself with no affordance (#15), makes the mobile first impression bad.
2. **Shared links land on a hidden card.** The "Share" button on every attraction produces
   `#top10/<id>`, and that link scrolls the card to y=0 — completely under 230 px of sticky header
   plus sticky filter bar. The recipient sees a mid-card paragraph and no title (#2). A CSS typo
   (a literal `\n` in `theme.css`) silently kills the rule meant to prevent this.
3. **The collaboration loop doesn't close.** "Add to my trip" is the page's one interactive promise,
   and the resulting shortlist lives in one browser's `localStorage` with no way to send it to the
   person organising the trip (#5). Friends can decide, but they can't tell anyone.

Findings are numbered in rough order of user impact.

---

## Findings

### 1. BLOCKER — Overview tab scrolls horizontally at 390 px (both guides)

**Where:** `#overview`, `.hero`, 390 px. Evidence: `rv-ux-z-overview-390.png`,
`rv-ux-dv-overview-1200.png`; measured `document.documentElement.scrollWidth = 529` vs
`innerWidth = 390`; `.hero` bounding box is **513.3 × 220** inside a 358 px content column. The hero
photo, its overlay title and the "Photo: NPS" credit chip are all clipped off the right edge.

**Problem:** `.hero{aspect-ratio:21/9; min-height:220px}` — when `min-height` wins over the
aspect-derived height, the box resolves its width from the ratio (220 × 21/9 = 513 px) instead of
from the container. Violates the most basic responsive contract; every horizontal swipe on Overview
now drags the page.

**Fix:** one declaration in `shared/theme.css`, verified:

```css
.hero{ ...; width:100%; }   /* doc width 529 -> 390, hero 358x220, min-height preserved */
```

`max-width:100%` also works. Do not just drop `min-height` — that collapses the hero to 153 px on a
phone.

### 2. BLOCKER — "Share" deep links land under the sticky chrome; title invisible

**Where:** `#top10/<id>` on both guides, 1200 px. Evidence: `rv-ux-z-deeplink-1200.png` — open
`…#top10/angels-landing` and the `<h3>` sits at **y = 17** while the sticky header bottom is **131**
and the sticky filter bar bottom is **230**. The card name, rank badge, tags and half the stats are
behind the chrome; the `.flash` highlight fires off-screen too. At 390 px the header bottom is 193
and the card top is 0.

**Root cause (two bugs):**
- `.attr` has `scroll-margin-top: 0px` (measured) — nothing compensates for the sticky stack.
- `shared/theme.css` line 262 contains **literal `\n` characters** instead of newlines:
  `…margin-bottom:0}\n.conds .eyebrow{…}\n.sec{scroll-margin-top:calc(var(--stick,120px) + 12px)}`.
  CSS parses `\n` as an escaped letter `n`, so the browser sees the selectors `n.conds .eyebrow`
  and **`n.sec`** — both match nothing. Confirmed via `document.styleSheets` enumeration.
  `.sec` therefore falls back to the earlier flat `scroll-margin-top:120px`, which is already less
  than the 131 px desktop header and far less than the 193 px mobile one.

**Fix:** (a) replace the two literal `\n` with real newlines; (b) scroll the sub-target with the
real offset rather than relying on `scroll-margin` alone, in `engine.js → show()`:

```js
const hd=document.querySelector('header.site'), f=document.querySelector('.filters');
const off=hd.offsetHeight + (f && getComputedStyle(f).position==='sticky' ? f.offsetHeight : 0) + 12;
const y=el.getBoundingClientRect().top + scrollY - off;
window.scrollTo({top:y});
```

### 3. BLOCKER — "Duness" filter pill on Death Valley

**Where:** `#top10` filter bar, Death Valley, all viewports. Evidence: `rv-ux-dv-top10-390.png` —
pills read `All · Viewpoints · Scenic drives · **Duness** · Areas · Hikes · Canyons`.

**Problem:** `build.py → sec_top10()` pluralises by appending `"s"` to `TYPE_LABEL`, and
`TYPE_LABEL["dunes"] == "Dunes"` is already plural. A visible spelling error in primary navigation
destroys the "research-backed, carefully checked" credibility the rest of the guide works for.

**Fix:** add an explicit plural map next to `TYPE_LABEL` (`"dunes":"Dunes"`, `"area":"Areas"`,
`"scenic-drive":"Scenic drives"`, …) and use it, or guard: `lbl + ("" if lbl.endswith("s") else "s")`.

### 4. MAJOR — White-on-accent fails contrast in dark mode on both guides, and in light mode on Death Valley

**Where:** `.btn.primary` ("Join this trip →"), `.fbtn.on` (active filter pill), `.iconbtn .cnt`
(trip counter badge), `.attr .rank`, `.tile .tile-n`, `.skip`. Evidence:
`rv-ux-dark-z-top10-1200.png`; measured ratios of `#ffffff` on `--accent`:

| theme | accent | ratio | verdict |
|---|---|---|---|
| Zion dark | `#e58a5e` | **2.58:1** | fails 4.5:1 text **and** 3:1 non-text |
| Death Valley dark | `#e0a24a` | **2.23:1** | fails both |
| Death Valley light | `#a8712a` | **4.15:1** | fails 4.5:1 for 13–14 px text |
| Zion light | `#b8532a` | 4.87:1 | passes |

The dark accents were clearly chosen for *surface* legibility (`--accent-ink` on `--accent-soft` is a
healthy 7.2–7.7:1) and then reused as a *button fill*, where they need the opposite polarity.

**Fix:** stop hard-coding `#fff` on accent fills. Add an `--on-accent` token per theme
(`#fff` in light, `#15120f` in dark) and use it in `.btn.primary`, `.fbtn.on`, `.iconbtn .cnt`,
`.attr .rank`, `.tile .tile-n`, `.skip`, and the Leaflet `pin span`. For DV light, darken
`--accent` to ≈`#8f5f1f` (5.6:1) or use `--on-accent:#fff` with a slightly darker fill.

### 5. MAJOR — The shortlist is unshareable, which defeats the page's purpose

**Where:** `.addtrip` / `#tripBox`, both guides. Evidence: `rv-ux-z-mytrip.png`;
`engine.js` persists to `localStorage["tg:zion"]` only.

**Problem:** This page exists so friends can say what they want to do. "Add to my trip" is the
gesture that captures exactly that — and then strands it in one browser profile on one device. The
organiser never sees it; a friend on their phone and the same friend on their laptop have two
different lists; clearing site data loses it silently. The empty state says "Your list is saved in
this browser," but that caveat disappears the moment the list is non-empty.

**Fix (no backend needed):** encode the shortlist in the URL and add a real share action next to
Print/Clear — `#itineraries/picks=angels-landing,emerald-pools,riverside-walk`, parsed on route and
merged into `ST.trip`. Button copy: *"Copy my picks to send to Aaron"*. A `mailto:` fallback with
the list pre-filled would close the loop even better. Keep the "saved in this browser" caveat
visible in the populated state too.

### 6. MAJOR — Three different things are called "trip"

**Where:** masthead `.iconbtn` "My trip" → `#itineraries`; tab "The Trip" → `#trip`; tab
"Itineraries" whose first card is headed "My trip". Evidence: `rv-ux-z-mytrip.png`,
`rv-ux-z-trip-1200.png`.

**Problem:** Clicking "My trip" in the header moves the active tab to **Itineraries** — a label that
shares no word with the control the user pressed (Nielsen #2, match between system and real world;
#4, consistency). Meanwhile "The Trip" means the actual November trip. Users testing this will click
"The Trip" looking for their saved list.

**Fix:** rename the shortlist to **"My picks"** everywhere (`.addtrip` → "+ Add to my picks", header
button → "My picks", card heading → "My picks"), and either rename the tab to **"Itineraries & my
picks"** or promote the picks card to the top of **The Trip** tab, next to "What we might do" where
the tiles that feed it already live.

### 7. MAJOR — Attraction photos are cropped to vertical slivers

**Where:** `.attr .pic img`, `#top10`, ≥720 px. Evidence: `rv-ux-z-top10-1200.png`; measured every
card — Angels Landing renders its **1600 × 1200** source at **300 × 952 (ratio 0.32)**; the ten cards
range 0.32–0.50 against a 1.33 source. Roughly 70–76% of each frame is thrown away, and what survives
is a strip of cliff face with no subject.

**Problem:** `.attr .pic img{height:100%;object-fit:cover}` makes the photo track the card's text
height, and `aspect-ratio:4/3` on the same element is dead code. These are the hero images of the
guide's marquee section.

**Fix:** pin the media box instead of stretching it:

```css
.attr .pic{align-self:start; position:sticky; top:calc(var(--stick,120px) + 60px);}
.attr .pic img{height:auto; aspect-ratio:4/3;}   /* drop height:100% */
```

Sticky is optional but pleasant on tall cards; the required change is `height:auto`.

### 8. MAJOR — `.stats` and `.kv` carry sentences, not stats

**Where:** `.attr .stats .v` and `.stay .kv .v`, both guides. Evidence: `rv-ux-z-top10-1200.png`
(Angels Landing "Distance" = *"1.9 mi each way to Scout Lookout, plus 0.5 mi each way on the chains
(~4.8 mi round trip)"*, wrapping to six lines; "Best time" = a full sentence);
`rv-ux-z-stay-1200.png` ("Good for" = *"Tents and RVs in A/B; non-electric C/D loops cap vehicles at
19 ft"*).

**Problem:** A stat grid is a scanning device — the eye expects `1.9 mi`, `1,187 ft`, `3–4 hr` in a
fixed rhythm. Prose in those slots breaks the rhythm, triples the block's height, and pushes the
summary and the "Add to my trip" CTA below the fold on every card.

**Fix:** split the contract in `tools/schema.md` — `stats.distance` becomes a short value
(`"1.9 mi each way"`, ≤ 20 chars, enforced in `validate.py`) plus an optional `distanceNote`
rendered as `.stat .n` small text under it, matching the `.fact .n` pattern already in Overview.
Move "Best time" out of the grid into its own labelled line.

### 9. MAJOR — Top 10 is 13,937 px tall on a phone with no compact view

**Where:** `#top10`, 390 px. Evidence: measured `#top10.scrollHeight = 13937` at 390 px
(7,877 px at 1200 px); the first card alone is **1,709 px**. Getting from #1 to #10 is ~16 full
screens of thumb-scrolling.

**Problem:** The core task is comparative — *which of these ten do I want?* — and the layout is
optimised for reading one at a time. There is no jump list, no collapse, and the filter bar
(the only comparison tool) is `position:static` below 720 px, so it scrolls away after the first
card and can't be reached again without returning to the top.

**Fix:** (a) add a **Compact / Detailed** toggle beside the filters that collapses each card to
image-thumb + name + tags + Add button (reuse the `.tile` component already built for The Trip tab);
(b) keep the filter bar sticky on mobile by making it a single scrollable row
(`.filters{position:sticky;top:var(--stick);flex-wrap:nowrap;overflow-x:auto}`) instead of the
`position:static` override at ≤720 px.

### 10. MAJOR — "Print / save PDF" inside My trip prints the entire 20-page guide

**Where:** `#tripPrint` in `#tripBox`; `@media print` in `theme.css`. Evidence: print emulation
gives **9 of 9 sections visible** and `scrollHeight = 20,673 px` (≈20 A4 pages);
`rv-ux-z-print-top.png`, `rv-ux-z-print-mid.png`.

**Problem:** The button sits directly under a three-item list, in a card headed "My trip", after the
line "≈ 8 hours of activity". Every affordance says *print these three things*. It prints all ten
attractions, the full FAQ, the photo grid and both campground sections. Classic mismatch between the
control's context and its effect.

**Fix:** add a print mode for the shortlist:

```js
$("#tripPrint").addEventListener("click",()=>{document.body.classList.add("print-picks");
  addEventListener("afterprint",()=>document.body.classList.remove("print-picks"),{once:true});
  print();});
```
```css
@media print{ body.print-picks .sec{display:none!important}
  body.print-picks #itineraries{display:block!important;break-before:auto} }
```
Relabel the untouched full-guide print (on the Join card) as **"Print the whole guide"**.

### 11. MAJOR — The print stylesheet deletes every URL

**Where:** `@media print{a{color:inherit;text-decoration:none}}`. Evidence: print emulation gives
footer links `color: rgb(107,98,89)`, `text-decoration-line: none`; `rv-ux-z-print-top.png` shows
"Open in maps" as flat grey text.

**Problem:** The most likely reason to print this guide is that Zion Canyon and Death Valley have
almost no cell service — the guide itself says so ("Cell service: essentially none"). A printout with
`recreation.gov` booking links, the Angels Landing lottery page, the shuttle schedule and the
campsite map link rendered as untappable grey words is exactly useless at the moment of need.

**Fix:**

```css
@media print{
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:.85em;word-break:break-all;color:#555}
  .credit a::after,nav a::after{content:""}
}
```
Also drop `.tripbar` (it prints a stale "65 days away" countdown next to a removed button) and add a
running `@page` footer with the guide name and trip dates.

### 12. MAJOR — No live-region feedback for any dynamic change

**Where:** `#fcount`, `#fnone`, `#tripCount`, `#tripBox`, `.copylink`, `.sharepage`. Evidence:
`grep -c aria-live` over `engine.js` and `build.py` = **0**; measured
`#fcount.getAttribute('aria-live') === null` after filtering from 10 → 0 results.

**Problem:** A screen-reader or voice-control user filters to "Canyons + Easy", the list silently
empties, "Showing 0 of 10" and the "Nothing matches those filters" card appear off-focus, and
nothing is announced (WCAG 4.1.3 Status Messages). Same for the trip counter incrementing and for
"Link copied" replacing "Share".

**Fix:** `role="status"` on the count and a polite live region for copy feedback:

```html
<span class="count" id="fcount" role="status" aria-live="polite"></span>
<p id="fnone" class="card" role="status" hidden>…
<div id="tripBox" aria-live="polite">
```
For `.copylink` / `.sharepage`, write the confirmation into a visually-hidden `role="status"` node
rather than swapping the button's own label (swapping the accessible name of the focused control is
also a WCAG 2.5.3 hazard).

### 13. MAJOR — The page scrolls behind the open lightbox

**Where:** `#lightbox` (`<dialog>`), both guides. Evidence: opened photo 1 at 390 px with
`scrollY = 40`, sent a wheel event, measured `scrollY = 440`;
`getComputedStyle(document.body).overflow === "visible"`.

**Problem:** Chrome's modal `<dialog>` blocks interaction but not document scroll. A phone user who
swipes to advance photos scrolls the page underneath instead (the swipe handler only fires above a
50 px horizontal delta, so vertical drags pass straight through), and on close they are dumped
hundreds of pixels away from the thumbnail they opened.

**Fix:**

```css
html:has(dialog[open]){overflow:hidden}
```
plus `{passive:false}` + `preventDefault()` on the lightbox `touchmove`, or a
`document.documentElement.style.overflow` toggle in `lbShow()` / the dialog's `close` handler for
older browsers.

### 14. MAJOR — Safety content is written for the wrong season

**Where:** `#safety`, both guides. Evidence: `rv-ux-z-safety-1200.png` — for a **21–25 November**
trip, the three "CRITICAL" cards lead with *"July averages 100°F with 16 days over 100°F"*,
*"Flash floods … peak with the monsoon — July and August average 14 and 15 thunderstorm days"*, and
a falls card citing summer crowding. Death Valley's is heat-first for a **January** trip.

**Problem:** This is the one tab where relevance is a safety property, not a nicety. The risks that
actually apply — sub-freezing nights, ice on the Angels Landing chains (mentioned only in a
`.linkrow` season note on the card), 45–50°F Narrows water and hypothermia, sunset at ~17:15 with
short daylight, winter road closures in DV — are absent or buried. A friend skims this once and
packs wrong.

**Fix:** add `appliesTo: ["winter"]` / `"months": [11,12,1,2]` to each `safety` entry in the schema,
and in `sec_safety()` sort entries whose window covers the trip dates to the top under a
*"For our dates (late November)"* heading, demoting the rest under *"Year-round / other seasons"*.
Same treatment for the season-mismatched `#itineraries` copy ("In summer the lot is often full by 9"
on a November trip).

### 15. MAJOR — The mobile header eats 23% of the viewport and hides half the navigation

**Where:** `header.site`, 390 px, both guides. Evidence: measured `header.offsetHeight = 193`
(131 at 1200 px) on a 844 px viewport — **22.9%**, permanently, because it is sticky; and
`nav.tabs.scrollWidth = 823` vs `clientWidth = 390`, i.e. **53% of the tab bar is off-screen** with
`scrollbar-width:none` and no fade or arrow. `rv-ux-z-top10-390.png` shows "The Trip" clipped to
"e Trip" on the left and "Photos & M…" cut on the right, with nothing to suggest either direction
scrolls.

**Fix:**
- Collapse the masthead on scroll: keep `h1` + tabs, hide `.crumbs` and `.sub` past ~80 px of scroll
  (an `IntersectionObserver` sentinel and a `body.scrolled` class); that recovers ~55 px.
- Move the three `.tools` buttons onto the tab row at ≤720 px instead of their own 40 px line.
- Add scroll affordance to the tab strip:
  `nav.tabs{mask-image:linear-gradient(90deg,#000 0,#000 calc(100% - 28px),transparent)}` plus
  `scroll-snap-type:x proximity` on the strip and `scroll-snap-align:center` on the links.

### 16. MAJOR — The unit toggle converts only half the page

**Where:** `#unitBtn`, `[data-units]`, both guides. Evidence: switched to metric on `#top10`; stats
converted correctly (`1.9 mi → 3.1 km`, `1,187 ft → 362 m`) but a scan of the same section still
finds imperial prose. In `guides/zion/index.html`: **"1,000 feet"**, **"60 feet of rope"**,
**"three feet"** ×2, **"a mile up the road"** — all outside `[data-units]` or spelled out in words.

**Problem:** A metric reader gets *"drop-offs of up to 1,000 feet"* two lines under *"3.1 km each
way"*. Half-converted is worse than not converted: the reader can no longer trust which system any
given number is in.

**Fix:** two parts. (a) Widen the regex to cover `feet|foot|miles|mile|inches` word forms, not just
the `mi|ft|°F` abbreviations. (b) Add a lint to `validate.py` that fails on an imperial unit
appearing in any `html:` field that the renderer does not wrap in `units()`; the CLAUDE.md rule
"miles/feet/°F in data (the client converts to metric)" is only enforceable if every such string
passes through the converter.

### 17. MAJOR — The unit button's visible label and accessible name say opposite things

**Where:** `#unitBtn`, both guides, all viewports. Evidence: in imperial mode the button reads
**"mi / °F"** with `aria-label="Switch to kilometers and Celsius"`; in metric it reads **"km / °C"**
with `aria-label="Switch to miles and Fahrenheit"`.

**Problem:** Two failures at once. The visible text is not contained in the accessible name, so
voice-control users saying *"click mi slash F"* get nothing (WCAG 2.5.3 Label in Name). And sighted
users cannot tell whether "mi / °F" is a state or an action — it is the classic toggle ambiguity.
(`#themeBtn` does this correctly: "☾ Dark" / aria-label "Switch to dark theme".)

**Fix:** make it a state control with an explicit label, not a mystery toggle:
`<button aria-pressed="false"><span class="visually-hidden">Units:</span> mi / °F</button>`, or
adopt the theme button's pattern — visible "→ km / °C", `aria-label="Switch to kilometers and
Celsius"`.

### 18. MAJOR — The photo lede promises something the photos don't deliver (Zion)

**Where:** `#photos` lede, Zion: *"8 photos from **Summer 2012** — a taste of **what the trip
actually looks like**."* Evidence: `rv-ux-z-photos-1200.png` — shorts, tank tops, bare legs in the
Narrows, a group on Angels Landing in full summer sun.

**Problem:** The trip is 21–25 November. Water temperature, daylight, crowd levels and required gear
are all different; a friend deciding whether to come, and what to pack, is being shown the wrong
season and told it is representative. (Death Valley's *"January 2025"* album genuinely matches its
January 2027 trip — so the copy is only wrong for Zion, which makes it worse: it is a generic string
applied without checking.)

**Fix:** derive the line from the album date vs. the trip date in `sec_photos()`. When the seasons
differ: *"8 photos from a summer trip in 2012 — the place, not the season. Late November is colder,
quieter, and the Narrows needs a drysuit."* When they match, keep the current wording.

### 19. MAJOR — Trip facts cards leave 400–470 px of dead space

**Where:** `.grid3.tripfacts` on `#trip`, ≥900 px, both guides. Evidence: `rv-ux-z-trip-1200.png`
("When" card ~370 px tall for three lines of content); `rv-ux-dv-trip-1200.png` is worse — the
"Home base" card runs to ~560 px and drags "When" and "Status" to match, leaving ~470 px blank in
each. The same pattern repeats in `#safety` (`rv-ux-z-safety-1200.png`, third card).

**Problem:** CSS grid stretches rows to the tallest item. Three cards with a 10:1 content ratio
should not be peers in a 3-up grid at all — the emptiness reads as "something failed to load."

**Fix:** `.grid3{align-items:start}` stops the stretch immediately. Better: give the base its own
full-width card (it is the single most load-bearing block on the page — where everyone sleeps) and
put the short "When" and "Status" facts in a two-up row above it. Consider trimming the base detail
to three sentences with the rest behind a "More about the site" `<details>`.

### 20. MAJOR — Bold is used so heavily it has stopped meaning anything

**Where:** `.stay .card`, trip "Home base" and "Getting in" cards, `#safety`, both guides.
Evidence: `rv-ux-z-stay-1200.png` — the Watchman "How to book" paragraph has **six** bold runs in
seven lines (*"100% reservation — no first-come, first-served sites"*, *"six months in advance"*,
*"A and B electric"*, *"C and D non-electric"*, *"E tent-only group sites"*, *"F walk-to,
tent-only"*). `rv-ux-dv-trip-1200.png` — five bold runs in the Home base paragraph.

**Problem:** Emphasis is a contrast device; at this density there is no contrast left and the eye
gets no landing point. Worse, bold is doing three different jobs at once — the actionable rule, the
numeric fact, and a list label that should be a list.

**Fix:** cap it at one bold run per paragraph (the actionable rule), turn the A–F loop breakdown
into a small `<table>` or `.kv` grid, and let the existing `.callout`/`.tag` components carry the
"how it's booked" signal — `<span class="tag reservable">` is already rendered directly above and
says the same thing.

### 21. MINOR — No `prefers-reduced-motion` support anywhere

**Where:** `html{scroll-behavior:smooth}`, `@keyframes flash`, `.tile:hover img{transform:scale(1.04)}`,
`.ph:hover img{transform:scale(1.03)}`. Evidence: `grep -c prefers-reduced-motion shared/theme.css`
= **0**; under Playwright `reducedMotion:'reduce'`, `scroll-behavior` still computes to `smooth`.

**Problem:** Every tab switch animates a full-page scroll-to-top, and deep links animate a scroll
plus a 1.6 s pulsing box-shadow. For vestibular-sensitive users this is the difference between a
usable page and a nauseating one (WCAG 2.3.3).

**Fix:**

```css
@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;
    transition-duration:.01ms!important}
}
```
and use `{behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'}`
in the JS `scrollTo` / `scrollIntoView` calls.

### 22. MINOR — The map has no legend, and pins collide

**Where:** `#map`, `#photos → Map`. Evidence: `rv-ux-z-map-1200.png` — 13 markers in three colour
schemes (orange numbered = Top 10, green 📷 = photos, blue ⌂ = home base) with nothing explaining
them; pins 1 and 3 each have a green photo pin tucked behind them, and pins 2 and 9 are not visible
at the default fit-bounds zoom.

**Problem:** Colour-as-sole-meaning with no key (WCAG 1.4.1 adjacent), plus occlusion that hides
content. The `+0.0025°` offset for approximated photo pins is too small to separate them at this
zoom.

**Fix:** render a legend row above the map from the same data that builds the pins —
`<ul class="chips"><li><span class="pin-key accent">1</span> Top 10, by rank</li>
<li><span class="pin-key good">📷</span> our photos</li>
<li><span class="pin-key info">⌂</span> home base</li></ul>`. Add `L.markerClusterGroup` or bump the
photo offset to ~0.006° and set `zIndexOffset` so photo pins sit above attraction pins.
Also add the standard "use two fingers to move the map" hint, since `scrollWheelZoom:false` means a
scroll gesture over the map currently does nothing with no explanation.

### 23. MINOR — A bad hash silently shows the wrong tab and keeps the bad URL

**Where:** `engine.js → route()`. Evidence: loading `…/zion/index.html#bogus` renders **The Trip**
while `location.hash` stays `#bogus` and `document.title` becomes "The Trip · Zion National Park".
Same for an unknown sub-target: `#top10/not-a-real-id` shows Top 10 with no scroll and no message.

**Problem:** A typo'd or truncated shared link (very likely — these get pasted into group chats that
mangle trailing characters) lands people on the wrong content with a URL that keeps reproducing the
error on refresh, and no indication anything went wrong.

**Fix:** in `route()`, when the id doesn't match a section, `history.replaceState(null,"","#"+secs[0].id)`
so the URL self-corrects. When `sub` is present but `getElementById(sub)` is null, show a dismissible
`role="status"` note at the top of the section: *"We couldn't find that spot — here's the full list."*

### 24. MINOR — The shortlist card's copy, formatting and computed total are all slightly off

**Where:** `#tripBox`, `renderTrip()` in `engine.js`. Evidence: `rv-ux-z-mytrip.png` with three
items saved.

Four separate problems in one card:
- **Case inconsistency:** rows read *"Hike · strenuous · …"* — `d.typeLabel` is title-cased,
  `d.difficulty` is the raw lowercase key. Use `DIFF_LABEL` here too (emit `data-difficulty-label`).
- **Prose in a list row:** *"3–4 hr to Scout Lookout; 1–2 hr more for the chains"* makes the row
  wrap; same root cause as #8.
- **The total is wrong and unqualified:** *"≈ 8 hours of activity"*. `parseHours()` takes only the
  first match in the string, so Angels Landing counts as 4 hr and the *"1–2 hr more for the chains"*
  is dropped. It also ignores drive and shuttle time entirely and isn't divided across the 4 nights,
  so it answers no question a user has. This also sits awkwardly against the repo's "no invented
  numbers" rule. Either sum all matches and label it *"≈ 8–11 hr on trail, excluding driving and
  shuttle time"*, or replace it with *"3 of 10 picked · 1 needs a permit"*.
- **Destructive action styled as benign:** "Print / save PDF" and "Clear" are both `.btn.ghost`
  (transparent border, muted text) inside a `.86rem` muted paragraph, separated by a single space.
  Give "Clear" `color:var(--bad)` and separate it with a `·`, or move it to the card's top-right.

### 25. MINOR — Focus order jumps backwards inside every attraction card, and plain links get no themed focus ring

**Where:** `.attr`, `#top10`. Evidence: instrumented Tab walk —
`… → A "NPS / Caitlin Ceci · PD" (y=1406) → SUMMARY "Tips from the research" (y=1224) →
BUTTON "+ Add to my trip" (y=1372) → …`. Focus moves down 1406, back up to 1224, then down again,
once per card (WCAG 2.4.3). Separately, the themed focus rule is
`nav.tabs a:focus-visible, button:…, select:…, input:…, summary:focus-visible` — **bare `a` is not
in the list**, so the ~200 content, source, credit and footer links fall back to the UA default
ring, including the white-on-translucent-black credit chip sitting on a photo.

**Fix:** add `a:focus-visible` to the themed rule (and `.ph:focus-visible`, which currently only gets
a caption reveal). For the order, move the photo credit out of `.pic` into the card's `.foot` next to
"Sources", where it reads better anyway — it is attribution, not a caption, and it also removes ten
12 px-tall tab stops from the middle of the section.

### 26. MINOR — Photo captions are invisible until hover

**Where:** `.ph .cap{opacity:0}` → `.ph:hover .cap, .ph:focus-visible .cap{opacity:1}`, `#photos`
grid. Evidence: `rv-ux-z-photos-1200.png` — eight thumbnails of people with no text at all.

**Problem:** The captions are the good part (*"The whole crew on top of Angels Landing, 1,500 feet
above the canyon floor"*), and on desktop nobody sees them without a deliberate hover on each tile.
The grid reads as an anonymous photo dump rather than a story about the last trip. The
`@media (hover:none)` rule already shows them permanently on touch — so the *worse* experience is on
the larger screen.

**Fix:** show a one-line clamped caption always (`opacity:1; -webkit-line-clamp:1`), expanding to two
lines on hover/focus. Also render `taken` dates in the grid, not just the lightbox.

### 27. MINOR — The landing page is a different product from the guides

**Where:** `index.html`. Evidence: measured `{skip:false, footer:false, unit:false, nav:false}` —
no skip link, no footer, no "last verified", no units control (the guides have all four);
`rv-ux-landing-1200.png`.

Three issues:
- **Wrong order.** Cards are emitted in `sorted(os.listdir(GUIDES))`, so Death Valley (Jan 2027)
  sits left of Zion (Nov 2026). For a page whose subject is two upcoming trips, chronological is the
  only defensible order. Sort `allg` by `trip.start`, trips first, in `render_landing()`.
- **Buried lede.** The one thing a friend opening this link needs — *which trip, when, am I invited*
  — is rendered in `.credit`: 0.72 rem mono, muted. Promote the date to ~1 rem non-mono text above
  the tagline; demote the tagline.
- **False affordance.** The `JOIN THIS TRIP` chip is a non-interactive `<span class="joinchip">`
  styled exactly like a filled button, inside a card-wide link. It looks like a second, separate
  action. Make it a plain `.tag`, or make the whole card's CTA explicit
  (`<span class="btn primary">Open the trip →</span>`).

Also: the theme choice *does* correctly persist from a guide to the landing page (verified), which is
good — keep that.

### 28. MINOR — Filters permit dead ends and the empty state doesn't say what's wrong

**Where:** `#filters`, `#fnone`. Evidence: `rv-ux-z-empty.png` — "Canyons" + "Easy" yields
*"Showing 0 of 10"* and *"Nothing matches those filters."*

**Problem:** The difficulty `<select>` always offers every difficulty present in the whole guide,
regardless of the active type, so users can construct impossible combinations and get punished for
it. The recovery offered is all-or-nothing ("Reset filters"), and the message never names the
culprits.

**Fix:** after each `applyFilters()`, disable `<option>`s with no matches under the current type
(the standard faceted-search behaviour), and make the empty state specific and partially
recoverable: *"No **Canyons** are rated **Easy**. [Clear difficulty] [Clear type]"*.
Additionally, "Reset" in the filter bar should be `disabled` when no filter is active — it currently
reads as an always-live control with nothing to do.

### 29. MINOR — Card borders are effectively invisible

**Where:** `--line` against `--bg` / `--surface`, every card, both themes. Measured:
light `#e2d9cc` on `#faf7f2` = **1.31:1**, on `#ffffff` = **1.40:1**; dark `#3a332c` on `#15120f` =
**1.50:1**, on `#1e1a16` = **1.39:1**. The accompanying `--shadow` is `rgba(…,.06)` in light — also
near-invisible.

**Problem:** The card is the primary grouping device on a page made almost entirely of cards, and its
boundary is below the 3:1 non-text threshold in all four theme combinations. On the `#safety` and
`#stay` tabs the cards visually merge into the background and the grouping has to be inferred from
whitespace alone. It also makes the `.stats`/`.kv` sub-panels (`--surface2`) the only visible
structure, which inverts the intended hierarchy.

**Fix:** darken `--line` to ≈`#d3c6b3` (2.1:1) / lighten the dark one to ≈`#4a4239`, and strengthen
the light shadow to `0 1px 2px rgba(34,29,23,.10), 0 8px 24px rgba(34,29,23,.08)`.

### 30. MINOR — A runtime image failure has no fallback

**Where:** `.attr .pic img`, `.gcard img`. Evidence: simulated a missing file at 390 px
(`rv-ux-z-longtitle-390.png`) — the browser's broken-image glyph and the alt text render *underneath*
the absolutely-positioned rank badge, and `.pic` collapses to a ~40 px strip.

**Problem:** `build.py → img()` checks `os.path.exists` at build time only, and the landing page
doesn't check at all (`<img src="guides/{slug}/img/{hero}">` is emitted unconditionally). A renamed
file, a failed `fetch_images.py`, or a partially-synced deploy produces this.

**Fix:** `onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'noimg'}))"`
on generated `<img>` tags — the `.noimg` diagonal-hatch placeholder already exists and looks
deliberate. Add the same `os.path.exists` guard to `render_landing()`.

### 31. POLISH — The trip banner wraps with orphaned separators

**Where:** `.tripbar`, 390 px, both guides. Evidence: `rv-ux-z-trip-390.png`, `rv-ux-dv-top10-390.png`
— lines end on a dangling `·` (*"Sat Nov 21 – Wed 25, 2026 ·"*, *"4 nights, base: Springdale, UT ·"*)
and Death Valley's countdown line *starts* with one (*"· 120 days away"*).

**Fix:** drop the `.tb-sep` spans and use a border/gap-based separator that disappears at the wrap
point: `.tripbar > span + span{border-left:1px solid var(--line);padding-left:10px}` with
`@media (max-width:720px){.tripbar > span + span{border-left:0;padding-left:0}}`. While there, give
the countdown more weight than 0.78 rem mono muted — it is the emotional hook of the whole banner,
and it currently reads as a build timestamp.

### 32. POLISH — Repeated vague link text, undersized link targets, mixed quote glyphs

**Where:** across both guides.
- *"details"* appears three times in Zion's "Also consider" list as the entire link text
  (`rv-ux-z-empty.png`), and *"source"* / *"nps.gov"* repeat in the alerts and card footers
  (WCAG 2.4.4). Give them context: `details <span class="visually-hidden">about Kolob Canyons</span>`.
- Measured link boxes well under the 24 × 24 CSS px target minimum (WCAG 2.5.8): photo credits at
  **148 × 12**, card sources at **54 × 16**, "details" at **53 × 19**, and the masthead crumb
  "Travel guides" at **99 × 13**. The inline-in-text exception covers some, but the standalone
  credit chip, the card-footer source links and the breadcrumb are not inline. Add
  `padding:6px 0` / `min-height:24px` to `.credit a`, `.attr .foot .src a` and `.crumbs a`.
- Straight and curly quotes are mixed: `"full almost every night mid-March through late November."`
  and `Zion's other lottery` sit beside the curly `’` used everywhere else. Normalise in the source
  data and add a `validate.py` check for `"` and `'` inside `html:` fields.
- Death Valley's base renders as bare *"Echo Canyon Road, site E1"* in the banner and on the landing
  card, where Zion's reads as a town (*"Springdale, UT"*). Nothing signals that one group is camping
  and the other is in motels — which changes what a friend needs to bring and book. Add a
  `base.kind` (`"town" | "campsite" | "lodge"`) and render *"camping at Echo Canyon Rd, site E1"*.

---

## What I'd fix first

`#1` and `#2` are one afternoon of CSS and both are correctness bugs with verified one-line fixes;
`#3` is a five-minute typo fix on a visible navigation label. `#4` (the `--on-accent` token) and
`#12` (live regions) are the cheapest real accessibility wins. `#5` — making the shortlist
shareable — is the one change that turns this from a nicely-built reference document into the
group-planning tool it is clearly trying to be.
