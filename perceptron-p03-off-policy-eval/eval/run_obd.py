"""OBD real-data check (v0): estimate the Bernoulli-TS policy's CTR from Uniform-Random logs (off-policy) and
compare with BTS's own on-policy CTR (ground truth), following the protocol of Saito et al. (arXiv:2008.07146).

Data: the small OBD sample shipped in the zr-obp repo (10,000 rows per policy, campaign "All"); fetch with
eval/fetch_obd_sample.sh. Reproduce: cd perceptron-p03-off-policy-eval && .venv/bin/python eval/run_obd.py
Evaluation policy: BTS with the ZOZOTOWN priors (obp/policy/conf/prior_bts.yaml), action distribution over
(item, position) by Monte Carlo (sample theta ~ Beta(alpha, beta), rank top-3), as obp's BernoulliTS does.
Assumption checked below: position p in the CSV (1..3) corresponds to rank p-1 of the BTS ranking.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from components.intervals.ci import bootstrap, wald  # noqa: E402

D = ROOT / ".data" / "obd"
COLS = ["item_id", "position", "click", "propensity_score"]


def bts_action_dist(n_sim=200_000, len_list=3, seed=12345):
    pr = yaml.safe_load(open(D / "prior_bts.yaml"))["all"]
    a, b = np.array(pr["alpha"]), np.array(pr["beta"])
    rng = np.random.default_rng(seed)
    counts = np.zeros((len(a), len_list))
    for _ in range(n_sim // 20_000):
        th = rng.beta(a, b, size=(20_000, len(a)))
        top = np.argsort(-th, axis=1)[:, :len_list]
        for k in range(len_list):
            counts[:, k] += np.bincount(top[:, k], minlength=len(a))
    return counts / counts.sum(0, keepdims=True)


def estimators(pi, a, k, r, ps):
    w = pi[a, k] / ps
    out = {"IPW": w * r}
    v_sn = (w * r).sum() / w.sum()
    out["SNIPW"] = v_sn + w * (r - v_sn) / w.mean()
    # Cross-fitted DM: CTR per (item, position) shrunk toward the position CTR (m pseudo-impressions).
    m, folds = 200.0, np.random.default_rng(0).integers(0, 2, len(r))
    qhat_logged, dm = np.zeros(len(r)), np.zeros(len(r))
    for f in (0, 1):
        tr, te = folds != f, folds == f
        q = np.zeros((pi.shape[0], 3))
        for kk in range(3):
            sel = tr & (k == kk)
            ctr_k = r[sel].mean()
            n_ak = np.bincount(a[sel], minlength=pi.shape[0])
            c_ak = np.bincount(a[sel], weights=r[sel], minlength=pi.shape[0])
            q[:, kk] = (c_ak + m * ctr_k) / (n_ak + m)
        qhat_logged[te] = q[a[te], k[te]]
        dm[te] = (pi[:, k[te]] * q[:, k[te]]).sum(0)
    out["DM"] = dm
    out["DR"] = dm + w * (r - qhat_logged)
    return out, w


def main():
    rnd = pd.read_csv(D / "random" / "all" / "all.csv", usecols=COLS)
    bts = pd.read_csv(D / "bts" / "all" / "all.csv", usecols=COLS)
    pi = bts_action_dist()
    # Check of the evaluation policy: BTS logs record their own propensities; compare with our Monte Carlo.
    est_ps = pi[bts.item_id.values, bts.position.values - 1]
    mae = float(np.abs(est_ps - bts.propensity_score.values).mean())
    corr = float(np.corrcoef(est_ps, bts.propensity_score.values)[0, 1])

    a, k, r, ps = rnd.item_id.values, rnd.position.values - 1, rnd.click.values.astype(float), rnd.propensity_score.values
    emp = np.zeros_like(pi)
    np.add.at(emp, (bts.item_id.values, bts.position.values - 1), 1.0)
    emp /= emp.sum(0, keepdims=True)
    policies = {"BTS static prior (obp protocol)": pi, "BTS week-average (empirical from BTS logs)": emp}
    truth = wald(bts.click.values.astype(float))
    lines = ["# OBD sample check — Random logs → BTS policy value (REAL data, small sample)", "",
             "Reproduce: `bash eval/fetch_obd_sample.sh && .venv/bin/python eval/run_obd.py` (from `perceptron-p03-off-policy-eval/`).", "",
             f"Rows: Random {len(rnd):,} (clicks {int(r.sum())}), BTS {len(bts):,} (clicks {int(bts.click.sum())}). Campaign: All (80 items, 3 positions).",
             f"Evaluation-policy check: our Monte-Carlo BTS propensities vs the BTS logs' own propensities: MAE {mae:.5f}, correlation {corr:.4f}.",
             f"Logged BTS propensity quantiles (10/50/90/99%): {np.round(np.quantile(bts.propensity_score, [.1, .5, .9, .99]), 4).tolist()} vs static-prior MC at the same (item, position): {np.round(np.quantile(est_ps, [.1, .5, .9, .99]), 4).tolist()}. "
             f"Correlation of the empirical BTS (item, position) frequencies with the static-prior MC: {np.corrcoef(emp.ravel(), pi.ravel())[0, 1]:.3f}. "
             "Reading (our hypothesis, UNVERIFIED against the OBP paper): the deployed BTS updated its posterior during the week, so the static prior only approximates it; the week-average policy is the closer match if CTRs are stable within the week.", "",
             f"**Ground truth (BTS on-policy CTR):** {truth.point:.5f} (95% Wald CI {truth.lo:.5f}–{truth.hi:.5f}).",
             f"No-change baseline (Random's own CTR used as the guess for BTS): {r.mean():.5f}.", "",
             "| evaluation policy | estimator | V̂(BTS) | 95% bootstrap CI | relative error vs on-policy CTR | ESS of weights |", "|---|---|---|---|---|---|"]
    for pname, pmat in policies.items():
        out, w = estimators(pmat, a, k, r, ps)
        for name, phi in out.items():
            ci = bootstrap(phi, B=2000, seed=1)
            lines.append(f"| {pname} | {name} | {ci.point:.5f} | {ci.lo:.5f}–{ci.hi:.5f} | {abs(ci.point - truth.point) / truth.point:.1%} | {w.sum() ** 2 / (w ** 2).sum():.0f} |")
    lines += ["", "Caveat: with about 40 clicks per 10k rows, the sampling error of both the estimates and the ground truth is large (±15–30%). "
              "Use the full dataset (about 26M rows) for conclusive numbers."]
    md = "\n".join(lines)
    (ROOT / "eval" / "results").mkdir(parents=True, exist_ok=True)
    (ROOT / "eval" / "results" / "obd_sample_summary.md").write_text(md + "\n")
    print(md)


if __name__ == "__main__":
    main()
