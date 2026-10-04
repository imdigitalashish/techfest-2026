"""Write eval/results/manifest.json: exact code/input checksums + headline metrics and denominators.

Run: innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/eval/make_manifest.py
"""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ["components/recharge_verifier/verifier.py", "components/twin_simulator/simulate.py",
         "components/recharge_verifier/autoresearch/eval.py", "components/recharge_verifier/autoresearch/eval_v2.py",
         "components/recharge_verifier/autoresearch/eval_v3.py",
         "eval/data/delhi_rain_hourly_openmeteo_default_monsoon2024_2025.csv"]
RUNS = {"v1_dev": "recharge_v1_dev.json", "v1_holdout": "recharge_v1_holdout.json",
        "v2_dev": "recharge_v1_evalv2_dev.json", "v2_holdout": "recharge_v1_evalv2_holdout.json",
        "v3_dev": "recharge_v1_evalv3_dev.json", "v3_holdout": "recharge_v1_evalv3_holdout.json"}
sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()  # noqa: E731
try:
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
except Exception:  # noqa: BLE001
    head = None
out = {"written_against_commit_parent": head, "sha256": {f: sha(f) for f in FILES},
       "rain_source": "Open-Meteo historical archive, default model (not pinned), hourly; minute pattern synthetic (seeded Dirichlet)",
       "scoring_unit": "detected event windows with true infiltration >= 0.2 m3 (a window can contain several storms)",
       "runs": {}}
for k, f in RUNS.items():
    r = json.loads((ROOT / "eval/results" / f).read_text())
    out["runs"][k] = {"file": f"eval/results/{f}", "split": r["split"], "rain_period": r["rain_period"],
                      "event_mdape": round(r["event_mdape"], 3), "event_ape_p90": round(r["event_ape_p90"], 3),
                      "false_implausible_rate": round(r["false_implausible_rate"], 4),
                      "clogging_precision": r["clogging_precision"], "clogging_recall": r["clogging_recall"],
                      "fake_recall": r["fake_recall"], "counts": r.get("counts")}
(ROOT / "eval/results/manifest.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: (v["event_mdape"], v["counts"]["scored_windows_true_infil_ge_0.2m3"]) for k, v in out["runs"].items()}))
