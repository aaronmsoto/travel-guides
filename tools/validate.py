#!/usr/bin/env python3
"""Validate guides/<slug>/guide.json against the contract in tools/schema.md. Exit 1 on errors.
Usage: python3 tools/validate.py [slug ...] [--links]  (--links also HEAD-checks every URL)"""
import json, os, sys, re, urllib.request, concurrent.futures
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GUIDES=os.environ.get("TG_GUIDES") or os.path.join(ROOT,"guides")
UA="travel-guides-builder/0.1 (https://github.com/aaronmsoto/travel-guides)"
ERR=[];WARN=[]
def err(s):ERR.append(s)
def warn(s):WARN.append(s)
def req(d,keys,ctx):
    for k in keys:
        if k not in d or d[k] in ("",None,[]): err(f"{ctx}: missing '{k}'")
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
    for a in A:
        ctx=f"{slug}/{a.get('id','?')}"
        req(a,["rank","id","name","type","summary","tips","image","sources"],ctx)
        if not re.match(r"^[a-z0-9-]+$",a.get("id","")): err(f"{ctx}: id must be kebab-case")
        if a.get("id") in ids: err(f"{ctx}: duplicate id")
        ids.add(a.get("id"))
        if a.get("type") not in ("hike","viewpoint","scenic-drive","area","canyon","dunes","walk"): err(f"{ctx}: bad type {a.get('type')}")
        if a.get("difficulty") and a["difficulty"] not in ("easy","moderate","strenuous","extreme"): err(f"{ctx}: bad difficulty")
        if a.get("permit","none") not in ("none","required","lottery"): err(f"{ctx}: bad permit")
        if a.get("permit","none")!="none" and not a.get("permitNote"): warn(f"{ctx}: permit set but no permitNote")
        if len(re.sub(r"<[^>]+>","",a.get("summary","")))>700: warn(f"{ctx}: summary > 700 chars")
        if not (3<=len(a.get("tips",[]))<=6): warn(f"{ctx}: tips should be 3–6")
        if a.get("image") and not os.path.exists(os.path.join(imgdir,a["image"])): warn(f"{ctx}: image {a['image']} missing from img/")
        if a.get("image") and man and a["image"] not in man: warn(f"{ctx}: image {a['image']} not in manifest")
    for c in g.get("stay",{}).get("camping",[]):
        if c.get("booking") not in ("reservable","first-come","mixed","permit"): err(f"{slug}/camping/{c.get('name')}: booking must be reservable|first-come|mixed|permit")
        req(c,["name","kind","where","booking","bookingDetail","url"],f"{slug}/camping/{c.get('name')}")
    for s in g.get("safety",[]):
        if s.get("level") not in ("critical","important","note"): err(f"{slug}/safety/{s.get('title')}: bad level")
    if not (5<=len(g.get("faq",[]))<=10): warn(f"{slug}: faq should have 5–10 entries")
    # html whitelist
    bad=set()
    def walk(x):
        if isinstance(x,dict): [walk(v) for v in x.values()]
        elif isinstance(x,list): [walk(v) for v in x]
        elif isinstance(x,str):
            for t in re.findall(r"</?([a-zA-Z]+)",x):
                if t.lower() not in ("b","i","a","br","em","strong","code"): bad.add(t)
    walk({k:v for k,v in g.items() if k!="sources"})
    if bad: warn(f"{slug}: disallowed inline tags will be escaped: {sorted(bad)}")
    # link check
    if links:
        urls=set(s["url"] for s in g.get("sources",[]))
        def walk2(x):
            if isinstance(x,dict): [walk2(v) for v in x.values()]
            elif isinstance(x,list): [walk2(v) for v in x]
            elif isinstance(x,str): urls.update(re.findall(r'https?://[^\s"<>]+',x))
        walk2(g)
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
