# E6: pre-registered H1 verdict (fresh test seeds 1060–1259, synced twins)

Integrity: n seeds 200, pre-window identical True, all filled True

H1: mean paired ΔIS (IA_sched_only − TWAP) < 0, one-sided α = 0.05 (bootstrap 95th percentile < 0). Secondary: Δ own impact < 0.

| policy | metric | mean Δ vs TWAP (bps) | one-sided 95% upper bound | two-sided 95% CI | P(boot mean ≥ 0) |
|---|---|---|---|---|---|
| IA_sched_only | is_bps | -0.0340 | -0.0160 | [-0.0563, -0.0127] | 0.0006 |
| IA_sched_only | own_impact_bps | -0.0414 | -0.0239 | [-0.0629, -0.0204] | 0.0001 |
| IA_sched_only | instant_bps | -0.0001 | +0.0032 | [-0.0039, +0.0039] | 0.4808 |
| IA_sched_only | drift_bps | +0.0075 | +0.0143 | [-0.0007, +0.0156] | 0.9621 |
| IA_full | is_bps | -0.0151 | +0.0107 | [-0.0441, +0.0161] | 0.1606 |
| IA_full | own_impact_bps | +0.0008 | +0.0254 | [-0.0262, +0.0304] | 0.5126 |
| IA_full | instant_bps | -0.0422 | -0.0386 | [-0.0470, -0.0381] | 0.0000 |
| IA_full | drift_bps | +0.0263 | +0.0336 | [+0.0177, +0.0351] | 1.0000 |
| VWAP | is_bps | -0.0159 | +0.0039 | [-0.0403, +0.0076] | 0.0940 |
| VWAP | own_impact_bps | -0.0137 | +0.0057 | [-0.0373, +0.0095] | 0.1217 |
| VWAP | instant_bps | -0.0005 | +0.0027 | [-0.0045, +0.0033] | 0.4001 |
| VWAP | drift_bps | -0.0016 | +0.0002 | [-0.0039, +0.0006] | 0.0767 |

**H1 CONFIRMED**: ΔIS = -0.0340 bps, one-sided 95% upper bound -0.0160; win rate 52%; TWAP mean IS -0.198 bps.
