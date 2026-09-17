#!/usr/bin/env python3
"""Render guides/<slug>/guide.json -> guides/<slug>/index.html (self-contained CSS/JS, relative images),
guides/<slug>/trip.ics, and the root index.html landing page.
Usage: python3 tools/build.py [slug ...]   (no args = all)"""
import json, os, sys, html, re, datetime, math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED=os.path.join(ROOT,"shared"); GUIDES=os.environ.get("TG_GUIDES") or os.path.join(ROOT,"guides")
CSS=open(os.path.join(SHARED,"theme.css")).read(); JS=open(os.path.join(SHARED,"engine.js")).read()
SITE=json.load(open(os.path.join(ROOT,"site.json"))) if os.path.exists(os.path.join(ROOT,"site.json")) else {}
BASEURL=(SITE.get("baseUrl") or "").rstrip("/")
E=lambda s: html.escape(str(s),quote=True)
ALLOWED_TAGS={"b","i","a","br","em","strong","code"}
def H(s):
    """html: field — allow a tiny inline whitelist, escape everything else."""
    if s is None: return ""
    s=re.sub(r"^\s*html:\s*","",str(s))
    def fix(m):
        tag=m.group(2).lower()
        if tag not in ALLOWED_TAGS: return E(m.group(0))
        if tag=="a" and m.group(1)!="/":
            href=re.search(r'href="([^"]*)"',m.group(0))
            u=href.group(1) if href else "#"
            if not re.match(r"^(https?:|mailto:|sms:|#|/)",u): u="#"
            if u.startswith("#"): return f'<a href="{E(u)}">'
            return f'<a href="{E(u)}" target="_blank" rel="noopener">'
        return f"<{m.group(1)}{tag}>"
    return re.sub(r"<(/?)([a-zA-Z]+)[^<>]*>",fix,s)
def units(s): return f'<span data-units>{s}</span>'
def strip_tags(s): return re.sub(r"<[^>]+>","",str(s or ""))
def trunc(s,n=150):
    s=strip_tags(s).strip()
    if len(s)<=n: return s
    return s[:n].rsplit(" ",1)[0].rstrip(",;:—-")+"…"
DIFF_LABEL={"easy":"Easy","moderate":"Moderate","strenuous":"Strenuous","extreme":"Extreme"}
TYPE_LABEL={"hike":"Hike","viewpoint":"Viewpoint","scenic-drive":"Scenic drive","area":"Area","canyon":"Canyon","dunes":"Dunes","walk":"Walk"}
TYPE_PLURAL={"hike":"Hikes","viewpoint":"Viewpoints","scenic-drive":"Scenic drives","area":"Areas","canyon":"Canyons","dunes":"Dunes","walk":"Walks"}
PERMIT_LABEL={"none":"No permit","required":"Permit required","lottery":"Permit lottery"}
BOOK_LABEL={"reservable":"Reservable","first-come":"First-come, first-served","mixed":"Reservable + first-come","permit":"Permit"}
SECTIONS=[("trip","The Trip"),("overview","Overview"),("top10","Top 10"),("photos","Photos & Map"),("plan","Plan"),("stay","Stay"),("safety","Safety"),("faq","FAQ")]
MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTHS_LONG=["January","February","March","April","May","June","July","August","September","October","November","December"]
DOW=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
ISO=re.compile(r"^\d{4}-\d{2}-\d{2}$")
def pdate(s): return datetime.date.fromisoformat(s)
def season_of(d): return {12:"winter",1:"winter",2:"winter",3:"spring",4:"spring",5:"spring",6:"summer",7:"summer",8:"summer"}.get(d.month,"fall")
def fmt_range(a,b):
    a,b=pdate(a),pdate(b)
    if a.year!=b.year: return f"{DOW[a.weekday()]} {MONTHS[a.month-1]} {a.day}, {a.year} – {DOW[b.weekday()]} {MONTHS[b.month-1]} {b.day}, {b.year}"
    if a.month!=b.month: return f"{DOW[a.weekday()]} {MONTHS[a.month-1]} {a.day} – {DOW[b.weekday()]} {MONTHS[b.month-1]} {b.day}, {a.year}"
    return f"{DOW[a.weekday()]} {MONTHS[a.month-1]} {a.day} – {DOW[b.weekday()]} {b.day}, {a.year}"
def fmt_day(s): d=pdate(s); return f"{DOW[d.weekday()]} {MONTHS[d.month-1]} {d.day}"
def fmt_day_year(s): d=pdate(s); return f"{DOW[d.weekday()]} {MONTHS[d.month-1]} {d.day}, {d.year}"
def haversine_mi(a,b):
    R=3958.8;la1,lo1,la2,lo2=map(math.radians,[a[0],a[1],b[0],b[1]])
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def load(slug):
    p=os.path.join(GUIDES,slug,"guide.json")
    g=json.load(open(p))
    mp=os.path.join(GUIDES,slug,"img","manifest.json")
    g["_manifest"]=json.load(open(mp)) if os.path.exists(mp) else {}
    g["_dir"]=os.path.join(GUIDES,slug)
    pp=os.path.join(GUIDES,slug,"photos","photos.json")
    P=json.load(open(pp)) if os.path.exists(pp) else {"albums":[]}
    for alb in P.get("albums",[]): alb["items"]=[it for it in alb["items"] if not it.get("private")]
    g["_photos"]=P
    g["_url"]=f"{BASEURL}/guides/{slug}/" if BASEURL else ""
    return g

# ---------- images & credits ----------
def has(g,name): return bool(name) and os.path.exists(os.path.join(g["_dir"],"img",name))
def credit_text(g,file):
    m=g["_manifest"].get(file)
    if not m: return ""
    author=m.get("author","");lic=m.get("license","")
    author=re.sub(r"^(Zion|Death Valley) National Park \(|\)$","",author).replace("NPS Photo/","NPS / ").replace("NPS Photo","NPS")
    lic=re.sub(r"\s*\(NPS\)","",lic).replace("Public domain","PD")
    inner=f'{E(author)} · {E(lic)}' if author else E(lic)
    if m.get("sourceUrl"): inner=f'<a href="{E(m["sourceUrl"])}" target="_blank" rel="noopener">{inner}</a>'
    return f'Photo: {inner}'
def credit(g,file,cls="credit"):
    t=credit_text(g,file)
    return f'<p class="{cls}">{t}</p>' if t else ""
def img(g,file,alt,mode="full",lazy=True,sizes=None):
    """mode: full | mid (srcset thumb/mid/full) | thumb"""
    if not file: return '<div class="noimg" aria-hidden="true"></div>'
    if not has(g,file): return '<div class="noimg" aria-hidden="true"></div>'
    m=g["_manifest"].get(file,{})
    d=g["_dir"]
    thumb=os.path.exists(os.path.join(d,"img","thumb-"+file)); mid=os.path.exists(os.path.join(d,"img","mid-"+file))
    onerr=' onerror="this.replaceWith(Object.assign(document.createElement(\'div\'),{className:\'noimg\'}))"'
    if mode=="thumb" and thumb:
        return f'<img src="img/thumb-{E(file)}" alt="{E(alt)}"{" loading=lazy" if lazy else ""}{onerr}>'
    if mode=="mid" and (thumb or mid):
        ss=[]
        if thumb: ss.append(f"img/thumb-{file} 480w")
        if mid: ss.append(f"img/mid-{file} 960w")
        ss.append(f"img/{file} {m.get('width',1600)}w")
        src=f"img/mid-{file}" if mid else f"img/{file}"
        return f'<img src="{E(src)}" srcset="{E(", ".join(ss))}" sizes="{E(sizes or "(max-width:720px) 100vw, 320px")}" alt="{E(alt)}"{" loading=lazy" if lazy else ""}{onerr}>'
    wh=f' width="{m["width"]}" height="{m["height"]}"' if m.get("width") else ""
    return f'<img src="img/{E(file)}" alt="{E(alt)}"{wh}{" loading=lazy" if lazy else ""}{onerr}>'

# ---------- trip helpers ----------
def trip_season(g):
    t=g.get("trip"); return season_of(pdate(t["start"])) if t else None
def trip_dates_label(g):
    t=g["trip"];d=pdate(t["start"]);return f"{'early' if d.day<=10 else 'mid' if d.day<=20 else 'late'} {MONTHS_LONG[d.month-1]}"
def nights_label(t):
    n=(pdate(t["end"])-pdate(t["start"])).days
    return f'{n} night{"s" if n!=1 else ""}'+(f' · {E(t["nightsNote"])}' if t.get("nightsNote") else "")
def ics(g):
    t=g["trip"];s=pdate(t["start"]);e=pdate(t["end"])+datetime.timedelta(days=1)
    def esc(x): return str(x).replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
    uid=f"{g['slug']}-{t['start']}@travel-guides"
    desc=trunc(t.get("pitch",""),400)+(f"\\n{g['_url']}" if g["_url"] else "")
    loc=t["base"]["name"]+(f", {g['name']}" if g["name"] not in t["base"]["name"] else "")
    geo=f"GEO:{t['base']['coords'][0]};{t['base']['coords'][1]}\r\n" if t["base"].get("coords") else ""
    return ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//travel-guides//EN\r\nCALSCALE:GREGORIAN\r\nBEGIN:VEVENT\r\n"
            f"UID:{uid}\r\nDTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\r\n"
            f"DTSTART;VALUE=DATE:{s.strftime('%Y%m%d')}\r\nDTEND;VALUE=DATE:{e.strftime('%Y%m%d')}\r\n"
            f"SUMMARY:{esc(t['title'])}\r\nLOCATION:{esc(loc)}\r\n{geo}DESCRIPTION:{esc(desc)}\r\n"
            +(f"URL:{g['_url']}\r\n" if g["_url"] else "")+"END:VEVENT\r\nEND:VCALENDAR\r\n")

def trip_banner(g):
    t=g.get("trip")
    if not t: return ""
    return (f'<div class="tripbar" data-start="{E(t["start"])}" data-end="{E(t["end"])}"><span class="tb-dates">📅 {E(fmt_range(t["start"],t["end"]))}</span>'
            f'<span class="tb-nights">{nights_label(t)}</span><span class="tb-base">{"camping at" if t["base"].get("kind")=="campsite" else "base:"} <b>{E(t["base"]["name"])}</b></span>'
            f'<span class="tb-count" id="tripCountdown"></span><span class="spacer"></span><a class="btn primary" href="#trip/join">Join this trip →</a></div>')

def sec_trip(g):
    t=g.get("trip")
    if not t: return ""
    host=t.get("host",SITE.get("host",{}).get("name","the organizer"))
    out=[f'<h2 class="sech">{E(t["title"])}</h2><p class="byline">Hosted by {E(host)}</p><p class="lede">{H(t.get("pitch",""))}</p>']
    # facts row: When · Cost (or Capacity)
    facts=[f'<div class="card fact-card"><p class="eyebrow">When</p><p class="big">{E(fmt_range(t["start"],t["end"]))}</p><p class="linkrow">{nights_label(t)} · <span id="tripCountdown2"></span></p><p class="linkrow"><a class="btn small" href="trip.ics" download="{E(g["slug"])}-trip.ics">＋ Add to calendar</a></p></div>']
    if t.get("capacity"):
        c=t["capacity"];ppl=c.get("people");veh=c.get("vehicles");pt=c.get("peopleTaken");vt=c.get("vehiclesTaken")
        rows=""
        if ppl: rows+=f'<div class="meter"><div class="l">People</div><div class="bar"><div class="fill" style="width:{min(100,int(100*(pt or 0)/ppl))}%"></div></div><div class="v">{(str(pt)+" of ") if pt is not None else "up to "}{ppl}</div></div>'
        if veh: rows+=f'<div class="meter"><div class="l">Vehicles</div><div class="bar"><div class="fill" style="width:{min(100,int(100*(vt or 0)/veh))}%"></div></div><div class="v">{(str(vt)+" of ") if vt is not None else "up to "}{veh}</div></div>'
        facts.append(f'<div class="card fact-card"><p class="eyebrow">Room at camp</p>{rows}<p class="linkrow">{H(c.get("note",""))}</p></div>')
    if t.get("cost"):
        rows="".join(f'<li><span class="cl">{E(x["label"])}</span><span class="cv">{units(E(x.get("amount","varies")))}</span>'+(f'<small>{units(H(x["note"]))}</small>' if x.get("note") else "")+'</li>' for x in t["cost"])
        facts.append(f'<div class="card fact-card cost"><p class="eyebrow">Roughly what it costs</p><ul class="costs">{rows}</ul>'+(f'<p class="linkrow">{H(t.get("costNote",""))}</p>' if t.get("costNote") else "")+'</div>')
    out.append(f'<div class="grid3 tripfacts">{"".join(facts)}</div>')
    # base: full width
    b=t["base"]
    bimg=img(g,b.get("image"),b.get("imageAlt",b["name"]),mode="mid",sizes="(max-width:720px) 100vw, 360px") if b.get("image") and has(g,b["image"]) else ""
    out.append(f'<div class="card base"><div class="base-body"><p class="eyebrow">Home base · {E(b.get("kind","base"))}</p><h3>{E(b["name"])}</h3>{units(H(b.get("detail","")))}'
               +(f'<p class="linkrow"><a href="{E(b["mapUrl"])}" target="_blank" rel="noopener">Open in maps</a></p>' if b.get("mapUrl") else "")+'</div>'
               +(f'<div class="base-pic">{bimg}{credit(g,b.get("image"))}</div>' if bimg else "")+'</div>')
    if b.get("bookingNote"): out.append(f'<div class="callout info"><p><b>If you’re joining:</b> {units(H(b["bookingNote"]))}</p></div>')
    # alerts affecting the trip
    AL=[a for a in g.get("overview",{}).get("alerts",[]) if a.get("affectsTrip")]
    if AL:
        out.append('<div class="callout warn"><p class="eyebrow">Affects our dates · checked '+E(g.get("lastVerified",""))+'</p><ul>'+"".join(f'<li>{H(a["text"])}'+(f' <a href="{E(a["sourceUrl"])}" target="_blank" rel="noopener">source</a>' if a.get("sourceUrl") else "")+'</li>' for a in AL)+'</ul></div>')
    out.append('<div class="grid2">')
    if t.get("arrival"): out.append(f'<div class="card"><h3>Getting in</h3>{units(H(t["arrival"]))}</div>')
    if t.get("departure"): out.append(f'<div class="card"><h3>Getting out</h3>{units(H(t["departure"]))}</div>')
    out.append('</div>')
    if t.get("keyDates"):
        def kd(k): return E(fmt_day_year(k["date"])) if ISO.match(k["date"]) else E(k["date"])
        out.append('<div class="card keydates"><h3>Dates that matter</h3><ol class="tl">'+"".join(f'<li><span class="when">{kd(k)}</span><span>{units(H(k["what"]))}</span></li>' for k in t["keyDates"])+'</ol></div>')
    # tiles + picks
    A=sorted(g.get("attractions",[]),key=lambda a:a["rank"])
    if A:
        tiles="".join(f'<a class="tile" href="#top10/{E(a["id"])}">{img(g,a.get("image"),a.get("imageAlt",a["name"]),mode="thumb")}<span class="tile-b"><span class="tile-n">{a["rank"]}</span><b>{E(a["name"])}</b><small>{E(TYPE_LABEL.get(a.get("type",""),a.get("type","")))}{(" · "+DIFF_LABEL.get(a["difficulty"],a["difficulty"])) if a.get("difficulty") else ""}{(" · "+E(a["stats"]["distance"])) if a.get("stats",{}).get("distance") and len(a["stats"]["distance"])<=24 else ""}</small></span></a>' for a in A)
        out.append(f'<h2 class="mt">What we might do</h2><p class="lede">No fixed schedule — these are the {len(A)} things worth the trip, ranked by popularity. Tap one for the full card; <b>Add to my picks</b> builds a list you can send {E(host)}.</p><div class="tiles">{tiles}</div>')
        out.append(f'<div class="card" id="picks"><h3>My picks</h3><div id="picksBox" aria-live="polite"></div></div>')
    C=t.get("conditions")
    if isinstance(C,list):
        out.append(f'<h2 class="mt">What these dates mean</h2><div class="grid3 conds">'+"".join(f'<div class="card"><p class="eyebrow">{E(c["label"])}</p>{units(H(c["text"]))}</div>' for c in C)+'</div>')
    elif C: out.append(f'<div class="card"><h2>What these dates mean</h2>{units(H(C))}</div>')
    out.append('<div class="grid2">')
    if t.get("bring"): out.append('<div class="card"><h3>Bring</h3><p class="linkrow" id="packCount"></p><ul class="checks">'+"".join(f'<li><label><input type="checkbox" data-pack="{i}"> <span>{units(H(b))}</span></label></li>' for i,b in enumerate(t["bring"]))+'</ul></div>')
    if t.get("openQuestions"): out.append('<div class="card"><h3>Still deciding</h3><ul>'+"".join(f'<li>{H(q)}</li>' for q in t["openQuestions"])+'</ul></div>')
    out.append('</div>')
    if t.get("join"):
        j=t["join"]
        out.append(f'<div class="card join" id="join"><h2>Want to come?</h2>{H(j.get("text",""))}'+("<ol>"+"".join(f'<li>{H(x)}</li>' for x in j.get("steps",[]))+"</ol>" if j.get("steps") else "")
                   +f'<div class="cta"><button type="button" class="btn sharepage">Copy link to this trip</button><a class="btn" href="trip.ics" download="{E(g["slug"])}-trip.ics">Add to calendar</a></div><span class="visually-hidden" role="status" id="copyStatus"></span></div>')
        if t.get("roster"):
            out.append('<div class="card"><h3>Who’s in so far</h3><ul>'+"".join(f'<li><b>{E(r["name"])}</b>'+(f' — {E(r["nights"])}' if r.get("nights") else "")+'</li>' for r in t["roster"])+'</ul></div>')
    if t.get("faq"):
        out.append('<h2 class="mt">Questions people ask before saying yes</h2>'+"".join(f'<details><summary>{E(q["q"])}</summary><div class="body">{units(H(q["a"]))}</div></details>' for q in t["faq"]))
    return "".join(out)

def sec_overview(g):
    o=g["overview"];out=[]
    hero=g.get("hero",{})
    out.append(f'<div class="hero">{img(g,hero.get("image"),hero.get("alt",g["name"]),lazy=False)}<div class="over"><h2>{E(g["name"])}</h2><p>{E(g.get("tagline",""))}</p></div>{credit(g,hero.get("image"))}</div>')
    out.append('<div class="facts">'+"".join(f'<div class="fact"><div class="l">{E(f["label"])}</div><div class="v">{units(H(f["value"]))}</div>{("<div class=n>"+units(H(f["note"]))+"</div>") if f.get("note") else ""}</div>' for f in g.get("quickFacts",[]))+'</div>')
    AL=sorted(o.get("alerts",[]),key=lambda a: 0 if a.get("affectsTrip") else 1)
    if AL:
        worst="bad" if any(a.get("level")=="critical" for a in AL) else ("warn" if any(a.get("level")=="warn" for a in AL) else "info")
        items="".join(f'<li>{"<span class=tag>affects our dates</span> " if a.get("affectsTrip") else ""}{H(a["text"])}'+(f' <a href="{E(a["sourceUrl"])}" target="_blank" rel="noopener">source</a>' if a.get("sourceUrl") else "")+'</li>' for a in AL)
        out.append(f'<div class="callout {worst} alerts"><p class="eyebrow">Current conditions · checked {E(g.get("lastVerified",""))} · {len(AL)} item{"s" if len(AL)!=1 else ""} <span id="staleNote"></span></p><ul>{items}</ul></div>')
    out.append('<div class="grid2"><div class="card"><h2>Why go</h2>'+units(H(o.get("summary","")))+'<p class="eyebrow mt1">Best for</p><div class="chips">'+"".join(f'<span class="chip">{E(c)}</span>' for c in o.get("bestFor",[]))+'</div></div>')
    out.append('<div class="card"><h2>Don’t miss</h2><ol>'+"".join(f'<li>{units(H(d))}</li>' for d in o.get("dontMiss",[]))+'</ol><p class="linkrow">Full details in <a href="#top10">Top 10</a>.</p></div></div>')
    ts=trip_season(g)
    out.append('<h2 class="mt">When to go</h2><div class="grid3 seasons">'+"".join(
        f'<div class="card season{" ours" if ts and s["name"].lower()==ts else ""}"><span class="verdict {E(s.get("verdict","good").lower())}">{E(s.get("verdict",""))}</span><h3>{E(s["name"])}{" · our trip" if ts and s["name"].lower()==ts else ""}</h3><p class="temps">{E(s.get("months",""))}</p><p class="temps">{units("Highs "+E(s.get("highs",""))+" · Lows "+E(s.get("lows","")))}</p>{units(H(s.get("notes","")))}</div>' for s in g.get("seasons",[]))+'</div>')
    return "".join(out)

def attraction(g,a):
    d=a.get("difficulty","");t=a.get("type","");p=a.get("permit","none")
    st=a.get("stats",{})
    stats="".join(f'<div class="stat"><div class="l">{E(l)}</div><div class="v">{units(E(st[k]))}</div></div>' for k,l in [("distance","Distance"),("elevationGain","Elevation gain"),("time","Time"),("trailheadOrParking","Start / parking")] if st.get(k))
    base=g.get("trip",{}).get("base",{}).get("coords")
    if base and a.get("coords"):
        mi=haversine_mi(base,a["coords"]);stats+=f'<div class="stat"><div class="l">From our base</div><div class="v">{units(f"≈ {mi:.0f} mi" if mi>=2 else f"≈ {mi:.1f} mi")}<small> straight line</small></div></div>'
    meta=f'<span class="tag type">{E(TYPE_LABEL.get(t,t))}</span>'
    if d: meta+=f'<span class="tag {E(d)}">{E(DIFF_LABEL.get(d,d))}</span>'
    meta+=f'<span class="tag {"permit" if p!="none" else ""}">{E(PERMIT_LABEL.get(p,p))}</span>'
    best=f'<p class="best"><b>Best time:</b> {E(a["bestTime"])}</p>' if a.get("bestTime") else ""
    tips=("<details class=\"tips\"><summary>Good to know</summary><div class=\"body\"><ul>"+"".join(f'<li>{units(H(x))}</li>' for x in a["tips"])+"</ul></div></details>") if a.get("tips") else ""
    permit=f'<div class="callout info compact"><p><b>{E(PERMIT_LABEL.get(p,p))}.</b> {units(H(a.get("permitNote","")))}</p></div>' if p!="none" and a.get("permitNote") else ""
    season=f'<p class="linkrow">Season note: {units(H(a["seasonNote"]))}</p>' if a.get("seasonNote") else ""
    acc=f'<p class="linkrow">Accessibility: {H(a["accessibility"])}</p>' if a.get("accessibility") else ""
    def host(u): return re.sub(r"^https?://(www\.)?","",u).split("/")[0]
    srcs=" · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(host(u))}<span class="visually-hidden"> — source for {E(a["name"])}</span></a>' for u in a.get("sources",[])[:2])
    cred=credit_text(g,a.get("image"))
    return (f'<article class="card attr" id="{E(a["id"])}" data-type="{E(t)}" data-type-label="{E(TYPE_LABEL.get(t,t))}" data-difficulty="{E(d)}" data-difficulty-label="{E(DIFF_LABEL.get(d,d))}" data-permit="{E(p)}" data-name="{E(a["name"])}" data-time="{E(st.get("time",""))}">'
            f'<div class="pic">{img(g,a.get("image"),a.get("imageAlt",a["name"]),mode="mid",sizes="(max-width:720px) 100vw, 300px")}<span class="rank" aria-label="Rank {a["rank"]}">{a["rank"]}</span></div>'
            f'<div class="body"><div class="head"><h3>{E(a["name"])}</h3></div><div class="meta">{meta}</div>'
            f'<div class="summary">{units(H(a.get("summary","")))}</div><div class="stats">{stats}</div>{best}{permit}{tips}{season}{acc}'
            f'<div class="foot"><button type="button" class="btn addtrip" aria-pressed="false">+ Add to my picks</button><button type="button" class="btn ghost copylink" data-id="{E(a["id"])}">Share</button><span class="spacer"></span><span class="src">Sources: {srcs}</span>'+(f'<span class="credit">{cred}</span>' if cred else "")+'</div></div></article>')

def sec_top10(g):
    types=[];seen=set()
    for a in g["attractions"]:
        if a.get("type") and a["type"] not in seen: seen.add(a["type"]);types.append(a["type"])
    fb='<div class="filters" id="filters" role="group" aria-label="Filter attractions"><button type="button" class="fbtn on" data-ftype="all" aria-pressed="true">All</button>'+"".join(f'<button type="button" class="fbtn" data-ftype="{E(t)}" aria-pressed="false">{E(TYPE_PLURAL.get(t,TYPE_LABEL.get(t,t)))}</button>' for t in types)
    fb+='<select id="fdiff" aria-label="Difficulty"><option value="all">Any difficulty</option>'+"".join(f'<option value="{k}">{v}</option>' for k,v in DIFF_LABEL.items() if any(a.get("difficulty")==k for a in g["attractions"]))+'</select>'
    fb+='<button type="button" class="fbtn" data-ftoggle="permit" aria-pressed="false">No permit needed</button><button type="button" class="fbtn" data-ftoggle="trip" aria-pressed="false">My picks only</button><span class="spacer"></span><span class="count" id="fcount" role="status" aria-live="polite"></span><button type="button" class="btn ghost" id="fclear">Reset</button></div>'
    cards="".join(attraction(g,a) for a in sorted(g["attractions"],key=lambda a:a["rank"]))
    none='<p id="fnone" class="card" role="status" hidden>Nothing matches those filters. <button type="button" class="btn ghost" onclick="document.getElementById(\'fclear\').click()">Reset filters</button></p>'
    also=""
    if g.get("alsoConsider"):
        items=""
        for x in g["alsoConsider"]:
            pic=img(g,x.get("image"),x.get("name",""),mode="thumb") if x.get("image") and has(g,x["image"]) else ""
            items+=f'<li>{("<span class=also-pic>"+pic+"</span>") if pic else ""}<span><b>{E(x["name"])}</b> — {units(H(x.get("why","")))}'+(f' <a href="{E(x["url"])}" target="_blank" rel="noopener">Details<span class="visually-hidden"> about {E(x["name"])}</span></a>' if x.get("url") else "")+(f'<span class="credit">{credit_text(g,x.get("image"))}</span>' if x.get("image") and credit_text(g,x.get("image")) else "")+'</span></li>'
        also=f'<div class="card also"><h2>Also consider</h2><ul>{items}</ul></div>'
    return f'<h2 class="sech">Top 10 natural attractions</h2><p class="lede">Ranked by popularity. Distances and times are official park figures where available. Tap <b>Add to my picks</b> to build a list you can send the host.</p>{fb}{cards}{none}{also}'

def mapdata(g):
    pts=[]
    for a in g.get("attractions",[]):
        if a.get("coords"): pts.append({"kind":"attraction","id":a["id"],"name":a["name"],"lat":a["coords"][0],"lng":a["coords"][1],"rank":a["rank"],"thumb":("img/thumb-"+a["image"]) if a.get("image") and os.path.exists(os.path.join(g["_dir"],"img","thumb-"+a["image"])) else None})
    t=g.get("trip")
    if t and t.get("base",{}).get("coords"): pts.append({"kind":"base","id":"base","name":"Home base: "+t["base"]["name"],"lat":t["base"]["coords"][0],"lng":t["base"]["coords"][1]})
    byid={p["id"]:p for p in pts}
    names={a["id"]:a["name"] for a in g.get("attractions",[])}
    if t: names["base"]="Home base: "+t["base"]["name"]
    photos=[]
    for alb in g["_photos"].get("albums",[]):
        for it in alb["items"]:
            lat,lng=it.get("lat"),it.get("lng"); approx=False
            if (lat is None or lng is None) and it.get("place") in byid: lat,lng=byid[it["place"]]["lat"],byid[it["place"]]["lng"]; approx=True
            photos.append({"file":"photos/"+it["file"],"thumb":"photos/thumb-"+it["file"],"w":it.get("w"),"h":it.get("h"),"caption":it.get("caption",""),"taken":it.get("taken"),"album":alb["title"],"credit":alb.get("credit",""),"place":it.get("place"),"placeName":names.get(it.get("place")),"lat":lat,"lng":lng,"approx":approx})
    return {"points":pts,"photos":photos,"center":g.get("mapCenter"),"zoom":g.get("mapZoom",10)}

def sec_photos(g):
    P=g["_photos"].get("albums",[])
    n=sum(len(a["items"]) for a in P)
    t=g.get("trip");ts=trip_season(g)
    out=[f'<h2 class="sech">Photos &amp; map</h2>']
    if n:
        albs=", ".join(E(a["title"]) for a in P)
        same=all(any(k in a["title"].lower() for k in [ts or "", MONTHS_LONG[pdate(t["start"]).month-1].lower() if t else ""]) for a in P) if t else True
        if same: out.append(f'<p class="lede">{n} photo{"s" if n!=1 else ""} from {albs} — same season as our trip, so this is close to what it will look like. Switch to the map to see where each one was taken alongside the Top 10.</p>')
        else: out.append(f'<p class="lede">{n} photo{"s" if n!=1 else ""} from {albs} — the place, not the season: our trip is in {E(trip_dates_label(g))}, so expect it colder, quieter, and with lower light. Switch to the map to see where each one was taken alongside the Top 10.</p>')
    else:
        out.append('<p class="lede">No photos from past trips yet — the map still shows where the Top 10 and our home base are.</p>')
    out.append('<div class="viewsw" role="group" aria-label="View"><button type="button" class="fbtn on" data-view="grid" aria-pressed="true">Grid</button><button type="button" class="fbtn" data-view="map" aria-pressed="false">Map</button></div>')
    grid=[];idx=0
    for alb in P:
        grid.append(f'<h3 class="albh">{E(alb["title"])}'+(f' <span class="credit inl">photos: {E(alb["credit"])}</span>' if alb.get("credit") else "")+'</h3><div class="pgrid">')
        for it in alb["items"]:
            grid.append(f'<button type="button" class="ph" data-i="{idx}" aria-label="Open photo: {E(it.get("caption") or it["file"])}"><img src="photos/thumb-{E(it["file"])}" alt="{E(it.get("caption",""))}" loading="lazy" width="480" height="{int(480*it["h"]/it["w"]) if it.get("w") else 360}"><span class="cap">{E(it.get("caption",""))}</span></button>')
            idx+=1
        grid.append('</div>')
    out.append(f'<div id="pgridwrap">{"".join(grid) if n else ""}</div>')
    out.append('<div id="mapwrap" hidden><ul class="chips legend" aria-label="Map legend"><li><span class="pin-key accent">1</span> Top 10, by rank</li><li><span class="pin-key good">📷</span> our photos</li><li><span class="pin-key info">⌂</span> home base</li></ul><div id="map" class="map" role="region" aria-label="Map of photos and attractions"></div><p class="credit">Map tiles © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors, loaded only when you open the map (needs a connection). Photo pins marked “near” are placed at the attraction, not from GPS. Scroll the page normally; use the +/− buttons or pinch to zoom.</p></div>')
    mdj=json.dumps(mapdata(g)).replace("</","<\\/")
    out.append(f'<script id="mapdata" type="application/json">{mdj}</script>')
    out.append('<dialog id="lightbox" class="lightbox" aria-label="Photo viewer"><button type="button" class="lb-x" data-lb="close" aria-label="Close">×</button><button type="button" class="lb-nav lb-prev" data-lb="prev" aria-label="Previous photo">‹</button><figure><img alt=""><figcaption><span class="lb-cap"></span><span class="lb-meta"></span></figcaption></figure><button type="button" class="lb-nav lb-next" data-lb="next" aria-label="Next photo">›</button></dialog>')
    return "".join(out)

def sec_plan(g):
    L=g["logistics"];out=['<h2 class="sech">Plan your visit</h2>']
    if L.get("gettingThere"):
        out.append('<div class="card"><h2>Getting there</h2><div class="tablewrap"><table><tr><th>From</th><th>Route &amp; time</th><th>Miles</th></tr>'+"".join(f'<tr><td><b>{E(r["from"])}</b></td><td>{units(H(r["how"]))}</td><td>{units(E(str(r.get("miles",""))+" mi") if r.get("miles") else "")}</td></tr>' for r in L["gettingThere"])+'</table></div></div>')
    out.append('<div class="grid2">')
    for k,t in [("gettingAround","Getting around"),("fees","Entrance fees & passes"),("reservations","Reservations & timed entry"),("services","Fuel, food, water, cell")]:
        if L.get(k): out.append(f'<div class="card"><h2>{t}</h2>{units(H(L[k]))}</div>')
    out.append('</div>')
    if L.get("permits"):
        out.append('<h2 class="mt">Permits</h2><div class="grid2">'+"".join(f'<div class="card"><p class="eyebrow">{"Required" if p.get("required") else "Optional / special"}</p><h3>{E(p["name"])}</h3>{units(H(p.get("how","")))}'+(f'<p class="linkrow"><a href="{E(p["url"])}" target="_blank" rel="noopener">Official page<span class="visually-hidden"> for {E(p["name"])}</span></a></p>' if p.get("url") else "")+'</div>' for p in L["permits"])+'</div>')
    return "".join(out)

def stay_card(g,c,kind):
    pic=img(g,c.get("image"),c.get("imageAlt",c["name"]),mode="mid",sizes="(max-width:720px) 100vw, 280px") if c.get("image") and has(g,c["image"]) else ""
    if kind=="camping":
        b=c.get("booking","")
        kv="".join(f'<div><div class="l">{l}</div><div class="v">{units(H(c[k]))}</div></div>' for k,l in [("sites","Sites"),("cost","Cost"),("season","Season"),("goodFor","Good for")] if c.get(k))
        am=("<div class=\"amen\">"+"".join(f'<span>{E(x)}</span>' for x in c["amenities"])+"</div>") if c.get("amenities") else ""
        body=(f'<div class="meta"><span class="tag {E(b)}">{E(BOOK_LABEL.get(b,b))}</span> <span class="tag">{E(c.get("kind",""))}</span></div><h3>{E(c["name"])}</h3><p class="where">{units(H(c.get("where","")))}</p><div class="kv">{kv}</div>{am}'
              f'<details class="how"><summary>How to book</summary><div class="body">{units(H(c.get("bookingDetail","")))}'+(f'<p>{units(H(c["notes"]))}</p>' if c.get("notes") else "")+'</div></details>'
              +(f'<p class="linkrow"><a href="{E(c["url"])}" target="_blank" rel="noopener">Official page / booking<span class="visually-hidden"> for {E(c["name"])}</span></a></p>' if c.get("url") else ""))
    else:
        ex=("<p class=\"linkrow\">Examples: "+", ".join(E(x) for x in c["examples"])+"</p>") if c.get("examples") else ""
        body=(f'<div class="meta"><span class="tag">{E(c.get("kind",""))}</span>'+(f'<span class="tag">{E(c["priceBand"])}</span>' if c.get("priceBand") else "")+f'</div><h3>{E(c["name"])}</h3><p class="where">{units(H(c.get("distance","")))}</p>{units(H(c.get("summary","")))}{ex}'
              +(f'<p class="linkrow"><a href="{E(c["url"])}" target="_blank" rel="noopener">Website<span class="visually-hidden"> for {E(c["name"])}</span></a></p>' if c.get("url") else ""))
    ours=' ours' if c.get("ours") else ''
    flag='<p class="eyebrow ours-flag">Where we’re staying</p>' if c.get("ours") else ''
    return f'<div class="card stay{ours}">{flag}<div class="stay-grid">{("<div class=stay-pic>"+pic+credit(g,c.get("image"))+"</div>") if pic else ""}<div>{body}</div></div></div>'

def sec_stay(g):
    S=g["stay"];out=['<h2 class="sech">Where to stay</h2><p class="lede">Camping inside the park and lodging just outside it. Booking rules change; each card links to the official page and says exactly how it’s booked.</p>']
    order=[("lodging","Lodging"),("camping","Camping")] if g.get("trip",{}).get("base",{}).get("kind")=="town" else [("camping","Camping"),("lodging","Lodging")]
    for k,title in order:
        if not S.get(k): continue
        items=sorted(S[k],key=lambda c: 0 if c.get("ours") else 1)
        out.append(f'<h2 class="mt">{title}</h2>'+"".join(stay_card(g,c,k) for c in items))
    return "".join(out)

def sec_safety(g):
    ts=trip_season(g);S=g.get("safety",[])
    def card(s): return f'<div class="card safety {E(s.get("level","note"))}"><p class="eyebrow">{E(s.get("level","note"))}</p><h3>{E(s["title"])}</h3>{units(H(s["body"]))}</div>'
    if ts and any(s.get("seasons") for s in S):
        ours=[s for s in S if not s.get("seasons") or ts in s["seasons"]]
        other=[s for s in S if s.get("seasons") and ts not in s["seasons"]]
        lvl={"critical":0,"important":1,"note":2}
        ours.sort(key=lambda s: lvl.get(s.get("level","note"),3))
        return (f'<h2 class="sech">Safety &amp; know-before-you-go</h2><p class="lede">The handful of things that actually hurt people here, with the specific rule that prevents each one — sorted for <b>our dates ({E(trip_dates_label(g))})</b>.</p>'
                f'<h2 class="mt">For our dates</h2><div class="grid2">{"".join(card(s) for s in ours)}</div>'
                +(f'<details class="other"><summary>Risks in other seasons ({len(other)})</summary><div class="body"><div class="grid2">{"".join(card(s) for s in other)}</div></div></details>' if other else ""))
    return '<h2 class="sech">Safety &amp; know-before-you-go</h2><p class="lede">The handful of things that actually hurt people here, with the specific rule that prevents each one.</p><div class="grid2">'+"".join(card(s) for s in S)+'</div>'

def sec_itin(g):
    out=['<h2 class="sech">Itineraries</h2><p class="lede">Generic plans for any time of year — useful if you can only come for a day. Our own trip has no fixed schedule; see <a href="#trip">The Trip</a> and add your picks.</p>']
    for it in g.get("itineraries",[]):
        out.append(f'<div class="card"><p class="eyebrow">{it.get("days",1)} day{"s" if it.get("days",1)!=1 else ""} · any season</p><h2>{E(it["title"])}</h2>'+(f'<p>{H(it["intro"])}</p>' if it.get("intro") else "")+'<ol class="tl">'+"".join(f'<li><span class="when">{E(p["when"])}</span><span>{units(H(p["what"]))}</span></li>' for p in it["plan"])+'</ol></div>')
    return "".join(out)

def sec_faq(g):
    return '<h2 class="sech">Frequently asked</h2><p class="lede">About the park in general. Trip questions are on <a href="#trip">The Trip</a>.</p>'+"".join(f'<details><summary>{E(q["q"])}</summary><div class="body">{units(H(q["a"]))}</div></details>' for q in g.get("faq",[]))

def footnav(g,others):
    items="".join(f'<li><a href="../{E(o["slug"])}/index.html#trip">{E(o["name"])}{(" — "+E(fmt_range(o["trip"]["start"],o["trip"]["end"]))) if o.get("trip") else ""} →</a></li>' for o in others)
    return f'<nav class="footnav" aria-label="More"><a class="btn" href="../../index.html">← All trips</a>'+(f'<div><p class="eyebrow">Other trips</p><ul>{items}</ul></div>' if items else "")+'</nav>'
def footer(g,others=()):
    srcs="".join(f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["title"])}</a></li>' for s in g.get("sources",[]))
    creds=[]
    for f,m in sorted(g["_manifest"].items()):
        if f.startswith(("thumb-","mid-")): continue
        inner=f'{E(m.get("title",f))} — {E(m.get("author",""))}, {E(m.get("license",""))}'
        if m.get("sourceUrl"): inner=f'<a href="{E(m["sourceUrl"])}" target="_blank" rel="noopener">{inner}</a>'
        creds.append(f'<li>{inner}</li>')
    pc="".join(f'<li>{E(a["title"])} album — {E(a.get("credit","personal photos"))}, used with permission</li>' for a in g["_photos"].get("albums",[]) if a["items"])
    return (f'<footer class="site">{footnav(g,others)}<p><b>Last verified {E(g.get("lastVerified",""))}.</b> Conditions, fees, and reservation rules change — always confirm on the official pages below before you go. This guide is independent and not affiliated with the National Park Service.</p>'
            f'<h2>Sources</h2><ul>{srcs}</ul><h2>Photo credits</h2><ul>{"".join(creds)}{pc}</ul></footer>')

def head_meta(g):
    t=g.get("trip")
    if t:
        title=f'{t["title"]} — you’re invited'
        desc=trunc(t.get("pitch",""),155)
    else:
        title=f'{g["name"]} travel guide'
        desc=trunc(g["overview"].get("summary",""),155)
    hero=g.get("hero",{}).get("image","")
    m=g["_manifest"].get(hero,{})
    og=[f'<meta property="og:title" content="{E(title)}">',f'<meta property="og:description" content="{E(desc)}">',f'<meta property="og:type" content="website">',f'<meta property="og:site_name" content="{E(SITE.get("title","Travel guides"))}">',f'<meta name="twitter:card" content="summary_large_image">']
    if hero:
        u=(g["_url"]+"img/"+hero) if g["_url"] else "img/"+hero
        og.append(f'<meta property="og:image" content="{E(u)}">')
        if m.get("width"): og.append(f'<meta property="og:image:width" content="{m["width"]}"><meta property="og:image:height" content="{m["height"]}">')
    if g["_url"]: og.append(f'<meta property="og:url" content="{E(g["_url"])}"><link rel="canonical" href="{E(g["_url"])}">')
    if SITE.get("noindex"): og.append('<meta name="robots" content="noindex">')
    return f'<title>{E(title)}</title>\n<meta name="description" content="{E(desc)}">\n'+"\n".join(og)

def render_guide(slug,others=()):
    g=load(slug)
    theme=g.get("theme",{})
    extra=""
    if theme.get("accent"): extra+=f':root{{--accent:{theme["accent"]};--accent-ink:{theme.get("accentInk",theme["accent"])};--accent-soft:{theme.get("accentSoft","#f6e6dd")}}}'
    if theme.get("accentDark"): extra+=f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--accent:{theme["accentDark"]};--accent-ink:{theme.get("accentInkDark",theme["accentDark"])};--accent-soft:{theme.get("accentSoftDark","#3a2418")}}}}}:root[data-theme="dark"]{{--accent:{theme["accentDark"]};--accent-ink:{theme.get("accentInkDark",theme["accentDark"])};--accent-soft:{theme.get("accentSoftDark","#3a2418")}}}'
    body={"trip":sec_trip,"overview":sec_overview,"top10":sec_top10,"photos":sec_photos,"plan":sec_plan,"stay":sec_stay,"safety":sec_safety,"faq":sec_faq}
    S=[x for x in SECTIONS if x[0]!="trip" or g.get("trip")]
    secs="".join(f'<section class="sec" id="{sid}" data-title="{t}" aria-labelledby="tab-{sid}">{body[sid](g)}</section>\n' for sid,t in S)
    tabs="".join(f'<a href="#{sid}" id="tab-{sid}" data-sec="{sid}">{t}</a>' for sid,t in S)
    t=g.get("trip");host=(t or {}).get("host",SITE.get("host",{}).get("name",""))
    rsvp=json.dumps({"title":t["title"],"host":host,"url":g["_url"] or None}) if t else "null"
    rsvpj=rsvp.replace("</","<\\/")
    page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{head_meta(g)}
<style>{CSS}{extra}</style>
</head><body data-slug="{E(slug)}" data-name="{E(g["name"])}" data-verified="{E(g.get("lastVerified",""))}">
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="masthead"><div class="titles"><p class="crumbs"><a class="homelink" href="../../index.html">← All trips</a><span class="sep">{E(g.get("state",""))}</span></p><h1>{E(g["name"])}</h1><p class="sub">{E(g.get("tagline",""))}</p></div>
<div class="tools">{('<a class="iconbtn" href="#trip/picks" title="The attractions you picked">My picks <span class="cnt" id="tripCount" hidden>0</span></a>') if t else ''}<button type="button" class="iconbtn" id="unitBtn" aria-pressed="false"><span class="visually-hidden">Units: </span>mi / °F</button><button type="button" class="iconbtn" id="themeBtn">☾ Dark</button></div></div>
<nav class="tabs" aria-label="Sections">{tabs}</nav></header>
<main id="main">{trip_banner(g)}
{secs}</main>
{footer(g,others)}
<script id="rsvpdata" type="application/json">{rsvpj}</script>
<script>{JS}</script>
</body></html>'''
    out=os.path.join(GUIDES,slug,"index.html")
    open(out,"w").write(page)
    if t: open(os.path.join(GUIDES,slug,"trip.ics"),"w",newline="").write(ics(g))
    print(f"built guides/{slug}/index.html  {os.path.getsize(out)//1024} KB  ({len(g['attractions'])} attractions, {len(g['_manifest'])} images, {sum(len(a['items']) for a in g['_photos']['albums'])} photos)")
    return g

def render_landing(guides):
    host=SITE.get("host",{}).get("name","")
    def key(g): return (0,g["trip"]["start"]) if g.get("trip") else (1,g["name"])
    cards=""
    for g in sorted(guides,key=key):
        hero=g.get("hero",{}).get("image","")
        t=g.get("trip")
        pic=f'<img src="guides/{E(g["slug"])}/img/{E(hero)}" alt="{E(g.get("hero",{}).get("alt",g["name"]))}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement(\'div\'),{{className:\'noimg\'}}))">' if hero and has(g,hero) else '<div class="noimg"></div>'
        if t:
            meta=f'<p class="gdates">📅 {E(fmt_range(t["start"],t["end"]))} <span class="tb-count" data-start="{E(t["start"])}" data-end="{E(t["end"])}"></span></p><p>{nights_label(t)} · {"camping at" if t["base"].get("kind")=="campsite" else "base:"} {E(t["base"]["name"])}</p>'
            cta=f'<span class="btn primary">See the plan →</span>'
            title=E(t["title"])
        else:
            meta=f'<p>{E(g.get("tagline",""))}</p>';cta='<span class="btn">Open the guide →</span>';title=E(g["name"])
        cards+=f'<a class="gcard" href="guides/{E(g["slug"])}/index.html#trip">{pic}<div class="b"><p class="eyebrow">{E(g["name"])} · {E(g.get("state",""))}</p><h2>{title}</h2>{meta}<p class="linkrow">{E(trunc(t.get("pitch","") if t else g.get("tagline",""),140))}</p><p class="cta">{cta}</p></div></a>'
    n=sum(1 for g in guides if g.get("trip"))
    title=SITE.get("title","Travel guides");sub=SITE.get("tagline","")
    ogimg=""
    first=sorted(guides,key=key)[0] if guides else None
    if first and BASEURL and first.get("hero",{}).get("image"): ogimg=f'<meta property="og:image" content="{E(BASEURL)}/guides/{E(first["slug"])}/img/{E(first["hero"]["image"])}">'
    page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(sub)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(sub)}"><meta property="og:type" content="website">{ogimg}{f'<meta property="og:url" content="{E(BASEURL)}/">' if BASEURL else ''}<meta name="twitter:card" content="summary_large_image">{'<meta name="robots" content="noindex">' if SITE.get("noindex") else ''}
<style>{CSS}</style></head><body data-slug="landing" data-name="{E(title)}">
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="masthead"><div class="titles"><h1>{E(title)}</h1><p class="sub">{E(sub)}{(" · hosted by "+E(host)) if host else ""}</p></div><div class="tools"><button type="button" class="iconbtn" id="themeBtn">☾ Dark</button></div></div></header>
<main id="main"><div class="guides">{cards}</div>
<p class="linkrow">Every fact in these guides links to its official source, and each guide’s footer shows when it was last checked.</p></main>
<script>{JS}</script></body></html>'''
    open(os.path.join(ROOT,"index.html"),"w").write(page)
    print("built index.html")

if __name__=="__main__":
    slugs=sys.argv[1:] or sorted(d for d in os.listdir(GUIDES) if os.path.exists(os.path.join(GUIDES,d,"guide.json")))
    allg=[load(d) for d in sorted(os.listdir(GUIDES)) if os.path.exists(os.path.join(GUIDES,d,"guide.json"))]
    gs=[render_guide(s,[o for o in allg if o["slug"]!=s]) for s in slugs]
    render_landing(allg)
