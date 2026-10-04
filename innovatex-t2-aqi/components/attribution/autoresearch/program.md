# Autoresearch program — C6 attribution (spike, ADR 001)

**Goal:** estimate a construction site's own PM10 increment at its fence line, every hour, from a 4-node ring + wind vane.
**Metric (lower is better):** `python eval.py` prints `DEV scalar` = MAE (µg/m³) over all dev hours (Feb–Dec 2025), with abstentions scored as 0. The lead re-checks the `TEST scalar` (Jan–Sep 2026) and secondary metrics (coverage, CSI > 50) on every kept change.
**Data:** REAL background PM10 (CPCB/DPCC monitor 6929 via the OpenAQ archive) + REAL ERA5 wind/RH; SIMULATED site, plume and sensors (see `eval.py` docstring). The numbers say how methods *rank* under realistic Delhi backgrounds and winds, not field accuracy.
**Rules:** edit only `../methods.py`; `eval.py` is frozen (any change starts a new ledger version); methods must be causal (hour t uses rows ≤ t); keep a change only if DEV improves by more than noise (≥ 1 µg/m³ until multi-seed is in place) and TEST doesn't get worse; log every attempt in `results.tsv` (kept or not).

## Status
- Evaluator v1 (5 seeds) is live. Independent review (ADR 001, 08:35) found that v1 favours self-calibration; **no further keep/revert decisions until evaluator v2** (lead-only): new sensor model with separate dust gains + a co-calibrated baseline; contaminated quiet hours and spatial gradients; 15-min winds, vane decorrelation, varied geometry; a hidden holdout that only the lead runs (TEST no longer printed to the loop).

## Idea backlog (ordered)
1. ~~Multi-seed evaluator v1~~ (done 08:03).
2. Use all non-downwind nodes (median) as the background instead of the single up-most node.
3. Weight the increment by wind-direction confidence (vane variance over the hour), and abstain when it's high.
4. Calm-wind pooling: estimate the site's pooled excess against a night-time background model rather than the ring minimum.
5. Self-calibration with slope + offset (robust regression on idle hours) instead of ratio-to-median; RH-dependent term.
6. Detect and reject tamper events (one node falls below the ring + RH jump) before differencing.
7. A probabilistic output: P(increment > threshold) from the bootstrap over nodes and hours (feeds C8).
