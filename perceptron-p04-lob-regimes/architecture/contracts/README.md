# Contracts

The executable contracts are the dataclasses in [`components/contracts.py`](../../components/contracts.py). This page restates them as language-neutral schemas so any component can be re-implemented (e.g. in C++/Rust for the latency stretch) and swapped behind the same seam.

## `BookDay` (C1 → C2)
| field | type | shape | meaning |
|---|---|---|---|
| symbol | str | — | e.g. `BTCUSDT` |
| day | str | — | UTC date `YYYY-MM-DD` |
| recv_us | int64 | (n,) | receive time, µs since epoch, non-decreasing (asserted) |
| exch_us | int64 | (n,) | exchange time, diagnostics only |
| bid_px, ask_px | float64 | (n, L) | level 0 = best; L = 5 |
| bid_sz, ask_sz | float64 | (n, L) | base-asset quantity |

## `FeatureFrame` (C2 → C4, C6)
| field | type | shape | invariant |
|---|---|---|---|
| step_us | int | — | grid spacing (1 000 000) |
| grid_us | int64 | (T,) | decision times |
| names | tuple[str] | (d,) | feature names (17 today) |
| X | float64 | (T, d) | row t depends only on messages with recv_us ≤ grid_us[t] (tested) |
| mid, spread_ticks | float64 | (T,) | as-of the grid time |

## `Labels` (C3 → C7, C8)
| field | type | shape | invariant |
|---|---|---|---|
| h_steps | int | — | horizon in grid steps (10) |
| y | float64 | (T,) | 1 up, 0 down, NaN tie or beyond the day |
| avail_step | int64 | (T,) | = t + h; C7 may consume y[t] only at steps ≥ avail_step[t] (tested) |
| move_bps | float64 | (T,) | signed mid move, basis points |

## `Alarm` (C6 → C7, C8)
`{step: int, detector: str, statistic: float, detail: {feature?: str, ...}}`

## `EpisodeResult` (C7 → C8, C9)
`{policy: str, day: str, p_up: float64[T], alarms: Alarm[], step_ns: int64[T], extra: {pred_ns: int64[T], w_trace: float64[T/60, K], head_names: str[]}}`

## Head interface (C5)
`predict(z: float64[d]) -> float` · `predict_batch(Z) -> float64[T]` · `sgd_update(z, y, lr, l2, prior)` · `refit_towards(Z, y, prior, lam)` · `fit(Z, y, C)`. Any head (GBDT, DeepLOB-style CNN, TLOB) that implements these five methods plugs into C7 unchanged.

## Policy spec (C7)
A dict: `{norm: static|ewma, heads: [(kind, params...)], combine: single|gate|fixed_share, detectors: [ks|ph], on_alarm: [refit|boost]}`. Policies are data (`components/adapter/POLICIES`), so the auto-research loop adds candidates without touching the loop.
