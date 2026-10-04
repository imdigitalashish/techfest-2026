"""Tiny C10 Flower parity demo.

Run from project root:
    source .venv/bin/activate
    python -m components.flower_adapter.run_demo
"""
from __future__ import annotations

from flwr.app import Context, RecordDict

from components.device_simulator import DEFAULT_PROFILES
from components.flower_adapter import FlowerLoraStrategy, LocalGrid, make_client_app, make_server_app
from components.orchestrator.simulate import ExperimentConfig, load_world, run_experiment


def run_flower_experiment(cfg: ExperimentConfig, lm, data, log=print):
    """Run the project loop through Flower ClientApp/ServerApp/Strategy objects."""
    strategy = FlowerLoraStrategy(cfg, lm, data, log=log)
    profiles = [p for p in DEFAULT_PROFILES if p.client_id not in cfg.exclude]
    node_by_cid = {p.client_id: idx + 1 for idx, p in enumerate(profiles)}
    strategy.bind_nodes(node_by_cid)

    client_app = make_client_app(lm, strategy.client_blocks)
    apps = {node: client_app for node in node_by_cid.values()}
    contexts = {
        node: Context(
            run_id=1,
            node_id=node,
            node_config={"client_id": cid, "partition-id": cid},
            state=RecordDict(),
            run_config={},
        )
        for cid, node in node_by_cid.items()
    }
    grid = LocalGrid(apps, contexts)
    server_app = make_server_app(strategy)
    server_context = Context(run_id=1, node_id=0, node_config={}, state=RecordDict(), run_config={})
    server_app(grid, server_context)
    return strategy.final_summary(), strategy.rounds_log


def main() -> None:
    cfg = ExperimentConfig(
        strategy="anchor_full",
        scenario="dropout",
        seed=0,
        rounds=2,
        exclude=("c1", "c4"),
        eval_every=2,
        batch_size=1,
    )
    print("Loading local SmolLM2-135M world (local_files_only=True)...")
    lm, data = load_world(cfg)

    flower_summary, _ = run_flower_experiment(cfg, lm, data)
    process_summary, _ = run_experiment(cfg, lm, data, log=lambda msg: print(msg.replace("[", "[process:", 1)))

    f_loss = flower_summary["final_macro_loss"]
    p_loss = process_summary["final_macro_loss"]
    diff = abs(f_loss - p_loss)
    print(f"Flower final macro loss:    {f_loss:.8f}")
    print(f"In-process final macro loss:{p_loss:.8f}")
    print(f"Absolute difference:        {diff:.8g}")
    print("MATCH" if diff < 1e-5 else "DIFF (same logic, but inspect device/order/runtime determinism)")


if __name__ == "__main__":
    main()
