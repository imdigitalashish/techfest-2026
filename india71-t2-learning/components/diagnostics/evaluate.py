from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from sklearn.metrics import accuracy_score, brier_score_loss

from eval.sim.world import make_world
from eval.sim.calibration import ASER2024_GOVT_STD3
from components.diagnostics.cutpoints import load as load_cutpoints
from components.diagnostics.engine import adaptive_test, aser_rule, bayes_irt

SEEDS = [101, 102, 103, 104, 105]
SUBJECTS = [
    ("language", "true_read_level", "read_goal", "read_thresholds"),
    ("numeracy", "true_math_level", "math_goal", "math_thresholds"),
]
WORLD_CFG = {**ASER2024_GOVT_STD3, "n_schools": 40, "n_clusters": 8}
SAMPLE_N = 300
SECONDS_PER_ORAL_ITEM = 20


def _tarl_assign(levels: list[int], schools: list[str]) -> list[int]:
    out = [0] * len(levels)
    by_school: dict[str, list[int]] = defaultdict(list)
    for i, school in enumerate(schools):
        by_school[school].append(i)
    for idxs in by_school.values():
        buckets: dict[int, list[int]] = defaultdict(list)
        for i in idxs:
            buckets[int(levels[i])].append(i)
        for lvl in list(sorted(buckets)):
            if 0 < len(buckets[lvl]) < 3 and len(buckets) > 1:
                target = lvl - 1 if lvl > 0 else 1
                buckets[target].extend(buckets.pop(lvl))
        for lvl, members in buckets.items():
            for i in members:
                out[i] = lvl
    return out


def _empty_metrics() -> dict[str, list[float]]:
    return {"level_acc": [], "adjacent_acc": [], "goal_acc": [], "brier": [], "tarl_acc": [], "mean_items": [], "p90_items": [], "minutes": []}


def evaluate_seed(seed: int) -> dict[str, dict[str, float]]:
    w = make_world(seed, WORLD_CFG)
    rows = w.children.sample(n=min(SAMPLE_N, len(w.children)), random_state=seed)
    per_method = {m: _empty_metrics() for m in ["aser_rule_full", "bayes_irt_full", "adaptive_cat_8"]}
    for subject, true_col, goal_col, thr_key in SUBJECTS:
        true_levels = [int(v) for v in rows[true_col]]
        true_goal = [int(v) for v in rows[goal_col]]
        schools = [str(v) for v in rows.udise_code]
        true_tarl = _tarl_assign(true_levels, schools)
        method_data = {m: {"pred": [], "goal_prob": [], "items": []} for m in per_method}
        for _, ch in rows.iterrows():
            d_rule = aser_rule(ch.student_raw_id, ch.udise_code, 3, subject, w.item_responses, w.item_bank)
            d_bayes = bayes_irt(ch.student_raw_id, ch.udise_code, 3, subject, w.item_responses, w.item_bank, load_cutpoints(subject))
            d_cat, used = adaptive_test(ch.student_raw_id, ch.udise_code, 3, subject, w.item_responses, w.item_bank, load_cutpoints(subject), max_items=8)
            for name, d, items in [("aser_rule_full", d_rule, 16), ("bayes_irt_full", d_bayes, 16), ("adaptive_cat_8", d_cat, len(used))]:
                method_data[name]["pred"].append(int(d.level))
                method_data[name]["goal_prob"].append(float(d.meets_grade_goal))
                method_data[name]["items"].append(float(items))
        for name, vals in method_data.items():
            pred = vals["pred"]
            goal_hat = [int(p >= 0.5) for p in vals["goal_prob"]]
            pred_tarl = _tarl_assign(pred, schools)
            per_method[name]["level_acc"].append(accuracy_score(true_levels, pred))
            per_method[name]["adjacent_acc"].append(float(np.mean([abs(p - t) <= 1 for p, t in zip(pred, true_levels)])))
            per_method[name]["goal_acc"].append(accuracy_score(true_goal, goal_hat))
            per_method[name]["brier"].append(brier_score_loss(true_goal, vals["goal_prob"]))
            per_method[name]["tarl_acc"].append(accuracy_score(true_tarl, pred_tarl))
            per_method[name]["mean_items"].append(float(np.mean(vals["items"])))
            per_method[name]["p90_items"].append(float(np.percentile(vals["items"], 90)))
            per_method[name]["minutes"].append(float(np.mean(vals["items"]) * SECONDS_PER_ORAL_ITEM / 60.0))
    return {name: {k: float(np.mean(v)) for k, v in vals.items()} for name, vals in per_method.items()}


def evaluate_seeds(seeds: list[int] = SEEDS) -> dict[str, dict[str, tuple[float, float]]]:
    collected: dict[str, dict[str, list[float]]] = {m: _empty_metrics() for m in ["aser_rule_full", "bayes_irt_full", "adaptive_cat_8"]}
    for seed in seeds:
        one = evaluate_seed(seed)
        for method, metrics in one.items():
            for key, value in metrics.items():
                collected[method][key].append(value)
    return {m: {k: (float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0) for k, v in vals.items()} for m, vals in collected.items()}


def scalar_c4_level_acc_at_8_items(seeds: list[int] = SEEDS) -> float:
    return evaluate_seeds(seeds)["adaptive_cat_8"]["level_acc"][0]


def main() -> None:
    results = evaluate_seeds(SEEDS)
    print(f"Assumption: each oral item takes {SECONDS_PER_ORAL_ITEM}s; minutes_per_child = mean_items*{SECONDS_PER_ORAL_ITEM}/60. Seeds={SEEDS}; cohort={SAMPLE_N} children/seed, both subjects.")
    header = "method level_acc adjacent_acc goal_acc brier tarl_acc mean_items p90_items minutes_per_child"
    print(header)
    for method in ["aser_rule_full", "bayes_irt_full", "adaptive_cat_8"]:
        r = results[method]
        print(" ".join([
            method,
            f"{r['level_acc'][0]:.3f}±{r['level_acc'][1]:.3f}",
            f"{r['adjacent_acc'][0]:.3f}±{r['adjacent_acc'][1]:.3f}",
            f"{r['goal_acc'][0]:.3f}±{r['goal_acc'][1]:.3f}",
            f"{r['brier'][0]:.3f}±{r['brier'][1]:.3f}",
            f"{r['tarl_acc'][0]:.3f}±{r['tarl_acc'][1]:.3f}",
            f"{r['mean_items'][0]:.2f}±{r['mean_items'][1]:.2f}",
            f"{r['p90_items'][0]:.1f}±{r['p90_items'][1]:.1f}",
            f"{r['minutes'][0]:.2f}±{r['minutes'][1]:.2f}",
        ]))
    print(f"METRIC c4_level_acc_at_8_items={results['adaptive_cat_8']['level_acc'][0]:.3f}")


if __name__ == "__main__":
    main()
