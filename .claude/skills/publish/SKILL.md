---
name: publish
description: Validate, build, commit, push to main, and confirm the GitHub Pages deploy and live URLs. Use after any content or code change that should go live.
---
# Publish

1. `python3 tools/validate.py` → must be 0 errors (warnings: read them; unused images and
   untraced links are usually real).
2. `python3 tools/build.py` → regenerates `index.html`, `guides/*/index.html`, `guides/*/trip.ics`.
   The workflow fails if committed HTML is stale, so always rebuild before committing.
3. Commit on the working branch, then fast-forward `main` to it and push both
   (`git branch -f main HEAD && git push origin main`). Only push `main` when every guide validates —
   a half-written guide would fail the deploy or go live.
4. Watch the run: `.github/workflows/pages.yml` (validate → build → stale check → deploy), ~30 s.
   Poll `https://api.github.com/repos/aaronmsoto/travel-guides/actions/runs?per_page=1&branch=main`
   until `completed success`, then `curl -sI https://aaronmsoto.github.io/travel-guides/` and the
   guide URLs; grep the live HTML for a string from the change.
5. If the deploy job is rejected by environment protection rules, the `github-pages` environment's
   deployment-branch policy must allow `main` (Settings → Environments → github-pages).
6. Report the live URLs and anything left UNVERIFIED.
