# Trust designs — exploratory preview on TUNING seeds 0–9 (Addendum B1 design space; test seeds 300–329 untouched)

L=1, P=10, 1440 steps, abandonment-aware LP, highspy. Served fraction mean over 10 tuning seeds; Δ vs the best fixed global trust (0.5) with paired bootstrap CI.

## shock

| policy | served | Δ vs trust 0.5 (pp) [95% CI] | seeds better |
|---|---|---|---|
| mpc-gated@scope=1,tau_shock=0.25,tau_quiet=0.5 | 0.9654 | +0.02 [-0.03, +0.06] | 6/10 |
| mpc-ewma@trust=0.5 | 0.9652 | +0.00 [+0.00, +0.00] | 0/10 |
| mpc-unctrust@kappa=1 | 0.9650 | -0.02 [-0.07, +0.03] | 6/10 |
| mpc-unctrust@kappa=0.5 | 0.9634 | -0.18 [-0.22, -0.14] | 0/10 |
| mpc-queue | 0.9629 | -0.22 [-0.35, -0.10] | 2/10 |
| mpc-gated@scope=1,tau_shock=0.5,tau_quiet=0.75 | 0.9616 | -0.36 [-0.43, -0.28] | 0/10 |
| mpc-unctrust@kappa=0.25 | 0.9607 | -0.45 [-0.54, -0.36] | 0/10 |
| mpc-ewma | 0.9526 | -1.26 [-1.44, -1.06] | 0/10 |

## shock+drift

| policy | served | Δ vs trust 0.5 (pp) [95% CI] | seeds better |
|---|---|---|---|
| mpc-ewma@trust=0.5 | 0.9437 | +0.00 [+0.00, +0.00] | 0/10 |
| mpc-gated@scope=1,tau_shock=0.25,tau_quiet=0.5 | 0.9432 | -0.05 [-0.11, -0.00] | 2/10 |
| mpc-unctrust@kappa=0.5 | 0.9422 | -0.15 [-0.21, -0.09] | 1/10 |
| mpc-unctrust@kappa=1 | 0.9417 | -0.20 [-0.24, -0.16] | 0/10 |
| mpc-gated@scope=1,tau_shock=0.5,tau_quiet=0.75 | 0.9413 | -0.24 [-0.28, -0.20] | 0/10 |
| mpc-unctrust@kappa=0.25 | 0.9403 | -0.34 [-0.40, -0.27] | 0/10 |
| mpc-ewma | 0.9339 | -0.98 [-1.12, -0.85] | 0/10 |
| mpc-queue | 0.9277 | -1.60 [-1.80, -1.42] | 0/10 |

