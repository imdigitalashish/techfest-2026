"""Lead-only: re-measure C6 variants after the allocator fix. Usage: python eval/rebaseline_c6.py <name> <shrink-json>"""
import json
import os
import pathlib
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402

import sakriya_paths  # noqa: F401,E402
from components.targeting import engine  # noqa: E402
from eval.targeting_eval import run  # noqa: E402

name, shrink = sys.argv[1], json.loads(sys.argv[2])
engine.CONFIG["shrink"] = shrink
runs = [run(s, 20000, 10.0, verbose=False) for s in (0, 1, 2)]
pol = ["random", "status_quo", "risk_bc", "ate_best", "uplift", "oracle"]
summary = {p: {k: float(np.mean([r[p][k] for r in runs])) for k in ("normalised", "value", "women_share")} for p in pol}
summary["uplift"]["normalised_sd"] = float(np.std([r["uplift"]["normalised"] for r in runs], ddof=1))
out = ROOT / "eval" / "results" / f"c6_{name}.json"
out.write_text(json.dumps({"variant": name, "shrink": shrink, "summary": summary, "runs": runs}, indent=1, default=str))
print(name, {p: round(summary[p]["normalised"], 4) for p in pol}, "uplift_sd", round(summary["uplift"]["normalised_sd"], 4))
