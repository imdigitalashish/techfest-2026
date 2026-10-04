# Falsification test 3 — clock skew and receive-time replay

Train 2026-09-01 → test 2026-10-01, 5 BTC legs. `exch`: exchange clock (baseline). `recv`: detection on the Tardis collector receive clock (real feed latency) with order latency δ. `skewN`: per-venue exchange-clock offsets ~ U(±5 ms), seed N, applied to detection and to fill truth on both days.

| variant | test episodes | median lifetime (ms) | S(10 ms) | pair half-life Spearman vs exch | threshold P&L | EV P&L | LEV P&L | LEV − threshold |
|---|---|---|---|---|---|---|---|---|
| exch | 102,075 | 34.9 | 0.702 | 1.000 | 1,175 | 1,169 | 1,342 | +166 |
| recv | 98,282 | 41.9 | 0.691 | 0.984 | 442 | -415 | 703 | +261 |
| skew0 | 100,459 | 35.2 | 0.730 | 0.995 | 1,272 | 1,226 | 1,436 | +164 |
| skew1 | 102,728 | 34.6 | 0.695 | 0.988 | 1,354 | 1,349 | 1,460 | +106 |
| skew2 | 100,622 | 34.6 | 0.698 | 0.992 | 1,154 | 1,131 | 1,298 | +145 |

Runtime 3778 s · commit `b7a857a` · `python -m eval.falsification clockskew`

**Provenance note.** This run started at 08:33 IST from an uncommitted working tree on top of `b7a857a`. `eval/falsification.py` was first committed in the commit that adds this file. Later edits (a `lev_edge_only` ablation policy, and t-intervals/sign tests for the walk-forward) do not touch the clock-skew path except to add one extra policy column. Re-run with `nice -n 10 .venv/bin/python -m eval.falsification clockskew` (≈1 h on the M5 under load; cells cache in `.cache/falsification/`).

**Reading.** Pair half-life *rankings* are stable under ±5 ms per-venue clock offsets and under receive-time replay: Spearman ≥ 0.984 against the exchange-clock baseline. In all five variants LEV keeps a positive uplift over the tuned per-pair threshold (+$106 to +$261 summed over the 6 cells). The survival-EV rule does **not** survive receive-time replay: −$415 against the threshold's +$442.
