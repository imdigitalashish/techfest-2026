"""Measurement assurance (spike 2): moderated block estimates with calibrated prediction intervals.

Point estimate (public data + the re-test sample only):
  1. Strata: K quantile groups of the public risk score (from `forensic_flags`).
  2. Re-test misclassification: a random subsample of re-tested children is assessed twice by independent
     assessors; the disagreement rate d = 2e(1-e) gives e, and each school's re-test share is corrected
     a_hat = (a - e) / (1 - 2e)  (assumes symmetric, independent assessor errors; left unclipped so that
     schools near 0 % are not biased upward).
  3. Stratum reporting bias b_s = mean of (reported - a_hat) over audited schools, weighted by
     enrolment / inclusion probability (children-weighted Horvitz-Thompson ratio estimator).
  4. School estimate t_i = clip(reported_i - b_s(i), 0, 1); block direct estimate = enrolment-weighted mean,
     with an analytic variance (shared stratum-bias error + school-specific deviations).
  5. Fay-Herriot shrinkage across blocks + precision-weighted benchmarking to the survey anchor
     (`components.area_estimation.core.fh_benchmark_arrays`).

Intervals: a parametric bootstrap of the WHOLE pipeline. Each replicate draws pseudo-true school rates from
the fitted bias model (stratum bias + school-specific deviation with the estimated within-stratum variance),
re-draws the audit selection with the same design, the re-tested children (hypergeometric, with
misclassification and double checks) and the anchor sample, re-runs steps 1-5, and records
(estimate - pseudo-truth) per block. The 90 % interval is estimate - [q95, q05] of that error distribution.

Only `retest` in core.py touches hidden truth; everything here uses public data and the re-test sample.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from components.trust_audit.core import GOAL_LEVEL, select_audit

BLOCK_COVARIATES = ["single_teacher", "infra_index"]


class AssuranceUnavailable(RuntimeError):
    """Raised instead of publishing intervals when the independent re-test did not materialise as designed."""


@dataclass
class Context:
    """Public, fixed inputs for one district (arrays aligned to `schools` row order)."""
    schools: pd.DataFrame
    risk: pd.DataFrame          # forensic_flags output (udise_code, risk_score, reported_pct_meeting_goal, ...)
    n: np.ndarray               # Grade-3 enrolment per school
    r: np.ndarray               # teacher-reported share meeting the goal (census)
    risk_score: np.ndarray
    strata: np.ndarray          # int 0..K-1
    block_idx: np.ndarray       # int 0..B-1
    blocks: list
    Xb: np.ndarray              # block covariates (B x p)
    Nb: np.ndarray              # children per block
    k_strata: int


@dataclass
class Fit:
    school_est: np.ndarray
    block_direct: np.ndarray
    block_direct_var: np.ndarray
    block_fh: np.ndarray
    bias_s: np.ndarray
    var_bias_s: np.ndarray
    sig2e_s: np.ndarray
    eps: float
    p_anchor: float
    var_anchor: float
    n_audited: int
    extras: dict = field(default_factory=dict)


def make_context(schools: pd.DataFrame, risk: pd.DataFrame, k_strata: int = 4) -> Context:
    df = schools[["udise_code", "block_lgd", "grade3_enrolment"] + BLOCK_COVARIATES].merge(
        risk[["udise_code", "risk_score", "reported_pct_meeting_goal"]], on="udise_code", how="left")
    rs = df["risk_score"].fillna(df["risk_score"].median()).to_numpy(float)
    edges = np.quantile(rs, np.linspace(0, 1, k_strata + 1)[1:-1])
    strata = np.searchsorted(edges, rs, side="right")
    blocks = sorted(df["block_lgd"].unique())
    bidx = np.array([blocks.index(b) for b in df["block_lgd"]])
    n = df["grade3_enrolment"].to_numpy(float)
    Xb = np.vstack([np.bincount(bidx, weights=df[c].astype(float).to_numpy() , minlength=len(blocks)) / np.bincount(bidx, minlength=len(blocks)) for c in BLOCK_COVARIATES]).T
    Nb = np.bincount(bidx, weights=n, minlength=len(blocks))
    return Context(schools=schools, risk=risk, n=n, r=df["reported_pct_meeting_goal"].fillna(0).to_numpy(float), risk_score=rs,
                   strata=strata, block_idx=bidx, blocks=blocks, Xb=Xb, Nb=Nb, k_strata=k_strata)


def misclassification_rate(n_double: float, n_disagree: float) -> float:
    if n_double <= 0:
        return 0.0
    d = min(n_disagree / n_double, 0.49)
    return float(np.clip((1 - np.sqrt(max(0.0, 1 - 2 * d))) / 2, 0.0, 0.2))


def anchor_summary(k: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Ratio estimate and cluster (between-school) variance of the anchor share."""
    k = np.asarray(k, float); y = np.asarray(y, float); J = len(k)
    if J == 0 or k.sum() == 0:
        return float("nan"), float("nan")
    p = y.sum() / k.sum()
    if J < 2:
        return float(p), float(max(p * (1 - p) / k.sum(), 1e-5))
    kbar = k.mean(); pj = y / np.maximum(k, 1)
    var = float(np.sum((k / kbar) ** 2 * (pj - p) ** 2) / (J * (J - 1)))
    return float(p), max(var, 1e-6)


def benchmark_only(theta, V, wts, p_anchor: float, var_anchor: float):
    """Precision-weighted benchmarking of block estimates to the survey anchor (shift common to all blocks)."""
    theta = np.asarray(theta, float); V = np.asarray(V, float); w = np.asarray(wts, float) / np.sum(wts)
    if not (np.isfinite(p_anchor) and np.isfinite(var_anchor)):
        return theta, np.sqrt(V)
    agg = float(np.sum(w * theta)); var_agg = float(np.sum((w ** 2) * V))
    k = var_agg / (var_agg + var_anchor)
    return np.clip(theta + k * (p_anchor - agg), 0, 1), np.sqrt(V + k ** 2 * var_anchor)


def tau2_adjusted(u: np.ndarray, sv: np.ndarray) -> float:
    """Between-block variance of reporting-bias deviations from block residual means u with sampling variances sv.

    Maximises log(tau2) + loglik(tau2) for u_B ~ N(0, tau2 + sv_B): an adjusted likelihood whose estimate is
    strictly positive, avoiding the zero estimates that plain moment/ML estimators give with ~6 blocks.
    """
    ok = np.isfinite(sv) & (sv > 0)
    u = np.asarray(u, float)[ok]; sv = np.asarray(sv, float)[ok]
    if len(u) < 2:
        return 1e-4
    grid = np.exp(np.linspace(np.log(1e-6), np.log(0.05), 400))
    tot = grid[:, None] + sv[None, :]
    ll = -0.5 * np.sum(np.log(tot) + u[None, :] ** 2 / tot, axis=1) + np.log(grid)
    return float(grid[int(np.argmax(ll))])


def estimate(ctx: Context, sel_idx: np.ndarray, pi: np.ndarray, m: np.ndarray, x_obs: np.ndarray,
             n_double: float, n_disagree: float, p_anchor: float, var_anchor: float, bias_model: str = "linear_r",
             meas_var_mode: str = "v1") -> Fit:
    """Steps 1-5 for one data set. sel_idx/pi/m/x_obs are aligned arrays for the audited schools."""
    K = ctx.k_strata
    eps = misclassification_rate(n_double, n_disagree)
    a = x_obs / np.maximum(m, 1)
    a_hat = (a - eps) / (1 - 2 * eps)  # unclipped: clipping near 0 biases low-performing schools upward
    n_i = ctx.n[sel_idx]
    fpc = np.where(n_i > 1, np.clip((n_i - m) / np.maximum(n_i - 1, 1), 0, 1), 0.0)
    a_s = (x_obs + 0.5) / (m + 1.0)
    if meas_var_mode == "v2":
        # v2 (code-review issue 6): finite-population sampling of true status + independent assessor flips (not removed by FPC)
        p_t = np.clip(a_s, 0.5 / (m + 1.0), 1 - 0.5 / (m + 1.0))
        meas_var = fpc * p_t * (1 - p_t) / np.maximum(m, 1) + eps * (1 - eps) / (np.maximum(m, 1) * (1 - 2 * eps) ** 2)
    else:
        meas_var = a_s * (1 - a_s) / np.maximum(m, 1) * fpc / (1 - 2 * eps) ** 2
    bias = ctx.r[sel_idx] - a_hat
    v = np.minimum(1.0 / np.clip(pi, 1e-3, 1.0), 100.0) * n_i  # HT weight x enrolment: the target is children-weighted
    st = ctx.strata[sel_idx]
    r_sel = ctx.r[sel_idx]
    pooled = float(np.sum(v * bias) / np.sum(v)) if len(v) else 0.0
    # stratum-wise bias model: weighted mean ("mean") or weighted regression on the reported rate ("linear_r")
    coef = np.zeros((K, 2)); coef[:, 0] = pooled
    for s in range(K):
        mask = st == s
        if bias_model == "linear_r" and mask.sum() >= 6 and np.ptp(r_sel[mask]) > 0.05:
            Xs = np.column_stack([np.ones(mask.sum()), r_sel[mask]]); ws = v[mask]
            coef[s] = np.linalg.lstsq(Xs * np.sqrt(ws)[:, None], bias[mask] * np.sqrt(ws), rcond=None)[0]
        elif mask.sum() >= 3:
            coef[s, 0] = float(np.sum(v[mask] * bias[mask]) / np.sum(v[mask]))
    pred_all = coef[ctx.strata, 0] + coef[ctx.strata, 1] * ctx.r
    pred_sel = pred_all[sel_idx]
    bias_s = np.array([float(np.average(pred_all[ctx.strata == s], weights=ctx.n[ctx.strata == s])) if (ctx.strata == s).any() else pooled for s in range(K)])
    var_bias_s = np.zeros(K); sig2e_s = np.zeros(K)
    resid_all, w_all = [], []
    for s in range(K):
        mask = st == s
        if mask.sum() >= 2:
            vs = v[mask]; res = bias[mask] - pred_sel[mask]
            dof = max(mask.sum() - (2 if (bias_model == "linear_r" and coef[s, 1] != 0) else 1), 1)
            s2 = float(np.sum(vs * res ** 2) / np.sum(vs)) * mask.sum() / dof
            sig2e_s[s] = max(s2 - float(np.sum(vs * meas_var[mask]) / np.sum(vs)), 1e-4)
            resid_all.append(res); w_all.append(vs)
    if resid_all:
        fallback = max(float(np.sum(np.concatenate(w_all) * np.concatenate(resid_all) ** 2) / np.sum(np.concatenate(w_all))) - float(np.mean(meas_var)), 1e-4)
    else:
        fallback = 0.02
    for s in range(K):
        mask = st == s
        if mask.sum() < 2:
            sig2e_s[s] = fallback
        if mask.sum() >= 3:
            vs = v[mask]
            var_bias_s[s] = float(np.sum(vs ** 2 * (sig2e_s[s] + meas_var[mask])) / np.sum(vs) ** 2)
        else:
            var_bias_s[s] = float(np.sum(v ** 2 * (fallback + meas_var)) / max(np.sum(v), 1e-9) ** 2) if len(v) else 0.01
    B = len(ctx.blocks); w = ctx.n / ctx.Nb[ctx.block_idx]
    # synthetic block estimate from the calibration model
    synth_school = np.clip(ctx.r - pred_all, 0, 1)
    synthetic = np.bincount(ctx.block_idx, weights=w * synth_school, minlength=B)
    # Fay-Herriot on the bias: direct = block's HT-weighted mean residual of audited schools
    res_sel = bias - pred_sel
    b_sel = ctx.block_idx[sel_idx]
    vb = np.bincount(b_sel, weights=v, minlength=B)
    u_direct = np.where(vb > 0, np.bincount(b_sel, weights=v * res_sel, minlength=B) / np.maximum(vb, 1e-12), 0.0)
    s2_sel = sig2e_s[st] + meas_var
    sv = np.where(vb > 0, np.bincount(b_sel, weights=v ** 2 * s2_sel, minlength=B) / np.maximum(vb, 1e-12) ** 2, np.inf)
    tau2 = tau2_adjusted(u_direct, sv)
    gamma = np.where(np.isfinite(sv), tau2 / (tau2 + sv), 0.0)
    u_hat = gamma * u_direct
    direct = np.clip(synthetic - u_hat, 0, 1)
    school_est = np.clip(synth_school - u_hat[ctx.block_idx], 0, 1)
    W_bs = np.zeros((B, K))
    np.add.at(W_bs, (ctx.block_idx, ctx.strata), w)
    var_direct = (W_bs ** 2) @ var_bias_s + np.bincount(ctx.block_idx, weights=w ** 2 * sig2e_s[ctx.strata], minlength=B) + np.where(np.isfinite(sv), gamma * np.where(np.isfinite(sv), sv, 0.0), tau2)
    fh, _ = benchmark_only(direct, var_direct, ctx.Nb, p_anchor, var_anchor)
    return Fit(school_est, direct, var_direct, fh, bias_s, var_bias_s, sig2e_s, eps, p_anchor, var_anchor, int(len(sel_idx)), extras={"pred_bias": pred_all, "coef": coef, "tau2": tau2, "synthetic": synthetic, "gamma": gamma})


def observed_inputs(ctx: Context, selected: pd.DataFrame, audit: pd.DataFrame, anchor: pd.DataFrame, subject: str = "language"):
    """Convert select_audit / retest / survey_anchor frames into the arrays `estimate` needs."""
    pos = {u: i for i, u in enumerate(ctx.schools["udise_code"])}
    # Validation added after pre-registration (code-review issue 4): refuse to publish intervals when the audit did not
    # materialise as designed. It only raises on incomplete audits, which never occurred in the registered runs.
    planned = set(selected.loc[selected["selected_for_audit"], "udise_code"])
    got = set(audit["udise_code"]) if len(audit) else set()
    if not planned or got != planned:
        raise AssuranceUnavailable(f"re-test returned {len(got)} of {len(planned)} selected schools")
    if (audit["n_audited_children"] <= 0).any() or audit["n_double"].sum() <= 0:
        raise AssuranceUnavailable("re-test has schools with no children or no double-assessed children")
    a = audit.merge(selected[["udise_code", "audit_inclusion_prob"]], on="udise_code", how="left")
    if a["audit_inclusion_prob"].isna().any():
        raise AssuranceUnavailable("missing inclusion probability for a re-tested school")
    sel_idx = np.array([pos[u] for u in a["udise_code"]], dtype=int)
    m = a["n_audited_children"].to_numpy(float)
    x_obs = a["n_meeting_goal_obs"].to_numpy(float)
    pi = a["audit_inclusion_prob"].fillna(1.0).to_numpy(float)
    an = anchor[anchor["subject"].eq(subject)].groupby("udise_code")["meets_goal"].agg(["size", "sum"])
    p_anchor, var_anchor = anchor_summary(an["size"].to_numpy(float), an["sum"].to_numpy(float))
    return sel_idx, pi, m, x_obs, float(a["n_double"].sum()), float(a["n_disagree"].sum()), p_anchor, var_anchor


@dataclass
class Design:
    budget: int
    design: str = "risk_pps"            # v2: "pps_systematic" (exact inclusion probabilities)
    children_per_school: int = 12
    double_check_frac: float = 0.2
    anchor_schools: int = 20
    anchor_children: int = 10
    double_check_mode: str = "per_school"   # v2: "pooled"
    meas_var_mode: str = "v1"               # v2: "v2"


def bootstrap(ctx: Context, fit: Fit, design: Design, R: int = 200, seed: int = 0, bias_model: str = "linear_r") -> dict:
    """Parametric bootstrap of the full pipeline; returns per-block error draws for 'direct' and 'fh'."""
    rng = np.random.default_rng(seed)
    B = len(ctx.blocks); N = len(ctx.n)
    n_int = ctx.n.astype(int)
    sd_e = np.sqrt(fit.sig2e_s[ctx.strata])
    base = ctx.r - fit.extras["pred_bias"]  # pseudo-truth around the synthetic model; block effects drawn below
    err_direct = np.zeros((R, B)); err_fh = np.zeros((R, B))
    risk_df = pd.DataFrame({"udise_code": ctx.schools["udise_code"].to_numpy(), "risk_score": ctx.risk_score})
    eps = fit.eps
    for rep in range(R):
        u_star = rng.normal(0, np.sqrt(fit.extras["tau2"]), B)
        t_star = np.clip(base - u_star[ctx.block_idx] - rng.normal(0, 1, N) * sd_e, 0, 1)
        K_star = np.rint(t_star * n_int).astype(int)
        T_block = np.bincount(ctx.block_idx, weights=K_star, minlength=B) / ctx.Nb
        sel = select_audit(ctx.schools, risk_df, design.budget, design=design.design, seed=int(rng.integers(1 << 31)))
        chosen = np.flatnonzero(sel["selected_for_audit"].to_numpy())
        pi = sel["audit_inclusion_prob"].to_numpy(float)[chosen]
        m = np.minimum(design.children_per_school, n_int[chosen])
        x_true = rng.hypergeometric(K_star[chosen], n_int[chosen] - K_star[chosen], m)
        x_obs = rng.binomial(x_true, 1 - eps) + rng.binomial(m - x_true, eps)
        if design.double_check_mode == "pooled":
            n_double = float(round(design.double_check_frac * m.sum())); n_dis = float(rng.binomial(int(n_double), 2 * eps * (1 - eps)))
        else:
            nd = np.rint(design.double_check_frac * m).astype(int)
            n_double = float(nd.sum()); n_dis = float(rng.binomial(nd, 2 * eps * (1 - eps)).sum())
        aj = rng.choice(N, size=min(design.anchor_schools, N), replace=False)
        kj = np.minimum(design.anchor_children, n_int[aj])
        yj = rng.hypergeometric(K_star[aj], n_int[aj] - K_star[aj], kj)
        p_a, v_a = anchor_summary(kj, yj)
        f = estimate(ctx, chosen, pi, m.astype(float), x_obs.astype(float), n_double, n_dis, p_a, v_a, bias_model=bias_model, meas_var_mode=design.meas_var_mode)
        err_direct[rep] = f.block_direct - T_block
        err_fh[rep] = f.block_fh - T_block
    return {"direct": err_direct, "fh": err_fh}


def intervals(fit: Fit, errors: dict, level: float = 0.90) -> pd.DataFrame:
    a = (1 - level) / 2
    rows = []
    for name, est in [("direct", fit.block_direct), ("fh", fit.block_fh)]:
        e = errors[name]
        lo = np.clip(est - np.quantile(e, 1 - a, axis=0), 0, 1)
        hi = np.clip(est - np.quantile(e, a, axis=0), 0, 1)
        for b in range(len(est)):
            rows.append({"method": name, "block": b, "estimate": float(est[b]), "lo": float(lo[b]), "hi": float(hi[b]),
                         "boot_bias": float(np.mean(e[:, b])), "boot_sd": float(np.std(e[:, b]))})
    return pd.DataFrame(rows)


def run_assurance(public_world, risk: pd.DataFrame, selected: pd.DataFrame, audit: pd.DataFrame, design: Design,
                  subject: str = "language", k_strata: int = 4, R: int = 200, seed: int = 0, bias_model: str = "linear_r") -> tuple[Context, Fit, pd.DataFrame]:
    ctx = make_context(public_world.schools, risk, k_strata)
    sel_idx, pi, m, x_obs, nd, ndis, p_a, v_a = observed_inputs(ctx, selected, audit, public_world.survey_anchor, subject)
    fit = estimate(ctx, sel_idx, pi, m, x_obs, nd, ndis, p_a, v_a, bias_model=bias_model, meas_var_mode=design.meas_var_mode)
    errs = bootstrap(ctx, fit, design, R=R, seed=seed, bias_model=bias_model)
    iv = intervals(fit, errs)
    iv["block_lgd"] = [ctx.blocks[b] for b in iv["block"]]
    return ctx, fit, iv
