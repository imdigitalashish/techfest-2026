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
    # dispatch on the requested strategy first and fail closed (code-review issue 9); the oracle is evaluation-only
    if strategy=="baseline_raw":
        est=_reported(public_world)
    elif strategy=="oracle":
        if truth_school is None: raise ValueError("oracle strategy is evaluation-only and needs truth_school")
        est=truth_school[["udise_code","true_read_goal_rate"]].rename(columns={"true_read_goal_rate":"p_goal"})
    elif strategy=="audit_adjusted":
        if not assessments: raise ValueError("audit_adjusted strategy needs assessments")
        est=_assessment_df(assessments)
    else:
        raise ValueError(f"unknown strategy {strategy!r}")
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


def target_schools(schools: pd.DataFrame, p_goal: pd.Series, R: int) -> list[str]:
    """Top-R schools by equity-weighted below-goal children, given estimated school goal rates (udise-indexed)."""
    df = schools[["udise_code", "grade3_enrolment", "share_st", "share_sc", "single_teacher"]].copy()
    df["p_goal"] = df["udise_code"].map(p_goal).fillna(p_goal.mean())
    df["equity_weight"] = 1.0 + 0.45 * df.share_st.fillna(0) + 0.30 * df.share_sc.fillna(0) + 0.20 * df.single_teacher.astype(float)
    df["score"] = df.grade3_enrolment * (1 - df.p_goal) * df.equity_weight
    return df.sort_values(["score", "grade3_enrolment"], ascending=False).head(int(R)).udise_code.tolist()


def below_goal_children_reached(world, chosen: list[str], subject: str = "language") -> float:
    """Effect-free targeting metric: true number of below-goal children in the targeted schools."""
    col = "read_goal" if subject == "language" else "math_goal"
    c = world.children[world.children.udise_code.isin(set(chosen))]
    return float((~c[col].astype(bool)).sum())
