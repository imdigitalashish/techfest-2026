"""FROZEN evaluator for the C4 ordinal-model tournament (ADR 002). The loop edits ../model.py only.

Entrant API (../model.py):  fit(texts: list[str], y: np.ndarray[int]) -> state ;  predict(state, texts) -> np.ndarray[int] in 1..9
Conditions on eval suite v1 (build: python eval/build_suite_v1.py; label trl_current, redacted, content-dedup split):
  in_dist           fit(all train)       -> test (all)
  sbir_to_internal  fit(train SBIR)      -> test internal
  internal_to_sbir  fit(train internal)  -> test SBIR
  crop60            fit(all train)       -> test, first 60 words only (abstract-length)
  papers            fit(all train)       -> 204 DOI-linked paper abstracts (project label as proxy)
PRIMARY scalar = shifted_mean_qwk = mean QWK over the 4 shifted conditions. Keep rule: paired bootstrap (1,000 resamples
per condition, shared indices) of delta vs the current best; keep iff mean delta >= +0.005 and P(delta > 0) >= 0.90
and in_dist QWK drops by < 0.02. First run (no best) is the baseline.
Usage (from apctt-trl-assessor/): python components/ordinal/autoresearch/eval.py --hypothesis "text"
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
K = 9
SHIFTED = ["sbir_to_internal", "internal_to_sbir", "crop60", "papers"]
PRED_DIR = ROOT / ".data" / "autoresearch"


def qwk(y, p):
    O = np.zeros((K, K))
    np.add.at(O, (y - 1, p - 1), 1)
    W = (np.subtract.outer(np.arange(K), np.arange(K)) ** 2) / (K - 1) ** 2
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    d = (W * E).sum()
    return float(1 - (W * O).sum() / d) if d > 0 else 0.0


def load(name):
    return [json.loads(l) for l in (ROOT / ".data" / "suite_v1" / name).open()]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hypothesis", required=True); a = ap.parse_args()
    meta = json.loads((ROOT / "eval/splits/suite_v1_meta.json").read_text())
    tr, te, pa = load("train.jsonl"), load("test.jsonl"), load("papers.jsonl")
    model = importlib.import_module("components.ordinal.model")
    t0 = time.time()
    fits = {}
    for name, rows in (("all", tr), ("sbir", [r for r in tr if r["source"] == "sbir"]),
                       ("internal", [r for r in tr if r["source"] == "internal"])):
        fits[name] = model.fit([r["text"] for r in rows], np.array([r["label"] for r in rows]))
    t_fit = time.time() - t0
    te_int = [r for r in te if r["source"] == "internal"]; te_sb = [r for r in te if r["source"] == "sbir"]
    conds = {"in_dist": ("all", te, lambda r: r["text"]),
             "sbir_to_internal": ("sbir", te_int, lambda r: r["text"]),
             "internal_to_sbir": ("internal", te_sb, lambda r: r["text"]),
             "crop60": ("all", te, lambda r: " ".join(r["text"].split()[:60])),
             "papers": ("all", pa, lambda r: r["text"])}
    preds, gold, res = {}, {}, {}
    t1 = time.time(); n_pred = 0
    for c, (m, rows, f) in conds.items():
        p = np.clip(np.asarray(model.predict(fits[m], [f(r) for r in rows])).astype(int), 1, K)
        y = np.array([r["label"] for r in rows])
        preds[c], gold[c] = p, y; n_pred += len(rows)
        res[c] = {"n": len(y), "qwk": round(qwk(y, p), 4), "mae": round(float(np.mean(abs(y - p))), 4),
                  "exact": round(float(np.mean(y == p)), 4), "within1": round(float(np.mean(abs(y - p) <= 1)), 4)}
    ms_doc = 1000 * (time.time() - t1) / n_pred
    primary = float(np.mean([res[c]["qwk"] for c in SHIFTED]))
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "components/ordinal/model.py"], capture_output=True, text=True, cwd=ROOT).stdout.strip())
    run_id = time.strftime("%Y%m%dT%H%M%S")
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(PRED_DIR / f"preds_{run_id}.npz", **{f"p_{c}": preds[c] for c in conds}, **{f"y_{c}": gold[c] for c in conds})
    best_f = HERE / "best.json"
    verdict, delta, p_pos = "baseline", 0.0, 1.0
    if best_f.exists():
        best = json.loads(best_f.read_text())
        bp = np.load(PRED_DIR / f"preds_{best['run_id']}.npz")
        rng = np.random.default_rng(20261004); ds = np.zeros(1000)
        for c in SHIFTED:
            y, p_new, p_old = gold[c], preds[c], bp[f"p_{c}"]
            for b in range(1000):
                i = rng.integers(0, len(y), len(y))
                ds[b] += (qwk(y[i], p_new[i]) - qwk(y[i], p_old[i])) / len(SHIFTED)
        delta, p_pos = float(ds.mean()), float(np.mean(ds > 0))
        keep = delta >= 0.005 and p_pos >= 0.90 and res["in_dist"]["qwk"] > best["in_dist_qwk"] - 0.02
        verdict = "KEEP" if keep else "discard"
    if verdict in ("baseline", "KEEP"):
        best_f.write_text(json.dumps({"run_id": run_id, "commit": commit, "shifted_mean_qwk": round(primary, 4),
                                      "in_dist_qwk": res["in_dist"]["qwk"], "hypothesis": a.hypothesis}, indent=1))
    out = {"run_id": run_id, "commit": commit, "model_py_dirty": dirty, "suite": meta["snapshot_sha256"][:12],
           "shifted_mean_qwk": round(primary, 4), "delta_vs_best": round(delta, 4), "p_delta_pos": round(p_pos, 3),
           "verdict": verdict, "fit_s_3models": round(t_fit, 1), "predict_ms_per_doc": round(ms_doc, 2), "conditions": res}
    (PRED_DIR / f"result_{run_id}.json").write_text(json.dumps(out, indent=1))
    tsv = HERE / "results.tsv"
    if not tsv.exists():
        tsv.write_text("run_id\tcommit\tdirty\thypothesis\tshifted_mean_qwk\tdelta\tp_pos\tverdict\tin_dist_qwk\tin_dist_mae\t"
                       "s2i_qwk\ti2s_qwk\tcrop60_qwk\tpapers_qwk\tpapers_mae\tfit_s\tms_doc\n")
    with tsv.open("a") as f:
        f.write(f"{run_id}\t{commit}\t{dirty}\t{a.hypothesis}\t{primary:.4f}\t{delta:+.4f}\t{p_pos:.3f}\t{verdict}\t"
                f"{res['in_dist']['qwk']:.4f}\t{res['in_dist']['mae']:.4f}\t{res['sbir_to_internal']['qwk']:.4f}\t"
                f"{res['internal_to_sbir']['qwk']:.4f}\t{res['crop60']['qwk']:.4f}\t{res['papers']['qwk']:.4f}\t"
                f"{res['papers']['mae']:.4f}\t{t_fit:.1f}\t{ms_doc:.2f}\n")
    print(f"shifted_mean_qwk {primary:.4f}  delta {delta:+.4f} (P>0 {p_pos:.2f})  {verdict}")
    print("  " + "  ".join(f"{c}:{res[c]['qwk']:.3f}/{res[c]['mae']:.3f}" for c in conds) + f"  fit {t_fit:.0f}s  {ms_doc:.1f}ms/doc")


if __name__ == "__main__":
    main()
