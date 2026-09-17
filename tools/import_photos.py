#!/usr/bin/env python3
"""Import personal trip photos into guides/<slug>/photos/ and photos.json.
Usage: python3 tools/import_photos.py <slug> --trip "January 2025" [--place <attraction-id>] [--caption "..."] [--credit "Name"] file.jpg ...
- Extracts EXIF date + GPS when present; resizes to 1600 px (thumb 480 px), strips EXIF from the published copy.
- Each photo gets an entry in photos.json; edit 'place', 'caption', 'lat'/'lng' by hand afterwards if EXIF was missing.
- 'place' must be an attraction id (or 'base') and resolves to coordinates at build time."""
import sys, os, json, re, datetime, hashlib
from PIL import Image, ImageOps
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def dms(v,ref):
    d=float(v[0])+float(v[1])/60+float(v[2])/3600
    return round(-d if ref in ("S","W") else d,5)
def main():
    a=sys.argv[1:]
    if len(a)<2: sys.exit(__doc__)
    slug=a[0]; trip=None; place=None; caption=None; credit=None; files=[]
    i=1
    while i<len(a):
        if a[i]=="--trip": trip=a[i+1]; i+=2
        elif a[i]=="--place": place=a[i+1]; i+=2
        elif a[i]=="--caption": caption=a[i+1]; i+=2
        elif a[i]=="--credit": credit=a[i+1]; i+=2
        else: files.append(a[i]); i+=1
    d=os.path.join(ROOT,"guides",slug,"photos"); os.makedirs(d,exist_ok=True)
    mp=os.path.join(d,"photos.json")
    M=json.load(open(mp)) if os.path.exists(mp) else {"albums":[]}
    if not trip: sys.exit("--trip is required (album name, e.g. 'January 2025')")
    alb=next((x for x in M["albums"] if x["title"]==trip),None)
    if not alb:
        alb={"title":trip,"credit":credit or "","items":[]}; M["albums"].append(alb)
    if credit: alb["credit"]=credit
    slugt=re.sub(r"[^a-z0-9]+","-",trip.lower()).strip("-")
    for f in files:
        im=Image.open(f); ex=im.getexif()
        taken=ex.get(36867) or ex.get_ifd(0x8769).get(36867) or ex.get(306)
        if taken:
            try: taken=datetime.datetime.strptime(taken,"%Y:%m:%d %H:%M:%S").isoformat(timespec="minutes")
            except Exception: pass
        g=ex.get_ifd(0x8825); lat=lng=None
        if g and 2 in g and 4 in g: lat,lng=dms(g[2],g[1]),dms(g[4],g[3])
        im=ImageOps.exif_transpose(im).convert("RGB")
        h=hashlib.sha1(open(f,"rb").read()).hexdigest()[:8]
        name=f"{slugt}-{h}.jpg"
        if any(it["file"]==name for it in alb["items"]): print("skip (exists)",name); continue
        big=im.copy(); big.thumbnail((1600,1600)); big.save(os.path.join(d,name),"JPEG",quality=82,optimize=True,progressive=True)
        th=im.copy(); th.thumbnail((480,480)); th.save(os.path.join(d,"thumb-"+name),"JPEG",quality=78,optimize=True)
        alb["items"].append({"file":name,"w":big.width,"h":big.height,"taken":taken,"lat":lat,"lng":lng,"place":place,"caption":caption or ""})
        print("added",name,big.size,os.path.getsize(os.path.join(d,name))//1024,"KB","gps:",(lat,lng),"taken:",taken)
    json.dump(M,open(mp,"w"),indent=1,ensure_ascii=False)
    print("photos.json:",sum(len(x["items"]) for x in M["albums"]),"photos in",len(M["albums"]),"album(s)")
if __name__=="__main__": main()
