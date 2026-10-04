# Independent code, evaluation, and reproduction review (2026-10-04)

Reviewed the project at `416aaa2` and concurrent E8/E7/E9 follow-ups
`892b97e`/`fe782e1`, with ABIDES pinned at `f9cbe51`, Python 3.11.14,
NumPy 2.2.6, pandas 2.3.3, and SciPy 1.17.0. This is a review of the
implementation and committed experiments, not another full 200-seed simulation.
The earlier review's legacy `post_trade` feedback/front-loading bug is **not**
repeated below. H1 evaluates that frozen policy as written, not a corrected
feedback rule.

## Reproduction

Ran `.venv/bin/python eval/summarize.py --exp E6_confirm_sync`; its generated
summary matched the tracked summary. Independently read the CSV with `csv`,
paired the two policies by the **sorted** seed, and bootstrapped the paired
differences with 10,000 percentile resamples and `RandomState(0)`. No result
from `summarize.py` was used in this independent calculation.

| Quantity (bps unless noted) | Committed E6 verdict / expected | Independent result / rerun | Assessment |
|---|---:|---:|---|
| H1 mean paired IS, IA_sched_only - TWAP | -0.0340 | -0.034039 | Matches to 4 decimals |
| H1 two-sided 95% CI | [-0.0563, -0.0127] | [-0.056153, -0.012550] | Endpoints differ by ~0.00015 |
| H1 one-sided 95% upper bound | -0.0160 | -0.015726 | Differs by 0.000274; both below zero |
| H1 bootstrap fraction with mean >= 0 | 0.0006 | 0.0010 | Four resamples of 10,000 difference |
| Own-impact mean paired difference | -0.0414 | -0.041394 | Matches to 4 decimals |
| Own-impact two-sided 95% CI | [-0.0629, -0.0204] | [-0.062653, -0.020317] | Endpoints differ by <= 0.00025 |
| Own-impact one-sided upper bound | -0.0239 | -0.023611 | Differs by 0.000289; both below zero |
| CSV integrity | 200 seeds x 4 policies; all filled | 800 unique rows, seeds 1060-1259; all fill 4,000, matching arrival mids at CSV precision | Matches |
| Fresh simulator rerun, seeds 1060-1062 | E6 rows for all four policies | 12/12 rows match **all 25 stable serialized CSV fields**, except variable `wall_s` | Exact at CSV precision |
| Requested rerun fields | IS, own impact, instant, drift, filled | 12/12 literal CSV matches for **each** field | Exact at CSV precision |

The `R_repro_sol` run used `nice -n 10`, one worker, and `--rng-sync
per_wakeup` only after `kern.memorystatus_level` returned 33 (threshold 30);
the 12 rows matched results originally run with nine workers. The committed
CSV is written with `float_format="%.6g"`, so literal CSV equality does not
establish equality of unrounded floating-point values. The small CI differences
are consistent with Monte Carlo resampling differences, **not** a change of
significance. The provided tests passed: `5 passed`.

**Independently verified headline:** from the 200 committed seed pairs,
mean paired IS = **-0.034039 bps** and mean paired own impact =
**-0.041394 bps**; independent 95% bootstrap CIs exclude zero, and the
one-sided H1 upper bound is negative. I re-simulated **three**, not 200,
seeds. The sample win rate is 103/200 (51.5%, reported as 52%); the median
paired IS is -0.00512 bps, so "beats TWAP" should mean *mean* IS, not
reliable improvement on most seeds.

## Numbered findings

1. **MAJOR - The kernel fit/holdout does not use the registered numeric seed
   split.** `eval/calibrate.py:17,44-49` sorts `seed_*.pkl` filenames
   lexicographically, then takes the first half. For 0-39, the actual fit
   seeds are `0,1,10-19,2,20-26`; the actual holdout is
   `27-29,3,30-39,4-9`. Seven registered holdout seeds (20-26) enter the
   fit, and seven registered fit seeds (3-9) enter the holdout. This directly
   contradicts `eval/preregistration.md:67-71` and the advertised E1 OOS
   split. **Likely numerical impact:** the saved `g_tr`, `tau_s`, and negative
   OOS R-squared values are for a *different* split. The now-committed E9
   report calls its criterion unmet (TWAP -0.0205, PROBE -0.4057), but
   those are **not** results for its registered 20-39 holdout; corrected
   values require the raw episodes. All 0-39 seeds remain in TRAIN, so
   this is **not** leakage from E6's test seeds and does not undo its
   observed fixed-policy H1 result. **Minimal fix:** sort decoded
   `r["seed"]` numerically, assert exact intended seed sets, refit E1/E9,
   and add a split test using filenames 0-39.

2. **MAJOR - Passive fills make the reported "instantaneous" TCA component
   include intervening market moves.** `components/tca/tca/metrics.py:38-50`
   assigns every fill to the most recent *decision timestamp*, not its
   actual order ID or fill-time book. For delayed limit fills, `m(td) - p`
   includes price changes between decision and fill, so the other two
   components are measured too early. In the three E6 rerun seeds, IA_full
   fills totaling **367, 990, and 764 of 4,000 shares** occurred >1 second
   after their assigned decision (max 8.86, 12.27, 29.17 seconds); the
   market-order H1 policies filled within 0.025 seconds. A synthetic
   delayed-fill example preserves the IS identity while moving 1,000 bps
   from true fill-time drift into decision-time "instant": therefore
   `tests/test_contracts_and_tca.py:30-41` cannot test the claimed economic
   attribution. **Likely numerical impact:** total IS is unaffected, but
   IA_full's reported -0.0422 bps instant benefit and drift/own split need
   not mean "spread/book walking" versus "timing"; the H1 market-order
   comparison is much less exposed. **Minimal fix:** retain order IDs and
   pre-match book observations for fills, decompose at execution time, and
   test a delayed passive fill with a moving twin mid.

3. **MAJOR - E7 conditions its bootstrap on positive draws and overstates
   square-root realism.** The newer `eval/realism.py:40-70` does align
   seeds and resample them jointly, but lines 50-53 **drop** every draw
   with nonpositive mean impact at any size before computing the exponent
   CI. In the now-committed E7 result only **75%** of draws survived: its
   `[0.546, 1.760]` CI is conditional on a positive curve, not the
   registered unconditional 5,000-draw bootstrap. The verdict in lines
   63-70 also never enforces the `I(Q) not increasing` flag required by
   `eval/preregistration.md:46-57`; a positive but nonmonotone
   `[1, 1.5, 1.4, 2.5, 3]`-cent curve gives delta ~0.391 and "consistent"
   instead of a flag. On **actual E7**, delta = **1.006** (near linear);
   the 1k/2k-share peak-impact CIs include zero, yet the pre-registered
   *overlap-only* rule calls the whole result "consistent with concave,
   square-root-like impact." The report appropriately labels that
   interpretation lenient/post hoc. **Likely numerical impact:** H1 IS
   is unchanged, but E7's CI omits 25% of valid bootstrap draws and its
   formal realism verdict overstates evidence for square-root impact.
   **Minimal fix:** preserve the historical preregistered verdict while
   explicitly marking the scientific conclusion unresolved/near-linear;
   for a *future* registered test, require complete 100-129 seed sets,
   monotone/resolved impact, and a specified failure rule when bootstrap
   means are nonpositive, rather than silently conditioning them away.

4. **MINOR - The "optimal" QP does not minimize its own documented
   objective.** `components/execution_agent/execution_agent/policies.py:98-109`
   documents diagonal cost `inst_cost * sum(x_i**2)` plus off-diagonal
   transient interactions, but puts `inst_cost + 0.5*g_tr` on the matrix
   diagonal. At the frozen calibration this adds 0.002943 to 0.005
   cents/share-squared (+59%). Under the **written** objective, its first
   4,000-share slice is ~145 rather than ~171 shares and its model cost is
   ~0.14% above the feasible unconstrained optimum. **Likely numerical
   impact:** the E6 IS is a real measurement of the implemented schedule,
   not evidence that it is optimal for the stated model; any revised
   schedule requires a new experiment. **Minimal fix:** either remove the
   extra diagonal term or explicitly specify and calibrate a self-impact
   cost separately from `inst_cost`, then test the stated objective's
   constrained optimum rather than only a U shape.

5. **MINOR - `pre_window_identical` does not assert bit identity.**
   `eval/run_experiment.py:45-46,60-65` compares only a one-second grid
   with default-tolerance `np.allclose`. At a 100,000-cent mid it reports
   `100000` and `100001` cents as identical: ~1 cent tolerance is larger
   than H1's 0.34-cent/share mean effect. **Likely numerical impact:** all
   800 E6 rows record equal arrival mids **at six significant digits**, and
   there is no demonstrated false-positive twin here; the pre-window flag alone
   cannot certify the claimed bit-exact pre-trade worlds. **Minimal fix:**
   check exact equality of time-stamped pre-trade book states (or label the
   current check as approximate sampled mids) and explicitly assert equal
   arrival mids.

6. **MINOR - The validation bootstrap depends on worker completion order.**
   `components/execution_agent/autoresearch/eval.py:38-48` collects
   `imap_unordered` results, then bootstraps `by.values()` with fixed
   `RandomState(0)` without sorting seeds. On the identical E6 differences,
   merely reversing the seed order changes the finite-sample 95% CI from
   `[-0.056153,-0.012550]` to `[-0.055952,-0.013118]`.
   **Likely numerical impact:** means and E6's separately seed-sorted
   `summarize.py` output are unaffected, but borderline validation/ratchet
   pass decisions can vary with scheduling. **Minimal fix:** construct
   arrays in `sorted(by)` order before drawing bootstrap indices; test
   invariance under reordered worker results.

7. **MINOR - The four-decimal H1 verdict has no committed reproducing
   analysis.** `eval/results/E6_H1_verdict.md:5-12` reports one-sided
   bounds, own-impact contrast CIs, and bootstrap tail fractions, but
   `eval/summarize.py:39-42,67-85` generates only rounded two-sided IS
   contrasts and own-impact *levels*. The newer `eval/claims.py` generates
   rounded deliverable claims, not the full four-decimal verdict with
   one-sided bounds and tail fractions. The seed-sorted bootstrap gives
   the small differences in the reproduction table; no generator or
   resampling seed/order for that verdict is recorded. **Likely numerical
   impact:** at most ~0.0003 bps in the reproduced bounds and 0.0004 in
   the displayed bootstrap fraction here; H1's sign and rejection at
   alpha=0.05 do not change. **Minimal fix:** commit a deterministic
   CSV-to-verdict script specifying paired seeds, RNG, draws, quantiles, and
   tail statistic; do not label the bootstrap tail fraction a calibrated
   null-hypothesis p-value without a null-based procedure.

## Checks and limits

- Seed hygiene outside finding 1: E1 has 0-39 (TRAIN); E3 and E5 reuse
  1000-1059 (exploratory TEST); E6 uses fresh 1060-1259. The H1 arms and
  seed range appear in `thought_node.md` at commit `6f6fb23` (08:26 IST),
  before the E6 CSV/verdict commit `b87051e` (09:43 IST). The later
  `eval/preregistration.md` was added after E6 but points to that earlier
  record. No policy access to the null future, test-seed calibration, or
  SELL sign/cent-to-bps error was found. E6's rounded CSV satisfies
  IS = drift + own impact + instant to within 1.01e-5 bps.
- Concurrent E8 on validation seeds 100-199 does **not** replicate the
  IA_sched_only benefit: independently recomputed from its committed CSV,
  paired IS is +0.005593 bps [-0.028397, +0.039259], and own impact is
  +0.000460 bps [-0.031475, +0.032181]. This is not an E6 CSV or
  preregistration failure, but it limits generalization; E10 is
  registered to replicate on 400 new test seeds.
- `_synchronise_rng` (`components/sim_env/sim_env/world.py:61-94`) seeds
  each per-wakeup and timing `RandomState` with affine maps whose
  multipliers (1,000,003 and 31) are odd. Thus for a *uniform 32-bit input
  seed*, each **individual** stream seed is uniform and calls still use
  the same marginal RNG sampling methods. Splitting wake timing from
  decisions **changes their joint dependence and market trajectories**;
  this is not proof that stock ABIDES and the synced variant have the
  same full market distribution. On E4's 30 matched seeds, null arrival
  differs on all 30 and mean null window volume changes from 34,397 to
  33,904 shares; that finite sample does not establish a systematic bias.
  H1 is verified **conditional on the declared synced-twin simulator**,
  not on unmodified ABIDES. A stylized-fact and naive-twin robustness
  check is still needed before generalizing it.
- `README.md` reproduces E1/E3/E4, not the headline E6; the exact E6
  command is in the earlier committed `thought_node.md`. ABIDES is pinned,
  but the `--system-site-packages` Python dependency versions are not;
  literal cross-machine reproducibility is not established by this
  same-machine rerun.
