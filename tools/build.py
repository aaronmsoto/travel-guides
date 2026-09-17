#!/usr/bin/env python3
"""Render guides/<slug>/guide.json -> guides/<slug>/index.html (self-contained CSS/JS, relative images)
and the root index.html landing page.   Usage: python3 tools/build.py [slug ...]   (no args = all)"""
import json, os, sys, html, re, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED=os.path.join(ROOT,"shared"); GUIDES=os.environ.get("TG_GUIDES") or os.path.join(ROOT,"guides")
CSS=open(os.path.join(SHARED,"theme.css")).read(); JS=open(os.path.join(SHARED,"engine.js")).read()
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
            if not re.match(r"^(https?:|mailto:|#|/)",u): u="#"
            return f'<a href="{E(u)}" target="_blank" rel="noopener">'
        return f"<{m.group(1)}{tag}>"
    return re.sub(r"<(/?)([a-zA-Z]+)[^<>]*>",fix,s)
def units(s): return f'<span data-units>{s}</span>'
DIFF_LABEL={"easy":"Easy","moderate":"Moderate","strenuous":"Strenuous","extreme":"Extreme"}
TYPE_LABEL={"hike":"Hike","viewpoint":"Viewpoint","scenic-drive":"Scenic drive","area":"Area","canyon":"Canyon","dunes":"Dunes","walk":"Walk"}
PERMIT_LABEL={"none":"No permit","required":"Permit required","lottery":"Permit lottery"}
BOOK_LABEL={"reservable":"Reservable","first-come":"First-come, first-served","mixed":"Reservable + first-come","permit":"Permit"}
SECTIONS=[("overview","Overview"),("top10","Top 10"),("plan","Plan"),("stay","Stay"),("safety","Safety"),("itineraries","Itineraries"),("faq","FAQ")]

def load(slug):
    p=os.path.join(GUIDES,slug,"guide.json")
    g=json.load(open(p))
    mp=os.path.join(GUIDES,slug,"img","manifest.json")
    g["_manifest"]=json.load(open(mp)) if os.path.exists(mp) else {}
    g["_dir"]=os.path.join(GUIDES,slug)
    return g

def credit(g,file,cls="credit"):
    m=g["_manifest"].get(file)
    if not m: return ""
    lic=m.get("license","");author=m.get("author","")
    if cls=="credit":
        author=re.sub(r"^Zion National Park \(|^Death Valley National Park \(|\)$","",author).replace("NPS Photo/","NPS / ").replace("NPS Photo","NPS")
        lic=re.sub(r"\s*\(NPS\)","",lic).replace("Public domain","PD")
    inner=f'{E(author)} · {E(lic)}' if author else E(lic)
    if m.get("sourceUrl"): inner=f'<a href="{E(m["sourceUrl"])}" target="_blank" rel="noopener">{inner}</a>'
    return f'<p class="{cls}">Photo: {inner}</p>'
def img(g,file,alt,thumb=False,lazy=True,cls=""):
    if not file: return ""
    p=os.path.join(g["_dir"],"img",file)
    if not os.path.exists(p): return f'<div class="noimg" aria-hidden="true"></div>'
    src="img/"+("thumb-"+file if thumb and os.path.exists(os.path.join(g["_dir"],"img","thumb-"+file)) else file)
    m=g["_manifest"].get(file,{})
    wh=f' width="{m["width"]}" height="{m["height"]}"' if m.get("width") and not thumb else ""
    full=f' data-full="img/{E(file)}"' if thumb else ""
    return f'<img src="{E(src)}" alt="{E(alt)}"{wh}{full}{" loading=lazy" if lazy else ""}{(" class="+chr(34)+cls+chr(34)) if cls else ""}>'

def sec_overview(g):
    o=g["overview"];out=[]
    hero=g.get("hero",{})
    out.append(f'<div class="hero">{img(g,hero.get("image"),hero.get("alt",g["name"]),lazy=False)}<div class="over"><h2>{E(g["name"])}</h2><p>{E(g.get("tagline",""))}</p></div>{credit(g,hero.get("image"))}</div>')
    out.append('<div class="facts">'+"".join(f'<div class="fact"><div class="l">{E(f["label"])}</div><div class="v">{units(H(f["value"]))}</div>{("<div class=n>"+H(f["note"])+"</div>") if f.get("note") else ""}</div>' for f in g.get("quickFacts",[]))+'</div>')
    AL=o.get("alerts",[])
    if AL:
        worst="bad" if any(a.get("level")=="critical" for a in AL) else ("warn" if any(a.get("level")=="warn" for a in AL) else "info")
        items="".join(f'<li>{H(a["text"])}'+(f' <a href="{E(a["sourceUrl"])}" target="_blank" rel="noopener">source</a>' if a.get("sourceUrl") else "")+'</li>' for a in AL)
        out.append(f'<div class="callout {worst} alerts"><p class="eyebrow">Current conditions · checked {E(g.get("lastVerified",""))} · {len(AL)} item{"s" if len(AL)!=1 else ""}</p><ul>{items}</ul></div>')
    out.append('<div class="grid2"><div class="card"><h2>Why go</h2>'+H(o.get("summary",""))+'<p class="eyebrow" style="margin-top:1em">Best for</p><div class="chips">'+"".join(f'<span class="chip">{E(c)}</span>' for c in o.get("bestFor",[]))+'</div></div>')
    out.append('<div class="card"><h2>Don’t miss</h2><ol>'+"".join(f'<li>{H(d)}</li>' for d in o.get("dontMiss",[]))+'</ol><p class="linkrow">Full details in <a href="#top10">Top 10</a>.</p></div></div>')
    out.append('<h2 style="margin-top:.5em">When to go</h2><div class="grid3">'+"".join(
        f'<div class="card season"><span class="verdict {E(s.get("verdict","good").lower())}">{E(s.get("verdict",""))}</span><h3>{E(s["name"])}</h3><p class="temps">{E(s.get("months",""))}</p><p class="temps">{units("Highs "+E(s.get("highs",""))+" · Lows "+E(s.get("lows","")))}</p>{units(H(s.get("notes","")))}</div>' for s in g.get("seasons",[]))+'</div>')
    return "".join(out)

def attraction(g,a):
    d=a.get("difficulty","");t=a.get("type","");p=a.get("permit","none")
    st=a.get("stats",{})
    stats="".join(f'<div class="stat"><div class="l">{E(l)}</div><div class="v">{units(E(st[k]))}</div></div>' for k,l in [("distance","Distance"),("elevationGain","Elevation gain"),("time","Time"),("trailheadOrParking","Start / parking")] if st.get(k))
    if a.get("bestTime"): stats+=f'<div class="stat"><div class="l">Best time</div><div class="v">{E(a["bestTime"])}</div></div>'
    meta=f'<span class="tag type">{E(TYPE_LABEL.get(t,t))}</span>'
    if d: meta+=f'<span class="tag {E(d)}">{E(DIFF_LABEL.get(d,d))}</span>'
    meta+=f'<span class="tag {"permit" if p!="none" else ""}">{E(PERMIT_LABEL.get(p,p))}</span>'
    tips=("<details class=\"tips\"><summary>Tips from the research</summary><div class=\"body\"><ul>"+"".join(f'<li>{units(H(x))}</li>' for x in a["tips"])+"</ul></div></details>") if a.get("tips") else ""
    permit=f'<div class="callout info" style="margin:.4em 0 .8em"><p><b>{E(PERMIT_LABEL.get(p,p))}.</b> {H(a.get("permitNote",""))}</p></div>' if p!="none" and a.get("permitNote") else ""
    season=f'<p class="linkrow">Season note: {units(H(a["seasonNote"]))}</p>' if a.get("seasonNote") else ""
    acc=f'<p class="linkrow">Accessibility: {H(a["accessibility"])}</p>' if a.get("accessibility") else ""
    def host(u): return re.sub(r"^https?://(www\.)?","",u).split("/")[0]
    srcs=" · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(host(u))}</a>' for u in a.get("sources",[])[:2])
    return (f'<article class="card attr" id="{E(a["id"])}" data-type="{E(t)}" data-type-label="{E(TYPE_LABEL.get(t,t))}" data-difficulty="{E(d)}" data-permit="{E(p)}" data-name="{E(a["name"])}" data-time="{E(st.get("time",""))}">'
            f'<div class="pic">{img(g,a.get("image"),a.get("imageAlt",a["name"]),thumb=False)}<span class="rank" aria-label="Rank {a["rank"]}">{a["rank"]}</span>{credit(g,a.get("image"))}</div>'
            f'<div class="body"><div class="head"><h3>{E(a["name"])}</h3></div><div class="meta">{meta}</div>'
            f'<div class="stats">{stats}</div><div class="summary">{units(H(a.get("summary","")))}</div>{permit}{tips}{season}{acc}'
            f'<div class="foot"><button type="button" class="btn addtrip" aria-pressed="false">+ Add to my trip</button><button type="button" class="btn ghost copylink" data-id="{E(a["id"])}">Share</button><span class="spacer"></span><span class="src">Sources: {srcs}</span></div></div></article>')

def sec_top10(g):
    types=[];seen=set()
    for a in g["attractions"]:
        if a.get("type") and a["type"] not in seen: seen.add(a["type"]);types.append(a["type"])
    fb='<div class="filters" id="filters" role="group" aria-label="Filter attractions"><button type="button" class="fbtn on" data-ftype="all" aria-pressed="true">All</button>'+"".join(f'<button type="button" class="fbtn" data-ftype="{E(t)}" aria-pressed="false">{E(TYPE_LABEL.get(t,t))}s</button>' for t in types)
    fb+='<select id="fdiff" aria-label="Difficulty"><option value="all">Any difficulty</option>'+"".join(f'<option value="{k}">{v}</option>' for k,v in DIFF_LABEL.items() if any(a.get("difficulty")==k for a in g["attractions"]))+'</select>'
    fb+='<button type="button" class="fbtn" data-ftoggle="permit" aria-pressed="false">No permit needed</button><button type="button" class="fbtn" data-ftoggle="trip" aria-pressed="false">My trip only</button><span class="spacer"></span><span class="count" id="fcount"></span><button type="button" class="btn ghost" id="fclear">Reset</button></div>'
    cards="".join(attraction(g,a) for a in sorted(g["attractions"],key=lambda a:a["rank"]))
    none='<p id="fnone" class="card" hidden>Nothing matches those filters. <button type="button" class="btn ghost" onclick="document.getElementById(\'fclear\').click()">Reset filters</button></p>'
    also=""
    if g.get("alsoConsider"):
        also='<div class="card also"><h2>Also consider</h2><ul>'+"".join(f'<li><b>{E(x["name"])}</b> — {units(H(x.get("why","")))}'+(f' <a href="{E(x["url"])}" target="_blank" rel="noopener">details</a>' if x.get("url") else "")+'</li>' for x in g["alsoConsider"])+'</ul></div>'
    return f'<h2 class="sech">Top 10 natural attractions</h2><p class="lede">Ranked by popularity. Distances and times are official park figures where available; “time” assumes an average hiker with stops. Tap <b>Add to my trip</b> to build a personal shortlist.</p>{fb}{cards}{none}{also}'

def sec_plan(g):
    L=g["logistics"];out=['<h2 class="sech">Plan your visit</h2>']
    if L.get("gettingThere"):
        out.append('<div class="card"><h2>Getting there</h2><div class="tablewrap"><table><tr><th>From</th><th>Route &amp; time</th><th>Miles</th></tr>'+"".join(f'<tr><td><b>{E(r["from"])}</b></td><td>{units(H(r["how"]))}</td><td>{units(E(str(r.get("miles",""))+" mi") if r.get("miles") else "")}</td></tr>' for r in L["gettingThere"])+'</table></div></div>')
    out.append('<div class="grid2">')
    for k,t in [("gettingAround","Getting around"),("fees","Entrance fees & passes"),("reservations","Reservations & timed entry"),("services","Fuel, food, water, cell")]:
        if L.get(k): out.append(f'<div class="card"><h2>{t}</h2>{units(H(L[k]))}</div>')
    out.append('</div>')
    if L.get("permits"):
        out.append('<h2>Permits</h2><div class="grid2">'+"".join(f'<div class="card"><p class="eyebrow">{"Required" if p.get("required") else "Optional / special"}</p><h3>{E(p["name"])}</h3>{units(H(p.get("how","")))}'+(f'<p class="linkrow"><a href="{E(p["url"])}" target="_blank" rel="noopener">Official page</a></p>' if p.get("url") else "")+'</div>' for p in L["permits"])+'</div>')
    return "".join(out)

def sec_stay(g):
    S=g["stay"];out=['<h2 class="sech">Where to stay</h2><p class="lede">Camping inside the park and lodging just outside it. Booking rules change; each card links to the official page and states how it’s booked.</p>']
    if S.get("camping"):
        out.append('<h2>Camping</h2>')
        for c in S["camping"]:
            b=c.get("booking","")
            kv="".join(f'<div><div class="l">{l}</div><div class="v">{E(c[k])}</div></div>' for k,l in [("sites","Sites"),("cost","Cost"),("season","Season"),("goodFor","Good for")] if c.get(k))
            am=("<div class=\"amen\">"+"".join(f'<span>{E(x)}</span>' for x in c["amenities"])+"</div>") if c.get("amenities") else ""
            out.append(f'<div class="card stay"><div class="meta" style="margin-bottom:6px"><span class="tag {E(b)}">{E(BOOK_LABEL.get(b,b))}</span> <span class="tag">{E(c.get("kind",""))}</span></div><h3>{E(c["name"])}</h3><p class="where">{units(H(c.get("where","")))}</p><div class="kv">{kv}</div>{am}<p><b>How to book:</b> {units(H(c.get("bookingDetail","")))}</p>'+(f'<p>{units(H(c["notes"]))}</p>' if c.get("notes") else "")+(f'<p class="linkrow"><a href="{E(c["url"])}" target="_blank" rel="noopener">Official page / booking</a></p>' if c.get("url") else "")+'</div>')
    if S.get("lodging"):
        out.append('<h2>Lodging</h2><div class="grid2">')
        for l in S["lodging"]:
            ex=("<p class=\"linkrow\">Examples: "+", ".join(E(x) for x in l["examples"])+"</p>") if l.get("examples") else ""
            out.append(f'<div class="card stay"><div class="meta" style="margin-bottom:6px"><span class="tag">{E(l.get("kind",""))}</span>'+(f'<span class="tag">{E(l["priceBand"])}</span>' if l.get("priceBand") else "")+f'</div><h3>{E(l["name"])}</h3><p class="where">{units(H(l.get("distance","")))}</p>{units(H(l.get("summary","")))}{ex}'+(f'<p class="linkrow"><a href="{E(l["url"])}" target="_blank" rel="noopener">Website</a></p>' if l.get("url") else "")+'</div>')
        out.append('</div>')
    return "".join(out)

def sec_safety(g):
    return '<h2 class="sech">Safety &amp; know-before-you-go</h2><p class="lede">The handful of things that actually hurt people here, with the specific rule that prevents each one.</p><div class="grid2">'+"".join(f'<div class="card safety {E(s.get("level","note"))}"><p class="eyebrow">{E(s.get("level","note"))}</p><h3>{E(s["title"])}</h3>{units(H(s["body"]))}</div>' for s in g.get("safety",[]))+'</div>'

def sec_itin(g):
    out=['<h2 class="sech">Itineraries &amp; my trip</h2><div class="card" id="tripCard"><h2>My trip</h2><div id="tripBox"></div></div>']
    for it in g.get("itineraries",[]):
        out.append(f'<div class="card"><p class="eyebrow">{it.get("days",1)} day{"s" if it.get("days",1)!=1 else ""}</p><h2>{E(it["title"])}</h2>'+(f'<p>{H(it["intro"])}</p>' if it.get("intro") else "")+'<ol class="tl">'+"".join(f'<li><span class="when">{E(p["when"])}</span><span>{units(H(p["what"]))}</span></li>' for p in it["plan"])+'</ol></div>')
    return "".join(out)

def sec_faq(g):
    return '<h2 class="sech">Frequently asked</h2>'+"".join(f'<details><summary>{E(q["q"])}</summary><div class="body">{units(H(q["a"]))}</div></details>' for q in g.get("faq",[]))

def footer(g):
    srcs="".join(f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["title"])}</a></li>' for s in g.get("sources",[]))
    creds=[]
    for f,m in sorted(g["_manifest"].items()):
        if f.startswith("thumb-"): continue
        inner=f'{E(m.get("title",f))} — {E(m.get("author",""))}, {E(m.get("license",""))}'
        if m.get("sourceUrl"): inner=f'<a href="{E(m["sourceUrl"])}" target="_blank" rel="noopener">{inner}</a>'
        creds.append(f'<li>{inner}</li>')
    return (f'<footer class="site"><p><b>Last verified {E(g.get("lastVerified",""))}.</b> Conditions, fees, and reservation rules change — always confirm on the official pages below before you go. This guide is independent and not affiliated with the National Park Service.</p>'
            f'<h2>Sources</h2><ul>{srcs}</ul><h2>Photo credits</h2><ul>{"".join(creds)}</ul></footer>')

def render_guide(slug):
    g=load(slug)
    theme=g.get("theme",{})
    extra=""
    if theme.get("accent"): extra+=f':root{{--accent:{theme["accent"]};--accent-ink:{theme.get("accentInk",theme["accent"])};--accent-soft:{theme.get("accentSoft","#f6e6dd")}}}'
    if theme.get("accentDark"): extra+=f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--accent:{theme["accentDark"]};--accent-ink:{theme.get("accentInkDark",theme["accentDark"])};--accent-soft:{theme.get("accentSoftDark","#3a2418")}}}}}:root[data-theme="dark"]{{--accent:{theme["accentDark"]};--accent-ink:{theme.get("accentInkDark",theme["accentDark"])};--accent-soft:{theme.get("accentSoftDark","#3a2418")}}}'
    body={"overview":sec_overview,"top10":sec_top10,"plan":sec_plan,"stay":sec_stay,"safety":sec_safety,"itineraries":sec_itin,"faq":sec_faq}
    secs="".join(f'<section class="sec" id="{sid}" data-title="{t}" aria-labelledby="tab-{sid}">{body[sid](g)}</section>\n' for sid,t in SECTIONS)
    tabs="".join(f'<a href="#{sid}" id="tab-{sid}" data-sec="{sid}">{t}</a>' for sid,t in SECTIONS)
    desc=E(re.sub(r"<[^>]+>","",g["overview"].get("summary",""))[:155])
    heroimg=g.get("hero",{}).get("image","")
    page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(g["name"])} travel guide</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{E(g["name"])} travel guide"><meta property="og:description" content="{desc}">{f'<meta property="og:image" content="img/{E(heroimg)}">' if heroimg else ""}
<style>{CSS}{extra}</style>
</head><body data-slug="{E(slug)}" data-name="{E(g["name"])}">
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="masthead"><div class="titles"><p class="crumbs"><a href="../../index.html">Travel guides</a> / {E(g.get("state",""))}</p><h1>{E(g["name"])}</h1><p class="sub">{E(g.get("tagline",""))}</p></div>
<div class="tools"><a class="iconbtn" href="#itineraries" title="Your saved shortlist">My trip <span class="cnt" id="tripCount" hidden>0</span></a><button type="button" class="iconbtn" id="unitBtn">mi / °F</button><button type="button" class="iconbtn" id="themeBtn">☾ Dark</button></div></div>
<nav class="tabs" aria-label="Sections">{tabs}</nav></header>
<main id="main">
{secs}</main>
{footer(g)}
<script>{JS}</script>
</body></html>'''
    out=os.path.join(GUIDES,slug,"index.html")
    open(out,"w").write(page)
    print(f"built guides/{slug}/index.html  {os.path.getsize(out)//1024} KB  ({len(g['attractions'])} attractions, {len(g['_manifest'])} images)")
    return g

def render_landing(guides):
    cards=""
    for g in guides:
        hero=g.get("hero",{}).get("image","")
        facts=" · ".join(H(f["value"]) for f in g.get("quickFacts",[])[:3])
        cards+=f'<a class="gcard" href="guides/{E(g["slug"])}/index.html"><img src="guides/{E(g["slug"])}/img/{E(hero)}" alt="{E(g.get("hero",{}).get("alt",g["name"]))}" loading="lazy"><div class="b"><p class="eyebrow">{E(g.get("state",""))}</p><h2>{E(g["name"])}</h2><p>{E(g.get("tagline",""))}</p><p class="credit" style="margin-top:.6em">{facts}</p></div></a>'
    page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Travel guides</title><meta name="description" content="Independent, research-backed travel guides to U.S. national parks: top 10 attractions, camping, lodging, permits, safety, and itineraries.">
<style>{CSS}</style></head><body data-slug="landing" data-name="Travel guides">
<header class="site"><div class="masthead"><div class="titles"><h1>Travel guides</h1><p class="sub">Research-backed guides to the places worth the drive. Top 10 attractions, where to stay, permits, safety, and ready-made itineraries.</p></div><div class="tools"><button type="button" class="iconbtn" id="themeBtn">☾ Dark</button></div></div></header>
<main id="main"><div class="guides">{cards}</div>
<p class="linkrow">Each guide is built from a declarative <code>guide.json</code> (see the README). Last verified dates are shown in every guide’s footer.</p></main>
<script>{JS}</script></body></html>'''
    open(os.path.join(ROOT,"index.html"),"w").write(page)
    print("built index.html")

if __name__=="__main__":
    slugs=sys.argv[1:] or sorted(d for d in os.listdir(GUIDES) if os.path.exists(os.path.join(GUIDES,d,"guide.json")))
    gs=[render_guide(s) for s in slugs]
    allg=[load(d) for d in sorted(os.listdir(GUIDES)) if os.path.exists(os.path.join(GUIDES,d,"guide.json"))]
    render_landing(allg)
