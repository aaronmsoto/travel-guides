# Adversarial product critique — "travel guides that double as trip invitations"

Reviewer persona: product lead, consumer travel. Reviewed 2026-09-17 against the built pages
(`guides/zion/index.html`, `guides/death-valley/index.html`, root `index.html`), `guide.json`
sources, `tools/schema.md`, `tools/*.py`, `shared/*`, and the research notes in
`guides/*/src/_research/`. Screenshots taken at 1280 px and 390 px on every tab, plus print media
and a real Leaflet map render.

---

## Verdict

**What is genuinely good.** The content is the best thing here, and it is not close. The Top 10
cards, the camping cards and the Safety tab are better than anything AllTrails, Wanderlog or a
Notion template will give you, because they carry the *mechanics*: "$6 per application (up to six
people) plus $3 per person if awarded, 12:01 a.m. to 3 p.m. MT, results 4 p.m. MT, start time is
measured at The Grotto." Furnace Creek's split reservable/first-come season, the $30-site-plus-$14-
utility-fee detail, "230 sites and almost no vegetation, rarely fills" — these are the facts that
decide a trip, and every one of them traces to an NPS or recreation.gov page fetched on a dated
research note. I spot-checked the Angels Landing lottery calendar, the Echo Canyon E1 capacity
(12 people, 3 vehicles, 70-ft pull-through, $10/night, 6-month window) and the Titus Canyon
2026–27 closure against `src/_research/`; all three were accurate and correctly qualified. The
pipeline is real: `validate.py` passes clean, `build.py` is deterministic (I rebuilt and diffed —
byte-identical), the pages are self-contained, the print stylesheet exists, the unit toggle works,
the map renders, the whole thing is ~700 lines of Python with no framework. The Trip tab is a
genuinely good idea, well executed: dates, base, getting in/out, "what these dates mean" as six
concrete condition blocks, a bring list written for *these* dates, and open questions that invite
disagreement. That last touch — "plans below are a working draft, say what you'd change" — is the
right instinct and no competitor does it.

**What would stop me shipping.** The product is a guide that mentions a trip, not an invitation.
The entire job-to-be-done is "get friends to say yes," and the response loop does not exist: there
is no mailto, no form, no phone number, no RSVP, no headcount, no way for a recipient to do
anything except read. Join step 1 is literally "Tell Aaron you are in" with no mechanism, and step
4 asks people to share their "Add to my trip" shortlist — which is localStorage-only and cannot be
exported or shared. Worse, the link itself is broken as a shared object: `og:image` is the
relative string `img/hero.jpg`, so pasting this into iMessage, Slack, WhatsApp or anywhere else
shows no image at all; the `og:title` is "Zion National Park travel guide" (not "Zion, Nov 21–25 —
come with us"); the description is the geology paragraph truncated mid-word at "happens ins"; and
there is no `og:url`, no `twitter:card`, no deploy step anywhere in the README, so the "Copy link
to this trip" button currently emits a `file:///home/user/...` path. Then the content, for all its
quality, is date-blind in ways a friend will notice: the Zion pitch's first sentence says "Four
nights in Springdale" when the plan sleeps night one in Las Vegas (three Springdale nights — a
joiner who books four books a wrong night); the Safety tab leads with a **critical** "Heat" card
for a late-November trip and, on Death Valley, with the summer "10 am rule" for a January camping
trip whose real risk is a 38°F night with no shelter; the itineraries are generic one-day/two-day
plans with no relation to the four days on offer; and nobody is told what any of this costs. A
Google Doc plus a group chat loses on content and wins on every one of those: it has a reply
button, a thread, a headcount, and someone types "rooms are ~$280/night, I booked the 22nd–24th."

---

## Scorecard

| Dimension | Score | Why |
|---|---|---|
| Job-to-be-done fit | **3 / 5** | Superb at "give them what they need to plan"; near-zero at "get them to say yes" — no reply path, no cost, no day shape, no headcount. |
| Content trust | **4 / 5** | Research quality and sourcing are excellent and auditable; docked for date-blind safety/itineraries, a wrong night count in the pitch, and no staleness signal after `lastVerified` ages. |
| Showing-off factor | **3 / 5** | Top 10 cards and Zion's hero genuinely sell it; Death Valley's hero is hazy and flat, the personal photos sell the people not the place, and the place people will sleep has no photo at all. |
| Share / response loop | **1 / 5** | Broken social preview, no hosted URL, no RSVP, no calendar file, no way to send back a shortlist, no group coordination. This is the product's stated purpose. |
| Pipeline quality | **3 / 5** | Deterministic, contract-driven, validator passes, third destination would be tractable; but the validator ignores `trip` entirely (which is how the "four nights" error shipped), there is no CI, no deploy, and ~5 MB of fetched-but-never-rendered images. |

---

## Findings

### BLOCKER — fix before sharing these two guides

**1. BLOCKER — The shared link has no social preview.**
*Where:* `tools/build.py` `render_guide()` head block; both built pages.
*Why it matters:* `<meta property="og:image" content="img/hero.jpg">` is a relative URL. Open
Graph requires an absolute one. Every place this link will actually be pasted — iMessage, Slack,
WhatsApp, Discord, Signal — will render a bare grey link card with no photo. For a product whose
whole thesis is "show off the destination so people join," the single highest-leverage image on
the internet is the one in the preview card, and it is currently absent. There is also no
`og:url`, no `og:type`, no `og:image:width/height`, no `twitter:card` (so X/Twitter falls back to
nothing), and the root landing page has no OG tags at all.
*Fix:* Add a `site.baseUrl` to a top-level config; emit absolute `og:image`, `og:url`,
`og:type=website`, `og:site_name`, `og:image:width/height` and `twitter:card=summary_large_image`.
Generate a dedicated 1200×630 share card per guide (hero crop + "Zion · Nov 21–25, 2026 · come
with us") rather than reusing the raw hero.

**2. BLOCKER — Preview title and description sell a guide, not an invitation, and truncate mid-word.**
*Where:* `build.py`: `title` = `f'{name} travel guide'`; `desc` = `overview.summary[:155]`.
*Why it matters:* The preview reads "Zion National Park travel guide — Zion is a narrow,
2,000-foot-deep gash of Navajo sandstone with a river running through the bottom, and almost
everything famous about the park happens ins". Death Valley's ends "...and the lowe". A recipient
scanning a group chat cannot tell this is *their friend inviting them somewhere on specific
dates*. Mid-word truncation also reads as unfinished work, which undercuts the trust the content
has earned.
*Fix:* When `trip` exists, set `og:title` to `"{trip.title} — you're invited"` and `og:description`
to the trip pitch, truncated on a word boundary with an ellipsis. Keep the guide-flavoured title
only for guides without a trip.

**3. BLOCKER — There is no way to respond, and no way to reach the host.**
*Where:* `trip.join.steps` in both `guide.json`; `sec_trip()` renders only "Copy link" and "Print".
`grep mailto:` across all three built pages returns zero.
*Why it matters:* The product's one conversion event is "say yes." Step 1 of the Join card is
"Tell Aaron you are in, and which nights" — through what? There is no email, no phone, no chat
link, no form. Step 4 asks joiners to share their Top-10 shortlist; the shortlist lives in
`localStorage` and has no export. A recipient who is sold has to leave the page, find the chat
they got it from, and retype everything the page already knows. Every competitor — even a Google
Doc — beats this.
*Fix (minimum viable, ~30 lines):* Add `trip.contact: {name, mailto, sms?, chatUrl?}` to the
schema. Render a primary "I'm in →" button that opens a prefilled `mailto:` / `sms:` with subject
"Zion Nov 21–25 — count me in", body pre-seeded with nights, headcount, vehicle, and the user's
saved shortlist names pulled from `localStorage`. That single button turns a static page into an
invitation and costs nothing to host.

**4. BLOCKER — Zion's pitch states the wrong number of nights in Springdale.**
*Where:* `guides/zion/guide.json` → `trip.pitch`: "Four nights in Springdale…" vs `trip.arrival`:
"Sat Nov 21: travel day… sleep in or near [Las Vegas]. Sun Nov 22: drive Las Vegas → Springdale."
Nov 21–25 is four nights total but only **three** in Springdale (22nd, 23rd, 24th). The tripbar and
landing card both repeat "4 nights, base: Springdale, UT".
*Why it matters:* This is the first sentence of the pitch and the most consequential number on the
page. Springdale is expensive and fills for the holiday week; a friend who books Nov 21–25 buys a
night they will not use and may not be able to cancel. The error is invisible to `validate.py`
because the validator does not look at `trip` at all (finding 18).
*Fix:* Correct to "Three nights in Springdale (plus a night in Las Vegas on the way in)"; render
the banner as "4 nights · 3 in Springdale"; add a validator rule that cross-checks any night count
in `pitch` against `end − start` and against `arrival`.

**5. BLOCKER — Nothing says what this costs.**
*Where:* Both `trip` blocks. Zion's only dollar figures are the $6/$3 lottery fee and the $35
entrance pass. There is no lodging price band, no camp fee split, no gas estimate, no food.
*Why it matters:* "How much is this going to cost me" is the first question anyone asks about a
trip, and for Zion over Thanksgiving week — where Springdale rooms routinely clear $250–400/night —
it is the whole decision. The guide's own Stay tab already carries the `priceBand` data
(`$$–$$$$`) and the Death Valley trip already knows the site is $10/night split 12 ways. Asking
someone to "book your own room in Springdale" with no number is asking them to do the scary part
alone.
*Fix:* Add `trip.cost: [{label, perPerson, note}]` and render a "Rough cost per person" card in
the trip facts row (replacing the near-empty Status card, finding 22): lodging band × nights,
share of the site fee, entrance pass, and a "does not include" line. Estimates with a stated basis
are far better than silence.

### MAJOR

**6. MAJOR — Safety is not date-aware, and leads with the wrong risk on both guides.**
*Where:* `guides/zion/guide.json` → `safety[0] = {critical, "Heat"}`, `safety[6] = {note, "Winter
ice"}`. `guides/death-valley/guide.json` → `safety[0] = {critical, "Extreme heat — the 10 am
rule"}`, `safety[7] = {note, "Winter at elevation"}`.
*Why it matters:* The Zion trip is Nov 21–25, when about ten nights a month drop below freezing and
shaded slickrock ices — the guide's own trip tab says so. The Death Valley trip is a January
camping trip at sea level with no shelter, where the trip tab warns "upper 30s at night, possibly
colder." Both Safety tabs open with a full-width **critical** card about summer heat and bury the
actually-relevant cold-weather card as a **note** at the bottom of the page. A reader who takes
the page at its word packs for the wrong trip. It also quietly tells an attentive reader that this
section was written for a generic visitor, not for them — which taxes the trust the rest of the
content earned.
*Fix:* Add `months: "Jun–Sep"` (or `seasons: ["summer"]`) to each safety entry. When `trip` exists,
sort trip-relevant entries first, promote the matching one to the top, and collapse the rest under
a "Risks in other seasons" disclosure. Same treatment for `seasons` verdicts.

**7. MAJOR — The itineraries have nothing to do with the trip.**
*Where:* `#itineraries` on both guides: "One perfect day" and "Two days", written for a generic
visitor. Zion's says "in summer the lot is often full by 9" and budgets "four to six hours
upstream" in The Narrows — for a trip where the water is in the low 40s °F.
*Why it matters:* The schema explicitly forbids a day-by-day schedule on the trip tab, and the
Itineraries tab does not fill the gap. So the page never answers the question that decides
attendance for anyone who can't come for the whole stretch: *which day is the big hike?* The Join
card says "join for the whole stretch or drive in for a day or two" — with no way to know which day
to pick. This is exactly what a group chat solves in two messages and the page does not solve at
all.
*Fix:* Add `trip.shape: [{date, label, note}]` — a loose, explicitly-provisional day shape ("Mon
23: big hike day (Angels Landing if the lottery lands) · Tue 24: Narrows or east side · Wed 25:
short morning, drive out by noon"). Render it under "What we might do" with a "this is a draft,
push back" framing. Keep the generic itineraries where they are, but re-tag them as "if you have
only a day."

**8. MAJOR — Booking deadlines are not computed against the trip dates, and at least one is already
misleading.**
*Where:* Death Valley Stay tab, Furnace Creek: "set a reminder for the day your date opens six
months out." Zion trip conditions: the Angels Landing day-before lottery mechanics.
*Why it matters:* For the Jan 15–18, 2027 trip, the six-month Furnace Creek window **opened around
July 15, 2026** — two months before this page was written. A joiner reading today is told to set a
future reminder for a window that is already open and filling. Conversely, the Zion day-before
lottery has a single actionable date (apply Nov 20, 2026, 12:01 a.m.–3 p.m. MT) that the page
never states. Turning static mechanics into dated actions is precisely the thing a trip-aware
guide can do that a general guide cannot — it is the differentiated core, and it is unbuilt.
*Fix:* Derive dates at build time from the trip. Render a "Dates that matter for this trip"
strip: "Furnace Creek reservations for our nights opened Jul 15, 2026 — book now", "Angels Landing
day-before lottery: apply Fri Nov 20, 12:01 a.m.–3 p.m. MT", "Springdale rooms: book by ~Oct".
This is 20 lines of Python and is the most convincing thing on the page.

**9. MAJOR — The "Add to my trip" shortlist is a dead end.**
*Where:* `shared/engine.js` — `ST.trip` in `localStorage`; `#tripBox` renders a list with Print and
Clear only.
*Why it matters:* The join flow's step 4 is "tap Add to my trip on what you'd want to do, and tell
us — that is how we'll plan cars and shuttle times." There is no mechanism to tell you. The
shortlist cannot be exported, linked, or sent. It is a solitaire feature in a product about group
coordination, and it makes a promise in the copy that the code does not keep.
*Fix:* Two cheap options, ship both. (a) "Copy my picks" → plain text list to paste into chat.
(b) Encode ids in the URL (`#itineraries/picks=angels-landing,the-narrows`) so the host gets a
link that shows exactly what that person wants. Wire the same list into the `mailto:` from
finding 3.

**10. MAJOR — No calendar file.**
*Where:* Nowhere. `grep -i ics` finds only the word "physics"-adjacent noise.
*Why it matters:* "Save the date" is the cheapest conversion step in event software and this
product has hard dates, a location with coordinates, and a host. A recipient who is interested but
not ready to commit has no way to park it. TripIt's entire original value proposition was getting
a trip into a calendar.
*Fix:* Emit a static `trip.ics` next to each guide (VEVENT, all-day, `DTSTART`/`DTEND`, `LOCATION`
= base name, `URL` = the guide, `DESCRIPTION` = pitch) and put "Add to calendar" beside "Copy
link" in the Join card and in the sticky trip bar.

**11. MAJOR — The binding group constraint is invisible, and there's no headcount.**
*Where:* Death Valley `trip.base.bookingNote`: "holds 12 people and 3 vehicles."
*Why it matters:* For the Death Valley trip, "3 vehicles" is the constraint that determines whether
someone can come at all, and it is a clause in the middle of a paragraph in a blue callout. There
is no "4 of 12 spots claimed, 2 of 3 vehicles" state, and no list of who is already in. Social
proof is the strongest lever an invitation has — "Dan and Priya are in" converts better than any
photograph — and the page has none. It also means the host cannot use the page to manage the one
number they have to manage.
*Fix:* Add `trip.capacity: {people, vehicles}` and `trip.roster: [{name, nights, vehicle}]`. Render
a capacity meter in the trip facts row and a "Who's in" list. The roster can stay a hand-edited
JSON array — it is still a rebuild-and-repost, but it converts.

**12. MAJOR — The personal photos undercut the goal and raise a consent problem.**
*Where:* `guides/zion/photos/` (8 photos, album "Summer 2012"), `guides/death-valley/photos/`
(10 photos, album "January 2025").
*Why it matters:* Two problems. (a) *Relevance and showing-off:* these are family snapshots, not
destination photos. Death Valley's set is dominated by close-ups of children — checkers on a
porch, a kid in a hoodie, "The kids own the dunes" — and Zion's set is fourteen years old, shot in
summer, for a November trip, and includes a rattlesnake close-up as the second image. The tab lede
promises "a taste of what the trip actually looks like." A stranger-ish friend scrolling this sees
someone else's family album, not a reason to come. (b) *Consent:* this page is designed to be
forwarded, and it publishes identifiable faces of minors at a stable URL with no access control.
That is a decision the people in the photos (or their parents) should make, not a build step.
*Fix:* Curate hard — six to eight photos where the *place* is the subject, people small or absent;
put the group shots in one clearly-labelled "our crew last time" row at the end. Add
`"private": true` to `photos.json` items so a face-heavy photo can be kept in the repo but excluded
from the build, and make it the default for anything with a recognisable child. Get explicit
sign-off before the link goes anywhere.

**13. MAJOR — Every deep link lands with the card hidden behind the sticky header.**
*Where:* `shared/theme.css` — `.conds .card{…}\n.conds .eyebrow{…}\n.sec{scroll-margin-top:calc(var(--stick,120px) + 12px)}`.
That is a **literal backslash-n inside the CSS file**, so the parser reads an escaped identifier
and silently kills both following rules. Verified in the browser: `.conds .eyebrow` computes to
`rgb(107,98,89)` (muted) instead of the accent, and `#top10/observation-point-east-mesa` scrolls
the card's top to viewport y = 0.125 px under a 131 px header.
*Why it matters:* Deep-linking is the product's main internal navigation. Every "Share" button on
every attraction card, every one of the ten tiles on the Trip tab, and every "see the card" link in
the photo lightbox lands mid-card with the title, rank badge and difficulty tags hidden. The
`.flash` highlight that is supposed to say "here it is" is off-screen too. The most likely link
anyone shares — "look at #2" — lands badly.
*Fix:* Replace the literal `\n` with real newlines, and add `scroll-margin-top: calc(var(--stick,
131px) + 16px)` to `.attr` as well as `.sec`. Then add a build-time smoke test that deep-links
each attraction id and asserts the card top is below the header.

**14. MAJOR — Top 10 ships full-resolution images; Zion's tab is 6 MB.**
*Where:* `build.py` `attraction()` calls `img(..., thumb=False)`; measured 6.08 MB / 12 requests to
scroll Zion's `#top10`, 3.74 MB for Death Valley. Thumbnails already exist for every image.
*Why it matters:* This link will be opened on a phone, often on the drive or in a place with one
bar. 6 MB for one tab is a slow, expensive first impression at exactly the moment you are trying
to impress. The 1600 px source is rendered into a ~800 px slot on desktop and ~360 px on mobile.
*Fix:* `srcset="img/thumb-x.jpg 480w, img/x.jpg 1600w"` with a `sizes` attribute, or generate a
960 px mid tier in `fetch_images.py`. Should cut the tab to under 1.5 MB with no visible change.

**15. MAJOR — Both "Print / save PDF" buttons print the entire guide and strip every URL.**
*Where:* `sec_trip()` join card and `renderTrip()` both call `window.print()`; `@media print` sets
`.sec{display:block!important}`. Measured: 28 pages, 4.2 MB.
*Why it matters:* The button on the Join card sits under "Want to come?" and implies "print this
invitation." The button in My Trip implies "print my shortlist." Both produce a 28-page document.
Worse, the print rules set `a{color:inherit;text-decoration:none}` with no `::after {content: " ("
attr(href) ")"}`, so the Sources list — the entire audit trail, and the thing you would want on
paper in a park with no cell service — prints as plain titles with no URLs. "Open in maps" prints
as three dead words. The countdown ("65 days away") is also baked into the PDF.
*Fix:* Give each button a scoped print mode (`body.printing-trip` / `printing-shortlist`) that
prints only the relevant section plus a compact essentials block. Add
`@media print { a[href^="http"]::after { content:" (" attr(href) ")"; font-size:.85em } }` and
suppress the countdown in print.

**16. MAJOR — The map is buried, unusable at the cluster, offline-broken, and unpinned.**
*Where:* `sec_photos()` / `buildMap()` in `engine.js`; verified with a real render.
*Why it matters:* Four separate problems on the single most useful planning artifact. (a) It is
behind a secondary toggle inside a tab called "Photos & Map," fourth in the nav — most recipients
will never see it. (b) At Furnace Creek, pins 1, 2, 3, 5, 6, 7 and 8 plus the base and the photo
pins all stack on top of each other; there is no clustering or spiderfy, so the cluster is
unreadable at the default fit-bounds zoom. (c) It loads Leaflet from `cdnjs.cloudflare.com` and
tiles from OpenStreetMap, which means the map is dead offline — directly contradicting README's
"works offline" and "no external requests" claims, in a park the guide itself describes as having
"essentially none" for cell service. (d) The remote `<script>` carries no `integrity` /
`crossorigin` attributes. (e) Most importantly for the trip job, the map shows *where* things are
but never *how far from our base* — the one number a joiner wants.
*Fix:* Promote the map to its own tab (or the top of the trip tab) with the base pre-centred; add
`markerCluster` or manual offsetting; precompute and display "N min from camp" per attraction as a
data field (it can be a researched constant, not a live routing call); pin Leaflet's version with
SRI; and correct the README's offline claim to "works offline except the map."

**17. MAJOR — The validator does not check `trip` at all.**
*Where:* `tools/validate.py` — `req(g, [...])` lists 16 top-level keys; `trip` is not one of them,
and there is no per-field checking of `trip`, `photos.json`, or attraction `coords`.
*Why it matters:* `trip` is the differentiator — the reason this product exists rather than being a
nicer AllTrails — and it has zero contract enforcement. That is how finding 4 (wrong night count)
passed `0 errors, 0 warnings`. The same gap means nothing catches a missing base coordinate (the
map silently loses the home pin), a `photos.json` `place` that doesn't match any attraction id
(the photo silently falls off the map), a past trip date, an empty bring list, or a source URL used
inline but absent from `sources` — which `CLAUDE.md` explicitly requires.
*Fix:* Extend `validate.py`: require `trip.{title,start,end,host,pitch,base,join}`; assert
`start < end` and `end >= today`; assert `base.coords` present and inside a plausible bbox; assert
every `photos.json` `place` resolves to an attraction id or `"base"`; assert every attraction has
`coords`; assert every `https?://` found anywhere in the file appears in `sources`; warn when
`lastVerified` is more than 45 days old or more than 30 days before `trip.start`.

**18. MAJOR — Nothing tells the reader when the page went stale.**
*Where:* Footer, `Last verified {date}`; alerts header "Current conditions · checked 2026-09-17".
*Why it matters:* The trust story is "we checked this against live sources." The Zion trip is 65
days out and Death Valley is 120. Alerts like the cyanobacteria watch, the East Rim rockfall
closure and the Death Valley road repairs change on a scale of weeks. By December this page will
still assert "Current conditions" in a confident yellow box with a September date, and the reader
has no signal that they should re-check. The one dimension the product is genuinely best-in-class
on is the one that decays silently.
*Fix:* Compute age client-side from `lastVerified` and render a tier: under 30 days, quiet; 30–90
days, an amber "checked N days ago — confirm on the official pages"; over 90 days, a banner. Add
the same warning to the print output. Also add a "re-verify before the trip" date to the host's
own workflow in `CLAUDE.md`.

**19. MAJOR — The FAQ answers a stranger's questions, not a friend's.**
*Where:* `faq` in both guides: "Do I need a reservation to enter Zion?", "Is it safe to visit in
summer?", "Can I get gas in the park?"
*Why it matters:* These are good general-guide questions and they are already answered better in
Plan and Safety. The questions an invited friend actually has are absent: *What will this cost me?
Can I come for just one day? Do I have to camp — can I sleep in a motel and drive in? Is this
kid-friendly? What car do I need? Am I fit enough for this? Can I bring my dog? What if I don't
want to hike? What happens if the weather turns?* An invitation that doesn't pre-empt the
objections leaves them to be raised — or not raised, and silently declined — in the group chat.
*Fix:* Split into `faq` (destination, keep, shorten) and `trip.faq` (join objections, render on
the trip tab directly under the Join card). Five or six entries each.

**20. MAJOR — 5.1 MB of images are fetched, credited, and never displayed — while the places people
will sleep have no photo.**
*Where:* Zion ships unused `springdale.jpg`, `watchman-campground.jpg`, `kolob-canyons.jpg`,
`hidden-canyon.jpg`, `weeping-rock.jpg`, `zion-mount-carmel-highway.jpg` (2.68 MB). Death Valley
ships unused `titus-canyon.jpg`, `racetrack-playa.jpg`, `natural-bridge.jpg`,
`twenty-mule-team-canyon.jpg`, `harmony-borax-works.jpg` (2.43 MB). All eleven appear in the
rendered "Photo credits" footer. Meanwhile `sec_stay()` and the `alsoConsider` block render no
images at all.
*Why it matters:* Two costs. The footer credits eleven photos the reader never sees, which is
confusing and slightly dishonest about what the page contains. And the highest-value image slot in
the whole invitation — "here is the campsite / the town we'll be staying in" — is empty, while the
exact photo that would fill it (`springdale.jpg`, `watchman-campground.jpg`) sits unused in the
repo. Someone deciding whether to camp on a bare gravel pad in January would very much like to see
the pad.
*Fix:* Add an optional `image` field to `stay.camping`, `stay.lodging` and `alsoConsider`, render it,
and point `trip.base` at one. Then make `validate.py` warn on manifest entries no template
references, and prune the genuinely unused ones.

### MINOR

**21. MINOR — The trip banner renders twice on the Trip tab.**
*Where:* `engine.js` sets `tbar.hidden = (secs[i].id === "trip")`, but `theme.css:243` declares
`.tripbar{display:flex}`, which overrides the user-agent `[hidden]{display:none}` rule (author
stylesheet beats UA). Verified: `[hidden=false→true, computed display:'flex']`.
*Why it matters:* The intended behaviour — suppress the redundant banner on the tab that already
shows all of it — never happens, so the Trip tab opens with the dates stated twice in the first
120 px. Small, but it is the first thing every recipient sees.
*Fix:* `.tripbar[hidden]{display:none}`.

**22. MINOR — The "Status" card wastes a third of the trip's hero row.**
*Where:* `sec_trip()` third grid card: "Planning / Hosted by Aaron. Plans below are a working draft."
*Why it matters:* It sits beside "When" and "Home base" in the most valuable real estate on the
page and communicates almost nothing actionable. "Planning" as a status does not tell a joiner
whether this is happening.
*Fix:* Replace with the cost-per-person card (finding 5) or the capacity/roster card (finding 11),
and move "hosted by Aaron, this is a draft" to a one-line byline under the title.

**23. MINOR — The landing page is a guide library, not a set of invitations.**
*Where:* root `index.html` / `render_landing()`.
*Why it matters:* Headline "Travel guides", subhead about "research-backed guides to the places
worth the drive", cards sorted alphabetically so the *later* trip (Death Valley, Jan 2027) appears
before the sooner one (Zion, Nov 2026), a "JOIN THIS TRIP" chip that is a static `<span>` styled as
a tag rather than a button, no host name anywhere, no countdown, no OG tags, and a closing line of
developer meta: "Each guide is built from a declarative `guide.json` (see the README)." Someone
who receives the root link has no idea who is inviting them or which trip is next.
*Fix:* Retitle to "Two trips. Come to one." with an "Aaron Soto" byline; sort by `trip.start`;
show the countdown on each card; make the chip a real CTA; delete the README line; add OG tags and
a favicon.

**24. MINOR — The mobile tab strip clips mid-word with no scroll affordance.**
*Where:* `nav.tabs` at 390 px; the active tab is centred by `scrollIntoView({inline:"center"})`.
*Why it matters:* On the Safety tab at phone width the strip reads "ap  Plan  Stay  **Safety**
Itineraries  FAQ" — a truncated "…ap" with no edge fade or chevron to say there is more to the
left. Nine tabs is a lot for 390 px. Most recipients will be on a phone.
*Fix:* Add left/right gradient masks on `nav.tabs` and consider collapsing Safety/FAQ/Itineraries
into a "More" group, or shorten labels ("Photos", "Plan", "Stay").

**25. MINOR — The Top 10 stat grid wraps badly when `distance` is long.**
*Where:* `.stats` on Angels Landing ("1.9 mi each way to Scout Lookout, plus 0.5 mi each way on the
chains (~4.8 mi round trip)") and The Narrows.
*Why it matters:* One long cell forces a six-line first column while Elevation gain, Time and
Start/parking each render two lines, leaving a large empty rectangle, and "Best time" drops onto a
second row. On the flagship card — rank 1, the first thing anyone scrolls to — the densest,
best-researched content looks disorganised.
*Fix:* Cap `stats.distance` at ~40 characters in the contract (validator warning) and move the
qualifier into `summary`, or switch `.stats` to a definition-list layout that tolerates uneven
lengths.

**26. MINOR — "Current conditions" mixes trip-relevant alerts with permanent and expired ones.**
*Where:* Death Valley `overview.alerts`: six items including "Scotty's Castle… remain closed" (since
the 2015 flood — an eleven-year-old permanent closure) and "The 2026 superbloom is over."
*Why it matters:* The alert box is the guide's urgency signal. Filling it with a decade-old closure
and a past-tense wildflower note teaches the reader to skim it, which is exactly when they will
miss the one that matters (Titus Canyon closed Oct 2026 – Sep 2027, which *does* overlap the trip).
*Fix:* Add `alerts[].affectsTrip: true|false` (or derive it from date ranges vs `trip.start/end`),
render the affecting ones in a dedicated "Affects our dates" block on the Trip tab, and demote the
rest to a collapsed "Other current conditions" list.

**27. MINOR — Itinerary and condition prose bolds place names but never links to the cards.**
*Where:* `itineraries[].plan[].what`, `trip.conditions[].text`. The schema explicitly documents
`<a href="#top10/angels-landing">` as supported; neither guide uses it once.
*Why it matters:* "Ride to **Temple of Sinawava (stop 9)**… continue upstream into **The Narrows**"
is a dead end — the reader has to go back to Top 10 and find it. The engineering for in-page
deep-linking is already built and unused, which makes the product feel less connected than it is.
*Fix:* Link the first mention of any attraction in itineraries, conditions and FAQ answers. Add a
validator warning when an attraction `name` appears in prose without a link.

**28. MINOR — The Bring list renders checkboxes that cannot be checked.**
*Where:* `theme.css` `.checks li::before{content:"☐"}`.
*Why it matters:* It looks like a packing checklist and behaves like a bulleted list. On a phone
the night before a trip, that is a small but real disappointment, and `localStorage` persistence is
already in the engine for exactly this kind of thing.
*Fix:* Real `<input type=checkbox>` with per-item `localStorage` state and a "N of 9 packed"
counter. Ten lines, and it gives people a reason to reopen the page.

**29. MINOR — No hosting or deploy step exists anywhere.**
*Where:* `README.md`, `CLAUDE.md` — neither mentions publishing. `engine.js` builds share URLs from
`location.origin + location.pathname`, which on a local file is `file:///home/user/...`.
*Why it matters:* The product is "a link you send to friends" and the repo has no link. Until this
is resolved, "Copy link to this trip" copies a path that works on exactly one machine. It also
blocks findings 1 and 2, which need an absolute base URL.
*Fix:* Add a GitHub Pages (or equivalent) step to the README, set `site.baseUrl` in config, and add
a `--check` CI job running `validate.py` plus a rebuild-and-diff so a hand-edited `index.html`
cannot be committed.

**30. IDEA — Per-attraction "N minutes from our base."**
*Where:* Would live on `attractions[].fromBase` or be derived at build time.
*Why it matters:* It is the single most repeated question on any trip ("how far is that from
camp?"), it converts the Top 10 from a guide into an itinerary-planning surface, and it is the kind
of trip-specific synthesis that no general product can offer. Zabriskie Point being ten minutes
from E1 is a reason to say yes. Pair it with a dated "what changed since you last looked" strip
("Updated Oct 4: added the day-before lottery date; Titus Canyon still closed") — the guide will be
rebuilt several times before the trip, so that gives people a reason to come back and makes the
freshness promise visible rather than implicit.

---

## Prioritized improvements

### Fix before sharing these two guides

| # | Improvement | Impact | Effort | Findings |
|---|---|---|---|---|
| 1 | **Fix the Zion night count** ("three nights in Springdale, plus a Vegas night"), everywhere it appears. | High | Trivial | 4 |
| 2 | **Publish, then fix the share surface**: pick a host, add `site.baseUrl`, emit absolute `og:image` + `og:url` + `twitter:card`, retitle the preview to the trip, stop truncating mid-word, generate a 1200×630 share card. | Very high | Low–Med | 1, 2, 29 |
| 3 | **Add a reply path**: `trip.contact`, a primary "I'm in →" button with a prefilled mailto/sms carrying nights, headcount, vehicle and saved picks. | Very high | Low | 3, 9 |
| 4 | **Add cost and capacity** to the trip facts row, replacing the Status card; surface "12 people / 3 vehicles" as a meter for Death Valley. | High | Low | 5, 11, 22 |
| 5 | **Make safety and alerts date-aware**: `months` on safety entries, `affectsTrip` on alerts, reorder for the trip season. | High | Low–Med | 6, 26 |
| 6 | **Fix the CSS `\n` bug and deep-link scroll-margin**, and add `.tripbar[hidden]{display:none}`. | Medium | Trivial | 13, 21 |
| 7 | **Curate the personal photos** down to place-first images, add `private: true`, get consent for any recognisable faces before the link goes out. | Medium–High | Low | 12 |
| 8 | **Extend `validate.py` to cover `trip`, photos, coords and source traceability**, and add the staleness warning. Without this, item 1 recurs on the third guide. | High | Low–Med | 17, 18 |

### Next version

| # | Improvement | Impact | Effort | Findings |
|---|---|---|---|---|
| 9 | **Trip-dated deadlines** — "reservations for our nights opened Jul 15", "lottery: apply Nov 20, 12:01 a.m. MT". The strongest differentiator available. | Very high | Medium | 8 |
| 10 | **A loose day shape** (`trip.shape`) so people can pick a day to drive in for; link itinerary prose to the cards. | High | Medium | 7, 27 |
| 11 | **`trip.ics` + "Add to calendar"**, and a roster / "who's in" list. | High | Low–Med | 10, 11 |
| 12 | **Trip FAQ** (cost, one day only, do I have to camp, kid-friendly, what car, not a hiker). | Medium–High | Low | 19 |
| 13 | **Promote and fix the map**: own tab, clustered pins, base-centred, "N min from camp" per attraction, SRI-pinned Leaflet, honest offline copy. | Medium–High | Medium | 16, 30 |
| 14 | **Performance and image reuse**: `srcset` on Top 10, a 960 px tier, images on Stay / Also-consider / base, prune unused assets. | Medium | Low–Med | 14, 20 |
| 15 | **Scoped print modes** (invitation card, shortlist) and printed URLs. | Medium | Low | 15 |
| 16 | **Polish**: landing page as an invitation set sorted by date, mobile tab fades, stat-grid wrapping, interactive bring list, favicon, "what changed" strip. | Medium | Low | 23, 24, 25, 28, 30 |

**Comparison, for calibration.** Against a Google Doc plus a group chat, this wins decisively on
content, structure and trust and loses on the only thing that closes the deal: a reply. Against
Wanderlog and TripIt, it wins on research depth and on being a beautiful thing to receive, and
loses on collaboration, cost splitting, calendar and live updates. Against AllTrails it wins on
"why go" and loses on maps and offline. The differentiated core — *a researched destination guide
that is also a specific, dated, personal invitation* — is real and nobody else is building it. It
is currently about 70% content and 10% invitation. Items 1–8 above get the invitation half to
parity with a group chat; items 9–11 make it something a group chat cannot do.
