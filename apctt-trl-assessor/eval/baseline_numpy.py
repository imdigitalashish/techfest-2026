"""Baseline v0-np: numpy-only text TRL predictors on NASA TechPort (CPU, no sklearn/scipy).

Written because the overloaded overnight machine could not import scipy in time; same frozen
split and same metrics as eval/baseline_tfidf.py.
Features: hashed unigram+bigram counts (crc32, D dims) -> log(1+tf) * idf (train) -> L2 rows.
Models:  majority | ridge (value, rounded) | thr-ridge: 8 ridge fits on 1[y>k] (one solve, 9 RHS)
         -> monotone P(y>k) -> class distribution -> decoded by mode / median / expectation.
Usage: python eval/baseline_numpy.py --label trl_current [--D 4096] [--alpha 1.0]
"""
from __future__ import annotations

import argparse, hashlib, json, re, subprocess, time, zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / ".data" / "techport" / "techport_trl.jsonl"
SEED, K = 20261004, 9
TOK = re.compile(r"[a-z][a-z0-9\-]{1,30}")


def group_key(title: str) -> str:  # identical to baseline_tfidf.py
    t = re.sub(r"(phase\s*(i{1,3}|[123])\b|sbir|sttr|\d{4})", " ", title.lower())
    t = re.sub(r"[^a-z]+", " ", t).strip()
    return t[:60]


def split(rows, label):
    f = HERE / "splits" / f"techport_v0_{label}_test_ids.txt"
    if f.exists():
        test = set(int(x) for x in f.read_text().split())
    else:
        test = {r["id"] for r in rows
                if int(hashlib.sha1(f"{SEED}:{group_key(r['title'])}".encode()).hexdigest(), 16) % 100 < 20}
        f.write_text("\n".join(str(i) for i in sorted(test)) + "\n")
    return [r for r in rows if r["id"] not in test], [r for r in rows if r["id"] in test]


def featurize(texts, D):
    X = np.zeros((len(texts), D), dtype=np.float32)
    for i, t in enumerate(texts):
        w = TOK.findall(t.lower())
        for tok in w + [a + " " + b for a, b in zip(w, w[1:])]:
            X[i, zlib.crc32(tok.encode()) % D] += 1.0
    return np.log1p(X)


def qwk(y, p):
    O = np.zeros((K, K)); 
    for a, b in zip(y, p): O[a - 1, b - 1] += 1
    W = (np.subtract.outer(np.arange(K), np.arange(K)) ** 2) / (K - 1) ** 2
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    return float(1 - (W * O).sum() / (W * E).sum())


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    prec = [np.mean(y[p == c] == c) for c in range(1, K + 1) if np.any(p == c)]
    labels = sorted(set(y.tolist()) | set(p.tolist()))  # sklearn convention; never-predicted classes count as 0
    macro_p = float(np.mean([np.mean(y[p == c] == c) if np.any(p == c) else 0.0 for c in labels]))
    return {"n": int(len(y)), "exact_acc": float(np.mean(y == p)), "within1_acc": float(np.mean(np.abs(y - p) <= 1)),
            "mae": float(np.mean(np.abs(y - p))), "qwk": qwk(y, p), "macro_precision": macro_p,
            "macro_precision_predicted_classes": float(np.mean(prec)) if prec else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", action="append"); ap.add_argument("--D", type=int, default=4096)
    ap.add_argument("--alpha", type=float, default=1.0)
    a = ap.parse_args()
    rows_all = [json.loads(l) for l in DATA.open()]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    for label in a.label or ["trl_current"]:
        rows = [r for r in rows_all if r.get(label)]
        tr, te = split(rows, label)
        ytr = np.array([r[label] for r in tr]); yte = np.array([r[label] for r in te])
        t0 = time.time()
        Xtr = featurize([r["text"] for r in tr], a.D)
        idf = np.log((1 + len(tr)) / (1 + (Xtr > 0).sum(0))) + 1
        Xtr *= idf; Xtr /= np.linalg.norm(Xtr, axis=1, keepdims=True) + 1e-9
        # targets: centred TRL value + 8 threshold indicators
        T = np.column_stack([ytr - ytr.mean()] + [(ytr > k).astype(np.float32) for k in range(1, K)])
        mu = T.mean(0); xm = Xtr.mean(0)
        Xc = Xtr - xm
        Wt = np.linalg.solve(Xc.T @ Xc + a.alpha * np.eye(a.D, dtype=np.float32), Xc.T @ (T - mu))
        t_fit = time.time() - t0
        t1 = time.time()
        Xte = featurize([r["text"] for r in te], a.D) * idf
        Xte /= np.linalg.norm(Xte, axis=1, keepdims=True) + 1e-9
        Z = (Xte - xm) @ Wt + mu
        t_pred = time.time() - t1
        res = {"label": label, "n_train": len(tr), "n_test": len(te), "commit": commit, "seed": SEED, "D": a.D,
               "alpha": a.alpha, "fit_s": t_fit, "predict_ms_per_doc": 1000 * t_pred / len(te), "models": {}}
        res["models"]["majority"] = metrics(yte, np.full_like(yte, np.bincount(ytr).argmax()))
        res["models"]["ridge_round"] = metrics(yte, np.clip(np.rint(Z[:, 0] + ytr.mean()), 1, K).astype(int))
        gt = np.minimum.accumulate(np.clip(Z[:, 1:], 0, 1), axis=1)
        cdf = np.concatenate([np.ones((len(gt), 1)), gt, np.zeros((len(gt), 1))], 1)
        P = np.clip(cdf[:, :-1] - cdf[:, 1:], 0, 1) + 1e-9; P /= P.sum(1, keepdims=True)
        lv = np.arange(1, K + 1)
        res["models"]["thr_ridge_mode"] = metrics(yte, lv[P.argmax(1)])
        res["models"]["thr_ridge_median"] = metrics(yte, lv[(np.cumsum(P, 1) >= 0.5).argmax(1)])
        res["models"]["thr_ridge_expect"] = metrics(yte, np.clip(np.rint(P @ lv), 1, K).astype(int))
        (HERE / "results" / f"baseline_np_v0_{label}.json").write_text(json.dumps(res, indent=1))
        tsv = HERE / "results" / "results_numpy.tsv"
        if not tsv.exists():
            tsv.write_text("timestamp\tcommit\tscript\tlabel\tmodel\tn_test\texact\twithin1\tmae\tqwk\n")
        with tsv.open("a") as f:
            for m, v in res["models"].items():
                f.write(f"{time.strftime('%Y-%m-%dT%H:%M')}\t{commit}\tbaseline_numpy\t{label}\t{m}\t{v['n']}\t"
                        f"{v['exact_acc']:.4f}\t{v['within1_acc']:.4f}\t{v['mae']:.4f}\t{v['qwk']:.4f}\n")
        print(f"== {label}: train {len(tr)} test {len(te)} fit {t_fit:.1f}s predict {res['predict_ms_per_doc']:.2f} ms/doc", flush=True)
        for m, v in res["models"].items():
            print(f"{m:18s} exact {v['exact_acc']:.3f} within1 {v['within1_acc']:.3f} MAE {v['mae']:.3f} QWK {v['qwk']:.3f}", flush=True)


if __name__ == "__main__":
    main()
