# NYC TLC real-trace replay — `eval/results/nyc-v2`

July 3–4 2025 yellow-taxi trips, Manhattan-internal, thinned to ~10 requests/min (q ≈ 0.20); train days July 1–2; 20 thinning replicates (seeds 200–219); K=40, P=10, L=1; mean arrivals per run 28775. Event window = July 4 21:30–23:30 (the largest observed surge, 20.7x in one cell 22:00–22:30; cause UNVERIFIED). `oracle` here is a retrospective 15-min centred smoother of realised demand (hindsight), not a forecast-value bound.

| policy | served_frac | lost_frac | mean_wait | empty_per_srv | event_lost | event_served | pending_frac |
|---|---|---|---|---|---|---|---|
| greedy | 0.9526 | 0.0449 | 2.4754 | 0.2518 | 111.9 | 0.9114 | 0.0025 |
| mpc-cusum-v1 | 0.9978 | 0.0016 | 0.7663 | 0.3531 | 1.8 | 0.9950 | 0.0006 |
| mpc-ewma | 0.9981 | 0.0015 | 0.7389 | 0.3640 | 1.4 | 0.9962 | 0.0004 |
| mpc-queue | 0.9934 | 0.0051 | 1.8532 | 0.2640 | 22.9 | 0.9779 | 0.0015 |
| oracle | 0.9981 | 0.0016 | 0.7097 | 0.3533 | 0.3 | 0.9972 | 0.0003 |
| reactive | 0.9729 | 0.0264 | 1.5286 | 0.3938 | 39.5 | 0.9700 | 0.0007 |
| static | 0.9360 | 0.0624 | 2.0154 | 0.3308 | 218.1 | 0.8475 | 0.0016 |

Best rule by mean: **reactive**

| comparison | Δ served (pp) [95% paired CI] | replicates won | Wilcoxon p | Δ event lost [95% CI] |
|---|---|---|---|---|
| mpc-ewma − reactive | +2.52 [+2.39, +2.67] | 20/20 | 1.9e-06 | -38.1 [-42.4, -33.9] |
| mpc-queue − reactive | +2.05 [+1.92, +2.20] | 20/20 | 1.9e-06 | -16.7 [-21.3, -12.0] |
| mpc-cusum-v1 − mpc-ewma | -0.03 [-0.04, -0.02] | 1/20 | 0.00016 | +0.3 [-0.1, +0.9] |
| mpc-queue − mpc-ewma | -0.47 [-0.52, -0.42] | 0/20 | 1.9e-06 | +21.4 [+18.7, +24.2] |
| oracle − mpc-ewma | -0.00 [-0.01, +0.01] | 10/20 | 0.65 | -1.1 [-1.6, -0.5] |
