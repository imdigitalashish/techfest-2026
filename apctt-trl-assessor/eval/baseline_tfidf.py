"""Baseline v0: text-only TRL predictors on NASA TechPort (CPU, scikit-learn).

Models (all on TF-IDF of title+description+benefits; no metadata):
  majority      - predicts the training mode (floor)
  logreg        - multinomial logistic regression, argmax (nominal)
  ridge         - ridge regression on the TRL value, rounded+clipped (ordinal-aware)
  cumlogit      - Frank & Hall (2001) cumulative decomposition: 8 binary P(y>k) logistic models
                  -> class distribution; decoded by mode / median / rounded expectation
Split: grouped 80/20 on a normalised-title key (seed 20261004), frozen to eval/splits/.
Metrics: exact acc, within-1 acc, MAE, quadratic weighted kappa (QWK), macro precision/F1, latency.

Usage: python eval/baseline_tfidf.py --label trl_current [--label trl_begin ...]
Writes eval/results/baseline_v0_<label>.json and appends to eval/results/results.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import cohen_kappa_score, f1_score, precision_score

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / ".data" / "techport" / "techport_trl.jsonl"
SEED = 20261004
K = 9


def group_key(title: str) -> str:
    t = re.sub(r"(phase\s*(i{1,3}|[123])\b|sbir|sttr|\d{4})", " ", title.lower())
    t = re.sub(r"[^a-z]+", " ", t).strip()
    return t[:60]


def split(rows, label):
    ids_file = HERE / "splits" / f"techport_v0_{label}_test_ids.txt"
    if ids_file.exists():
        test_ids = set(int(x) for x in ids_file.read_text().split())
    else:
        test_ids = set()
        for r in rows:
            h = int(hashlib.sha1(f"{SEED}:{group_key(r['title'])}".encode()).hexdigest(), 16) % 100
            if h < 20:
                test_ids.add(r["id"])
        ids_file.write_text("\n".join(str(i) for i in sorted(test_ids)) + "\n")
    tr = [r for r in rows if r["id"] not in test_ids]
    te = [r for r in rows if r["id"] in test_ids]
    return tr, te


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return {
        "n": int(len(y)),
        "exact_acc": float(np.mean(y == p)),
        "within1_acc": float(np.mean(np.abs(y - p) <= 1)),
        "mae": float(np.mean(np.abs(y - p))),
        "qwk": float(cohen_kappa_score(y, p, weights="quadratic", labels=list(range(1, K + 1)))),
        "macro_precision": float(precision_score(y, p, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y, p, average="macro", zero_division=0)),
    }


def decode(P):
    """P: (n, 9) class distribution over TRL 1..9."""
    levels = np.arange(1, K + 1)
    mode = levels[P.argmax(1)]
    median = levels[(np.cumsum(P, 1) >= 0.5).argmax(1)]
    expect = np.clip(np.rint(P @ levels), 1, K).astype(int)
    return {"mode": mode, "median": median, "expect": expect}


def cumlogit_fit_predict(Xtr, ytr, Xte, C):
    # P(y > k) for k = 1..8, then differences -> class probs (monotone-fixed).
    gt = np.zeros((Xte.shape[0], K - 1))
    for k in range(1, K):
        yb = (ytr > k).astype(int)
        if yb.min() == yb.max():
            gt[:, k - 1] = yb[0]
            continue
        m = LogisticRegression(C=C, max_iter=2000)
        m.fit(Xtr, yb)
        gt[:, k - 1] = m.predict_proba(Xte)[:, 1]
    gt = np.minimum.accumulate(gt, axis=1)  # enforce P(y>k) non-increasing in k
    cdf_gt = np.concatenate([np.ones((len(gt), 1)), gt, np.zeros((len(gt), 1))], 1)
    P = np.clip(cdf_gt[:, :-1] - cdf_gt[:, 1:], 0, 1)
    return P / P.sum(1, keepdims=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", action="append", default=None)
    ap.add_argument("--C", type=float, default=4.0)
    args = ap.parse_args()
    labels = args.label or ["trl_current"]
    rows_all = [json.loads(l) for l in DATA.open()]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    for label in labels:
        rows = [r for r in rows_all if r.get(label)]
        tr, te = split(rows, label)
        ytr = np.array([r[label] for r in tr]); yte = np.array([r[label] for r in te])
        t0 = time.time()
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True, max_features=200000)
        Xtr = vec.fit_transform([r["text"] for r in tr])
        t_vec = time.time() - t0
        t1 = time.time(); Xte = vec.transform([r["text"] for r in te]); t_vec_te = time.time() - t1
        res = {"label": label, "n_train": len(tr), "n_test": len(te), "commit": commit, "seed": SEED,
               "train_label_dist": {int(k): int(v) for k, v in zip(*np.unique(ytr, return_counts=True))},
               "test_label_dist": {int(k): int(v) for k, v in zip(*np.unique(yte, return_counts=True))},
               "models": {}}
        maj = int(np.bincount(ytr).argmax())
        res["models"]["majority"] = metrics(yte, np.full_like(yte, maj))
        t0 = time.time()
        lr = LogisticRegression(C=args.C, max_iter=3000); lr.fit(Xtr, ytr)
        t_fit = time.time() - t0
        t0 = time.time(); Plr = np.zeros((len(te), K)); Plr[:, lr.classes_ - 1] = lr.predict_proba(Xte); t_pred = time.time() - t0
        for name, p in decode(Plr).items():
            res["models"][f"logreg_{name}"] = metrics(yte, p)
        res["models"]["logreg_mode"]["fit_s"] = t_fit
        res["models"]["logreg_mode"]["predict_ms_per_doc"] = 1000 * (t_pred + t_vec_te) / len(te)
        rg = Ridge(alpha=1.0); rg.fit(Xtr, ytr)
        res["models"]["ridge_round"] = metrics(yte, np.clip(np.rint(rg.predict(Xte)), 1, K).astype(int))
        t0 = time.time(); Pcl = cumlogit_fit_predict(Xtr, ytr, Xte, args.C); t_cl = time.time() - t0
        for name, p in decode(Pcl).items():
            res["models"][f"cumlogit_{name}"] = metrics(yte, p)
        res["models"]["cumlogit_median"]["fit_plus_predict_s"] = t_cl
        res["vectorize_train_s"] = t_vec
        out = HERE / "results" / f"baseline_v0_{label}.json"
        out.write_text(json.dumps(res, indent=1))
        tsv = HERE / "results" / "results.tsv"
        if not tsv.exists():
            tsv.write_text("timestamp\tcommit\tlabel\tmodel\tn_test\texact\twithin1\tmae\tqwk\tmacro_prec\n")
        with tsv.open("a") as f:
            for m, v in res["models"].items():
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M')}\t{commit}\t{label}\t{m}\t{v['n']}\t{v['exact_acc']:.4f}\t"
                        f"{v['within1_acc']:.4f}\t{v['mae']:.4f}\t{v['qwk']:.4f}\t{v['macro_precision']:.4f}\n")
        print(f"\n== {label}: train {len(tr)} / test {len(te)}")
        print(f"{'model':20s} exact  within1  MAE    QWK    macroP")
        for m, v in res["models"].items():
            print(f"{m:20s} {v['exact_acc']:.3f}  {v['within1_acc']:.3f}    {v['mae']:.3f}  {v['qwk']:.3f}  {v['macro_precision']:.3f}")


if __name__ == "__main__":
    main()
