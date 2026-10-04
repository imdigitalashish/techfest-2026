# Long-horizon summary — `eval/results/long-week-v2`

Scenario long-week · 7 simulated days (10080 steps) · 7 shocks per run · seeds [200, 201, 202, 203, 204, 205, 206, 207, 208, 209] (frozen, CRN) · units 40 · P=10 · L=1.

| policy | served fraction [95% CI over seeds] | lost per shock (120-step window) | recover steps | mean wait |
|---|---|---|---|---|
| greedy | 0.7242 [0.7185, 0.7296] | 713.0 | 112.3 | 3.71 |
| mpc-cusum-v1 | 0.9342 [0.9303, 0.9384] | 295.9 | 85.0 | 2.09 |
| mpc-ewma | 0.9356 [0.9315, 0.9398] | 290.3 | 84.4 | 2.10 |
| mpc-queue | 0.9306 [0.9273, 0.9340] | 261.1 | 66.7 | 3.06 |
| oracle | 0.9350 [0.9310, 0.9392] | 291.8 | 83.5 | 2.03 |
| reactive | 0.8722 [0.8682, 0.8763] | 422.0 | 110.8 | 3.40 |
| static | 0.7433 [0.7405, 0.7463] | 729.7 | 120.0 | 3.18 |

Best rule-based allocator (by mean): **reactive**

| comparison | Δ served (pp) [95% paired CI] | seeds won | Δ lost per shock | Wilcoxon p |
|---|---|---|---|---|
| mpc-cusum-v1 − reactive | +6.20 [+6.10, +6.29] | 10/10 | -126.1 | 0.00195 |
| mpc-ewma − reactive | +6.34 [+6.26, +6.43] | 10/10 | -131.7 | 0.00195 |
| mpc-queue − reactive | +5.84 [+5.72, +5.94] | 10/10 | -160.9 | 0.00195 |
| oracle − reactive | +6.27 [+6.18, +6.37] | 10/10 | -130.2 | 0.00195 |
| mpc-cusum-v1 − mpc-ewma | -0.14 [-0.17, -0.12] | 0/10 | +5.6 | 0.00195 |
| greedy − oracle | -21.08 [-21.77, -20.51] | 0/10 | +421.1 | 0.00195 |
| mpc-cusum-v1 − oracle | -0.08 [-0.11, -0.04] | 1/10 | +4.0 | 0.00586 |
| mpc-ewma − oracle | +0.07 [+0.02, +0.11] | 9/10 | -1.5 | 0.0195 |
| mpc-queue − oracle | -0.44 [-0.61, -0.31] | 0/10 | -30.7 | 0.00195 |
| reactive − oracle | -6.27 [-6.37, -6.18] | 0/10 | +130.2 | 0.00195 |
| static − oracle | -19.16 [-19.52, -18.89] | 0/10 | +437.8 | 0.00195 |

## Per-day served fraction (descriptive; 95% CI = bootstrap over whole seed trajectories)

| policy | d1 | d2 | d3 | d4 | d5 | d6 | d7 | whole-run mean [95% CI over seeds] |
|---|---|---|---|---|---|---|---|---|
| greedy | 0.910 | 0.914 | 0.869 | 0.760 | 0.634 | 0.517 | 0.466 | 0.7243 [0.7184, 0.7299] |
| mpc-cusum-v1 | 0.959 | 0.950 | 0.939 | 0.938 | 0.937 | 0.906 | 0.910 | 0.9343 [0.9303, 0.9384] |
| mpc-ewma | 0.960 | 0.951 | 0.941 | 0.939 | 0.938 | 0.907 | 0.912 | 0.9357 [0.9316, 0.9399] |
| mpc-queue | 0.967 | 0.960 | 0.947 | 0.934 | 0.924 | 0.891 | 0.891 | 0.9306 [0.9274, 0.9340] |
| oracle | 0.959 | 0.951 | 0.940 | 0.939 | 0.938 | 0.905 | 0.913 | 0.9350 [0.9310, 0.9393] |
| reactive | 0.906 | 0.899 | 0.886 | 0.878 | 0.870 | 0.834 | 0.832 | 0.8723 [0.8683, 0.8764] |
| static | 0.855 | 0.841 | 0.801 | 0.749 | 0.699 | 0.638 | 0.621 | 0.7434 [0.7406, 0.7465] |
