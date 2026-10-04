# Autoresearch program — C5 recharge-verifier

- **Goal:** minimise `event_mdape` (median absolute % error of infiltrated volume per storm event) printed by the FROZEN `eval.py --split dev`, without degrading the secondary metrics (fake_recall ↑, false_implausible_rate ↓, clogging F1, coverage ≥ 0.95, season_total_abs_pct_err ↓).
- **Editable:** `components/recharge_verifier/verifier.py` only. Contract: output dicts must stay shaped like `RechargeEvent` (architecture/contracts/gwcontracts.py).
- **Frozen:** `eval.py`, `components/twin_simulator/simulate.py`, the splits, the seeds, and the registry-noise model.
- **Keep rule:** keep a change only if dev `event_mdape` improves by > 0.5 points AND no secondary metric regresses by more than 10 % relative; then confirm on `--split holdout` (monsoon 2024) before pushing. Every run is logged in `results.tsv`.
- **Honesty:** pits are SIMULATED (rain is real ERA5). Report every number as simulation. Physical-rig numbers replace these in November.

## Idea backlog (ordered)
1. Fake detection: require the rise to be co-located in time with rain (rain in the 30 min before the rise onset), not just over the whole padded window. Expected: fake_recall ↑, false_implausible_rate ↓.
2. The implausibility threshold uses rain × catchment × 0.75; learn a per-structure runoff coefficient from its first N verified events (median ratio).
3. k estimation: pool recession segments across the last 3 events (robust median), weight by segment length; fit the exponential with a noise floor (h > 5σ).
4. Overflow handling: when the stage sits at the spill level, infiltration = k·A·H_max (exact) — already in the integral; check the inflow estimate, not the infiltration.
5. Event splitting: split multi-storm windows at local minima so per-event k is not mixed.
6. Season total error is large (61 %): check whether long low-stage tails (noise near 0) inflate ∫h dt. Subtract the noise floor (h < 2σ → 0).
