"""C6 Aggregator: turns device updates into the next global adapter.

Baselines
  FedAvgAB   FedAvg over LoRA A and B *separately*, weights ∝ n_k: what "PEFT + Flower FedAvg" does.
             Heterogeneous ranks via HetLoRA-style zero-padding/truncation. Devices cut off by the
             round deadline are dropped. Inexact: mean(B)·mean(A) ≠ mean(B·A).
Spike (working name "AnchorLoRA")
  Anchor     All devices share one frozen, seed-generated A (the anchor); device k trains only the
             first r_k columns of B. Updates live in one fixed linear space, so aggregation is exact
             for any mix of ranks (Σ_k w_k ΔB_k·A = Σ_k w_k (ΔB_k A)), and classic FL machinery applies
             exactly on top: FedNova step-normalisation, macro (uniform) weights, median-norm clipping,
             MIFA-style memory of absent devices, and acceptance of partial work.
             Prior-art status of each ingredient: see research/components/aggregator.md.

Published baselines
  FFA-LoRA   (ICLR 2024) freeze the random A, FedAvg(n_k) over B, homogeneous rank: `Anchor(homogeneous_rank=8)`.
  FlexLoRA   (arXiv 2402.11505) heterogeneous ranks; n_k-weighted full-size product average + SVD redistribution.

Strategies work on plain dicts of tensors (no model), so they are unit-testable on random tensors.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import torch

LayerState = dict[str, tuple[torch.Tensor, torch.Tensor]]


def product_space_report(layers, delta: Callable[[str], torch.Tensor], cids: list[str],
                         contrib: Callable[[str, str], torch.Tensor]) -> dict:
    """Per-device influence on the applied update, in ΔW = B·A space, computed layer by layer.

    P = delta(layer) is the global update actually applied; c_k = contrib(k, layer) is what the strategy meant to
    add for device k. Returns influence_share {k: <c_k, P> / ||P||²} (projection; can exceed 1 or go negative
    when contributions cancel), norm_share {k: ||c_k|| / Σ_j ||c_j||} (bounded in [0, 1]), aggregation_error
    ||P − Σ_k c_k|| / ||Σ_k c_k|| (0 when aggregation is exact) and update_norm ||P||.
    """
    dots = {c: 0.0 for c in cids}
    sq = {c: 0.0 for c in cids}
    pp = err = cc = 0.0
    for name in layers:
        P = delta(name)
        S = torch.zeros_like(P)
        dvec, nvec = [], []
        for c in cids:
            C = contrib(c, name)
            dvec.append((C * P).sum())
            nvec.append((C * C).sum())
            S += C
        vals = torch.stack([(P * P).sum(), ((P - S) ** 2).sum(), (S * S).sum()] + dvec + nvec).tolist()
        pp, err, cc = pp + vals[0], err + vals[1], cc + vals[2]
        for i, c in enumerate(cids):
            dots[c] += vals[3 + i]
            sq[c] += vals[3 + len(cids) + i]
    norms = {c: math.sqrt(v) for c, v in sq.items()}
    tot = sum(norms.values())
    resid = math.sqrt(err)
    # relative error is undefined when the intended contributions cancel to ~0 (review 2026-10-04, item 6)
    rel = resid / math.sqrt(cc) if cc > 1e-24 else (0.0 if resid == 0.0 else None)
    return dict(influence_share={c: (d / pp if pp > 0 else 0.0) for c, d in dots.items()},
                norm_share={c: (v / tot if tot > 0 else 0.0) for c, v in norms.items()},
                aggregation_error=rel, aggregation_residual=resid,
                update_norm=math.sqrt(pp))


EMPTY_REPORT = dict(reporters=[], used_memory_for=[], weights={}, influence_share={}, norm_share={},
                    aggregation_error=0.0, aggregation_residual=0.0, update_norm=0.0)


def _pad_pair(pair: tuple[torch.Tensor, torch.Tensor], ref: tuple[torch.Tensor, torch.Tensor]):
    """Zero-pad a sliced (A_k [r_k, d_in], B_k [d_out, r_k]) to the global (r_max) shapes and device of `ref`."""
    a, b = pair
    A_ref, B_ref = ref
    if a.shape == A_ref.shape:
        return a.to(A_ref.device), b.to(B_ref.device)  # no-op in-process; needed when payloads arrive on CPU (Flower)
    A = torch.zeros_like(A_ref)
    B = torch.zeros_like(B_ref)
    A[: a.shape[0]] = a.to(A.device)
    B[:, : b.shape[1]] = b.to(B.device)
    return A, B


def _weights(cids: list[str], n: dict[str, int], scheme: str) -> dict[str, float]:
    if scheme == "n":
        raw = {c: float(n[c]) for c in cids}
    elif scheme == "sqrt_n":
        raw = {c: math.sqrt(n[c]) for c in cids}
    elif scheme == "uniform":
        raw = {c: 1.0 for c in cids}
    else:
        raise ValueError(scheme)
    tot = sum(raw.values())
    return {c: v / tot for c, v in raw.items()}


@dataclass
class FedAvgAB:
    name: str = "fedavg_ab"
    homogeneous_rank: int | None = None  # set → every device uses this rank (literal starter baseline)
    weighting: str = "n"
    train_A: bool = True
    accept_partial: bool = False

    def rank_for(self, device_rank: int) -> int:
        return self.homogeneous_rank or device_rank

    def init_global(self, init: LayerState) -> dict:
        return {"layers": {k: (A.clone(), B.clone()) for k, (A, B) in init.items()}}

    def client_view(self, g: dict, rank: int) -> LayerState:
        view = {}
        for k, (A, B) in g["layers"].items():
            A2, B2 = A.clone(), B.clone()
            A2[rank:] = 0  # HetLoRA-style truncation to the device's rank
            B2[:, rank:] = 0
            view[k] = (A2, B2)
        return view

    def payload(self, view: LayerState, after: LayerState, rank: int) -> tuple[dict, int]:
        # only the device's r_k rows of A and r_k columns of B travel; the server zero-pads (HetLoRA-style)
        out = {k: (A[:rank].contiguous(), B[:, :rank].contiguous()) for k, (A, B) in after.items()}
        return out, sum(4 * (a.numel() + b.numel()) for a, b in out.values())

    def aggregate(self, g: dict, payloads: dict[str, dict], metas: dict[str, dict], t: int):
        cids = sorted(payloads)
        old = g["layers"]
        if not cids:
            return g, dict(EMPTY_REPORT)
        padded = {c: {k: _pad_pair(payloads[c][k], old[k]) for k in old} for c in cids}
        w = _weights(cids, {c: metas[c]["n_examples"] for c in cids}, self.weighting)
        new = {}
        for k in old:
            new[k] = (sum(w[c] * padded[c][k][0] for c in cids), sum(w[c] * padded[c][k][1] for c in cids))

        def contrib(c: str, k: str) -> torch.Tensor:
            A_c, B_c = padded[c][k]
            return w[c] * (B_c @ A_c - old[k][1] @ old[k][0])

        rep = product_space_report(old, lambda k: new[k][1] @ new[k][0] - old[k][1] @ old[k][0], cids, contrib)
        return {"layers": new}, dict(reporters=cids, used_memory_for=[], weights=w, **rep)

    def eval_view(self, g: dict) -> LayerState:
        return g["layers"]


@dataclass
class Anchor:
    name: str = "anchor"
    normalize: str = "none"          # "none" | "nova" (divide each update by the steps it actually did)
    weighting: str = "n"             # "n" | "sqrt_n" | "uniform" (macro objective)
    clip_kappa: float | None = None  # clip each device's update to kappa × median norm
    memory: bool = False             # MIFA-style: reuse an absent device's last update
    memory_max_age: int = 4
    accept_partial: bool = False     # keep the work of devices cut off by the deadline
    server_lr: float = 1.0
    train_A: bool = False
    homogeneous_rank: int | None = None
    tau_from: str = "planned"        # τ_eff from "planned" steps, or "actual" steps done (true FedNova)
    memory_decay: float | None = None  # weight a remembered update by decay**age, then renormalise
    segment_norm: bool = False       # PreLort-style: column j averaged only over devices with rank > j

    def rank_for(self, device_rank: int) -> int:
        return self.homogeneous_rank or device_rank

    def init_global(self, init: LayerState) -> dict:
        return {"A": {k: A.clone() for k, (A, _) in init.items()},
                "B": {k: B.clone() for k, (_, B) in init.items()},
                "mem": {}, "mem_round": {}, "n": {}, "tau": {}, "rank": {}}

    def client_view(self, g: dict, rank: int) -> LayerState:
        # every device runs the FULL global adapter; it only trains the first `rank` columns of B
        return {k: (g["A"][k].clone(), g["B"][k].clone()) for k in g["A"]}

    def payload(self, view: LayerState, after: LayerState, rank: int) -> tuple[dict, int]:
        # only the device's own r_k columns of ΔB travel (A is regenerated from the seed); the server pads
        out = {k: (after[k][1] - view[k][1])[:, :rank].contiguous() for k in after}
        return out, sum(4 * v.numel() for v in out.values())

    @staticmethod
    def _pad(payload: dict, ref: dict) -> dict:
        """Zero-pad sliced ΔB_k [d_out, r_k] back to [d_out, r_max]; exact (masked columns are zero anyway)."""
        out = {}
        for k, v in payload.items():
            full = ref[k]
            if v.shape[1] == full.shape[1]:
                out[k] = v.to(full.device)  # no-op in-process; needed when payloads arrive on CPU (Flower)
            else:
                z = torch.zeros_like(full)
                z[:, : v.shape[1]] = v.to(full.device)
                out[k] = z
        return out

    def aggregate(self, g: dict, payloads: dict[str, dict], metas: dict[str, dict], t: int):
        g.setdefault("rank", {})
        dirs = {}
        for c in sorted(payloads):
            g["n"][c] = metas[c]["n_examples"]
            g["tau"][c] = metas[c]["steps_done"] if self.tau_from == "actual" else metas[c]["planned_steps"]
            g["rank"][c] = next(iter(payloads[c].values())).shape[1]
            s = 1.0 / max(1, metas[c]["steps_done"]) if self.normalize == "nova" else 1.0
            dirs[c] = {k: v * s for k, v in self._pad(payloads[c], g["B"]).items()}
        if self.clip_kappa is not None and len(dirs) >= 2:
            norms = {c: math.sqrt(sum(float((v * v).sum()) for v in d.values())) for c, d in dirs.items()}
            med = sorted(norms.values())[len(norms) // 2]
            for c, d in dirs.items():
                f = min(1.0, self.clip_kappa * med / norms[c]) if norms[c] > 0 else 1.0
                if f < 1.0:
                    dirs[c] = {k: v * f for k, v in d.items()}
        used_memory = []
        if self.memory:
            for c, d in dirs.items():
                g["mem"][c], g["mem_round"][c] = d, t
            active = {c: g["mem"][c] for c in sorted(g["mem"]) if t - g["mem_round"][c] <= self.memory_max_age}
            used_memory = [c for c in active if c not in dirs]
        else:
            active = dirs
        cids = sorted(active)
        if not cids:
            return g, dict(EMPTY_REPORT)
        oldB = {k: v.clone() for k, v in g["B"].items()}
        w = _weights(cids, g["n"], self.weighting)
        if self.memory and self.memory_decay is not None:
            w = {c: w[c] * self.memory_decay ** (t - g["mem_round"][c]) for c in cids}
            tot = sum(w.values())
            w = {c: v / tot for c, v in w.items()}
        tau_eff = sum(w[c] * g["tau"][c] for c in cids) if self.normalize == "nova" else 1.0
        r_max = next(iter(g["B"].values())).shape[1]
        if self.segment_norm:
            colw = {c: torch.zeros(r_max, dtype=torch.float64) for c in cids}
            for j in range(r_max):
                owners = [c for c in cids if g["rank"].get(c, r_max) > j]
                tot = sum(w[c] for c in owners)
                for c in owners:
                    colw[c][j] = w[c] / tot
            coef = {c: (self.server_lr * tau_eff * colw[c]).to(torch.float32) for c in cids}

            def scale(c: str, v: torch.Tensor) -> torch.Tensor:
                return v * coef[c].to(v.device)  # per-column coefficients
        else:
            coef = {c: self.server_lr * tau_eff * w[c] for c in cids}

            def scale(c: str, v: torch.Tensor) -> torch.Tensor:
                return coef[c] * v  # scalar path, bit-identical to the v1 runs
        for k in g["B"]:
            g["B"][k] = g["B"][k] + sum(scale(c, active[c][k]) for c in cids)
        old = {k: (g["A"][k], oldB[k]) for k in g["A"]}
        new = {k: (g["A"][k], g["B"][k]) for k in g["A"]}

        def contrib(c: str, k: str) -> torch.Tensor:
            return scale(c, active[c][k]) @ g["A"][k]

        rep = product_space_report(g["A"], lambda k: (g["B"][k] - oldB[k]) @ g["A"][k], cids, contrib)
        return g, dict(reporters=sorted(dirs), used_memory_for=used_memory, weights=w, **rep)

    def eval_view(self, g: dict) -> LayerState:
        return {k: (g["A"][k], g["B"][k]) for k in g["A"]}


@dataclass
class FlexLoRA:
    """FlexLoRA (Bai et al., arXiv 2402.11505), implemented from its §3 equations (read 2026-10-04):
    clients train both LoRA factors at their own rank r_i; the server forms the full-size weighted average
    W_g = Σ n_i s B_i A_i / Σ n_i, takes SVD(W_g) = U Σ Vᵀ and sends client i  B_i = U[:, :r_i] Σ[:r_i, :r_i] / s,
    A_i = V[:r_i, :]ᵀ. The PEFT scale s = α / r_max is identical for every device here, so we work in B·A units.
    Our choices (not from the paper): round 0 uses the standard LoRA init (B = 0, A random truncated to r_i);
    devices cut off by the deadline are dropped (as in the starter); the evaluated global model is the rank-r_max
    truncation of W_g (our PEFT model holds rank-r_max adapters); its relative truncation error is reported.
    """
    name: str = "flexlora"
    weighting: str = "n"
    train_A: bool = True
    accept_partial: bool = False
    homogeneous_rank: int | None = None

    def rank_for(self, device_rank: int) -> int:
        return self.homogeneous_rank or device_rank

    def init_global(self, init: LayerState) -> dict:
        return {"init": {k: (A.detach().cpu().clone(), B.detach().cpu().clone()) for k, (A, B) in init.items()},
                "W": None, "svd": None, "r_max": next(iter(init.values()))[0].shape[0]}

    def _factor(self, g: dict, k: str, rank: int) -> tuple[torch.Tensor, torch.Tensor]:
        A0, B0 = g["init"][k]
        A, B = torch.zeros_like(A0), torch.zeros_like(B0)
        if g["W"] is None:  # round 0: standard LoRA init
            A[:rank] = A0[:rank]
            return A, B
        U, S, Vh = g["svd"][k]
        r = min(rank, S.shape[0])
        B[:, :r] = U[:, :r] * S[:r]
        A[:r] = Vh[:r]
        return A, B

    def client_view(self, g: dict, rank: int) -> LayerState:
        return {k: self._factor(g, k, rank) for k in g["init"]}

    def payload(self, view: LayerState, after: LayerState, rank: int) -> tuple[dict, int]:
        out = {k: (A[:rank].detach().cpu().contiguous(), B[:, :rank].detach().cpu().contiguous())
               for k, (A, B) in after.items()}
        return out, sum(4 * (a.numel() + b.numel()) for a, b in out.values())

    def aggregate(self, g: dict, payloads: dict[str, dict], metas: dict[str, dict], t: int):
        cids = sorted(payloads)
        if not cids:
            return g, dict(EMPTY_REPORT)
        layers = list(g["init"])
        old = g["W"] or {k: torch.zeros(g["init"][k][1].shape[0], g["init"][k][0].shape[1]) for k in layers}
        w = _weights(cids, {c: metas[c]["n_examples"] for c in cids}, self.weighting)
        prod = {c: {k: payloads[c][k][1] @ payloads[c][k][0] for k in layers} for c in cids}
        new = {k: sum(w[c] * prod[c][k] for c in cids) for k in layers}

        def contrib(c: str, k: str) -> torch.Tensor:
            return w[c] * (prod[c][k] - old[k])

        rep = product_space_report(layers, lambda k: new[k] - old[k], cids, contrib)
        g["W"] = new
        g["svd"] = {k: torch.linalg.svd(new[k], full_matrices=False) for k in layers}
        tail = sum(float((S[g["r_max"]:] ** 2).sum()) for _, S, _ in g["svd"].values())
        tot = sum(float((S ** 2).sum()) for _, S, _ in g["svd"].values())
        rep["truncation_error"] = math.sqrt(tail / tot) if tot > 0 else 0.0
        return g, dict(reporters=cids, used_memory_for=[], weights=w, **rep)

    def eval_view(self, g: dict) -> LayerState:
        return self.client_view(g, g["r_max"])


STRATEGIES: dict[str, Callable[[], object]] = {
    # literal starter baseline: PEFT LoRA r=8 on every device + FedAvg(n_k) over A and B; late devices dropped
    "fedavg_ab_homo": lambda: FedAvgAB(name="fedavg_ab_homo", homogeneous_rank=8),
    # control (code review item 2): the starter, but it also keeps the partial work of deadline-cut devices
    "fedavg_ab_homo_partial": lambda: FedAvgAB(name="fedavg_ab_homo_partial", homogeneous_rank=8,
                                               accept_partial=True),
    # published: FFA-LoRA (ICLR 2024, arXiv 2403.12313) — freeze the random A, FedAvg(n_k) over B, homogeneous r=8
    "ffa_lora": lambda: Anchor(name="ffa_lora", homogeneous_rank=8),
    # published: FlexLoRA (arXiv 2402.11505) — heterogeneous ranks, n_k-weighted product average + SVD split
    "flexlora": lambda: FlexLoRA(name="flexlora"),
    # heterogeneous ranks with HetLoRA-style zero-padding, still naive averaging
    "fedavg_ab_het": lambda: FedAvgAB(name="fedavg_ab_het"),
    # ablation: exact anchor space alone (n_k weights, no normalisation, no memory, late devices dropped)
    "anchor_naive": lambda: Anchor(name="anchor_naive"),
    # spike: exact anchor space + FedNova + macro weights + median clipping + memory + partial work
    "anchor_full": lambda: Anchor(name="anchor_full", normalize="nova", weighting="uniform", clip_kappa=2.0,
                                  memory=True, memory_max_age=4, accept_partial=True),
    # ratchet candidates (results in components/aggregator/autoresearch/results.tsv)
    "anchor_full_tauact": lambda: Anchor(name="anchor_full_tauact", normalize="nova", weighting="uniform",
                                         clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True,
                                         tau_from="actual"),
    "anchor_full_decay": lambda: Anchor(name="anchor_full_decay", normalize="nova", weighting="uniform",
                                        clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True,
                                        memory_decay=0.5),
    "anchor_full_seg": lambda: Anchor(name="anchor_full_seg", normalize="nova", weighting="uniform",
                                      clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True,
                                      segment_norm=True),
    "anchor_full_sqrtn": lambda: Anchor(name="anchor_full_sqrtn", normalize="nova", weighting="sqrt_n",
                                        clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True),
    # attribution ablation (ADR 001 review 09:50): no step normalisation at all
    "anchor_full_nonorm": lambda: Anchor(name="anchor_full_nonorm", normalize="none", weighting="uniform",
                                         clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True),
    # leave-one-mechanism-out ablations (each removes exactly one ingredient of anchor_full)
    "anchor_full_nopartial": lambda: Anchor(name="anchor_full_nopartial", normalize="nova", weighting="uniform",
                                            clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=False),
    "anchor_full_nomem": lambda: Anchor(name="anchor_full_nomem", normalize="nova", weighting="uniform",
                                        clip_kappa=2.0, memory=False, accept_partial=True),
    "anchor_full_noclip": lambda: Anchor(name="anchor_full_noclip", normalize="nova", weighting="uniform",
                                         clip_kappa=None, memory=True, memory_max_age=4, accept_partial=True),
    "anchor_full_nweights": lambda: Anchor(name="anchor_full_nweights", normalize="nova", weighting="n",
                                           clip_kappa=2.0, memory=True, memory_max_age=4, accept_partial=True),
}

BASE_STRATEGIES = ["fedavg_ab_homo", "ffa_lora", "flexlora", "anchor_full"]


def make_strategy(name: str):
    return STRATEGIES[name]()
