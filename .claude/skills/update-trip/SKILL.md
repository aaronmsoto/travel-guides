---
name: update-trip
description: Change an existing trip's facts — dates, status, base, roster/who's in, cost, key dates, directions, join steps — or re-verify a guide's conditions before the trip. Use for "update the Zion trip…" style requests.
---
# Update a trip

- Everything lives in `guides/<slug>/guide.json → trip`. Never edit built HTML.
- Common edits: `status` (potential → planning → confirmed), `start`/`end` (+ `nightsNote` if the
  first night is elsewhere), `roster` (only what the host states, e.g. "Ben's family (3rd grade DLI
  class) — camping at Furnace Creek Campground"), `capacity` (people/vehicles for a campsite),
  `keyDates`, `cost`, `arrival`/`departure` (drivers from the LA/OC area), `conditions`, `bring`,
  `join.steps` (always "Coordinate with <host>"), `faq`.
- Re-verification before a trip: re-fetch the agency's conditions/alerts page, update
  `overview.alerts` (set `affectsTrip`), fees, shuttle/permit windows, campground status; bump
  `lastVerified`; note the fetch date in `src/_research/`. The site shows a staleness warning
  after 30/90 days, and `validate.py` warns after 45.
- After edits: `python3 tools/validate.py <slug>` (0 errors), `python3 tools/build.py`, review the
  `#trip` render, then `publish`.
