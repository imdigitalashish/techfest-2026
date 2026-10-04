# Summary — `eval/results/p3-v1`

Episodes: 25 · seeds per cell: 5–5 · horizon: 1440 steps · units: 40

Mean [95% bootstrap CI] over seeds; IQM in the last column of each block. Paired tests pair episodes by seed (common random numbers).

## shock

| policy | served_frac | lost_frac | mean_wait | empty_per_srv | shock_lost | shock_served | recover_steps | IQM served |
|---|---|---|---|---|---|---|---|---|
| greedy | 0.8017 [0.7845, 0.8145] | 0.1979 [0.1851, 0.2152] | 1.23 [1.211, 1.253] | 0.375 [0.3665, 0.3836] | 633.8 [567.6, 691.4] | 0.7032 [0.679, 0.7282] | 120 [120, 120] | 0.8057 |
| mpc-cusum-v1 | 0.889 [0.8798, 0.8988] | 0.1109 [0.101, 0.1201] | 0.8223 [0.8111, 0.8316] | 0.5657 [0.5633, 0.5682] | 511.4 [461.2, 557.8] | 0.7594 [0.7397, 0.779] | 120 [120, 120] | 0.8883 |
| mpc-ewma | 0.8891 [0.8796, 0.8988] | 0.1107 [0.1011, 0.1204] | 0.8396 [0.8262, 0.8534] | 0.5952 [0.5905, 0.6001] | 511.2 [463.6, 561.8] | 0.7599 [0.7386, 0.7775] | 120 [120, 120] | 0.8889 |
| oracle | 0.8899 [0.8804, 0.8998] | 0.1099 [0.09998, 0.1194] | 0.8055 [0.781, 0.8249] | 0.5506 [0.5445, 0.555] | 517.4 [464.4, 567.2] | 0.7573 [0.7351, 0.7781] | 120 [120, 120] | 0.8889 |
| reactive | 0.7827 [0.7749, 0.7913] | 0.2171 [0.2085, 0.225] | 0.6333 [0.6233, 0.645] | 0.6238 [0.6108, 0.6351] | 701.4 [656.6, 747.2] | 0.6729 [0.6549, 0.6874] | 120 [120, 120] | 0.7819 |

Reference (best rule-based by mean served_frac): **greedy**

| policy vs ref | metric | mean diff [95% paired CI] | win-rate | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| mpc-cusum-v1 | served_frac | +0.08729 [+0.07104, +0.107] | 1.00 | 0.062 | 1 |
| mpc-cusum-v1 | lost_frac | -0.08707 [-0.1069, -0.07065] | 1.00 | 0.062 | 1 |
| mpc-cusum-v1 | mean_wait | -0.4074 [-0.433, -0.3818] | 1.00 | 0.062 | 1 |
| mpc-cusum-v1 | empty_per_srv | +0.1907 [+0.1806, +0.2007] | 0.00 | 0.062 | 1 |
| mpc-cusum-v1 | shock_lost | -122.4 [-176.4, -61.2] | 0.80 | 0.12 | 1 |
| mpc-cusum-v1 | shock_served | +0.05625 [+0.02698, +0.08289] | 0.80 | 0.12 | 1 |
| mpc-cusum-v1 | recover_steps | +0 [+0, +0] | 0.00 | 1 | 1 |
| mpc-ewma | served_frac | +0.08743 [+0.07039, +0.1081] | 1.00 | 0.062 | 1 |
| mpc-ewma | lost_frac | -0.0872 [-0.108, -0.06998] | 1.00 | 0.062 | 1 |
| mpc-ewma | mean_wait | -0.3901 [-0.4144, -0.3658] | 1.00 | 0.062 | 1 |
| mpc-ewma | empty_per_srv | +0.2202 [+0.212, +0.2284] | 0.00 | 0.062 | 1 |
| mpc-ewma | shock_lost | -122.6 [-183.2, -53.4] | 0.80 | 0.12 | 1 |
| mpc-ewma | shock_served | +0.05668 [+0.02596, +0.0839] | 0.80 | 0.12 | 1 |
| mpc-ewma | recover_steps | +0 [+0, +0] | 0.00 | 1 | 1 |
| oracle | served_frac | +0.08824 [+0.0723, +0.108] | 1.00 | 0.062 | 1 |
| oracle | lost_frac | -0.08805 [-0.1079, -0.07197] | 1.00 | 0.062 | 1 |
| oracle | mean_wait | -0.4241 [-0.4571, -0.3896] | 1.00 | 0.062 | 1 |
| oracle | empty_per_srv | +0.1756 [+0.165, +0.1861] | 0.00 | 0.062 | 1 |
| oracle | shock_lost | -116.4 [-172, -49.8] | 0.80 | 0.12 | 1 |
| oracle | shock_served | +0.05415 [+0.02353, +0.07986] | 0.80 | 0.12 | 1 |
| oracle | recover_steps | +0 [+0, +0] | 0.00 | 1 | 1 |
| reactive | served_frac | -0.01895 [-0.03443, +0.001114] | 0.20 | 0.12 | 1 |
| reactive | lost_frac | +0.01915 [-0.0009382, +0.03469] | 0.20 | 0.12 | 1 |
| reactive | mean_wait | -0.5964 [-0.6202, -0.5725] | 1.00 | 0.062 | 1 |
| reactive | empty_per_srv | +0.2488 [+0.2324, +0.2651] | 0.00 | 0.062 | 1 |
| reactive | shock_lost | +67.6 [+10.4, +132.6] | 0.20 | 0.12 | 1 |
| reactive | shock_served | -0.03031 [-0.05848, -0.003768] | 0.20 | 0.19 | 1 |
| reactive | recover_steps | +0 [+0, +0] | 0.00 | 1 | 1 |
