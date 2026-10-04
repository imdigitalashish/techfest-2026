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
h2{font-size:17px;margin:0 0 10px}select,input{font:inherit}.row{display:flex;gap:14px;flex-wrap:wrap}.card{flex:1;min-width:210px;border:1px solid #e3e6df;border-radius:8px;padding:12px}
.big{font-size:26px;font-weight:650}.muted{color:#5b6470;font-size:13px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #eceee9;padding:6px 6px;text-align:left;vertical-align:top}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:12px;background:#e8f3ec;color:#14532d}.tag.derived{background:#eef1fb;color:#24357a}.tag.assumption,.tag.UNVERIFIED{background:#fdecea;color:#8a1c12}
.warn{background:#fff7e6;border:1px solid #f0c36d;border-radius:8px;padding:10px 12px;margin-top:10px;font-size:13px}.ok{background:#e8f3ec;border:1px solid #9ccfae;border-radius:8px;padding:10px 12px;margin-top:10px;font-size:13px}
.legend span{display:inline-flex;align-items:center;margin-right:14px;font-size:13px}.legend i{width:12px;height:12px;border-radius:2px;margin-right:5px;display:inline-block}
code{font-size:12px;background:#f1f3ef;padding:1px 4px;border-radius:4px}footer{color:#5b6470;font-size:12px;padding:0 28px 30px;max-width:1180px;margin:0 auto}
</style></head><body>
<header><h1>Green Auto India — India-specific automotive LCA (prototype)</h1>
<p>Case studies: petrol vs electric scooter · sedan cars (petrol / diesel / CNG / electric) · unit: g per vehicle-km (GHG indicator) · every input traceable to a cited record</p></header>
<main>
<section><h2>Scenario</h2><select id="sc"></select><p id="scdesc" class="muted"></p><div id="harm"></div></section>
<section><h2>Life-cycle GHG by stage (central values; whiskers = 90% Monte Carlo interval)</h2><div class="legend" id="legend"></div><svg id="bars" width="100%" height="200"></svg></section>
<section><h2>Comparison with the reference vehicle (paired Monte Carlo)</h2><div class="row" id="cards"></div></section>
<section id="wisec"><h2>What-if: grid emission factor for charging</h2>
<p class="muted">National generation factor with a state T&amp;D-loss adjustment (India runs one integrated grid; state losses FY2023-24 from Lok Sabha USQ 842 include commercial losses — this is not a state generation mix). CEA FY2025-26 at generation: build margin 0.446 · average 0.675 · operating margin 0.963 kg CO<sub>2</sub>/kWh (CO<sub>2</sub> only).</p>
Charging state: <select id="st"></select><br><input type="range" id="ef" min="0" max="1.4" step="0.0001" style="width:60%"> <b id="efv"></b> kg/kWh at generation, effective (same gas basis as the scenario: <span id="efb"></span>)
<p id="whatif" class="big"></p><p id="breakeven" class="muted"></p></section>
<section><h2>Which inputs drive the EV-vs-ICE difference (screening)</h2><div id="gaps"></div>
<p class="muted">Normalized squared Spearman rank correlation between each input and the difference — a screening measure of where better Indian data would help most, not a variance decomposition. Parameter uncertainty only; scenario choices (average vs margin grid) are shown as separate scenarios.</p></section>
<section><h2>Provenance — every input used in this scenario</h2><table id="prov"></table></section>
</main>
<footer>Prototype for Techfest 2026 × MHI × ICAT, Challenge 2 (Green Auto India). Engine: <code>components/lca_engine</code>; eval: <code>python3 eval/eval.py</code> (harness v2, code commit __COMMIT__). Not an ISO 14044 critically reviewed study; results are illustrative and use legacy 2021 vehicle data.</footer>
<script>
const R=__RESULTS__, DB=__DB__;
const COLORS={vehicle_production:"#4b7f52",battery_production:"#9bc53d",maintenance:"#a37c3a",fuel_production_wtt:"#e0a458",electricity_production_wtt:"#3e7cb1",tailpipe_ttw:"#c0392b"};
const NAMES={vehicle_production:"Vehicle production (+recycling)",battery_production:"Battery production",maintenance:"Maintenance",fuel_production_wtt:"Fuel production (WTT)",electricity_production_wtt:"Electricity (generation + T&D)",tailpipe_ttw:"Tailpipe (TTW)"};
const KIND={replication:"verification",decision:"decision",sensitivity:"sensitivity"};
const sel=document.getElementById('sc');const groups={};
Object.entries(R).forEach(([k,r])=>{(groups[r.case]=groups[r.case]||[]).push([k,r])});
Object.entries(groups).forEach(([c,items])=>{const g=document.createElement('optgroup');g.label=c;items.forEach(([k,r])=>{const o=document.createElement('option');o.value=k;o.textContent=`[${KIND[r.kind]||r.kind}] ${r.label}`;g.appendChild(o)});sel.appendChild(g)});
sel.value=R['in2026_avg_co2e']?'in2026_avg_co2e':Object.keys(R)[0];
document.getElementById('legend').innerHTML=Object.keys(NAMES).map(k=>`<span><i style="background:${COLORS[k]}"></i>${NAMES[k]}</span>`).join('');
function fmt(x,d=1){return Number(x).toFixed(d)}
function nice(v){const p=Math.pow(10,Math.floor(Math.log10(v)));return Math.ceil(v/p*2)/2*p}
function draw(){
 const r=R[sel.value];document.getElementById('scdesc').textContent=r.description;
 const fam=r.gas_basis_families.join(', ');
 document.getElementById('harm').innerHTML=r.harmonized?`<div class="ok">Gas basis harmonized: all emission factors on ${fam}.</div>`:`<div class="warn"><b>Partial, unharmonized GHG indicator.</b> Emission factors use different bases (${fam}); CEA grid factors are CO<sub>2</sub>-only at the busbar (no CH<sub>4</sub>/N<sub>2</sub>O or upstream). Read totals as indicative; see the methodology, §Gas basis.</div>`;
 const prods=Object.entries(r.products),svg=document.getElementById('bars'),W=svg.clientWidth||900,L=270,maxv=nice(Math.max(...prods.map(([k,p])=>p.mc_total.p95))*1.12),sx=v=>L+(W-L-80)*v/maxv,H=prods.length*58+30;
 svg.setAttribute('height',H);let h='';prods.forEach(([pid,p],i)=>{let y=12+i*58,x=0;h+=`<text x="0" y="${y+21}" font-size="13">${p.label}</text>`;
  Object.entries(p.stages).forEach(([s,v])=>{h+=`<rect x="${sx(x)}" y="${y}" width="${Math.max(0,sx(x+v)-sx(x))}" height="32" fill="${COLORS[s]||'#999'}"><title>${NAMES[s]||s}: ${fmt(v,2)} g/km</title></rect>`;x+=v});
  const m=p.mc_total;h+=`<line x1="${sx(m.p05)}" x2="${sx(m.p95)}" y1="${y+16}" y2="${y+16}" stroke="#111" stroke-width="1.5"/><line x1="${sx(m.p05)}" x2="${sx(m.p05)}" y1="${y+8}" y2="${y+24}" stroke="#111"/><line x1="${sx(m.p95)}" x2="${sx(m.p95)}" y1="${y+8}" y2="${y+24}" stroke="#111"/>`;
  h+=`<text x="${sx(m.p95)+6}" y="${y+21}" font-size="13" font-weight="600">${fmt(p.total)}</text>`});
 const step=maxv/5;for(let t=0;t<=maxv+1e-9;t+=step){h+=`<text x="${sx(t)}" y="${H-4}" font-size="11" fill="#777">${fmt(t,0)}</text>`}
 svg.innerHTML=h;
 const ref=r.products[r.reference_product];
 document.getElementById('cards').innerHTML=Object.entries(r.comparisons).map(([pid,c])=>{const p=r.products[pid];return `<div class="card"><div class="muted">${p.label} vs ${ref.label}</div><div class="big">${c.reduction_central>=0?fmt(100*c.reduction_central)+"% lower":fmt(-100*c.reduction_central)+"% higher"}</div><div class="muted">90% interval ${fmt(100*c.reduction_mc.p05)} to ${fmt(100*c.reduction_mc.p95)}% · P(lower) ${fmt(100*c.p_lower,0)}%</div><div class="muted">pedigree score ${fmt(p.dq_score,2)} (1 best…5 worst) · India-specific emission factors: ${fmt(100*p.india_footprint_share,0)}% of footprint</div></div>`}).join('')+`<div class="card"><div class="muted">Reference: ${ref.label}</div><div class="big">${fmt(ref.total)} g/km</div><div class="muted">90% interval ${fmt(ref.mc_total.p05)}–${fmt(ref.mc_total.p95)} · n=${r.n_iterations}, seed ${r.seed}</div><div class="muted">pedigree score ${fmt(ref.dq_score,2)} · India-specific emission factors: ${fmt(100*ref.india_footprint_share,0)}% of footprint</div></div>`;
 const imp=r.comparison?r.comparison.importance:(Object.values(r.comparisons)[0]||{}).importance||{};
 document.getElementById('gaps').innerHTML=Object.entries(imp).slice(0,7).map(([k,v])=>`<div style="display:flex;align-items:center;gap:8px;margin:3px 0"><div style="width:${Math.round(420*v)}px;height:14px;background:#14532d"></div><span class="muted">${fmt(100*v)}%</span> <code>${k}</code> <span class="muted">${DB.records[k]?DB.records[k].name:''}</span></div>`).join('');
 const used={};prods.forEach(([pid,p])=>Object.entries(p.params).forEach(([n,rid])=>{(used[rid]=used[rid]||[]).push(p.powertrain+':'+n)}));
 document.getElementById('prov').innerHTML='<tr><th>Used by</th><th>Record</th><th>Value</th><th>Status</th><th>Source · locator · quote</th></tr>'+Object.entries(used).map(([rid,us])=>{const d=DB.records[rid],s=DB.sources[d.source_id];
  return `<tr><td class="muted">${[...new Set(us)].join('<br>')}</td><td>${d.name}<br><span class="muted">${rid}</span></td><td>${d.value} ${d.unit}<br><span class="muted">${d.gas_basis}, ${d.geography}, ${d.reference_year}</span></td><td><span class="tag ${d.status}">${d.status}</span><br><span class="muted">pedigree ${[d.pedigree.reliability,d.pedigree.completeness,d.pedigree.temporal,d.pedigree.geographical,d.pedigree.technological].join('-')}</span></td><td><a href="${s.url}">${s.title}</a> (${s.publisher}, ${s.year})<br><span class="muted">${d.locator}</span>${d.quote?`<br><i class="muted">“${d.quote}”</i>`:''}${d.derivation?`<br><span class="muted">= ${d.derivation}</span>`:''}</td></tr>`}).join('');
 whatif(true)}
function bevOf(r){return Object.values(r.products).find(p=>p.powertrain==='BEV')}
function whatif(reset){
 const r=R[sel.value],ev=bevOf(r),sec=document.getElementById('wisec');
 if(!ev||!ev.params.ef_gen){sec.style.opacity=.45;document.getElementById('whatif').textContent='(What-if available in scenarios that use CEA grid factors.)';document.getElementById('breakeven').textContent='';return}
 sec.style.opacity=1;const ref=r.products[r.reference_product];
 const tdScen=DB.records[ev.params.td].value,stSel=document.getElementById('st');
 if(reset){let o=stSel.querySelector('option[data-scen]');if(!o){o=document.createElement('option');o.dataset.scen='1';stSel.insertBefore(o,stSel.firstChild)}
  o.value=tdScen;o.textContent=`This scenario's loss setting (${(100*tdScen).toFixed(2)}%)`;stSel.value=String(tdScen)}
 const elec=DB.records[ev.params.elec].value/100,td=Number(stSel.value);
 // effective factor at generation implied by the scenario's own electricity stage (CO2 or CO2e, whichever it uses)
 const effGen=ev.stages.electricity_production_wtt/1000/elec*(1-tdScen);
 document.getElementById('efb').textContent=ev.params.gwp_ch4?'CO2e incl. CH4/N2O + coal-mine methane':'CO2 only';
 const slider=document.getElementById('ef');if(reset){slider.value=effGen.toFixed(4)}
 const g=Number(slider.value);document.getElementById('efv').textContent=fmt(g,3);
 const other=ev.total-ev.stages.electricity_production_wtt,evt=other+1000*elec*g/(1-td);
 document.getElementById('whatif').textContent=`EV ${fmt(evt)} vs ${ref.label} ${fmt(ref.total)} g/km → ${evt<=ref.total?fmt(100*(1-evt/ref.total))+'% lower':fmt(100*(evt/ref.total-1))+'% higher'} (meter factor ${fmt(g/(1-td),3)} kg/kWh)`;
 const be=(ref.total-other)/1000/elec*(1-td);
 document.getElementById('breakeven').textContent=`Break-even grid factor (EV = reference): ${fmt(be,3)} kg/kWh at generation, ${fmt(be/(1-td),3)} at the meter (same gas basis as the scenario). Static what-if at central values; consumption at the scenario's central value.`}
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
