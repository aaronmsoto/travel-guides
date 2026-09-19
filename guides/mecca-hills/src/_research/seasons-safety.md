# Seasons, weather, daylight and safety

Fetch date for every entry: **2026-09-17**.

## 1. Climate normals — the station to use

The nearest long-record NOAA station to Mecca is **Jacqueline Cochran Regional Airport, Thermal, CA**
(GHCN id **USW00003104**, listed by NOAA as "DESERT RESORTS RGNL AP, CA US"), about 10 miles northwest
of Mecca in the same valley floor. Do **not** use Palm Springs Regional (USW00093138) — it is 40 miles
up-valley and several hundred feet higher.

**NOAA 1991–2020 monthly normals, USW00003104** (queried 2026-09-17 via
https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020&stations=USW00003104&dataTypes=MLY-TMAX-NORMAL,MLY-TMIN-NORMAL,MLY-PRCP-NORMAL&format=json ):

| Month | Normal high °F | Normal low °F | Normal precip in |
|---|---|---|---|
| Jan | 71.0 | 39.0 | 0.64 |
| Feb | 74.3 | 42.9 | 0.61 |
| Mar | 81.1 | 49.0 | 0.34 |
| Apr | 87.2 | 54.8 | 0.08 |
| May | 94.6 | 62.9 | 0.01 |
| Jun | 103.0 | 69.1 | 0.01 |
| Jul | 106.9 | 75.6 | 0.13 |
| Aug | 106.2 | 74.9 | 0.12 |
| Sep | 101.5 | 68.2 | 0.32 |
| **Oct** | **90.9** | **56.9** | **0.19** |
| Nov | 78.7 | 44.7 | 0.17 |
| Dec | 69.3 | 37.7 | 0.34 |

**NOAA 1991–2020 daily normals for our dates**, same station (queried 2026-09-17 via the
`normals-daily-1991-2020` dataset):

| Date | Normal high °F | Normal low °F |
|---|---|---|
| Oct 16 | 90.9 | 56.9 |
| **Oct 17** | **90.5** | **56.5** |
| **Oct 18** | **90.2** | **56.1** |
| Oct 19 | 89.8 | 55.7 |

So: a normal mid-October day at Mecca is **about 90°F in the afternoon and about 56°F at dawn** — a
34-degree swing. That is the number the guide uses, and it is why the plan is an evening hike.

**Season table used in the guide** (derived from the monthly table above, same source):
- Spring, Mar–May: highs 81–95°F, lows 49–63°F — verdict Best
- Summer, Jun–Aug: highs 103–107°F, lows 69–76°F — verdict Hard
- Fall, Sep–Nov: highs 79–102°F, lows 45–68°F — verdict Best
- Winter, Dec–Feb: highs 69–74°F, lows 38–43°F — verdict Best
(Summer is the only genuinely bad season; the other three are honestly good, so the table leans on the
notes to separate them: September is still 100°F+, and the wind and cold of January are real.)

**Rain:** the valley averages well under half an inch in any month; October's normal is **0.19 in**.
The risk is not volume, it is that a single desert cell dumps it into a slot canyon (see 3 below).

## 2. Daylight and moon for Saturday October 17, 2026

US Naval Observatory, coordinates 33.6190, -116.0000, time zone -7 (PDT), queried 2026-09-17:
https://aa.usno.navy.mil/api/rstt/oneday?date=2026-10-17&coords=33.6190,-116.0000&tz=-7

- Begin civil twilight **06:25**
- Sunrise **06:51**
- Solar noon 12:29
- **Sunset 18:08** (6:08 p.m. PDT)
- End civil twilight **18:33**
- Moon: waxing crescent, **42% illuminated**; moonrise 13:24, moonset **23:14**. First Quarter is
  October 18 at 09:12.

Notes: the owner's estimate of "roughly 6:15 p.m." is close — the authoritative figure is **6:08 p.m.**
There are **25 minutes of usable twilight after sunset**. Starting the loop "just before sunset" would
put the group in a slot canyon in the dark, so the guide says to **start the hike about three hours
before sunset (around 3 p.m.)** to be back at camp near sunset, and to carry headlamps regardless.
The moon sets at about 11:15 p.m., so the darkest sky is late.

## 3. Safety items and their sources

**Heat.** BLM's own alert: bring "at least one liter per person," plus electrolytes; "Plan to start
your hike early, as temperatures rise quickly by early afternoon"; "always hike with a buddy and let
someone know when you expect to leave and return."
— https://www.blm.gov/visit/mecca-hills-wilderness (fetched 2026-09-17)
A 90°F normal high with no shade in a sand-floored canyon is the summer/early-fall risk; the guide
carries this as `seasons: ["summer","fall"]` for the trip-aware sorting and pushes the hike to the
cool end of the day. One liter is BLM's floor, not a target — the guide says a gallon per person per
day at camp, consistent with BLM's general desert guidance and with there being no water on site.

**Flash floods in slot canyons.** No BLM page for this unit states it explicitly, so the guide relies
on: freecampsites — "Do not visit the area if there is any threat of rain. This is a flash flood area.
The roads wash out and get closed"; hikingguy — check the weather, avoid thunderstorm or flash-flood
warnings, "Painted Canyon Road closes after rain"; and the documented precedent of Box Canyon Road
being destroyed by a storm on September 30, 2018 and reopening only after a $3 million repair on
May 3, 2019.
— https://freecampsites.net/?_escaped_fragment_=1834&query=sitedetails
— https://hikingguy.com/hiking-trails/palm-springs-hiking-trails/ladder-canyon-trail-painted-canyon-loop-hike/
— https://ukenreport.com/box-canyon-road-reopens/ (all fetched 2026-09-17)
Level: **critical**. Seasons: no restriction (desert storms here come in late summer monsoon and in
winter), so it renders for our dates.

**The ladders.** No official source describes, counts or vouches for them. hikingguy: the tallest is
"probably about 12-15 feet" and "sometimes a rung or two can be missing." AllTrails reviews through
early 2026 describe them as in place, with a February 15, 2026 report flagging the last ladder as
dangerous. Level: **important**. **UNVERIFIED** — the guide says the ladders are not maintained
infrastructure you can count on, that you should test each one, and that the route can be walked as an
out-and-back up Big Painted Canyon with no ladders at all.
— https://hikingguy.com/hiking-trails/palm-springs-hiking-trails/ladder-canyon-trail-painted-canyon-loop-hike/
— https://www.alltrails.com/trail/us/california/ladder-canyon-and-painted-canyon-trail--4 (fetched 2026-09-17)

**Getting lost in the maze.** Official and quotable: BLM calls the area "a badlands labyrinth, a
natural maze of small, narrow, steep canyons" and states there are **no designated trails**, with
"little to no cell service," and tells visitors to "download your map before arriving."
— https://www.blm.gov/visit/mecca-hills-wilderness (fetched 2026-09-17)
Level: **important**.

**No cell service / no help.** Same BLM alert. The nearest town is Mecca; the field office is in Palm
Springs, 760-833-7100, public room 8 a.m.–4 p.m. Monday–Friday.
— https://www.blm.gov/office/palm-springs-south-coast-field-office (fetched 2026-09-17)
Level: **important**.

**Driving sandy washes.** BLM calls Painted Canyon Road four-wheel-drive access; camper reports
describe deep sand and vehicles getting stuck. Level: **important**. See `access-road-camping.md` §4.

**Fire.** Seasonal California Desert District restrictions run April 15 – October 29, 2026; a free
California Campfire Permit is required year-round for any campfire, barbecue or gas stove on BLM land
outside a developed campground; during a Red Flag Warning campfires are suspended outright.
— https://www.blm.gov/announcement/blm-announces-seasonal-fire-restrictions-southern-california
— https://www.blm.gov/programs/fire/regional-info/california/fire-restrictions (fetched 2026-09-17)
Level: **important**. Seasons: summer and fall.

**Cold and wind at night.** A 56°F normal low is not dangerous, but campers report strong night wind in
the wash ("wind picks up significantly at night — tents need extra staking").
— https://thedyrt.com/camping/california/california-painted-canyon (fetched 2026-09-17)
Level: **note**. Seasons: fall, winter.

## 4. Things I deliberately did not claim

- **No dark-sky certification.** I found no International Dark-Sky Association designation for Mecca
  Hills, Painted Canyon or Chuckwalla National Monument. The guide describes the sky without claiming a
  rating.
- **No visitor numbers.** BLM publishes no visitation figure for this unit.
- **No drive time or mileage from Huntington Beach from an official source.** See `logistics.md`.
- **No air-quality figure for the Salton Sea.** The dust and odor are widely reported; I found no
  citable official advisory for our dates, so the guide keeps it qualitative.
- **No claim that the pit toilet exists.** Two secondary sources report one; no official source does.

## Addendum (2026-09-19): dates moved to Oct 24–25, 2026

Host moved the trip from Oct 17–18 to **Oct 24–25, 2026** (same Sat/Sun pattern). Re-fetched daylight
and moon data for the new date:

US Naval Observatory, coordinates 33.6190, -116.0000, time zone -7 (PDT), queried 2026-09-19:
https://aa.usno.navy.mil/api/rstt/oneday?date=2026-10-24&coords=33.6190,-116.0000&tz=-7

- Begin civil twilight **06:31**
- Sunrise **06:56**
- Solar noon 12:28
- **Sunset 18:00** (6:00 p.m. PDT)
- End civil twilight **18:25**
- Moon: waxing gibbous, **97% illuminated**; moonrise **16:58** (before sunset), moonset 05:19.
  Full Moon is the next night, Oct 25 at 21:12.

Notes: sunset moved 8 minutes earlier than the Oct 17 figure (negligible for planning — the "start
about 3 hours before sunset, ~3:30 p.m." guidance is unchanged). The moon phase changed materially:
Oct 17 was a 42% crescent that stayed out of the way until 11:15 p.m.; Oct 24 is a 97% gibbous that
rises at 4:58 p.m., before the hike even starts. Camp will be much brighter at night (helpful for
general camp life) but the Milky Way / dark-sky pitch is weaker on this date — flagged in the guide's
"also consider" note on the night sky, and worth knowing if photography is a priority.
Climate normals for Oct 24/25 (same NOAA station, 1991–2020 daily normals) are ~89.5°F / ~55°F,
about 1°F cooler than the Oct 17/18 figures already used — within the "about 90°F / about 56°F"
rounding already in the guide, so the weather text was not changed.
