# CLAUDE.md — Juntar trip guides

Declarative trip guides: `guides/<slug>/guide.json` is the source of truth; `tools/build.py`
renders it. **Never hand-edit `guides/*/index.html` or root `index.html`** — rebuild instead.
Live: https://juntar.net/ · three guides: mecca-hills, zion, death-valley.

## Commands
- `python3 tools/validate.py [slug]` — 0 errors before building or committing; read the warnings
- `python3 tools/build.py [slug]` — renders guide(s), landing page, trip.ics (deterministic)
- `python3 tools/new_guide.py <slug> …` — scaffold a guide with TODO-marked fields
- `python3 tools/fetch_images.py <slug>` — after editing `img/sources.json`
- `python3 tools/import_photos.py <slug> --trip "…" --place <id> --caption "…" file.jpg`
- `python3 tools/validate.py --links` — live URL check (slow; before a re-verification)

## Skills and agents (in `.claude/`)
- Skills: `new-trip`, `add-photos`, `update-trip`, `critique`, `publish` — follow them; they encode
  the order of operations and the checks.
- Agents: `trip-researcher` (Opus, writes guide.json + notes), `image-sourcer` (Sonnet, licensed
  images), `critic-traveler` / `critic-ux` / `critic-product` (Opus, fresh-context reviewers).
  Launch research and images in parallel; launch the three critics in parallel.

## Conventions
- Contract in `tools/schema.md` (schema 1 + 1.2 additions). Extend the contract first, then
  `tools/build.py`, then data. Validate after every data change.
- Every factual field traces to a URL in `sources`; research notes with fetch dates live in
  `guides/<slug>/src/_research/`. No invented numbers — omit, "varies", or UNVERIFIED in notes.
- `html:` fields allow only `<b> <i> <em> <strong> <a> <br> <code>`; no "html:" prefixes; expand
  jargon on first use; at most one bold run per paragraph; "Good to know", never "tips from the research".
- Attractions: exactly 10, ranked 1..10 by popularity, kebab-case ids, `coords` required, official
  distances/times, `stats.distance` ≤ 40 chars.
- Camping entries state the booking mode (`reservable | first-come | mixed | permit`) and the exact
  mechanics in `bookingDetail`; the group's own site/town is `ours: true`.
- Images: only public domain / CC0 / CC BY / CC BY-SA; credit renders from `img/manifest.json`;
  every manifest image must be used somewhere; ≤ ~12 MB per guide; keep the 960 px `mid-` tier.
- US spelling; miles/feet/°F in data (the client converts).
- Per-park colors in `guide.json → theme`; the light accent must pass 4.5:1 under white text.
- The Trip tab is the product: `trip` complete (status, base, arrival/departure, conditions, bring,
  cost, keyDates, join, faq; roster/capacity as known). `status` is `potential | planning |
  confirmed`. Night counts must agree with the dates (`nightsNote` when the first night is elsewhere).
- Directions are for drivers from the LA/OC (Huntington Beach) area: no flights, airports, or
  rental cars anywhere.
- Joining is coordinated with the host in person/chat: no RSVP forms or contact fields. Readers
  send the host a link to their picks.
- No day-by-day schedule on the trip tab (host's call); the Top 10 tiles carry "what we might do".
- Roster lists only what the host states. Never infer or attach names to people in photos.
  Family photos are fine to publish; `private: true` in photos.json hides one.
- Safety entries carry `seasons`; alerts carry `affectsTrip`; both drive the trip-aware rendering.
- Site-level text lives in `site.json` (title, tagline, host, baseUrl, noindex).

## Host decisions (2026-09-17)
- The three-persona critique runs only when the host asks — not by default for new guides.
- Potential trips are shown on the home page (tagged "potential", "See the idea").
- Uploading a photo is opting in: photos are public by default; `private: true` opts one out later.
- Host is "Aaron" via `site.json` for now; per-trip hosts/co-hosts are a planned change if the
  prototype gets positive feedback — keep `trip.host` in the data so that is a renderer-only change.

## Publishing
- Commit on the working branch; fast-forward `main` and push only when every guide validates
  (a half-written guide fails the deploy or goes live). `.github/workflows/pages.yml` validates,
  builds, fails on stale HTML, deploys. The `github-pages` environment must allow `main`.
- `_reviews/`, `tools/`, `shared/`, `src/`, `site.json` are excluded from the published site.

## Adding a guide (short form — the `new-trip` skill has the full version)
1. `tools/new_guide.py` scaffold → 2. `trip-researcher` + `image-sourcer` in parallel →
3. `import_photos.py` → 4. validate, build, review at 1200/390 px light+dark →
5. `publish` (run `critique` only when asked).
