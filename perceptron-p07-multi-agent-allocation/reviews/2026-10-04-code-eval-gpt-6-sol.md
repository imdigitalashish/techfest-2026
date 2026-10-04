# Review — code + evaluation correctness — gpt-6-sol (reasoning effort: max)

- **Date:** 2026-10-04, 10:24 IST.
- **Reviewer:** `rubber-duck` sub-agent with model override `gpt-6-sol`, effort max. Started 10:12 IST, before the Supervisor's sessions-only directive (10:15).
- **Scope:** simulator, planner, coordinator, policies, forecasters/detector, harness, stats, phase, long, NYC adapter, tests.
- **Reviewer's verdict (paraphrased):**
  - No off-by-one in P-step abandonment or hop/incoming timing (toy checks).
  - Arrivals are policy-independent (CRN holds).
  - But solver-dependent trajectories, an LP/simulator mismatch at τ=0, and a pre-registration mismatch in `stats.py` prevent treating the gaps as fully validated.

| # | Finding (reviewer) | Severity | Decision | Reason / action (lead) |
|---|---|---|---|---|
| 1 | The LP demand row is an inequality, so demand can vanish (neither served nor carried). At τ=0 the LP may keep a unit idle in a zone with a queue, while the simulator's FIFO matching serves it immediately. | High | **ACCEPTED as a documented limitation; fix deferred** | Free disposal of demand is a deliberate fluid relaxation (unserved demand abandons). The τ=0 "mandatory matching" mismatch is real. An exact fix needs a non-convex/MILP constraint (stay ⇒ serve). Re-planning every step bounds the damage, and it affects every MPC arm identically. Listed in ADR 001 *Limitations* and as a planner work item (try a penalty on idle units in zones with a queue at τ=0) before the midway check. |
| 2 | Equal LP objectives do not give equal episodes. Rounding degenerate optima is solver-dependent (toy: highspy 259 vs scipy 246 served). | High | **ACCEPTED (record + reproduce); tie-break deferred** | Every new result row records `planner_backend`. HiGHS is deterministic per backend and version, so runs reproduce exactly on the same backend. Legacy runs (mvp-v1, p3-v1, phase-v1) all used scipy, the only backend before 09:55. `--legacy` now exists in `eval/phase.py` too. A deterministic tie-break (tiny fixed cost perturbation) would change the pre-registered code mid-study, so it is deferred to the next protocol version. |
| 3 | `eval/stats.py` does not implement the pre-registered test (best rule picked on test seeds; Holm per scenario across rows). | High | **ACCEPTED (already addressed)** | The pre-registered analysis is `eval/confirm.py`: fixed references from `prereg.json`, Holm across the 6 primary scenario tests. It now asserts complete paired grids. `stats.py` is exploratory and is labelled so in reports. |
| 4 | The NYC "oracle" sees realised future demand (centred 15-min smoothing). | Med | **ACCEPTED** | Reported as a "retrospective (hindsight) smoother", never as a forecast-value bound. |
| 5 | Full `rates` passed to every policy's metadata. | Med | **ACCEPTED (fixed)** | `eval/harness.py` now passes `rates=None` to every non-oracle policy. Earlier runs are unaffected (verified by grep: no non-oracle policy reads `meta["rates"]`). |
| 6 | "Recovery" is absolute-threshold attainment and is censored at 120 for every policy at P=3. | Med | **ACCEPTED** | Headline shock metric = requests lost per shock (120-step window). Recovery is reported only with `recovered_frac` (censoring explicit). A relative recovery definition is a future item. |
| 7 | Requests pending at the horizon are unreported (~1.0–1.4% at L=8, P=10). | Med | **ACCEPTED (fixed for new runs)** | `pending_frac` is now in every new row. Draining cohorts to their deadline is deferred. Phase cells with large pending are flagged in the text. |
| 8 | `long.py` batch-means CI treats days as independent after averaging over seeds. | Med | **ACCEPTED (fixed)** | Whole-run CI now bootstraps over whole seed trajectories; per-day curves are descriptive only. |
| 9 | `@k=v` parses every value as float; `@horizon=8` crashes. | Low | **ACCEPTED (fixed)** | `horizon` is parsed as int; verified (`mpc-ewma@horizon=14` → H=14). |
