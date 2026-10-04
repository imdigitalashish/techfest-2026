"""C7 Round orchestrator: an in-process federated simulation (synchronous rounds with a deadline).

One base model is shared by all simulated devices (only LoRA tensors differ), so a 5-device run fits
easily on a 24 GB M5. The Flower adapter (components/flower_adapter) wraps the same strategy objects
for multi-process demos.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

import torch

from components.aggregator import make_strategy
from components.contracts import AggregationReport, ClientUpdate, EvalReport, RunSummary
from components.data_partitioner import DOMAINS, build_domain_blocks
from components.device_simulator import DEFAULT_PROFILES, WEAK_CLIENTS, availability_schedule
from components.local_trainer import build_lora_model, evaluate, local_train, reset_lora


@dataclass
class ExperimentConfig:
    strategy: str = "fedavg_ab_het"
    scenario: str = "clean"
    seed: int = 0
    rounds: int = 12
    model_id: str = "HuggingFaceTB/SmolLM2-135M"
    model_tag: str = "smollm2-135m"
    targets: tuple[str, ...] = ("q_proj", "v_proj")
    r_max: int = 16
    alpha: float = 32.0
    batch_size: int = 4
    lr: float = 1e-3
    seq_len: int = 128
    eval_every: int = 3
    exclude: tuple[str, ...] = ()
    strategy_overrides: dict = field(default_factory=dict)


def _fmt_err(v) -> str:
    return "n/a" if v is None else f"{v:.3f}"


def load_world(cfg: ExperimentConfig):
    """Load the shared base model and every domain's token blocks once."""
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(cfg.model_id, local_files_only=True)
    data = {d: build_domain_blocks(tok, d, seq_len=cfg.seq_len, model_tag=cfg.model_tag) for d in DOMAINS}
    lm = build_lora_model(cfg.model_id, cfg.r_max, cfg.alpha, list(cfg.targets))
    return lm, data


def run_experiment(cfg: ExperimentConfig, lm, data, log=print) -> tuple[dict, list[dict]]:
    t_start = time.time()
    strat = make_strategy(cfg.strategy)
    for k, v in cfg.strategy_overrides.items():
        setattr(strat, k, v)
    profiles = [p for p in DEFAULT_PROFILES if p.client_id not in cfg.exclude]
    eval_blocks = {d: data[d][1] for d in DOMAINS}
    client_blocks = {p.client_id: data[p.domain][0][: p.n_train_blocks] for p in profiles}

    init = reset_lora(lm, cfg.seed)
    g = strat.init_global(init)
    sched = availability_schedule(profiles, cfg.rounds, cfg.seed, cfg.scenario)
    torch.manual_seed(cfg.seed)

    lm.set_state(strat.eval_view(g))
    base = evaluate(lm, eval_blocks)
    evals = [EvalReport(round=0, per_domain_loss=base, macro_loss=sum(base.values()) / len(base),
                        worst_loss=max(base.values()), worst_domain=max(base, key=base.get)).model_dump()]
    rounds_log, upload = [], {p.client_id: 0 for p in profiles}

    for t in range(cfg.rounds):
        payloads, metas, updates = {}, {}, []
        for p in profiles:
            cid, planned = p.client_id, p.local_steps
            allowed = sched[(t, cid)]
            rank = strat.rank_for(p.rank)
            status = "ok"
            if allowed == 0:
                status = "offline"
            elif allowed < planned and not strat.accept_partial:
                status = "late_discarded"
            if status != "ok":
                updates.append(ClientUpdate(round=t, client_id=cid, rank=rank, planned_steps=planned, steps_done=0,
                                            n_examples=p.n_train_blocks, train_loss=float("nan"), upload_bytes=0,
                                            wall_s=0.0, status=status).model_dump())
                continue
            steps = allowed
            view = strat.client_view(g, rank)
            lm.set_state(view)
            loss, wall = local_train(lm, client_blocks[cid], rank, steps, cfg.batch_size, cfg.lr,
                                     strat.train_A, seed=cfg.seed * 1_000_003 + t * 101 + int(cid[1:]))
            payload, nbytes = strat.payload(view, lm.get_state(), rank)
            payloads[cid] = payload
            metas[cid] = dict(n_examples=p.n_train_blocks, planned_steps=planned, steps_done=steps)
            upload[cid] += nbytes
            updates.append(ClientUpdate(round=t, client_id=cid, rank=rank, planned_steps=planned, steps_done=steps,
                                        n_examples=p.n_train_blocks, train_loss=loss, upload_bytes=nbytes,
                                        wall_s=wall, status="partial" if steps < planned else "ok").model_dump())
        g, rep = strat.aggregate(g, payloads, metas, t)
        agg = AggregationReport(round=t, strategy=cfg.strategy, **rep).model_dump()
        entry = {"round": t + 1, "updates": updates, "aggregation": agg}
        if (t + 1) % cfg.eval_every == 0 or t == cfg.rounds - 1:
            lm.set_state(strat.eval_view(g))
            ev = evaluate(lm, eval_blocks)
            er = EvalReport(round=t + 1, per_domain_loss=ev, macro_loss=sum(ev.values()) / len(ev),
                            worst_loss=max(ev.values()), worst_domain=max(ev, key=ev.get)).model_dump()
            evals.append(er)
            entry["eval"] = er
            log(f"[{cfg.strategy}|{cfg.scenario}|s{cfg.seed}] r{t + 1:02d} macro={er['macro_loss']:.4f} "
                f"worst={er['worst_loss']:.4f} share_c0={agg['influence_share'].get('c0', float('nan')):.2f} "
                f"err={_fmt_err(agg['aggregation_error'])} reporters={','.join(agg['reporters'])}")
        rounds_log.append(entry)

    final = evals[-1]["per_domain_loss"]
    macros = [e["macro_loss"] for e in evals]
    shares = [r["aggregation"]["influence_share"] for r in rounds_log if r["aggregation"]["influence_share"]]
    nshares = [r["aggregation"]["norm_share"] for r in rounds_log if r["aggregation"]["norm_share"]]
    truncs = [r["aggregation"]["truncation_error"] for r in rounds_log
              if r["aggregation"].get("truncation_error") is not None]
    weak_domains = [p.domain for p in DEFAULT_PROFILES if p.client_id in WEAK_CLIENTS]
    summary = RunSummary(
        strategy=cfg.strategy, scenario=cfg.scenario, seed=cfg.seed, rounds=cfg.rounds,
        base_macro_loss=evals[0]["macro_loss"], final_macro_loss=evals[-1]["macro_loss"],
        final_worst_loss=evals[-1]["worst_loss"],
        final_min_rel_gain=min((base[d] - final[d]) / base[d] for d in final),
        final_per_domain_loss=final,
        mean_macro_loss=sum(macros[1:]) / max(1, len(macros) - 1),
        max_spike=max([0.0] + [b - a for a, b in zip(macros, macros[1:])]),
        dominance_c0=sum(s.get("c0", 0.0) for s in shares) / max(1, len(shares)),
        dominance_max=sum(max(s.values()) for s in shares) / max(1, len(shares)),
        dominance_c0_norm=sum(s.get("c0", 0.0) for s in nshares) / max(1, len(nshares)),
        weak_gain=sum(base[d] - final[d] for d in weak_domains) / len(weak_domains),
        aggregation_error=(lambda v: sum(v) / len(v) if v else 0.0)(
            [r["aggregation"]["aggregation_error"] for r in rounds_log if r["aggregation"]["aggregation_error"] is not None]),
        truncation_error=(sum(truncs) / len(truncs)) if truncs else None,
        upload_mb={c: b / 1e6 for c, b in upload.items()},
        wall_s=time.time() - t_start,
    ).model_dump()
    summary["config"] = asdict(cfg)
    return summary, rounds_log
