"""Flower ClientApp for one simulated LoRA device."""
from __future__ import annotations

from collections.abc import Mapping

import torch
from flwr.app import ConfigRecord, Context, Message, MetricRecord, RecordDict
from flwr.clientapp import ClientApp

from components.aggregator import make_strategy
from components.local_trainer import LoraModel, local_train

from .serialization import payload_to_record, record_to_layer_state


def make_client_app(lm: LoraModel, client_blocks: Mapping[str, torch.Tensor]) -> ClientApp:
    """Create a ClientApp that executes local_train for configured client_id."""
    app = ClientApp()

    @app.train()
    def train(message: Message, context: Context) -> Message:  # noqa: ARG001
        cfg = message.content["config"]
        cid = str(cfg["client_id"])
        rank = int(cfg["rank"])
        steps = int(cfg["allowed_steps"])
        view = record_to_layer_state(message.content["arrays"], message.content["array_schema"])

        lm.set_state(view)
        loss, wall = local_train(
            lm,
            client_blocks[cid],
            rank=rank,
            steps=steps,
            batch_size=int(cfg["batch_size"]),
            lr=float(cfg["lr"]),
            train_A=bool(cfg["train_A"]),
            seed=int(cfg["seed"]),
        )
        strat = make_strategy(str(cfg["strategy"]))
        payload, upload_bytes = strat.payload(view, lm.get_state(), rank)
        payload_arrays, payload_schema = payload_to_record(payload)
        status = "partial" if steps < int(cfg["planned_steps"]) else "ok"
        content = RecordDict(
            {
                "payload": payload_arrays,
                "payload_schema": payload_schema,
                "meta": ConfigRecord(
                    {
                        "client_id": cid,
                        "status": status,
                        "rank": rank,
                        "planned_steps": int(cfg["planned_steps"]),
                        "steps_done": steps,
                        "n_examples": int(cfg["n_examples"]),
                        "train_loss": float(loss),
                        "upload_bytes": int(upload_bytes),
                        "wall_s": float(wall),
                    }
                ),
                "metrics": MetricRecord({"num-examples": int(cfg["n_examples"]), "train-loss": float(loss)}),
            }
        )
        return Message(content, reply_to=message)

    return app
