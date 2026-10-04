"""Pilot sample size (two-proportion, two-sided test). Inputs are ASSUMPTIONS for illustration, not estimates:
baseline six-month meaningful-use rate 20%, minimum detectable effect +2 percentage points, alpha 0.05, power 0.80;
for BC-cluster randomisation, an illustrative ICC of 0.02 with 50 persons per cluster.
Usage: .venv/bin/python eval/power_calc.py -> eval/results/power_calc.json"""
import json
import math
import pathlib

from scipy.stats import norm

p0, d, alpha, power, icc, m = 0.20, 0.02, 0.05, 0.80, 0.02, 50
p1 = p0 + d
z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
n_ind = math.ceil(z ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / d ** 2)
deff = 1 + (m - 1) * icc
out = {"baseline": p0, "mde_pp": 100 * d, "alpha": alpha, "power": power, "n_per_arm_individual": n_ind,
       "icc": icc, "cluster_size": m, "design_effect": deff, "n_per_arm_clustered": math.ceil(n_ind * deff),
       "clusters_per_arm": math.ceil(n_ind * deff / m)}
pathlib.Path(__file__).resolve().parents[1].joinpath("eval", "results", "power_calc.json").write_text(json.dumps(out, indent=1))
print(out)
