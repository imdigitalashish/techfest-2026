"""Sensitivity of the C5 capture–recapture conclusion to model choice and linkage radius.

For each policy (fixed independence model; AIC over non-saturated models; BIC over all; AIC over all = mse.py default)
and radius (100/150/250 m): national estimate and the state validation (median ratio, median |ln ratio|, 90% CI
coverage) on states with >= 100 official stations. Usage: .venv/bin/python -W ignore components/census_completeness/mse_sensitivity.py
"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import mse as M  # noqa: E402

def run(policy, radius, B=200):
    rng = np.random.default_rng(M.SEED)
    d = M.link(M.load_sources(), radius=radius); h = M.histories(d)
    pcs = pd.read_csv(f"{M.R_}/components/charger_ingest/data/official_pcs_statewise.csv")
    off = {M.key(s): int(v) for s, v in pcs[pcs.source == "pib2151390"][["state", "pcs_total"]].values}
    models = {"indep": [()], "aic_nonsat": [m for m in M.MODELS if len(m) < 3], "bic_all": M.MODELS, "aic_all": M.MODELS}[policy]
    def est(cells):
        n_obs = cells.sum(); fits = {m: M.fit(cells, m) for m in models}; fits = {m: f for m, f in fits.items() if f}
        if not fits: return None
        k = lambda m: len(M.design(m)[0])
        crit = (lambda m: fits[m][1] + (np.log(n_obs) - 2) * k(m)) if policy == "bic_all" else (lambda m: fits[m][1])
        mb = min(fits, key=crit); N = n_obs + fits[mb][0]
        boots = []
        for _ in range(B):  # re-select the model inside each replicate (within this policy's model set)
            yb = rng.multinomial(int(n_obs), cells / n_obs).astype(float)
            fb = {m: M.fit(yb, m) for m in models}; fb = {m: f for m, f in fb.items() if f}
            if fb:
                mbb = min(fb, key=lambda m: fb[m][1] + ((np.log(n_obs) - 2) * k(m) if policy == "bic_all" else 0)); boots.append(n_obs + fb[mbb][0])
        lo, hi = np.percentile(boots, [5, 95]) if len(boots) > 50 else (np.nan, np.nan)
        return N, lo, hi, "+".join(mb) or "indep"
    rows = []
    for st, g in h.groupby("state_key"):
        if off.get(st, 0) >= 100:
            r = est(M.cells_of(g))
            if r: rows.append((st, off[st], *r))
    df = pd.DataFrame(rows, columns=["state", "official", "N", "lo", "hi", "model"])
    lr = np.log(df.N / df.official)
    nat = est(M.cells_of(h))
    return {"policy": policy, "radius_m": radius, "sites": int(len(h)), "national": round(nat[0]), "national_model": nat[3],
            "states": int(len(df)), "median_ratio": round(float(np.median(df.N / df.official)), 3),
            "median_abs_log": round(float(np.median(np.abs(lr))), 3),
            "ci_coverage": round(float(((df.official >= df.lo) & (df.official <= df.hi)).mean()), 3),
            "passes": bool(np.median(np.abs(lr)) < np.log(1.25) and ((df.official >= df.lo) & (df.official <= df.hi)).mean() >= 0.8)}

if __name__ == "__main__":
    out = [run(p, 150) for p in ("aic_all", "aic_nonsat", "bic_all", "indep")] + [run("aic_all", r) for r in (100, 250)]
    json.dump(out, open(f"{M.R_}/eval/results/c5_mse_sensitivity.json", "w"), indent=1)
    print(pd.DataFrame(out).to_string(index=False))
