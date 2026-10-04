# Realism scorecard (pre-registered E7): impact vs size, TWAP, synced twins

Seeds 100–129 (n = 30 per size, same seeds at every size); window volume V = 33904 shares (null twin). Peak impact = mean twin gap at T1 (end of execution).

| Q (shares) | Q/V | peak impact @T1 (¢) | 95% CI | decay ratio (T1+10 min / T1) |
|---|---|---|---|---|
| 1000 | 0.029 | +0.78 | [-1.23, +3.00] | -1.34 |
| 2000 | 0.059 | +1.57 | [-0.28, +3.52] | -1.70 |
| 4000 | 0.118 | +3.67 | [+1.82, +5.53] | -0.57 |
| 8000 | 0.236 | +6.77 | [+4.63, +8.95] | -0.49 |
| 16000 | 0.472 | +12.32 | [+9.35, +15.17] | -0.27 |

**δ = 1.006**, 95% paired-bootstrap CI [0.546, 1.760] (75% of resamples had positive impact at every size). Square-root law: δ ≈ 0.5. **Verdict (pre-registered rule): consistent with concave, square-root-like impact.**

**Post hoc (not pre-registered).** The rule above is lenient: it accepts any CI overlapping [0.3, 0.7]. Impact ratio per size doubling: ×2.00, ×2.34, ×1.85, ×1.82 (square-root law: ×1.41; linear: ×2). Slope over the sizes whose peak CI excludes 0 ([4000, 8000, 16000]): δ = 0.87, 95% CI [0.57, 1.35] (100% of draws valid). Twin gap 10 min after completion, ¢ (mean [95% CI]): 1000: -1.05 [-5.05, +2.07], 2000: -2.67 [-6.80, +0.83], 4000: -2.08 [-8.70, +2.78], 8000: -3.28 [-9.10, +1.18], 16000: -3.28 [-7.73, +0.35].
