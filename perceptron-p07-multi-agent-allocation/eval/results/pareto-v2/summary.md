# Service vs movement (Pareto) — `eval/results/pareto-v2` + shock rows of `eval/results/mvp-v2`

Scenario shock, seeds 200–229 (paired with mvp-v2), L=1, P=10. `@c_move=x` = planner move-cost weight (default 0.05). Sorted by empty repositioning hops per served request.

| policy | served fraction | empty hops / served | lost per shock |
|---|---|---|---|
| mpc-queue@c_move=0.5 | 0.9096 | 0.250 | 378.5 |
| mpc-ewma@c_move=1.0 | 0.9046 | 0.315 | 427.4 |
| greedy | 0.9057 | 0.326 | 404.5 |
| mpc-queue | 0.9549 | 0.381 | 235.0 |
| mpc-ewma@c_move=0.5 | 0.9373 | 0.413 | 320.5 |
| mpc-ewma@c_move=0.2 | 0.9424 | 0.459 | 300.7 |
| oracle | 0.9418 | 0.481 | 302.6 |
| mpc-cusum-v1 | 0.9417 | 0.489 | 305.3 |
| mpc-ewma | 0.9430 | 0.511 | 297.3 |
| static | 0.8642 | 0.512 | 573.5 |
| reactive | 0.8996 | 0.585 | 426.2 |
| mpc-myopic | 0.9337 | 0.603 | 339.9 |

| comparison | Δ served (pp) [95% CI] | seeds won | Wilcoxon p | Δ empty hops / served |
|---|---|---|---|---|
| mpc-ewma@c_move=0.5 − reactive | +3.77 [+3.55, +4.00] | 30/30 | 1.9e-09 | -0.172 |
| mpc-ewma@c_move=0.5 − greedy | +3.16 [+2.76, +3.59] | 30/30 | 1.9e-09 | +0.087 |
| mpc-queue − greedy | +4.92 [+4.52, +5.35] | 30/30 | 1.9e-09 | +0.054 |
| mpc-ewma@c_move=1.0 − greedy | -0.10 [-0.34, +0.14] | 10/30 | 0.26 | -0.012 |
| mpc-queue@c_move=0.5 − greedy | +0.39 [+0.13, +0.65] | 19/30 | 0.0062 | -0.076 |
