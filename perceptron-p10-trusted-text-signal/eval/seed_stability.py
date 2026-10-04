"""Seed stability of headline metrics (LightGBM subsampling seeds 0, 1, 2; no oracle grid).

    for s in 1 2; do PYTHONPATH=. nice -n 10 .venv/bin/python eval/run_baselines.py --tag seed_minilm_s$s --scorer minilm --no-oracle --seed $s; done
    PYTHONPATH=. .venv/bin/python eval/seed_stability.py      # seed 0 = text_minilm_v1
"""
import json
from pathlib import Path

import numpy as np

R = Path("eval/results")
runs = {0: "text_minilm_v1", 1: "seed_minilm_s1", 2: "seed_minilm_s2"}
paths = {
    "split_cov": "ablation.fusion.split.coverage", "cqr_cov": "ablation.fusion.cqr_mapie.coverage",
    "aci_cov": "ablation.fusion.cqr_aci.coverage", "aci_width": "ablation.fusion.cqr_aci.mean_width",
    "pinball_fusion": "ablation.fusion.pinball_mean", "pinball_price": "ablation.price_only.pinball_mean",
    "cert_k3_cov": "spike.clean_k3.coverage", "cert_k3_width": "spike.clean_k3.mean_width",
    "cr_aci_clean_cov": "spike.cr_aci.cr_aci_clean.coverage", "cr_aci_pump_cov": "spike.cr_aci.cr_aci_pump.coverage",
    "cr_aci_clean_width": "spike.cr_aci.cr_aci_clean.mean_width", "cqr_aci_clean_width": "spike.cr_aci.cqr_aci_clean.mean_width",
}


def get(d, p):
    for k in p.split("."):
        d = d[k]
    return d


data = {s: json.loads((R / f"{t}.json").read_text()) for s, t in runs.items()}
out = {}
for name, p in paths.items():
    v = np.array([get(data[s], p) for s in runs])
    out[name] = {"seeds": v.tolist(), "mean": float(v.mean()), "sd": float(v.std(ddof=1)), "range": float(v.max() - v.min())}
d = np.array([get(data[s], paths["pinball_price"]) - get(data[s], paths["pinball_fusion"]) for s in runs])
out["pinball_improvement_from_text"] = {"seeds": d.tolist(), "mean": float(d.mean())}
(R / "seed_stability_minilm.json").write_text(json.dumps(out, indent=2))
for k, v in out.items():
    print(k, [round(x, 4) for x in v["seeds"]], "mean", round(v["mean"], 4), "sd", round(v.get("sd", float("nan")), 4))
