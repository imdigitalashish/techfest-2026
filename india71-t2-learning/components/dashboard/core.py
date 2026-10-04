from __future__ import annotations
import html, json
from pathlib import Path
import pandas as pd


def _pct(x):
    try: return f"{100*float(x):.1f}%"
    except Exception: return "—"

def _bar(value, lo=None, hi=None):
    v=max(0,min(100,100*float(value))); l=max(0,min(100,100*float(lo if lo is not None else value))); h=max(0,min(100,100*float(hi if hi is not None else value)))
    return f'<svg class="ci" viewBox="0 0 100 10" role="img" aria-label="estimate {_pct(value)}"><line x1="{l:.1f}" x2="{h:.1f}" y1="5" y2="5"/><circle cx="{v:.1f}" cy="5" r="3"/></svg>'

def _dump(obj):
    if hasattr(obj,"model_dump"):
        d=obj.model_dump();
        return {k: (v.value if hasattr(v,"value") else v) for k,v in d.items()}
    if isinstance(obj,dict): return {k:_dump(v) for k,v in obj.items()}
    if isinstance(obj,list): return [_dump(v) for v in obj]
    return obj

def build_dashboard(outputs: dict, out_dir: str | Path) -> Path:
    out=Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    trust=outputs.get("trust",[]); areas=outputs.get("areas",{}); alloc=outputs.get("allocations",[]); metrics=outputs.get("metrics",{})
    trust_df=pd.DataFrame([_dump(t) for t in trust]) if trust else pd.DataFrame()
    area_list=areas.get("fh_benchmarked", areas if isinstance(areas,list) else [])
    area_df=pd.DataFrame([_dump(a) for a in area_list]) if area_list else pd.DataFrame()
    blocks=area_df[area_df.area_level.eq("block")].copy() if not area_df.empty else pd.DataFrame()
    district=area_df[area_df.area_level.eq("district")].iloc[0].to_dict() if not area_df.empty and area_df.area_level.eq("district").any() else {}
    schools=outputs.get("schools")
    if schools is not None and not trust_df.empty:
        t=trust_df.merge(schools[["udise_code","block_lgd"]],on="udise_code",how="left")
        by=t.groupby("block_lgd").agg(raw=("reported_pct_meeting_goal","mean"),audited=("selected_for_audit","sum"),flags=("flags",lambda x: sum(len(v) for v in x if isinstance(v,list)))).reset_index()
        blocks=blocks.merge(by,left_on="area_code",right_on="block_lgd",how="left")
    adf=pd.DataFrame([_dump(a) for a in alloc]) if alloc else pd.DataFrame()
    if not adf.empty and schools is not None:
        camps=adf.merge(schools[["udise_code","block_lgd"]],left_on="area_code",right_on="udise_code",how="left").groupby("block_lgd").units.sum().reset_index(name="camps")
        blocks=blocks.merge(camps,left_on="area_code",right_on="block_lgd",how="left",suffixes=("","_camp"))
    rows=[]
    for _,r in blocks.sort_values("area_code").iterrows():
        flags = 0 if pd.isna(r.get("flags", 0)) else int(r.get("flags", 0) or 0)
        audited = 0 if pd.isna(r.get("audited", 0)) else int(r.get("audited", 0) or 0)
        camps = 0 if pd.isna(r.get("camps", 0)) else int(r.get("camps", 0) or 0)
        trust_class="high" if flags>30 else "med" if flags>10 else "low"
        rows.append(f"<tr><td>{html.escape(str(r.area_code))}</td><td>{_pct(r.get('raw',0))}</td><td><strong>{_pct(r.estimate)}</strong></td><td>{_bar(r.estimate,r.ci_low,r.ci_high)}</td><td><span class='pill {trust_class}'>{flags} flags</span></td><td>{audited}</td><td>{camps}</td></tr>")
    json_path=out/"block_dashboard_outputs.json"; json_path.write_text(json.dumps(_dump(outputs),indent=2,default=str),encoding="utf-8")
    html_text=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SYNTHETIC FLN Trust Dashboard</title><style>
:root{{--ink:#17211b;--muted:#516258;--paper:#fbf8ef;--panel:#fffdf7;--green:#176b4d;--amber:#b46a20;--red:#a33831;--line:#ded5c4;--blue:#215a8f}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top left,#e8f3dc,transparent 34rem),var(--paper);color:var(--ink);font:15px/1.5 ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1180px;margin:auto;padding:32px 20px 48px}}header{{display:grid;grid-template-columns:1.6fr 1fr;gap:20px;align-items:end;margin-bottom:22px}}h1{{font-size:clamp(2rem,4vw,4.8rem);line-height:.95;margin:0;letter-spacing:-.04em}}.banner{{background:#17211b;color:#fff7d6;padding:10px 14px;border-radius:999px;display:inline-block;font-weight:800;margin-bottom:18px}}.summary{{background:var(--panel);border:1px solid var(--line);box-shadow:0 14px 38px rgba(0,0,0,.10);border-radius:26px;padding:20px}}.summary b{{font-size:2rem;color:var(--green)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}}.tile{{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:16px;min-height:112px}}.tile span{{display:block;color:var(--muted);font-size:.85rem}}.tile strong{{font-size:1.8rem}}table{{width:100%;border-collapse:separate;border-spacing:0;background:var(--panel);border:1px solid var(--line);border-radius:24px;overflow:hidden;box-shadow:0 18px 46px rgba(0,0,0,.09)}}th,td{{padding:13px 14px;text-align:left;border-bottom:1px solid var(--line)}}th{{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:#5d5b4d;background:#f4eddc}}tr:last-child td{{border-bottom:0}}.ci{{width:160px;height:24px}}.ci line{{stroke:var(--amber);stroke-width:2;stroke-linecap:round}}.ci circle{{fill:var(--green)}}.pill{{border-radius:999px;padding:4px 9px;font-weight:750;font-size:.82rem}}.pill.low{{background:#e4f2dc;color:#285b31}}.pill.med{{background:#fff0c7;color:#7d520e}}.pill.high{{background:#ffe0db;color:#8d2c25}}footer{{color:var(--muted);margin-top:18px}}@media(max-width:760px){{header,.grid{{grid-template-columns:1fr}}table{{font-size:13px}}th,td{{padding:10px 8px}}.ci{{width:96px}}}}
</style></head><body><main><div class='banner'>SYNTHETIC DATA — simulated district calibrated to published aggregates</div><header><h1>District FLN trust picture</h1><section class='summary'><span>Survey anchor vs benchmarked aggregate</span><br><b>{_pct(district.get('estimate',0))}</b><p>Block estimates are audit-adjusted, small-area shrunk, and benchmarked to the district survey anchor within sampling error.</p></section></header><section class='grid'><div class='tile'><span>Risk-PPS audit MAE @10%</span><strong>{metrics.get('block_mae_pp_at_10pct_budget','—')}</strong></div><div class='tile'><span>Area RMSE</span><strong>{metrics.get('area_block_rmse_pp','—')}</strong></div><div class='tile'><span>Allocation gain</span><strong>{metrics.get('allocation_gain_children','—')}</strong></div><div class='tile'><span>Dashboard status</span><strong>Demo</strong></div></section><table><thead><tr><th>Block</th><th>Raw reported</th><th>Audit-adjusted</th><th>90% CI</th><th>Trust flags</th><th>Schools audited</th><th>Allocated camps</th></tr></thead><tbody>{''.join(rows)}</tbody></table><footer>All figures are synthetic and for Techfest 2026 decision-support prototyping only. JSON companion: block_dashboard_outputs.json.</footer></main></body></html>"""
    path=out/"block_dashboard.html"; path.write_text(html_text,encoding="utf-8")
    return path
