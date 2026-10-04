"""Tests for the encoded department boundary (pprl.py): same decisions as link.link_pprl_bloom, encodings only."""

from __future__ import annotations

import io
import json
import random
from pathlib import Path

import pandas as pd
import pytest

from components.identity_linkage.eval_linkage import pairwise_metrics
from components.identity_linkage.link import DEFAULT_CLK_KEY, link_pprl_bloom, records_from_frame
from components.identity_linkage.pprl import ALLOWED_COLUMNS, accept_at, check_boundary, encode_department, match_encoded
from components.identity_linkage.synth_registries import generate_benchmark

COMMITTED = json.loads((Path(__file__).resolve().parents[2] / "eval" / "results" / "identity_linkage.json").read_text())


def _key(d):
    return d.method, tuple((s.value, r) for s, r in d.members), d.match_probability


def test_encoded_path_reproduces_committed_default_cell() -> None:
    poshan, health, truth = generate_benchmark()
    decisions = match_encoded(encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY))
    m = pairwise_metrics(decisions, truth)
    for k in ("f1", "precision", "recall", "clerical_review_share"):
        assert m[k] == COMMITTED["pprl_bloom"][k], k


@pytest.mark.parametrize("coverage,noise", [(0.35, 0.0), (0.0, 0.4), (1.0, 0.2)])
def test_same_decisions_as_link_pprl_bloom(coverage: float, noise: float) -> None:
    poshan, health, _ = generate_benchmark(n=500, seed=7, shared_id_rate=coverage, extra_noise=noise)
    ref = link_pprl_bloom(records_from_frame(poshan), records_from_frame(health))
    got = match_encoded(encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY))
    assert [_key(d) for d in got] == [_key(d) for d in ref]


def test_only_allowed_columns_and_no_plaintext_cross_the_boundary() -> None:
    poshan, health, _ = generate_benchmark(n=300, seed=7)
    for raw in (poshan, health):
        enc = encode_department(raw, DEFAULT_CLK_KEY)
        assert tuple(enc.columns) == ALLOWED_COLUMNS
        blob = enc.to_json(orient="records")
        recs = records_from_frame(raw)
        secrets = {v for r in recs for v in (r.child_name, r.mother_name, r.father_name, r.village_code, r.awc_code,
                                            r.facility_code) if v and len(v) >= 3}
        secrets |= {r.dob.isoformat() for r in recs if r.dob}
        secrets |= {v for r in recs for v in r.shared_ids.values() if v != r.source_record_id}
        assert not [s for s in secrets if s in blob]
    with pytest.raises(ValueError):
        match_encoded(poshan, encode_department(health, DEFAULT_CLK_KEY))
    leaky = encode_department(poshan, DEFAULT_CLK_KEY).assign(child_name=poshan.child_name)
    with pytest.raises(ValueError):
        check_boundary(leaky)


def test_matcher_treats_record_ids_as_opaque_labels() -> None:
    poshan, health, _ = generate_benchmark(n=400, seed=11, shared_id_rate=0.2, extra_noise=0.1)
    ep, eh = encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY)
    rng = random.Random(5)
    rename = {rid: f"X{rng.getrandbits(48):012x}" for rid in list(ep.record_id) + list(eh.record_id)}
    back = {v: k for k, v in rename.items()}
    got = match_encoded(ep.assign(record_id=ep.record_id.map(rename)), eh.assign(record_id=eh.record_id.map(rename)))
    relabelled = [(d.method, tuple((s.value, back[r]) for s, r in d.members), d.match_probability) for d in got]
    assert relabelled == [_key(d) for d in match_encoded(ep, eh)]


def test_accept_at_equals_rerun_at_that_threshold() -> None:
    poshan, health, _ = generate_benchmark(n=500, seed=3, shared_id_rate=0.0, extra_noise=0.3)
    ep, eh = encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY)
    low = match_encoded(ep, eh, threshold=0.86)
    for t in (0.91, 0.94, 0.97):
        rerun = match_encoded(ep, eh, threshold=t)
        assert [(_key(d), d.child_key) for d in accept_at(low, t)] == [(_key(d), d.child_key) for d in rerun]


def test_sex_token_missing_after_round_trip_is_not_a_disagreement() -> None:
    poshan, health, _ = generate_benchmark(n=300, seed=7)
    ep, eh = encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY)
    ep2 = pd.read_json(io.StringIO(ep.to_json(orient="records")), orient="records")[list(ALLOWED_COLUMNS)]
    assert [_key(d) for d in match_encoded(ep2, eh)] == [_key(d) for d in match_encoded(ep, eh)]


def _accepted(decisions):
    from components.identity_linkage.eval_linkage import _accepted_pairs
    return _accepted_pairs(decisions)


def test_precision_operating_point_reaches_perfect_precision_with_ids_only() -> None:
    from components.identity_linkage.eval_linkage import precision_operating_point
    poshan, health, truth = generate_benchmark(n=400, seed=7, shared_id_rate=1.0)
    low = match_encoded(encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY), threshold=0.86)
    assert any(d.method == "probabilistic" for d in low)  # one-sided records still get (false) score-based candidates
    op = precision_operating_point(low, truth, target=1.0, start=0.91)
    assert op["reached"] and op["ids_only"] and op["display"] == "IDs only"
    m = pairwise_metrics(accept_at(low, op["threshold"]), truth)
    assert (m["precision"], m["recall"], m["f1"]) == (1.0, 1.0, 1.0)


def test_precision_operating_point_with_no_scored_pairs() -> None:
    from components.identity_linkage.eval_linkage import precision_operating_point
    poshan, health, truth = generate_benchmark(n=300, seed=7, shared_id_rate=0.5)
    low = match_encoded(encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY), threshold=0.86)
    ids_only = [d for d in low if d.method == "deterministic"]
    op = precision_operating_point(ids_only, truth, target=0.99, start=0.91)
    assert op["reached"] and op["ids_only"]
    assert precision_operating_point([], truth, target=0.99, start=0.91)["reached"] is False


@pytest.mark.parametrize("coverage,noise,target", [(0.0, 0.4, 0.98), (0.35, 0.0, 0.995), (0.2, 0.2, 0.97)])
def test_precision_operating_point_is_lowest_and_display_reproduces_links(coverage: float, noise: float, target: float) -> None:
    from components.identity_linkage.eval_linkage import precision_operating_point
    poshan, health, truth = generate_benchmark(n=600, seed=5, shared_id_rate=coverage, extra_noise=noise)
    low = match_encoded(encode_department(poshan, DEFAULT_CLK_KEY), encode_department(health, DEFAULT_CLK_KEY), threshold=0.86)
    op = precision_operating_point(low, truth, target=target, start=0.91)
    chosen = accept_at(low, op["threshold"])
    if op["reached"]:
        assert pairwise_metrics(chosen, truth)["precision"] >= target
        lower = [d.match_probability for d in low if d.method == "probabilistic" and 0.91 <= d.match_probability < op["threshold"]]
        for t in lower:  # every lower threshold misses the target
            assert pairwise_metrics(accept_at(low, t), truth)["precision"] < target
    if not op["ids_only"]:
        assert _accepted(accept_at(low, float(op["display"]))) == _accepted(chosen)
