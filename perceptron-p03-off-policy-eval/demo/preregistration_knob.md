# Pre-registration — the α-knob: "the evaluator that says I don't know" (REAL data, Open Bandit Dataset)

**Registered:** 2026-10-04 21:07:33 IST (`TZ=Asia/Kolkata date`; the git commit that adds this file is the evidence).
**Status at registration:** no knob quantity has been computed from data. No estimate, diagnostic or interval at any α, on any period, from the extract or the raw rows. The only knob-related numbers anyone has seen are the committed "far-end" cells listed in §11. They come from `eval/results/` (α = 1 for the BTS logs; α = 0 for the Random logs).
**Gate rule: FROZEN** at `eval/gate_rule.json` (commit b4e95ae, calibrated 2026-10-04 13:39:26 IST on the simulator only), applied through `components/report/gate.py`. Nothing about the gate changes for this analysis.

## 1. Question
How far can a candidate policy move away from the policy that wrote the logs before the logs can no longer tell its value? Does the frozen overlap gate stop answering in the right place, judged against a real reference line from the concurrent A/B arms?

## 2. Data
- Open Bandit Dataset (ZOZO, Inc.; CC BY 4.0), campaign All, both arms (Bernoulli Thompson sampling "BTS" and uniform Random).
- Window: 2019-11-24 00:00 → 2019-11-27 12:00 UTC, the window of `eval/results/obd_slice.json`.
- Vendored in `demo/data/` by `demo/make_extract.py`. The extract holds counts per (UTC hour, item, position, exact logged propensity, click) for BTS, and per (hour, item, position, click, pre-window flag) for Random.
- Each file's sha256 is recorded in `demo/data/extract_manifest.json` before the knob run. The knob code refuses to run on a file that does not match the manifest, or that fails the checks in §10.

## 3. Candidate policies
- π_α = (1 − α)·π_BTS + α·U, where U is uniform over the 80 items at each position (marginal 1/80, the Random arm's logged propensity).
- π_BTS is the deployed sampler as it was at each impression, so π_α is a per-impression mixture.
- Policy value is linear in the policy: V(π_α) = (1 − α)·V(BTS) + α·V(U).
- **Grid:** α ∈ {0.00, 0.01, …, 1.00} (101 points). The demo slider moves on this grid only.

## 4. Periods (6, all reported)

| id | definition (UTC) |
|---|---|
| W | the pre-registered window: 2019-11-24 00:00:00.047846 → 2019-11-27 12:00 (84 h) |
| W1 | first half of W, ending 2019-11-25 18:00:00.023923 (hours 0–41) — the pre-registered "before" half |
| W2 | second half of W (hours 42–83) — the pre-registered "after" half |
| Nov 24 | whole UTC day 2019-11-24, from 00:00:00 (the whole-day definition of the disclosed deviation run; 3 more Random rows than W's first day) |
| Nov 25 | whole UTC day 2019-11-25 |
| Nov 26 | whole UTC day 2019-11-26 |

2019-11-27 is excluded because only 12 hours of it are available; it is not a whole day.

## 5. Log sources
- **S-B, BTS logs (primary).** The period's BTS-arm rows, with w_i = (1 − α) + α·(1/80)/ps_i.
  - This is exact: ps_i is the logged probability that the deployed BTS chose the logged item at that position at that moment, and U's probability is 1/80.
  - No policy reconstruction is used.
- **S-R, Random logs (secondary; approximate target).** The period's Random-arm rows, with w_j = (1 − α)·π̂_h(a_j | k_j)/0.0125 + α.
  - π̂_h is the committed P-hourly reconstruction: the BTS arm's hourly empirical item frequencies per position over W, exactly as in `eval/run_obd_slice.py`.
  - The target is therefore (1 − α)·π̂ + α·U, which only approximates π_α, because BTS adapted within hours.

## 6. Estimators
- **IPW** (primary): V̂ = mean(w·r).
- **SNIPW:** V̂ = Σwr / Σw, with influence φ = V̂ + w(r − V̂)/mean(w), as in `eval/run_obd_slice.py`.
- **DR is excluded.**
  - Its direct-method term needs π_BTS(a | x) for all 80 items, which is not logged.
  - The committed DR's cross-fitting folds are random over row order, so they cannot be reproduced from an aggregated extract.

## 7. Reference line
- V_ref(α) = (1 − α)·CTR_BTS(P) + α·CTR_Random(P): the on-policy click rates of the two concurrent A/B arms over the same period P.
- SE = sqrt((1 − α)²·se_B² + α²·se_R²). Each arm uses a Wald SE (sd with ddof = 1), and the arms are treated as independent.
- It is called the **concurrent A/B reference**, never ground truth:
  - the arms ran concurrently, but the arm-balance flag is unresolved (raw-label artefact, `eval/results/obd_raw_labels.md`);
  - on S-R the target is approximate.

## 8. Intervals
- **Primary: row-level Wald**, se = sd(φ, ddof = 1)/√n (rows treated as iid).
- **Secondary: hour-cluster (CR1)**, Var = H/(H − 1)·Σ_h(Σ_{i∈h}(φ_i − V̂))²/n², with one cluster per UTC hour.
- The committed results used a 500-draw row-bootstrap SE. Here the analytic SE is used because it is deterministic. Where a committed SE exists for an endpoint, both are reported.

## 9. Endpoints (each period × source × estimator × α)
- **E1 (primary):** the reference lies inside the estimator's 95% CI: |V̂ − V_ref| ≤ 1.96·se(V̂).
- **E2:** the analogue of the committed S1 test — 0 lies inside the 95% CI of V̂ − V_ref.
  - The arm whose rows enter both terms is handled exactly: the BTS rows for S-B, the Random rows for S-R.
  - The other arm is independent.
- **E3:** the gate decision, `decide()` from `components/report/gate.py` with `eval/gate_rule.json`.
  - The diagnostics are gate.py's formulas on (w(α), r): ESS/n, effective rewards, mean-weight z.
  - They are computed from sufficient statistics and cross-checked against gate.py's `diagnostics()` on expanded arrays at 11 values of α per series (relative tolerance 1e-9).
- **E4:** E1 and E2 with the hour-cluster SE. For E2, both arms are clustered jointly by hour.
- **Confident wrong sign:** not applicable; these are value rows, not effect contrasts.

**Pre-declared summaries, per series (period × source):**
- The first α at which the gate abstains, scanning away from the logging policy (S-B upward from 0; S-R downward from 1), or "never".
- E1's first failing α on the same scan.
- Counts over the grid: answered & E1 holds; answered & E1 fails ("answered miss"); abstained & E1 holds ("unnecessary abstention"); abstained & E1 fails ("justified abstention"). The same for E2.
- The largest answered miss: the distance from the reference to the nearest CI edge, per 1,000.
- **Primary summary:** IPW, row-level, S-B.

## 10. Reproduction checks
These must pass before any knob result is reported. A failure is reported and stops the run.
- **Extract vs committed, non-knob numbers** (`obd_slice.json`, `obd_slice_deviation_floor.json`, relative tolerance 1e-12):
  - CTR in W: BTS 0.0048902875209694075, Random 0.0034422548509314517;
  - halves cells R1, R2, B1 and B2; naive +1.62 and reference +1.26 per 1,000;
  - row counts.
- **Far-end cells:** the IPW and SNIPW values of every committed far-end cell in §11 (relative tolerance 1e-9).
  - The before-period cells are backed out as `policy_effect_after − interaction` from the committed Shapley fields.
  - The far-end ESS/n and z are checked against `gate_obd_posthoc.json` (relative tolerance 1e-6).

## 11. Predictions — from committed far-end cells only
Produced by `python3 demo/prereg_predictions.py`, which uses only the standard library and reads no data. These are predictions, not results; every miss will be reported.

**What follows by algebra, and so is not new evidence.** Let λ be the far-end share (λ = α for S-B, 1 − α for S-R). Then:
- IPW(λ) − V_ref(λ) = λ·(IPW_far − V_ref,far);
- the mean-weight |z| is the same at every λ > 0;
- ESS/n follows from the far-end mean weight and ESS.

So the IPW curves are fixed by the far-end cells. The genuinely new evidence is:
- W on the BTS side;
- the z of Nov 24 (both sources) and of W1 on the Random side;
- SNIPW along α;
- the hour-cluster intervals;
- the exact crossings.

The gate was designed after OBD failures had been seen (POST-HOC, `eval/results/gate_obd_posthoc.md`). On the far-end cells it is not out-of-sample.

**P1:** at the logging end (α = 0 for S-B, α = 1 for S-R), every estimate equals that arm's own CTR, ESS/n = 1 and z = 0. The gate answers and E1 holds.

**P2:** the algebra above. E2 for IPW and the gate's |z| are constant away from the logging end. E1 for IPW crosses at most once.

**P3–P5:** the gate, E1 and E2 per series. Half-widths use the committed bootstrap SE, so the crossings are approximate (±0.01–0.02).

| series | far-end ESS/n (committed) | far-end z (committed) | predicted gate | predicted E1 (IPW, row-level) | predicted E2 (IPW) |
|---|---|---|---|---|---|
| W2 · BTS logs | 0.009170 | -0.619 | answers up to alpha 0.42, first abstains at alpha 0.43 | holds everywhere; far-end IPW error -0.132/1,000, far-end half-width 0.276 | holds at every alpha |
| Nov 26 · BTS logs | 0.007954 | -1.907 | answers up to alpha 0.39, first abstains at alpha 0.40 | fails from alpha 0.28 onwards (away from the logging end); far-end IPW error -0.451/1,000, far-end half-width 0.281 | fails at every alpha except the logging end |
| Nov 25 · BTS logs | 0.000540 | +4.606 | abstain at every grid point except the logging end (abs(z) 4.6 > 3 at the far end) | fails from alpha 0.43 onwards (away from the logging end); far-end IPW error -0.316/1,000, far-end half-width 0.240 | holds at every alpha |
| W1 · BTS logs | 0.000577 | abs 6.1 (sign not recorded) | abstain at every grid point except the logging end (abs(z) 6.1 > 3 at the far end; abs(z) from demo_verdicts.md, sign not recorded) | holds everywhere; far-end IPW error -0.144/1,000, far-end half-width 0.427 | holds at every alpha |
| Nov 24 · BTS logs | 0.000672 | — | answers up to alpha 0.11, first abstains at alpha 0.12 [z not committed: conditional on abs(z) <= 3] | holds everywhere; far-end IPW error -0.049/1,000, far-end half-width 0.708 | holds at every alpha |
| W · BTS logs | — | — | not predicted (no committed far-end cell) | not predicted | not predicted |
| W · Random logs | 0.113958 | +1.371 | answers everywhere (ESS/n stays >= 0.114) | holds everywhere; far-end IPW error +0.079/1,000, far-end half-width 0.483 | holds at every alpha |
| W2 · Random logs | 0.137348 | -0.985 | answers everywhere (ESS/n stays >= 0.137) | holds everywhere; far-end IPW error +0.442/1,000, far-end half-width 0.726 | holds at every alpha |
| Nov 26 · Random logs | 0.142692 | +0.005 | answers everywhere (ESS/n stays >= 0.143) | holds everywhere; far-end IPW error +0.747/1,000, far-end half-width 0.997 | holds at every alpha |
| Nov 25 · Random logs | 0.098475 | +2.734 | answers everywhere (ESS/n stays >= 0.098) | holds everywhere; far-end IPW error -0.785/1,000, far-end half-width 0.868 | holds at every alpha |
| W1 · Random logs | 0.099611 | — | answers everywhere (ESS/n stays >= 0.100) [z not committed: conditional on abs(z) <= 3] [committed: passed the gate at the far end, demo_verdicts.md] | holds everywhere; far-end IPW error -0.240/1,000, far-end half-width 0.672 | holds at every alpha |
| Nov 24 · Random logs | 0.104625 | — | answers everywhere (ESS/n stays >= 0.105) [z not committed: conditional on abs(z) <= 3] | holds everywhere; far-end IPW error +0.242/1,000, far-end half-width 0.895 | holds at every alpha |

**Read-out of the predictions:**
- With the BTS logs, the gate is expected to stop answering at about α 0.43 (W2) and 0.40 (Nov 26).
- With the BTS logs, it is expected to refuse at every α > 0 on Nov 25 and W1, because the mean-weight test does not change with α.
- On Nov 26, between α ≈ 0.28 and 0.39, IPW's interval is expected to miss the A/B reference while the gate still answers. That would be the gate answering too long.
- With the Random logs, the gate is expected to answer everywhere and hold the reference everywhere.

## 12. Reporting
- All 12 series × 101 α × 2 estimators go in `demo/results/knob_results.json` and `demo/results/knob_summary.md`. They are shown on screen (the all-periods strip) whatever they show.
- After this commit, no change to the grid, the periods, the estimators, the thresholds or the intervals. Any deviation is disclosed and reported next to the registered result.
