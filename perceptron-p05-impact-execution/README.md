# P5 · Market-impact-aware execution (Perceptron 2026)

Start with the journal: [`thought_node.md`](thought_node.md). Morning-package documents:

- [`research/landscape.md`](research/landscape.md)
- [`architecture/components.md`](architecture/components.md)
- [`architecture/adr/001-spike.md`](architecture/adr/001-spike.md)
- [`deliverables/round1-abstract.md`](deliverables/round1-abstract.md)

## Reproduce
```bash
cd perceptron-p05-impact-execution
scripts/fetch_abides.sh                                   # ABIDES @ f9cbe51 into .cache/ (gitignored)
python3.11 -m venv --system-site-packages .venv           # needs numpy, pandas, scipy, pydantic, pytest
.venv/bin/python -m pytest -q tests                       # contracts + TCA identity + policies
# calibration on train seeds, then held-out test (naive twins), then synchronised twins
.venv/bin/python eval/run_experiment.py --exp E1_calib_train --seeds 0:40 --qty 4000 --policies eval/policies/calib.json --workers 8
.venv/bin/python eval/calibrate.py --exp E1_calib_train
.venv/bin/python eval/run_experiment.py --exp E3_test --seeds 1000:1060 --qty 4000 --policies eval/policies/test.json --workers 9
.venv/bin/python eval/summarize.py --exp E3_test
.venv/bin/python eval/run_experiment.py --exp E4_nsr_sync --seeds 100:130 --qty 4000 --policies eval/policies/twap_only.json --rng-sync per_wakeup
.venv/bin/python eval/nsr.py E4_nsr_naive E4_nsr_sync
```
`eval/policies/test.json` is generated from `eval/results/calibration.json` by `eval/make_test_policies.py`.

## Layout
- `components/sim_env`: ABIDES adapter, pomegranate shim, world builder, twins, RNG synchronisation.
- `components/execution_agent`: the ABIDES agent and pure policies (TWAP, VWAP, PROBE, IA), plus `autoresearch/` (frozen eval, program, ledger).
- `components/tca`: implementation shortfall and the exact twin decomposition.
- `components/impact_model`: propagator fit and prediction.
- `eval/`: runner, calibration, summariser, NSR. Results go to `eval/results/`; raw per-seed pickles go to `.data/` (gitignored).
