# C4 fair_value — fair basis and lead-lag

## 1) Contract summary

C4 consumes `StateFrame` from C3 and emits:

- `BasisFrame(ts_us, pair, basis_bps, basis_sd_bps)` for USD/USDT, spot/perp, and venue-pair fair differences.
- `LeadLag(pair, lag_us, xcorr)` describing which venue/instrument leads and by how much.

Downstream, C6 uses this basis to distinguish executable mispricing from normal venue/product basis. The architecture baseline is a 60 s rolling median of `(mid_A - mid_B) / mid`; candidate upgrades are Kalman/local-level basis, Hayashi-Yoshida lead-lag, and micro-price fair value. The isolated scalar metric is out-of-sample RMSE, in bps, of the next-100 ms mid-difference forecast.

## 2) State of the art with opened sources

- **Non-synchronous lead-lag is a first-class statistical problem, not a resampling detail.** Hoffmann, Rosenbaum, and Yoshida model lead-lag as a time shift theta such that `(X_t, Y_{t+theta})` is a semimartingale, and estimate it from randomly sampled non-synchronous data using contrast optimization based on a modified Hayashi-Yoshida covariation estimator; the convergence rate depends on sampling sparsity. Source opened: arXiv API for `1303.4871`; also summarized via `papers-microstructure.md`.
- **Crypto price-discovery work uses the same stack P6 needs.** Pascual, Rubio, Cebada, and Veciana analyze ETH CEX-vs-DEX and BTC spot-vs-futures price discovery using Hasbrouck Information Share, Gonzalo-Granger Permanent-Transitory decomposition, and Hayashi-Yoshida; they report CEX leadership for ETH and generally futures-leading-spot for BTC, but mixed outcomes in high-volatility periods. Source opened: arXiv API for `2506.08718`; also via `papers-microstructure.md`.
- **Lead-lag can predict but still fail to trade.** Huth and Abergel find asymmetric high-frequency cross-correlations, liquidity-driven leadership, and about 60% directional accuracy for predicting a lagger's next midquote move from a leader, yet a naive market-order strategy cannot profit because of the bid/ask spread. Source opened: arXiv API for `1111.7103`; also via `papers-microstructure.md`.
- **Latency races set a useful scale anchor.** Aquilina, Budish, and O'Neill use full exchange message data and find equity latency-arbitrage races are frequent, very fast, and materially affect effective spread and price impact. Source opened: BIS working-paper landing page for WP 955; numbers also via `papers-microstructure.md`.
- **UNVERIFIED gap:** no source opened here gives a clean sub-second CEX-CEX crypto basis half-life or a production-ready micro-price formula validated across crypto venues. We should label any such claim as a P6 measurement, not literature fact.

## 3) Baseline we ship now

Ship a deterministic, as-of-only fair-value module:

1. For each pair `(A, B)`, compute each venue/product mid as `(bid + ask) / 2` only when both sides are present and quote age is within C3's `max_age_us`.
2. Compute raw basis in bps: `10000 * (mid_A - mid_B) / ((mid_A + mid_B) / 2)`.
3. Estimate `basis_bps` as a rolling median over the previous 60 s on the receive-time clock; estimate `basis_sd_bps` with rolling MAD scaled to sigma.
4. Emit a simple lead-lag diagnostic by receive-time cross-correlation over a bounded lag grid, but label it `diagnostic_xcorr`, not the trading signal, because naive grid correlation is vulnerable to non-synchronous-tick bias.
5. For spot/perp, keep funding-rate and carry terms as configurable assumptions until verified fee/funding sources exist.

This baseline is robust, demoable, and aligns with the architecture contract while avoiding look-ahead.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| Asynchronous HY lead-lag map | Estimate pair-specific lead-lag with a Hayashi-Yoshida-style non-synchronous covariation grid, then expose a live venue-leadership heatmap. | 4 | 4 | 3 | 4 | 5 | Strongly aligned with opened sources; protects against Epps/resampling bias. |
| Kalman/local-level basis | Treat fair basis as latent state with observation noise from spread, quote age, and venue reliability; output basis and uncertainty. | 5 | 3 | 4 | 5 | 4 | Directly improves C6 thresholds and explains confidence. |
| Micro-price efficient-price blend | Replace plain mid with size-weighted micro-price per venue, then combine venues by inverse spread/age/liquidity weights. | 4 | 2 | 5 | 5 | 4 | Easy to implement and ablate; literature source for formula not opened, so mark model choice as engineering baseline. |
| Regime-switching leader | Let leadership switch by volatility/liquidity regime rather than using one static lead-lag. | 4 | 4 | 3 | 4 | 4 | Motivated by Pascual et al.'s mixed high-volatility findings. |

Top candidate: **Kalman/local-level basis** because it directly improves the contract metric, produces uncertainty for C6, and is feasible without needing proprietary message data.

## 5) Isolated scalar metric

**OOS RMSE of next-100 ms mid-difference forecast, bps.**

For each pair and held-out day:

- At time `t`, predict `raw_basis_bps(t + 100 ms)` using only information received by `t`.
- Score `sqrt(mean((prediction - realized_basis)^2))` after masking stale quotes.
- Report per-pair RMSE and a size-weighted aggregate.
- Add secondary diagnostics: calibration of `basis_sd_bps` and sign accuracy, but do not optimize on them.

## 6) Risks

- **Look-ahead leakage:** exchange-time joins can accidentally use updates not yet received; C4 must consume only C3's as-of receive-time state.
- **Clock skew:** cross-venue timestamp errors can masquerade as lead-lag; use receive-time diagnostics unless exchange clocks are corrected.
- **Non-synchronous bias:** naive resampling can create or erase lead-lag; HY-style estimates should be the rigorous path.
- **Overfitting basis windows:** selecting window length on the test day inflates performance; tune on training days only.
- **Funding/carry assumptions:** spot/perp fair value needs verified funding and borrow terms; mark missing inputs as assumptions.
