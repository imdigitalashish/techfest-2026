# P3 code, evaluation, and reproducibility review (GPT-6 Sol)

**Reviewed:** 2026-10-04 14:03:41 IST (`TZ=Asia/Kolkata date`). Base: `a0ebb0d` after `git fetch origin && git rebase origin/main`; the review branch initially had no diff from `origin/main`. This is an audit of the committed P3 implementation against `eval/preregistration_obd.md`, not a differential branch review. The preregistration was committed as `f88de64` at 13:06:47 IST; its first result file was committed as `3cec249` at 13:16:04 IST. Read `PLAYBOOK.md` sections 6 and 10.

**Overall:** All **44/44 dynamic numbers** in the abstract reproduced exactly. Reproducibility does **not** establish that the static-policy comparison estimates the deployed BTS policy or that the two real-data arms support a causal "true effect": those are the two blocker-level findings below. No dataset was fetched or modified. Existing gitignored OBD data were linked from the lead's worktree for read-only use.

## Runs and provenance

Working directory for every payload: `perceptron-p03-off-policy-eval/`. `PY=/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-effective-funicular/perceptron-p03-off-policy-eval/.venv/bin/python`. Each heavy run was guarded with `sysctl -n kern.memorystatus_level >= 30`, executed alone with `nice -n 10`, and timed with `/usr/bin/time -p`. Dates/times are from `TZ=Asia/Kolkata date`.

| Effective command | IST start-end | Wall (`real`) | Output / comparison with `HEAD` |
|---|---|---:|---|
| `nice -n 10 "$PY" -m pytest -q tests` | 13:46:02-13:46:03 | 1.61 s | 11 passed. |
| `nice -n 10 "$PY" eval/run_decomposer_review.py --seeds 20` | 13:46:19-13:46:40 | 20.44 s | JSON, CSV, Markdown and drift-sweep figure byte-identical; mean Shapley-policy coverage 0.95. |
| `nice -n 10 "$PY" eval/calibrate_gate.py --seeds 20` | 13:47:45-13:48:11 | 26.07 s | CSV byte-identical; rule fields identical except runtime `calibrated_at`: committed 13:39:26, regenerated 13:48:11 IST. ESS/n floor 0.05, reward floor 0, answer rate 0.470833, answered coverage 0.961652. |
| `nice -n 10 "$PY" eval/run_obd_slice.py` | 13:48:35-13:54:18 | 343.20 s | JSON and Markdown byte-identical. R 660,904; BTS 5,956,296; 84 hours, 0 hours dropped; both half-window DR S1 tests contain 0; one preregistered day pair. |
| `nice -n 10 "$PY" eval/run_obd_slice.py --floor_start_to_hour` | 13:54:28-14:00:54 | 386.74 s | Disclosed-deviation JSON byte-identical; 3 day pairs and 3/3 deploy-direction DR S1 failures. **Not** a preregistered window. |
| `nice -n 10 "$PY" eval/run_sim_bank.py --seeds 30 --msm_seeds 10` | 14:01:00-14:01:10 | 9.84 s | Bank CSV and Markdown byte-identical; S1 naive -0.0558, true effect +0.0752, DR +0.0748; S4 MSM 10/10. |
| `nice -n 10 "$PY" eval/apply_gate_obd.py` | 14:02:25-14:02:31 | 5.23 s | 6/10 answered, 0 CI misses among answered, 3/3 misses abstained, flagship deploy-half **abstained**. JSON matches committed except propagated calibration timestamp. An earlier attempt was *not started*: the memory check returned 29 (<30). |
| `nice -n 10 "$PY" - <<'PY' ... PY` (80 full-refit DM bootstraps; script below) | 14:02:49-14:03:04 | 14.90 s | P-static DM full-refit SE 0.000195558 versus committed fixed-term bootstrap SE 0.0000007350; the corrected difference CI crosses zero. No output files written. |
| `"$PY" eval/build_headline.py` | 14:03:15-14:03:16 | 0.71 s | `headline.json` byte-identical. |
| `"$PY" deliverables/render.py` | 14:03:15-14:03:16 | 0.05 s | Abstract byte-identical; rendered body 885 words. |
| `"$PY" eval/check_docs.py` | 14:03:15-14:03:16 | 0.05 s | Exit 1: abstract **70 numeric tokens, 0 untraced**; selection memo **23 tokens, 18 untraced**. The memo is being rewritten; this is the expected memo-only failure, not an abstract-number bug. |

The official ZIP range reader was **inspected, not re-run** (no network download). `obd_zip_slice.py` explicitly casts timestamps to nanoseconds after pandas parsing; `run_obd_slice.py` also upgrades legacy microsecond arrays. Both reproduced JSON windows have the expected 2019 UTC timestamps. The IPW, linearised SNIPW and DR point formulas, paired on-policy-minus-OPE effect terms, S1 cancellation of the shared observed after-arm mean, 2x2 Shapley policy/interaction formulas and their paired variances, UTC midpoint/day-pair and >=1,000-B-rows-per-hour filtering, density-ratio prior correction, and Hajek MSM weight extrema agree with the preregistration/code definitions. I checked the MSM extrema against all `2^4` endpoint-weight assignments on a four-row example; both endpoints matched. The exceptions are below.

## Reproduction of every dynamic abstract number

The 44 distinct `{{key}}` placeholders in `round1-abstract.tmpl.md` were compared with both committed and regenerated `headline.json`; regenerated `round1-abstract.md` was byte-identical. Units follow the abstract: `_k` means per 1,000 impressions, `_pp` means percentage points. **Verdict codes:** **D** = trustworthy descriptive sample statistic; **T** = numerical comparison correct but wrong target for the claimed live-policy validation; **C** = measured point correct but causal "truth" needs arm exchangeability, and the deploy-half fails the gate; **P** = correct *post-hoc*, overlapping cases, not independent/preregistered confirmation; **S** = correct for the specified synthetic world/seeds only; **F** = correct in the *calibration sample*, not held-out gate performance. These codes give a separate interpretation to each reproduced number.

| Number (`abstract` key) | Committed | Reproduced | Match? | Verdict |
|---|---:|---:|:---:|:---:|
| `obd_rows_random` | 660,904 | 660,904 | yes | D |
| `a2_static_dr_relerr` | 0.1% | 0.1% | yes | T |
| `obd_ctr_bts_k` | 4.89 | 4.89 | yes | D |
| `a2_static_ipw_relerr` | 1.1% | 1.1% | yes | T |
| `a3A_naive_k` | +1.62 | +1.62 | yes | D |
| `a3A_truth_k` | +1.26 | +1.26 | yes | C |
| `a3A_overstate` | 29% | 29% | yes | C |
| `a3A_dr_k` | +1.40 | +1.40 | yes | C |
| `a3B_naive_k` | −1.25 | −1.25 | yes | D |
| `a3B_truth_k` | −1.26 | −1.26 | yes | C |
| `a3B_dr_k` | −1.70 | −1.70 | yes | C |
| `dayA_dr_fail` | 3/3 | 3/3 | yes | P |
| `dayA_min_ess_pct` | 0.05% | 0.05% | yes | P |
| `gate_obd_answered` | 6/10 | 6/10 | yes | P |
| `gate_obd_wrong` | 0 | 0 | yes | P |
| `bank_seeds` | 30 | 30 | yes | S |
| `s1_naive_pp` | −5.6 | −5.6 | yes | S |
| `s1_truth_pp` | +7.5 | +7.5 | yes | S |
| `s1_dr_pp` | +7.5 | +7.5 | yes | S |
| `s1_dr_rmse_pp` | 0.6 | 0.6 | yes | S |
| `s1_naive_wrong` | 30/30 | 30/30 | yes | S |
| `shap_cover` | 95% | 95% | yes | S |
| `s4_dr_bias_pp` | −6.9 | −6.9 | yes | S |
| `s4_dr_cover` | 0% | 0% | yes | S |
| `s4_msm_valid` | 10/10 | 10/10 | yes | S |
| `s4_gamma_star` | 1.25 | 1.25 | yes | S |
| `obd_hours` | 84 | 84 | yes | D |
| `a1_median_ratio` | 16 | 16 | yes | D |
| `sweep_points` | 13 | 13 | yes | S |
| `sweep_right_from` | −0.25 | −0.25 | yes | S |
| `sweep_wrong_from` | −0.75 | −0.75 | yes | S |
| `sweep_dr_rmse_max_pp` | 0.6 | 0.6 | yes | S |
| `sweep_naive_rmse_max_pp` | 26.2 | 26.2 | yes | S |
| `fb_dr_pp` | +9.1 | +9.1 | yes | S |
| `fb_direct_pp` | +8.9 | +8.9 | yes | S |
| `fb_total_pp` | +14.6 | +14.6 | yes | S |
| `ms_dr_bias_pp` | +0.09 | +0.09 | yes | S |
| `ms_dm_bias_pp` | +1.58 | +1.58 | yes | S |
| `ms_mixdr_bias_pp` | −0.01 | −0.01 | yes | S |
| `ms_mixdm_bias_pp` | +0.57 | +0.57 | yes | S |
| `gate_sim_configs` | 36 | 36 | yes | F |
| `gate_sim_cov` | 0.96 | 0.96 | yes | F |
| `gate_sim_ungated_worst` | 0.65 | 0.65 | yes | F |
| `gate_sim_answer` | 47% | 47% | yes | F |

**Additional claim checks:** Preregistered half-window S1 DR difference CIs contain 0 in both directions (A: [-0.00020766, +0.00049268], B: [-0.00117844, +0.00028530]); A's naive CI excludes the observed truth point, B's includes it. The preregistered UTC whole-day analysis has **one** pair (Nov 25 to Nov 26). The `3/3` is from the separately disclosed floor-to-hour deviation: its Nov 24-to-26 and Nov 25-to-26 deploy cases reuse exactly the same W2 OPE estimate (0.00148330) and truth (0.00106427), so they are not three independent failures. The `6/10` gate cases also mix preregistered and deviation windows and reuse after-day outcomes. Simulator bank, drift, feedback, misspecification and confounding figures are trustworthy **as synthetic results**, not evidence of real-world coverage. The gate's `0.96` is coverage on the *same 720 runs used to select its thresholds*; no held-out gate coverage is in this headline.

## Issues

**C1 - blocker - `eval/obd_balance_posthoc.py:28-36`; `deliverables/round1-abstract.tmpl.md:27-29`. Real-arm causal "truth" is unverified.** The preregistered balance test reports TVD 0.3611-0.3639 in every user feature (>0.05), so its own arm-assignment caveat applies. The post-hoc diagnostic declares this a label artefact by collapsing every category missing in one arm into a shared `"other"` bin and sorting category shares without identities. That cannot distinguish relabelling from a real 36% category substitution: I checked R={A:64%, D:36%}, B={A:64%, E:36%}; true labelled TVD is 0.36, both post-hoc tests are 0. Both arms' CTRs are observed, but their difference is a causal policy effect only on exchangeable users. **Fix:** verify semantic category alignment and arm randomisation (or reweight/check comparable contexts with an identified estimand); until then retain the preregistered caveat prominently and call `+1.26` an *observed arm difference*, not established causal truth.

**C2 - blocker - `eval/run_obd_slice.py:128,166-175`; `deliverables/round1-abstract.tmpl.md:26`. The `0.1%` "deployed BTS policy" accuracy compares two different policies.** `P-static` is the Monte Carlo distribution from the *initial static prior*; the comparator is the actual BTS arm's on-policy CTR over an adaptive 84-hour deployment. The same run finds 20/20 top cells change by >=1.5 in six-hour median logged propensity (median factor 16.06), and static versus observed window-average item-slot frequencies correlate only 0.631. The point difference of `0.1%` is reproducible, but it is **not** the estimation error of the deployed time-varying policy; P-hourly DR's separately reported point difference is `0.9%` and is itself an hourly reconstruction. The static DR 95% CI (~0.00446-0.00531) also dwarfs the `0.1%` point coincidence. **Fix:** describe this as a static-prior estimate compared descriptively with BTS CTR, report both registered reconstructions, and use the actual logged dynamic policy (or a matching static-policy on-policy arm) before claiming recovery of its value.

**C3 - major - `eval/run_obd_slice.py:47-50,74-83,174-179`; `components/estimators/ope.py:63-73`. The DM bootstrap treats fitted predictions as known.** `boot_se(dm)` resamples only the already-fitted cross-fold predictions; it never re-estimates cell CTRs, so it excludes the principal source of DM variability. The committed P-static DM SE is `7.3502e-7`, and the printed DM CI rounds to `0.00472-0.00472`. An independent 80-resample bootstrap *refitting DM on every sampled log* (same static policy, same data and two-fold algorithm) gave SE `0.000195558` (266x larger). Adding the published truth SE changes the DM-minus-truth CI to `[-0.00055954, +0.00021518]`: the reported **"NO" consistency** flips to **yes** for P-static. The generic DM `influence=dm` has the same limitation if fed to `wald`/`bootstrap`. **Fix:** bootstrap the complete DM training/evaluation procedure, or supply a valid nuisance-estimation influence/variance estimator; rerun DM CIs and consistency readouts. The DR point formula and paired-policy-effect bootstrap are a separate matter and checked out.

The independent diagnostic was run without creating a file:

```bash
nice -n 10 "$PY" - <<'PY'
import json
import numpy as np
from eval.run_obd import bts_action_dist
from eval.run_obd_slice import S, Z, load, ope_terms

result = json.loads(open('eval/results/obd_slice.json').read())
start = np.datetime64(result['window']['start_utc'], 'ns').astype('int64')
end = np.datetime64(result['window']['end_utc'], 'ns').astype('int64')
source = load(S / 'random' / 'all' / 'all.npz')
mask = (source['ts'] >= start) & (source['ts'] < end)
rows = {key: source[key][mask] for key in ('item', 'pos', 'click', 'ps')}
pi_static = bts_action_dist(n_sim=400_000)
phi, _ = ope_terms(rows, pi_static)
n = len(rows['click'])
fixed_se = phi['DM'].std(ddof=1) / np.sqrt(n)
rng = np.random.default_rng(20261004)
boot = []
for _ in range(80):
    ix = rng.integers(0, n, n)
    sample = {key: val[ix] for key, val in rows.items()}
    boot.append(float(ope_terms(sample, pi_static)[0]['DM'].mean()))
refit_se = float(np.std(boot, ddof=1))
truth, tse = result['a2']['truth'], result['a2']['truth_se']
diff = float(phi['DM'].mean() - truth)
print(n, len(boot), float(fixed_se), refit_se)
print(diff - Z * np.hypot(refit_se, tse), diff + Z * np.hypot(refit_se, tse))
PY
```

**C4 - major - `eval/apply_gate_obd.py:59-72`; `eval/results/gate_obd_posthoc.md:11`; `deliverables/round1-abstract.tmpl.md:28-30`. The flagship real deploy result fails the team's own gate.** The pre-registered half-window A estimate is `+1.40` per 1,000 and its DR difference CI includes the observed truth, but the calibrated gate **abstains** (ESS/n `0.00917` < `0.05`). The abstract presents this as a successful "DR gives..." result while only mentioning gate abstention on the day pairs. **Fix:** put the half-window abstention beside the result and distinguish retrospective closeness from a decision the proposed certificate would actually answer. The `6/10` post-hoc number includes this unnecessary abstention; it cannot certify the flagship case.

**C5 - major - `components/report/gate.py:20-45`; `eval/gate_rule.json:2-4`. The advertised reward-count check does nothing at the chosen threshold.** Calibration selected `tau_r=0`, so a log with *zero rewards* passes the `ess_r < tau_r` test. I ran `w=[0.5,1.5]*50`, `r=zeros(100)`; diagnostics were ESS/n `0.8`, effective rewards `0.0`, mean-weight z `0.0`, and `decide` returned `(True, [])`. A zero-variance weight sample also gives nonfinite z, which the runtime `abs(z) > tau_z` check cannot reject. **Fix:** explicitly abstain on zero informative rewards and nonfinite diagnostics (and establish/validate a positive reward floor if promising that safeguard); rerun calibration and update the gate claims.

**C6 - major - `components/simulator/sim.py:72-78,101-109`. The hidden-override before-period Shapley ground truth uses the wrong new policy.** `deployed(X,u,"new")` applies the override whenever new is running, and `v_after_new` correctly uses it, but `v_before_new` uses nominal `policy(X,"new")`. For `ScenarioConfig(hidden_confounding=1.0)` and 20,000 fixed-seed before contexts, I measured nominal V(new) `0.45624` versus deployed V(new) `0.51996` (difference `+0.06372`). This would misattribute about half that difference in a hidden-confounding Shapley truth. The current S4 *after-effect* headline is not affected. **Fix:** define the same deployed intervention in both period-policy counterfactual cells, or explicitly distinguish/rename a hypothetical nominal-before policy and do not use it as actual Shapley truth.

**C7 - minor - `eval/calibrate_gate.py:55-77`. "Ungated" still runs a mean-weight gate.** `evaluate(df,0,0)` retains `abs(z_mean_w)<=3`, excluding 27/720 runs; its reported answer rate is `0.9625` and pooled coverage `0.91919`, while the actual no-gate baseline answers all 720 with coverage `0.91667`. The abstract's worst-configuration value `0.65` happens to be the same under both baselines, but the comparison is mislabeled. **Fix:** calculate ungated metrics directly on all rows, separately from the thresholded evaluator.

**C8 - minor - `eval/run_obd_slice.py:200-225,241-246`; `components/decomposer/decompose.py:82-85`. The environment Shapley term has no reported variance/CI.** The preregistration asks for CIs of decomposition terms; policy and interaction have them, but `shapley_env=naive-s_pol` and its on-policy truth are printed as bare points. Summing the naive and policy variances as if independent would also be wrong because they reuse the same rows. **Fix:** use paired per-row terms `0.5*(R_after + OPE_old_after)` minus `0.5*(R_before + OPE_new_before)`, bootstrap within each period, and add independent periods' variances; report an env interval for estimate and on-policy truth.

**C9 - minor - `eval/run_obd_slice.py:147-151`; `eval/preregistration_obd.md:27-29`. The cell-hour distinct-propensity readout uses an unregistered subset.** The preregistration says to report distinct logged propensity values per cell-hour for the analysis cells. The implementation aggregates only the top **five** cells and their first **48** observed hours, though the decision rule uses 20 cells and W spans 84 hours. The generated report discloses the restriction, and it does not change the 20/20 decision, but this auxiliary statistic is not the registered full-cell/full-window readout. **Fix:** report all preregistered top-20 cell-hours, or clearly flag the 5-by-48 summary as a post-registration deviation alongside the complete readout.

**Bottom line for the abstract:** Retain the reproduced sample sizes, on-policy CTR, observed descriptive before/after gap, simulator results (explicitly synthetic), and the disclosed post-hoc gate counts. Qualify/rewrite the live-policy `0.1%`, unconditional real-data `true effect`, flagship DR success, and gate-generalisation wording until C1-C5 are addressed. Do not turn the 3/3 overlapping deviation pairs or the in-sample 0.96 calibration coverage into independent real-world validation.
