# C11 eval — rigorous evaluation harness

## 1) Contract summary

C11 consumes all upstream outputs and writes reproducible `eval/results/*.json` and reports: decay summaries, policy tables across latency grid and fee tiers, and latency-PnL frontiers. The architecture specifies train on 2026-09-01, test on 2026-10-01, plus live recording where available. Every deliverable number must come from a result file with the command that reproduces it.

The end-to-end scalar metric is net PnL versus latency frontier plus capture ratio. C4 and C6 keep their own isolated metrics: next-100 ms basis RMSE and AUC-PR for profitable-at-latency labels.

## 2) State of the art with opened sources

- **Latency evaluation must model failed attempts, not just fills.** Aquilina, Budish, and O'Neill state that message data reveal both winners and losers of races, while ordinary order-book data hide failed attempts; their BIS page reports latency races are frequent, fast, and economically meaningful. Source opened: BIS WP 955 page; also via `papers-microstructure.md`.
- **Statistical signal is not sufficient evidence of tradability.** Huth and Abergel find lead-lag predictive accuracy but no naive market-order profit after spread. Source opened: arXiv API for `1111.7103`; also via `papers-microstructure.md`.
- **Non-synchronous sampling must be audited.** Hoffmann, Rosenbaum, and Yoshida's estimator is explicitly for randomly sampled non-synchronous data; evaluation should therefore include look-ahead and alignment tests. Source opened: arXiv API for `1303.4871`; also via `papers-microstructure.md`.
- **Regime and venue leadership can change.** Pascual et al. report that crypto spot/futures leadership becomes mixed during high-volatility periods, so held-out testing must include regime slices instead of one blended score. Source opened: arXiv API for `2506.08718`; also via `papers-microstructure.md`.
- **Multiple-testing/overfitting control is central in strategy evaluation.** Crossref metadata opened for Bailey and Lopez de Prado's *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality* confirms the method and venue. The source page content available here did not include formulas; formula-level implementation details remain **UNVERIFIED** in this session.
- **Block bootstrap confidence intervals:** requested for C11, but no primary source was opened in this session. Include the method in the harness as a conservative dependence-aware CI and mark the literature citation **UNVERIFIED** until a primary source is opened.

## 3) Baseline we ship now

Ship a reproducible evaluation harness with these runs:

1. **Data split:** train/tune on 2026-09-01; final report on 2026-10-01; optional live recording as an out-of-sample sanity check. If those exact days are unavailable, use the closest full days and write the substitution into the result metadata.
2. **Latency sweep:** evaluate L in `{0, 100us, 500us, 1ms, 5ms, 10ms, 50ms, 100ms, 500ms, 1s}` or the subset supported by data resolution.
3. **Fee-tier sweep:** `retail`, `vip`, and `mm=0bps upper-bound` to show whether performance exists only under unrealistic costs.
4. **Policies:** compare naive cross, z-score detector, model-based detector, and EV ranking if C7/C8 exist.
5. **Oracle upper bound:** compute best possible capture from opportunities known in hindsight at the same latency and fee tier, without allowing impossible pre-receive-time information in the policy under test.
6. **Labels:** generate profitable-at-latency labels through C9 exchange-time replay, including partial/failed/legged attempts.
7. **Reproducibility:** every table row stores config hash, git commit if available, input file list, command, and random seed.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| Latency-fee frontier with oracle capture ratio | Plot net PnL and capture ratio over latency x fee tiers versus hindsight oracle. | 5 | 4 | 5 | 5 | 5 | Best judge-facing bridge between MVP and Optiver-style latency budgets. |
| Deflated-Sharpe model-selection guard | Report raw Sharpe plus deflated/selection-adjusted Sharpe for all tested thresholds/models. | 4 | 4 | 3 | 4 | 3 | Source metadata opened, but formula details need verification before final implementation. |
| Dependence-aware block-bootstrap CIs | Confidence intervals over days/episodes using blocks to respect clustered opportunity arrivals. | 4 | 3 | 4 | 4 | 3 | Method source not opened; include as evaluation engineering with citation gap. |
| Look-ahead/leakage test suite | Automated perturbation tests: shift receive times, forbid future rows, compare exchange-time vs receive-time joins. | 5 | 3 | 5 | 5 | 4 | High rigour score; catches the most common backtest failure modes. |

Top candidate: **Latency-fee frontier with oracle capture ratio** because it directly answers the problem statement, is highly demoable, and makes latency/cost trade-offs visually obvious.

## 5) Isolated scalar metric

**Capture ratio at operating latency and fee tier:**

`capture_ratio = strategy_net_pnl_bps / oracle_net_pnl_bps`

Report it together with absolute net PnL/day. The oracle must obey the same latency and fee tier but can choose the best opportunities in hindsight from the replay. If oracle PnL is non-positive, mark capture ratio undefined and report absolute PnL only.

Primary tables:

- Net PnL/day by policy x latency x fee tier.
- Capture ratio by policy x latency x fee tier.
- Opportunity half-life and survival calibration by pair.
- C4 RMSE and C6 AUC-PR as component gates.

## 6) Risks

- **Look-ahead bias:** the largest risk; add invariant tests that no feature at receive time `t` uses a row first received after `t`.
- **Multiple testing:** many thresholds, pairs, and latencies can manufacture a winner; freeze final config before test day and report selection-adjusted metrics.
- **Serial dependence:** opportunities cluster, so iid standard errors are overconfident; use day-level and block-level uncertainty summaries, with source citation still UNVERIFIED for block bootstrap.
- **Oracle leakage:** oracle is an upper bound, not a policy; it must be clearly separated from deployable results.
- **Cost sensitivity:** apparent alpha may vanish under retail fees; always show fee-tier sweeps.
- **Resolution limits:** if quote data are coarser than a latency point, mark that cell unsupported rather than interpolating certainty.
- **Survivorship/data gaps:** missing venues or outage windows can bias frontier curves; report coverage and masked intervals.
