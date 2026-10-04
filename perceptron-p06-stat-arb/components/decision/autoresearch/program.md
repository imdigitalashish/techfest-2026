# Auto-research program — C8 decision spike (latency-aware act / skip)

**Goal.** Maximise the realised simulated P&L of *which* detected mispricings we act on, at a given end-to-end latency and fee level, on data the candidate has never seen.

**Metric (scalar, printed by the FROZEN `eval.py`).** The sum over six cells (taker fee per leg ∈ {1, 2} bps × one-way latency δ ∈ {1, 5, 20} ms) of validation-half P&L in USD, with a 0.05 BTC cap per arbitrage. Validation is 2026-09-01 12:00–24:00 UTC; training is 00:00–12:00 UTC. Five BTC legs from the Tardis free sample: binance spot, binance-futures perp, coinbase BTC-USD, okex BTC-USDT, okex-swap BTC-USDT-SWAP. Secondary metrics: trades, hit rate, mean bps, per-cell P&L, and the block-bootstrap SE of the total (hourly blocks).

**What the loop may change.** Only `candidate.py` (its `CONFIG` and/or code). It receives training rows *with* simulator labels (`pnl_usd`, `pnl_bps`, `outcome`) and validation rows *without* labels, and returns an act mask. Contract: `fit(train) -> model`, `act(model, rows) -> np.ndarray[bool]`. It must not read files.

**Keep rule.** Keep a change only if metric − best > the bootstrap SE of the new total; otherwise revert. Every run is appended to `results.tsv`.

**Fresh-holdout re-check (lead).** `eval.py --holdout` fits on all of 2026-09-01 and scores 2026-10-01, which the loop never uses, to catch metric gaming.

**Idea backlog** (ordered by prior):
1. Per-pair threshold θ*[pair, cell] (strong baseline).
2. EV with Kaplan–Meier survival by venue pair: act iff S(L)·net − (1 − S(L))·λ > 0.
3. EV with survival by pair × edge bucket.
4. λ scaling (risk aversion) ×{0.5, 2}.
5. Learned success probability (gradient-boosted classifier on features + L) × win/loss magnitudes.
6. Learned executable value (gradient-boosted regressor of P&L bps), "LEV".
7. Intersections: per-pair threshold ∧ EV > 0.
8. Next: confirmation delay Δ (needs the simulator in the loop), Hawkes/lead–lag features, compiled trees for µs inference.

**Constraints.** Decision compute must stay ≤ 10 µs per opportunity on the production path (numpy/compiled), and must be reported. No look-ahead: features are only those visible at decision time.
