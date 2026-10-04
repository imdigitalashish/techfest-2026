# ADR 001 — Spike choice: latency-conditioned decision layer (C8), with survival decay (C7) as its interpretable core

- **Status:** accepted (first version, 2026-10-04 07:10 IST). It will be revisited after the multi-day walk-forward. Decision owner: project lead.
- **Evidence:** [`eval/results/baseline_0901_to_1001.md`](../../eval/results/baseline_0901_to_1001.md) (train Tardis 2026-09-01 → held-out 2026-10-01, 9 BTC legs) and the first ratchet [`components/decision/autoresearch/results.tsv`](../../components/decision/autoresearch/results.tsv).

## Context
The brief asks us to "identify and rank cross-asset mispricings in near real time, trading off signal confidence against acting-on-it latency". Detection itself is easy: on 2026-10-01 our detector found 345,890 ≥1-bps episodes across 9 BTC venues. The hard part is the value of an episode **at the moment our order arrives**. That depends on whether the episode is real, whether it survives our latency, and whether it clears fees at the size available.

## Candidates (scored 1–5: impact on judged criteria · novelty · feasibility by Dec · measurability · demoability)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| **A. Decision layer: latency-conditioned value + act/wait (C8), survival decay as its interpretable core (C7)** | 5 | 4 | 5 | 5 | 5 | **24** |
| B. Lead–lag fair value (Hayashi–Yoshida / state-space) (C4) | 4 | 3 | 4 | 4 | 3 | 18 |
| C. Learned latency-budget allocation across vantage points (C2 + deployment) | 3 | 4 | 3 | 3 | 4 | 17 |
| D. Covariate survival model alone (C7: Weibull AFT / Cox) | 3 | 3 | 5 | 5 | 3 | 19 |

## Six Thinking Hats (on A)
- **White (facts):** median episode lifetime 90.5 ms; S(10 ms) = 0.82; Weibull shape ρ = 0.43 (decreasing hazard). At 1 bps/leg fees, naive P&L falls from +$1,490 (1 ms) to −$1,570 (10 ms). The tuned per-pair threshold earns +$1,977 / +$768. EV(KM-by-pair) earns +$1,990 / +$672, and LEV earns +$1,926 / +$802. Ranking power of raw edge collapses with latency (Spearman with realised P&L 0.83 → 0.05 from 0.5 to 50 ms), while LEV keeps 0.41. The ratchet's best learned rule beat the tuned threshold by +$99 on validation, but the bootstrap SE was ≈ $150, so it was not kept.
- **Red (gut / judges):** Optiver judges will respect a frontier plot with honest negatives more than a backtest that always wins. "We rank by what it will be worth when we arrive" is a one-line idea they'll remember.
- **Black (risks):** cross-venue exchange clocks aren't a common clock; Binance-spot Tardis quotes are ~100 ms granular; λ is not constant; survival ≠ profitability (long-lived crosses may be toxic); one held-out day; the gain over a tuned threshold is not yet significant.
- **Yellow (benefits):** the layer directly answers the brief's trade-off and is measurable by a single scalar (simulated P&L at latency L). It also degrades gracefully: at high latency it learns to skip trades instead of losing money.
- **Green (alternatives):** use survival as a feature, not the objective. Model residual survival S(a+L)/S(a) for aged episodes. Use a downside-quantile model for risk-adjusted ranking. Allocate scarce fast-path capacity across signals. Learn which vantage point to trade from.
- **Blue (process):** keep A as the spike, B as the next component upgrade, and everything else as best practice. Gate every claim on the falsification tests below.

## Thesis → antithesis → synthesis
- **Thesis (lead):** EV = S(L|x)·net − (1 − S(L|x))·λ, with S from censored survival of episode lifetimes, trades confidence against latency in one quantity. The hazard shape gives an explicit act-now-vs-wait rule.
- **Antithesis (independent `rubber-duck` agent, 2026-10-04):** survival is the wrong target. Persistence ≠ executable profit, and long-lived crosses can be stale or toxic. 1 − S(L) is not the legging probability, and λ is heterogeneous and heavy-tailed. Exchange-time replay across venues may be causally invalid. Our own numbers show survival adds little beyond edge, pair and the fee hurdle. One day of data is not robustness. It proposes predicting **latency-conditioned executable markout** directly from simulator labels, with survival as a feature.
- **Synthesis (decision):** the spike is the **decision layer**. Its primary model is LEV(x, L) = E[realised P&L | features, end-to-end latency], learned from simulator labels: joint IOC legs at venue-specific arrival times, partial fills, fees and unwind loss. A downside-quantile companion and an act-now-vs-wait rule sit alongside it. Survival stays (a) as the MVP decay report and (b) as an interpretable prior/feature, using residual survival for aged episodes. The tuned per-pair threshold is the bar to beat. "Cross-asset" is honoured by a tier-3 BTC/ETH lead–lag extension, not claimed from cross-venue BTC alone.

## Consequences
- C8 gets the ratchet loop (frozen `eval.py`, keep only beyond bootstrap SE, fresh-holdout re-check). C7 keeps KM by pair as production baseline (IBS 0.109 vs pooled 0.126 on the held-out day).
- The evaluation must add: multi-day walk-forward on Tardis first-of-month days; receive-time replay and ±clock-offset perturbation; risk metrics (drawdown, tail loss, turnover); and a compiled/linear LEV path, since the current tree model costs ~1.5 ms in Python versus 7 µs for the survival EV.

## Falsification tests (from the antithesis; all three must pass before the finals claim)
1. **Walk-forward superiority:** on ≥ 12 disjoint days, the paired-bootstrap lower bound of (LEV − tuned pair×latency threshold) P&L is > 0.
2. **Incremental-information ablation:** removing/permuting the survival or LEV score among matched events (edge, pair, age, spread, volatility) degrades out-of-sample P&L and ranking.
3. **Causal replay robustness:** re-running with receive-time decisions, ±5 ms clock-offset perturbations and partial fills does not reverse the half-life ordering or the policy uplift.

## Status update — 2026-10-04 10:00 IST
- **Test 3:** passed for LEV (uplift positive in all 5 clock variants; half-life rank ρ ≥ 0.984). Survival-EV as a decision rule fails receive-time replay, which confirms the synthesis: survival is the report and a feature, LEV is the rule. Partial fills beyond top-of-book remain untested. See [results](../../eval/results/falsification_clockskew.md).
- **Test 1:** inconclusive at n = 4 days: 4/4 positive, mean +$248/day, but the t-CI includes 0. Needs ≥ 12 days. See [results](../../eval/results/falsification_walkforward.md).
- **Test 2:** partial. Full-feature LEV beats edge-only LEV on 4/4 days, with the same significance caveat. Matched-event permutation is not yet run.
