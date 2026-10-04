"""Build the static, self-contained dashboard (no server, no CDN) from the latest eval run + the factor database.

Reproduce (from ev-c2-green-auto-lca/):  python3 eval/eval.py && python3 components/dashboard/build.py
Output: deliverables/dashboard/index.html  (open in any browser)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "components" / "lca_engine"))
from greenauto.db import FactorDB  # noqa: E402

TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Green Auto India — LCA dashboard (prototype)</title>
<style>
body{font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1b1f23;background:#f6f7f4}
header{background:#14532d;color:#fff;padding:18px 28px}header h1{margin:0;font-size:22px}header p{margin:4px 0 0;opacity:.85}
main{max-width:1180px;margin:0 auto;padding:20px 28px}section{background:#fff;border:1px solid #e3e6df;border-radius:10px;padding:18px 20px;margin:0 0 18px}
h2{font-size:17px;margin:0 0 10px}select,input{font:inherit}.row{display:flex;gap:18px;flex-wrap:wrap}.card{flex:1;min-width:200px;border:1px solid #e3e6df;border-radius:8px;padding:12px}
.big{font-size:28px;font-weight:650}.muted{color:#5b6470;font-size:13px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #eceee9;padding:6px 6px;text-align:left;vertical-align:top}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:12px;background:#e8f3ec;color:#14532d}.tag.derived{background:#eef1fb;color:#24357a}.tag.assumption,.tag.UNVERIFIED{background:#fdecea;color:#8a1c12}
.legend span{display:inline-flex;align-items:center;margin-right:14px;font-size:13px}.legend i{width:12px;height:12px;border-radius:2px;margin-right:5px;display:inline-block}
code{font-size:12px;background:#f1f3ef;padding:1px 4px;border-radius:4px}footer{color:#5b6470;font-size:12px;padding:0 28px 30px;max-width:1180px;margin:0 auto}
</style></head><body>
<header><h1>Green Auto India — India-specific automotive LCA (prototype)</h1>
<p>Case study 1: 110 cc petrol scooter vs 2.9 kWh electric scooter · functional unit: 1 vehicle-km · GHG (g CO<sub>2</sub>e/km) · every number traceable to a cited record</p></header>
<main>
<section><h2>Scenario</h2><select id="sc"></select><p id="scdesc" class="muted"></p></section>
<section><h2>Life-cycle GHG by stage (central values; whiskers = 90% Monte Carlo interval)</h2><div class="legend" id="legend"></div><svg id="bars" width="100%" height="190"></svg></section>
<section class="row" id="cards"></section>
<section><h2>What-if: grid emission factor for charging</h2>
<p class="muted">Electricity stage = consumption (kWh/km) × grid factor at the meter. CEA FY2025-26 references: build margin 0.446 · average 0.675 · operating margin 0.963 kg CO<sub>2</sub>/kWh at generation (grossed up for 17.63% T&amp;D losses).</p>
Charging state (T&amp;D losses FY2023-24, Lok Sabha USQ 842): <select id="st"></select><br><input type="range" id="ef" min="0" max="1.4" step="0.005" style="width:60%"> <b id="efv"></b> kg CO<sub>2</sub>/kWh at generation
<p id="whatif" class="big"></p><p id="breakeven" class="muted"></p></section>
<section><h2>Where to collect Indian data next (share of rank-variance of the reduction)</h2><div id="gaps"></div>
<p class="muted">Parameter uncertainty only (pedigree-derived lognormals, paired sampling). Scenario choices (average vs marginal grid) move the result far more — compare the scenarios above.</p></section>
<section><h2>Provenance — every parameter in this scenario</h2><table id="prov"></table></section>
</main>
<footer>Prototype for Techfest 2026 × MHI × ICAT, Challenge 2 (Green Auto India). Engine: <code>components/lca_engine</code>; eval: <code>python3 eval/eval.py</code> (commit __COMMIT__). Not an ISO 14044-reviewed study.</footer>
<script>
const R=__RESULTS__, DB=__DB__;
const COLORS={vehicle_production:"#4b7f52",battery_production:"#9bc53d",fuel_production_wtt:"#e0a458",electricity_production_wtt:"#3e7cb1",tailpipe_ttw:"#c0392b"};
const NAMES={vehicle_production:"Vehicle production",battery_production:"Battery production",fuel_production_wtt:"Fuel production (WTT)",electricity_production_wtt:"Electricity generation + T&D",tailpipe_ttw:"Tailpipe (TTW)"};
const sel=document.getElementById('sc');
Object.keys(R).forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=R[k].label;sel.appendChild(o)});
sel.value=Object.keys(R).includes('in2026_cea_average')?'in2026_cea_average':Object.keys(R)[0];
document.getElementById('legend').innerHTML=Object.keys(NAMES).map(k=>`<span><i style="background:${COLORS[k]}"></i>${NAMES[k]}</span>`).join('');
function fmt(x,d=1){return Number(x).toFixed(d)}
function draw(){
 const r=R[sel.value];document.getElementById('scdesc').textContent=r.description;
 const prods=Object.entries(r.products),svg=document.getElementById('bars'),W=svg.clientWidth||900,L=260,maxv=80,sx=v=>L+(W-L-30)*v/maxv;
 let h='';prods.forEach(([pid,p],i)=>{let y=20+i*75,x=0;h+=`<text x="0" y="${y+22}" font-size="13">${p.label}</text>`;
  Object.entries(p.stages).forEach(([s,v])=>{h+=`<rect x="${sx(x)}" y="${y}" width="${Math.max(0,sx(x+v)-sx(x))}" height="34" fill="${COLORS[s]||'#999'}"><title>${NAMES[s]||s}: ${fmt(v,2)} g/km</title></rect>`;x+=v});
  const m=p.mc_total;h+=`<line x1="${sx(m.p05)}" x2="${sx(m.p95)}" y1="${y+17}" y2="${y+17}" stroke="#111" stroke-width="1.5"/><line x1="${sx(m.p05)}" x2="${sx(m.p05)}" y1="${y+9}" y2="${y+25}" stroke="#111"/><line x1="${sx(m.p95)}" x2="${sx(m.p95)}" y1="${y+9}" y2="${y+25}" stroke="#111"/>`;
  h+=`<text x="${sx(m.p95)+6}" y="${y+22}" font-size="13" font-weight="600">${fmt(p.total)} g/km</text>`});
 for(let t=0;t<=maxv;t+=20){h+=`<text x="${sx(t)}" y="185" font-size="11" fill="#777">${t}</text>`}
 svg.innerHTML=h;
 const c=r.comparison,ps=r.products;
 document.getElementById('cards').innerHTML=`<div class="card"><div class="muted">EV reduction vs petrol (central)</div><div class="big">${fmt(100*c.reduction_central)}%</div><div class="muted">90% interval ${fmt(100*c.reduction_mc.p05)}–${fmt(100*c.reduction_mc.p95)}%</div></div>
 <div class="card"><div class="muted">P(EV lower than petrol)</div><div class="big">${fmt(100*c.p_bev_lower)}%</div><div class="muted">paired Monte Carlo, n=${r.n_iterations}, seed ${r.seed}</div></div>
 <div class="card"><div class="muted">Data-quality index (1 best … 5 worst)</div><div class="big">${fmt(ps[c.ice].dqi,2)} / ${fmt(ps[c.bev].dqi,2)}</div><div class="muted">petrol / EV · India-specific share ${fmt(100*ps[c.ice].india_weighted_share,0)}% / ${fmt(100*ps[c.bev].india_weighted_share,0)}%</div></div>`;
 document.getElementById('gaps').innerHTML=Object.entries(c.variance_share_of_reduction).slice(0,7).map(([k,v])=>`<div style="display:flex;align-items:center;gap:8px;margin:3px 0"><div style="width:${Math.round(420*v)}px;height:14px;background:#14532d"></div><span class="muted">${fmt(100*v)}%</span> <code>${k}</code> <span class="muted">${DB.records[k]?DB.records[k].name:''}</span></div>`).join('');
 const rows=[];prods.forEach(([pid,p])=>Object.entries(p.params).forEach(([n,rid])=>{const d=DB.records[rid],s=DB.sources[d.source_id];
  rows.push(`<tr><td>${p.powertrain}</td><td><code>${n}</code></td><td>${d.name}<br><span class="muted">${rid}</span></td><td>${d.value} ${d.unit}<br><span class="muted">${d.gas_basis}, ${d.geography}, ${d.reference_year}</span></td><td><span class="tag ${d.status}">${d.status}</span><br><span class="muted">pedigree ${Object.values(d.pedigree).join('-')}</span></td><td><a href="${s.url}">${s.title}</a> (${s.publisher}, ${s.year})<br><span class="muted">${d.locator}</span>${d.quote?`<br><i class="muted">“${d.quote}”</i>`:''}${d.derivation?`<br><span class="muted">= ${d.derivation}</span>`:''}</td></tr>`)}));
 document.getElementById('prov').innerHTML='<tr><th>Vehicle</th><th>Param</th><th>Record</th><th>Value</th><th>Status</th><th>Source · locator · quote</th></tr>'+rows.join('');
 const ev=ps[c.bev];document.getElementById('ef').dataset.elec=ev.stages.electricity_production_wtt;whatif(true)}
function whatif(reset){
 const r=R[sel.value],c=r.comparison,ev=r.products[c.bev],ice=r.products[c.ice];
 const elecRid=ev.params.elec,elec=DB.records[elecRid].value/100,td=Number(document.getElementById('st').value);
 const slider=document.getElementById('ef');if(reset){slider.value=0.675}
 const g=Number(slider.value);document.getElementById('efv').textContent=fmt(g,3);
 const other=ev.total-ev.stages.electricity_production_wtt,evt=other+1000*elec*g/(1-td);
 document.getElementById('whatif').textContent=`EV ${fmt(evt)} vs petrol ${fmt(ice.total)} g/km → ${fmt(100*(1-evt/ice.total))}% lower (meter factor ${fmt(g/(1-td),3)} kg CO2/kWh)`;
 const be=(ice.total-other)/1000/elec*(1-td);
 document.getElementById('breakeven').textContent=`Break-even grid factor (EV = petrol): ${fmt(be,3)} kg CO2/kWh at generation, i.e. ${fmt(be/(1-td),3)} at the meter. (Static what-if; national generation mix — India runs one integrated grid — with the selected state's T&D losses, which include commercial losses; production and petrol values fixed at this scenario's central values.)`}
const stSel=document.getElementById('st');const TD=Object.values(DB.records).filter(d=>d.id.endsWith('.td_loss_share.fy2023_24')).map(d=>[d.geography==='IN'?'All India':d.name.replace('T&D losses, ','').replace(' (share of energy available)',''),d.value]).sort((a,b)=>a[0]==='All India'?-1:b[0]==='All India'?1:a[0].localeCompare(b[0]));
TD.forEach(([n,v])=>{const o=document.createElement('option');o.value=v;o.textContent=`${n} (${(100*v).toFixed(2)}%)`;stSel.appendChild(o)});stSel.onchange=()=>whatif(false);
sel.onchange=draw;document.getElementById('ef').oninput=()=>whatif(false);window.onresize=draw;draw();
</script></body></html>"""


def main() -> None:
    results = json.loads((ROOT / "eval/results/scenarios_full.json").read_text())
    commit = json.loads((ROOT / "eval/results/latest.json").read_text())["commit"]
    db = FactorDB.load()
    dbj = {"records": {k: json.loads(r.model_dump_json()) for k, r in db.records.items()},
           "sources": {k: json.loads(s.model_dump_json()) for k, s in db.sources.items()}}
    html = (TEMPLATE.replace("__RESULTS__", json.dumps(results, default=float))
            .replace("__DB__", json.dumps(dbj)).replace("__COMMIT__", commit))
    out = ROOT / "deliverables" / "dashboard"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"wrote {out / 'index.html'} ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
