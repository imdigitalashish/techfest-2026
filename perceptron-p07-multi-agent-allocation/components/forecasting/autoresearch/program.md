# Auto-research program — C4+C5 spike (change detector + forecaster)

**Goal:** minimise the forecast error of the demand belief that the MPC plans on, both overall and right after an abrupt shock, without false alarms on transient spikes.

**Metric (frozen, `eval.py`, lower is better):** `score = MAE_all + MAE_post_shock`.
- Scenario `shock+drift+spikes`: 1-day horizon, gamma-Poisson over-dispersion 0.2, 24 transient spikes.
- **Dev seeds 0–19 only.**
- H = 6-step forecasts compared with the *true* rates.

Secondary metrics are printed but not optimised: false alarms per zone-day outside labelled change windows; detection delay.

**Ratchet rules:**
1. Edit only `candidate.py` (keep each trial as `candidate_vN.py`).
2. Run `python -m components.forecasting.autoresearch.eval components.forecasting.autoresearch.candidate_vN:make` from the project root.
3. Append a row to `results.tsv`.
4. Keep a trial only if the score improves by > 0.005 (roughly the seed-to-seed noise of the mean; *to be measured properly*). Otherwise revert.
5. Every 5 kept changes, the lead re-checks on **held-out seeds 100–119** and end to end (MPC served fraction, P = 3 and P = 10) to catch metric gaming.

**Constraints:**
- Must satisfy the `DemandForecaster` contract (`observe(t, counts)`, `forecast(t, H) -> Forecast`).
- O(Z) per step.
- No access to `trace.rates` or the change labels.

**Idea backlog (ordered):**
1. ✅ Running post-change mean after an alarm (v1, kept).
2. Spatial pooling: CUSUM on 2×2 blocks plus single zones. A shock on a block is detected about 4× faster at equal false-alarm rate.
3. Two detectors (δ=1 fast, δ=0.3 slow) with separate thresholds, to catch shocks smaller than 2× in busy zones.
4. Spike-robustness: require persistence (alarm only if the post-change MLE stays high for m steps), or robust BOCPD (Altamirano et al. 2023).
5. BOCPD run-length mixture forecast (Adams & MacKay 2007) with a Poisson-gamma conjugate model.
6. Holt trend term for gradual drift.
7. A conformal-PID upper band, scored separately (coverage, width) for the safety-stock variant.
8. Optuna sweep over (α, δ, h) once the structure stabilises.
