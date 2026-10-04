"""Genre/source-shift robustness study v0 (numpy threshold-ridge, same features as the skeleton model).

A. Cross-source shift inside TechPort: train on SBIR/STTR vs NASA-internal programs, test on each (frozen split).
B. Input-truncation stress tests on the frozen test split (title only, first 60 words, description only, ...).
C. Paired genre test: for projects with DOI-linked papers (OpenAlex abstracts), predict TRL from the project
   description and from the paper (title + abstract); label = the project's trl_current for both (a noisy proxy
   for the paper). The model is trained on TechPort rows excluding those projects and their title groups.
Usage: python eval/genre_shift.py   -> eval/results/genre_shift_v0.json + markdown on stdout
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from components.skeleton.ordinal import featurize  # noqa: E402

spec = importlib.util.spec_from_file_location("bn", HERE / "baseline_numpy.py")
bn = importlib.util.module_from_spec(spec); spec.loader.exec_module(bn)
K, D, ALPHA, LABEL = 9, 4096, 1.0, "trl_current"
LV = np.arange(1, K + 1)


def fit(texts, y):
    X = featurize(texts, D)
    idf = np.log((1 + len(texts)) / (1 + (X > 0).sum(0))) + 1
    X *= idf; X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    T = np.column_stack([y - y.mean()] + [(y > k).astype(np.float32) for k in range(1, K)])
    mu, xm = T.mean(0), X.mean(0)
    Xc = X - xm
    W = np.linalg.solve(Xc.T @ Xc + ALPHA * np.eye(D, dtype=np.float32), Xc.T @ (T - mu))
    return {"W": W, "mu": mu, "xm": xm, "idf": idf, "ym": float(y.mean())}


def predict(m, texts):
    X = featurize(texts, D) * m["idf"]; X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    Z = (X - m["xm"]) @ m["W"] + m["mu"]
    ridge = np.clip(np.rint(Z[:, 0] + m["ym"]), 1, K).astype(int)
    gt = np.minimum.accumulate(np.clip(Z[:, 1:], 0, 1), axis=1)
    cdf = np.concatenate([np.ones((len(gt), 1)), gt, np.zeros((len(gt), 1))], 1)
    P = np.clip(cdf[:, :-1] - cdf[:, 1:], 0, 1) + 1e-9; P /= P.sum(1, keepdims=True)
    med = LV[(np.cumsum(P, 1) >= 0.5).argmax(1)]
    return ridge, med, P @ LV


def m(y, p):
    r = bn.metrics(y, p)
    return {k: round(v, 3) if isinstance(v, float) else v for k, v in r.items() if k != "macro_precision_predicted_classes"}


def text(r):
    return r["text"]


def main():
    rows = [r for r in map(json.loads, (HERE.parent / ".data/techport/techport_trl.jsonl").open()) if r.get(LABEL)]
    test_ids = set(int(x) for x in (HERE / "splits" / f"techport_v0_{LABEL}_test_ids.txt").read_text().split())
    tr = [r for r in rows if r["id"] not in test_ids]; te = [r for r in rows if r["id"] in test_ids]
    sb = lambda r: r["program"] == "SBIR/STTR"
    out = {"label": LABEL, "D": D, "alpha": ALPHA}

    # A. cross-source shift
    A = {}
    groups = {"all": lambda r: True, "sbir_sttr": sb, "nasa_internal": lambda r: not sb(r)}
    models = {g: fit([text(r) for r in tr if f(r)], np.array([r[LABEL] for r in tr if f(r)], dtype=np.float32)) for g, f in groups.items()}
    for g_tr, mdl in models.items():
        for g_te in ("sbir_sttr", "nasa_internal"):
            sub = [r for r in te if groups[g_te](r)]
            y = np.array([r[LABEL] for r in sub]); ridge, med, _ = predict(mdl, [text(r) for r in sub])
            A[f"train={g_tr}|test={g_te}"] = {"n_train": sum(map(groups[g_tr], tr)), "ridge_round": m(y, ridge), "thr_median": m(y, med)}
    out["A_cross_source"] = A

    # B. truncation stress tests (model trained on all train rows)
    B = {}; y = np.array([r[LABEL] for r in te]); mdl = models["all"]
    variants = {"full (title+description+benefits)": text, "title only": lambda r: r["title"],
                "description only": lambda r: r["description"], "benefits only": lambda r: r["benefits"] or r["title"],
                "first 60 words of description": lambda r: " ".join(r["description"].split()[:60])}
    for name, f in variants.items():
        ridge, med, _ = predict(mdl, [f(r) for r in te])
        B[name] = {"ridge_round": m(y, ridge), "thr_median": m(y, med)}
    out["B_truncation"] = B

    # C. paired genre test on DOI-linked papers
    papers = [p for p in map(json.loads, (HERE.parent / ".data/openalex/linked_papers.jsonl").open())
              if len((p.get("abstract") or "").split()) >= 30]
    byid = {r["id"]: r for r in rows}
    papers = [p for p in papers if p["project_id"] in byid]
    pids = {p["project_id"] for p in papers}
    keys = {bn.group_key(byid[i]["title"]) for i in pids}
    trC = [r for r in rows if r["id"] not in pids and bn.group_key(r["title"]) not in keys]
    mC = fit([text(r) for r in trC], np.array([r[LABEL] for r in trC], dtype=np.float32))
    y = np.array([byid[p["project_id"]][LABEL] for p in papers])
    rd, md, ed = predict(mC, [text(byid[p["project_id"]]) for p in papers])
    rp, mp, ep = predict(mC, [p["title"] + " \n" + p["abstract"] for p in papers])
    rng = np.random.default_rng(20261004); diffs = []
    for _ in range(2000):
        i = rng.integers(0, len(y), len(y)); diffs.append(np.mean(abs(y[i] - rp[i])) - np.mean(abs(y[i] - rd[i])))
    out["C_paired_papers"] = {
        "n_papers": len(papers), "n_projects": len(pids), "n_train": len(trC),
        "label_dist": {int(k): int(v) for k, v in zip(*np.unique(y, return_counts=True))},
        "description": {"ridge_round": m(y, rd), "thr_median": m(y, md), "mean_expected_trl": round(float(ed.mean()), 3)},
        "paper_abstract": {"ridge_round": m(y, rp), "thr_median": m(y, mp), "mean_expected_trl": round(float(ep.mean()), 3)},
        "mae_paper_minus_description_ridge": round(float(np.mean(abs(y - rp)) - np.mean(abs(y - rd))), 3),
        "bootstrap95_ci": [round(float(np.percentile(diffs, 2.5)), 3), round(float(np.percentile(diffs, 97.5)), 3)],
        "corr_expected_trl_desc_vs_paper": round(float(np.corrcoef(ed, ep)[0, 1]), 3)}
    (HERE / "results" / "genre_shift_v0.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
