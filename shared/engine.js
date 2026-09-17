"use strict";
(function(){
  const SLUG=document.body.dataset.slug||"guide";
  const KEY="tg:"+SLUG;
  const $=(s,r)=>(r||document).querySelector(s), $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
  function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")}
  function load(){try{return JSON.parse(localStorage.getItem(KEY)||"{}")||{}}catch(e){return {}}}
  function save(st){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
  let ST=load(); if(!Array.isArray(ST.trip))ST.trip=[];

  // ---- theme toggle ----
  const tbtn=$("#themeBtn");
  function applyTheme(){
    let t=null;try{t=localStorage.getItem("tg:theme")}catch(e){}
    if(t)document.documentElement.dataset.theme=t;else delete document.documentElement.dataset.theme;
    if(tbtn){const dark=t?t==="dark":matchMedia("(prefers-color-scheme: dark)").matches;tbtn.textContent=dark?"☀︎ Light":"☾ Dark";tbtn.setAttribute("aria-label",dark?"Switch to light theme":"Switch to dark theme")}
  }
  if(tbtn)tbtn.addEventListener("click",()=>{
    const cur=document.documentElement.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");
    const nxt=cur==="dark"?"light":"dark";try{localStorage.setItem("tg:theme",nxt)}catch(e){}applyTheme();
  });
  applyTheme();

  // ---- section router (hash-based, shareable) ----
  const secs=$$("main section.sec"), tabs=$$("nav.tabs a[data-sec]");
  if(!secs.length)return;
  function show(id,sub,scroll){
    let i=secs.findIndex(s=>s.id===id); if(i<0)i=0;
    secs.forEach((s,k)=>s.classList.toggle("on",k===i));
    tabs.forEach(a=>{const on=a.dataset.sec===secs[i].id;a.classList.toggle("on",on);a.setAttribute("aria-current",on?"page":"false")});
    document.title=(secs[i].dataset.title||"")+" · "+document.body.dataset.name;
    const tbar=document.querySelector(".tripbar");if(tbar)tbar.hidden=(secs[i].id==="trip");
    if(sub){const el=document.getElementById(sub);if(el){el.classList.remove("hide");requestAnimationFrame(()=>{el.scrollIntoView({block:"start"});el.classList.add("flash")})}}
    else window.scrollTo({top:0});
    const tab=tabs[i];if(tab&&tab.scrollIntoView)tab.scrollIntoView({inline:"center",block:"nearest"});
  }
  function route(scroll){
    const h=location.hash.replace(/^#/,"");const [id,sub]=h.split("/");
    show(id||secs[0].id,sub,scroll);
  }
  window.addEventListener("hashchange",()=>route(true));
  try{history.scrollRestoration="manual"}catch(e){}
  route(false);
  const toTop=()=>{if(!location.hash.includes("/"))window.scrollTo(0,0)};
  setTimeout(toTop,0);window.addEventListener("load",()=>setTimeout(toTop,30));
  // sticky offset for filter bar
  function setStick(){const hd=$("header.site");if(hd)document.documentElement.style.setProperty("--stick",hd.offsetHeight+"px")}
  setStick();window.addEventListener("resize",setStick);

  // ---- Top-10 filters ----
  const cards=$$(".attr");
  const fbar=$("#filters");
  const F={type:"all",diff:"all",permit:false,trip:false};
  function applyFilters(){
    let n=0;
    cards.forEach(c=>{
      const d=c.dataset;
      let ok=true;
      if(F.type!=="all"&&F.type!==(d.type||""))ok=false;
      if(F.diff!=="all"&&F.diff!==(d.difficulty||""))ok=false;
      if(F.permit&&d.permit!=="none")ok=false;
      if(F.trip&&!ST.trip.includes(c.id))ok=false;
      c.classList.toggle("hide",!ok); if(ok)n++;
    });
    const cnt=$("#fcount");if(cnt)cnt.textContent=n===cards.length?"Showing all "+n:"Showing "+n+" of "+cards.length;
    const none=$("#fnone");if(none)none.hidden=n>0;
  }
  if(fbar){
    fbar.addEventListener("click",e=>{
      const b=e.target.closest("[data-ftype]");if(b){F.type=b.dataset.ftype;$$("[data-ftype]",fbar).forEach(x=>{x.classList.toggle("on",x===b);x.setAttribute("aria-pressed",x===b)});applyFilters();return}
      const t=e.target.closest("[data-ftoggle]");if(t){F[t.dataset.ftoggle]=!F[t.dataset.ftoggle];t.classList.toggle("on",F[t.dataset.ftoggle]);t.setAttribute("aria-pressed",F[t.dataset.ftoggle]);applyFilters()}
    });
    const sel=$("#fdiff",fbar);if(sel)sel.addEventListener("change",()=>{F.diff=sel.value;applyFilters()});
    const clr=$("#fclear");if(clr)clr.addEventListener("click",()=>{F.type="all";F.diff="all";F.permit=false;F.trip=false;$$("[data-ftype]",fbar).forEach(x=>{x.classList.toggle("on",x.dataset.ftype==="all");x.setAttribute("aria-pressed",x.dataset.ftype==="all")});$$("[data-ftoggle]",fbar).forEach(x=>{x.classList.remove("on");x.setAttribute("aria-pressed","false")});if(sel)sel.value="all";applyFilters()});
  }

  // ---- My trip (localStorage) ----
  function tripBtnState(){
    cards.forEach(c=>{const b=$(".addtrip",c);if(!b)return;const on=ST.trip.includes(c.id);b.classList.toggle("on",on);b.setAttribute("aria-pressed",on);b.textContent=on?"✓ In my trip":"+ Add to my trip"});
    const cnt=$("#tripCount");if(cnt){cnt.textContent=ST.trip.length;cnt.hidden=!ST.trip.length}
    renderTrip();
  }
  function parseHours(s){ // "4–5 hr" -> 5 ; "45 min" -> .75 ; "1.5–2 hr" -> 2
    if(!s)return 0;const m=s.match(/([\d.]+)\s*(?:[–-]\s*([\d.]+))?\s*(hr|hour|h|min)/i);if(!m)return 0;
    const v=parseFloat(m[2]||m[1]);return /min/i.test(m[3])?v/60:v;
  }
  function renderTrip(){
    const box=$("#tripBox");if(!box)return;
    if(!ST.trip.length){box.innerHTML='<p class="trip-empty">Nothing saved yet. Open <a href="#top10">Top 10</a> and tap “Add to my trip” on anything you want to do. Your list is saved in this browser.</p>';return}
    let hrs=0,permits=0;
    const items=ST.trip.map(id=>cards.find(c=>c.id===id)).filter(Boolean).map((c,i)=>{
      const d=c.dataset;hrs+=parseHours(d.time);if(d.permit!=="none")permits++;
      return '<li><span class="n">'+(i+1)+'</span><span class="t"><a href="#top10/'+esc(c.id)+'">'+esc(d.name)+'</a><small>'+esc([d.typeLabel,d.difficulty,d.time].filter(Boolean).join(" · "))+(d.permit!=="none"?' · permit '+esc(d.permit):'')+'</small></span><button type="button" class="btn ghost rmtrip" data-id="'+esc(c.id)+'" aria-label="Remove '+esc(d.name)+'">Remove</button></li>';
    }).join("");
    box.innerHTML='<ul class="trip-list">'+items+'</ul><p class="linkrow">≈ '+(hrs?Math.round(hrs*2)/2+' hours of activity':'time varies')+(permits?' · <b>'+permits+'</b> item'+(permits>1?'s':'')+' need'+(permits>1?'':'s')+' a permit or lottery':'')+' · <button type="button" class="btn ghost" id="tripPrint">Print / save PDF</button> <button type="button" class="btn ghost" id="tripClear">Clear</button></p>';
    $("#tripPrint",box).addEventListener("click",()=>window.print());
    $("#tripClear",box).addEventListener("click",()=>{if(confirm("Clear your saved trip list?")){ST.trip=[];save(ST);tripBtnState();applyFilters()}});
  }
  document.addEventListener("click",e=>{
    const b=e.target.closest(".addtrip");if(b){const c=b.closest(".attr");const i=ST.trip.indexOf(c.id);if(i>=0)ST.trip.splice(i,1);else ST.trip.push(c.id);save(ST);tripBtnState();if(F.trip)applyFilters();return}
    const r=e.target.closest(".rmtrip");if(r){ST.trip=ST.trip.filter(x=>x!==r.dataset.id);save(ST);tripBtnState();if(F.trip)applyFilters();return}
    const cp=e.target.closest(".copylink");if(cp){const url=location.origin+location.pathname+"#top10/"+cp.dataset.id;(navigator.clipboard?navigator.clipboard.writeText(url):Promise.reject()).then(()=>{cp.textContent="Link copied";setTimeout(()=>cp.textContent="Share",1500)},()=>{prompt("Copy this link",url)})}
  });
  tripBtnState();applyFilters();

  // ---- trip countdown + share ----
  const tb=$(".tripbar");
  if(tb){
    const st=new Date(tb.dataset.start+"T00:00:00"),en=new Date(tb.dataset.end+"T23:59:59"),now=new Date();
    const days=Math.ceil((st-now)/864e5);
    let txt=days>1?days+" days away":days===1?"tomorrow":now<=en?"happening now":"wrapped up";
    $$("#tripCountdown,#tripCountdown2").forEach(n=>n.textContent=txt);
    if(days<=0&&now>en)tb.classList.add("past");
  }
  document.addEventListener("click",e=>{
    const b=e.target.closest(".sharepage");if(!b)return;
    const url=location.origin+location.pathname+"#trip";
    (navigator.clipboard?navigator.clipboard.writeText(url):Promise.reject()).then(()=>{b.textContent="Link copied ✓";setTimeout(()=>b.textContent="Copy link to this trip",1800)},()=>prompt("Copy this link",url));
  });
  // deep link to #trip/join -> scroll to the join card
  // ---- photos: grid/map switch, lightbox, lazy Leaflet map ----
  const MD=(()=>{try{return JSON.parse(($("#mapdata")||{}).textContent||"null")}catch(e){return null}})();
  const lb=$("#lightbox");let lbi=0;
  function lbShow(i){
    if(!MD||!MD.photos.length||!lb)return;lbi=(i+MD.photos.length)%MD.photos.length;const p=MD.photos[lbi];
    const im=$("img",lb);im.src=p.file;im.alt=p.caption||"";
    $(".lb-cap",lb).textContent=p.caption||"";
    const meta=[p.album,p.placeName?(p.approx?"near ":"")+p.placeName:null,p.taken?p.taken.slice(0,10):null].filter(Boolean).join(" · ");
    $(".lb-meta",lb).innerHTML=esc(meta)+(p.place&&p.place!=="base"?' · <a href="#top10/'+esc(p.place)+'">see the card</a>':'')+"  ("+(lbi+1)+"/"+MD.photos.length+")";
    if(!lb.open)lb.showModal();
    const nx=MD.photos[(lbi+1)%MD.photos.length];if(nx){const pre=new Image();pre.src=nx.file}
  }
  document.addEventListener("click",e=>{
    const ph=e.target.closest(".ph[data-i]");if(ph){lbShow(+ph.dataset.i);return}
    const nb=e.target.closest("[data-lb]");if(nb&&lb){const k=nb.dataset.lb;if(k==="close")lb.close();else lbShow(lbi+(k==="next"?1:-1));return}
    if(lb&&lb.open&&e.target===lb)lb.close();
  });
  if(lb){lb.addEventListener("keydown",e=>{if(e.key==="ArrowRight")lbShow(lbi+1);else if(e.key==="ArrowLeft")lbShow(lbi-1)});
    let tx=null;lb.addEventListener("touchstart",e=>{tx=e.touches[0].clientX},{passive:true});lb.addEventListener("touchend",e=>{if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50)lbShow(lbi+(dx<0?1:-1));tx=null});
    lb.addEventListener("close",()=>{$("img",lb).src=""});}
  let mapObj=null,leafletLoading=null;
  function loadLeaflet(){
    if(window.L)return Promise.resolve();
    if(leafletLoading)return leafletLoading;
    leafletLoading=new Promise((res,rej)=>{
      const css=document.createElement("link");css.rel="stylesheet";css.href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css";document.head.appendChild(css);
      const sc=document.createElement("script");sc.src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js";sc.onload=res;sc.onerror=rej;document.head.appendChild(sc);
    });return leafletLoading;
  }
  function buildMap(){
    if(mapObj||!MD||!window.L)return;
    const el=$("#map");if(!el)return;
    const all=[...MD.points,...MD.photos.filter(p=>p.lat!=null)];
    mapObj=L.map(el,{scrollWheelZoom:false});
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:17,attribution:"© OpenStreetMap"}).addTo(mapObj);
    const bounds=[];
    const pin=(color,txt)=>L.divIcon({className:"pin",html:'<span style="background:'+color+'">'+txt+'</span>',iconSize:[26,26],iconAnchor:[13,13],popupAnchor:[0,-12]});
    MD.points.forEach(p=>{
      const isBase=p.kind==="base";
      const m=L.marker([p.lat,p.lng],{icon:pin(isBase?"var(--info)":"var(--accent)",isBase?"⌂":p.rank),title:p.name}).addTo(mapObj);
      m.bindPopup('<b>'+esc(p.name)+'</b>'+(p.thumb?'<br><img src="'+p.thumb+'" alt="" style="width:180px;border-radius:6px;margin-top:6px">':'')+(isBase?'':'<br><a href="#top10/'+esc(p.id)+'">Open card</a>'));
      bounds.push([p.lat,p.lng]);
    });
    // group photos by location
    const groups={};MD.photos.forEach((p,i)=>{if(p.lat==null)return;const k=p.lat.toFixed(4)+","+p.lng.toFixed(4);(groups[k]=groups[k]||[]).push(i)});
    Object.values(groups).forEach(ids=>{
      const p=MD.photos[ids[0]];const off=p.approx?0.0025:0;
      const m=L.marker([p.lat+off,p.lng+off],{icon:pin("var(--good)","📷"),title:ids.length+" photo(s)"}).addTo(mapObj);
      m.bindPopup('<div class="popphotos">'+ids.map(i=>'<img src="'+MD.photos[i].thumb+'" alt="" data-lbi="'+i+'" style="width:84px;height:64px;object-fit:cover;border-radius:5px;margin:2px;cursor:pointer">').join("")+'</div><small>'+ids.length+' photo'+(ids.length>1?'s':'')+(p.placeName?' '+(p.approx?'near ':'at ')+esc(p.placeName):'')+'</small>');
      bounds.push([p.lat,p.lng]);
    });
    if(bounds.length)mapObj.fitBounds(bounds,{padding:[30,30]});else mapObj.setView(MD.center||[37,-113],MD.zoom||9);
    el.addEventListener("click",e=>{const t=e.target.closest("[data-lbi]");if(t)lbShow(+t.dataset.lbi)});
  }
  const vsw=$(".viewsw");
  if(vsw){vsw.addEventListener("click",e=>{
    const b=e.target.closest("[data-view]");if(!b)return;
    $$("[data-view]",vsw).forEach(x=>{x.classList.toggle("on",x===b);x.setAttribute("aria-pressed",x===b)});
    const map=b.dataset.view==="map";$("#pgridwrap").hidden=map;$("#mapwrap").hidden=!map;
    if(map){loadLeaflet().then(()=>{buildMap();mapObj&&setTimeout(()=>mapObj.invalidateSize(),50)}).catch(()=>{$("#map").innerHTML='<p class="card">The map needs an internet connection to load.</p>'})}
  })}
  // ---- units toggle (mi ↔ km / °F ↔ °C) ----
  const ubtn=$("#unitBtn");
  function convText(s,metric){
    if(!metric)return s;
    return s.replace(/(\d[\d,]*(?:\.\d+)?)\s*(?:–|-)\s*(\d[\d,]*(?:\.\d+)?)\s*°F/g,(m,a,b)=>f2c(a)+"–"+f2c(b)+"°C")
            .replace(/(\d[\d,]*(?:\.\d+)?)\s*°F/g,(m,a)=>f2c(a)+"°C")
            .replace(/(\d[\d,]*(?:\.\d+)?)\s*(?:–|-)\s*(\d[\d,]*(?:\.\d+)?)\s*mi\b/g,(m,a,b)=>mi2km(a)+"–"+mi2km(b)+" km")
            .replace(/(\d[\d,]*(?:\.\d+)?)\s*mi\b(?!n)/g,(m,a)=>mi2km(a)+" km")
            .replace(/(\d[\d,]*(?:\.\d+)?)\s*(?:–|-)\s*(\d[\d,]*(?:\.\d+)?)\s*ft\b/g,(m,a,b)=>ft2m(a)+"–"+ft2m(b)+" m")
            .replace(/(\d[\d,]*(?:\.\d+)?)\s*ft\b/g,(m,a)=>ft2m(a)+" m");
  }
  const num=s=>parseFloat(String(s).replace(/,/g,""));
  const f2c=v=>Math.round((num(v)-32)*5/9), mi2km=v=>{const k=num(v)*1.609;return k<10?(Math.round(k*10)/10):Math.round(k)}, ft2m=v=>Math.round(num(v)*0.3048).toLocaleString("en-US");
  const unitNodes=$$("[data-units]");
  unitNodes.forEach(n=>n.dataset.orig=n.innerHTML);
  function applyUnits(){
    let metric=false;try{metric=localStorage.getItem("tg:units")==="metric"}catch(e){}
    unitNodes.forEach(n=>{n.innerHTML=convText(n.dataset.orig,metric)});
    if(ubtn){ubtn.textContent=metric?"km / °C":"mi / °F";ubtn.setAttribute("aria-label",metric?"Switch to miles and Fahrenheit":"Switch to kilometers and Celsius")}
  }
  if(ubtn)ubtn.addEventListener("click",()=>{let m=false;try{m=localStorage.getItem("tg:units")==="metric";localStorage.setItem("tg:units",m?"imperial":"metric")}catch(e){}applyUnits()});
  applyUnits();
})();
