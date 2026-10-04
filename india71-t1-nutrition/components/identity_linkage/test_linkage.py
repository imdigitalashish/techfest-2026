from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta

import pandas as pd

from architecture.contracts.models import IdentityRecord, LinkDecision, Sex, SourceSystem
from components.identity_linkage.eval_linkage import pairwise_metrics
from components.identity_linkage.link import deterministic_links, link_from_frames, stable_child_key
from components.identity_linkage.synth_registries import generate_benchmark, identities_for_cohort


def test_link_decision_validates() -> None:
    d = LinkDecision(
        child_key="abc",
        members=[(SourceSystem.POSHAN_TRACKER, "p1"), (SourceSystem.RCH, "r1")],
        method="deterministic",
        match_probability=1.0,
        synthetic=True,
    )
    assert d.members[0][0] is SourceSystem.POSHAN_TRACKER


def test_child_key_stable_for_same_inputs() -> None:
    assert stable_child_key("cluster-1", b"vault") == stable_child_key("cluster-1", b"vault")
    assert stable_child_key("cluster-1", b"vault") != stable_child_key("cluster-2", b"vault")


def test_deterministic_id_match_wins() -> None:
    p = IdentityRecord(
        source=SourceSystem.POSHAN_TRACKER,
        source_record_id="p1",
        child_name="Aarav",
        mother_name="Sita",
        dob="2021-01-02",
        sex=Sex.MALE,
        village_code="V001",
        shared_ids={"rch_id": "R1"},
        synthetic=True,
    )
    h = IdentityRecord(
        source=SourceSystem.RCH,
        source_record_id="r1",
        child_name="Different",
        mother_name="Different",
        dob="2019-05-01",
        sex=Sex.FEMALE,
        village_code="V001",
        shared_ids={"rch_id": "R1"},
        synthetic=True,
    )
    decisions, used_p, used_h = deterministic_links([p], [h])
    assert decisions[0].method == "deterministic"
    assert decisions[0].match_probability == 1.0
    assert used_p == {"p1"}
    assert used_h == {"r1"}


def test_plaintext_and_pprl_f1_on_default_benchmark() -> None:
    poshan, health, truth = generate_benchmark()
    plain = pairwise_metrics(link_from_frames(poshan, health, "plaintext"), truth)
    pprl = pairwise_metrics(link_from_frames(poshan, health, "pprl"), truth)
    assert plain["f1"] > 0.8
    assert pprl["f1"] > 0.8


def _fingerprint(p: pd.DataFrame, h: pd.DataFrame, truth: dict) -> str:
    return hashlib.sha256((p.to_csv(index=False) + h.to_csv(index=False) + repr(sorted(truth.items()))).encode()).hexdigest()


def test_stress_knob_defaults_reproduce_original_benchmark() -> None:
    # sha256 of the generator's output before the knobs were added (commit 8df16c7)
    assert _fingerprint(*generate_benchmark(n=400, seed=7)) == "d95b71920839d558a5ce2068ddd797b6a9a4889843c72cbc0bcf5228ce7607c7"
    assert _fingerprint(*generate_benchmark(n=400, seed=7, shared_id_rate=0.35, extra_noise=0.0)) == _fingerprint(*generate_benchmark(n=400, seed=7))


def _text(s: pd.Series) -> pd.Series:
    return s.map(lambda v: "" if v is None or v != v else str(v))


def test_shared_id_rate_changes_only_the_shared_ids() -> None:
    p0, h0, _ = generate_benchmark(n=300, seed=7, shared_id_rate=0.0)
    p1, h1, _ = generate_benchmark(n=300, seed=7, shared_id_rate=1.0)
    cols = ["child_name", "mother_name", "father_name", "dob", "sex", "village_code"]
    assert p0[cols].equals(p1[cols]) and h0.equals(h1)
    assert sum("rch_id" in s for s in p0.shared_ids) == 0
    assert sum("rch_id" in s for s in p1.shared_ids) > 250


def test_extra_noise_is_monotone_common_random_numbers() -> None:
    base, _, _ = generate_benchmark(n=300, seed=7)
    lo, _, _ = generate_benchmark(n=300, seed=7, extra_noise=0.1)
    hi, _, _ = generate_benchmark(n=300, seed=7, extra_noise=0.3)
    for col in ["child_name", "mother_name", "dob"]:
        changed = _text(lo[col]) != _text(base[col])
        assert changed.any()
        assert (_text(hi[col])[changed] == _text(lo[col])[changed]).all()
        assert (_text(hi[col]) != _text(base[col])).sum() > changed.sum()


def test_identities_for_cohort_link_through_pprl() -> None:
    rng = random.Random(3)
    rows = []
    for i in range(240):
        dob = date(2021, 1, 1) + timedelta(days=rng.randrange(0, 1400))
        rows.append({"child_key": f"C{i:06d}", "awc_code": f"P1S1A{1 + i % 6:02d}", "sex": rng.choice("MF"),
                     "dob_true": pd.Timestamp(dob), "dob_recorded": pd.Timestamp(dob.replace(day=1))})
    poshan, health, truth, ids = identities_for_cohort(pd.DataFrame(rows), seed=11)
    assert len(poshan) == 240 and len(ids) == 240
    assert all(truth[("poshan_tracker", v["pt_id"])] == k for k, v in ids.items())
    assert all(truth[("rch", v["rch_id"])] == k for k, v in ids.items() if v["rch_id"])
    ids_only = pairwise_metrics(link_from_frames(poshan, health, "ids"), truth)
    pprl = pairwise_metrics(link_from_frames(poshan, health, "pprl"), truth)
    assert pprl["f1"] > ids_only["f1"] and pprl["f1"] > 0.8
