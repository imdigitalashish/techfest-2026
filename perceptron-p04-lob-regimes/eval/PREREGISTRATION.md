# Pre-registration — v2 evaluation of the P4 spike

- **Written:** 2026-10-04, committed 11:43:47 IST (`d9ad7a9`), before any v2 result (dev or holdout) existed. *(The original line said "~12:00 IST"; corrected in Amendment 2 from the commit metadata.)* The commit that adds this file is the pre-registration commit (its hash appears in `git log -- eval/PREREGISTRATION.md`).
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

### Amendment 1 — committed 2026-10-04 11:58:28 IST (`a9b310b`), after the dev runs; the v2 holdout had not been run
1. **Selection by the registered rule (§8).** Results in `eval/results/v2_dev.md`. H = 10 and B = 600 had the lowest dev pooled log-loss among the 6 variants (0.6562). They are written into `CFG_V2` and apply to every Fixed-Share + harm policy: `spike`, `spike_wf`, `spike_gbdt`, `fs_coin_harm`.
2. **What dev showed** (dev only):
   - Plain volatility-regime gating reached 0.6489, −0.0125 vs static, better on 12/12 days.
   - The Fixed-Share mixture was weaker (0.6559), and adding the abstain expert made it worse (0.6580).
   - The textbook KS→refit was worse than static on 12/12 days (+0.0216).
   - In the FOMC window (2024-05-01) every model was worse than a coin flip (0.6954–0.7396).
3. **Post-dev revision `spike_gate`, added before the holdout run.** It combines:
   - the volatility-regime gate (C7);
   - a harm gate that shrinks p toward 0.5 while the *raw* gated model's CUSUM of (loss − ln 2) is alarmed;
   - the calibrated lean KS, as audit only (it raises alarms but takes no action).

   Grid (`eval/tuning_v2_amend1.json`, results in `eval/results/v2_dev_amend1.md`): λ ∈ {0, 0.5} × H ∈ {5, 10, 20} × B ∈ {300, 1800}. The §8 rule selected **λ = 0.5, H = 20, B = 300** (dev 0.6492).

   **Stated in advance:** on dev this does *not* beat plain regime gating (0.6492 vs 0.6489). Its dev benefit is confined to the FOMC window, where it scores 0.6988 vs 0.6992 for plain gating, and down to 0.6925 for more aggressive settings at a cost to the average.
4. **Added holdout hypotheses** (secondary, labelled post-dev; same test, 97.5% day-cluster CI):
   - **H1b:** `spike_gate` < `static_snorm`.
   - **H2b:** `spike_gate` < `ks_refit`.
   - **H3:** `spike_gate` < `regime_gated` (expected null on the dev evidence).

   Also reported: `regime_gated` against all references.
5. **Holdout policy list** gains `spike_gate`, `spike_gate_wf` and `regime_gated_wf`. Thresholds τ for the top-decile rule come from the dev runs (`tau_alias` in `CFG_V2`). Policies without a dev counterpart (`spike_gbdt`) get no top-decile rule.
6. **Nothing else changed.** H1 and H2 (the registered `spike`) remain the primary hypotheses.

### Amendment 2 — 2026-10-04 ~13:10 IST (AFTER the holdout run; disclosures and exploratory analyses only)
The holdout run finished at 12:02:51 IST (commit `a9b310b`, clean tree). The cross-model reviews (`reviews/2026-10-04-*`) found the following. Nothing below changes the registered analysis or its numbers.

1. **Prior exposure (review A1/S1).** 2025-08-01, one of the 22 holdout days, had been evaluated and read in the overnight v1 run (`eval/results/baseline.md`, v1 holdout), before v2 was registered. Two other v1 holdout days, 2024-05-01 and 2024-11-01, are v2 dev days. So "the holdout had not been … read" in Amendment 1 holds for 21 of the 22 days, not all of them.

   Exploratory sensitivity analysis (`eval/sensitivity_v2.py` → `eval/results/v2_holdout_sensitivity.md`):
   - excluding 2025-08-01 changes no conclusion;
   - the same holds under 99% CIs (Bonferroni over the five reported hypotheses), equal-day weighting, and leave-one-day-out.
2. **Hypothesis family (A2).** The 97.5% Bonferroni level covers only H1 and H2. H1b, H2b and H3 were added after dev, so they are secondary. At 99% (five hypotheses), H1b and H2b still exclude 0, and H3 still shows a small worsening.
3. **Post-hoc ablation (A9, exploratory).** `static_enorm` (one head, EWMA features) vs `regime_gated` (three heads, EWMA features) isolates the regime heads from the normalisation (`eval/results/v2_holdout_posthoc_ablation.md`): −0.0083 [−0.0118, −0.0059], better on 22/22 days. EWMA alone vs static: −0.0016, CI spans 0.
4. **Code fixes after the holdout; the registered results were not re-run.**
   - S2: `score()` now also reports `edge_bps_all_signals`. The existing `edge_bps` is non-tie, i.e. conditional on a move; the edge table was always all-signal.
   - S3: `run_episode` rejects Labels whose availability differs from t + h.
   - S4: exits after the day's last quote are excluded. This affects at most one signal per day in the edge table.
   - S5: the number check is now sign-sensitive.
5. **Wording corrections (A3–A8).**
   - λ = 0.5 is *confidence shrinkage*, not abstention.
   - The CUSUM is a heuristic without ARL calibration under dependent losses, and it monitors the *raw* gated model.
   - KS thresholds are empirical marginal quantiles, not daily false-alarm control.
   - The forecast target is P(up | non-zero 10-s move).

### Amendment 3 — 2026-10-04 22:23 IST (disclosure only; no analysis changed)
**Labeler tie handling.** `components/labeler` marks a tie only when `mid[t+h] == mid[t]` exactly, with mid = 0.5·(bid+ask) in float64. When the same mid comes from a different bid/ask pair (e.g. a symmetric spread change), the two floats can differ by about one ulp. That "move" (|move| < 1e-6 bps) then gets labelled up or down by rounding noise instead of being dropped as a tie.

The demo builder found this while testing the semi-synthetic splice. Measured on all 46 days with the committed code: **4** such labels out of 3,012,921 scored labels (1.3×10⁻⁶), at most 1 per day. They are identical across policies, so paired comparisons are unaffected beyond negligible noise. The committed labeler stays frozen for reproducibility. A future version would compare integer tick prices.

