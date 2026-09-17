# travel-guides

Research-backed, single-page travel guides that double as **trip invitations**. Each guide is a
**declarative `guide.json`** rendered by a small build step into a self-contained HTML page
(inline CSS/JS, relative images) that works offline (except the map), prints cleanly, and needs
no server. The first tab is **The Trip**: dates, home base, getting in/out, what these dates mean,
cost, capacity, a packing list, and an "I'm in" RSVP that carries the reader's picks.

| Guide | Page | Source of truth |
|---|---|---|
| Zion National Park (Utah) | `guides/zion/index.html` | `guides/zion/guide.json` |
| Death Valley National Park (California/Nevada) | `guides/death-valley/index.html` | `guides/death-valley/guide.json` |

Open `index.html` at the repo root for the landing page. Every guide has the same nine tabs:
**The Trip** · **Overview** (hero, quick facts, current alerts, seasons) · **Top 10** (ranked
natural attractions with filters and "Add to my picks") · **Photos & Map** (personal photos from
past trips, a lightbox, and a map of photo pins, Top 10 pins and the home base) · **Plan** ·
**Stay** (camping with exact booking mechanics, lodging) · **Safety** (sorted for the trip's
season) · **Itineraries** · **FAQ**. A footer lists every source and photo credit.

## Architecture

```
guides/<slug>/guide.json        declarative content — the only file authors edit (contract: tools/schema.md)
guides/<slug>/img/sources.json  where each photo comes from + license (input to fetch_images.py)
guides/<slug>/img/manifest.json generated: file → title/author/license/sourceUrl/size
guides/<slug>/img/*.jpg         generated: resized photos (≤1600 px) + thumb-*.jpg
guides/<slug>/src/_research/    research notes with source URLs and fetch dates (audit trail)
guides/<slug>/photos/           personal trip photos + photos.json (tools/import_photos.py)
guides/<slug>/index.html        GENERATED — never edit by hand
guides/<slug>/trip.ics          GENERATED — "Add to calendar"
site.json                       site title, host, baseUrl (absolute Open Graph tags), noindex
shared/theme.css, engine.js     one design system + one client engine for every guide
tools/build.py                  guide.json + shared → guides/<slug>/index.html + root index.html
tools/validate.py               contract checks; --links also fetches every URL
tools/fetch_images.py           downloads/resizes photos, writes manifest.json
_reviews/                       adversarial critique reports and the improvement log
```

## Build

```bash
python3 tools/validate.py              # 0 errors required
python3 tools/fetch_images.py zion     # only when img/sources.json changed
python3 tools/build.py                 # all guides + landing page
python3 tools/validate.py --links      # optional: live-check every URL (slow)
python3 tools/import_photos.py <slug> --trip "January 2025" --place <attraction-id> --caption "..." photo.jpg
```

Dependencies: Python 3.11+, Pillow (`pip install Pillow`) for image fetching only.

## Pipeline (how a guide gets made)

1. **Research** — an agent fetches official pages (nps.gov, recreation.gov, DOT, gateway towns)
   and writes `src/_research/*.md` with a source URL and fetch date on every fact, then authors
   `guide.json` against `tools/schema.md`. Unverifiable numbers are omitted, not guessed.
2. **Images** — an agent finds public-domain / CC BY / CC BY-SA photos (NPS, Wikimedia Commons),
   records them in `img/sources.json`, and `fetch_images.py` normalizes them and writes credits.
3. **Build + validate** — `validate.py` enforces the contract (exactly 10 ranked attractions,
   4 seasons, booking modes, allowed inline HTML, images present); `build.py` renders.
4. **Adversarial critique** — three fresh-context reviewers (prospective traveler, UI/UX
   designer, product innovator) attack the built pages; findings are merged into
   `_reviews/critique-report.md` and fixed; the report logs what changed.

## Publishing

The site is built for GitHub Pages at the `baseUrl` in `site.json`
(`https://aaronmsoto.github.io/travel-guides/`). Plan: create `main` from the working branch, add a
Pages workflow that runs `validate.py` + `build.py` and deploys, add `.nojekyll`, and enable
Pages (Settings → Pages → Source: GitHub Actions). `noindex` in `site.json` keeps the pages out of
search engines while links still work for anyone they're sent to.

## Client features

Hash routing (`#top10/angels-landing` deep-links to a card; `#trip/picks=a,b` shares a pick
list) · filters by type, difficulty, permit-free, "my picks" · **My picks** saved in `localStorage`,
sent with the RSVP, copyable as a link · **I'm in** RSVP (prefilled email/text when a contact is
set, otherwise a ready-to-paste message) · `trip.ics` calendar file · packing checklist that
remembers ticks · miles/°F ↔ km/°C toggle · light/dark theme with an `--on-accent` token · print
(whole guide, or just the picks, with URLs printed) · live regions, reduced-motion, keyboard
accessible · no external requests except the on-demand map (Leaflet from cdnjs with SRI,
OpenStreetMap tiles).

## Licensing

Text: © the repository owner. Photos: each carries its own license (public domain, CC BY, or
CC BY-SA) shown under the image and in the footer; share-alike images stay share-alike.
Not affiliated with the National Park Service.
