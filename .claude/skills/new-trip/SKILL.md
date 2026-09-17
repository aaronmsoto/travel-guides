---
name: new-trip
description: Add a new trip guide end to end — scaffold, research (trip-researcher), images (image-sourcer), personal photos, validate, build, review renders, three-persona critique, fixes, publish. Use when the host says "add a trip to <place>" with dates and a base.
---
# New trip guide

Inputs to collect from the host before starting (ask only for what is missing):
dates (start/end), destination, home base (campsite / town / lodge, exact site if known), status
(`potential` for an idea, `planning` when dates are set, `confirmed` when booked), the must-see
attractions, who is already in (only what the host states — never infer names from photos),
any photos from past trips with the album name, and anything unusual (permits, lottery, vehicle).

Steps
1. `python3 tools/new_guide.py <slug> --name "…" --state "…" --start YYYY-MM-DD --end YYYY-MM-DD --base "…" --kind campsite|town|lodge --status potential`
2. Launch **trip-researcher** (background) with: the host's facts above, the must-haves, the
   directions convention (drivers from the LA/OC area, no flights/rental cars), the join
   convention (coordinate with the host), and "read tools/schema.md + guides/death-valley/guide.json first".
   In parallel launch **image-sourcer** with the expected filenames (hero.jpg, `<attraction-id>.jpg`,
   plus stay/also-consider subjects) — it can start from the must-haves and fill the rest when
   guide.json lands.
3. Import personal photos while agents run: see the `add-photos` skill.
4. When both report: `python3 tools/validate.py <slug>` → 0 errors; reconcile image filenames with
   `img/manifest.json`; check `photos.json` places resolve to attraction ids.
5. `python3 tools/build.py` and review renders at 1200 px and 390 px (`#trip`, `#overview`,
   `#top10`, `#photos`, `#stay`), light and dark. Fix data, not HTML.
6. Critique only when the host asks for it (`critique` skill); by default go straight to publish.
7. `publish` skill. Commit message: "<Place>: new guide (…)"; mention UNVERIFIED items in the reply.

Conventions that must hold (validate.py enforces most): exactly 10 ranked attractions with coords;
trip block complete; night count consistent with dates; safety entries carry `seasons`; alerts
carry `affectsTrip`; the group's own site/town marked `ours: true`; images licensed PD/CC BY/CC BY-SA
only; guide ≤ ~12 MB of images.
