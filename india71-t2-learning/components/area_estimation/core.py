from __future__ import annotations
from typing import Iterable
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from architecture.contracts.fln_contracts import AreaEstimate, AreaLevel, SourceSystem, Subject, TrustAssessment


def _clip(x): return float(np.clip(x,0,1))

def survey_anchor(survey_anchor: pd.DataFrame, subject="language") -> tuple[float,float,int]:
    s=survey_anchor[survey_anchor.subject.eq(subject)] if not survey_anchor.empty else survey_anchor
    if s.empty: return (float("nan"), float("nan"), 0)
    p=float(s.meets_goal.mean()); n=len(s); se=float(np.sqrt(max(p*(1-p),1e-6)/max(n,1)))
    return p,se,n

def teacher_direct(public_world, subject="language") -> pd.DataFrame:
    goal=4 if subject=="language" else 3
    r=public_world.teacher_reports[public_world.teacher_reports.subject.eq(subject)]
    sch=r.groupby("udise_code").reported_level.apply(lambda x: float((x>=goal).mean())).reset_index(name="estimate")
    return public_world.schools[["udise_code","block_lgd","district_lgd","grade3_enrolment"]].merge(sch,on="udise_code",how="left").fillna({"estimate":0.0})

def trust_frame(assessments: Iterable[TrustAssessment], public_world) -> pd.DataFrame:
    df=pd.DataFrame([a.model_dump() for a in assessments])
    df=df.rename(columns={"adjusted_pct_meeting_goal":"estimate","adjusted_se":"school_se"})
    return public_world.schools[["udise_code","block_lgd","district_lgd","grade3_enrolment","single_teacher","share_sc","share_st","ptr","infra_index"]].merge(df,on="udise_code",how="left")

def aggregate_blocks(school_est: pd.DataFrame, value_col="estimate", se_col: str|None=None) -> pd.DataFrame:
    rows=[]
    for b,g in school_est.groupby("block_lgd"):
        w=g.grade3_enrolment.to_numpy(float); w=w/w.sum()
        est=float(np.sum(w*g[value_col].astype(float)))
        se=float(np.sqrt(np.sum((w*g[se_col].fillna(0.08).astype(float))**2))) if se_col and se_col in g else float(np.sqrt(max(est*(1-est),1e-6)/max(g.grade3_enrolment.sum(),1)))
        rows.append({"block_lgd":b,"estimate":est,"se":max(se,0.01),"n_children":int(g.grade3_enrolment.sum())})
    return pd.DataFrame(rows)

ANCHOR_DEFF = 2.0  # ASSUMPTION used only by the legacy path when no cluster variance is available


def fh_benchmark_arrays(y, V, X, wts, p_anchor: float, var_anchor: float):
    """Fay-Herriot empirical-Bayes block estimates + precision-weighted benchmarking to an anchor.

    y: direct block estimates; V: their variances; X: block covariates (B x p); wts: children per block.
    With few blocks (~6 per district) only a couple of covariates are used. The anchor pulls the district
    aggregate only in proportion to its relative precision; its variance is propagated into every block SE.
    Returns (theta, se).
    """
    y = np.asarray(y, float); V = np.maximum(np.asarray(V, float), 1e-6); X = np.asarray(X, float); wts = np.asarray(wts, float)
    B = len(y); wbar = float(np.average(y, weights=wts))
    if B >= 4:
        mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd == 0] = 1.0
        pred = Ridge(alpha=1.0).fit((X - mu) / sd, y).predict((X - mu) / sd)
        pred = np.nan_to_num(pred, nan=wbar, posinf=wbar, neginf=0.0)
    else:
        pred = np.full(B, wbar)
    A = max(0.0, float(np.var(y - pred, ddof=min(3, B - 1)) - np.mean(V))) if B > 3 else 0.0
    gamma = A / (A + V) if A > 0 else np.zeros_like(V)
    theta = gamma * y + (1 - gamma) * pred
    se = np.sqrt(gamma * V + (1 - gamma) ** 2 * np.maximum(A, 1e-4) + (1 - gamma) ** 2 * np.mean(V) / max(B, 1))
    if np.isfinite(p_anchor) and np.isfinite(var_anchor):
        w = wts / wts.sum()
        agg = float(np.sum(w * theta)); var_agg = float(np.sum((w * se) ** 2))
        k = var_agg / (var_agg + var_anchor)
        theta = np.clip(theta + k * (p_anchor - agg), 0, 1)
        se = np.sqrt(se ** 2 + (k ** 2) * var_anchor)
    return theta, se


def fay_herriot_benchmark(public_world, school_est: pd.DataFrame, subject="language") -> pd.DataFrame:
    """Legacy DataFrame path (kept for the dashboard); the calibrated path is components.trust_audit.assurance."""
    blk=aggregate_blocks(school_est,"estimate","school_se")
    cov=public_world.schools.groupby("block_lgd").agg(single_teacher=("single_teacher","mean"),infra_index=("infra_index","mean"),n_children=("grade3_enrolment","sum")).reset_index()
    d=blk.merge(cov,on=["block_lgd","n_children"],how="left")
    p_anchor,se_anchor,_=survey_anchor(public_world.survey_anchor,subject)
    theta,se=fh_benchmark_arrays(d.estimate.to_numpy(float), d.se.to_numpy(float)**2, d[["single_teacher","infra_index"]].astype(float).fillna(0).to_numpy(), d.n_children.to_numpy(float), p_anchor, ANCHOR_DEFF*se_anchor**2 if np.isfinite(se_anchor) else float("nan"))
    d["estimate"]=theta; d["se"]=se
    return d[["block_lgd","estimate","se","n_children"]]


def to_area_estimates(blocks: pd.DataFrame, method: str, subject="language", sources=None, district_code="2701") -> list[AreaEstimate]:
    sources=sources or [SourceSystem.STATE_ASSESSMENT]
    out=[]
    for _,r in blocks.iterrows():
        lo=_clip(r.estimate-1.645*r.se); hi=_clip(r.estimate+1.645*r.se)
        out.append(AreaEstimate(area_level=AreaLevel.BLOCK, area_code=str(r.block_lgd), subject=Subject.LANGUAGE if subject=="language" else Subject.NUMERACY, grade=3, estimate=_clip(r.estimate), ci_low=min(lo,hi), ci_high=max(lo,hi), n_children=int(r.n_children), method=method, sources_used=sources))
    est=float(np.average(blocks.estimate,weights=blocks.n_children)); se=float(np.sqrt(np.sum(((blocks.n_children/blocks.n_children.sum())*blocks.se)**2)))
    out.append(AreaEstimate(area_level=AreaLevel.DISTRICT, area_code=district_code, subject=Subject.LANGUAGE if subject=="language" else Subject.NUMERACY, grade=3, estimate=_clip(est), ci_low=_clip(est-1.645*se), ci_high=_clip(est+1.645*se), n_children=int(blocks.n_children.sum()), method=method, sources_used=sources))
    return out

def estimate_areas(public_world, assessments: Iterable[TrustAssessment], subject="language") -> dict[str, list[AreaEstimate]]:
    raw=aggregate_blocks(teacher_direct(public_world,subject),"estimate")
    tf=trust_frame(assessments,public_world)
    adj=aggregate_blocks(tf,"estimate","school_se")
    fh=fay_herriot_benchmark(public_world,tf,subject)
    return {"baseline_direct":to_area_estimates(raw,"baseline_direct",subject,[SourceSystem.STATE_ASSESSMENT],public_world.schools.district_lgd.iloc[0]),
            "audit_adjusted_direct":to_area_estimates(adj,"audit_adjusted_direct",subject,[SourceSystem.STATE_ASSESSMENT,SourceSystem.AUDIT_RETEST],public_world.schools.district_lgd.iloc[0]),
            "fh_benchmarked":to_area_estimates(fh,"fay_herriot_benchmarked_to_survey_anchor",subject,[SourceSystem.STATE_ASSESSMENT,SourceSystem.AUDIT_RETEST,SourceSystem.ASER],public_world.schools.district_lgd.iloc[0])}

def evaluate_area(world, area_estimates: list[AreaEstimate]) -> dict:
    est=pd.DataFrame([a.model_dump() for a in area_estimates if str(a.area_level)=="AreaLevel.BLOCK" or a.area_level.value=="block"])
    truth=world.children.groupby("udise_code").read_goal.mean().reset_index(name="true").merge(world.schools[["udise_code","block_lgd","grade3_enrolment"]],on="udise_code")
    t=truth.groupby("block_lgd").apply(lambda g: pd.Series({"true":np.average(g.true,weights=g.grade3_enrolment)}), include_groups=False).reset_index()
    j=est.merge(t,left_on="area_code",right_on="block_lgd")
    rmse=float(np.sqrt(np.mean((j.estimate-j.true)**2))*100); cov=float(np.mean((j.ci_low<=j.true)&(j.true<=j.ci_high)))
    dist=[a for a in area_estimates if a.area_level.value=="district"][0]
    anch,_,_=survey_anchor(world.survey_anchor)
    return {"block_rmse_pp":rmse,"coverage90":cov,"aggregate_anchor_abs_diff_pp":float(abs(dist.estimate-anch)*100)}
