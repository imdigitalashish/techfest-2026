"""FROZEN evaluator v1 for early_warning (spike B). Supersedes eval.py (v0), which is kept for history:
v0 had look-ahead (AWC credibility over full history) and an oracle candidate pool (truth-based exclusion).
Both were flagged by the GPT-6 Sol and GPT-6 Astra reviews (reviews/2026-10-04-*).

Protocol (SYNTHETIC simulator; all numbers are engineering checks, not clinical validation):
- Features: prediction-time only (`features(..., unit_cred=False)`, `ANTHRO_V1`); a test asserts that
  appending future records cannot change earlier features.
- Candidate pool at month t: children with a usable measurement at t whose *observed* status
  (WHZ / MUAC 6-59 m / oedema) is normal. Observed SAM/MAM go to the protocol pathway, not the list.
  Truly-wasted-but-observed-normal children stay in the pool and use capacity.
- Capacity: top-K per AWC per month (K=5, assumption).
- Training labels: OBSERVED wasting (usable WHZ < -2, or observed SAM/MAM) in t+1..t+3 (truth is never
  used for training). Train seeds 21-22.
- Outcome on test seeds 23-24 (truth): unique incident episodes, onset o = true WLZ < -2 at o and
  >= -2 at o-1 and o-2; evaluable if o-3 >= 0. Detected if flagged in any month o-3..o-1
  (i.e. >= ~30 days before onset). Lead = o - first flag month.
- Primary scalar: episode recall@K (pooled over test seeds) with a cluster bootstrap over AWCs.
Run: .venv/bin/python -m components.early_warning.eval_v1   (writes eval/results/early_warning_v1.json)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from components.cohort_simulator.simulate import SimConfig, simulate
from components.early_warning import model as ew
from components.growth_standards import who

K = 5
TRAIN_SEEDS, TEST_SEEDS = (21, 22), (23, 24)
OUT = Path(__file__).resolve().parents[2] / "eval" / "results" / "early_warning_v1.json"
N_BOOT = 400


def build(seed: int):
    sim = simulate(SimConfig(seed=seed))
    truth = sim["truth_monthly"][["child_key", "month_index", "measured_on", "true_wlz"]]
    df = ew.features(sim["measurements"], sim["health_events"], truth[["child_key", "measured_on", "month_index"]],
                     unit_cred=False)
    cls = who.classify(df, muac_cm=df.muac_cm, oedema=df.oedema, age_days=df.age_days)
    df["obs_status"] = cls.nutrition_status.to_numpy()
    df = df.merge(truth[["child_key", "month_index", "true_wlz"]], on=["child_key", "month_index"], how="left")
    df["seed"] = seed
    return df, truth


def observed_labels(df: pd.DataFrame) -> pd.Series:
    """Observed wasting in t+1..t+3 for each row (NaN if no usable observation in the window)."""
    obs = df[["child_key", "month_index"]].copy()
    obs["wasted_obs"] = df.obs_status.isin(["sam", "mam"]).astype(float)
    lab = pd.Series(np.nan, index=df.index)
    key = obs.set_index(["child_key", "month_index"]).wasted_obs
    key = key[~key.index.duplicated()]
    hits = np.full(len(df), np.nan)
    for h in (1, 2, 3):
        idx = pd.MultiIndex.from_arrays([df.child_key, df.month_index + h])
        v = key.reindex(idx).to_numpy()
        hits = np.where(np.isnan(hits), v, np.where(np.isnan(v), hits, np.maximum(hits, v)))
    lab[:] = hits
    return lab


def episodes(truth: pd.DataFrame) -> pd.DataFrame:
    t = truth.sort_values(["child_key", "month_index"])
    g = t.groupby("child_key")
    prev1, prev2 = g.true_wlz.shift(1), g.true_wlz.shift(2)
    m1, m2 = g.month_index.shift(1), g.month_index.shift(2)
    onset = (t.true_wlz < -2) & (prev1 >= -2) & (prev2 >= -2) & (m1 == t.month_index - 1) & (m2 == t.month_index - 2)
    ep = t[onset & (t.month_index >= 3)][["child_key", "month_index"]].rename(columns={"month_index": "onset"})
    return ep.reset_index(drop=True)


def flag(pool: pd.DataFrame, score: np.ndarray, k: int = K) -> pd.DataFrame:
    d = pool.assign(score=score)
    d["rank"] = d.groupby(["seed", "awc_code", "month_index"]).score.rank(ascending=False, method="first")
    return d[d["rank"] <= k]


def evaluate(pool: pd.DataFrame, eps: pd.DataFrame, flagged: pd.DataFrame, max_month: dict) -> dict:
    f = flagged[["seed", "child_key", "month_index", "awc_code", "true_wlz"]]
    m = eps.merge(f, on=["seed", "child_key"], how="left")
    m = m[(m.month_index >= m.onset - 3) & (m.month_index <= m.onset - 1)]
    first = m.groupby(["seed", "child_key", "onset"]).month_index.min()
    e = eps.set_index(["seed", "child_key", "onset"])
    e["detected"] = first.reindex(e.index).notna()
    e["lead"] = (e.index.get_level_values("onset") - first.reindex(e.index)).to_numpy()
    # slot-level: flagged child-months with a complete 3-month future
    fs = f[f.month_index <= f.seed.map(max_month) - 3]
    onset_set = set(zip(eps.seed, eps.child_key, eps.onset))
    nxt = [any((s, c, t + h) in onset_set for h in (1, 2, 3)) for s, c, t in zip(fs.seed, fs.child_key, fs.month_index)]
    return {
        "episode_recall": float(e.detected.mean()),
        "median_lead_months": float(np.nanmedian(e.lead)) if e.detected.any() else None,
        "slot_precision_incident_next_3m": float(np.mean(nxt)) if len(fs) else None,
        "slot_share_truly_wasted_now_missed_by_measurement": float((fs.true_wlz < -2).mean()) if len(fs) else None,
        "n_episodes": int(len(e)),
    }, e.reset_index()


def main() -> dict:
    train = pd.concat([build(s)[0] for s in TRAIN_SEEDS], ignore_index=True)
    train["label"] = observed_labels(train)
    train = train[(train.obs_status == "normal") & train.label.notna()]
    tests = [build(s) for s in TEST_SEEDS]
    pool = pd.concat([d[d.obs_status == "normal"] for d, _ in tests], ignore_index=True)
    eps = pd.concat([episodes(t).assign(seed=s) for (d, t), s in zip(tests, TEST_SEEDS)], ignore_index=True)
    max_month = {s: int(t.month_index.max()) for (d, t), s in zip(tests, TEST_SEEDS)}

    m_anthro = ew.fit_logistic(train, ew.ANTHRO_V1)
    m_full = ew.fit_logistic(train, ew.ANTHRO_V1 + ew.HEALTH)
    rng = np.random.default_rng(0)
    scores = {
        "random_within_awc": rng.random(len(pool)),
        "rule_no_gain_2m": ew.score_rule_no_gain(pool),
        "lowest_observed_whz": ew.score_lowest_whz(pool),
        "logistic_anthro": m_anthro.predict_proba(ew.fill(pool[ew.ANTHRO_V1]))[:, 1],
        "logistic_anthro_plus_linked_health": m_full.predict_proba(ew.fill(pool[ew.ANTHRO_V1 + ew.HEALTH]))[:, 1],
    }
    res = {"metric": f"episode_recall_at_{K}_per_awc_month", "K": K, "train_seeds": TRAIN_SEEDS,
           "test_seeds": TEST_SEEDS, "n_train_rows": int(len(train)), "n_pool_rows": int(len(pool)), "methods": {}}
    per_ep = {}
    for name, sc in scores.items():
        r, e = evaluate(pool, eps, flag(pool, sc), max_month)
        res["methods"][name] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
        per_ep[name] = e
    # cluster bootstrap over AWCs (episodes clustered by the child's AWC)
    awc_of = pool.drop_duplicates(["seed", "child_key"]).set_index(["seed", "child_key"]).awc_code
    base = per_ep["lowest_observed_whz"]
    base["awc"] = awc_of.reindex(pd.MultiIndex.from_arrays([base.seed, base.child_key])).to_numpy()
    clusters = base.awc.dropna().unique()
    boot = {n: [] for n in ("logistic_anthro", "logistic_anthro_plus_linked_health", "lowest_observed_whz", "diff_full_vs_lowest_whz")}
    det = {n: per_ep[n].detected.to_numpy() for n in scores}
    groups = {c: np.nonzero(base.awc.to_numpy() == c)[0] for c in clusters}
    for _ in range(N_BOOT):
        idx = np.concatenate([groups[c] for c in rng.choice(clusters, len(clusters))])
        for n in ("logistic_anthro", "logistic_anthro_plus_linked_health", "lowest_observed_whz"):
            boot[n].append(det[n][idx].mean())
        boot["diff_full_vs_lowest_whz"].append(det["logistic_anthro_plus_linked_health"][idx].mean() - det["lowest_observed_whz"][idx].mean())
    res["bootstrap_95ci"] = {n: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)] for n, v in boot.items()}
    res["value"] = res["methods"]["logistic_anthro_plus_linked_health"]["episode_recall"]
    res["synthetic"] = True
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    main()
