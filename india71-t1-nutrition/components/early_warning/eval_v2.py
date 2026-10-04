"""FROZEN evaluator v2 for early_warning: eval_v1's protocol plus the INFANT GATE the proposal promises.

Why v2 (gpt-6-astra demo review, 2026-10-04, item M1): the proposal routes children under 6 months past the
ranking ("SAM, infants under 6 months and danger signs bypass ranking"), but eval_v1 let them compete for the
K slots. v1 stays frozen as history; v2 is the protocol the design actually describes.

Differences from v1 (everything else identical: simulator seeds, features, observed-label training, K,
episode definition, bootstrap):
- Candidate pool: observed-normal children aged >= MIN_AGE_DAYS (183 d) at the measurement (`pool_of`).
  Younger infants go to the infant pathway (protocol/ASHA home visits), not to the K slots.
- Training rows: the same gate (models learn on the population they rank).
- Episodes: v1's incident-episode definition, plus `rankable` = the child was >= 183 d old at the start of the
  1-3 month flag window (onset month o; window starts at o-3). Recall is computed over rankable episodes; the
  share of episodes whose window starts in infancy is reported as `infant_pathway_share`.
Run: .venv/bin/python -m components.early_warning.eval_v2   (writes eval/results/early_warning_v2.json)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from components.cohort_simulator.simulate import SimConfig, simulate
from components.early_warning import eval_v1
from components.early_warning import model as ew
from components.growth_standards import who

K = eval_v1.K
TRAIN_SEEDS, TEST_SEEDS = eval_v1.TRAIN_SEEDS, eval_v1.TEST_SEEDS
N_BOOT = eval_v1.N_BOOT
MIN_AGE_DAYS = 183
OUT = Path(__file__).resolve().parents[2] / "eval" / "results" / "early_warning_v2.json"

observed_labels = eval_v1.observed_labels
flag = eval_v1.flag
evaluate = eval_v1.evaluate


def build(seed: int):
    """eval_v1.build plus age_days in the truth frame (needed for the gate)."""
    sim = simulate(SimConfig(seed=seed))
    truth = sim["truth_monthly"][["child_key", "month_index", "measured_on", "age_days", "true_wlz"]]
    df = ew.features(sim["measurements"], sim["health_events"], truth[["child_key", "measured_on", "month_index"]],
                     unit_cred=False)
    cls = who.classify(df, muac_cm=df.muac_cm, oedema=df.oedema, age_days=df.age_days)
    df["obs_status"] = cls.nutrition_status.to_numpy()
    df = df.merge(truth[["child_key", "month_index", "true_wlz"]], on=["child_key", "month_index"], how="left")
    df["seed"] = seed
    return df, truth


def pool_of(df: pd.DataFrame) -> pd.DataFrame:
    """Rankable candidates: observed normal and at least 6 months old."""
    return df[(df.obs_status == "normal") & (df.age_days >= MIN_AGE_DAYS)]


def episodes(truth: pd.DataFrame) -> pd.DataFrame:
    """v1 incident episodes + age at the start of the flag window + `rankable`."""
    ep = eval_v1.episodes(truth[["child_key", "month_index", "measured_on", "true_wlz"]])
    age = truth.set_index(["child_key", "month_index"]).age_days
    age = age[~age.index.duplicated()]
    at_onset = age.reindex(pd.MultiIndex.from_arrays([ep.child_key, ep.onset])).to_numpy(dtype=float)
    at_start = age.reindex(pd.MultiIndex.from_arrays([ep.child_key, ep.onset - 3])).to_numpy(dtype=float)
    at_start = np.where(np.isnan(at_start), at_onset - 91, at_start)  # child not yet born/registered at o-3
    ep = ep.assign(age_at_window_start_days=at_start, rankable=at_start >= MIN_AGE_DAYS)
    return ep


def main() -> dict:
    train = pd.concat([build(s)[0] for s in TRAIN_SEEDS], ignore_index=True)
    train["label"] = observed_labels(train)
    train = pool_of(train)
    train = train[train.label.notna()]
    tests = [build(s) for s in TEST_SEEDS]
    pool = pd.concat([pool_of(d) for d, _ in tests], ignore_index=True)
    eps_all = pd.concat([episodes(t).assign(seed=s) for (d, t), s in zip(tests, TEST_SEEDS)], ignore_index=True)
    eps = eps_all[eps_all.rankable][["child_key", "onset", "seed"]].reset_index(drop=True)
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
    res = {"metric": f"rankable_episode_recall_at_{K}_per_awc_month", "K": K, "min_age_days": MIN_AGE_DAYS,
           "train_seeds": TRAIN_SEEDS, "test_seeds": TEST_SEEDS, "n_train_rows": int(len(train)),
           "n_pool_rows": int(len(pool)), "n_episodes_all": int(len(eps_all)), "n_episodes_rankable": int(len(eps)),
           "infant_pathway_share": round(float(1 - eps_all.rankable.mean()), 4), "methods": {}}
    per_ep = {}
    for name, sc in scores.items():
        r, e = evaluate(pool, eps, flag(pool, sc), max_month)
        res["methods"][name] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
        per_ep[name] = e
    awc_of = pool.drop_duplicates(["seed", "child_key"]).set_index(["seed", "child_key"]).awc_code
    base = per_ep["lowest_observed_whz"]
    base["awc"] = awc_of.reindex(pd.MultiIndex.from_arrays([base.seed, base.child_key])).to_numpy()
    clusters = base.awc.dropna().unique()
    groups = {c: np.nonzero(base.awc.to_numpy() == c)[0] for c in clusters}
    det = {n: per_ep[n].detected.to_numpy() for n in scores}
    boot = {n: [] for n in ("logistic_anthro", "logistic_anthro_plus_linked_health", "lowest_observed_whz",
                            "rule_no_gain_2m", "diff_lowest_whz_vs_rule", "diff_full_vs_lowest_whz")}
    for _ in range(N_BOOT):
        idx = np.concatenate([groups[c] for c in rng.choice(clusters, len(clusters))])
        for n in ("logistic_anthro", "logistic_anthro_plus_linked_health", "lowest_observed_whz", "rule_no_gain_2m"):
            boot[n].append(det[n][idx].mean())
        boot["diff_lowest_whz_vs_rule"].append(det["lowest_observed_whz"][idx].mean() - det["rule_no_gain_2m"][idx].mean())
        boot["diff_full_vs_lowest_whz"].append(det["logistic_anthro_plus_linked_health"][idx].mean() - det["lowest_observed_whz"][idx].mean())
    res["bootstrap_95ci"] = {n: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
                             for n, v in boot.items()}
    res["value"] = res["methods"]["lowest_observed_whz"]["episode_recall"]
    res["synthetic"] = True
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    main()
