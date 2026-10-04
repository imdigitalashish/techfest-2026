"""Evaluate identity linkage benchmark and print one JSON line."""

from __future__ import annotations

import json
import time
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
