from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np, pandas as pd

from eval.sim.world import make_world
from components.trust_audit import forensic_flags, select_audit, retest, adjust
from components.trust_audit.evaluate import evaluate as trust_evaluate
from components.area_estimation import estimate_areas, evaluate_area, survey_anchor
from components.allocation import allocate_camps, evaluate_allocation
from components.dashboard import build_dashboard

SEEDS=[1,2,3,4,5]

def _mean_sd(xs): return f"{np.mean(xs):.3f} ± {np.std(xs,ddof=1):.3f}" if len(xs)>1 else f"{xs[0]:.3f}"

def pipeline(seed:int, write_demo=False):
    w=make_world(seed); pub=w.public_view()
    try:
        __import__("components.diagnostics"); __import__("components.teacher_view")
    except Exception:
        pass
    risk=forensic_flags(pub.teacher_reports,pub.schools,pub.item_responses,pub.item_bank)
    sel=select_audit(pub.schools,risk,max(1,round(0.10*len(pub.schools))),"risk_pps",seed=seed+17)
    audit=retest(w,sel,12,seed=seed+31)
    trust=adjust(pub.schools,risk,audit,sel)
    areas=estimate_areas(pub,trust)
    area_metrics=evaluate_area(w,areas["fh_benchmarked"])
    raw_alloc=allocate_camps(pub,trust,None,"baseline_raw")
    adj_alloc=allocate_camps(pub,trust,None,"audit_adjusted")
    oracle_alloc=allocate_camps(pub,trust,None,"oracle",truth_school=w.truth_school)
    alloc_metrics={"allocation_raw_children":evaluate_allocation(w,raw_alloc),"allocation_adjusted_children":evaluate_allocation(w,adj_alloc),"allocation_oracle_children":evaluate_allocation(w,oracle_alloc)}
    out={"seed":seed,"trust":trust,"areas":areas,"allocations":adj_alloc,"schools":pub.schools,"metrics":{**area_metrics,**alloc_metrics}}
    if write_demo:
        m={"area_block_rmse_pp":f"{area_metrics['block_rmse_pp']:.2f} pp","allocation_gain_children":f"{alloc_metrics['allocation_adjusted_children']:.1f}"}
        build_dashboard({**out,"metrics":m},ROOT/"deliverables/demo")
    return {"seed":seed,**area_metrics,**alloc_metrics}

def main():
    resdir=ROOT/"eval/results"; resdir.mkdir(parents=True,exist_ok=True)
    trust_df=trust_evaluate(SEEDS)
    rows=[pipeline(s,write_demo=(s==SEEDS[0])) for s in SEEDS]
    df=pd.DataFrame(rows)
    metric=float(trust_df[trust_df.budget_frac.eq(0.10)].risk_pps_block_mae_pp.mean())
    baseline={"synthetic":True,"seeds":SEEDS,"trust_audit":json.loads(trust_df.to_json(orient="records")),"pipeline":rows,"block_mae_pp_at_10pct_budget":metric}
    (resdir/"baseline.json").write_text(json.dumps(baseline,indent=2),encoding="utf-8")
    summary=[]; summary.append("# SYNTHETIC FLN evaluation summary\n"); summary.append("Command: `python3 eval/run_eval.py`\n")
    summary.append("| Metric | mean ± sd |\n|---|---:|\n")
    summary.append(f"| Trust risk-PPS block MAE @10% audit (pp) | {_mean_sd(trust_df[trust_df.budget_frac.eq(0.10)].risk_pps_block_mae_pp.tolist())} |\n")
    summary.append(f"| Raw reported block MAE @10% audit row (pp) | {_mean_sd(trust_df[trust_df.budget_frac.eq(0.10)].raw_block_mae_pp.tolist())} |\n")
    summary.append(f"| Inflation detection AUC | {_mean_sd(trust_df[trust_df.budget_frac.eq(0.10)].risk_auc.tolist())} |\n")
    summary.append(f"| Area FH benchmarked block RMSE (pp) | {_mean_sd(df.block_rmse_pp.tolist())} |\n")
    summary.append(f"| Area 90% CI coverage | {_mean_sd(df.coverage90.tolist())} |\n")
    summary.append(f"| Aggregate-anchor abs diff (pp) | {_mean_sd(df.aggregate_anchor_abs_diff_pp.tolist())} |\n")
    summary.append(f"| Allocation raw children reached | {_mean_sd(df.allocation_raw_children.tolist())} |\n")
    summary.append(f"| Allocation adjusted children reached | {_mean_sd(df.allocation_adjusted_children.tolist())} |\n")
    summary.append(f"| Allocation oracle children reached | {_mean_sd(df.allocation_oracle_children.tolist())} |\n")
    (resdir/"summary.md").write_text("".join(summary),encoding="utf-8")
    print(f"METRIC block_mae_pp_at_10pct_budget={metric:.3f}")
    print("SYNTHETIC seeds=1..5")
    print("trust_risk_pps_mae_pp_10pct",_mean_sd(trust_df[trust_df.budget_frac.eq(0.10)].risk_pps_block_mae_pp.tolist()))
    print("area_block_rmse_pp",_mean_sd(df.block_rmse_pp.tolist()))
    print("allocation_adjusted_children",_mean_sd(df.allocation_adjusted_children.tolist()))
    print(f"wrote {resdir/'baseline.json'} {resdir/'summary.md'} {ROOT/'deliverables/demo/block_dashboard.html'}")
if __name__=="__main__": main()
