"""Compare every shared numeric leaf of two result JSONs (v1 reproduced by gpt-6-sol; v2 = after review fixes).

    PYTHONPATH=. .venv/bin/python eval/compare_versions.py   -> eval/results/v1_vs_v2_diff.json
"""
import json
from pathlib import Path

R = Path("eval/results")


def leaves(d, pre=""):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from leaves(v, f"{pre}.{k}" if pre else k)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from leaves(v, f"{pre}.{i}")
    elif isinstance(d, (int, float)) and not isinstance(d, bool):
        yield pre, float(d)


out = {}
for a, b in (("baseline_v1", "baseline_v2"), ("text_minilm_v1", "text_minilm_v2")):
    x, y = dict(leaves(json.loads((R / f"{a}.json").read_text()))), dict(leaves(json.loads((R / f"{b}.json").read_text())))
    shared = [k for k in x if k in y and "runtime" not in k]
    diffs = sorted(((abs(x[k] - y[k]), k, x[k], y[k]) for k in shared), reverse=True)
    out[f"{a}_vs_{b}"] = {"shared_numeric_leaves": len(shared), "identical": sum(d == 0 for d, *_ in diffs),
                          "max_abs_diff": diffs[0][0] if diffs else 0.0,
                          "top_diffs": [{"path": k, "v1": v1, "v2": v2} for d, k, v1, v2 in diffs[:8] if d > 0],
                          "new_leaves_in_v2": sorted({k.split(".")[0] + "." + k.split(".")[1] for k in y if k not in x and k.count(".") >= 1})[:20]}
(R / "v1_vs_v2_diff.json").write_text(json.dumps(out, indent=2))
for k, v in out.items():
    print(k, "| shared", v["shared_numeric_leaves"], "| identical", v["identical"], "| max |diff|", f"{v['max_abs_diff']:.3g}")
    for t in v["top_diffs"][:4]:
        print("   ", t["path"], t["v1"], "->", t["v2"])
