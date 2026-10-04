# NYC TLC real-trace replay — `eval/results/nyc-v2b`

July 10–11 2025 (train July 8–9) yellow-taxi trips, Manhattan-internal, thinned to ~10 requests/min; 20 thinning replicates (seeds 200–219); K=40, P=10, L=1; mean arrivals per run 28743. Event window = July 4 21:30–23:30 (the largest observed surge, 20.7x in one cell 22:00–22:30; cause UNVERIFIED). `oracle` here is a retrospective 15-min centred smoother of realised demand (hindsight), not a forecast-value bound.

| policy | served_frac | lost_frac | mean_wait | empty_per_srv | pending_frac |
|---|---|---|---|---|---|
| greedy | 0.9605 | 0.0364 | 2.3080 | 0.2494 | 0.0031 |
| mpc-cusum-v1 | 0.9995 | 0.0001 | 0.5528 | 0.3334 | 0.0004 |
| mpc-ewma | 0.9995 | 0.0000 | 0.5312 | 0.3425 | 0.0004 |
| mpc-queue | 0.9958 | 0.0028 | 1.6311 | 0.2529 | 0.0014 |
| oracle | 0.9997 | 0.0000 | 0.5130 | 0.3319 | 0.0003 |
| reactive | 0.9843 | 0.0149 | 1.1524 | 0.3628 | 0.0007 |
| static | 0.9570 | 0.0410 | 1.6202 | 0.3177 | 0.0020 |

Best rule by mean: **reactive**

| comparison | Δ served (pp) [95% paired CI] | replicates won | Wilcoxon p | Δ event lost [95% CI] |
|---|---|---|---|---|
| mpc-ewma − reactive | +1.52 [+1.43, +1.59] | 20/20 | 1.9e-06 | — |
| mpc-queue − reactive | +1.14 [+1.07, +1.21] | 20/20 | 1.9e-06 | — |
| mpc-cusum-v1 − mpc-ewma | -0.00 [-0.01, +0.01] | 6/20 | 0.53 | — |
| mpc-queue − mpc-ewma | -0.37 [-0.41, -0.35] | 0/20 | 1.9e-06 | — |
| oracle − mpc-ewma | +0.02 [+0.01, +0.02] | 18/20 | 0.00029 | — |
