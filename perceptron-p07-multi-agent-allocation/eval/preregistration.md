# Pre-registration — confirmatory evaluation `mvp-v2` (written 2026-10-04 10:15 IST, before any run on seeds 200–229)

**Why.** The hostile-judge review (reviews/2026-10-04-abstract-v0.2-rubber-duck.md) showed two problems with mvp-v1: the "best rule" reference was chosen on the same test seeds, and only uncorrected p-values were headlined. This file fixes the protocol *before* the confirmatory data exist. It is committed (git timestamp) before `eval/results/mvp-v2` is created.

## Fixed design
- **Test seeds:** 200–229 (30 seeds, never used before). Tuning and ratchet seeds: 0–99. Earlier test seeds: 100–119.
- **Scenarios** (1440 steps = 1 simulated day, K=40 units, P=10, L=1): stationary, shock, drift, shock+drift, spikes, shock+drift+spikes.
- **Planner (all MPC variants):** abandonment-aware LP backlog (ρ = 1 − 1/P), HiGHS warm-start backend; H=6 unless stated. Code at the commit containing this file.
- **Common random numbers:** every policy replays the identical pre-sampled request stream per (scenario, seed).

## Reference rule per scenario (chosen on tuning seeds 0–19 — `eval/results/tuning-rules`)
| scenario | reference rule | its tuning-seed served fraction |
|---|---|---|
| stationary | greedy | 0.9771 |
| shock | greedy | 0.9156 |
| drift | reactive | 0.9351 |
| shock+drift | reactive | 0.8736 |
| spikes | greedy | 0.9726 |
| shock+drift+spikes | reactive | 0.8615 |

## Primary hypothesis (one family, Holm-corrected over the 6 scenarios)
- **H-primary:** `mpc-ewma` (look-ahead MPC with a deseasonalised EWMA forecast) has a higher served fraction than the scenario's reference rule.
- **Test:** paired by seed; mean difference with a 95% paired-bootstrap CI (10 000 resamples); two-sided Wilcoxon signed-rank; Holm across the 6 scenarios.
- **Pre-specified claim scope:** the MVP claim ("beats the rule baseline when demand suddenly shifts") rests on the **shock**, **shock+drift** and **shock+drift+spikes** rows.

## Secondary comparisons (reported with CIs; Holm within each family; exploratory, not used for the MVP claim)
- **S1, look-ahead ablations** (same LP and solver):
  - `mpc-myopic` (H = L+1) vs `mpc-ewma`: value of horizon.
  - `mpc-queue` (no demand forecast, queue only) vs `mpc-ewma`: value of the demand forecast.
- **S2, spike:** `mpc-cusum-v1` vs `mpc-ewma`. Served fraction overall, and requests lost in the 120 steps after each shock onset.
- **S3, forecast-value bound:** `oracle` (MPC fed the true expected rates — a perfect *forecast*, not a hindsight optimum or upper bound) vs `mpc-ewma`.
- **S4, cost of movement:** empty hops per served request for every policy. A separate Pareto run (`mpc-ewma@c_move ∈ {0.05, 0.2, 0.5, 1.0}`, shock scenario) traces service vs movement.

## Reporting rules
- Report every comparison above, whichever way it comes out. No seed is dropped.
- Recovery time is right-censored at 120 steps. Report the fraction of shocks recovered within 120 steps alongside the censored mean.
- Effect sizes in percentage points of served fraction; win counts over 30 seeds.
- Anything outside this list is labelled *exploratory*.
