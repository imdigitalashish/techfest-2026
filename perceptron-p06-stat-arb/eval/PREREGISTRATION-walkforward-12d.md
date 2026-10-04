# Pre-registration — walk-forward test of LEV vs the tuned per-pair threshold (12 held-out days)

- **Registered:** 2026-10-04 14:24 IST. This file's git commit is the evidence of the time; any later change is appended below as a dated amendment, never by editing this text.
- **Code:** commit `604f54d` (the parent of this registration commit). The final run must use these blobs unchanged:

| file | git blob |
|---|---|
| `eval/falsification.py` | `bb9dd8400c36` |
| `components/decision/autoresearch/rules.py` | `15aa319dab06` |
| `components/decision/autoresearch/build_cells.py` | `8d2d7b4381b6` |
| `components/detector/cross.py` | `a511eafaf5f6` |
| `components/sim/fills.py` | `2a1851b17e29` |
| `components/decision/policies.py` | `72e19e374ac0` |
| `components/decision/lev.py` | `ed7ed63f4a81` |
| `components/decay/survival.py` | `04c12a4c7125` |
| `components/costs/fees.py` | `37d1d5d4b57d` |
| `components/feed/normalize.py` | `e793e8bfd904` |
| `eval/run_baseline.py` | `1bbe6d57eecf` |

- **Data:** Tardis.dev free first-of-month `quotes` samples for 13 days, 2025-10-01 … 2026-10-01, and 5 BTC legs: binance BTCUSDT, binance-futures BTCUSDT, coinbase BTC-USD, okex BTC-USDT, okex-swap BTC-USDT-SWAP. Sizes and md5 are in `eval/results/data_manifest_wf12.tsv`, committed with this file.

## Hypothesis
H1: out of sample, the latency-conditioned executable-value model **LEV** earns more simulated P&L than the **tuned per-pair × cell threshold**, the strongest simple baseline found so far.

## Design (unchanged from the exploratory runs)
- For each consecutive pair of days (i−1, i), every policy is fitted on day i−1's simulator-labelled candidates and scored on day i. This gives **12 test days**, 2025-11-01 … 2026-10-01.
- **Cells:** taker fee ∈ {1, 2} bps per leg × one-way latency δ ∈ {1, 5, 20} ms. Order latency = feed latency = δ. Decision compute is 7 µs. The 0.05 BTC cap applies per arbitrage. IOC legs fill against exchange-time top of book at arrival; a mismatched leg is unwound on the same venue 2δ later. Detection uses the exchange clock with a 1 bp threshold over a 60 s EWMA fair basis.
- **Day score:** P&L summed over the 6 cells, in USD.
- **LEV:** HistGradientBoostingRegressor (max_iter 200, learning rate 0.05, other parameters default, random_state 0) on 13 features (`rules.LEARN_X`), target P&L bps clipped to ±30. Act iff predicted value > 0.
- **Threshold:** θ per (pair, fee, δ) chosen on the training day from {0, 0.25, 0.5, 1, 1.5, 2, 3, 5, 10} bps to maximise training P&L.

## Primary analysis and decision rule
- **Statistic:** Dᵢ = P&L_LEV,i − P&L_threshold,i over the 12 test days; report mean D.
- **Decision:** H1 is **supported** iff **both** of these 95% lower bounds are > 0: the two-sided paired t-interval of mean D, and the percentile bootstrap over days (10,000 resamples, seed 0). Otherwise the result is reported as **"not established — within noise"**. ADR 001 specified the bootstrap bound only; the t-interval is added because the percentile bootstrap is optimistic with few days.

## Secondary analyses (reported regardless; descriptive, no multiplicity correction)
- One-sided sign test and Wilcoxon signed-rank; median D; relative uplift (ΣD / ΣP&L_threshold).
- **Unseen subset:** the 7 test days never examined before this registration (2025-11-01 … 2026-05-01).
- Per-cell uplift.
- GBM classifier vs threshold; EV (Kaplan–Meier by pair) vs threshold; threshold vs naive.
- Ablation: LEV vs LEV with edge/pair/latency/fee features only.

## Disclosure of prior looks
Five of the twelve test days (2026-06-01 … 2026-10-01) were already examined in exploratory walk-forwards with the same design:
- `eval/results/falsification_walkforward_4d.md`: 4 test days, LEV − threshold +$248/day, t-CI [−$187, +$682];
- a 5-day run: +$238/day, t-CI [−$58, +$533], 5/5 days positive. It is being regenerated to `falsification_walkforward_5d` after a file mix-up.

The LEV features and hyperparameters were fixed on 2026-10-04 before any of these looks, and have not changed.

## Command
```
cd perceptron-p06-stat-arb && eval/run_guarded.sh .venv/bin/python -m eval.falsification walkforward \
  --days 2025-10-01 2025-11-01 2025-12-01 2026-01-01 2026-02-01 2026-03-01 2026-04-01 2026-05-01 2026-06-01 2026-07-01 2026-08-01 2026-09-01 2026-10-01 \
  --out falsification_walkforward_12d_prereg \
  --subset unseen7:2025-11-01,2025-12-01,2026-01-01,2026-02-01,2026-03-01,2026-04-01,2026-05-01
```
Outputs go to `eval/results/falsification_walkforward_12d_prereg.{md,json}`; the result is reported whatever it is.
