#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(__dirname,"..");
function escXml(s) {
  return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&apos;");
}
function escHtml(s) {
  return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;");
}
function titleCase(s) {
  return String(s).replaceAll("-"," ").replace(/\b\w/g, c => c.toUpperCase());
}
function clip(s, n) {
  s = String(s).replace(/\s+/g," ").trim();
  return s.length <= n ? s : s.slice(0,n-1).trimEnd()+"…";
}
function wrapWords(s, maxChars) {
  const words = String(s).replace(/\s+/g," ").trim().split(" ");
  const lines = [];
  let line = "";
  for (const word of words) {
    const candidate = line ? line+" "+word : word;
    if (candidate.length > maxChars && line) {
      lines.push(line);
      line = word;
    } else line = candidate;
  }
  if (line) lines.push(line);
  return lines;
}
function textBlock(x,y,lines,cls,lineHeight=18) {
  return `<text x="${x}" y="${y}" class="${cls}">` + lines.map((line,i)=>`<tspan x="${x}" dy="${i===0?0:lineHeight}">${escXml(line)}</tspan>`).join("") + `</text>`;
}
function rect(x,y,w,h,cls,rx=10) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" class="${cls}"/>`;
}
function pathEdge(x1,y1,x2,y2,cls="edge") {
  const mid = Math.round((x1+x2)/2);
  return `<path d="M ${x1} ${y1} H ${mid} V ${y2} H ${x2}" class="${cls}"/>`;
}
function costValue(v) {
  return ({low:1,medium:2,high:3,variable:2})[v] ?? 0;
}
function generateTriageSvg(registry) {
  const systems = Object.fromEntries(registry.systems.map(x=>[x.id,x]));
  const triggers = Object.fromEntries(registry.triggers.map(x=>[x.id,x]));
  const rows = [...registry.recommendations].sort((a,b)=>{
    const ta=triggers[a.trigger_id], tb=triggers[b.trigger_id];
    return ta.family.localeCompare(tb.family) || ta.id.localeCompare(tb.id) || a.id.localeCompare(b.id);
  });
  const rowH=118, top=80, height=Math.max(900, top+rows.length*rowH+80), width=2780;
  const xs={root:30,family:350,trigger:650,guide:1260,system:2210};
  const ws={root:250,family:220,trigger:520,guide:820,system:360};
  const recY = new Map(rows.map((r,i)=>[r.id, top+i*rowH+45]));
  const triggerRows = new Map();
  const familyRows = new Map();
  const systemRows = new Map();
  for (const r of rows) {
    const t=triggers[r.trigger_id];
    (triggerRows.get(t.id) ?? triggerRows.set(t.id,[]).get(t.id)).push(recY.get(r.id));
    (familyRows.get(t.family) ?? familyRows.set(t.family,[]).get(t.family)).push(recY.get(r.id));
    (systemRows.get(r.system_id) ?? systemRows.set(r.system_id,[]).get(r.system_id)).push(recY.get(r.id));
  }
  const avg = arr => arr.reduce((a,b)=>a+b,0)/arr.length;
  const triggerY = new Map([...triggerRows].map(([k,v])=>[k,avg(v)]));
  const familyY = new Map([...familyRows].map(([k,v])=>[k,avg(v)]));
  const systemY = new Map([...systemRows].map(([k,v])=>[k,avg(v)]));
  const rootY = height/2;
  const css = `
<style>
text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#111827}.title{font-size:18px;font-weight:700}.small{font-size:13px}.tiny{font-size:12px}.root{fill:#111827;stroke:#111827}.family{fill:#e0f2fe;stroke:#0284c7}.trigger{fill:#f8fafc;stroke:#64748b}.guide{fill:#fef3c7;stroke:#d97706}.system{fill:#dcfce7;stroke:#16a34a;stroke-width:2}.edge{fill:none;stroke:#cbd5e1;stroke-width:2}.edgeStrong{fill:none;stroke:#94a3b8;stroke-width:2.2}.rootText{fill:#fff;font-size:15px;font-weight:700}.familyText{font-size:14px;font-weight:700;fill:#0c4a6e}.systemText{font-size:14px;font-weight:700;fill:#14532d}.muted{font-size:11px;fill:#475569}
</style>`;
  const out=[`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,css,`<rect width="100%" height="100%" fill="#ffffff"/>`];
  for (const [family,y] of familyY) out.push(pathEdge(xs.root+ws.root,rootY,xs.family,y));
  for (const t of registry.triggers) if (triggerY.has(t.id)) out.push(pathEdge(xs.family+ws.family,familyY.get(t.family),xs.trigger,triggerY.get(t.id)));
  for (const r of rows) {
    out.push(pathEdge(xs.trigger+ws.trigger,triggerY.get(r.trigger_id),xs.guide,recY.get(r.id),"edgeStrong"));
    out.push(pathEdge(xs.guide+ws.guide,recY.get(r.id),xs.system,systemY.get(r.system_id),"edgeStrong"));
  }
  out.push(rect(xs.root,rootY-38,ws.root,76,"root",18));
  out.push(textBlock(xs.root+20,rootY-7,["What kind of machinery","are you about to reinvent?"],"rootText",20));
  for (const [family,y] of [...familyY].sort()) {
    out.push(rect(xs.family,y-28,ws.family,56,"family",12));
    out.push(textBlock(xs.family+14,y+5,[titleCase(family)],"familyText"));
  }
  for (const t of registry.triggers.filter(t=>triggerY.has(t.id)).sort((a,b)=>a.id.localeCompare(b.id))) {
    const y=triggerY.get(t.id);
    out.push(rect(xs.trigger,y-38,ws.trigger,76,"trigger",12));
    out.push(textBlock(xs.trigger+14,y-10,wrapWords(clip(t.smell,115),62).slice(0,3),"small",17));
  }
  for (const r of rows) {
    const s=systems[r.system_id], y=recY.get(r.id);
    out.push(rect(xs.guide,y-48,ws.guide,96,"guide",12));
    out.push(textBlock(xs.guide+14,y-24,[`${s.name} — ${r.strength} · ${r.boundary.kind}`],"title"));
    out.push(textBlock(xs.guide+14,y-2,wrapWords(`Why: ${clip(r.advantage,120)}`,104).slice(0,2),"tiny",16));
    out.push(textBlock(xs.guide+14,y+29,wrapWords(`Avoid if: ${clip(r.avoid_when[0],105)}`,104).slice(0,2),"muted",15));
  }
  for (const [sid,y] of [...systemY].sort()) {
    const s=systems[sid];
    out.push(rect(xs.system,y-32,ws.system,64,"system",16));
    out.push(textBlock(xs.system+16,y-3,[s.name],"systemText"));
    out.push(textBlock(xs.system+16,y+17,[`${s.category} · ${s.maturity.status}`],"muted"));
  }
  out.push(`</svg>`);
  return out.join("\n");
}
function generateTopologySvg(registry) {
  const systems = Object.fromEntries(registry.systems.map(x=>[x.id,x]));
  const triggers = Object.fromEntries(registry.triggers.map(x=>[x.id,x]));
  const familySystems = new Map();
  for (const r of registry.recommendations) {
    const family=triggers[r.trigger_id].family;
    if (!familySystems.has(family)) familySystems.set(family,new Set());
    familySystems.get(family).add(r.system_id);
  }
  const families=[...familySystems.keys()].sort();
  const cols=3, panelW=720, gapX=40, gapY=34, left=40, top=90;
  const panelHeights = families.map(f=>110+familySystems.get(f).size*42);
  const rowHeights=[];
  for(let i=0;i<families.length;i+=cols) rowHeights.push(Math.max(...panelHeights.slice(i,i+cols)));
  const rowYs=[]; let y=top; for(const h of rowHeights){rowYs.push(y); y+=h+gapY;}
  const width=left*2+cols*panelW+(cols-1)*gapX, height=y+40;
  const css=`<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#111827}.panel{fill:#f8fafc;stroke:#cbd5e1;stroke-width:1.5}.chip{fill:#fff;stroke:#94a3b8}.head{font-size:18px;font-weight:700;fill:#0f172a}.meta{font-size:12px;fill:#64748b}.name{font-size:14px;font-weight:700}</style>`;
  const out=[`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,css,`<rect width="100%" height="100%" fill="#ffffff"/>`,textBlock(40,45,["Capability topology — systems clustered by problem family"],"head")];
  families.forEach((family,i)=>{
    const row=Math.floor(i/cols), col=i%cols, px=left+col*(panelW+gapX), py=rowYs[row], ph=panelHeights[i];
    out.push(rect(px,py,panelW,ph,"panel",16));
    out.push(textBlock(px+20,py+34,[titleCase(family)],"head"));
    const ids=[...familySystems.get(family)].sort();
    ids.forEach((sid,j)=>{
      const s=systems[sid], cy=py+58+j*42;
      out.push(rect(px+18,cy,panelW-36,34,"chip",10));
      out.push(textBlock(px+32,cy+22,[s.name],"name"));
      out.push(textBlock(px+panelW-210,cy+22,[s.category],"meta"));
    });
  });
  out.push(`</svg>`);
  return out.join("\n");
}
function generateBoundarySvg(registry) {
  const order=["file-cli","process-rpc","library-ffi","embedded-runtime","spec-artifact","generated-artifact","subsystem-language","whole-project"];
  const systems=Object.fromEntries(registry.systems.map(x=>[x.id,x]));
  const groups=new Map(order.map(x=>[x,[]]));
  for(const r of registry.recommendations) {
    if (!groups.has(r.boundary.kind)) groups.set(r.boundary.kind,[]);
    groups.get(r.boundary.kind).push(r);
  }
  for(const arr of groups.values()) arr.sort((a,b)=>a.system_id.localeCompare(b.system_id));
  const colW=310, gap=18, left=40, top=120;
  const maxItems=Math.max(...[...groups.values()].map(x=>x.length),1);
  const height=top+maxItems*70+100, width=left*2+order.length*colW+(order.length-1)*gap;
  const css=`<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#111827}.lane{fill:#f8fafc;stroke:#cbd5e1}.chip{fill:#ffffff;stroke:#64748b}.head{font-size:15px;font-weight:700}.small{font-size:11px;fill:#64748b}.axis{font-size:14px;font-weight:700;fill:#475569}</style>`;
  const out=[`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,css,`<rect width="100%" height="100%" fill="#ffffff"/>`,textBlock(40,42,["Integration boundary depth"],"head"),textBlock(40,70,["Lower commitment → higher commitment"],"axis")];
  order.forEach((kind,i)=>{
    const x=left+i*(colW+gap), arr=groups.get(kind)??[];
    out.push(rect(x,top-42,colW,height-top-20,"lane",14));
    out.push(textBlock(x+12,top-14,[kind],"head"));
    out.push(textBlock(x+12,top+5,[`${arr.length} recommendation${arr.length===1?"":"s"}`],"small"));
    arr.forEach((r,j)=>{
      const y=top+32+j*68, s=systems[r.system_id];
      out.push(rect(x+10,y,colW-20,56,"chip",10));
      out.push(textBlock(x+22,y+22,[clip(s.name,32)],"head"));
      out.push(textBlock(x+22,y+41,[`${s.category} · ${r.strength}`],"small"));
    });
  });
  out.push(`</svg>`);
  return out.join("\n");
}
function generateAtlasHtml(registry) {
  const systems=Object.fromEntries(registry.systems.map(x=>[x.id,x]));
  const triggers=Object.fromEntries(registry.triggers.map(x=>[x.id,x]));
  const recs=[...registry.recommendations].sort((a,b)=>{
    const ta=triggers[a.trigger_id],tb=triggers[b.trigger_id];
    return ta.family.localeCompare(tb.family)||ta.id.localeCompare(tb.id)||a.id.localeCompare(b.id);
  });
  const strengthRank={"candidate":1,"strong":2,"very-strong":3,"extremely-strong":4};
  const costBar=v=>{
    const n=costValue(v);
    return `<span class="costbar" title="${escHtml(v)}">${[1,2,3].map(i=>`<i class="${i<=n?"on":""}"></i>`).join("")}</span><span class="costlabel">${escHtml(v)}</span>`;
  };
  const cards=recs.map(r=>{
    const s=systems[r.system_id],t=triggers[r.trigger_id];
    const alts=(r.closest_alternatives??[]).map(a=>`<li><strong>${escHtml(a.name)}</strong>: ${escHtml(a.reason)}</li>`).join("");
    const avoids=r.avoid_when.map(x=>`<li>${escHtml(x)}</li>`).join("");
    return `<article class="card" data-search="${escHtml((t.family+" "+t.smell+" "+s.name+" "+s.category+" "+r.boundary.kind+" "+r.advantage).toLowerCase())}">
      <div class="cardhead"><div><span class="family">${escHtml(titleCase(t.family))}</span><h3>${escHtml(s.name)}</h3></div><div class="badges"><span class="badge strength s${strengthRank[r.strength]??1}">${escHtml(r.strength)}</span><span class="badge boundary">${escHtml(r.boundary.kind)}</span><span class="badge category">${escHtml(s.category)}</span></div></div>
      <p class="smell">${escHtml(t.smell)}</p>
      <p><strong>Why cross:</strong> ${escHtml(r.advantage)}</p>
      <div class="two"><div><strong>Avoid when</strong><ul>${avoids}</ul></div><div><strong>Closest alternatives</strong><ul>${alts||"<li>None recorded</li>"}</ul></div></div>
      <p><strong>Cheapest boundary:</strong> ${escHtml(r.boundary.interface)}</p>
      <div class="costs"><span>Learning ${costBar(r.crossing_cost.learning)}</span><span>Integration ${costBar(r.crossing_cost.integration)}</span><span>Ops ${costBar(r.crossing_cost.operational)}</span><span>License ${costBar(r.crossing_cost.licensing)}</span></div>
    </article>`;
  }).join("\n");
  const categoryLegend=[...new Set(registry.systems.map(x=>x.category))].sort().map(x=>`<span class="legendchip">${escHtml(x)}</span>`).join("");
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>right-tool visual atlas</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#0f172a;background:#f8fafc}*{box-sizing:border-box}body{margin:0}header{padding:28px 32px;background:#111827;color:white}header h1{margin:0 0 8px;font-size:30px}header p{margin:0;max-width:980px;color:#cbd5e1}.stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.stat{background:#1f2937;padding:8px 12px;border-radius:10px}nav{position:sticky;top:0;z-index:2;padding:10px 24px;background:white;border-bottom:1px solid #e2e8f0}nav a{margin-right:18px;color:#0369a1;text-decoration:none;font-weight:700}main{padding:24px;max-width:1800px;margin:auto}section{margin:0 0 42px}h2{font-size:24px}.panel{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:16px;box-shadow:0 1px 2px #0000000d}.viz{width:100%;max-height:78vh;object-fit:contain;object-position:left top;border:1px solid #e2e8f0;background:white}.legend{display:flex;gap:8px;flex-wrap:wrap}.legendchip,.badge,.family{display:inline-block;border-radius:999px;padding:4px 8px;font-size:12px;font-weight:700}.legendchip{background:#e2e8f0}.controls{display:flex;gap:12px;margin:14px 0}.controls input{flex:1;padding:12px;border:1px solid #cbd5e1;border-radius:10px;font-size:15px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px}.card{background:white;border:1px solid #cbd5e1;border-radius:14px;padding:16px}.cardhead{display:flex;justify-content:space-between;gap:12px}.card h3{margin:5px 0 0;font-size:20px}.family{background:#e0f2fe;color:#075985}.badges{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}.badge{background:#e2e8f0}.badge.boundary{background:#fef3c7;color:#92400e}.badge.category{background:#dcfce7;color:#166534}.strength.s4{background:#fee2e2;color:#991b1b}.strength.s3{background:#ffedd5;color:#9a3412}.strength.s2{background:#fef9c3;color:#854d0e}.smell{font-weight:700;color:#334155}.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}.two ul{margin-top:6px;padding-left:20px}.costs{display:flex;flex-wrap:wrap;gap:12px;color:#475569;font-size:12px}.costbar{display:inline-flex;gap:2px;margin:0 4px}.costbar i{width:12px;height:7px;border-radius:2px;background:#e2e8f0}.costbar i.on{background:#475569}.costlabel{font-weight:700}.note{color:#64748b}.hidden{display:none}@media(max-width:700px){main{padding:12px}.grid{grid-template-columns:1fr}.two{grid-template-columns:1fr}.cardhead{display:block}.badges{justify-content:flex-start;margin-top:8px}}
</style></head>
<body><header><h1>right-tool visual atlas</h1><p>Start from the machinery you are about to reinvent. Cross an ecosystem boundary only when the specialist deletes enough implementation, semantics, or risk to repay the crossing cost.</p>
<div class="stats"><span class="stat">${registry.systems.length} systems</span><span class="stat">${registry.triggers.length} triggers</span><span class="stat">${registry.recommendations.length} recommendation edges</span><span class="stat">${[...new Set(registry.triggers.map(x=>x.family))].length} capability families</span></div></header>
<nav><a href="#triage">Triage DAG</a><a href="#topology">Capability topology</a><a href="#boundaries">Boundary depth</a><a href="#compare">Compare candidates</a></nav>
<main>
<section id="triage"><h2>Subsystem triage DAG</h2><p class="note">Root → capability family → recognizable implementation smell → recommendation guidance → shared specialist terminal.</p><div class="panel"><img class="viz" src="triage.svg" alt="Subsystem triage decision DAG"></div></section>
<section id="topology"><h2>Capability topology</h2><p class="note">Systems are clustered by the problem families that lead to them. A system may appear in more than one cluster without duplicating source data.</p><div class="panel"><img class="viz" src="capability-topology.svg" alt="Capability topology"></div></section>
<section id="boundaries"><h2>Integration-boundary depth</h2><p class="note">Prefer the leftmost boundary that captures the asymmetric advantage; deeper adoption needs correspondingly stronger justification.</p><div class="panel"><img class="viz" src="boundary-depth.svg" alt="Integration boundary depth"></div></section>
<section id="compare"><h2>Candidate comparison panels</h2><div class="legend">${categoryLegend}</div><div class="controls"><input id="q" type="search" placeholder="Filter by smell, system, category, boundary, or capability…"></div><div id="cards" class="grid">${cards}</div></section>
</main>
<script>
const q=document.getElementById('q');const cards=[...document.querySelectorAll('.card')];
q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();for(const c of cards)c.classList.toggle('hidden',v&&!c.dataset.search.includes(v));});
</script></body></html>`;
}
function generateAll(registry) {
  return {
    "docs/triage.svg": generateTriageSvg(registry),
    "docs/capability-topology.svg": generateTopologySvg(registry),
    "docs/boundary-depth.svg": generateBoundarySvg(registry),
    "docs/atlas.html": generateAtlasHtml(registry)
  };
}
const registry=JSON.parse(fs.readFileSync(path.join(ROOT,"registry","registry.json"),"utf8"));
const outputs=generateAll(registry);
for(const [rel,content] of Object.entries(outputs)){const p=path.join(ROOT,rel);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,content.endsWith("\n")?content:content+"\n","utf8");}
console.log("generated "+Object.keys(outputs).join(", "));
