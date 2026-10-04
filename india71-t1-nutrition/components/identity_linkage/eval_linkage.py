"""Evaluate identity linkage benchmark and print one JSON line."""

from __future__ import annotations

import json
import math
import time
from decimal import ROUND_FLOOR, Decimal
from typing import Iterable

from architecture.contracts.models import LinkDecision
from components.identity_linkage.link import link_from_frames
from components.identity_linkage.synth_registries import generate_benchmark


def _accepted_pairs(decisions: Iterable[LinkDecision]) -> set[frozenset[tuple[str, str]]]:
    out = set()
    for d in decisions:
        if d.method in {"deterministic", "probabilistic"} and len(d.members) == 2:
            out.add(frozenset((src.value, rid) for src, rid in d.members))
    return out


def _truth_pairs(truth: dict[tuple[str, str], str]) -> set[frozenset[tuple[str, str]]]:
    by_cluster: dict[str, list[tuple[str, str]]] = {}
    for record, cluster in truth.items():
        by_cluster.setdefault(cluster, []).append(record)
    pairs = set()
    for members in by_cluster.values():
        if len(members) == 2:
            pairs.add(frozenset(members))
    return pairs


def pairwise_metrics(decisions: list[LinkDecision], truth: dict[tuple[str, str], str]) -> dict[str, float]:
    pred = _accepted_pairs(decisions)
    gold = _truth_pairs(truth)
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    clerical_share = sum(1 for d in decisions if d.method == "clerical_review") / max(1, len(decisions))
    return {"precision": precision, "recall": recall, "f1": f1, "clerical_review_share": clerical_share}


def _display_threshold(lo: float | None, hi: float) -> str:
    """Shortest decimal string v (rounded down from hi) with lo < float(v) <= hi: any such threshold gives the same links."""
    for digits in range(3, 18):
        v = Decimal(hi).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_FLOOR)
        if (lo is None or float(v) > lo) and float(v) <= hi:
            return format(v, "f")
    return repr(hi)


def precision_operating_point(decisions: Iterable[LinkDecision], truth: dict[tuple[str, str], str], target: float,
                              start: float) -> dict[str, object]:
    """IN-SAMPLE helper (it uses the gold labels): the lowest acceptance threshold >= `start` at which the precision of
    accepted links reaches `target`, for decisions matched at a low clerical threshold (see pprl.accept_at, which makes
    the one-to-one assignment independent of the threshold).

    Candidate operating points, most links first: every distinct score >= start (accept that score and above), then the
    upper end that accepts no score-based link at all (shared-ID links only). An operating point with no accepted link has
    no precision and is never "reached". Returns threshold (exact; any value in (interval[0], interval[1]] gives the same
    links), interval, display (shortest decimal in that interval), ids_only, reached."""
    gold = _truth_pairs(truth)
    det = [frozenset((s.value, r) for s, r in d.members) for d in decisions if d.method == "deterministic"]
    scored = sorted(((d.match_probability, frozenset((s.value, r) for s, r in d.members) in gold)
                     for d in decisions if d.method in ("probabilistic", "clerical_review") and len(d.members) == 2),
                    key=lambda x: -x[0])
    distinct = sorted({s for s, _ in scored}, reverse=True)
    max_score = distinct[0] if distinct else None
    upper = math.nextafter(max_score, math.inf) if max_score is not None else start
    points = [{"threshold": max(upper, start), "interval": [max_score, None], "ids_only": True,
               "accepted": len(det), "true": sum(p in gold for p in det)}]
    n_acc, n_true, i = points[0]["accepted"], points[0]["true"], 0
    for k, t in enumerate(distinct):
        while i < len(scored) and scored[i][0] == t:
            n_acc += 1
            n_true += scored[i][1]
            i += 1
        if t < start:
            break
        lower = distinct[k + 1] if k + 1 < len(distinct) else None
        points.append({"threshold": t, "interval": [lower, t], "ids_only": False, "accepted": n_acc, "true": n_true})
    ok = [p for p in points if p["accepted"] and p["true"] / p["accepted"] >= target]
    reached = bool(ok)
    best = min(ok, key=lambda p: p["threshold"]) if ok else max(
        (p for p in points if p["accepted"]), key=lambda p: (p["true"] / p["accepted"], -p["threshold"]), default=points[0])
    lo, hi = best["interval"]
    display = "IDs only" if best["ids_only"] else _display_threshold(lo, hi)
    return {"threshold": best["threshold"], "interval": [lo, hi], "display": display, "ids_only": best["ids_only"],
            "reached": reached, "target_precision": target}


def run_eval(n: int = 5000, seed: int = 2026) -> dict[str, object]:
    poshan, health, truth = generate_benchmark(n=n, seed=seed)
    result: dict[str, object] = {"n_true_children": n, "poshan_records": len(poshan), "health_records": len(health)}
    for name, method in [("ids_only", "ids"), ("plaintext_probabilistic", "plaintext"), ("pprl_bloom", "pprl")]:
        start = time.perf_counter()
        decisions = link_from_frames(poshan, health, method=method)  # type: ignore[arg-type]
        metrics = pairwise_metrics(decisions, truth)
        metrics["runtime_seconds"] = time.perf_counter() - start
        result[name] = metrics
    return result


if __name__ == "__main__":
    print(json.dumps(run_eval(), sort_keys=True, separators=(",", ":")))
