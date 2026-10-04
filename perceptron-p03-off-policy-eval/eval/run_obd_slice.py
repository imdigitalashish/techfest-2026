"""Real Open Bandit Dataset check on large slices — implements eval/preregistration_obd.md (registered 13:06:47 IST).

Reproduce (from perceptron-p03-off-policy-eval/):
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/random/all/all.csv --budget_mb 30
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/bts/all/all.csv --budget_mb 100
  bash eval/fetch_obd_sample.sh          # only for prior_bts.yaml
  nice -n 10 .venv/bin/python eval/run_obd_slice.py
Writes eval/results/obd_slice_summary.md and eval/results/obd_slice.json. REAL data (ZOZOTOWN Open Bandit Dataset, campaign All).
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
from run_obd import bts_action_dist  # noqa: E402

S = ROOT / ".data" / "obd_slice"
HOUR = 3_600_000_000_000
B_BOOT, SEED = 500, 1
Z = 1.959963984540054


def load(path):
    d = np.load(path)
    out = {k: d[k] for k in d.files}
    if out["ts"].max() < 10 ** 17:  # slices written before the unit fix hold microseconds (pandas 3 infers "us")
        out["ts"] = out["ts"] * 1000
    return out


def sub(d, m):
    return {k: v[m] for k, v in d.items()}


def wald_mean(x):
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))


def boot_se(phi, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(phi)
    return float(np.std([phi[rng.integers(0, n, n)].mean() for _ in range(B_BOOT)], ddof=1))


def fit_q(a, k, r, n_items, m=200.0):
    q = np.zeros((n_items, 3))
    for kk in range(3):
        s = k == kk
        ctr = r[s].mean()
        n_ak = np.bincount(a[s], minlength=n_items)
        c_ak = np.bincount(a[s], weights=r[s], minlength=n_items)
        q[:, kk] = (c_ak + m * ctr) / (n_ak + m)
    return q


def ope_terms(d, pi, hidx=None, n_items=80):
    """Influence terms of IPW/SNIPW/DM/DR for evaluation policy pi: static (n_items, 3) or hourly (H, n_items, 3)."""
    a, k, r, ps = d["item"].astype(int), d["pos"].astype(int) - 1, d["click"].astype(float), d["ps"]
    pa = pi[a, k] if pi.ndim == 2 else pi[hidx, a, k]
    w = pa / ps
    out = {"IPW": w * r}
    v = (w * r).sum() / w.sum()
    out["SNIPW"] = v + w * (r - v) / w.mean()
    folds = np.random.default_rng(0).integers(0, 2, len(r))
    dm, ql = np.zeros(len(r)), np.zeros(len(r))
    for f in (0, 1):
        tr, te = folds != f, folds == f
        q = fit_q(a[tr], k[tr], r[tr], n_items)
        if pi.ndim == 2:
            dm[te] = (pi * q).sum(0)[k[te]]
        else:
            dm[te] = (pi * q[None]).sum(1)[hidx[te], k[te]]
        ql[te] = q[a[te], k[te]]
    out["DM"] = dm
    out["DR"] = dm + w * (r - ql)
    diag = {"ess": float(w.sum() ** 2 / (w ** 2).sum()), "max_w": float(w.max()), "n": int(len(w))}
    return out, diag


def main():
    R, B = load(S / "random" / "all" / "all.npz"), load(S / "bts" / "all" / "all.npz")
    n_items = int(max(R["item"].max(), B["item"].max())) + 1
    t0 = max(R["ts"].min(), B["ts"].min())
    t_end = (B["ts"].max() // HOUR) * HOUR
    R, B = sub(R, (R["ts"] >= t0) & (R["ts"] < t_end)), sub(B, (B["ts"] >= t0) & (B["ts"] < t_end))
    h0 = t0 // HOUR
    R["h"], B["h"] = R["ts"] // HOUR - h0, B["ts"] // HOUR - h0
    H = int(max(R["h"].max(), B["h"].max())) + 1
    nb_h = np.bincount(B["h"], minlength=H)
    keep_h = nb_h >= 1000
    R, B = sub(R, keep_h[R["h"]]), sub(B, keep_h[B["h"]])
    res = {"window": {"start_utc": str(np.datetime64(int(t0), "ns")), "end_utc": str(np.datetime64(int(t_end), "ns")),
                      "hours": int(H), "hours_dropped": int((~keep_h).sum()), "n_random": int(len(R["ts"])),
                      "n_bts": int(len(B["ts"])), "n_items": n_items}}
    md = ["# Real OBD check on large slices — results (REAL data; campaign All)", "",
          "Implements [`preregistration_obd.md`](../preregistration_obd.md) (registered 2026-10-04 13:06:47 IST, before these results). "
          "Reproduce: see the header of `eval/run_obd_slice.py`.", "",
          f"Window W: {res['window']['start_utc']} → {res['window']['end_utc']} UTC ({H} hours; {res['window']['hours_dropped']} dropped for < 1,000 BTS rows). "
          f"Rows in W: Random {len(R['ts']):,} · BTS {len(B['ts']):,}. Items: {n_items}.", ""]

    # P-hourly reconstruction from BTS (time, item, position) only
    cnt = np.zeros((H, n_items, 3))
    np.add.at(cnt, (B["h"], B["item"].astype(int), B["pos"].astype(int) - 1), 1.0)
    tot = cnt.sum(1, keepdims=True)
    pi_h = np.divide(cnt, tot, out=np.zeros_like(cnt), where=tot > 0)
    pi_s = bts_action_dist(n_sim=400_000)
    pi_u = np.full((n_items, 3), 1.0 / n_items)

    # ---- Analysis 1: did the deployed BTS change within W? ----
    cell = B["item"].astype(int) * 3 + (B["pos"].astype(int) - 1)
    top = np.argsort(-np.bincount(cell, minlength=n_items * 3))[:20]
    bucket = (B["ts"] - t0) // (6 * HOUR)
    nbk = int(bucket.max()) + 1
    ratios, rhos, rows = [], [], []
    for c in top:
        m = cell == c
        meds = np.array([np.median(B["ps"][m & (bucket == j)]) if (m & (bucket == j)).any() else np.nan for j in range(nbk)])
        ok = ~np.isnan(meds)
        ratio = float(np.nanmax(meds) / np.nanmin(meds))
        rho = float(stats.spearmanr(np.arange(nbk)[ok], meds[ok]).statistic)
        ratios.append(ratio)
        rhos.append(rho)
        rows.append((int(c // 3), int(c % 3) + 1, int(m.sum()), float(np.nanmin(meds)), float(np.nanmax(meds)), ratio, rho))
    distinct = []
    for c in top[:5]:
        m = cell == c
        for hh in np.unique(B["h"][m])[:48]:
            distinct.append(len(np.unique(B["ps"][m & (B["h"] == hh)])))
    emp_w = cnt.sum(0) / cnt.sum(0).sum(0, keepdims=True)
    corr_static = float(np.corrcoef(emp_w.ravel(), pi_s.ravel())[0, 1])
    changed = int(sum(r_ >= 1.5 for r_ in ratios))
    res["a1"] = {"cells_ratio_ge_1.5": changed, "decision_changed": changed >= 10, "median_ratio": float(np.median(ratios)),
                 "median_abs_spearman": float(np.median(np.abs(rhos))), "distinct_ps_per_cell_hour_median": float(np.median(distinct)),
                 "corr_wavg_freq_vs_static_prior": corr_static, "buckets_6h": nbk}
    md += ["## Analysis 1 — did the deployed BTS change during W?", "",
           f"**Pre-registered decision:** {'CHANGED' if changed >= 10 else 'NOT CHANGED'} ({changed}/20 top cells have max/min 6-hour median propensity ≥ 1.5; median ratio {np.median(ratios):.2f}; median |Spearman ρ| with time {np.median(np.abs(rhos)):.2f}; {nbk} buckets).",
           f"Distinct logged propensity values per cell-hour (top-5 cells, up to 48 hours each): median {np.median(distinct):.0f}. "
           f"Correlation of the W-average empirical (item, position) frequency with the static-prior Monte Carlo: {corr_static:.3f}.", "",
           "| item | position | BTS rows | min 6h-median ps | max 6h-median ps | max/min | Spearman ρ vs time |", "|---|---|---|---|---|---|---|"]
    md += [f"| {i} | {p} | {n:,} | {lo:.4f} | {hi:.4f} | {ra:.2f} | {rh:+.2f} |" for i, p, n, lo, hi, ra, rh in rows]
    md.append("")

    # ---- Analysis 2: V(BTS) from Random logs, truth = BTS on-policy CTR ----
    tv, tse = wald_mean(B["click"].astype(float))
    res["a2"] = {"truth": tv, "truth_se": tse, "random_ctr": float(R["click"].mean())}
    md += ["## Analysis 2 — standard protocol: V(BTS) from Random logs vs BTS on-policy CTR (same window)", "",
           f"**Truth (BTS on-policy CTR in W):** {tv:.5f} ± {Z * tse:.5f} (95%). Random's own CTR in W: {R['click'].mean():.5f}.", "",
           "| evaluation policy | estimator | V̂(BTS) | 95% CI (bootstrap SE) | relative error | 95% CI of V̂ − truth | consistent? | ESS / n |", "|---|---|---|---|---|---|---|---|"]
    for pname, pi, hidx in (("P-static", pi_s, None), ("P-hourly", pi_h, R["h"])):
        terms, dg = ope_terms(R, pi, hidx, n_items)
        res["a2"][pname] = {"ess": dg["ess"], "n": dg["n"]}
        for e, phi in terms.items():
            v, se = float(phi.mean()), boot_se(phi)
            dlo, dhi = v - tv - Z * np.hypot(se, tse), v - tv + Z * np.hypot(se, tse)
            cons = dlo <= 0 <= dhi
            res["a2"][pname][e] = {"value": v, "se": se, "rel_err": abs(v - tv) / tv, "diff_lo": dlo, "diff_hi": dhi, "consistent": bool(cons)}
            md.append(f"| {pname} | {e} | {v:.5f} | {v - Z * se:.5f}–{v + Z * se:.5f} | {abs(v - tv) / tv:.1%} | {dlo:+.5f}…{dhi:+.5f} | {'yes' if cons else 'NO'} | {dg['ess']:,.0f} / {dg['n']:,} |")
    md.append("")

    # ---- Analysis 3: real before/after with real truth, both directions ----
    def before_after(R1, R2, B1, B2, label):
        cells = {k_: wald_mean(d["click"].astype(float)) for k_, d in (("R1", R1), ("R2", R2), ("B1", B1), ("B2", B2))}
        out = {"label": label, "cells": {k_: {"v": v, "se": s} for k_, (v, s) in cells.items()}}
        lines = []
        for dname, old, new, oldlog1, newlog2, est_old_from_new2, est_new_from_old1 in (
            ("A_deploy_BTS", "R", "B", R1, B2, (B2, pi_u, None), (R1, pi_h, R1["h"])),
            ("B_rollback_to_Random", "B", "R", B1, R2, (R2, pi_h, R2["h"]), (B1, pi_u, None)),
        ):
            vo1, so1 = cells[f"{old}1"]
            vo2, so2 = cells[f"{old}2"]
            vn1, sn1 = cells[f"{new}1"]
            vn2, sn2 = cells[f"{new}2"]
            naive, naive_se = vn2 - vo1, np.hypot(sn2, so1)
            truth, truth_se = vn2 - vo2, np.hypot(sn2, so2)
            t_pol = 0.5 * ((vn1 - vo1) + (vn2 - vo2))
            t_env = 0.5 * ((vo2 - vo1) + (vn2 - vn1))
            t_int = (vn2 - vo2) - (vn1 - vo1)
            t_pol_se = 0.5 * np.sqrt(sn1 ** 2 + so1 ** 2 + sn2 ** 2 + so2 ** 2)
            t_int_se = np.sqrt(sn1 ** 2 + so1 ** 2 + sn2 ** 2 + so2 ** 2)
            d2, pi2, h2 = est_old_from_new2
            terms2, dg2 = ope_terms(d2, pi2, h2, n_items)
            d1, pi1, h1 = est_new_from_old1
            terms1, dg1 = ope_terms(d1, pi1, h1, n_items)
            r2, r1 = d2["click"].astype(float), d1["click"].astype(float)
            rec = {"naive": naive, "naive_se": naive_se, "truth": truth, "truth_se": truth_se,
                   "naive_ci_contains_truth": bool(abs(naive - truth) <= Z * naive_se),
                   "true_env_old": vo2 - vo1, "shapley_truth": {"policy": t_pol, "policy_se": t_pol_se, "env": t_env, "interaction": t_int, "interaction_se": t_int_se},
                   "ess_after": dg2["ess"], "n_after": dg2["n"], "ess_before": dg1["ess"], "n_before": dg1["n"]}
            for e in ("IPW", "SNIPW", "DR"):
                phi_after = r2 - terms2[e]  # policy effect in W2: on-policy new minus OPE old (same rows)
                pe, pe_se = float(phi_after.mean()), boot_se(phi_after)
                vo2_hat_se = boot_se(terms2[e])
                diff = float(terms2[e].mean()) - vo2  # (estimate - truth) = V(W2,old) - V_hat(W2,old)
                diff = -diff
                diff_se = np.hypot(vo2_hat_se, so2)
                phi_before = terms1[e] - r1  # V_hat(W1,new) - V(W1,old) (same rows)
                pb, pb_se = float(phi_before.mean()), boot_se(phi_before)
                s_pol, s_pol_se = 0.5 * (pb + pe), 0.5 * np.hypot(pb_se, pe_se)
                s_int, s_int_se = pe - pb, np.hypot(pb_se, pe_se)
                rec[e] = {"policy_effect_after": pe, "se": pe_se, "minus_truth": diff, "minus_truth_lo": diff - Z * diff_se,
                          "minus_truth_hi": diff + Z * diff_se, "S1_ci_contains_0": bool(abs(diff) <= Z * diff_se),
                          "abs_err": abs(pe - truth), "shapley_policy": s_pol, "shapley_policy_se": s_pol_se,
                          "shapley_env": naive - s_pol, "interaction": s_int, "interaction_se": s_int_se}
            out[dname] = rec
            lines.append(f"| {label} | {dname} | {naive:+.5f} ± {Z * naive_se:.5f} | **{truth:+.5f}** ± {Z * truth_se:.5f} | "
                         f"{rec['DR']['policy_effect_after']:+.5f} ± {Z * rec['DR']['se']:.5f} | {rec['IPW']['policy_effect_after']:+.5f} | {rec['SNIPW']['policy_effect_after']:+.5f} | "
                         f"{'yes' if rec['DR']['S1_ci_contains_0'] else 'NO'} | {abs(naive - truth):.5f} vs {rec['DR']['abs_err']:.5f} | {'yes' if rec['naive_ci_contains_truth'] else 'no'} | {dg2['ess']:,.0f}/{dg2['n']:,} |")
        return out, lines

    t_mid = t0 + (t_end - t0) // 2
    m1R, m1B = R["ts"] < t_mid, B["ts"] < t_mid
    main_res, main_lines = before_after(sub(R, m1R), sub(R, ~m1R), sub(B, m1B), sub(B, ~m1B), "halves")
    res["a3_halves"] = main_res
    hdr = ["| split | direction | naive before/after | truth (concurrent A/B in W2) | DR policy effect | IPW | SNIPW | S1: DR CI(est − truth) ∋ 0 | abs err naive vs DR | naive CI ∋ truth | ESS/n (after logs) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    md += ["## Analysis 3 — real before/after with real truth (W split at its midpoint)", "",
           f"W1 = before ({res['window']['start_utc'][:16]} → {str(np.datetime64(int(t_mid), 'ns'))[:16]} UTC), W2 = after. Direction A: old = Random → new = BTS. Direction B: old = BTS → new = Random.",
           "All four cells V(period, policy) are observed on-policy because both arms ran concurrently; that is the truth. ± = 95% half-width.", ""] + hdr + main_lines + [""]
    md += ["**2×2 Shapley decomposition (DR fills the two unobserved cells) vs all-on-policy truth:**", "",
           "| direction | policy (Shapley) est vs truth | env (Shapley) est vs truth | interaction est vs truth |", "|---|---|---|---|"]
    for dname in ("A_deploy_BTS", "B_rollback_to_Random"):
        rr, st = main_res[dname]["DR"], main_res[dname]["shapley_truth"]
        md.append(f"| {dname} | {rr['shapley_policy']:+.5f} ± {Z * rr['shapley_policy_se']:.5f} vs {st['policy']:+.5f} ± {Z * st['policy_se']:.5f} | "
                  f"{rr['shapley_env']:+.5f} vs {st['env']:+.5f} | {rr['interaction']:+.5f} ± {Z * rr['interaction_se']:.5f} vs {st['interaction']:+.5f} ± {Z * st['interaction_se']:.5f} |")
    md.append("")

    # Secondary: ordered pairs of whole UTC days inside W
    day = R["ts"] // (24 * HOUR)
    dayB = B["ts"] // (24 * HOUR)
    full_days = [int(d_) for d_ in np.unique(dayB) if (d_ * 24 * HOUR >= t0) and ((d_ + 1) * 24 * HOUR <= t_end)
                 and keep_h[max(0, int(d_ * 24 - h0)):int(d_ * 24 - h0) + 24].all()]
    sec_lines, res["a3_daypairs"] = [], {}
    for d1, d2 in combinations(full_days, 2):
        lab = f"{np.datetime64(d1, 'D')}→{np.datetime64(d2, 'D')}"
        r_, l_ = before_after(sub(R, day == d1), sub(R, day == d2), sub(B, dayB == d1), sub(B, dayB == d2), lab)
        res["a3_daypairs"][lab] = r_
        sec_lines += l_
    md += ["### Secondary — every ordered pair of whole UTC days inside W (all reported)", ""] + hdr + sec_lines + [""]

    # Balance check in W2
    tvds = {}
    R2, B2 = sub(R, ~m1R), sub(B, ~m1B)
    for j in range(4):
        x, y = R2[f"uf{j}"], B2[f"uf{j}"]
        cats, cnts = np.unique(np.concatenate([x, y]), return_counts=True)
        topc = cats[np.argsort(-cnts)[:50]]
        px = np.array([np.mean(x == c) for c in topc] + [np.mean(~np.isin(x, topc))])
        py = np.array([np.mean(y == c) for c in topc] + [np.mean(~np.isin(y, topc))])
        tvds[f"user_feature_{j}"] = float(0.5 * np.abs(px - py).sum())
    res["balance_tvd_W2"] = tvds
    flag = any(v > 0.05 for v in tvds.values())
    md += ["## Balance check (W2): total-variation distance between arms, per user feature (top 50 categories + other)", "",
           " · ".join(f"{k_}: {v:.4f}" for k_, v in tvds.items()) + (" — **CAVEAT: arm assignment may not be randomised by user**" if flag else " — all ≤ 0.05 (no caveat)"), ""]

    out = ROOT / "eval" / "results"
    (out / "obd_slice.json").write_text(json.dumps(res, indent=1, default=float))
    (out / "obd_slice_summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
