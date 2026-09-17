---
name: add-photos
description: Import personal trip photos into a guide's Photos & Map tab with captions and map placement. Use when the host shares photos from a past trip.
---
# Add photos

1. Identify the location of each photo from its content (landmarks) and the host's notes. Never
   name people; captions describe place and moment ("The whole crew at Zabriskie Point"). Kids and
   families are fine to show — the host has said so — but nothing that reads as a name tag.
2. For each photo:
   `python3 tools/import_photos.py <slug> --trip "<Album, e.g. January 2025>" --credit "Aaron Soto" --place <attraction-id|base> --caption "…" /path/to/photo.jpg`
   The tool resizes to 1600 px, strips EXIF from the published copy, keeps GPS/date in photos.json
   when present, and writes a 480 px thumb. `--place` must be an attraction id from guide.json (or
   `base`); it drives the map pin when there is no GPS.
3. Hide a photo from the page without deleting it: add `"private": true` to its item in
   `guides/<slug>/photos/photos.json`.
4. Reorder if a photo should not lead the album (e.g. the rattlesnake): edit the `items` order.
5. `python3 tools/validate.py <slug>` (checks that every place resolves and files exist),
   `python3 tools/build.py <slug>`, then `publish`.
