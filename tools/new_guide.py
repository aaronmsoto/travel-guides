#!/usr/bin/env python3
"""Scaffold a new guide: folders + a guide.json skeleton with every required field marked TODO.
Usage: python3 tools/new_guide.py <slug> --name "Joshua Tree National Park" --state California \
         --start 2027-03-12 --end 2027-03-14 --base "Jumbo Rocks Campground" --kind campsite|town|lodge [--status potential]
Then fill guide.json (see tools/schema.md), source images (img/sources.json → fetch_images.py),
import photos (import_photos.py), validate, build."""
import sys, os, json, argparse
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap=argparse.ArgumentParser();ap.add_argument("slug");ap.add_argument("--name",required=True);ap.add_argument("--state",required=True)
ap.add_argument("--start",required=True);ap.add_argument("--end",required=True);ap.add_argument("--base",required=True)
ap.add_argument("--kind",choices=["campsite","town","lodge"],required=True);ap.add_argument("--status",default="potential",choices=["potential","planning","confirmed"])
ap.add_argument("--host",default=None)
a=ap.parse_args()
site=json.load(open(os.path.join(ROOT,"site.json"))) if os.path.exists(os.path.join(ROOT,"site.json")) else {}
host=a.host or site.get("host",{}).get("name","Aaron")
d=os.path.join(ROOT,"guides",a.slug)
if os.path.exists(os.path.join(d,"guide.json")): sys.exit(f"{d}/guide.json already exists")
for sub in ("img","src/_research","photos"): os.makedirs(os.path.join(d,sub),exist_ok=True)
T="TODO"
attr=lambda i:{"rank":i,"id":f"todo-{i}","name":T,"type":"hike","difficulty":"easy","stats":{"distance":T,"elevationGain":T,"time":T,"trailheadOrParking":T},"permit":"none","bestTime":T,"summary":T,"tips":[T,T,T],"image":f"todo-{i}.jpg","coords":[0,0],"sources":["https://TODO"]}
g={"schema":1,"slug":a.slug,"name":a.name,"shortName":a.name.split(" ")[0],"state":a.state,"tagline":T,"lastVerified":"TODO-YYYY-MM-DD",
 "hero":{"image":"hero.jpg","alt":T},
 "quickFacts":[{"label":"Entrance fee","value":T},{"label":"Best months","value":T},{"label":"Cell service","value":T},{"label":"Reservation needed?","value":T}],
 "overview":{"summary":T,"bestFor":[T],"dontMiss":[T,T,T],"alerts":[]},
 "seasons":[{"name":n,"months":T,"highs":T,"lows":T,"verdict":"Good","notes":T} for n in ("Spring","Summer","Fall","Winter")],
 "logistics":{"gettingThere":[{"from":"LA / OC area (our route)","how":T}],"gettingAround":T,"fees":T,"permits":[],"reservations":T,"services":T},
 "attractions":[attr(i) for i in range(1,11)],
 "alsoConsider":[],
 "stay":{"camping":[{"name":a.base if a.kind=="campsite" else T,"kind":"developed","where":T,"booking":"first-come","bookingDetail":T,"url":"https://TODO","ours":a.kind=="campsite"}],
         "lodging":[{"name":a.base if a.kind!="campsite" else T,"kind":"town","distance":T,"summary":T,"url":"https://TODO","ours":a.kind!="campsite"}]},
 "safety":[{"title":"Heat","level":"critical","seasons":["summer"],"body":T},{"title":"Cold nights","level":"important","seasons":["fall","winter"],"body":T}],
 "faq":[{"q":T,"a":T} for _ in range(5)],
 "sources":[{"title":T,"url":"https://TODO"}],
 "mapCenter":[0,0],"mapZoom":10,
 "theme":{"accent":"#a5533d","accentInk":"#7d3a29","accentSoft":"#f7e6e1","accentDark":"#e8906f","accentInkDark":"#f0aa90","accentSoftDark":"#3b241c"},
 "trip":{"title":f"{a.name.split(' National')[0]} — {T}","start":a.start,"end":a.end,"status":a.status,"host":host,"pitch":T,
   "base":{"name":a.base,"kind":a.kind,"coords":[0,0],"detail":T,"mapUrl":"https://www.google.com/maps/search/?api=1&query="+a.base.replace(" ","+"),"bookingNote":T},
   "arrival":T,"departure":T,
   "conditions":[{"label":"Weather","text":T},{"label":"Daylight","text":T},{"label":"Camp life: water, toilets, trash" if a.kind=="campsite" else "Where we sleep","text":T}],
   "bring":[T,T,T],"cost":[{"label":"Site / room","amount":"varies","note":T},{"label":"Entrance","amount":T}],
   "keyDates":[],"roster":[],
   "join":{"text":T,"steps":[f"<b>Coordinate with {host}</b> — which nights, how many people, and what you’re driving.",T,"Tap <b>Add to my picks</b> on what you’d want to do, then send the link."]},
   "faq":[{"q":"Roughly what will this cost me?","a":T},{"q":"Is it kid-friendly?","a":T},{"q":"What car do I need?","a":T}]}}
json.dump(g,open(os.path.join(d,"guide.json"),"w"),indent=1,ensure_ascii=False)
json.dump([],open(os.path.join(d,"img","sources.json"),"w"))
open(os.path.join(d,"src/_research/README.md"),"w").write(f"# Research notes — {a.name}\n\nOne file per theme (attractions.md, camping-lodging.md, seasons-safety.md, logistics.md).\nEvery fact: source URL + fetch date. Mark anything unverifiable UNVERIFIED.\n")
print(f"scaffolded guides/{a.slug}/ — fill guide.json (grep TODO), then img/sources.json → fetch_images.py, import_photos.py, validate.py, build.py")
