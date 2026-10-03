from __future__ import annotations
from typing import Iterable
import numpy as np, pandas as pd
from architecture.contracts.fln_contracts import AllocationDecision, TrustAssessment


def _reported(public_world, subject="language"):
    goal=4 if subject=="language" else 3
    r=public_world.teacher_reports[public_world.teacher_reports.subject.eq(subject)]
    return r.groupby("udise_code").reported_level.apply(lambda x: float((x>=goal).mean())).reset_index(name="p_goal")

def _assessment_df(assessments: Iterable[TrustAssessment]):
    return pd.DataFrame([{"udise_code":a.udise_code,"p_goal":a.adjusted_pct_meeting_goal} for a in assessments])

def allocate_camps(public_world, assessments: Iterable[TrustAssessment]|None=None, R:int|None=None, strategy="audit_adjusted", effect_pp:float=0.15, truth_school:pd.DataFrame|None=None) -> list[AllocationDecision]:
    schools=public_world.schools.copy(); R=int(R or max(1, round(0.10*len(schools))))
    if strategy=="baseline_raw" or assessments is None:
        est=_reported(public_world)
    elif strategy=="oracle" and truth_school is not None:
        est=truth_school[["udise_code","true_read_goal_rate"]].rename(columns={"true_read_goal_rate":"p_goal"})
    else:
        est=_assessment_df(assessments)
    df=schools.merge(est,on="udise_code",how="left"); df["p_goal"]=df.p_goal.fillna(df.p_goal.mean() if df.p_goal.notna().any() else 0.25)
    df["equity_weight"]=1.0+0.45*df.share_st.fillna(0)+0.30*df.share_sc.fillna(0)+0.20*df.single_teacher.astype(float)
    df["expected_gain"]=df.grade3_enrolment*(1-df.p_goal)*effect_pp
    df["score"]=df.expected_gain*df.equity_weight
    top=df.sort_values(["score","grade3_enrolment"],ascending=False).head(R)
    return [AllocationDecision(area_code=str(r.udise_code),resource="remedial_camp",units=1.0,expected_additional_children_meeting_goal=float(r.expected_gain),equity_weighted_score=float(r.score),rationale=f"SYNTHETIC {strategy}: TaRL camp effect assumption +{effect_pp:.0%}; prioritized below-goal children with SC/ST and single-teacher equity weights.") for _,r in top.iterrows()]

def evaluate_allocation(world, decisions: list[AllocationDecision], effect_pp:float=0.15) -> float:
    chosen={d.area_code for d in decisions}
    df=world.schools[["udise_code","grade3_enrolment"]].merge(world.truth_school[["udise_code","true_read_goal_rate"]],on="udise_code")
    return float((df[df.udise_code.isin(chosen)].grade3_enrolment*(1-df[df.udise_code.isin(chosen)].true_read_goal_rate)*effect_pp).sum())
