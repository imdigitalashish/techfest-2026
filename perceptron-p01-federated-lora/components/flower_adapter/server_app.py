"""Flower ServerApp strategy wrapper for the project aggregation strategies."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

import torch
from flwr.app import ArrayRecord, ConfigRecord, Context, Message, MetricRecord, RecordDict
from flwr.app.message_type import MessageType
from flwr.serverapp import ServerApp
from flwr.serverapp.grid import Grid
from flwr.serverapp.strategy import Result, Strategy

from components.aggregator import make_strategy
from components.contracts import AggregationReport, ClientUpdate, EvalReport
from components.data_partitioner import DOMAINS
from components.device_simulator import DEFAULT_PROFILES, availability_schedule
from components.local_trainer import LoraModel, evaluate, reset_lora
from components.orchestrator.simulate import ExperimentConfig

from .serialization import layer_state_to_record, record_to_payload


class FlowerLoraStrategy(Strategy):
    """Message-API Strategy that delegates aggregation to C6 strategy objects."""

    def __init__(self, cfg: ExperimentConfig, lm: LoraModel, data: dict[str, tuple[torch.Tensor, torch.Tensor]], log=print) -> None:
        self.cfg = cfg
        self.lm = lm
        self.data = data
        self.log = log
        self.inner = make_strategy(cfg.strategy)
        for key, value in cfg.strategy_overrides.items():
            setattr(self.inner, key, value)
        self.profiles = [p for p in DEFAULT_PROFILES if p.client_id not in cfg.exclude]
        self.profile_by_cid = {p.client_id: p for p in self.profiles}
        self.node_by_cid: dict[str, int] = {}
        self.cid_by_node: dict[int, str] = {}
        self.sched = availability_schedule(self.profiles, cfg.rounds, cfg.seed, cfg.scenario)
        self.client_blocks = {p.client_id: data[p.domain][0][: p.n_train_blocks] for p in self.profiles}
        self.eval_blocks = {d: data[d][1] for d in DOMAINS}
        init = reset_lora(lm, cfg.seed)
        self.g = self.inner.init_global(init)
        self.rounds_log: list[dict[str, Any]] = []
        self.evals: list[dict[str, Any]] = []
        self.upload = {p.client_id: 0 for p in self.profiles}

    def initial_arrays(self) -> ArrayRecord:
        arrays, _ = layer_state_to_record(self.inner.eval_view(self.g))
        return arrays

    def _schema(self) -> ConfigRecord:
        _, schema = layer_state_to_record(self.inner.eval_view(self.g))
        return schema

    def bind_nodes(self, node_by_cid: dict[str, int]) -> None:
        self.node_by_cid = dict(node_by_cid)
        self.cid_by_node = {node: cid for cid, node in node_by_cid.items()}

    def configure_train(self, server_round: int, arrays: ArrayRecord, config: ConfigRecord, grid: Grid):  # noqa: ARG002
        t = server_round - 1
        messages = []
        for p in self.profiles:
            cid = p.client_id
            allowed = self.sched[(t, cid)]
            if allowed == 0:
                continue
            if allowed < p.local_steps and not self.inner.accept_partial:
                continue
            rank = self.inner.rank_for(p.rank)
            view = self.inner.client_view(self.g, rank)
            view_arrays, view_schema = layer_state_to_record(view)
            task_cfg = ConfigRecord(
                {
                    "round": t,
                    "client_id": cid,
                    "rank": rank,
                    "planned_steps": p.local_steps,
                    "allowed_steps": allowed,
                    "batch_size": self.cfg.batch_size,
                    "lr": self.cfg.lr,
                    "train_A": bool(self.inner.train_A),
                    "seed": self.cfg.seed * 1_000_003 + t * 101 + int(cid[1:]),
                    "strategy": self.cfg.strategy,
                    "n_examples": p.n_train_blocks,
                }
            )
            record = RecordDict({"arrays": view_arrays, "array_schema": view_schema, "config": task_cfg})
            node_id = self.node_by_cid.get(cid)
            if node_id is None:
                continue
            messages.append(grid.create_message(record, MessageType.TRAIN, node_id, group_id=str(server_round)))
        return messages

    def aggregate_train(self, server_round: int, replies):
        t = server_round - 1
        payloads, metas = {}, {}
        updates = []
        seen = set()
        for reply in replies:
            if reply.has_error():
                continue
            meta = reply.content["meta"]
            cid = str(meta["client_id"])
            seen.add(cid)
            payloads[cid] = record_to_payload(reply.content["payload"], reply.content["payload_schema"])
            metas[cid] = {
                "n_examples": int(meta["n_examples"]),
                "planned_steps": int(meta["planned_steps"]),
                "steps_done": int(meta["steps_done"]),
            }
            self.upload[cid] += int(meta["upload_bytes"])
            updates.append(
                ClientUpdate(
                    round=t,
                    client_id=cid,
                    rank=int(meta["rank"]),
                    planned_steps=int(meta["planned_steps"]),
                    steps_done=int(meta["steps_done"]),
                    n_examples=int(meta["n_examples"]),
                    train_loss=float(meta["train_loss"]),
                    upload_bytes=int(meta["upload_bytes"]),
                    wall_s=float(meta["wall_s"]),
                    status=str(meta["status"]),
                ).model_dump()
            )
        for p in self.profiles:
            if p.client_id in seen:
                continue
            allowed = self.sched[(t, p.client_id)]
            status = "offline" if allowed == 0 else "late_discarded"
            updates.append(
                ClientUpdate(
                    round=t,
                    client_id=p.client_id,
                    rank=self.inner.rank_for(p.rank),
                    planned_steps=p.local_steps,
                    steps_done=0,
                    n_examples=p.n_train_blocks,
                    train_loss=float("nan"),
                    upload_bytes=0,
                    wall_s=0.0,
                    status=status,
                ).model_dump()
            )
        self.g, rep = self.inner.aggregate(self.g, payloads, metas, t)
        agg = AggregationReport(round=t, strategy=self.cfg.strategy, **rep).model_dump()
        self.rounds_log.append({"round": server_round, "updates": sorted(updates, key=lambda u: u["client_id"]), "aggregation": agg})
        arrays, _ = layer_state_to_record(self.inner.eval_view(self.g))
        metrics = MetricRecord(
            {
                "aggregation-error": float("nan") if agg["aggregation_error"] is None else float(agg["aggregation_error"]),
                "update-norm": float(agg["update_norm"]),
                "num-reporters": len(agg["reporters"]),
            }
        )
        return arrays, metrics

    def configure_evaluate(self, server_round: int, arrays: ArrayRecord, config: ConfigRecord, grid: Grid):  # noqa: ARG002
        return []

    def aggregate_evaluate(self, server_round: int, replies):  # noqa: ARG002
        return None

    def evaluate_global(self, server_round: int, arrays: ArrayRecord | None = None) -> MetricRecord | None:  # noqa: ARG002
        if server_round != 0 and server_round % self.cfg.eval_every != 0 and server_round != self.cfg.rounds:
            return None
        self.lm.set_state(self.inner.eval_view(self.g))
        losses = evaluate(self.lm, self.eval_blocks)
        report = EvalReport(
            round=server_round,
            per_domain_loss=losses,
            macro_loss=sum(losses.values()) / len(losses),
            worst_loss=max(losses.values()),
            worst_domain=max(losses, key=losses.get),
        ).model_dump()
        self.evals.append(report)
        if server_round:
            agg = self.rounds_log[-1]["aggregation"]
            self.rounds_log[-1]["eval"] = report
            self.log(
                f"[flower:{self.cfg.strategy}|{self.cfg.scenario}|s{self.cfg.seed}] r{server_round:02d} "
                f"macro={report['macro_loss']:.4f} worst={report['worst_loss']:.4f} "
                f"share_c0={agg['influence_share'].get('c0', float('nan')):.2f} "
                f"err={'n/a' if agg['aggregation_error'] is None else format(agg['aggregation_error'], '.3f')} reporters={','.join(agg['reporters'])}"
            )
        return MetricRecord({"macro-loss": float(report["macro_loss"]), "worst-loss": float(report["worst_loss"])})

    def summary(self) -> None:
        self.log(f"FlowerLoraStrategy({self.cfg.strategy}, rounds={self.cfg.rounds}, profiles={[p.client_id for p in self.profiles]})")

    def final_summary(self) -> dict[str, Any]:
        final = self.evals[-1]
        base = self.evals[0]
        return {
            "strategy": self.cfg.strategy,
            "scenario": self.cfg.scenario,
            "seed": self.cfg.seed,
            "rounds": self.cfg.rounds,
            "base_macro_loss": base["macro_loss"],
            "final_macro_loss": final["macro_loss"],
            "final_worst_loss": final["worst_loss"],
            "final_per_domain_loss": final["per_domain_loss"],
            "upload_mb": {c: b / 1e6 for c, b in self.upload.items()},
            "config": asdict(self.cfg),
        }


def make_server_app(strategy: FlowerLoraStrategy, timeout: float = 3600.0) -> ServerApp:
    """Create a ServerApp whose main executes the C10 strategy wrapper."""
    app = ServerApp()

    @app.main()
    def main(grid: Grid, context: Context) -> None:  # noqa: ARG001
        strategy.start(
            grid=grid,
            initial_arrays=strategy.initial_arrays(),
            num_rounds=strategy.cfg.rounds,
            timeout=timeout,
            train_config=ConfigRecord(),
            evaluate_fn=strategy.evaluate_global,
        )

    return app
