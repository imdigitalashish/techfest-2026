import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from mrv_ledger import chain
from mrv_ledger.canonical import canonical_json
from mrv_ledger.evaluate import _mutations
from mrv_ledger.reconcile import DEFAULT, reconcile
from mrv_ledger.synth import make_trips

JS = Path(__file__).resolve().parents[2] / "dashboard" / "site" / "ledger_verify.js"


@pytest.fixture(scope="module")
def ledger():
    trips = make_trips({"honest": 30, "inflated": 10, "phantom": 5, "wetted": 5}, seed=3)
    entries = []
    for t in trips:
        chain.append(entries, t.record, reconcile(t.record, t.capacity_m3))
    return entries


def test_clean_chain_verifies(ledger):
    assert chain.verify(ledger, chain.anchor(ledger)).ok
    assert ledger[0].prev_hash == chain.GENESIS_HASH


def test_every_single_field_edit_is_detected(ledger):
    for i, e in enumerate(ledger):
        for m in _mutations(e):
            es = list(ledger)
            es[i] = m()
            assert not chain.verify(es).ok, (i, es[i])


def test_every_deletion_and_adjacent_swap_is_detected(ledger):
    anchor = chain.anchor(ledger)
    for i in range(len(ledger)):
        es = ledger[:i] + ledger[i + 1:]
        assert not chain.verify(es, anchor).ok
        if i + 1 < len(ledger):
            es = list(ledger)
            es[i], es[i + 1] = es[i + 1], es[i]
            assert not chain.verify(es).ok


def test_tail_truncation_needs_the_anchor(ledger):
    cut = ledger[:-1]
    assert chain.verify(cut).ok  # chain alone cannot see a missing tail ...
    assert not chain.verify(cut, chain.anchor(ledger)).ok  # ... the published anchor can


def test_signatures_catch_a_consistent_rewrite(ledger):
    keys = {e.record.crew_id: chain.demo_key(e.record.crew_id) for e in ledger}
    reg = {k: chain.public_hex(v) for k, v in keys.items()}
    sigs = [chain.sign_entry(e, e.record.crew_id, keys[e.record.crew_id]) for e in ledger]
    assert chain.verify_signatures(ledger, sigs, reg).ok
    es = []
    for e in ledger:
        rec = e.record.model_copy(update={"claimed_wet_kg": e.record.claimed_wet_kg * 2}) if e.seq == 5 else e.record
        chain.append(es, rec, e.reconciliation)
    assert chain.verify(es).ok  # re-hashed chain is internally consistent
    assert not chain.verify_signatures(es, sigs, reg).ok


@pytest.mark.parametrize("x,expected", [
    (1e16, "10000000000000000"), (1e21, "1e+21"), (1e-5, "0.00001"), (1e-7, "1e-7"), (123.456, "123.456"),
    (0.5, "0.5"), (12.0, "12"), (-0.25, "-0.25"), (1.5e300, "1.5e+300"), (5e-324, "5e-324"), (0.1 + 0.2, "0.30000000000000004"),
])
def test_number_layout_matches_ecmascript(x, expected):
    assert canonical_json(x) == expected


def test_keys_sorted_and_compact():
    assert canonical_json({"b": [1, 2.5, None], "a": {"y": True, "x": "é\n"}}) == '{"a":{"x":"é\\n","y":true},"b":[1,2.5,null]}'


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_browser_verifier_matches_python(ledger, tmp_path):
    rng = random.Random(5)
    nums = [rng.uniform(-1e6, 1e6) for _ in range(200)] + [rng.random() * 10 ** rng.randint(-12, 25) for _ in range(200)]
    good = [json.loads(e.model_dump_json()) for e in ledger]
    bad = list(good)
    bad[7] = dict(bad[7], record=dict(bad[7]["record"], claimed_wet_kg=bad[7]["record"]["claimed_wet_kg"] + 1))
    (tmp_path / "in.json").write_text(json.dumps({"good": good, "bad": bad, "nums": nums, "anchor": chain.anchor(ledger)}))
    script = f"""
const L = require({json.dumps(str(JS))}); const d = require({json.dumps(str(tmp_path / 'in.json'))});
(async () => {{
  const g = await L.verifyChain(d.good, d.anchor), b = await L.verifyChain(d.bad, d.anchor);
  console.log(JSON.stringify({{g: g.ok, b: b.ok, bad: b.badSeqs, nums: d.nums.map(L.canonicalize),
    syncHash: L.sha256HexSync(L.entryBody(d.good[0]))}}));
}})();"""
    out = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    assert out["g"] is True and out["b"] is False and out["bad"] == [7]
    assert out["nums"] == [canonical_json(x) for x in nums]
    assert out["syncHash"] == ledger[0].hash


def test_reconcile_flags():
    trips = make_trips({"honest": 1, "phantom": 1}, seed=9)
    flags = {t.kind: reconcile(t.record, t.capacity_m3).flag for t in trips}
    assert flags["phantom"] in ("review", "reject")
    honest = next(t for t in trips if t.kind == "honest")
    big = honest.record.model_copy(update={"claimed_wet_kg": honest.record.claimed_wet_kg * 10 + 500})
    assert reconcile(big, honest.capacity_m3).flag == "reject"
    no_fill = honest.record.model_copy(update={"pre_fill_fraction": None})
    r = reconcile(no_fill, honest.capacity_m3)
    assert r.flag == "review" and any("cannot reconcile" in x for x in r.reasons)
    assert reconcile(no_fill, honest.capacity_m3, twin_cleared_wet_kg=honest.true_wet_kg).sensor_estimated_kg > 0
    assert DEFAULT.dry_density_kg_m3 == pytest.approx(DEFAULT.wet_bulk_density_kg_m3 * (1 - DEFAULT.moisture_fraction))


# ------------------------------------------------- signer binding (review issue 4) ----
def _keys(entries):
    keys = {c: chain.demo_key(c) for c in sorted({e.record.crew_id for e in entries})}
    return keys, {c: chain.public_hex(k) for c, k in keys.items()}


def test_cross_crew_resign_is_rejected_unless_delegated(ledger):
    keys, reg = _keys(ledger)
    e = ledger[0]
    other = next(c for c in keys if c != e.record.crew_id)
    sig = chain.sign_entry(e, other, keys[other])  # valid Ed25519 from a registered device, but not this record's crew
    r = chain.verify_signatures([e], [sig], {other: reg[other]})
    assert not r.ok and "holds no delegation" in r.problems[0]
    assert chain.verify_signatures([e], [sig], reg, delegations={e.record.crew_id: [other]}).ok


def test_signature_for_another_hash_is_rejected(ledger):
    keys, reg = _keys(ledger)
    e, f = ledger[0], ledger[1]
    crew = e.record.crew_id
    own = chain.sign_entry(e, crew, keys[crew])
    foreign = chain.sign_entry(e.model_copy(update={"hash": f.hash}), crew, keys[crew])  # signs f.hash at e's seq
    assert chain.verify_signatures([e], [own], reg).ok
    for s in (dict(own, hash=f.hash), foreign, dict(foreign, hash=e.hash)):
        assert not chain.verify_signatures([e], [s], reg).ok


def test_insider_resign_is_caught_by_other_crews_or_the_anchor(ledger):
    keys, reg = _keys(ledger)
    sigs = [chain.sign_entry(e, e.record.crew_id, keys[e.record.crew_id]) for e in ledger]
    published = chain.anchor(ledger)

    def resign_from(j):
        es = ledger[:j]
        for e in ledger[j:]:
            rec = e.record.model_copy(update={"claimed_wet_kg": e.record.claimed_wet_kg * 2}) if e.seq == j else e.record
            chain.append(es, rec, e.reconciliation)
        insider = ledger[j].record.crew_id
        return es, sigs[:j] + [chain.sign_entry(e, insider, keys[insider]) for e in es[j:]]

    es, new = resign_from(10)  # the re-signed suffix holds other crews' records
    assert chain.verify(es).ok and not chain.verify_signatures(es, new, reg).ok
    es, new = resign_from(len(ledger) - 1)  # only the insider's own newest record: signatures cannot tell
    assert chain.verify_signatures(es, new, reg).ok and not chain.verify(es, published).ok


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_browser_signature_checks_match_python(ledger, tmp_path):
    keys, reg = _keys(ledger)
    good = [chain.sign_entry(e, e.record.crew_id, keys[e.record.crew_id]) for e in ledger]
    e0 = ledger[0]
    other = next(c for c in keys if c != e0.record.crew_id)
    data = {"entries": [json.loads(e.model_dump_json()) for e in ledger], "reg": reg, "good": good,
            "cross": [chain.sign_entry(e0, other, keys[other])] + good[1:],
            "wrong": [dict(good[0], hash=ledger[1].hash)] + good[1:], "deleg": {e0.record.crew_id: [other]}}
    (tmp_path / "s.json").write_text(json.dumps(data))
    script = f"""
const L = require({json.dumps(str(JS))}); const d = require({json.dumps(str(tmp_path / 's.json'))});
(async () => {{
  const r = (s, g) => L.verifySignatures(d.entries, s, d.reg, g);
  console.log(JSON.stringify({{good: await r(d.good), cross: await r(d.cross), wrong: await r(d.wrong),
    deleg: await r(d.cross, d.deleg), legacy: await L.verifySignatures(d.entries, d.good, d.reg)}}));
}})();"""
    out = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    if not out["good"].get("supported"):
        pytest.skip("this node's WebCrypto lacks Ed25519")
    assert out["good"]["ok"] and out["legacy"]["ok"] and out["deleg"]["ok"]
    assert out["cross"]["badSeqs"] == [0] and "no delegation" in out["cross"]["problems"][0]
    assert out["wrong"]["badSeqs"] == [0] and "different hash" in out["wrong"]["problems"][0]
