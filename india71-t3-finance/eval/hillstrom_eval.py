"""Public-data check for the C6 learner on a REAL randomised experiment (Hillstrom / MineThatData 2008).

64,000 customers randomised (≈1/3 each) to: no e-mail, men's-merchandise e-mail, women's-merchandise e-mail.
Outcome: website visit within two weeks. This is retail e-mail, NOT banking — it tests whether our learner
(T-learner with HistGradientBoosting + shrinkage toward arm averages, the C6 v0.1 recipe) finds real
heterogeneity well enough to beat "best arm to a random subset" at a partial budget.

Policy value on the held-out half is estimated without bias by inverse-probability weighting (IPW), which is
valid because arms were randomised: V(pi) = mean( y * 1[a == pi(x)] / p(a) ).
Usage (from india71-t3-finance/): python eval/hillstrom_eval.py --seeds 0 1 2
Data: .data/hillstrom/hillstrom.csv from
http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / ".data" / "hillstrom" / "hillstrom.csv"
ARM_MAP = {"No E-Mail": "none", "Mens E-Mail": "mens", "Womens E-Mail": "womens"}
TREAT = ["mens", "womens"]
CFG = {"max_iter": 200, "learning_rate": 0.05, "max_leaf_nodes": 15, "min_samples_leaf": 40, "l2": 1.0, "shrink": 0.5}


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    df["arm"] = df["segment"].map(ARM_MAP)
    df["hist_seg"] = df["history_segment"].str[0].astype(int)
    for c, levels in {"zip_code": ["Urban", "Surburban", "Rural"], "channel": ["Phone", "Web", "Multichannel"]}.items():
        for v in levels:
            df[f"{c}_{v}"] = (df[c] == v).astype(int)
    return df


FEATS = ["recency", "history", "mens", "womens", "newbie", "hist_seg", "zip_code_Urban", "zip_code_Surburban",
         "zip_code_Rural", "channel_Phone", "channel_Web", "channel_Multichannel"]


def fit_predict(tr: pd.DataFrame, te: pd.DataFrame, seed: int, shrink: float) -> pd.DataFrame:
    p = {}
    for a in ["none"] + TREAT:
        m = tr["arm"] == a
        clf = HistGradientBoostingClassifier(max_iter=CFG["max_iter"], learning_rate=CFG["learning_rate"],
                                             max_leaf_nodes=CFG["max_leaf_nodes"], min_samples_leaf=CFG["min_samples_leaf"],
                                             l2_regularization=CFG["l2"], random_state=seed)
        clf.fit(tr.loc[m, FEATS], tr.loc[m, "visit"])
        p[a] = clf.predict_proba(te[FEATS])[:, 1]
    base = tr.loc[tr["arm"] == "none", "visit"].mean()
    ate = {a: tr.loc[tr["arm"] == a, "visit"].mean() - base for a in TREAT}
    return pd.DataFrame({a: ate[a] + shrink * ((p[a] - p["none"]) - ate[a]) for a in TREAT}, index=te.index)


def ipw_value(te: pd.DataFrame, pi: np.ndarray, prop: dict) -> np.ndarray:
    """Per-row IPW contributions; mean = estimated visit rate under policy pi."""
    match = (te["arm"].to_numpy() == pi)
    w = np.array([1.0 / prop[a] for a in te["arm"]])
    return te["visit"].to_numpy() * match * w


def run(seed: int, budgets=(0.1, 0.2, 0.3, 0.5, 1.0), boot: int = 200) -> dict:
    df = load()
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(df))
    tr, te = df.iloc[idx[: len(df) // 2]], df.iloc[idx[len(df) // 2:]]
    prop = te["arm"].value_counts(normalize=True).to_dict()
    U = fit_predict(tr, te, seed, CFG["shrink"])
    U0 = fit_predict(tr, te, seed, 1.0)
    ate_tr = {a: tr.loc[tr["arm"] == a, "visit"].mean() - tr.loc[tr["arm"] == "none", "visit"].mean() for a in TREAT}
    best = max(ate_tr, key=ate_tr.get)
    none = ipw_value(te, np.array(["none"] * len(te), dtype=object), prop)
    out = {"seed": seed, "n_test": int(len(te)), "train_ate": {k: round(v, 4) for k, v in ate_tr.items()}, "budgets": {}}
    for b in budgets:
        k = int(round(b * len(te)))
        pols = {}
        r = np.full(len(te), "none", dtype=object)
        r[rng.permutation(len(te))[:k]] = rng.choice(TREAT, size=k)
        pols["random"] = r
        r = np.full(len(te), "none", dtype=object)
        r[rng.permutation(len(te))[:k]] = best
        pols["best_arm"] = r
        for name, M in (("uplift_t", U0), ("uplift_shrunk", U)):
            score = M.max(axis=1).to_numpy()
            arm = M.idxmax(axis=1).to_numpy()
            r = np.full(len(te), "none", dtype=object)
            top = np.argsort(-score)[:k]
            r[top] = arm[top]
            pols[name] = r
        res = {}
        for name, pi in pols.items():
            contrib = ipw_value(te, pi, prop) - none
            est = contrib.mean()
            bs = [contrib[rng.integers(0, len(contrib), len(contrib))].mean() for _ in range(boot)]
            res[name] = {"incr_visits_per_1000": round(1000 * est, 2), "ci95": [round(1000 * np.percentile(bs, 2.5), 2), round(1000 * np.percentile(bs, 97.5), 2)]}
        # paired difference uplift_shrunk - best_arm
        d = (ipw_value(te, pols["uplift_shrunk"], prop) - ipw_value(te, pols["best_arm"], prop))
        bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(boot)]
        res["diff_shrunk_vs_best_arm"] = {"per_1000": round(1000 * d.mean(), 2), "ci95": [round(1000 * np.percentile(bs, 2.5), 2), round(1000 * np.percentile(bs, 97.5), 2)]}
        out["budgets"][str(b)] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    a = ap.parse_args()
    runs = [run(s) for s in a.seeds]
    pols = ["random", "best_arm", "uplift_t", "uplift_shrunk"]
    print("REAL RCT (Hillstrom e-mail): incremental visits per 1,000 customers vs no e-mail (IPW, held-out half; mean over seeds)")
    for b in runs[0]["budgets"]:
        row = {p: np.mean([r["budgets"][b][p]["incr_visits_per_1000"] for r in runs]) for p in pols}
        d = np.mean([r["budgets"][b]["diff_shrunk_vs_best_arm"]["per_1000"] for r in runs])
        cis = [r["budgets"][b]["diff_shrunk_vs_best_arm"]["ci95"] for r in runs]
        print(f"  budget {float(b):>4.0%}: " + "  ".join(f"{p} {v:6.1f}" for p, v in row.items()) + f"  | shrunk - best_arm {d:+.1f} (per-seed 95% CIs {cis})")
    out = ROOT / "eval" / "results" / "hillstrom_uplift.json"
    out.write_text(json.dumps({"seeds": a.seeds, "config": CFG, "runs": runs}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
