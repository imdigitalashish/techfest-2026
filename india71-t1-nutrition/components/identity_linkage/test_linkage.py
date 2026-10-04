from __future__ import annotations

from architecture.contracts.models import IdentityRecord, LinkDecision, Sex, SourceSystem
from components.identity_linkage.eval_linkage import pairwise_metrics
from components.identity_linkage.link import deterministic_links, link_from_frames, stable_child_key
from components.identity_linkage.synth_registries import generate_benchmark


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
