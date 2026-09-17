---
name: critique
description: Run the three fresh-context adversarial reviewers (prospective traveler, UI/UX designer, product innovator) on the built pages, synthesize _reviews/critique-report.md, and implement the fixes. Use before sharing a new guide or after a large redesign.
---
# Three-persona critique

1. Build first (`python3 tools/build.py`). Make the Playwright helpers available (the session's
   scratchpad `pw/` folder with `shot2.js`, `shot3.js`, `env.sh` exporting `CHROME`; if absent,
   `npm i playwright` in a scratch folder and point `CHROME` at `/opt/pw-browsers/chromium-*/chrome-linux/chrome`).
2. Launch **critic-traveler**, **critic-ux**, **critic-product** in parallel (background), each told
   which guides to review, the trip facts, the by-design decisions (coordinate-with-host joining,
   drivers from the LA/OC area, no day-by-day schedule), and where the screenshot helpers are.
3. When all three report, read the three files and write `_reviews/critique-report.md`:
   consensus verdict, cross-cutting themes table (finding ids per persona), fix plan split into
   "fixed in this pass" / "deliberately not done (why)" / "next version", and an implementation log.
4. Implement: renderer/engine/theme changes first, then data, then rebuild; verify in-browser
   (mobile width, deep links, dark mode). Keep by-design decisions unless the host changes them.
5. Append the implementation log, commit (`_reviews/` is committed but excluded from the site), `publish`.
