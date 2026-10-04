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

Strategies work on plain dicts of tensors (no model), so they are unit-testable on random tensors.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import torch

LayerState = dict[str, tuple[torch.Tensor, torch.Tensor]]


def product_space_report(old: LayerState, new: LayerState, cids: list[str],
                         contrib: Callable[[str, str], torch.Tensor]) -> tuple[dict[str, float], float, float]:
    """Influence shares in ΔW space, computed layer by layer.

    P = ΔW_new − ΔW_old is the global update actually applied; c_k = contrib(k, layer) is what the
    strategy meant to add for device k. Returns ({k: <c_k, P> / ||P||²}, ||P − Σ_k c_k|| / ||Σ_k c_k||, ||P||).
    """
    dots = {c: 0.0 for c in cids}
    pp = err = cc = 0.0
    for name, (A0, B0) in old.items():
        A1, B1 = new[name]
        P = B1 @ A1 - B0 @ A0
        S = torch.zeros_like(P)
        dvec = []
        for c in cids:
            C = contrib(c, name)
            dvec.append((C * P).sum())
            S += C
        vals = torch.stack([(P * P).sum(), ((P - S) ** 2).sum(), (S * S).sum()] + dvec).tolist()
        pp, err, cc = pp + vals[0], err + vals[1], cc + vals[2]
        for c, v in zip(cids, vals[3:]):
            dots[c] += v
    shares = {c: (d / pp if pp > 0 else 0.0) for c, d in dots.items()}
    rel = math.sqrt(err) / math.sqrt(cc) if cc > 0 else 0.0
    return shares, rel, math.sqrt(pp)


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
        nbytes = sum(4 * rank * (A.shape[1] + B.shape[0]) for A, B in after.values())
        return {k: (A.clone(), B.clone()) for k, (A, B) in after.items()}, nbytes

    def aggregate(self, g: dict, payloads: dict[str, dict], metas: dict[str, dict], t: int):
        cids = sorted(payloads)
        old = g["layers"]
        if not cids:
            return g, dict(reporters=[], used_memory_for=[], weights={}, influence_share={},
                           aggregation_error=0.0, update_norm=0.0)
        w = _weights(cids, {c: metas[c]["n_examples"] for c in cids}, self.weighting)
        new = {}
        for k in old:
            new[k] = (sum(w[c] * payloads[c][k][0] for c in cids), sum(w[c] * payloads[c][k][1] for c in cids))

        def contrib(c: str, k: str) -> torch.Tensor:
            A_c, B_c = payloads[c][k]
            return w[c] * (B_c @ A_c - old[k][1] @ old[k][0])

        shares, err, norm = product_space_report(old, new, cids, contrib)
        return {"layers": new}, dict(reporters=cids, used_memory_for=[], weights=w, influence_share=shares,
                                     aggregation_error=err, update_norm=norm)

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
                out[k] = v
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
            return g, dict(reporters=[], used_memory_for=[], weights={}, influence_share={},
                           aggregation_error=0.0, update_norm=0.0)
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

        shares, err, norm = product_space_report(old, new, cids, contrib)
        return g, dict(reporters=sorted(dirs), used_memory_for=used_memory, weights=w, influence_share=shares,
                       aggregation_error=err, update_norm=norm)

    def eval_view(self, g: dict) -> LayerState:
        return {k: (g["A"][k], g["B"][k]) for k in g["A"]}


STRATEGIES: dict[str, Callable[[], object]] = {
    # literal starter baseline: PEFT LoRA r=8 on every device + FedAvg(n_k) over A and B; late devices dropped
    "fedavg_ab_homo": lambda: FedAvgAB(name="fedavg_ab_homo", homogeneous_rank=8),
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
}

BASE_STRATEGIES = ["fedavg_ab_homo", "fedavg_ab_het", "anchor_naive", "anchor_full"]


def make_strategy(name: str):
    return STRATEGIES[name]()
