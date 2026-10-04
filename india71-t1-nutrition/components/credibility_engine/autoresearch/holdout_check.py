"""Lead's anti-gaming re-check: fresh seeds + a DIFFERENT fabrication pattern than the frozen eval world.
Run: .venv/bin/python -m components.credibility_engine.autoresearch.holdout_check
"""

import json

import numpy as np
from sklearn.metrics import roc_auc_score

from components.cohort_simulator.simulate import SimConfig, simulate
from components.credibility_engine import engine

WORLDS = {
    "fresh_seeds_same_pattern": dict(),
    "variant_pattern": dict(fab_real_p=0.5, fab_dw=(0.1, 0.4), fab_dl=(0.2, 1.5)),
}


def run(seeds=(101, 102, 103)) -> dict:
    out = {}
    for name, kw in WORLDS.items():
        a_fab, a_bad = [], []
        for seed in seeds:
            sim = simulate(SimConfig(seed=seed, **kw))
            _, _, units = engine.assess(sim["measurements"])
            u = units.merge(sim["geo"][["awc_code", "worker_type"]], left_on="unit_id", right_on="awc_code")
            susp = 1 - u.credibility
            a_fab.append(roc_auc_score((u.worker_type == "fabricating").astype(int), susp))
            a_bad.append(roc_auc_score((u.worker_type != "good").astype(int), susp))
        out[name] = {"auroc_fabricating": round(float(np.mean(a_fab)), 4), "sd": round(float(np.std(a_fab)), 4),
                     "auroc_nongood": round(float(np.mean(a_bad)), 4)}
    out["synthetic"] = True
    print(json.dumps(out))
    return out


if __name__ == "__main__":
    run()
