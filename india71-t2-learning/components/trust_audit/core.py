from __future__ import annotations

from datetime import datetime
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import roc_auc_score

from architecture.contracts.fln_contracts import Provenance, SourceSystem, Subject, TrustAssessment

GOAL_LEVEL = {"language": 4, "numeracy": 3}
SUBJECT_ENUM = {"language": Subject.LANGUAGE, "numeracy": Subject.NUMERACY}
FEATURES = ["reported_pct_meeting_goal", "heaping_at_goal", "within_school_variance", "beginner_share", "gap_vs_classroom", "gap_vs_block_peers", "gap_vs_covariates"]


def _rank01(s: pd.Series, high: bool = True) -> pd.Series:
    if s.isna().all():
        return pd.Series(0.0, index=s.index)
    r = s.fillna(s.median()).rank(method="average", pct=True)
    return r if high else 1.0 - r


def _reported_school(reports: pd.DataFrame, subject: str) -> pd.DataFrame:
    goal = GOAL_LEVEL[subject]
    r = reports[reports["subject"].eq(subject)].copy()
    if r.empty:
        return pd.DataFrame(columns=["udise_code", "reported_pct_meeting_goal", "heaping_at_goal", "within_school_variance", "beginner_share", "n_reported"])
    return r.groupby("udise_code").agg(
        reported_pct_meeting_goal=("reported_level", lambda x: float((x >= goal).mean())),
        heaping_at_goal=("reported_level", lambda x: float((x == goal).mean())),
        within_school_variance=("reported_level", lambda x: float(np.var(x, ddof=0))),
        beginner_share=("reported_level", lambda x: float((x == 0).mean())),
        n_reported=("reported_level", "size"),
    ).reset_index()


def _classroom_goal(item_responses: pd.DataFrame | None, item_bank: pd.DataFrame | None, subject: str) -> pd.DataFrame:
    if item_responses is None or item_bank is None or item_responses.empty or item_bank.empty:
        return pd.DataFrame(columns=["udise_code", "classroom_pct_meeting_goal"])
    goal = GOAL_LEVEL[subject]
    bank = item_bank[(item_bank["subject"].eq(subject)) & (item_bank["level"].ge(goal))][["item_id"]]
    if bank.empty:
        return pd.DataFrame(columns=["udise_code", "classroom_pct_meeting_goal"])
    resp = item_responses[item_responses["subject"].eq(subject)].merge(bank, on="item_id")
    if resp.empty:
        return pd.DataFrame(columns=["udise_code", "classroom_pct_meeting_goal"])
    child = resp.groupby(["udise_code", "student_raw_id"])["score"].mean().reset_index(name="goal_item_score")
    child["classroom_goal"] = child["goal_item_score"] >= 0.5
    return child.groupby("udise_code")["classroom_goal"].mean().reset_index(name="classroom_pct_meeting_goal")


def forensic_flags(school_reports: pd.DataFrame, schools: pd.DataFrame | None = None, item_responses: pd.DataFrame | None = None, item_bank: pd.DataFrame | None = None, subject: str = "language") -> pd.DataFrame:
    """Build transparent school-level inflation risk features from public reports only."""
    base = _reported_school(school_reports, subject)
    if schools is not None and not schools.empty:
        base = schools[["udise_code", "block_lgd", "grade3_enrolment", "single_teacher", "share_sc", "share_st", "ptr", "infra_index"]].merge(base, on="udise_code", how="left")
    for c in ["reported_pct_meeting_goal", "heaping_at_goal", "within_school_variance", "beginner_share"]:
        if c not in base:
            base[c] = np.nan
        base[c] = base[c].fillna(base[c].median() if base[c].notna().any() else 0.0)
    cls = _classroom_goal(item_responses, item_bank, subject)
    base = base.merge(cls, on="udise_code", how="left")
    base["gap_vs_classroom"] = (base["reported_pct_meeting_goal"] - base["classroom_pct_meeting_goal"]).fillna(0.0)
    if "block_lgd" in base:
        block_sum = base.groupby("block_lgd")["reported_pct_meeting_goal"].transform("sum")
        block_n = base.groupby("block_lgd")["reported_pct_meeting_goal"].transform("count")
        peer = np.where(block_n > 1, (block_sum - base["reported_pct_meeting_goal"]) / (block_n - 1), base["reported_pct_meeting_goal"].mean())
        base["gap_vs_block_peers"] = base["reported_pct_meeting_goal"] - peer
    else:
        base["gap_vs_block_peers"] = 0.0
    # UDISE+-covariate residual hook: kept conservative in the spike because public
    # covariates explain little after block/classroom gaps in the synthetic world.
    base["gap_vs_covariates"] = 0.0
    score = (
        0.18 * _rank01(base["reported_pct_meeting_goal"]) +
        0.20 * _rank01(base["heaping_at_goal"]) +
        0.13 * _rank01(base["within_school_variance"], high=False) +
        0.10 * _rank01(base["beginner_share"], high=False) +
        0.20 * _rank01(base["gap_vs_classroom"]) +
        0.10 * _rank01(base["gap_vs_block_peers"]) +
        0.09 * _rank01(base["gap_vs_covariates"])
    )
    base["risk_score"] = np.clip(score, 0, 1)
    flags = []
    for _, row in base.iterrows():
        f = []
        if row.heaping_at_goal >= base.heaping_at_goal.quantile(0.80): f.append("goal_heaping")
        if row.gap_vs_classroom >= max(0.08, base.gap_vs_classroom.quantile(0.80)): f.append("classroom_gap")
        if row.gap_vs_block_peers >= max(0.08, base.gap_vs_block_peers.quantile(0.80)): f.append("block_peer_gap")
        if row.within_school_variance <= base.within_school_variance.quantile(0.20): f.append("low_variance")
        flags.append(f)
    base["flags"] = flags
    return base


def select_audit(schools: pd.DataFrame, risk: pd.DataFrame, budget_schools: int, design: str = "risk_pps", seed: int | None = None, p_min: float = 0.01) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frame = schools[["udise_code"] + (["block_lgd"] if "block_lgd" in schools else [])].merge(risk[["udise_code", "risk_score"]], on="udise_code", how="left")
    n = len(frame); b = int(max(0, min(budget_schools, n)))
    if n == 0:
        return frame.assign(selected_for_audit=False, audit_inclusion_prob=0.0)
    if b == 0:
        return frame.assign(selected_for_audit=False, audit_inclusion_prob=0.0)
    if design == "random":
        prob = np.full(n, b / n)
        chosen = rng.choice(n, size=b, replace=False)
    elif design == "stratified_neyman" and "block_lgd" in frame:
        chosen = []
        prob = np.zeros(n)
        risk_sd = frame.groupby("block_lgd")["risk_score"].transform(lambda x: max(float(x.std(ddof=0)), 0.05))
        weights = frame.groupby("block_lgd")["udise_code"].transform("count") * risk_sd
        alloc = (weights.groupby(frame["block_lgd"]).first() / weights.groupby(frame["block_lgd"]).first().sum() * b).round().astype(int)
        for block, idx in frame.groupby("block_lgd").groups.items():
            idx = np.array(list(idx)); k = int(max(1, min(len(idx), alloc.get(block, 1))))
            chosen.extend(rng.choice(idx, size=k, replace=False).tolist()); prob[idx] = k / len(idx)
        if len(chosen) > b:
            chosen = rng.choice(chosen, size=b, replace=False).tolist()
        elif len(chosen) < b:
            rest = [i for i in range(n) if i not in chosen]
            chosen += rng.choice(rest, size=b-len(chosen), replace=False).tolist()
    else:
        floor = min(float(p_min), b / n * 0.5)
        r = frame["risk_score"].fillna(frame["risk_score"].mean()).to_numpy(dtype=float)
        w = np.maximum(r, 0.02); w = w / w.sum()
        prob = np.clip(floor + max(0.0, b - n * floor) * w, 0, 1)
        sample_w = prob / prob.sum()
        chosen = rng.choice(n, size=b, replace=False, p=sample_w)
    out = frame.copy()
    out["selected_for_audit"] = False
    out.loc[list(chosen), "selected_for_audit"] = True
    out["audit_inclusion_prob"] = np.clip(prob, 1e-6, 1.0)
    return out


def retest(world, selected: pd.DataFrame, children_per_school: int = 12, subject: str = "language", seed: int | None = None,
           double_check_frac: float = 0.2, error_rate: float = 0.03) -> pd.DataFrame:
    """Independent re-test simulator; intentionally the only trust/audit function using hidden truth.

    Each re-tested child's goal status is misrecorded with probability `error_rate` (assessor error).
    A random `double_check_frac` of re-tested children is assessed again by a second, independent assessor
    (same error rate), so the system can estimate the assessor error rate from disagreements.
    """
    rng = np.random.default_rng(seed if seed is not None else getattr(world, "seed", 0) + 1000)
    goal_col = "read_goal" if subject == "language" else "math_goal"
    rows = []
    kids_by_school = world.children.groupby("udise_code")
    for u in selected.loc[selected["selected_for_audit"], "udise_code"]:
        if u not in kids_by_school.groups or goal_col not in world.children:
            continue
        kids = kids_by_school.get_group(u)
        take = min(int(children_per_school), len(kids))
        idx = rng.choice(kids.index.to_numpy(), size=take, replace=False)
        truth = kids.loc[idx, goal_col].astype(bool).to_numpy()
        obs = np.where(rng.random(take) < error_rate, ~truth, truth)
        nd = int(round(double_check_frac * take))
        dbl = rng.choice(take, size=nd, replace=False) if nd > 0 else np.array([], dtype=int)
        obs2 = np.where(rng.random(nd) < error_rate, ~truth[dbl], truth[dbl])
        rows.append({"udise_code": u, "audited_pct_meeting_goal": float(obs.mean()), "n_audited_children": int(take),
                     "n_meeting_goal_obs": int(obs.sum()), "n_double": int(nd), "n_disagree": int((obs2 != obs[dbl]).sum())})
    return pd.DataFrame(rows, columns=["udise_code", "audited_pct_meeting_goal", "n_audited_children", "n_meeting_goal_obs", "n_double", "n_disagree"])


def adjust(schools: pd.DataFrame, risk: pd.DataFrame, audit_sample: pd.DataFrame, selected: pd.DataFrame, subject: str = "language") -> list[TrustAssessment]:
    df = risk.merge(selected[["udise_code", "selected_for_audit", "audit_inclusion_prob"]], on="udise_code", how="left").merge(audit_sample, on="udise_code", how="left")
    df["selected_for_audit"] = df["selected_for_audit"].fillna(False).astype(bool)
    df["audit_inclusion_prob"] = df["audit_inclusion_prob"].fillna(1.0)
    df["bias"] = df["reported_pct_meeting_goal"] - df["audited_pct_meeting_goal"]
    aud = df[df["bias"].notna()].copy()
    if len(aud) >= 4:
        w = np.minimum(1.0 / np.clip(aud["audit_inclusion_prob"].astype(float), 1e-2, 1.0), 100.0)
        avg_bias = float(np.average(aud["bias"].astype(float), weights=w))
        bins = np.quantile(df["risk_score"].astype(float), [0, 0.33, 0.66, 1.0])
        bins = np.unique(bins)
        if len(bins) < 3:
            pred_bias = np.full(len(df), avg_bias)
        else:
            df_bins = pd.cut(df["risk_score"], bins=bins, include_lowest=True, labels=False)
            aud_bins = pd.cut(aud["risk_score"], bins=bins, include_lowest=True, labels=False)
            means = {}
            for bval in sorted(pd.Series(aud_bins).dropna().unique()):
                mask = (aud_bins == bval)
                means[int(bval)] = float(np.average(aud.loc[mask, "bias"], weights=w[mask]))
            pred_bias = np.array([means.get(int(b), avg_bias) if pd.notna(b) else avg_bias for b in df_bins])
        resid = aud["bias"].astype(float).to_numpy() - np.array([pred_bias[df.index.get_loc(i)] for i in aud.index])
        resid_sd = float(np.sqrt(np.average(resid**2, weights=w))) if len(resid) else 0.05
    elif len(aud) > 0:
        pred_bias = np.full(len(df), float(np.average(aud["bias"], weights=1.0/np.clip(aud["audit_inclusion_prob"], 1e-3, 1))))
        resid_sd = float(aud["bias"].std(ddof=0) if len(aud) > 1 else 0.08)
    else:
        pred_bias = np.zeros(len(df)); resid_sd = 0.10
    df["adjusted_pct_meeting_goal"] = np.clip(df["reported_pct_meeting_goal"] - pred_bias, 0, 1)
    n = df.get("n_reported", pd.Series(30, index=df.index)).fillna(30).clip(lower=1)
    binom = np.sqrt(df["adjusted_pct_meeting_goal"] * (1 - df["adjusted_pct_meeting_goal"]) / n)
    df["adjusted_se"] = np.sqrt(binom**2 + min(resid_sd, 0.25)**2 / max(len(aud), 1))
    now = datetime.utcnow()
    out = []
    for _, r in df.iterrows():
        out.append(TrustAssessment(
            udise_code=str(r.udise_code), subject=SUBJECT_ENUM[subject], grade=3,
            reported_pct_meeting_goal=float(np.clip(r.reported_pct_meeting_goal, 0, 1)),
            risk_score=float(np.clip(r.risk_score, 0, 1)), flags=list(r.flags) if isinstance(r.flags, list) else [],
            selected_for_audit=bool(r.selected_for_audit), audit_inclusion_prob=float(np.clip(r.audit_inclusion_prob, 0, 1)),
            audited_pct_meeting_goal=None if pd.isna(r.get("audited_pct_meeting_goal", np.nan)) else float(np.clip(r.audited_pct_meeting_goal, 0, 1)),
            adjusted_pct_meeting_goal=float(np.clip(r.adjusted_pct_meeting_goal, 0, 1)), adjusted_se=float(max(r.adjusted_se, 0.0)),
        ))
    return out


def assessments_frame(assessments: Iterable[TrustAssessment]) -> pd.DataFrame:
    return pd.DataFrame([a.model_dump() for a in assessments])


def detection_auc(risk: pd.DataFrame, truth_school: pd.DataFrame) -> float:
    joined = risk.merge(truth_school[["udise_code", "inflating_school"]], on="udise_code")
    if joined["inflating_school"].nunique() < 2:
        return float("nan")
    return float(roc_auc_score(joined["inflating_school"].astype(int), joined["risk_score"]))
