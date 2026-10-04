# P7 — Shock-aware look-ahead allocator (Perceptron 2026, Problem 7)

Journal and current state: [thought_node.md](thought_node.md) · approach: [deliverables/architecture.md](deliverables/architecture.md) · abstract: [deliverables/round1-abstract.md](deliverables/round1-abstract.md) · components: [architecture/components.md](architecture/components.md) · spike decision: [architecture/adr/001-spike.md](architecture/adr/001-spike.md) · research: [research/landscape.md](research/landscape.md)

## Run it (from this folder)
```bash
uv venv .venv --python 3.11 --system-site-packages && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pytest -q tests                                   # 6 contract tests
.venv/bin/python -m eval.harness --scenarios shock shock+drift --seeds 100-109 --horizon 1440 --out eval/results/mvp-v1
.venv/bin/python -m eval.stats eval/results/mvp-v1                    # writes summary.md (CIs, paired tests)
.venv/bin/python -m components.forecasting.autoresearch.eval          # frozen C4+C5 metric (ratchet)
```

## Layout
- `architecture/contracts/contracts.py` — typed contracts (FleetState, StepInfo, DemandTrace, Forecast, Plan, Policy).
- `components/scenarios` — the demand generator (synthetic, labelled shocks/drift/spikes).
- `components/simulator` — the numpy core and PettingZoo `ParallelEnv`.
- `components/detection` — the Poisson CUSUM.
- `components/forecasting` — forecasters, plus `autoresearch/` (program.md, frozen eval.py, results.tsv).
- `components/planner` — the MPC LP.
- `components/coordinator` — flows → per-unit orders.
- `components/policies` — static / greedy / reactive / mpc-ewma / mpc-cusum / mpc-cusum-v1 / oracle.
- `eval/` — the harness, the stats module and committed result folders.

Seeds 0–99 are for development and tuning; seeds 100+ are frozen test seeds. All demand is **synthetic** unless a folder says otherwise.
