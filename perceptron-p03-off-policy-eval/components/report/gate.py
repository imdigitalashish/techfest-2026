"""C10 Report — overlap gate: say "can't tell from these logs" instead of printing a confident wrong number.

Truth-free diagnostics on the logs used for an off-policy term (weights w_i = pi_target(A_i|X_i) / pscore_i, rewards r_i):
  ess_frac  = (sum w)^2 / (n * sum w^2)              effective sample size as a share of n (overlap)
  ess_r     = (sum w r)^2 / sum (w r)^2              effective number of contributing rewards (sparse clicks)
  z_mean_w  = (mean(w) - 1) / (sd(w) / sqrt(n))      E[w] = 1 when propensities are right and the support covers the target
Rule (thresholds calibrated on the simulator only: eval/calibrate_gate.py -> eval/gate_rule.json):
  abstain if ess_frac < tau_ess or ess_r < tau_r or |z_mean_w| > tau_z.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

RULE = Path(__file__).resolve().parents[2] / "eval" / "gate_rule.json"


def diagnostics(w: np.ndarray, r: np.ndarray) -> dict:
    w, r = np.asarray(w, float), np.asarray(r, float)
    n = len(w)
    wr = w * r
    sd = w.std(ddof=1)
    z = (w.mean() - 1.0) / (sd / np.sqrt(n)) if sd > 0 else (0.0 if np.isclose(w.mean(), 1.0) else np.inf)
    return {
        "ess_frac": float(w.sum() ** 2 / (n * (w ** 2).sum())),
        "ess_r": float(wr.sum() ** 2 / (wr ** 2).sum()) if (wr ** 2).sum() > 0 else 0.0,
        "z_mean_w": float(z),
        "max_w": float(w.max()),
        "n": int(n),
    }


def load_rule(path: Path = RULE) -> dict:
    return json.loads(path.read_text())


def decide(diag: dict, rule: dict) -> tuple[bool, list[str]]:
    """Returns (answer?, reasons for abstaining)."""
    reasons = []
    if diag["ess_frac"] < rule["tau_ess"]:
        reasons.append(f"ESS/n {diag['ess_frac']:.4f} < {rule['tau_ess']}")
    if diag["ess_r"] < rule["tau_r"]:
        reasons.append(f"effective rewards {diag['ess_r']:.0f} < {rule['tau_r']}")
    if abs(diag["z_mean_w"]) > rule["tau_z"]:
        reasons.append(f"|mean-weight z| {abs(diag['z_mean_w']):.1f} > {rule['tau_z']}")
    return (not reasons), reasons
