"""Contract tests: run on CPU in seconds (`pytest -q tests/`)."""
from __future__ import annotations

import torch

from components.aggregator import Anchor, FedAvgAB, make_strategy
from components.contracts import DeviceProfile, export_schemas
from components.device_simulator import DEFAULT_PROFILES, availability_schedule

D_IN, D_OUT, R = 12, 10, 8


def _init(seed=0, layers=3):
    g = torch.Generator().manual_seed(seed)
    return {f"l{i}": (torch.randn(R, D_IN, generator=g), torch.zeros(D_OUT, R)) for i in range(layers)}


def _fake_train(view, rank, train_A, seed):
    g = torch.Generator().manual_seed(seed)
    out = {}
    for k, (A, B) in view.items():
        A2, B2 = A.clone(), B.clone()
        B2[:, :rank] += torch.randn(D_OUT, rank, generator=g)
        if train_A:
            A2[:rank] += 0.5 * torch.randn(rank, D_IN, generator=g)
        out[k] = (A2, B2)
    return out


def _round(strat, ranks, steps=None, n=None, t=0):
    g = strat.init_global(_init())
    payloads, metas = {}, {}
    for i, r in enumerate(ranks):
        cid = f"c{i}"
        view = strat.client_view(g, r)
        after = _fake_train(view, r, strat.train_A, seed=100 + i)
        payloads[cid], _ = strat.payload(view, after, r)
        metas[cid] = dict(n_examples=(n or [100] * len(ranks))[i], planned_steps=(steps or [4] * len(ranks))[i],
                          steps_done=(steps or [4] * len(ranks))[i])
    return strat.aggregate(g, payloads, metas, t)


def test_anchor_is_exact_for_mixed_ranks():
    _, rep = _round(Anchor(), ranks=[8, 4, 2, 1])
    assert rep["aggregation_error"] < 1e-5
    assert abs(sum(rep["influence_share"].values()) - 1.0) < 1e-4


def test_fedavg_ab_is_inexact_for_mixed_ranks():
    _, rep = _round(FedAvgAB(), ranks=[8, 4, 2, 1])
    assert rep["aggregation_error"] > 1e-3


def test_uniform_weights_cap_data_rich_device():
    _, rep_n = _round(Anchor(weighting="n"), ranks=[8, 8, 8, 8], n=[800, 100, 100, 100])
    _, rep_u = _round(Anchor(weighting="uniform"), ranks=[8, 8, 8, 8], n=[800, 100, 100, 100])
    assert rep_n["weights"]["c0"] > 0.7 and abs(rep_u["weights"]["c0"] - 0.25) < 1e-9


def test_memory_reuses_absent_device_then_expires():
    s = Anchor(memory=True, memory_max_age=1)
    g = s.init_global(_init())
    pay = {k: torch.ones(D_OUT, R) for k in g["B"]}
    meta = dict(n_examples=10, planned_steps=2, steps_done=2)
    g, rep0 = s.aggregate(g, {"c0": pay, "c1": pay}, {"c0": meta, "c1": meta}, 0)
    g, rep1 = s.aggregate(g, {"c0": pay}, {"c0": meta}, 1)
    assert rep1["used_memory_for"] == ["c1"]
    g, rep3 = s.aggregate(g, {"c0": pay}, {"c0": meta}, 3)
    assert rep3["used_memory_for"] == []


def test_nova_normalises_partial_work():
    s = Anchor(normalize="nova", weighting="uniform")
    g = s.init_global(_init(layers=1))
    k = next(iter(g["B"]))
    full = {k: torch.full((D_OUT, R), 4.0)}   # 4 steps of +1
    part = {k: torch.full((D_OUT, R), 1.0)}   # 1 step of +1 (cut off)
    g, _ = s.aggregate(g, {"c0": full, "c1": part},
                       {"c0": dict(n_examples=1, planned_steps=4, steps_done=4),
                        "c1": dict(n_examples=1, planned_steps=4, steps_done=1)}, 0)
    assert torch.allclose(g["B"][k], torch.full((D_OUT, R), 4.0))  # both directions count per step


def test_schedule_is_strategy_independent_and_seeded():
    a = availability_schedule(DEFAULT_PROFILES, 12, seed=3, scenario="dropout")
    b = availability_schedule(DEFAULT_PROFILES, 12, seed=3, scenario="dropout")
    assert a == b
    assert all(a[(t, "c4")] == 0 for t in range(4, 9))
    assert all(v == p.local_steps for (t, c), v in availability_schedule(DEFAULT_PROFILES, 5, 0, "clean").items()
               for p in DEFAULT_PROFILES if p.client_id == c)


def test_registry_and_schemas(tmp_path):
    for name in ["fedavg_ab_homo", "fedavg_ab_het", "anchor_naive", "anchor_full"]:
        make_strategy(name)
    assert len(export_schemas(tmp_path)) == 6
    DeviceProfile(client_id="x", device_class="phone", domain="wiki", n_train_blocks=1, rank=1, local_steps=1)


def test_new_anchor_options_keep_exactness():
    for kw in [dict(segment_norm=True), dict(tau_from="actual", normalize="nova"),
               dict(memory=True, memory_decay=0.5), dict(weighting="sqrt_n")]:
        _, rep = _round(Anchor(**kw), ranks=[8, 4, 2, 1], steps=[4, 1, 2, 4])
        assert rep["aggregation_error"] < 1e-5, kw


def test_segment_norm_gives_full_weight_to_sole_owner_of_a_column():
    s = Anchor(segment_norm=True, weighting="uniform")
    g = s.init_global(_init(layers=1))
    k = next(iter(g["B"]))
    hi = torch.zeros(D_OUT, R)
    hi[:, :] = 1.0                     # rank-8 device writes every column
    lo = torch.zeros(D_OUT, R)
    lo[:, :2] = 1.0                    # rank-2 device writes columns 0-1 only
    meta = dict(n_examples=1, planned_steps=1, steps_done=1)
    g, _ = s.aggregate(g, {"c0": {k: hi}, "c1": {k: lo}}, {"c0": meta, "c1": meta}, 0)
    assert torch.allclose(g["B"][k], torch.ones(D_OUT, R))  # shared columns: mean of 1 and 1; others: sole owner


def test_default_coefficients_match_scalar_path():
    s = Anchor(normalize="nova", weighting="uniform")
    g = s.init_global(_init(layers=1))
    k = next(iter(g["B"]))
    gen = torch.Generator().manual_seed(1)
    p = {c: {k: torch.randn(D_OUT, R, generator=gen)} for c in ("c0", "c1", "c2")}
    m = {c: dict(n_examples=1 + i, planned_steps=3 + i, steps_done=1 + i) for i, c in enumerate(p)}
    g, _ = s.aggregate(g, p, m, 0)
    w = 1 / 3
    tau = sum(w * m[c]["planned_steps"] for c in sorted(p))   # same op order as Anchor.aggregate
    ref = g["B"][k].new_zeros(D_OUT, R) + sum((1.0 * tau * w) * (p[c][k] * (1.0 / m[c]["steps_done"]))
                                              for c in sorted(p))
    assert torch.equal(g["B"][k], ref)
