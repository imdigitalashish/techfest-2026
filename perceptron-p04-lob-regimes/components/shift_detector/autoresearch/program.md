# C6 shift monitor — auto-research program

**Goal:** a rolling-KS-family detector that stays quiet on ordinary days and fires soon after real regime changes. The Minimum Viable bar asks for a "simple statistical test"; we keep KS and make it *calibrated*.

**Metric (frozen in [`eval.py`](eval.py), lower is better):**
`SCORE = mean false alarms per dev day + 10 × fraction of verified dev events missed`. A hit is an alarm in [event, event + 30 min]. Dev days and events come from `eval/config.py` and `data/events.csv` (verified rows only). Secondary metrics: detection delay in seconds, and the per-feature thresholds.

**Reference points:** naive Bonferroni KS ≈ 47.7 (fires at its cooldown cap). A silent detector scores 10.0.

**Rules:**
1. Only `components/shift_detector/` code and the candidate JSON files change. `eval.py` and `eval/config.py` are frozen. Contract tests (`python -m pytest -q tests`) must pass.
2. Keep a change only if SCORE improves by more than 1.0 (≈ one false alarm per day) *and* no dev event becomes missed.
3. Log every run in `results.tsv` (timestamp · commit · candidate · hypothesis · score · delta vs best · kept · notes).
4. The lead re-checks kept candidates on the **holdout** days (never used here) with `eval/run_baseline.py` before any claim goes into a deliverable.

**Idea backlog (ordered):**
1. Empirical-null thresholds: leave-one-train-day-out windowed KS statistics at quantile q (q = 0.999, 1.0). *(running)*
2. Drop features whose null is unstable across training days (message rate dominates naive alarms).
3. One projection test on the forecaster's logit or a PCA score instead of 7 per-feature tests (Failing Loudly).
4. Time-of-day-matched reference windows (seasonality-aware null).
5. Harm gate: CUSUM / e-detector on ℓ(deployed) − ℓ(static), with a delayed-label confirmation before firing.
6. Calendar prior: lower the threshold within ±15 min of scheduled releases (known in advance, so no leakage).
7. Persist/cooldown sweep (Optuna) once 1–4 settle.
