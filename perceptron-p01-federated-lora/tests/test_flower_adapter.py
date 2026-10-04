from __future__ import annotations

import torch
from flwr.app import ConfigRecord, Message, RecordDict
from flwr.supercore.task_identity import TaskIdentity

from components.aggregator import Anchor
from components.flower_adapter.serialization import (
    layer_state_to_record,
    payload_to_record,
    record_to_layer_state,
    record_to_payload,
)
from components.flower_adapter.server_app import FlowerLoraStrategy
from components.orchestrator.simulate import ExperimentConfig


def test_layer_state_round_trips_through_arrayrecord() -> None:
    state = {
        "layer.z": (torch.randn(2, 3), torch.randn(4, 2)),
        "layer.a": (torch.randn(2, 5), torch.randn(6, 2)),
    }
    arrays, schema = layer_state_to_record(state)
    out = record_to_layer_state(arrays, schema)
    assert set(out) == set(state)
    for name in state:
        assert torch.equal(out[name][0], state[name][0])
        assert torch.equal(out[name][1], state[name][1])


def test_anchor_payload_round_trips_through_arrayrecord() -> None:
    payload = {"layer": torch.randn(4, 2)}
    arrays, schema = payload_to_record(payload)
    out = record_to_payload(arrays, schema)
    assert torch.equal(out["layer"], payload["layer"])


def test_server_wrapper_aggregates_fake_anchor_payloads() -> None:
    init = {"layer": (torch.ones(2, 3), torch.zeros(4, 2))}
    anchor = Anchor(name="anchor_full", weighting="uniform", train_A=False, accept_partial=True)

    strategy = FlowerLoraStrategy.__new__(FlowerLoraStrategy)
    strategy.cfg = ExperimentConfig(strategy="anchor_full", rounds=1, exclude=("c1", "c4"))
    strategy.inner = anchor
    strategy.g = anchor.init_global(init)
    strategy.profiles = []
    strategy.rounds_log = []
    strategy.upload = {"c0": 0, "c2": 0}

    TaskIdentity.run_id = 1
    TaskIdentity.node_id = 0
    TaskIdentity.task_id = 0

    replies = []
    for cid, delta in {"c0": torch.ones(4, 2), "c2": 3 * torch.ones(4, 2)}.items():
        arrays, schema = payload_to_record({"layer": delta})
        content = RecordDict(
            {
                "payload": arrays,
                "payload_schema": schema,
                "meta": ConfigRecord(
                    {
                        "client_id": cid,
                        "status": "ok",
                        "rank": 2,
                        "planned_steps": 1,
                        "steps_done": 1,
                        "n_examples": 10,
                        "train_loss": 0.0,
                        "upload_bytes": 32,
                        "wall_s": 0.0,
                    }
                ),
            }
        )
        request = Message(RecordDict(), dst_node_id=1, message_type="train")
        replies.append(Message(content, reply_to=request))

    arrays, metrics = strategy.aggregate_train(1, replies)
    out = record_to_layer_state(arrays)

    assert metrics is not None
    assert metrics["num-reporters"] == 2
    assert torch.allclose(strategy.g["B"]["layer"], 2 * torch.ones(4, 2))
    assert torch.allclose(out["layer"][1], 2 * torch.ones(4, 2))
