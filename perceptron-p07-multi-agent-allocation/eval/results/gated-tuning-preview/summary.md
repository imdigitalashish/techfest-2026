# Gated-trust preview on TUNING seeds 0–9 (exploratory; test seeds untouched — eval/preregistration.md Addendum B)

L=1, P=10, 1440 steps, abandonment-aware LP. `mpc-gated@tau_shock=a,tau_quiet=b` plans on a×forecast in zones with a recent CUSUM alarm (self or neighbour, last 60 steps) and b×forecast elsewhere. Served fraction (mean over 10 tuning seeds).

## shock

| policy | served |
|---|---|
| mpc-ewma@trust=0.25 | 0.9653 |
| mpc-ewma@trust=0.5 | 0.9652 |
| mpc-gated@tau_shock=0.25,tau_quiet=0.5 | 0.9651 |
| mpc-gated@tau_shock=0,tau_quiet=0.5 | 0.9646 |
| mpc-queue | 0.9629 |
| mpc-ewma@trust=0.75 | 0.9606 |
| mpc-gated@tau_shock=0.25,tau_quiet=0.75 | 0.9600 |
| mpc-gated@tau_shock=0,tau_quiet=0.75 | 0.9597 |
| mpc-ewma | 0.9526 |
| mpc-gated@tau_shock=0,tau_quiet=1 | 0.9525 |
| mpc-gated@tau_shock=0.25,tau_quiet=1 | 0.9523 |

mpc-ewma@trust=0.25 − mpc-queue: +0.23 pp [+0.14, +0.31] (9/10)

mpc-ewma@trust=0.25 − mpc-ewma@trust=0.25: +0.00 pp [+0.00, +0.00] (0/10)

## shock+drift

| policy | served |
|---|---|
| mpc-gated@tau_shock=0.25,tau_quiet=0.5 | 0.9438 |
| mpc-ewma@trust=0.5 | 0.9437 |
| mpc-gated@tau_shock=0,tau_quiet=0.5 | 0.9434 |
| mpc-gated@tau_shock=0.25,tau_quiet=0.75 | 0.9407 |
| mpc-gated@tau_shock=0,tau_quiet=0.75 | 0.9406 |
| mpc-ewma@trust=0.75 | 0.9403 |
| mpc-ewma@trust=0.25 | 0.9397 |
| mpc-ewma | 0.9339 |
| mpc-gated@tau_shock=0,tau_quiet=1 | 0.9338 |
| mpc-gated@tau_shock=0.25,tau_quiet=1 | 0.9337 |
| mpc-queue | 0.9277 |

mpc-gated@tau_shock=0.25,tau_quiet=0.5 − mpc-ewma: +0.99 pp [+0.87, +1.12] (10/10)

mpc-gated@tau_shock=0.25,tau_quiet=0.5 − mpc-ewma@trust=0.5: +0.01 pp [-0.02, +0.04] (6/10)

