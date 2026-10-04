# Forecast-trust sweep (exploratory) — `eval/results/trust-v2` + `eval/results/mvp-v2`

The planner plans on trust × forecast: trust = 0 is the queue-only LP (`mpc-queue`), trust = 1 is `mpc-ewma`. L=1, P=10, seeds 200–229 (paired, CRN). Exploratory: no correction across the sweep.

| scenario | trust 0 | 0.25 | 0.5 | 0.75 | 1 | best | best − max(trust 0, trust 1) (pp) [95% CI] |
|---|---|---|---|---|---|---|---|
| drift | 0.9679 | 0.9867 | 0.9954 | 0.9962 | 0.9946 | mpc-ewma@trust=0.75 | +0.16 [+0.13, +0.18] |
| shock | 0.9549 | 0.9569 | 0.9563 | 0.9511 | 0.9430 | mpc-ewma@trust=0.25 | +0.20 [+0.17, +0.23] |
| shock+drift | 0.9284 | 0.9397 | 0.9434 | 0.9394 | 0.9321 | mpc-ewma@trust=0.5 | +1.13 [+1.05, +1.21] |
| shock+drift+spikes | 0.9251 | 0.9350 | 0.9380 | 0.9332 | 0.9256 | mpc-ewma@trust=0.5 | +1.24 [+1.16, +1.33] |
