#!/usr/bin/env python3
"""Validate guides/<slug>/guide.json (+ photos.json) against tools/schema.md. Exit 1 on errors.
Usage: python3 tools/validate.py [slug ...] [--links]  (--links also GET-checks every URL)"""
import json, os, sys, re, datetime, urllib.request, concurrent.futures
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GUIDES=os.environ.get("TG_GUIDES") or os.path.join(ROOT,"guides")
UA="travel-guides-builder/0.1 (https://github.com/aaronmsoto/travel-guides)"
ERR=[];WARN=[]
def err(s):ERR.append(s)
def warn(s):WARN.append(s)
def req(d,keys,ctx):
    for k in keys:
        if k not in d or d[k] in ("",None,[]): err(f"{ctx}: missing '{k}'")
WORDS={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}
def check(slug,links):
    p=os.path.join(GUIDES,slug,"guide.json")
    try: g=json.load(open(p))
    except Exception as e: err(f"{slug}: JSON parse error: {e}"); return
    req(g,["schema","slug","name","state","tagline","lastVerified","hero","quickFacts","overview","seasons","logistics","attractions","stay","safety","itineraries","faq","sources"],slug)
    if g.get("slug")!=slug: err(f"{slug}: slug field '{g.get('slug')}' != folder")
    if len(g.get("tagline",""))>110: warn(f"{slug}: tagline > 110 chars")
    if len(g.get("seasons",[]))!=4: err(f"{slug}: seasons must have 4 entries")
    for s in g.get("seasons",[]):
        if s.get("verdict") not in ("Best","Good","Fair","Hard"): err(f"{slug}: season {s.get('name')} verdict must be Best|Good|Fair|Hard")
    today=datetime.date.today()
    try:
        lv=datetime.date.fromisoformat(g.get("lastVerified",""))
        if (today-lv).days>45: warn(f"{slug}: lastVerified is {(today-lv).days} days old — re-verify")
    except Exception: err(f"{slug}: lastVerified must be YYYY-MM-DD")
    A=g.get("attractions",[])
    if len(A)!=10: err(f"{slug}: attractions must be exactly 10 (got {len(A)})")
    ranks=sorted(a.get("rank") for a in A)
    if ranks!=list(range(1,len(A)+1)): err(f"{slug}: attraction ranks must be 1..{len(A)} (got {ranks})")
    ids=set()
    imgdir=os.path.join(GUIDES,slug,"img"); man={}
    mp=os.path.join(imgdir,"manifest.json")
    if os.path.exists(mp): man=json.load(open(mp))
    else: warn(f"{slug}: no img/manifest.json yet")
    hero=g.get("hero",{}).get("image")
    if hero and not os.path.exists(os.path.join(imgdir,hero)): warn(f"{slug}: hero image {hero} missing")
    used_imgs={hero} if hero else set()
    for a in A:
        ctx=f"{slug}/{a.get('id','?')}"
        req(a,["rank","id","name","type","summary","tips","image","sources","coords"],ctx)
        if not re.match(r"^[a-z0-9-]+$",a.get("id","")): err(f"{ctx}: id must be kebab-case")
        if a.get("id") in ids: err(f"{ctx}: duplicate id")
        ids.add(a.get("id"))
        if a.get("type") not in ("hike","viewpoint","scenic-drive","area","canyon","dunes","walk"): err(f"{ctx}: bad type {a.get('type')}")
        if a.get("difficulty") and a["difficulty"] not in ("easy","moderate","strenuous","extreme"): err(f"{ctx}: bad difficulty")
        if a.get("permit","none") not in ("none","required","lottery"): err(f"{ctx}: bad permit")
        if a.get("permit","none")!="none" and not a.get("permitNote"): warn(f"{ctx}: permit set but no permitNote")
        if len(re.sub(r"<[^>]+>","",a.get("summary","")))>700: warn(f"{ctx}: summary > 700 chars")
        if not (3<=len(a.get("tips",[]))<=6): warn(f"{ctx}: tips should be 3–6")
        c=a.get("coords")
        if c and not (isinstance(c,list) and len(c)==2 and -90<=c[0]<=90 and -180<=c[1]<=180): err(f"{ctx}: coords must be [lat,lng]")
        st=a.get("stats",{})
        if len(st.get("distance",""))>40: warn(f"{ctx}: stats.distance > 40 chars — move the qualifier into summary")
        if a.get("image"):
            used_imgs.add(a["image"])
            if not os.path.exists(os.path.join(imgdir,a["image"])): warn(f"{ctx}: image {a['image']} missing from img/")
            if man and a["image"] not in man: warn(f"{ctx}: image {a['image']} not in manifest")
    for c in g.get("stay",{}).get("camping",[]):
        if c.get("booking") not in ("reservable","first-come","mixed","permit"): err(f"{slug}/camping/{c.get('name')}: booking must be reservable|first-come|mixed|permit")
        req(c,["name","kind","where","booking","bookingDetail","url"],f"{slug}/camping/{c.get('name')}")
        if c.get("image"): used_imgs.add(c["image"])
    for l in g.get("stay",{}).get("lodging",[]):
        if l.get("image"): used_imgs.add(l["image"])
    for x in g.get("alsoConsider",[]):
        if x.get("image"): used_imgs.add(x["image"])
    for s in g.get("safety",[]):
        if s.get("level") not in ("critical","important","note"): err(f"{slug}/safety/{s.get('title')}: bad level")
        for se in s.get("seasons",[]) or []:
            if se not in ("spring","summer","fall","winter"): err(f"{slug}/safety/{s.get('title')}: bad season {se}")
    if not (5<=len(g.get("faq",[]))<=10): warn(f"{slug}: faq should have 5–10 entries")
    # ---- trip ----
    t=g.get("trip")
    if t:
        ctx=f"{slug}/trip"
        req(t,["title","start","end","host","pitch","base","join","conditions","bring"],ctx)
        try:
            s=datetime.date.fromisoformat(t["start"]);e=datetime.date.fromisoformat(t["end"])
            if not s<e: err(f"{ctx}: start must be before end")
            if e<today: warn(f"{ctx}: trip is in the past")
            nights=(e-s).days
            m=re.search(r"\b(one|two|three|four|five|six|seven|\d)\s+nights?\b",re.sub(r"<[^>]+>","",t.get("pitch","")),re.I)
            if m:
                n=WORDS.get(m.group(1).lower()) or int(m.group(1))
                if n!=nights and not t.get("nightsNote"): err(f"{ctx}: pitch says {n} nights but the dates give {nights}; add nightsNote or fix the pitch")
        except Exception as ex: err(f"{ctx}: bad dates ({ex})")
        b=t.get("base",{})
        req(b,["name","detail","kind"],ctx+"/base")
        if b.get("kind") not in ("town","campsite","lodge"): err(f"{ctx}/base: kind must be town|campsite|lodge")
        if not b.get("coords"): err(f"{ctx}/base: coords required (map home pin)")
        if b.get("image"): used_imgs.add(b["image"])
        if not t.get("cost"): warn(f"{ctx}: no cost card")
        if not t.get("faq"): warn(f"{ctx}: no trip faq")
        for k in t.get("keyDates",[]) or []:
            if re.match(r"^\d{4}-\d{2}-\d{2}$",k.get("date","")) and (datetime.date.fromisoformat(k["date"])-e).days>14: warn(f"{ctx}: keyDate {k['date']} is well after the trip")
        if isinstance(t.get("conditions"),list) and not (3<=len(t["conditions"])<=9): warn(f"{ctx}: conditions should be 3–9 blocks")
        # jargon on the trip tab
        blob=json.dumps(t).lower()
        for j,exp in [("wag bag","wag bag"),(" cfs","cubic feet"),(" mt ","mountain time"),("dispersed","dispersed")]:
            if j in blob and exp not in blob and j!="dispersed": warn(f"{ctx}: '{j.strip()}' used without expansion")
        if not any(s.get("seasons") for s in g.get("safety",[])): warn(f"{slug}: no safety entry has 'seasons' — Safety cannot be sorted for the trip")
    else: warn(f"{slug}: no trip block — this guide will not render as an invitation")
    # ---- photos ----
    pp=os.path.join(GUIDES,slug,"photos","photos.json")
    if os.path.exists(pp):
        P=json.load(open(pp))
        for alb in P.get("albums",[]):
            for it in alb["items"]:
                if not os.path.exists(os.path.join(GUIDES,slug,"photos",it["file"])): err(f"{slug}/photos: {it['file']} missing")
                if it.get("place") and it["place"]!="base" and it["place"] not in ids: err(f"{slug}/photos: {it['file']} place '{it['place']}' is not an attraction id")
                if not it.get("place") and (it.get("lat") is None): warn(f"{slug}/photos: {it['file']} has no place and no GPS — it will not appear on the map")
                if not it.get("caption"): warn(f"{slug}/photos: {it['file']} has no caption")
    # ---- unused images ----
    for f in man:
        if f not in used_imgs: warn(f"{slug}: image {f} is in the manifest but not used by any card (credited but never shown)")
    # ---- html whitelist + prefixes + quotes ----
    bad=set();prefixes=0
    def walk(x):
        nonlocal prefixes
        if isinstance(x,dict): [walk(v) for v in x.values()]
        elif isinstance(x,list): [walk(v) for v in x]
        elif isinstance(x,str):
            if re.match(r"^\s*html:",x): prefixes+=1
            for tg in re.findall(r"</?([a-zA-Z]+)",x):
                if tg.lower() not in ("b","i","a","br","em","strong","code"): bad.add(tg)
    walk({k:v for k,v in g.items() if k!="sources"})
    if bad: warn(f"{slug}: disallowed inline tags will be escaped: {sorted(bad)}")
    if prefixes: err(f"{slug}: {prefixes} fields still start with 'html:' — remove the prefix")
    # ---- source traceability ----
    urls=set()
    def walk2(x):
        if isinstance(x,dict): [walk2(v) for v in x.values()]
        elif isinstance(x,list): [walk2(v) for v in x]
        elif isinstance(x,str): urls.update(re.findall(r'https?://[^\s"<>]+',x))
    walk2({k:v for k,v in g.items() if k not in ("sources","trip")})
    listed=set(s["url"].rstrip("/") for s in g.get("sources",[]))
    for u in sorted(urls):
        if u.rstrip("/") not in listed and "google.com/maps" not in u: warn(f"{slug}: inline link not listed in sources: {u}")
    if links:
        walk2(g.get("trip",{}));urls.update(listed)
        def head(u):
            try:
                r=urllib.request.Request(u,headers={"User-Agent":UA},method="GET")
                with urllib.request.urlopen(r,timeout=20) as resp: return u,resp.status
            except Exception as e: return u,str(e)[:60]
        with concurrent.futures.ThreadPoolExecutor(8) as ex:
            for u,st in ex.map(head,sorted(urls)):
                if st!=200: warn(f"{slug}: link {st}: {u}")
        print(f"{slug}: checked {len(urls)} links")
if __name__=="__main__":
    args=[a for a in sys.argv[1:] if not a.startswith("--")]; links="--links" in sys.argv
    slugs=args or sorted(d for d in os.listdir(GUIDES) if os.path.exists(os.path.join(GUIDES,d,"guide.json")))
    for s in slugs: check(s,links)
    for w in WARN: print("WARN",w)
    for e in ERR: print("ERROR",e)
    print(f"{len(ERR)} errors, {len(WARN)} warnings")
    sys.exit(1 if ERR else 0)
