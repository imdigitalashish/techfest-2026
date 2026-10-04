# Auto-research program: C6 aggregator (AnchorLoRA)

Adapted from karpathy/autoresearch (PLAYBOOK §5): edit the aggregator, run the frozen evaluator, keep the change only if the metric improves beyond noise, revert otherwise, and log every attempt in `results.tsv`.

## Goal
Lower the **macro held-out loss** (nats/token, mean over 5 domains) after 12 rounds of the fixed **dropout** scenario, without hurting the worst domain or breaking exactness.

## Metric (printed by `eval.py`, which is FROZEN: never edit it in the loop)
- Primary scalar: `final_macro_loss`, mean over the seeds in `eval.py` (currently seeds 0 and 1). Lower is better.
- Guards (a change is rejected if any fails): `aggregation_error` < 1e-4 · `final_worst_loss` not worse than the current best by > 0.01 · contract tests pass (`pytest -q tests/`).
- Noise: with 2 seeds the seed-to-seed spread is to be measured from the first replicated runs. Until then a change must beat the best by ≥ 0.005 nats **on both seeds**. Every 5 kept changes, re-check on fresh seeds 7 and 8 (holdout) to catch metric gaming.

## Constraints
- Only `components/aggregator/strategies.py` changes (and only the `Anchor` class or new strategies registered in `STRATEGIES`). Data, devices, trainer, evaluator and `eval.py` are frozen.
- The device schedule is seeded, so every candidate sees identical dropouts (paired comparison).
- Budget: one evaluation ≈ 9–15 min on the shared M5 tonight. Move to an Azure GPU for ≥ 50-round, ≥ 5-seed confirmations.

## Idea backlog (from ADR 001 synthesis; highest value first)
1. τ_eff from **actual** steps (true FedNova) vs **planned** steps (current) vs no rescale.
2. Decayed memory: weight × γ^age (γ ∈ {0.5, 0.8}) vs hard max-age 4 vs no memory.
3. Server optimiser on the aggregated ΔB: server lr ∈ {0.5, 1.5}, FedAvgM momentum 0.9 (FedOpt family).
4. Weights: uniform vs √n vs q-FFL-style loss-aware (needs per-device train loss, already in `ClientUpdate`).
5. Clipping: κ ∈ {1.5, 3, ∞}, ΔW-space vs B-space, running median.
6. Rotating rank masks (device k trains a rotating window of B columns) vs prefix ranks.
7. Anchor refresh: every k rounds merge ΔW into the base and redraw A from seed + k.
8. Online influence cap: water-fill weights so no device exceeds 1/K + ε share.

## How to run one iteration
```bash
cd perceptron-p01-federated-lora && source .venv/bin/activate
python -m components.aggregator.autoresearch.eval --strategy anchor_full      # prints METRIC <float>
# compare with the best row in results.tsv; keep (commit) or revert; append a row either way
```
