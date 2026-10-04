# Headline reproducibility review — 2026-10-04

**Model:** `gpt-6-sol` · **Effort:** `max` · **Commit reviewed:** `a99d42c0b1d73ed57be040bfb98f9b22787b1928` (includes headline abstract commit `d1d66fd0e0e7c1cd440267ff6df00a751d7e70d3`).

**Verdict:** All tested numerical headlines recompute from the committed episode CSVs. Seven regenerated text reports match after normalizing their output-directory prefixes; `phase_summary.csv` and all three regenerated plots are byte-identical. Eight independent episode replays match **31/31** available metrics by exact floating-point equality. Solver: `highspy` distribution **1.15.1** (`highspy.__version__` is not exposed).

## Numbered findings

1. **Med — the proposed adaptive, per-zone trust gate is not the tested implementation.** The abstract says trust is set per zone from calibrated uncertainty and detector regime state (`deliverables/round1-abstract.md:17`). The implementation instead stores one scalar `float(trust)` for the whole episode (`components/policies/policies.py:112`) and applies it only as `self.trust * fc.mean` in the LP call (`:144`). The scalar trust sweep and its numerical gains reproduce, but they do not validate the claimed adaptive/per-zone mechanism; that mechanism should be described as planned rather than built.
2. **Low — the phase module's oracle description is not an upper bound.** `eval/phase.py:8` calls the true-rate-forecast comparison an "upper bound on the value of ANY better forecast", whereas `eval/preregistration.md:31` correctly says it is *not* an upper bound. At `(L,P)=(4,3),(8,3),(8,10)`, true-rate MPC serves **1.09, 1.49, and 1.10 pp less** than EWMA MPC. This is a wording/interpretation error, not a numerical discrepancy.
3. **Low — the ~6 ms/step latency is end-to-end wall time, not isolated LP solve time.** The requested statistic, median `wall_s / horizon` for the 180 `mpc-ewma` MVP rows, is **5.949 ms/step**, matching the rounded abstract claim. But `wall_s` spans the entire simulator/policy loop (`eval/harness.py:73-88`), whereas solver timing is recorded separately (`:94`); the median per-episode `solve_ms_mean` is **5.379 ms**. Label the former as episode wall time per step rather than a solver-only benchmark.

## Committed versus recomputed headline values

Recomputed directly from copied `episodes.csv` data with the repository's paired bootstrap (`10,000` resamples, seed `0`), Wilcoxon, and Holm definitions, then checked against the regenerated reports. Percentage-point differences are in served fraction.

| Claim | Committed | Recomputed |
|---|---|---|
| MVP shock, EWMA − pre-registered greedy | **+3.73 pp** [+3.28, +4.20], 30/30, Holm `1.1e-8` | **+3.73 pp** [+3.28, +4.20], 30/30, Holm `1.1e-8` |
| MVP shock+drift, EWMA − pre-registered reactive | **+5.47 pp** [+5.36, +5.59], 30/30, Holm `1.1e-8` | **+5.47 pp** [+5.36, +5.59], 30/30, Holm `1.1e-8` |
| MVP shock+drift+spikes, EWMA − reactive | **+5.99 pp** [+5.82, +6.15], 30/30, Holm `1.1e-8` | **+5.99 pp** [+5.82, +6.15], 30/30, Holm `1.1e-8` |
| Phase `(L,P)` planning vs best rule | **7/8** cells; winning gains +2.27 to +9.82 pp, 20/20 each; `(8,10)` −0.38 pp | **7/8** cells; +2.27 to +9.82 pp, 20/20 each; `(8,10)` −0.38 pp (6/20) |
| Pre-registered phase detector H1 | **No significant predicted benefit**; significant *harm* at `(1,10)` +4.4 lost/shock, Holm `.026`, and `(8,10)` +21.9, Holm `.011` | **No significant predicted benefit**; +4.4, Holm `.02589`, and +21.85, Holm `.01054` |
| True-rate forecast in long-lead phase cells | Worse in **3/4**: −1.09, −1.49, −1.10 pp | Worse in **3/4**: −1.09, −1.49, −1.10 pp |
| Pure shock, queue-only − EWMA lost/shock | **−62.3** | **−62.3** |
| Week, EWMA − reactive; lost/shock | **+6.34 pp** [+6.26, +6.43], **−131.7** lost/shock; day 7 greedy **0.466**, EWMA **0.912** | **+6.34 pp** [+6.26, +6.43], **−131.7**; day 7 **0.466 / 0.912** |
| Month, EWMA − reactive (four seeds) | **+6.37 pp** [+6.29, +6.44], 4/4 | **+6.37 pp** [+6.29, +6.44], 4/4 |
| NYC replay, EWMA − reactive; July-4 event loss | **+2.52 pp** [+2.39, +2.67], 20/20; **−38.1** event losses | **+2.52 pp** [+2.39, +2.67], 20/20; **−38.15** event losses |
| Pareto, EWMA `c_move=0.5` − reactive | **+3.77 pp** served, **−0.172** empty hops/served | **+3.77 pp** served, **−0.171924** empty hops/served |
| Half-trust vs best extreme | Shock+drift **+1.13 pp**, shock+drift+spikes **+1.24 pp**; best shock `0.25`, drift `0.75` | **+1.13 / +1.24 pp**; best shock `0.25`, drift `0.75` |
| MPC latency, median `wall_s/horizon` | Approximately **6 ms/step** | **5.948717 ms/step** (180 EWMA rows) |

The main preregistration was committed as `6e58813` at 10:10 IST, before the MVP CSV commit `11ad5bf` at 10:30; phase addendum `a5eb3f0` at 10:25 preceded phase CSV commit `4d52027` at 10:40. The trust sweep is explicitly exploratory, not the future preregistered trust test across fresh grid seeds. The four-seed month result is descriptive (its Wilcoxon `p=0.125`).

## Analysis and simulation reproduction

From **this checkout's** `perceptron-p07-multi-agent-allocation/` working directory, copied all seven analyzed `eval/results/*-v2` folders to `/tmp` before running `nice -n 10 "$PY" -m eval.confirm`, `eval.phase --summarise-only`, `eval.long` (week and month), and `eval.summarise_misc` (NYC, Pareto, trust) on the copies. The only raw text differences are the expected `/tmp/...` versus `eval/results/...` directory names in report headings; replacing the temporary prefix with `eval/results` yields exact text equality. `phase_summary.csv`, `phase.png`, and both `daily.png` files are byte-identical.

For replay, every job used the CSV's `policy`, `scenario`, `seed`, `n_agents`, `patience`, `horizon`, and `hop_steps`, plus `legacy=False`, through `eval.harness.run_episode`. All rows below use seed `200`; each displayed metric is **committed = replayed** (six-decimal display; equality checked at full precision with round-trip CSV float parsing).

| Folder / policy / scenario | Horizon; L/P | Served fraction | Lost fraction | Empty hops/served | Lost/shock |
|---|---|---:|---:|---:|---:|
| MVP / `mpc-ewma` / shock | 1440; 1/10 | 0.967675 | 0.032018 | 0.507240 | 199 |
| MVP / `mpc-queue` / shock | 1440; 1/10 | 0.974312 | 0.025012 | 0.370758 | 144 |
| MVP / `reactive` / shock | 1440; 1/10 | 0.913164 | 0.086160 | 0.560334 | 374 |
| MVP / `mpc-ewma` / shock+drift+spikes | 1440; 1/10 | 0.941053 | 0.058346 | 0.632470 | 310 |
| Phase / `mpc-ewma` / shock | 720; 4/3 | 0.622067 | 0.375451 | 0.321545 | 891 |
| Week / `reactive` / long-week | 10080; 1/10 | 0.870103 | 0.129801 | 0.702717 | 469.571429 |
| NYC / `mpc-ewma` / nyc-jul03-04 | 2880; 1/10 | 0.998603 | 0.001257 | 0.364037 | — |
| Trust / `mpc-ewma@trust=0.5` / shock+drift | 1440; 1/10 | 0.957412 | 0.041424 | 0.590374 | 227 |

NYC has no synthetic `shock_lost` column, hence **31/31** available comparisons rather than 32. Its TLC inputs are gitignored and supplied by the lead's `.data`; this is a reproduction using those inputs, not a self-contained fresh checkout. The adapter's cache freshness check (`components/scenarios/nyc_tlc.py`) would have rewritten the lead's cache because this worktree's mapping-file mtime is newer. For the NYC replay only, I used a private byte-identical cache copy with refreshed *copy* mtime and symlinks to the lead's read-only source files. Source and cache bytes remained unchanged; the worktree's temporary `.data` symlink was removed.

**Information boundary:** `eval/harness.py:68` replaces `rates` with `None` before resetting any non-oracle policy; `FleetState` and `StepInfo` expose observed state/outcomes, not true rates (`architecture/contracts/contracts.py:57-94`). Only `oracle` reads `meta["rates"]` (`components/policies/policies.py:138`). The scalar trust knob changes only the forecast tensor passed to `planner.solve` (`:144`), not the forecaster observations, queue, or ground-truth trace.

This is an exact reproduction of seven analyses and a bounded eight-episode simulation sample, **not** a rerun of every committed episode.

## Lead decisions (2026-10-04 11:15 IST)

| # | Decision | Reason / action |
|---|---|---|
| 1 | **ACCEPTED** | The abstract now separates what was tested from what is planned. Tested: one scalar trust shared by all zones (exploratory sweep, `eval/results/trust-v2`). Planned: per-zone, uncertainty- and regime-gated trust, under the pre-registered Addendum B test. A tuning-seed preview (`eval/results/gated-tuning-preview`) shows that regime *gating* adds ≈0 over the best fixed trust (+0.01 pp), so the gain comes from global shrinkage. The ADR and memo were updated accordingly. |
| 2 | **ACCEPTED (fixed)** | `eval/phase.py` docstring: the true-rate forecast is "a reference, NOT an upper bound". A repo-wide sweep found no other occurrence outside third-party code. |
| 3 | **ACCEPTED** | The abstract now says "~6 ms per decision step end to end (median, laptop)": median `wall_s/horizon` = 5.949 ms over the 180 mvp-v2 `mpc-ewma` rows, as this review reproduced. |

All headline numbers reproduced exactly: 7/7 regenerated analyses; 8 replayed episodes matching on 31/31 metrics, highspy 1.15.1. No numbers in the abstract change.
