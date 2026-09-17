"use strict";
(function(){
  const SLUG=document.body.dataset.slug||"guide";
  const KEY="tg:"+SLUG;
  const $=(s,r)=>(r||document).querySelector(s), $$=(s,r)=>Array.from((r||document).querySelectorAll(s));
  function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")}
  function load(){try{return JSON.parse(localStorage.getItem(KEY)||"{}")||{}}catch(e){return {}}}
  function save(st){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
  let ST=load(); if(!Array.isArray(ST.trip))ST.trip=[]; if(!ST.pack||typeof ST.pack!=="object")ST.pack={};
  const REDUCE=matchMedia("(prefers-reduced-motion: reduce)").matches;
  const SB=REDUCE?"auto":"smooth";
  const RSVP=(()=>{try{return JSON.parse(($("#rsvpdata")||{}).textContent||"null")}catch(e){return null}})();
  function announce(msg){const n=$("#copyStatus");if(n){n.textContent="";setTimeout(()=>n.textContent=msg,20)}}

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

  // ---- countdown (guide banner + landing cards) ----
  function countdown(el){
    const st=new Date(el.dataset.start+"T00:00:00"),en=new Date(el.dataset.end+"T23:59:59"),now=new Date();
    const days=Math.ceil((st-now)/864e5);
    return days>1?days+" days away":days===1?"tomorrow":now<=en?"happening now":"wrapped up";
  }
  $$(".gcard .tb-count").forEach(n=>n.textContent="· "+countdown(n));

  // ---- section router (hash-based, shareable) ----
  const secs=$$("main section.sec"), tabs=$$("nav.tabs a[data-sec]");
  if(!secs.length)return;
  function stickyOffset(){
    const hd=$("header.site");let off=hd?hd.offsetHeight:0;
    const f=$(".filters");if(f&&getComputedStyle(f).position==="sticky"&&f.offsetParent)off+=f.offsetHeight;
    return off+12;
  }
  function scrollToEl(el){const y=el.getBoundingClientRect().top+window.scrollY-stickyOffset();window.scrollTo({top:Math.max(0,y),behavior:SB})}
  function show(id,sub){
    let i=secs.findIndex(s=>s.id===id);
    if(i<0){i=0;try{history.replaceState(null,"","#"+secs[0].id)}catch(e){}}
    secs.forEach((s,k)=>s.classList.toggle("on",k===i));
    tabs.forEach(a=>{const on=a.dataset.sec===secs[i].id;a.classList.toggle("on",on);a.setAttribute("aria-current",on?"page":"false")});
    document.title=(secs[i].dataset.title||"")+" · "+document.body.dataset.name;
    const tbar=$(".tripbar");if(tbar)tbar.hidden=(secs[i].id==="trip");
    const note=$("#routeNote");if(note)note.remove();
    if(sub&&!/^picks=/.test(sub)){
      const el=document.getElementById(sub);
      if(el){el.classList.remove("hide");requestAnimationFrame(()=>{scrollToEl(el);el.classList.add("flash");setTimeout(()=>el.classList.remove("flash"),1800)})}
      else{secs[i].insertAdjacentHTML("afterbegin",'<p class="callout warn" id="routeNote" role="status">We couldn’t find that spot in this guide — here’s the full section.</p>');window.scrollTo({top:0})}
    } else window.scrollTo({top:0});
    const tab=tabs[i];if(tab&&tab.scrollIntoView)tab.scrollIntoView({inline:"center",block:"nearest"});
  }
  function parseHash(){const h=location.hash.replace(/^#/,"");const k=h.indexOf("/");return k<0?[h,""]:[h.slice(0,k),h.slice(k+1)]}
  function route(){
    const [id,sub]=parseHash();
    if(sub&&/^picks=/.test(sub)){ // incoming shared picks: merge into local list
      const ids=sub.slice(6).split(",").filter(Boolean);let added=0;
      ids.forEach(x=>{if(document.getElementById(x)&&!ST.trip.includes(x)){ST.trip.push(x);added++}});
      if(added){save(ST)}
      try{history.replaceState(null,"","#trip/picks")}catch(e){}
      show("trip","picks");tripBtnState();return;
    }
    show(id||secs[0].id,sub);
  }
  window.addEventListener("hashchange",route);
  try{history.scrollRestoration="manual"}catch(e){}
  function setStick(){const hd=$("header.site");if(hd)document.documentElement.style.setProperty("--stick",hd.offsetHeight+"px")}
  setStick();window.addEventListener("resize",setStick);
  // compact masthead once scrolled (mobile)
  let lastScrolled=false;
  window.addEventListener("scroll",()=>{const s=window.scrollY>60;if(s!==lastScrolled){lastScrolled=s;document.body.classList.toggle("scrolled",s);setStick()}},{passive:true});

  // ---- trip countdown + share ----
  const tb=$(".tripbar");
  if(tb){const txt=countdown(tb);$$("#tripCountdown,#tripCountdown2").forEach(n=>n.textContent=txt);if(txt==="wrapped up")tb.classList.add("past")}
  function copy(text,btn,label,done){
    (navigator.clipboard?navigator.clipboard.writeText(text):Promise.reject()).then(()=>{if(btn){const o=btn.textContent;btn.textContent=done||"Copied ✓";setTimeout(()=>btn.textContent=o,1800)}announce(label||"Copied to clipboard")},()=>{prompt("Copy this:",text)});
  }
  function pageUrl(){return (RSVP&&RSVP.url)||(location.origin+location.pathname)}

  // ---- staleness ----
  (function(){const v=document.body.dataset.verified;const n=$("#staleNote");if(!v||!n)return;const days=Math.floor((Date.now()-new Date(v+"T00:00:00"))/864e5);
    if(days>90){n.textContent="· "+days+" days old — re-check the official pages";n.className="stale bad"}else if(days>30){n.textContent="· checked "+days+" days ago — confirm before you go";n.className="stale warn"}})();

  // ---- Top-10 filters ----
  const cards=$$(".attr");
  const fbar=$("#filters");
  const F={type:"all",diff:"all",permit:false,trip:false};
  function applyFilters(){
    let n=0;
    cards.forEach(c=>{
      const d=c.dataset;let ok=true;
      if(F.type!=="all"&&F.type!==(d.type||""))ok=false;
      if(F.diff!=="all"&&F.diff!==(d.difficulty||""))ok=false;
      if(F.permit&&d.permit!=="none")ok=false;
      if(F.trip&&!ST.trip.includes(c.id))ok=false;
      c.classList.toggle("hide",!ok); if(ok)n++;
    });
    const cnt=$("#fcount");if(cnt)cnt.textContent=n===cards.length?"Showing all "+n:"Showing "+n+" of "+cards.length;
    const none=$("#fnone");if(none)none.hidden=n>0;
    const clr=$("#fclear");if(clr)clr.disabled=(F.type==="all"&&F.diff==="all"&&!F.permit&&!F.trip);
  }
  if(fbar){
    fbar.addEventListener("click",e=>{
      const b=e.target.closest("[data-ftype]");if(b){F.type=b.dataset.ftype;$$("[data-ftype]",fbar).forEach(x=>{x.classList.toggle("on",x===b);x.setAttribute("aria-pressed",x===b)});applyFilters();return}
      const t=e.target.closest("[data-ftoggle]");if(t){F[t.dataset.ftoggle]=!F[t.dataset.ftoggle];t.classList.toggle("on",F[t.dataset.ftoggle]);t.setAttribute("aria-pressed",F[t.dataset.ftoggle]);applyFilters()}
    });
    const sel=$("#fdiff",fbar);if(sel)sel.addEventListener("change",()=>{F.diff=sel.value;applyFilters()});
    const clr=$("#fclear");if(clr)clr.addEventListener("click",()=>{F.type="all";F.diff="all";F.permit=false;F.trip=false;$$("[data-ftype]",fbar).forEach(x=>{x.classList.toggle("on",x.dataset.ftype==="all");x.setAttribute("aria-pressed",x.dataset.ftype==="all")});$$("[data-ftoggle]",fbar).forEach(x=>{x.classList.remove("on");x.setAttribute("aria-pressed","false")});if(sel)sel.value="all";applyFilters()});
  }

  // ---- My picks (localStorage + shareable) ----
  function pickNames(){return ST.trip.map(id=>cards.find(c=>c.id===id)).filter(Boolean).map(c=>c.dataset.name)}
  function picksUrl(){return pageUrl()+"#trip/picks="+ST.trip.join(",")}
  function tripBtnState(){
    cards.forEach(c=>{const b=$(".addtrip",c);if(!b)return;const on=ST.trip.includes(c.id);b.classList.toggle("on",on);b.setAttribute("aria-pressed",on);b.textContent=on?"✓ In my picks":"+ Add to my picks"});
    const cnt=$("#tripCount");if(cnt){cnt.textContent=ST.trip.length;cnt.hidden=!ST.trip.length}
    renderTrip();
  }
  function renderTrip(){
    const box=$("#picksBox");if(!box)return;
    if(!ST.trip.length){box.innerHTML='<p class="trip-empty">Nothing picked yet. Tap a tile above or open <a href="#top10">Top 10</a> and hit <b>Add to my picks</b> on anything you’d want to do. Picks are kept in this browser; copy the link to send them to the host.</p>';return}
    let permits=0;
    const items=ST.trip.map(id=>cards.find(c=>c.id===id)).filter(Boolean).map((c,i)=>{
      const d=c.dataset;if(d.permit!=="none")permits++;
      return '<li><span class="n">'+(i+1)+'</span><span class="t"><a href="#top10/'+esc(c.id)+'">'+esc(d.name)+'</a><small>'+esc([d.typeLabel,d.difficultyLabel,d.time].filter(Boolean).join(" · "))+(d.permit!=="none"?' · permit '+esc(d.permit):'')+'</small></span><button type="button" class="btn ghost rmtrip" data-id="'+esc(c.id)+'" aria-label="Remove '+esc(d.name)+'">Remove</button></li>';
    }).join("");
    box.innerHTML='<ul class="trip-list">'+items+'</ul><p class="linkrow">'+ST.trip.length+' of '+cards.length+' picked'+(permits?' · <b>'+permits+'</b> need'+(permits>1?'':'s')+' a permit or lottery':'')+' · kept in this browser</p>'+
      '<p class="cta"><button type="button" class="btn primary" id="picksCopy">Copy a link to my picks</button> <button type="button" class="btn ghost danger" id="tripClear">Clear</button></p>';
    $("#picksCopy",box).addEventListener("click",e=>copy(picksUrl(),e.currentTarget,"Link to your picks copied","Link copied ✓ — send it to the host"));
    $("#tripClear",box).addEventListener("click",()=>{if(confirm("Clear your picks?")){ST.trip=[];save(ST);tripBtnState();applyFilters()}});
  }
  document.addEventListener("click",e=>{
    const b=e.target.closest(".addtrip");if(b){const c=b.closest(".attr");const i=ST.trip.indexOf(c.id);if(i>=0)ST.trip.splice(i,1);else ST.trip.push(c.id);save(ST);tripBtnState();if(F.trip)applyFilters();announce(i>=0?"Removed from your picks":"Added to your picks");return}
    const r=e.target.closest(".rmtrip");if(r){ST.trip=ST.trip.filter(x=>x!==r.dataset.id);save(ST);tripBtnState();if(F.trip)applyFilters();return}
    const cp=e.target.closest(".copylink");if(cp){copy(pageUrl()+"#top10/"+cp.dataset.id,cp,"Link copied","Link copied");return}
    const sp=e.target.closest(".sharepage");if(sp){copy(pageUrl()+"#trip",sp,"Link copied","Link copied ✓");return}
  });
  tripBtnState();applyFilters();

  // ---- packing checklist ----
  const packs=$$("[data-pack]");
  function packState(){packs.forEach(c=>{c.checked=!!ST.pack[c.dataset.pack]});const n=packs.filter(c=>c.checked).length;const pc=$("#packCount");if(pc)pc.textContent=packs.length?(n+" of "+packs.length+" packed · ticks are saved in this browser"):""}
  packs.forEach(c=>c.addEventListener("change",()=>{ST.pack[c.dataset.pack]=c.checked;save(ST);packState()}));
  packState();

  // ---- photos: grid/map switch, lightbox, lazy Leaflet map ----
  const MD=(()=>{try{return JSON.parse(($("#mapdata")||{}).textContent||"null")}catch(e){return null}})();
  const lb=$("#lightbox");let lbi=0;
  function lbShow(i){
    if(!MD||!MD.photos.length||!lb)return;lbi=(i+MD.photos.length)%MD.photos.length;const p=MD.photos[lbi];
    const im=$("img",lb);im.src=p.file;im.alt=p.caption||"";
    $(".lb-cap",lb).textContent=p.caption||"";
    const meta=[p.album,p.placeName?(p.approx?"near ":"")+p.placeName:null,p.taken?p.taken.slice(0,10):null].filter(Boolean).join(" · ");
    $(".lb-meta",lb).innerHTML=esc(meta)+(p.place&&p.place!=="base"?' · <a href="#top10/'+esc(p.place)+'">see the card</a>':'')+"  ("+(lbi+1)+"/"+MD.photos.length+")";
    if(!lb.open){lb.showModal();document.documentElement.classList.add("lb-open")}
    const nx=MD.photos[(lbi+1)%MD.photos.length];if(nx){const pre=new Image();pre.src=nx.file}
  }
  document.addEventListener("click",e=>{
    const ph=e.target.closest(".ph[data-i]");if(ph){lbShow(+ph.dataset.i);return}
    const nb=e.target.closest("[data-lb]");if(nb&&lb){const k=nb.dataset.lb;if(k==="close")lb.close();else lbShow(lbi+(k==="next"?1:-1));return}
    if(lb&&lb.open&&e.target===lb)lb.close();
  });
  if(lb){lb.addEventListener("keydown",e=>{if(e.key==="ArrowRight")lbShow(lbi+1);else if(e.key==="ArrowLeft")lbShow(lbi-1)});
    let tx=null;lb.addEventListener("touchstart",e=>{tx=e.touches[0].clientX},{passive:true});
    lb.addEventListener("touchmove",e=>{e.preventDefault()},{passive:false});
    lb.addEventListener("touchend",e=>{if(tx===null)return;const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50)lbShow(lbi+(dx<0?1:-1));tx=null});
    lb.addEventListener("close",()=>{$("img",lb).src="";document.documentElement.classList.remove("lb-open")});}
  let mapObj=null,leafletLoading=null;
  const LEAFLET={js:"https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js",jsSri:"sha384-NElt3Op+9NBMCYaef5HxeJmU4Xeard/Lku8ek6hoPTvYkQPh3zLIrJP7KiRocsxO",css:"https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css",cssSri:"sha384-c6Rcwz4e4CITMbu/NBmnNS8yN2sC3cUElMEMfP3vqqKFp7GOYaaBBCqmaWBjmkjb"};
  function loadLeaflet(){
    if(window.L)return Promise.resolve();
    if(leafletLoading)return leafletLoading;
    leafletLoading=new Promise((res,rej)=>{
      const css=document.createElement("link");css.rel="stylesheet";css.href=LEAFLET.css;css.integrity=LEAFLET.cssSri;css.crossOrigin="anonymous";document.head.appendChild(css);
      const sc=document.createElement("script");sc.src=LEAFLET.js;sc.integrity=LEAFLET.jsSri;sc.crossOrigin="anonymous";sc.onload=res;sc.onerror=rej;document.head.appendChild(sc);
    });return leafletLoading;
  }
  function buildMap(){
    if(mapObj||!MD||!window.L)return;
    const el=$("#map");if(!el)return;
    mapObj=L.map(el,{scrollWheelZoom:false});
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:17,attribution:"© OpenStreetMap"}).addTo(mapObj);
    const bounds=[];
    const pin=(cls,txt)=>L.divIcon({className:"pin",html:'<span class="'+cls+'">'+txt+'</span>',iconSize:[26,26],iconAnchor:[13,13],popupAnchor:[0,-12]});
    MD.points.forEach(p=>{
      const isBase=p.kind==="base";
      const m=L.marker([p.lat,p.lng],{icon:pin(isBase?"info":"accent",isBase?"⌂":p.rank),title:p.name,zIndexOffset:isBase?500:0}).addTo(mapObj);
      m.bindPopup('<b>'+esc(p.name)+'</b>'+(p.thumb?'<br><img src="'+p.thumb+'" alt="" style="width:180px;border-radius:6px;margin-top:6px">':'')+(isBase?'':'<br><a href="#top10/'+esc(p.id)+'">Open card</a>'));
      bounds.push([p.lat,p.lng]);
    });
    const groups={};MD.photos.forEach((p,i)=>{if(p.lat==null)return;const k=p.lat.toFixed(4)+","+p.lng.toFixed(4);(groups[k]=groups[k]||[]).push(i)});
    Object.values(groups).forEach(ids=>{
      const p=MD.photos[ids[0]];const off=p.approx?0.006:0;
      const m=L.marker([p.lat+off,p.lng-off],{icon:pin("good","📷"),title:ids.length+" photo(s)",zIndexOffset:1000}).addTo(mapObj);
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
  const num=s=>parseFloat(String(s).replace(/,/g,""));
  const f2c=v=>Math.round((num(v)-32)*5/9), mi2km=v=>{const k=num(v)*1.609;return k<10?(Math.round(k*10)/10):Math.round(k)}, ft2m=v=>Math.round(num(v)*0.3048).toLocaleString("en-US");
  const N="(\\d[\\d,]*(?:\\.\\d+)?)";
  function convText(s,metric){
    if(!metric)return s;
    return s.replace(new RegExp(N+"\\s*(?:–|-)\\s*"+N+"\\s*°F","g"),(m,a,b)=>f2c(a)+"–"+f2c(b)+"°C")
            .replace(new RegExp(N+"\\s*°F","g"),(m,a)=>f2c(a)+"°C")
            .replace(new RegExp(N+"s\\s*°F","g"),(m,a)=>f2c(a)+"s °C")
            .replace(new RegExp(N+"\\s*(?:–|-)\\s*"+N+"\\s*(?:mi\\b|miles?\\b)","g"),(m,a,b)=>mi2km(a)+"–"+mi2km(b)+" km")
            .replace(new RegExp(N+"\\s*(?:mi\\b(?!n)|miles?\\b)","g"),(m,a)=>mi2km(a)+" km")
            .replace(new RegExp(N+"\\s*(?:–|-)\\s*"+N+"\\s*(?:ft\\b|feet\\b|foot\\b)","g"),(m,a,b)=>ft2m(a)+"–"+ft2m(b)+" m")
            .replace(new RegExp(N+"[- ]?(?:ft\\b|feet\\b|foot\\b)","g"),(m,a)=>ft2m(a)+" m")
            .replace(/\ba mile\b/g,"1.6 km").replace(/\bhalf a mile\b/g,"800 m").replace(/\ba half-mile\b/g,"an 800 m");
  }
  const unitNodes=$$("[data-units]");
  unitNodes.forEach(n=>n.dataset.orig=n.innerHTML);
  function applyUnits(){
    let metric=false;try{metric=localStorage.getItem("tg:units")==="metric"}catch(e){}
    unitNodes.forEach(n=>{n.innerHTML=convText(n.dataset.orig,metric)});
    if(ubtn){ubtn.innerHTML='<span class="visually-hidden">Units: </span>'+(metric?"km / °C":"mi / °F");ubtn.setAttribute("aria-pressed",metric);ubtn.title=metric?"Showing metric — click for miles and °F":"Showing miles and °F — click for metric"}
  }
  if(ubtn)ubtn.addEventListener("click",()=>{let m=false;try{m=localStorage.getItem("tg:units")==="metric";localStorage.setItem("tg:units",m?"imperial":"metric")}catch(e){}applyUnits()});
  applyUnits();

  route();
  const toTop=()=>{const [,sub]=parseHash();if(!sub)window.scrollTo(0,0)};
  setTimeout(toTop,0);window.addEventListener("load",()=>setTimeout(toTop,30));
})();
