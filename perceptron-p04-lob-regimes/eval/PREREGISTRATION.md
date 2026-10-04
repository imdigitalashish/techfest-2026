# Pre-registration — v2 evaluation of the P4 spike

- **Written:** 2026-10-04 ~12:00 IST, before any v2 result (dev or holdout) existed. The commit that adds this file is the pre-registration commit (its hash appears in `git log -- eval/PREREGISTRATION.md`).
- **Code at registration:** `components/` and `eval/run_v2.py`, `eval/config_v2.py`, `eval/tuning_v2.json` at the same commit.
- **Amendments** are appended at the bottom, dated, and committed *before* the run they affect.

## 1. Question
On data one to three years after training, does the spike forecast 10-second BTC mid-price direction better than:
- (A) a static model, and
- (B) the textbook "rolling KS → retrain" baseline?

The spike is a calibrated, harm-aware shift monitor plus a regime-head mixer.

We also ask whether any edge survives the spread and real exchange fees.

## 2. Data
- **Source:** Binance USD-M BTCUSDT perpetual, Tardis.dev `book_snapshot_5` (top-5 levels, exchange and receive timestamps).
- **Days:** **every free day**, i.e. the first of each month from 2023-01-01 to 2026-10-01 (46 days). Free access covers only these days; other days return HTTP 401 (verified 2026-10-04). Since all of them are used, there is no day selection.
- **Integrity:** one MD5 per file in `data/manifest.csv`. A day that fails to download or parse is excluded and listed in an amendment before the holdout run.
- **Scheduled events** (tagged ex ante from official sources, `data/events.csv`): FOMC statements at 2023-02-01 19:00 UTC, 2023-11-01 18:00 UTC and 2024-05-01 18:00 UTC (federalreserve.gov). No verified scheduled event falls on a holdout day, so holdout detection delay cannot be measured; alarm rates are reported instead.

## 3. Split (frozen in `eval/config_v2.py`)
| Split | Days | Used for |
|---|---|---|
| Train | 2023-01 … 2023-12 (12) | Everything that is fitted: scalers, logistic heads, volatility-regime edges and heads, KS references and empirical-null thresholds, GBDT |
| Dev | 2024-01 … 2024-12 (12) | Only the harm-gate threshold *H* and boost length *B*, by the rule in §8 |
| Holdout | 2025-01 … 2026-10 (22) | Reported once, after the §8 amendment is committed |

Walk-forward policies (`*_wf`) refit scalers and heads for each evaluated day on **all days strictly before it**, with rows subsampled every 10 s, i.e. non-overlapping labels.

## 4. Task
- **Grid and clock:** 1 s decision grid on receive time.
- **Label:** sign of the mid-price change over 10 s. Ties are excluded from log-loss and AUC, but kept as zero moves in the edge calculation.
- **Label availability:** online learners may use the label of step t only at t + 10 s; a contract test enforces this.
- **Features:** the 17 causal features from v1, unchanged.

## 5. Policies (exact specs: `components/adapter/__init__.py`, `POLICIES`, at this commit)
- **`static_snorm`** — baseline A. Logistic regression on static z-scores, trained on 2023.
- **`ks_refit`** — baseline B. Rolling two-sample KS on 7 features, Bonferroni α = 1e-3, 600 s window subsampled every 10 s, 3 consecutive rejections, 30-min cooldown. On each alarm, refit on the post-alarm window.
- **`spike`** — the spike:
  - EWMA normaliser.
  - Fixed-Share mixture (η = 1, α = 1e-3) over 8 experts: static, slow and fast SGD, periodic refit, three volatility-regime heads, and a constant p = 0.5 "abstain" expert.
  - **Harm gate:** CUSUM on (deployed log-loss − ln 2) from delayed labels.
  - **Calibrated rolling KS** (label-free) on the 5 "lean" features, with thresholds at the 0.999 quantile of the leave-one-train-day-out null.
  - An alarm from either detector raises the switching rate to α = 0.05 for *B* steps.
- **Ablation ladder:** `fixed_share` (no abstain expert, no detectors) → `fs_coin` (+ abstain expert) → `fs_coin_harm` (+ harm gate) → `spike` (+ calibrated KS).
- **Other comparators:**
  - `regime_gated`, `periodic_refit`, `online_sgd`;
  - `ksc_refit` (calibrated KS → refit);
  - `static_wf` and `spike_wf` (walk-forward);
  - `static_gbdt` (HistGradientBoosting, 200 iterations, trained on 2023);
  - `spike_gbdt` (the spike plus a GBDT expert).

## 6. Primary hypotheses (holdout, pooled over all holdout days)
- **H1:** mean per-step log-loss difference (spike − `static_snorm`) < 0.
- **H2:** mean per-step log-loss difference (spike − `ks_refit`) < 0.
- **Test:** paired **day-cluster bootstrap** with 2,000 resamples of whole days, applied to the pooled mean difference.
- **Decision:** a hypothesis is "supported" if the upper end of its **97.5%** two-sided CI is below 0. The level is Bonferroni-adjusted for two primary hypotheses. Otherwise it is "not supported".
- **Also reported:** a moving-block bootstrap 95% CI (600-step blocks), and the number of days on which the spike is better.

## 7. Secondary outcomes (reported; no decision rule)
- AUC and accuracy.
- Δ against `static_wf`: is daily retraining enough?
- The ablation ladder.
- Alarms per day by detector.
- **Trading edge per signal, in bps of mid** (signal = sign(p − 0.5) every second, 10 s hold):
  - gross mid-to-mid;
  - taker: cross the spread at decision + 0 ms and + 100 ms, and again at horizon + delay;
  - maker upper bound: both legs passive at the touch, ignoring queue position and adverse selection;
  - each net of the official Binance USDⓈ-M fees: Regular 2.0/5.0 bps and VIP 9 0.0/1.7 bps (maker/taker);
  - break-even fee per side;
  - a top-decile confidence rule with τ = the dev 90th percentile of |p − 0.5| for each policy, frozen from the dev run.
- Per-step latency (Python reference implementation).
- Per-day regime descriptors: volatility, spread, depth, price level.

## 8. Dev selection rule (the only tuning)
- **Grid** (`eval/tuning_v2.json`): H ∈ {10, 20, 40} nats × B ∈ {120, 600} steps.
- **Choice:** the variant with the lowest dev pooled log-loss. If several are within 0.0002 of the best, prefer the one with fewer alarms per day.
- The chosen H and B are written into `CFG_V2["harm"]["threshold"]` and `CFG_V2["fs_boost_steps"]` by an amendment, committed before the holdout run.

## 9. Reporting commitment
- All holdout numbers are reported, whatever their direction, in `eval/results/v2_holdout.{json,md}`.
- The results metadata records the commit hash and whether the tree was dirty.
- Any deviation from this protocol is logged as a dated amendment.

## 10. Limitations stated in advance
- One instrument.
- First-of-month days only, so days are not contiguous and between-day shifts dominate.
- One 10 s horizon.
- Edge figures ignore market impact, funding and queue dynamics; maker figures are upper bounds.
- No verified scheduled events on holdout days.

## Amendments
_(none yet)_
