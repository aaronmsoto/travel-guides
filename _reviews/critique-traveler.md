# Adversarial review — prospective traveler (invited friend)

**Persona:** Aaron sent me a link. Moderately outdoorsy, never been to either park, busy. I want to know:
dates, where we sleep, how to get there, what it costs me, what to bring, and how to say yes — in about
two minutes, mostly on my phone.
**Read:** landing page, `guides/zion/index.html`, `guides/death-valley/index.html` — raw text plus
screenshots at 390 px and desktop. Anchor/scroll behavior tested in a real browser.

---

## Verdict — Zion (Nov 21–25, 2026, Springdale)

1. **Probably yes** — the writing is genuinely good and the crew photos on top of Angels Landing sold me
   harder than anything else on the page.
2. What nearly stopped me: **I could not find a way to say yes.** "Tell Aaron you are in" — there is no
   email, no phone, no chat link, no form anywhere in the file.
3. Second thing that nearly stopped me: **how many nights do I book?** The page says "Four nights in
   Springdale" and then puts me in Las Vegas on night one. That is a real money question, unanswered.
4. Third: **what does this cost me?** The only prices on the trip page are a $6 lottery fee and $35
   entrance. Springdale hotel rates on Thanksgiving week are the whole budget and are nowhere.
5. And the "Status: Planning / working draft" card told me not to book anything yet, which is exactly
   the opposite of what the page needs me to do.

## Verdict — Death Valley (Jan 15–18, 2027, Echo Canyon Rd site E1)

1. **Yes, if my car can get there** — the $10/night site, the dark-sky pitch and the January 2025 photos
   (kids on the dunes, checkers on the porch) make this the more inviting of the two.
2. What nearly stopped me: **the page contradicts itself about whether my car can reach camp.** Trip tab
   says "a careful SUV or crossover"; Stay tab says passenger cars "cannot reach most sites" and demands
   8 inches of clearance; FAQ says "usually 4x4 for … Echo Canyon."
3. Related and worse: the FAQ mentions in passing that **"most rental agreements forbid unpaved roads."**
   I am flying into Vegas and renting a car. Nobody tells me what to do about that.
4. Third: **the toilet situation is one bullet** — "a shovel or wag bags — no toilets at camp." For
   anyone who has not dispersed-camped, that is the single biggest yes/no factor, and it is a footnote.
5. Fourth: I cannot tell if there is room for me. "Holds 12 people and 3 vehicles" plus "Still deciding:
   whether to add a second site if the group passes three vehicles" reads as *maybe full*.

---

## Findings, ranked by impact on my decision to join

### 1. BLOCKER — There is no way to actually join
**Both guides · Trip tab · "Want to come?" card, step 1**
> "Tell Aaron you are in, and which nights." (Zion)
> "Tell Aaron you are in — how many people, which nights, and what you are driving" (Death Valley)

There is no `mailto:`, phone number, group-chat link, form or even Aaron's last name in the body of
either page. The only clickable things in the entire Join card are **"Copy link to this trip"** and
**"Print / save PDF"** — both of which help me share the page, not attend the trip. I read the whole
invitation and then had nowhere to put my yes. Everything else in this review is downstream of this.

**Fix:** make step 1 a real button at the top of the Join card and in the sticky trip bar —
`mailto:me@aaronsoto.com?subject=Zion%20Nov%2021–25%20—%20I'm%20in&body=Names:%0ANights:%0ADriving:`
— plus a second button for the group chat if there is one. Replace "Copy link / Print" as the card's
primary actions; they are secondary.

### 2. BLOCKER — Zion: "four nights in Springdale" is three nights in Springdale
**Zion · Trip tab · header bar, "When" card, and "Getting in"**
> Header: "4 nights, base: **Springdale, UT**"
> Intro: "**Four nights in Springdale** with Zion Canyon a mile up the road."
> Getting in: "**Sat Nov 21:** travel day. Fly or drive to **Las Vegas** and sleep in or near the city.
> **Sun Nov 22:** drive Las Vegas → Springdale…"

Nov 21 is a Las Vegas night. Springdale is 22, 23, 24 — **three** nights. If I follow the instruction
"Book your own room in Springdale… book early," I book four nights over Thanksgiving week and burn
$200–400 on a room I sleep 160 miles away from. This is the most expensive error on the page.

**Fix:** header → "4 nights: 1 in Las Vegas + 3 in Springdale." Join checklist → "Book Springdale for
**Sun Nov 22, Mon 23, Tue 24**, check out Wed Nov 25. Book Las Vegas for Sat Nov 21 if you fly in."

### 3. BLOCKER — Death Valley: three different answers to "can my car get to camp?"
**Death Valley · Trip / Stay / FAQ tabs**
> Trip → Roads to camp: "The first mile of Echo Canyon Road to E1 is graded gravel that **a careful SUV
> or crossover handles**."
> Stay → Echo Canyon Road sites: "**a high-clearance SUV or truck with at least 15-inch wheel rims and
> 8 inches of ground clearance. 4WD is 'highly encouraged.' Trailers, RVs and passenger cars cannot
> reach most sites.**" Good for: "**High-clearance 4x4 owners**"
> FAQ → Do I need a 4WD: "You need high clearance and **usually 4x4 for the Racetrack, Echo Canyon** and
> most backcountry roads."

I drive a crossover. Tab one says fine, tab two says I need 8 inches of clearance and a 4x4, tab three
agrees with tab two. I cannot resolve this, so the safe answer is "I'll sit this one out."

**Fix:** one authoritative box on the Trip tab: "**Can my car get to camp?** E1 is the first site, one
mile in on graded gravel — [specific vehicles that have done it]. The 8-inch-clearance/4WD rule
recreation.gov quotes applies to E2–E9 further up. If you are unsure, park at [X] and we will shuttle
you the last mile." Then make the Stay card's requirement explicitly about the deeper sites.

### 4. BLOCKER — Death Valley: my rental car may not be allowed on the road to camp
**Death Valley · FAQ tab · "Do I need a 4WD or high-clearance vehicle?"**
> "Note that **most rental agreements forbid unpaved roads** — Farabee's Jeep Rentals in Furnace Creek
> rents vehicles that are allowed off pavement."

This is buried in the seventh paragraph of a FAQ, three tabs from the invitation, and it invalidates the
default plan for every joiner who flies to Las Vegas. Meanwhile the Join card says only "Get yourself to
Las Vegas… we will coordinate a Pahrump meet-up."

**Fix:** put it in the Join card: "Flying in? Standard rental contracts ban dirt roads. Either ride with
us from Pahrump, or rent from [Farabee's / a company that allows it]." Name a price for the Jeep option.

### 5. MAJOR — The "Join this trip" button lands on a card whose heading is hidden
**Both guides · sticky trip bar · "Join this trip →" (`#trip/join`)**

Measured in the browser at 390 px: the sticky header is 193 px tall; the anchor scrolls `#join` to
y = 0, so the card's **"Want to come?" heading and its entire opening pitch sit behind the header.**
What I actually see after tapping the biggest button on the page is a sentence starting mid-air —
"…or drive in for a day or two." — followed by the numbered list and two buttons that are Copy-link and
Print. Desktop is the same bug, 131 px worth. Top-10 deep links lose their photo the same way.

**Fix:** `section[id], .card[id]{scroll-margin-top: calc(var(--header-h) + 12px)}`, and set
`--header-h` from the existing `setStick()` measurement that already runs in `engine.js`.

### 6. MAJOR — "Status: Planning — a working draft" tells me not to commit
**Both guides · Trip tab · Status card**
> "**Planning** · Hosted by Aaron. Plans below are a working draft — say what you'd change."

On a phone this gets a full card to itself, right above "If you're joining: … book early." It is
internally contradictory: book early, but nothing is decided. As a reader deciding whether to spend
$600 and four days off, "working draft" is a reason to wait.

**Fix:** split the two ideas. Status → "**Confirmed** — site E1 booked, Aaron's room booked. **RSVP by
[date].**" Then a separate, smaller line: "The day-to-day is still open — tell us what you want to do."

### 7. MAJOR — Neither trip says how many spots are left, or by when to answer
**Both guides · Trip tab · intro + "Want to come?"**
> Zion: "**There is room for more people**"
> DV: "holds 12 people and 3 vehicles, so joiners can share our site — just tell Aaron how many people
> and cars" / Still deciding: "Whether to add a second site nearby if the group passes three vehicles"

"Room for more people" could mean two or ten. On Death Valley the vehicle cap actively reads as a
warning that I might be the one who breaks it. And there is no deadline anywhere in either guide, even
though both say things fill up ("Springdale fills for the holiday week, so book early").

**Fix:** a live line in the trip bar: "**6 of 12 spots taken · 1 vehicle slot left · RSVP by Dec 1.**"

### 8. MAJOR — Zion: no answer to "what will this cost me"
**Zion · Trip tab (whole tab)**

The only money on the tab is "$6 per application … $3 per person if drawn" and "$35 per vehicle." The
dominant cost — a Springdale room the week of Thanksgiving — is given as "$$–$$$$" two tabs away, with
no nightly number. Narrows gear rental is required by the Bring list with no price. Flights/rental car
from Las Vegas: nothing. Death Valley does better ($10/night + $30/vehicle) but still gives no total.

**Fix:** a "**Roughly what it costs**" card on each Trip tab — Zion: "3 nights Springdale ≈ $X–$Y/night
(more over Thanksgiving) · entrance $35/car, split · Narrows gear rental ≈ $Z/day · rental car + gas
from LAS ≈ $W. Ballpark per person: $___." Death Valley: "$10/night site ÷ group · $30/car · food and
gas. Ballpark: $___ — the cheap trip."

### 9. MAJOR — Zion: the Stay tab does not tell a joiner how to book what we're booking
**Zion · Stay tab**

The Trip tab sends me here — "Book your own room in Springdale (**see Stay** for the town and example
properties)". Stay opens with **Camping**: three long cards (Watchman, South, Lava Point) full of
reservation mechanics for campgrounds nobody on this trip is using. Three screens down I reach
Springdale, which gives me: no prices, no booking link (the card's only link is
`springdale.utah.gov/424/Shuttles`, a shuttle page), and "Examples: Cliffrose Springdale, Desert Pearl
Inn, Cable Mountain Lodge…" with no links. **And nowhere does it say which property Aaron is in**,
even though the Trip tab offers "or ask about sharing ours."

**Fix:** a pinned first card on Stay — "**Where we're staying:** [property], [nightly range], [booking
link], 0.4 mi from the pedestrian entrance. Book the same place or anywhere on the shuttle line."
Demote camping below lodging on this guide, and link each example property.

### 10. MAJOR — Death Valley: the bathroom answer is one bullet with jargon in it
**Death Valley · Trip tab · Bring list**
> "Trash bags to pack everything out, and a shovel or **wag bags** — no toilets at camp"

"Wag bags" is unexplained. For someone who has only ever camped at a campground, "no toilets, bring a
shovel" is the decision, not a packing note. The Trip tab's "Water & facilities" card says only
"Nearest restrooms are at Furnace Creek" (a 10-minute drive) and the rules for burying waste appear
only on a *different* Stay card, for a *different* kind of site.

**Fix:** a plain-English "**Camp life: water, toilets, trash**" card on the Trip tab — what a wag bag
is, whether digging is allowed at E1, how far the drive to a real restroom is, whether anyone is
bringing a pop-up privy, and where showers are ("The Ranch, for a fee" — say how much).

### 11. MAJOR — The landing page does not say I'm invited
**Landing (`index.html`) · masthead and cards**
> "**Travel guides** — Research-backed guides to the places worth the drive. Top 10 attractions, where
> to stay, permits, safety, and ready-made itineraries."

This is the first thing I see after tapping Aaron's link, and it reads like a guidebook publisher. No
host name, no "come with us," no spots, no dates in the heading. The invitation only starts on the
guide pages. The small "JOIN THIS TRIP" chips are `<span>`s that look like buttons and do nothing on
their own (the whole card is the link).

**Fix:** retitle to something like "**Two trips I'm planning — come along**", add "Hosted by Aaron
Soto," and put the status on each card ("3 spots left · RSVP by Dec 1"). Make the chip a real link.

### 12. MAJOR — Dev-speak on a page sent to friends
**Landing · footer line under the cards**
> "Each guide is built from a **declarative `guide.json`** (see the README). Last verified dates are
> shown in every guide's footer."

Monospace `guide.json`, "declarative," and a README I cannot open. This is the last thing on the page
and it tells me I am reading someone's side project, not an invitation.

**Fix:** delete it, or replace with "Every fact links to its official source; each guide's footer shows
when it was last checked."

### 13. MAJOR — "Tips from the research" (×20 cards)
**Both guides · Top 10 tab · every attraction card**

Every single Top 10 card has a sub-heading reading **"Tips from the research."** It is the author's
process talking, not a friend talking. The tips themselves are excellent ("Hike to Scout Lookout
without a permit — great view, and you decide about the chains there") and deserve a better frame.

**Fix:** "Good to know" or "If you go" or "What we'd do."

### 14. MAJOR — Zion: the page says November is not the best time, then takes me in November
**Zion · Overview tab vs Trip tab**
> Overview: "**Best months: April–May, October–early November.**"
> Overview → Fall: "September stays busy … before visitation drops sharply in November."
> Trip: "Late November means cool, quiet trails, a shuttle that is still running…"

Nov 21–25 sits just outside the stated best window, and the Overview never acknowledges the trip. If I
tab over before I decide, the site's own summary undercuts the invitation.

**Fix:** one sentence in the Trip tab's "What these dates mean": "This is a week past the 'best months'
on the Overview — we are trading a little warmth for far fewer people and a shuttle that still runs."

### 15. MAJOR — Zion: the Narrows is sold on the Trip tab without the health advisory
**Zion · Trip tab · "The Narrows" card vs Overview/Safety**
> Trip: "Open unless flow is above 150 cfs or a flash flood warning is issued. Water will be in the low
> 40s °F — rented dry pants or a drysuit from a Springdale outfitter is the difference between fun and
> misery."
> Overview/Safety: "**Toxic cyanobacteria health watch** on the Virgin River … Do not submerge your
> head, touch algae mats, or drink or filter in-stream water… Children and dogs are most at risk."

The word "cyanobacteria" appears **zero times** in the Trip tab. Discovering an active toxic-algae
advisory two tabs *after* being pitched a full day of wading feels like it was kept from me.

**Fix:** add to the Trip tab's Narrows card: "There's an active toxic-algae advisory on the river —
wading is fine, keep heads out and don't drink or filter it. Details in Safety."

### 16. MAJOR — The itineraries are for a trip nobody on this page is taking
**Both guides · Itineraries tab**

Both guides offer only "**One perfect day**" and "**Two days**." Zion is four nights (≈3 full days plus
a short Wednesday); Death Valley is three nights (≈2.5 days). Worse, the Zion one is written for summer
on a November trip — "In summer the lot is often full by 9" and "The Narrows properly: **four to six
hours upstream and back**" in water the Trip tab says will be in the low 40s °F.

**Fix:** add "**Our trip, day by day (draft)**" as the first itinerary on each guide, dated Nov 22 /
23 / 24 and Jan 16 / 17 / 18, and mark the generic ones "any time of year."

### 17. MAJOR — "Add to my trip" goes nowhere, but the Join card depends on it
**Both guides · Top 10 + Itineraries · "My trip" list**
> Join step 4: "Skim the Top 10, tap **Add to my trip** on what you'd want to do, **and tell us** —
> that is how we'll plan cars and shuttle times."

The list lives in my browser's `localStorage`. Its only buttons are "Print / save PDF" and "Clear." I
did the homework and there is no send. And when empty it says "Your list is saved in this browser" —
which quietly tells me it never reaches Aaron.

**Fix:** a "**Send my picks to Aaron**" button that opens a prefilled email listing the saved items.

### 18. MAJOR — Top 10 cards bury the reason to go under a wall of specs (phone)
**Both guides · Top 10 tab · every card at 390 px**

On a phone the fact grid renders as two narrow columns before any prose, so Angels Landing opens with
"1.9 mi each way / to Scout / Lookout, plus / 0.5 mi each / way on the / chains (~4.8 / mi round / trip)"
broken over eight lines. The spec block plus badges fill the screen; the sentence that actually sells
it — "one of the most exposed maintained trails in the national park system … chains bolted into the
rock, drop-offs of up to 1,000 feet" — is below the fold. The cards answer "how far" before "why."

**Fix:** below 480 px, stack the facts one per row *after* the description, or lead each card with a
single bold line ("The park's signature hike — a knife-edge ridge with chains and 1,000-foot drops").

### 19. MINOR — Zion: Las Vegas is 160 miles on one tab and 170 on two others
**Zion · Trip vs Overview vs Plan**
> Trip: "drive Las Vegas → Springdale, about **160 mi**, ~2 h 45 min"
> Overview: "Nearest airports — **Las Vegas 170 mi**" · Plan: "NPS lists the airport at **170 miles**"

Small, but it is the number I use to book a flight and plan a drive, and it made me double-check
everything else on the page.

**Fix:** pick one ("170 mi from LAS, about 2 h 45 min") or label the difference explicitly.

### 20. MINOR — Jargon used on the Trip tab, explained (if at all) two tabs later
**Both guides · Trip tab**
- Zion: "the **day-before lottery**: apply 12:01 a.m.–3 p.m. **MT** the day before" — MT is only
  expanded in Overview ("All permit deadlines are quoted in MT"), a tab away, and "day-before lottery"
  is never defined in plain words on the Trip tab.
- Zion: "Open unless flow is above **150 cfs**" — "cubic feet per second" appears once, in Overview.
- DV: "a reserved, **designated dispersed** site", "**high clearance**", "**wag bags**", "Backcountry
  Roadside Camping" (a recreation.gov facility name that reads like an internal label).

**Fix:** expand on first use, in the Trip tab, every time: "Mountain Time (Utah — one hour ahead of Las
Vegas)", "150 cubic feet per second — the park's closure line", "a private site we reserved on a dirt
road, with nothing at it: no water, no toilet, no picnic table."

### 21. MINOR — Zion photos are from a different season than the trip
**Zion · Photos & Map tab · gallery intro**
> "**8 photos from Summer 2012** — a taste of what the trip actually looks like."

They are wonderful photos and the best sales tool on the page — but they show shorts, warm water,
green cottonwoods and a rattlesnake, and the trip is late November with water "in the low 40s °F."
"What the trip actually looks like" is not what this trip will look like. (Death Valley gets this
right: "10 photos from **January 2025**" against a January trip.)

**Fix:** "From a summer trip in 2012 — same places, warmer water. November is colder, quieter and the
light is lower." Or add two or three November frames.

### 22. MINOR — A coiled rattlesnake is the second photo in the invitation gallery
**Zion · Photos & Map tab · grid position 2**
> alt: "A rattlesnake coiled in the shade beside the Angels Landing trail — watch where you put your
> hands"

Full-width on a phone, directly after the group summit shot, and the grid shows **no captions** (they
only appear in the lightbox) — so it lands with no context in the one part of the page whose job is to
make me want to come. It also contradicts the November framing; snakes are not a November problem.

**Fix:** move it later in the grid, show captions under grid images, or keep it in Safety instead.

### 23. MINOR — "Duness"
**Death Valley · Top 10 tab · type filter chips**

The filter row reads: All / Viewpoints / Scenic drives / **Duness** / Areas / Hikes / Canyons. An
auto-pluralizer added "s" to "Dunes." It is the kind of typo that makes me trust the numbers less.

**Fix:** pluralization exception, or take the label from the data.

### 24. MINOR — Landing page: the "JOIN THIS TRIP" pill breaks across two lines
**Landing · Zion card · `.joinchip` at 390 px**

It renders as "JOIN THIS" on one line and "TRIP" on the next, with the pill background split in two.
The Death Valley card above it fits, so it looks like a glitch rather than a design.

**Fix:** `white-space:nowrap` on the chip and let the line wrap before it (and make it an actual link).

### 25. MINOR — Death Valley trip bar wraps to an orphan separator
**Death Valley · sticky trip bar at 390 px**

Renders as "3 nights, base: Echo Canyon Road, site E1" / "· 120 days away" — the middle dot starts the
second line on its own. Zion's shorter base name hides the bug.

**Fix:** drop the separator when the bar wraps, or make each fact its own row on narrow screens.

### 26. MINOR — Death Valley: "all three nights or just the weekend" is not a choice
**Death Valley · Trip tab · "Want to come?"**
> "Come for **all three nights or just the weekend**."

The trip is Fri–Mon of MLK weekend. All three nights *are* the weekend. I read it twice looking for the
option I was being offered.

**Fix:** "Come for all three nights, or just Saturday and Sunday — the site is booked either way."

### 27. MINOR — The Bring list looks tickable and isn't
**Both guides · Trip tab · "Bring" (`ul.checks`)**

Each line is prefixed with a ☐ glyph (CSS `content:"☐"`), so on a phone it reads as an interactive
packing checklist. Tapping does nothing and nothing is remembered. Given that "Add to my trip" *is*
interactive elsewhere on the same page, this is a fair thing to expect.

**Fix:** either make them real, persisted checkboxes (same `localStorage` pattern as "My trip") with a
"share my packing list" action, or drop the checkbox glyph for plain bullets.

### 28. NICE-TO-HAVE — No "add to calendar"
**Both guides · trip bar**

Both pages lead with 📅 and a date range, and the very first thing I want to do once I am interested is
put it on my calendar before I forget. There is no `.ics` and no calendar link.

**Fix:** an "Add to calendar" link next to the dates generating a simple `.ics` (all-day, park name,
base location, link back to the guide).

### 29. NICE-TO-HAVE — Death Valley: gear is assumed, not offered
**Death Valley · Trip tab · Bring + "Want to come?" step 3**
> "Sort a cold-weather sleeping setup and your own water and food (see Bring)."
> "Sleeping setup rated to **20°F**: bag, insulated pad, and a warm hat for sleeping"

A 20°F bag and an insulated pad are $250+ if I don't own them, and that is a quiet, invisible reason to
say no. Zion has the same gap with Narrows gear ("rent dry pants or drysuit… in Springdale" — no price,
no shop named).

**Fix:** "Don't own a winter bag? Aaron has two spares / REI Las Vegas rents one for ~$X / here's the
cheap option." For Zion, name the Springdale outfitter and the day rate.

### 30. NICE-TO-HAVE — Nothing tells me who else is coming or what the evenings are like
**Both guides · Trip tab**

The strongest line on either page is Death Valley's "hikes are more fun in a group, cars fill up
efficiently, and dinners in Springdale are better with company" (Zion) — but neither page says who is
already in, whether it is couples or families or solo friends, whether kids are along (the photos
suggest yes, on both trips), or what a night actually looks like. That is the part of a trip people
say yes to.

**Fix:** a short "**Who's coming**" line, and one sentence per trip about the evenings — "dinner in
town most nights, one group cook-out" / "camp chairs, a stove and a very dark sky."

### 31. NICE-TO-HAVE — Hidden tabs on a phone
**Both guides · tab strip at 390 px**

Four of nine tabs are visible ("The Trip · Overview · Top 10 · Photos & M…"); Stay, Safety, Itineraries
and FAQ are off-screen with no scroll affordance beyond the cut-off word. The Stay and FAQ tabs answer
most of the questions in this review, and a hurried reader will never see them.

**Fix:** a fade/chevron at the right edge, and inline links from the Trip tab into Stay, Plan and FAQ
at the moment each question arises ("Where exactly do I book? → Stay").
