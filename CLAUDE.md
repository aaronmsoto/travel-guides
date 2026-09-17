# CLAUDE.md — travel-guides

Declarative travel guides: `guides/<slug>/guide.json` is the source of truth; `tools/build.py`
renders it. **Never hand-edit `guides/*/index.html` or root `index.html`** — rebuild instead.

## Commands
- `python3 tools/validate.py [slug]` — must report 0 errors before building or committing
- `python3 tools/build.py [slug]` — renders guide(s) + landing page
- `python3 tools/fetch_images.py <slug>` — after editing `img/sources.json`
- `python3 tools/validate.py --links` — live URL check (slow; run before a release)

## Conventions
- Content contract lives in `tools/schema.md`. Extend the contract there first, then the renderer
  in `tools/build.py`, then the data.
- Every factual field must be traceable to a URL in `sources`; research notes with fetch dates
  go in `guides/<slug>/src/_research/`. No invented numbers — omit or mark "varies".
- `html:` fields allow only `<b> <i> <em> <strong> <a> <br> <code>`; everything else is escaped.
- Attractions: exactly 10, ranked 1..10 by popularity, kebab-case ids, official distances/times.
- Camping entries must state the booking mode (`reservable | first-come | mixed | permit`) and the
  exact mechanics (window, fee, season) in `bookingDetail`.
- Images: only public domain / CC0 / CC BY / CC BY-SA; credit is rendered automatically from
  `img/manifest.json`. Keep guides ≤ ~12 MB of images.
- US spelling; miles/feet/°F in data (the client converts to metric).
- Shared CSS/JS is in `shared/`; per-park accent colors go in `guide.json → theme` (the light
  accent must pass 4.5:1 against `--on-accent` white; dark accents use a dark `--on-accent`).
- The Trip tab is the product: keep `trip` complete (contact, cost, capacity, keyDates, conditions,
  faq) and never restate a night count that disagrees with the dates — `validate.py` checks it.
- No day-by-day schedule on the trip tab (owner's call); the Top 10 tiles carry "what we might do".
- Personal photos: `private: true` in photos.json hides a photo from the page; get consent before a
  link with identifiable people goes out.
- Never commit a hand-edited `index.html`; `tools/build.py` is deterministic — rebuild and diff.

## Adding a guide
1. `mkdir -p guides/<slug>/img guides/<slug>/src/_research`
2. Research → `guide.json` per `tools/schema.md`; images → `img/sources.json` → `fetch_images.py`
3. `validate.py` → `build.py` → open `guides/<slug>/index.html` (desktop + 390 px wide)
4. Adversarial critique with three fresh-context personas → `_reviews/` → fix → rebuild
