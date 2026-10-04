from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import argparse, json
import numpy as np
import pandas as pd

from eval.sim.world import make_world
from eval.sim.calibration import ASER2024_GOVT_STD3
from components.trust_audit.core import forensic_flags, select_audit, retest, adjust, assessments_frame, detection_auc


def _block_truth(world):
    return world.children.groupby("udise_code").read_goal.mean().reset_index(name="true").merge(world.schools[["udise_code","block_lgd","grade3_enrolment"]], on="udise_code")


def _block_mae(world, vals, col):
    truth = _block_truth(world)
    est = truth[["udise_code","block_lgd","grade3_enrolment","true"]].merge(vals[["udise_code", col]], on="udise_code")
    blk = est.groupby("block_lgd").apply(lambda g: pd.Series({
        "true": np.average(g["true"], weights=g["grade3_enrolment"]),
        "est": np.average(g[col], weights=g["grade3_enrolment"]),
    }), include_groups=False).reset_index()
    return float((blk["est"] - blk["true"]).abs().mean() * 100)


def _coverage(world, vals):
    truth = _block_truth(world)
    est = truth.merge(vals, on="udise_code")
    rows=[]
    for b,g in est.groupby("block_lgd"):
        w=g["grade3_enrolment"].to_numpy(float); w=w/w.sum()
        mean=float(np.sum(w*g["adjusted_pct_meeting_goal"]))
        se=float(np.sqrt(np.sum((w*g["adjusted_se"])**2)))
        true=float(np.average(g["true"], weights=g["grade3_enrolment"]))
        rows.append((mean-1.645*se <= true <= mean+1.645*se))
    return float(np.mean(rows))


def evaluate_seed(seed:int, budget_frac:float=0.10, world=None, risk=None):
    w=world if world is not None else make_world(seed, dict(ASER2024_GOVT_STD3)); pub=w.public_view(); n=len(pub.schools); b=max(1, round(n*budget_frac))
    risk=risk if risk is not None else forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank)
    raw=risk[["udise_code","reported_pct_meeting_goal"]]
    res={"seed":seed,"budget_frac":budget_frac,"raw_block_mae_pp":_block_mae(w,raw,"reported_pct_meeting_goal"),"risk_auc":detection_auc(risk,w.truth_school)}
    for design in ["random","risk_pps"]:
        sel=select_audit(pub.schools,risk,b,design=design,seed=seed+17)
        audit=retest(w,sel,children_per_school=12,seed=seed+31)
        ta=adjust(pub.schools,risk,audit,sel)
        vals=assessments_frame(ta)
        res[f"{design}_block_mae_pp"]=_block_mae(w,vals,"adjusted_pct_meeting_goal")
        res[f"{design}_coverage90"]=_coverage(w,vals)
    return res


def evaluate(seeds=(1,2,3,4,5), budget_fracs=(0.05,0.10,0.20)):
    rows=[]
    for s in seeds:
        w=make_world(int(s)); pub=w.public_view()
        risk=forensic_flags(pub.teacher_reports, pub.schools, pub.item_responses, pub.item_bank)
        for bf in budget_fracs:
            rows.append(evaluate_seed(int(s), float(bf), world=w, risk=risk))
    return pd.DataFrame(rows)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--seeds", default="1,2,3,4,5"); ap.add_argument("--json", action="store_true")
    args=ap.parse_args(); seeds=[int(x) for x in args.seeds.split(",") if x]
    df=evaluate(seeds)
    metric=float(df[df.budget_frac.eq(0.10)]["risk_pps_block_mae_pp"].mean())
    print(f"METRIC block_mae_pp_at_10pct_budget={metric:.3f}")
    sec=df.groupby("budget_frac").agg({"raw_block_mae_pp":["mean","std"],"random_block_mae_pp":["mean","std"],"risk_pps_block_mae_pp":["mean","std"],"risk_auc":["mean","std"],"risk_pps_coverage90":["mean","std"]})
    print(sec.to_string(float_format=lambda x: f"{x:.3f}"))
    if args.json: print(df.to_json(orient="records"))
if __name__ == "__main__": main()
