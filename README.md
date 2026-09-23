# Juntar — trip guides

**The more the merrier!** Live site:
https://juntar.net/

Each guide is a research-backed destination page that doubles as a **trip invitation**: the first
tab is *The Trip* (dates, home base, getting there from the LA/OC area, what those dates mean,
cost, who's in, packing list, how to join), followed by the reference tabs (Overview, Top 10,
Photos & Map, Plan, Stay, Safety, FAQ). Joining is coordinated directly with the host; readers can
pick attractions and send the host a link to their picks.

| Trip | Dates | Base | Status |
|---|---|---|---|
| [Mecca Hills — Painted Canyon & Ladder Canyon](guides/mecca-hills/) | Oct 17–18, 2026 | Dispersed camp in Painted Canyon (BLM); The Living Desert on the way home | potential |
| [Zion National Park](guides/zion/) | Nov 21–25, 2026 | Springdale, UT (night 1 in Las Vegas) | planning |
| [Death Valley National Park](guides/death-valley/) | Jan 15–18, 2027 | Echo Canyon Road site E1 (reserved dispersed) | planning |

## How it works

Every guide is a **declarative `guide.json`** (contract: `tools/schema.md`) rendered by
`tools/build.py` into a self-contained HTML page: inline CSS/JS, relative images, works offline
except the on-demand map, prints cleanly, no server. Authors edit JSON, never the built HTML.

```
site.json                       site title/tagline, host, baseUrl (absolute Open Graph tags), noindex
guides/<slug>/guide.json        the only file authors edit — destination + trip
guides/<slug>/img/              licensed photos (sources.json → fetch_images.py → manifest.json, thumbs, mid tier)
guides/<slug>/photos/           personal photos + photos.json (import_photos.py; private:true hides one)
guides/<slug>/src/_research/    dated research notes with a source URL on every fact
guides/<slug>/index.html        GENERATED (also trip.ics)
shared/theme.css, engine.js     one design system + one client engine for every guide
tools/                          build.py · validate.py · fetch_images.py · import_photos.py · new_guide.py · schema.md
_reviews/                       adversarial critique reports (not published)
docs/                           specifications and research memos (v0.2 plan; not published)
.claude/skills, .claude/agents  the reusable workflows and subagents (see below)
.github/workflows/pages.yml     validate → build → stale-HTML check → deploy on every push to main
```

## Commands

```bash
python3 tools/validate.py              # 0 errors required; read the warnings
python3 tools/build.py                 # all guides + landing page + trip.ics
python3 tools/new_guide.py <slug> --name "…" --state "…" --start YYYY-MM-DD --end YYYY-MM-DD --base "…" --kind campsite|town|lodge
python3 tools/fetch_images.py <slug>   # after editing img/sources.json
python3 tools/import_photos.py <slug> --trip "April 2023" --place <attraction-id> --caption "…" photo.jpg
python3 tools/validate.py --links      # live URL check before a re-verification
```

Dependencies: Python 3.11+, Pillow (`pip install Pillow`). Playwright + Chromium only for screenshot review.

## Workflows (Claude Code skills)

`/new-trip` scaffold → research → images → photos → validate → build → publish ·
`/add-photos` · `/update-trip` (dates, status, roster, re-verification) · `/critique`
(three fresh-context reviewers → `_reviews/critique-report.md` → fixes) · `/publish`
(validate, build, push `main`, confirm the deploy). Subagents: `trip-researcher` (Opus),
`image-sourcer` (Sonnet), `critic-traveler`, `critic-ux`, `critic-product` (Opus).

## Client features

Hash routing and deep links (`#top10/angels-landing`, `#trip/picks=a,b`) · Top 10 filters ·
**My picks** kept in the browser and copyable as a link for the host · `trip.ics` "Add to
calendar" · packing checklist that remembers ticks · Photos & Map (lightbox; Leaflet map loaded on
demand with photo pins, Top 10 pins, home base) · Safety sorted for the trip's season · staleness
warning after 30/90 days · miles/°F ↔ km/°C · light/dark · print with URLs · keyboard, live
regions, reduced motion.

## Publishing

Pushes to `main` deploy to GitHub Pages via `.github/workflows/pages.yml` (about 30 seconds). The custom domain `juntar.net` is set by the `CNAME` file at the repo root (published with the site); the old `aaronmsoto.github.io/travel-guides/` URL redirects there.
`site.json → noindex` keeps pages out of search engines; links work for anyone they're sent to.

## Licensing

Text © the repository owner. Destination photos carry their own license (public domain, CC BY, or
CC BY-SA), shown under each image and in the footer. Personal photos are the host's, used with
permission; no names are attached to anyone in them. Not affiliated with the National Park
Service or the Bureau of Land Management.
