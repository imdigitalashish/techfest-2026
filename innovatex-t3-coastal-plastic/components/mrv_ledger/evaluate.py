"""Isolated metric for C11 on SYNTHETIC trips + tamper campaign. Writes results/metrics.json and eval_detail.json.

Reproduce: cd innovatex-t3-coastal-plastic/components && python3 -m mrv_ledger.evaluate
"""
from __future__ import annotations

import json
import math
import random
import subprocess
from dataclasses import replace
from pathlib import Path

from . import chain
from .reconcile import DEFAULT, Params, reconcile, z_score
from .synth import Trip, make_trips

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
REPRODUCE = "cd innovatex-t3-coastal-plastic/components && python3 -m mrv_ledger.evaluate"
TARGET_FPR = 0.05
OFF = 1e9


def _scores(trips: list[Trip], p: Params):
    z, ratio, rule = [], [], []
    no_z = replace(p, z_review=OFF, z_reject=OFF)
    for t in trips:
        r = t.record
        claimed = r.claimed_wet_kg * (1 - p.moisture_fraction)
        sensor = max(0.0, r.pre_fill_fraction - r.post_fill_fraction) * t.capacity_m3 * p.dry_density_kg_m3
        z.append(z_score(claimed, sensor, t.capacity_m3, p))
        ratio.append(claimed / max(sensor, 1.0))
        rule.append(reconcile(r, t.capacity_m3, no_z).flag != "ok")
    return z, ratio, rule


def _threshold(scores: list[float], always: list[bool], fpr: float) -> float:
    """Smallest threshold whose honest flag rate (score > thr or rule flag) is <= fpr."""
    n = len(scores)
    budget = int(fpr * n) - sum(always)
    free = sorted((s for s, a in zip(scores, always) if not a), reverse=True)
    if budget < 0:
        return float("inf")
    return free[budget] if budget < len(free) else float("-inf")


def _auc(pos: list[float], neg: list[float]) -> float:
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank_sum, i = 0.0, 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        rank_sum += avg * sum(1 for k in range(i, j + 1) if allv[k][1] == 1)
        i = j + 1
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def _precision(prev: float, tpr: float, fpr: float) -> float:
    d = prev * tpr + (1 - prev) * fpr
    return prev * tpr / d if d else 0.0


def evaluate_reconciliation(p: Params = DEFAULT, n_cal: int = 20000, seed_cal: int = 11, seed_test: int = 12) -> dict:
    cal = make_trips({"honest": n_cal}, seed=seed_cal, p=p)
    z_c, r_c, rule_c = _scores(cal, p)
    # conservative calibration: aim below 5% by the one-sided 95% sampling margin of the calibration set
    cal_target = TARGET_FPR - 1.645 * math.sqrt(TARGET_FPR * (1 - TARGET_FPR) / n_cal)
    z_thr = _threshold(z_c, rule_c, cal_target)
    r_thr = _threshold(r_c, [False] * len(r_c), cal_target)
    test = make_trips({"honest": 10000, "inflated": 3000, "phantom": 1000, "wetted": 1000}, seed=seed_test, p=p)
    z_t, r_t, rule_t = _scores(test, p)
    flag_prop = [a or z > z_thr for z, a in zip(z_t, rule_t)]
    flag_base = [r > r_thr for r in r_t]
    flag_quo = [t.record.weighbridge_wet_kg is not None and t.record.claimed_wet_kg > 1.02 * t.record.weighbridge_wet_kg
                for t in test]
    honest = [i for i, t in enumerate(test) if t.kind == "honest"]
    fraud = [i for i, t in enumerate(test) if t.kind != "honest"]

    def rate(flags, idx):
        return sum(flags[i] for i in idx) / len(idx) if idx else float("nan")

    out = {"calibration_target_fpr": round(cal_target, 4), "z_threshold_review": round(z_thr, 4), "ratio_threshold_baseline": round(r_thr, 4), "methods": {}}
    for name, flags, score in (("proposed_z", flag_prop, z_t), ("baseline_ratio", flag_base, r_t),
                               ("status_quo_slip_check", flag_quo, None)):
        tpr, fpr = rate(flags, fraud), rate(flags, honest)
        m = {"recall_all_fraud": tpr, "false_flag_rate_honest": fpr,
             "precision_at_5pct_prevalence": _precision(0.05, tpr, fpr),
             "precision_at_10pct_prevalence": _precision(0.10, tpr, fpr)}
        for kind in ("inflated", "phantom", "wetted"):
            m[f"recall_{kind}"] = rate(flags, [i for i in fraud if test[i].kind == kind])
        for lo, hi in ((1.2, 1.5), (1.5, 2.0), (2.0, 3.0)):
            m[f"recall_inflated_x{lo}-{hi}"] = rate(flags, [i for i in fraud if test[i].kind == "inflated"
                                                           and lo <= test[i].factor < hi])
        if score is not None:
            m["auc"] = _auc([score[i] for i in fraud], [score[i] for i in honest])
        out["methods"][name] = {k: round(v, 4) for k, v in m.items()}
    # sensitivity: nominal density wrong by -20% / +25% (honest trips only, same thresholds)
    sens = {}
    for bias in (0.8, 1.25):
        hon = make_trips({"honest": 2000}, seed=13, p=p, density_bias=bias)
        z_h, _, rule_h = _scores(hon, p)
        sens[f"false_flag_rate_if_true_density_x{bias}"] = round(
            sum(a or z > z_thr for z, a in zip(z_h, rule_h)) / len(z_h), 4)
    out["sensitivity"] = sens
    out["n_test"] = {k: sum(t.kind == k for t in test) for k in ("honest", "inflated", "phantom", "wetted")}
    return out, test, z_thr


# ------------------------------------------------------------------ tampering ----
def _mutations(e):
    r, c = e.record, e.reconciliation
    return [
        lambda: e.model_copy(update={"record": r.model_copy(update={"claimed_wet_kg": r.claimed_wet_kg + 0.01})}),
        lambda: e.model_copy(update={"record": r.model_copy(update={"site_id": r.site_id + "x"})}),
        lambda: e.model_copy(update={"record": r.model_copy(update={"crew_id": "SYN-crew-9"})}),
        lambda: e.model_copy(update={"record": r.model_copy(update={"post_fill_fraction": (r.post_fill_fraction or 0) + (0.001 if (r.post_fill_fraction or 0) < 0.5 else -0.001)})}),
        lambda: e.model_copy(update={"record": r.model_copy(update={"photo_sha256": r.photo_sha256[:1]})}),
        lambda: e.model_copy(update={"record": r.model_copy(update={"t_end": r.t_end.replace(minute=(r.t_end.minute + 1) % 60)})}),
        lambda: e.model_copy(update={"reconciliation": c.model_copy(update={"flag": "ok" if c.flag != "ok" else "review"})}),
        lambda: e.model_copy(update={"reconciliation": c.model_copy(update={"sensor_estimated_kg": c.sensor_estimated_kg * 2 + 1})}),
        lambda: e.model_copy(update={"reconciliation": c.model_copy(update={"reasons": c.reasons[1:]})}),
        lambda: e.model_copy(update={"prev_hash": "f" * 64}),
    ]


def tamper_campaign(trips: list[Trip], p: Params, n_entries: int = 300, trials: int = 200, seed: int = 21) -> dict:
    rng = random.Random(seed)
    entries = []
    for t in trips[:n_entries]:
        chain.append(entries, t.record, reconcile(t.record, t.capacity_m3, p))
    published = chain.anchor(entries)
    keys = {f"SYN-crew-{i}": chain.demo_key(f"SYN-crew-{i}") for i in range(1, 6)}
    registry = {k: chain.public_hex(v) for k, v in keys.items()}
    sigs = [chain.sign_entry(e, e.record.crew_id, keys[e.record.crew_id]) for e in entries]
    assert chain.verify(entries, published).ok and chain.verify_signatures(entries, sigs, registry).ok

    def rewrite(es, j):
        es = list(es)
        es[j] = _mutations(es[j])[0]()
        for k in range(j, len(es)):
            prev = es[k - 1].hash if k else chain.GENESIS_HASH
            es[k] = es[k].model_copy(update={"seq": k, "prev_hash": prev,
                                             "hash": chain.entry_hash(k, es[k].record, es[k].reconciliation, prev)})
        return es

    def op(kind):
        es = list(entries)
        j = rng.randrange(len(es))
        if kind == "edit":
            es[j] = rng.choice(_mutations(es[j]))()
        elif kind == "delete":
            del es[j]
        elif kind == "reorder":
            k = rng.choice([x for x in range(len(es)) if x != j])
            es[j], es[k] = es[k], es[j]
        elif kind == "insert":
            prev = es[j - 1].hash if j else chain.GENESIS_HASH
            forged = es[j].model_copy(update={"seq": j, "prev_hash": prev})
            forged = forged.model_copy(update={"hash": chain.entry_hash(j, forged.record, forged.reconciliation, prev)})
            es.insert(j, forged)
        elif kind == "truncate_tail":
            es = es[:len(es) - rng.randint(1, 5)]
        elif kind == "rewrite_suffix":
            es = rewrite(es, j)
        return es

    res = {}
    for kind in ("edit", "delete", "reorder", "insert", "truncate_tail", "rewrite_suffix"):
        with_anchor = without = 0
        for _ in range(trials):
            es = op(kind)
            with_anchor += not chain.verify(es, published).ok
            without += not chain.verify(es).ok
        res[kind] = {"trials": trials, "detected_with_anchor": with_anchor / trials, "detected_chain_only": without / trials}
    es = rewrite(entries, rng.randrange(len(entries)))
    res["rewrite_suffix"]["detected_by_signatures"] = float(not chain.verify_signatures(es, sigs, registry).ok)
    res["all_detected_with_anchor"] = all(v["detected_with_anchor"] == 1.0 for k, v in res.items() if isinstance(v, dict))
    return res


def main() -> dict:
    OUT.mkdir(exist_ok=True)
    rec, test, z_thr = evaluate_reconciliation()
    tam = tamper_campaign(test, replace(DEFAULT, z_review=z_thr))
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    except OSError:
        sha = "unknown"
    detail = {"data": "SYNTHETIC (mrv_ledger/synth.py); parameters are ASSUMPTIONS (reconcile.Params)",
              "params": DEFAULT.as_dict(), "reconciliation": rec, "tamper": tam, "git_sha_at_run": sha,
              "reproduce": REPRODUCE}
    (OUT / "eval_detail.json").write_text(json.dumps(detail, indent=1))
    prop, base = rec["methods"]["proposed_z"], rec["methods"]["baseline_ratio"]
    flat = {
        "data": "SYNTHETIC",
        "recall_fraud_at_5pct_false_flags": prop["recall_all_fraud"],
        "false_flag_rate_test": prop["false_flag_rate_honest"],
        "recall_inflated_x1.2-3": prop["recall_inflated"],
        "recall_inflated_x1.2-1.5": prop["recall_inflated_x1.2-1.5"],
        "recall_phantom": prop["recall_phantom"],
        "recall_wetted_or_silted": prop["recall_wetted"],
        "precision_at_5pct_prevalence": prop["precision_at_5pct_prevalence"],
        "precision_at_10pct_prevalence": prop["precision_at_10pct_prevalence"],
        "baseline_ratio_recall_at_5pct": base["recall_all_fraud"],
        "status_quo_slip_check_recall": rec["methods"]["status_quo_slip_check"]["recall_all_fraud"],
        "tamper_detection_rate_with_anchor": min(v["detected_with_anchor"] for v in tam.values() if isinstance(v, dict)),
        "reproduce": REPRODUCE,
    }
    (OUT / "metrics.json").write_text(json.dumps(flat, indent=1))
    return flat


if __name__ == "__main__":
    for k, v in main().items():
        print(f"{k}: {v}")
