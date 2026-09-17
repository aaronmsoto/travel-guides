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
    if(sub){const el=document.getElementById(sub);if(el){el.classList.remove("hide");requestAnimationFrame(()=>{el.scrollIntoView({block:"start"});el.classList.add("flash")})}}
    else window.scrollTo({top:0});
    const tab=tabs[i];if(tab&&tab.scrollIntoView)tab.scrollIntoView({inline:"center",block:"nearest"});
  }
  function route(scroll){
    const h=location.hash.replace(/^#/,"");const [id,sub]=h.split("/");
    show(id||secs[0].id,sub,scroll);
  }
  window.addEventListener("hashchange",()=>route(true));
  route(false);
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
