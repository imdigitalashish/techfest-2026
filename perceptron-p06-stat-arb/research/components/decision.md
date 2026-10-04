# C8 decision — latency-aware EV ranking and act/wait

## 1) Contract summary

C8 consumes one live `Opportunity`, C7 `DecayModel`, C2 `LatencyModel`, C5 costs, and an estimated failed-attempt/legging loss `lambda`. It emits either no order or an `OrderIntent` with decision timestamp, venues, size, limit prices, and `ev_bps`.

The key rule is:

`EV_now = S(L | x) * (edge - cost) - (1 - S(L | x)) * lambda`

where `L` is end-to-end order latency. Waiting `Delta` for confirmation gives:

`EV_wait(Delta) = S(Delta + L | x) * (edge - cost) - (S(Delta | x) - S(Delta + L | x)) * lambda`

C8 ranks simultaneous opportunities by EV subject to inventory/capital caps. The architecture baselines are “trade every cross above fees” and z-score thresholds. The isolated metric is simulated net PnL/day at latency `L` and fee tier, plus capture ratio versus an oracle.

## 2) State of the art with opened sources

- **Survival probabilities are legitimate decision inputs, not just descriptive stats.** C7 sources support estimating `S(t|x)` from censored lifetimes: Kaplan-Meier for nonparametric curves ([lifelines KM tutorial](https://lifelines.readthedocs.io/en/latest/Survival%20analysis%20with%20lifelines.html)), Cox for covariates ([lifelines CoxPHFitter](https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html)), gradient-boosted survival for nonlinear covariates ([scikit-survival boosting](https://scikit-survival.readthedocs.io/en/stable/user_guide/boosting.html)), neural Cox extensions ([JMLR 2019](https://jmlr.org/papers/v20/18-424.html); [DeepSurv PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5828433/)), and survival-distribution evaluation ([JMLR 2020](https://jmlr.org/papers/v21/18-772.html)).
- **Latency-aware finance exists, but the exact EV/optimal-delay rule was not verified in opened sources.** Searches/fetches for Moallemi-Sağlam “The Cost of Latency in High-Frequency Trading” and Cartea-Sánchez-Betancourt “Optimal Execution with Stochastic Delay” hit inaccessible or failed pages in this session. Therefore, their specific models and conclusions are **UNVERIFIED** here and should not be cited as support beyond being follow-up leads.
- **Optimal stopping for mean-reverting spreads is an opened adjacent precedent.** The research worker opened Leung and Li, “Optimal Mean Reversion Trading with Transaction Costs and Stop-Loss Exit,” and verified it frames OU spread trading as an optimal entry/exit problem with transaction costs and stop-loss boundaries ([arXiv page](https://arxiv.org/abs/1411.5062)). This supports the general idea that entry timing has option value, but it does not verify our censored-survival EV formula.
- **LOB survival/fill models are an adjacent execution precedent.** The research worker opened Arroyo et al. and verified fill-probability survival estimation from LOB time series using a causal convolution/Transformer architecture ([arXiv page](https://arxiv.org/abs/2306.05479)). This supports modeling execution opportunity lifetime, but C8’s decision objective remains our project-specific formulation.
- **Sequential confirmation / SPRT / quickest detection are UNVERIFIED in this pass.** No opened primary source in this session directly supports applying SPRT or quickest-detection theory to this stat-arb latency decision. Treat such framing as future research unless verified later.

## 3) Baseline we ship now

Ship C8 in four deterministic modes, all using the same simulator-facing `OrderIntent` contract:

1. **Naive baseline:** act immediately when `edge - cost > 0` and size is positive.
2. **Z-score baseline:** act immediately when deviation exceeds `k * basis_sd` and `edge - cost > 0`.
3. **EV-now baseline:** compute `S(L|x)` from C7 and act only if `EV_now > min_ev_bps`; rank opportunities by `EV_now * size_notional` under inventory caps.
4. **Grid-search wait policy:** evaluate a small predeclared confirmation grid, e.g. `Delta in {0, 1, 2, 5, 10, 25, 50} ms`; choose the best positive EV action, otherwise skip. `Delta=0` is act now.

Initial assumptions:

- `lambda` is estimated from C9 as the mean or conservative quantile loss of one filled leg plus forced unwind when the other leg misses.
- `edge` is net of C4 fair basis and C5 fees; C8 should not re-detect opportunities.
- If `S(t|x)` is unavailable for a horizon, use conservative interpolation or skip; do not extrapolate tail survival invisibly.
- For Round 1, confirmation means “recompute the opportunity after waiting Delta,” not placing a hidden order or changing queue priority.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Critical read |
|---|---|---:|---:|---:|---:|---:|---|
| Survival-EV ranker | Rank by `S(L|x)*(edge-cost) - (1-S(L|x))*lambda` instead of raw edge or z-score. | 5 | 4 | 5 | 5 | 5 | Core differentiator; survival and latency are known areas, but this exact cross-asset EV packaging was not found in opened sources. |
| Hazard-shaped optimal confirmation delay | Choose `Delta*` from a latency grid; fake crosses with high early hazard can be allowed to die before acting. | 5 | 5 | 4 | 5 | 5 | Best innovation story if backtest confirms positive PnL/capture. Literature gap remains UNVERIFIED, so present as our spike. |
| Risk-sensitive EV with conformal/lower survival | Use a lower confidence bound on `S(L|x)` or require EV positive under pessimistic survival. | 4 | 4 | 2 | 4 | 3 | Attractive but source details for conformal survival are not verified; keep as stretch. |
| Inventory-aware opportunity knapsack | Allocate limited notional to top EV opportunities with per-venue/instrument exposure caps. | 4 | 2 | 4 | 5 | 4 | Less novel, but necessary if many opportunities fire simultaneously. |
| Policy frontier over latency budget | Show PnL/capture as latency is swept and identify where act/wait flips. | 4 | 3 | 5 | 5 | 5 | Demo-friendly and directly tied to problem statement; more evaluation innovation than model innovation. |

Best C8 candidates: **survival-EV ranker** and **hazard-shaped optimal confirmation delay**.

## 5) Isolated scalar metric

**Simulated net PnL/day at latency `L` and fee tier**, using C9 exchange-time fill truth.

Primary report:

- `net_pnl_bps_per_day` and `net_pnl_usd_per_day` for each policy;
- `capture_ratio = policy_pnl / oracle_pnl`, where the oracle has the same candidates and latency assumptions but knows whether execution will still be profitable;
- latency frontier across `L` grid points.

Secondary checks:

- trade count/day;
- hit rate after fees;
- average legging loss;
- EV calibration: realized mean PnL by predicted EV bucket;
- regret of chosen `Delta` versus hindsight best grid `Delta`.

## 6) Failure modes and tests

- **Misestimated `lambda`:** underpricing failed legs makes EV too aggressive. Test sensitivity over mean, p75, p90, and stress `lambda` from C9.
- **Survival miscalibration at exactly `L`:** a good C-index can still produce bad EV. Test realized PnL and survival calibration by predicted `S(L)` decile.
- **Double-counting costs:** C6/C8/C9 may each subtract fees. Test a toy opportunity with known prices and fees end-to-end.
- **Ignoring asymmetric venue latency:** buy and sell legs may have different `L_order`. Test pair-specific arrival times and leg ordering in C9.
- **Confirmation wait changes edge:** `EV_wait` assumes the opportunity can be re-evaluated after `Delta`; edge may shrink even if still alive. Test both binary survival and edge-decay `E[edge(t)]/edge(0)` variants.
- **Clock skew creates false act/wait wins:** waiting may appear beneficial because labels use misaligned clocks. Test synthetic streams with injected skew and assert the policy does not improve from impossible look-ahead.
- **Overfit thresholds and Delta grid:** optimizing `min_ev_bps`, `lambda`, and Delta on the test day inflates PnL. Test locked hyperparameters on a held-out day.
- **Crowding/capital constraints ignored:** ranking by bps alone can choose tiny or mutually exclusive trades. Test notional-weighted EV with per-venue and per-instrument caps.
- **Regime shifts:** hazard and loss distributions may invert during news. Test daily walk-forward and volatility-tercile breakdowns.
