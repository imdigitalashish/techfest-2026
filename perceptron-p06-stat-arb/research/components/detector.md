# C6 detector — executable mispricings

## 1) Contract summary

C6 consumes `StateFrame`, `BasisFrame`, threshold theta, and fee tier. It emits `OpportunityFrame` episodes with:

- identifiers and lifecycle: `opp_id, t_start_us, t_end_us, duration_us, censored`;
- trade direction: `sell_venue, buy_venue`;
- economics: `edge0_bps` net of fair basis, `net0_bps` after fees, and executable `size` from top-of-book size;
- features: quote ages, spreads, 1 s volatility, and `edge_max_bps`.

Architectural baselines are naive executable crosses (`bid_A - ask_B > fees`) and z-score thresholds (`k * sigma_basis`). The isolated metric is AUC-PR for the label “still profitable after fees when the order arrives at latency L,” computed by C9 against exchange-time truth.

## 2) State of the art with opened sources

- **Detect tradable edge, not only statistical predictability.** Huth and Abergel report high-frequency lead-lag predictability, including about 60% accuracy for next midquote variation, but a naive market-order strategy does not profit after bid/ask spread. Source opened: arXiv API for `1111.7103`; also via `papers-microstructure.md`.
- **Use non-synchronous-safe features.** Hoffmann, Rosenbaum, and Yoshida estimate lead-lag from non-synchronous samples with a modified Hayashi-Yoshida covariation approach, warning by construction that tick alignment matters. Source opened: arXiv API for `1303.4871`; also via `papers-microstructure.md`.
- **Crypto leadership is regime-dependent.** Pascual et al. use Information Share, Permanent-Transitory decomposition, and Hayashi-Yoshida on crypto CEX/DEX and spot/futures settings; they find high-volatility periods can produce mixed futures-vs-spot leadership. Source opened: arXiv API for `2506.08718`; also via `papers-microstructure.md`.
- **Latency-race evidence requires failed-attempt visibility.** Aquilina, Budish, and O'Neill emphasize that full exchange message data reveal both race winners and losers, which ordinary order-book data cannot. P6 will not have that full evidence unless its simulator explicitly records unfilled/legged attempts. Source opened: BIS WP 955 page; also via `papers-microstructure.md`.
- **UNVERIFIED gap:** no opened source here validates a specific ML classifier for crypto cross-venue executable-cross detection. Any model-based detector should be presented as our ablation, not state-of-the-art fact.

## 3) Baseline we ship now

Ship three detector tiers behind one interface:

### Tier 1 — same asset across venues

For each instrument and ordered venue pair `(sell=A, buy=B)`:

`edge_bps = 10000 * (bid_A - ask_B) / mid_ref - fair_basis_bps(A,B)`

Emit an opportunity when:

- both quotes are fresh under `max_age_us`;
- `bid_A > ask_B` after applying fair basis;
- `edge_bps - taker_fees_bps - configured_safety_bps > 0`;
- executable size is positive: `min(bid_sz_A, ask_sz_B)`.

### Tier 2 — spot-perp basis

Detect spot/perp deviations after subtracting rolling fair basis and configured funding/carry assumptions. Emit separate direction fields so the simulator can distinguish spot buy/perp sell from perp buy/spot sell. Funding/carry numbers remain assumptions until verified sources exist.

### Tier 3 — correlated assets BTC/ETH

Start with a conservative z-score detector on the residual:

`resid = mid_ETH - beta_t * mid_BTC - alpha_t`

Use rolling or Kalman hedge ratio from C4/C6 model state. Emit only if the simulated two-leg or basket execution is available and fees are included. Mark this tier as stretch unless Tier 1 and Tier 2 evaluation are already stable.

Across all tiers, stale quotes are masked rather than forward-filled indefinitely; non-synchronous updates are handled through C3 quote ages and C4 fair basis. Episode start/end is defined on receive-time state transitions to avoid look-ahead.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| Executability-first labels | Train/tune thresholds against “profitable at latency L after fees” labels from C9, not raw crosses. | 5 | 3 | 5 | 5 | 5 | Directly addresses Huth-Abergel's predictability-vs-profitability pitfall. |
| Staleness-aware z-score | Threshold is `k * basis_sd + age_penalty + spread_penalty`, with penalties learned/tuned on held-out labels. | 4 | 3 | 5 | 5 | 4 | Simple, robust, and explains why old quotes are discounted. |
| Regime-gated detector tiers | Switch detector settings by volatility/liquidity regime and venue-leadership confidence. | 4 | 4 | 3 | 4 | 4 | Motivated by mixed leadership under stress in Pascual et al. |
| Kalman hedge-ratio BTC/ETH residual | Model correlated-asset opportunities through time-varying beta rather than fixed beta or raw ratio. | 4 | 3 | 3 | 4 | 3 | Good innovation, but execution and inventory complexity are higher. |

Top candidate: **Executability-first labels** because it is rigorous, easy to explain to judges, and connects detection directly to latency-aware PnL rather than superficial signal accuracy.

## 5) Isolated scalar metric

**AUC-PR for “profitable at latency L after fees.”**

For each emitted candidate at receive time `t`:

1. Use C9 to simulate IOC arrival at `t + L_order` on both legs using exchange-time truth.
2. Label positive if net realized bps after fees and unwind/legging loss is above zero.
3. Score detector confidence against this label across held-out days and latency grid points.
4. Report AUC-PR by tier and pair; PR is preferred because executable opportunities are rare and imbalanced.

Secondary metrics: false-positive rate per 10,000 events, median detected edge, realized capture ratio, and stale-quote rejection rate.

## 6) Risks

- **False crosses from stale quotes:** quote age must be a hard mask and a model feature.
- **Non-synchronous updates:** simultaneous venue states are trader beliefs, not exchange simultaneity; episode construction must use receive-time state.
- **Fee/funding uncertainty:** unverified fees or funding assumptions can flip labels; C11 must sweep fee tiers.
- **Class imbalance:** raw accuracy is meaningless; use PR curves and calibration.
- **Overlapping opportunities:** duplicated episodes can inflate sample size; cluster by instrument/pair and overlap window for evaluation.
- **Correlated-asset legging risk:** BTC/ETH residual trades are not pure arbitrage; keep them separate from same-asset crosses in reporting.
