"""POST-HOC (reviews A8, C3): dependence-aware intervals for the real OBD headline numbers, and a DM interval that
refits the reward model inside the bootstrap.

1. Hour-block bootstrap: per-row DR terms are summed per hour and hours are resampled (2,000 draws), so within-hour
   dependence (same users, slates, adaptive policy state) is kept. Shown next to the row-level (iid) interval.
2. DM refit bootstrap: the full DM procedure (cell CTR fit + prediction) is re-run on each of 80 resamples.
Reproduce: cd perceptron-p03-off-policy-eval && nice -n 10 .venv/bin/python eval/obd_block_bootstrap.py
Writes eval/results/obd_block_bootstrap{.md,.json}. REAL data; post hoc (not in the pre-registration).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))
from run_obd_slice import HOUR, S, Z, bts_action_dist, load, ope_terms, sub  # noqa: E402

RES = ROOT / "eval" / "results"


def block_ci(phi, hour, B=2000, seed=7):
    hs, inv = np.unique(hour, return_inverse=True)
    S_h, N_h = np.bincount(inv, weights=phi), np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(hs), (B, len(hs)))
    means = S_h[draws].sum(1) / N_h[draws].sum(1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)), int(len(hs))


def main():
    o = json.loads((RES / "obd_slice.json").read_text())
    R, B = load(S / "random" / "all" / "all.npz"), load(S / "bts" / "all" / "all.npz")
    t0, t_end = max(R["ts"].min(), B["ts"].min()), (B["ts"].max() // HOUR) * HOUR
    R, B = sub(R, (R["ts"] >= t0) & (R["ts"] < t_end)), sub(B, (B["ts"] >= t0) & (B["ts"] < t_end))
    h0 = t0 // HOUR
    R["h"], B["h"] = R["ts"] // HOUR - h0, B["ts"] // HOUR - h0
    H = int(max(R["h"].max(), B["h"].max())) + 1
    cnt = np.zeros((H, 80, 3))
    np.add.at(cnt, (B["h"], B["item"].astype(int), B["pos"].astype(int) - 1), 1.0)
    tot = cnt.sum(1, keepdims=True)
    pi_h = np.divide(cnt, tot, out=np.zeros_like(cnt), where=tot > 0)
    pi_u = np.full((80, 3), 1.0 / 80)
    t_mid = t0 + (t_end - t0) // 2
    R2, B2 = sub(R, R["ts"] >= t_mid), sub(B, B["ts"] >= t_mid)
    out, L = {}, ["# POST-HOC: dependence-aware intervals for the real OBD headline numbers (reviews A8, C3)", "",
                  "Reproduce: `nice -n 10 .venv/bin/python eval/obd_block_bootstrap.py`. Hour-block bootstrap: 2,000 resamples of whole hours. Units: clicks per 1,000 impressions.", "",
                  "| quantity | estimate | row-level 95% CI (as reported) | hour-block 95% CI | hours | reference | reference inside block CI? |", "|---|---|---|---|---|---|---|"]
    for key, label, d2, pi, hidx, rec in (
        ("halves_A", "halves · deploy BTS: DR after-period effect", B2, pi_u, None, o["a3_halves"]["A_deploy_BTS"]),
        ("halves_B", "halves · roll back: DR after-period effect", R2, pi_h, R2["h"], o["a3_halves"]["B_rollback_to_Random"]),
    ):
        terms, _ = ope_terms(d2, pi, hidx, 80)
        phi = d2["click"].astype(float) - terms["DR"]
        est, se = float(phi.mean()), rec["DR"]["se"]
        lo, hi, nh = block_ci(phi, d2["h"])
        ref = rec["truth"]
        out[key] = {"est": est, "iid_hw": Z * se, "block_lo": lo, "block_hi": hi, "block_hw": (hi - lo) / 2, "hours": nh,
                    "ref": ref, "block_ref_in_ci": bool(lo <= ref <= hi)}
        L.append(f"| {label} | {1000 * est:+.2f} | {1000 * (est - Z * se):+.2f} … {1000 * (est + Z * se):+.2f} | {1000 * lo:+.2f} … {1000 * hi:+.2f} | {nh} | {1000 * ref:+.2f} | {'yes' if lo <= ref <= hi else 'NO'} |")
    pi_s = bts_action_dist(n_sim=400_000)
    for pol, pi, hidx in (("P-static", pi_s, None), ("P-hourly", pi_h, R["h"])):
        terms, _ = ope_terms(R, pi, hidx, 80)
        v = float(terms["DR"].mean())
        lo, hi, nh = block_ci(terms["DR"], R["h"])
        rec = o["a2"][pol]["DR"]
        out[f"a2_{pol}"] = {"est": v, "block_lo": lo, "block_hi": hi, "ref": o["a2"]["truth"], "block_ref_in_ci": bool(lo <= o["a2"]["truth"] <= hi)}
        L.append(f"| Analysis 2 · V(BTS) DR, {pol} | {1000 * v:.3f} | {1000 * (v - Z * rec['se']):.3f} … {1000 * (v + Z * rec['se']):.3f} | {1000 * lo:.3f} … {1000 * hi:.3f} | {nh} | {1000 * o['a2']['truth']:.3f} | {'yes' if lo <= o['a2']['truth'] <= hi else 'NO'} |")
    # DM with the reward model refitted in every resample (review C3)
    n = len(R["click"])
    rng = np.random.default_rng(20261004)
    boot = []
    for _ in range(80):
        ix = rng.integers(0, n, n)
        boot.append(float(ope_terms({k: R[k][ix] for k in ("item", "pos", "click", "ps")}, pi_s, None, 80)[0]["DM"].mean()))
    dm = float(ope_terms(R, pi_s, None, 80)[0]["DM"].mean())
    se_refit = float(np.std(boot, ddof=1))
    diff_lo = dm - o["a2"]["truth"] - Z * np.hypot(se_refit, o["a2"]["truth_se"])
    diff_hi = dm - o["a2"]["truth"] + Z * np.hypot(se_refit, o["a2"]["truth_se"])
    out["dm_refit"] = {"dm": dm, "se_refit": se_refit, "se_fixed_reported": o["a2"]["P-static"]["DM"]["se"],
                       "diff_lo": diff_lo, "diff_hi": diff_hi, "consistent": bool(diff_lo <= 0 <= diff_hi)}
    L += ["", f"**DM (P-static) with the reward model refitted in each of 80 resamples:** SE {1000 * se_refit:.4f} per 1,000 vs {1000 * o['a2']['P-static']['DM']['se']:.6f} reported "
          f"(the fixed-prediction bootstrap ignored model uncertainty). The 95% CI of DM − truth is {1000 * diff_lo:+.3f} … {1000 * diff_hi:+.3f}, so the reported \"NO\" consistency becomes "
          f"**{'yes' if diff_lo <= 0 <= diff_hi else 'no'}**. The pre-registered table is left as is; this row corrects its interpretation."]
    (RES / "obd_block_bootstrap.json").write_text(json.dumps(out, indent=1))
    (RES / "obd_block_bootstrap.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
