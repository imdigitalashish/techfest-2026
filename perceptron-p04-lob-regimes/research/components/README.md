# Per-component research (first version)

> Lean overnight mode: one file with a section per component. The cited sources and their quotes are in [`../landscape.md`](../landscape.md) and [`../notes/`](../notes/). Each section gives the state of the art, our baseline and the innovation candidates, each with the scalar that would decide it.

## C1 Ingest
- **State of the art:** vendor tick archives (Tardis.dev, LOBSTER, Databento). Production systems run on *receive* time.
- **Baseline:** Tardis `book_snapshot_5`, sorted by `local_timestamp`, MD5-pinned.
- **Measured:** receive−exchange delay 2.9 ms p50 / 19 ms p99 / 2.2 s max (2023-11-01).
- **Candidates:** (1) rebuild the book from `incremental_book_L2` for event-time features — scalar: rows/s; (2) add `trades` for trade-flow imbalance (download deferred by bandwidth).

## C2 Features
- **State of the art:** OFI (Cont, Kukanov & Stoikov 2014), multi-level OFI (Xu, Gould & Howison 2019), deep models on raw book states (DeepLOB, TLOB).
- **Baseline:** 17 causal features, including depth-normalised OFI.
- **Candidates:** (1) OFI normalised by *contemporaneous* depth vs trailing depth — scalar: single-feature AUC on dev and its stability across days (coefficient of variation); (2) event-time sampling (every N book changes) vs the 1 s clock; (3) trade-flow imbalance once trades are downloaded.

## C3 Labeler
- **State of the art:** smoothed k-step labels (FI-2010 style) are criticised for horizon bias (TLOB). Spread-aware labels make the task harder (TLOB).
- **Baseline:** raw sign of Δmid over 10 s; ties excluded (21%).
- **Candidates:** (1) 3-class with a spread-sized dead zone; (2) a spread-change target (the MV allows "direction or spread") as a second head — scalar: log-loss of each target.

## C4 Normaliser
- **State of the art:** DAIN, RevIN, SAN (normalising away drifting statistics).
- **Baseline:** EWMA z-score (half-life 30 min, causal, Numba).
- **Measured:** −0.0053 [−0.0064, −0.0041] holdout log-loss vs a static z-score with the same head.
- **Candidates:** (1) half-life chosen by the ratchet; (2) normalise by state variables (depth, volatility) as the theory suggests — scalar: Δlog-loss vs static.

## C5 Forecaster heads
- **State of the art:** TLOB / MLPLOB / DeepLOB (deep), GBDT (Kaggle winners), linear models on OFI.
- **Baseline:** logistic regression, d=17. AUC 0.674 dev / 0.618 holdout.
- **Candidates:** (1) LightGBM head; (2) small MLP (MLPLOB-like) via PyTorch/MLX — scalar: holdout log-loss at a fixed latency budget (an inference-compute frontier in the spirit of arXiv 2606.25986).

## C6 Shift monitor ⚡ (spike)
- **State of the art:** KS/KSWIN, ADWIN, Page-Hinkley/CUSUM, BOCPD (and its robust version), e-detectors with ARL guarantees, conformal test martingales (2026 optimal constructions), harmful-shift tracking (Podkopaev & Ramdas).
- **Baseline:** Bonferroni rolling KS (48 alarms/day — saturated) and Page-Hinkley on log-loss.
- **Candidates:**
  1. **Empirical-null calibration** (leave-one-train-day-out windowed KS statistics) — implemented; results in [`../../eval/results/calibrated_ks.md`](../../eval/results/calibrated_ks.md). First result: alarms fall only from 48 to 37–39 per dev day, still driven by message-rate and depth levels → next, monitor normalised features.
  2. **Harm gate:** a CUSUM/e-detector on ℓ(deployed) − ℓ(static).
  3. **Calendar-aware prior:** BOCPD hazard raised around scheduled releases.
  4. **One projection test** instead of 7 per-feature tests (Failing Loudly).
- **Scalar:** false alarms per calm day at a fixed detection delay (event timestamps and spliced streams).

## C7 Adapter / mixer ⚡ (spike)
- **State of the art:** OneNet / FSNet (online ensembles), Proceed (proactive under label delay), Fixed-Share / AdaHedge / strongly adaptive learning (tracking regret), Markov-switching / GMM regimes (Two Sigma), online learning in Kaggle winners (Optiver TATC).
- **Baseline:** 9 policies.
- **Best so far:** volatility-regime gating, −0.0132 [−0.0148, −0.0115] holdout Δlog-loss.
- **Candidates:**
  1. Regime heads inside a Fixed-Share mixer, with alarm-boosted switching.
  2. Soft gating by regime posterior (HMM/BOCPD).
  3. A Proceed-style proactive switch on label-free signals.
- **Scalar:** holdout Δlog-loss vs static, with a block-bootstrap CI.

## C8 Evaluator
- **State of the art:** prequential evaluation for streams; TCPDBench margins for changepoints; moving-block bootstrap for dependent data.
- **Baseline:** implemented.
- **Candidates:** Diebold–Mariano tests; per-regime breakdowns; edge net of spread and fees (for the Optiver realism questions).

## C9 Latency
- **State of the art:** in-network inference (LOBIN, arXiv 2608.02424); the latency frontier is weaker than the compute frontier (arXiv 2606.25986), so latency must be measured.
- **Baseline:** per-step `perf_counter_ns` in Python.
- **Candidates:** Numba-compiled online step; a C++ step with the same contract — scalar: p99 µs against the budget (≤50 µs).
