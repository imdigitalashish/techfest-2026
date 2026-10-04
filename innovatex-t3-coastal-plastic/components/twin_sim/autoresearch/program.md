# P2 dispatch ratchet — program

**Goal:** lower `escaped_kg_mean` printed by the FROZEN `eval.py`. It is the mean, over 20 fixed Monte Carlo draws (seed 20261004), of plastic escaping the 4 booms, summed over the tuning monsoons Jun–Sep 2019–2023, under policy P2 at a fixed budget of 2 crews × 8 h/day.

**What the loop may change:** `twin_sim/p2_knobs.json`, plus the P2 logic in `twin_sim/dispatch.py::p2_factory`. Every hypothesis is logged to `results.tsv`. The loop never edits `eval.py`, the twin physics, the parameter ranges, P0 or P1.

**Keep rule:** keep a change only if the metric drops by more than 0.1% (the eval is deterministic with fixed seeds, so this threshold guards against chasing tiny over-fits). Otherwise revert.

**Hold-out discipline:** 2024–2025 are never evaluated in the loop. The held-out result is computed once, after the loop, by `python -m twin_sim.run`.

**Constraints (hard):**
- Equal crew-hours: `eval.py` asserts them.
- Daylight shifts only: starts 06:30–10:30 IST.
- The policy sees only operator-available information: noisy simulated fill sensors, the harmonic tide prediction, and the archived day-ahead JMA GSM rain forecast through `risk_forecaster`, which uses nominal parameters and never a draw's true values.

**Idea backlog (not yet tried):**
- Season-level crew-hour banking: surge crews on forecast storm days and stand them down on dry days. This needs a contract decision because it changes what "equal crew-hours" means.
- Split shifts: two sites per crew when their low-water windows differ. At present all sites share the same tide phase, so the gain is expected to be about zero.
- A learned value function: fitted Q(site, start) on tuning-year rollouts.

Run: `cd innovatex-t3-coastal-plastic/components && python twin_sim/autoresearch/ratchet.py [--round2]`
