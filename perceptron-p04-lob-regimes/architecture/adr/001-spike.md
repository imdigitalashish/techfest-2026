# ADR 001 — Spike components: the calibrated, harm-aware shift monitor (C6) and the regime-adaptive head mixer (C7)

- **Status:** accepted (first version, 2026-10-04). Revisit after the 12 Oct selection and again at the 1 Dec midway check.
- **Deciders:** project lead. Lean mode was in force overnight, so there was no independent adversarial sub-agent. The antithesis below was written by the lead against its own proposal, and an independent `rubber-duck` review is scheduled once the network allows (see *Follow-ups*).
- **Evidence:** [`eval/results/baseline.md`](../../eval/results/baseline.md), [`eval/results/calibrated_ks.md`](../../eval/results/calibrated_ks.md), [`research/landscape.md`](../../research/landscape.md).

## Context

The Minimum Viable bar asks for a short-horizon direction/spread forecaster plus a simple statistical shift test (e.g. rolling KS) "and show the model reacting to it". The obvious baseline is "rolling KS on features → retrain on recent data". On real Binance BTCUSDT data (6 evaluation days, 1 s grid, 10 s horizon), our harness shows this baseline is **harmful**:
- Bonferroni rolling KS (α=1e-3) fires at its cooldown cap of 48 alarms/day **on every day**. On 1-second microstructure features, every 10-minute window differs significantly from the reference. With autocorrelation and n in the thousands, the i.i.d. p-value carries no information.
- Refitting on post-alarm windows *raises* log-loss: +0.0167 [+0.0115, +0.0220] on dev, +0.0202 [+0.0157, +0.0247] on holdout (95% moving-block bootstrap).
- A static model degrades quietly from 2023 (dev log-loss 0.6473, AUC 0.674) to 2024–25 (holdout 0.6808, AUC 0.618).
- Volatility-regime heads trained offline cut holdout log-loss by 0.0132 [0.0115, 0.0148] and are the best policy in both FOMC windows.

The question is which one or two components should carry the innovation.

### First calibration attempt (run 2026-10-04 07:49, `python eval/run_baseline.py --policies static_snorm ks_refit ksc_refit regime_gated fixed_share fs_ksc_boost --tag calibrated_ks`)
- The empirical-null KS (0.999 quantile of leave-one-train-day-out windowed statistics) cut alarms from 48 to 37–39 per dev day and to 15–47 per holdout day. That is better, but nowhere near quiet.
- The remaining alarms come almost entirely from **activity-level features** (`log_msgs_10s`, `log_depth5`), whose levels drift from month to month. Two training days cannot span that.
- Refitting on these alarms still hurts (`ksc_refit`: +0.0175 [+0.0132, +0.0220] dev, +0.0152 [+0.0113, +0.0196] holdout).
- Using them only to boost Fixed-Share switching is neutral (`fs_ksc_boost` −0.0066 vs `fixed_share` −0.0070 on holdout).
- **Implication:** calibration alone is not the spike. The spike is calibration **plus** monitoring the *invariant / normalised* representation **plus** the harm gate. Those are ratchet ideas 2–5 in [`program.md`](../../components/shift_detector/autoresearch/program.md).

## Candidates (scored 1–5)

| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by 15 Dec | Measurable (scalar) | Demoable | Total |
|---|---|---|---|---|---|---|
| **A. C6 calibrated + harm-aware shift monitor**: empirical-null thresholds (leave-one-day-out, real autocorrelation and seasonality), then a sequential loss test (CUSUM / e-detector) that confirms harm before acting; calendar-aware prior around scheduled releases | 5 (it *is* the MV bullet, done right) | 4 (KS calibration is classical; combining it with harm gating [Podkopaev & Ramdas] and exogenous event priors in a µs LOB loop is new) | 5 | 5 (false alarms/day at fixed delay) | 5 (alarm timeline over an FOMC day) | **24** |
| **B. C7 regime-adaptive heads + Fixed-Share mixer**: offline regime heads plus online heads, mixed by tracking-regret weights; alarms *boost the switching rate* instead of refitting | 5 (stretch goal 1) | 3 (MoE/expert tracking is known; alarm-modulated switching is less common) | 5 (baseline already runs) | 5 (holdout Δlog-loss with CI) | 4 | **22** |
| C. Stronger forecaster head (TLOB/DeepLOB/GBDT) | 3 | 1 (benchmarks exist) | 4 | 5 | 3 | 16 |
| D. Generative-model regime simulator (LOB-Bench/MarS-style) for stress tests | 3 | 4 | 2 | 3 | 4 | 16 |
| E. Conformal test martingale on model p-values (2026 optimal constructions) | 4 | 5 | 3 (theory-heavy) | 4 | 3 | 19 → folded into A as a variant |
| F. Compiled (Numba/C++/FPGA-style) online step | 3 (stretch goal 2) | 2 | 4 | 5 (p99 µs) | 4 | 18 → best-practice track |

**Decision:** A and B are the spikes. C and F are best-practice tracks behind the existing contracts. E is a variant inside A. D is out of scope before the finals.

## Six Thinking Hats (on A+B)

- **White (facts):** naive KS gives 48 alarms/day and is harmful (numbers above). Regime heads give −0.013 log-loss on holdout. The receive−exchange delay is 2.9 ms median and 19 ms p99. Single-head steps take 3–7 µs p50 in Python; the 7-head mixer takes 41 µs p50 (shared machine). Only 8 days are on disk; NFP dates are unverified.
- **Red (gut):** Optiver judges will love "we tried the textbook baseline, measured that it hurts, and explained why". A clean alarm timeline that is quiet all day and fires minutes after the FOMC statement is the demo shot.
- **Black (risks):** (1) an empirical null from 2 training days may be too narrow or too loose → more train days and leave-one-day-out CV; (2) the edge is tiny (AUC 0.62–0.67), so a judge may ask "so what?" → report edge in bps against the spread and position the work as robustness; (3) the harm test needs labels, which arrive with a 10 s delay — fine at this horizon, but say so; (4) over-tuning on 3 dev days → frozen holdout and ratchet discipline; (5) crypto ≠ equities → add LOBSTER sample days if time allows.
- **Yellow (benefits):** directly answers "detect and adapt instead of silently degrading". Every claim has a scalar metric. O(1) per-step costs fit a µs budget. The same seams accept stronger heads later.
- **Green (alternatives):** BOCPD with a time-varying hazard driven by the release calendar; a single learned projection test (Failing Loudly) instead of 7 per-feature tests; conformal PID for abstention; a spread-forecast head as a second target.
- **Blue (process):** freeze `eval/config.py`, ratchet C6 thresholds and C7 mixer hyper-parameters on dev only (`components/*/autoresearch/results.tsv`), re-check on holdout by the lead, grow the holdout with more first-of-month days.

## Thesis → antithesis → synthesis

- **Thesis:** shift handling, not model capacity, is the bottleneck. Make detection calibrated and harm-aware, and make adaptation a cheap re-weighting of pre-trained regime heads.
- **Antithesis (lead as adversary):** "Calibration just raises the threshold until nothing fires. A detector that never fires is useless, and the regime heads already do the adapting without any detector, so C6 adds nothing to the log-loss." Also: "Volatility terciles are a hand-made regime definition. A GBDT with volatility as a feature would learn the same interactions."
- **Synthesis:** C6 is judged on its own scalar — false alarms per calm day **at a fixed detection delay** on known event times and on spliced streams with known changepoints — not only by downstream log-loss. A calibrated monitor is worth having even when the mixer adapts on its own: it is the audit trail ("the model knows when it is in a regime it was not trained for"), it drives the mixer's switching rate, and it gates expensive actions (refits, risk limits). The GBDT objection is tested directly: a GBDT head is added behind C5, and the regime mixer must beat it on holdout Δlog-loss, or we report that it does not.

## First principles

Order-flow imbalance moves prices with a slope ∝ 1/depth (Cont, Kukanov & Stoikov 2014). A liquidity shock therefore changes the *coefficient* (a concept shift), while a volatility burst changes feature *scales* (a covariate shift). The cheapest robust design removes the scale drift label-free (EWMA normaliser C4), conditions on the state variables the theory names (depth-normalised OFI in C2, volatility/depth regimes in C7), and keeps statistical alarms (C6) for what is left. An alarm is only worth acting on if it predicts higher loss.

## Consequences

- C6 and C7 get `autoresearch/` ratchets (frozen `eval.py`, `results.tsv`). The first ledger is under `components/shift_detector/autoresearch/`.
- C5 stays logistic for the Round-1 plan. GBDT/DeepLOB heads are best-practice additions, not the pitch.
- The Round-1 abstract frames the novelty as: (1) a measured failure of the textbook baseline, (2) a calibrated, harm-aware monitor, (3) regime-adaptive heads with alarm-modulated switching, (4) a latency contract.

## Follow-ups

1. Independent `rubber-duck` adversarial review of this ADR once sub-agents are allowed again.
2. More training days for the empirical null (download the remaining first-of-month days after 08:30).
3. A semi-synthetic splice benchmark (calm day → event day at a known time) for detection delay against the false-alarm rate.
4. Harm test: CUSUM / e-detector on the loss difference between the deployed mixture and the static head.
