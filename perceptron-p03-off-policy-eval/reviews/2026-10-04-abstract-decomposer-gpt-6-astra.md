# Hostile review: Round-1 abstract and decomposer

**Reviewer:** GPT-6 Astra (`gpt-6-astra`), independent hostile-judge review under PLAYBOOK section 10.

**Clock:** review started at 2026-10-04 13:45:31 IST; report timestamp captured at 2026-10-04 13:55:57 IST, both using `TZ=Asia/Kolkata date`. **Reviewed snapshot:** `a0ebb0d1683d07759e18bfced7e93d50a28597fa`, after the requested fetch/rebase. The abstract's latest modifying commit in that snapshot is `5ab7b67`. All local paths below are relative to `perceptron-p03-off-policy-eval/`, except `PLAYBOOK.md` and `_briefs/perceptron.txt`. Bare result filenames denote `eval/results/`; `round1-abstract.md` denotes `deliverables/round1-abstract.md`. Line references describe this pinned snapshot, not subsequent fixes.

**Scope:** the specified abstract, template/rendering chain, diagram, component map, ADR, preregistration, result tables, headline JSON, literature landscape, and the implementation paths that produce the claims. I independently recomputed small aggregates from committed CSV/JSON using Python's standard library. I did not execute project code, rerun experiments, download the dataset, or modify any project file except this review. Primary literature records actually opened are listed in section 7. Full experimental reproducibility, raw-data integrity, and papers' full-text theorem details are **UNVERIFIED** by this read-only review.

**Verdict: 59/100, or 2.95/5. I would not shortlist this version.** The core OPE and two-factor Shapley algebra are mostly sound. The pitch is not: it changes estimands, calls a non-rejection a correct answer, treats an unmatched policy reference as ground truth, and markets an exploratory filter as a certificate. This is a potentially useful audit tool, not yet a validated causal certificate. More estimators and more decimal places will not repair that.

Severity meanings: **blocker** = withdraw or correct the central submission claim before submitting; **major** = materially changes interpretation, validity, or rubric score; **minor** = presentation/readiness detail without invalidating the estimator. There are **14 issues: 2 blockers, 11 major, 1 minor**. The lead can mark each A-number ACCEPTED or REJECTED with reasons.

## 1. Official rubric and shortlist judgment

The weights and definitions come from `_briefs/perceptron.txt:308-354`. Round 1 explicitly judges the **plan**, not whether code/results already exist (`:305-307`); I do not penalize an honestly labelled future feature merely for being unfinished. I do penalize invalid comparisons and claims of existing capabilities that the proposal relies on.

| Criterion | Weight | Score / 5 | Weighted contribution / 5 | Judgment and evidence |
|---|---:|---:|---:|---|
| Problem Understanding & Relevance | 20% | 4 | 0.80 | Correctly identifies confounding of before/after, overlap, difference estimation, and feedback non-identification. Loses the fifth point because "policy effect" alternates between an after-period contrast and a symmetric attribution. `deliverables/round1-abstract.md:9-18,26-31`; A3. |
| Technical Soundness & Feasibility | 25% | 3 | 0.75 | Standard IPS/DR and Shapley are feasible on CPU; the paired-score algebra is sensible. Policy/reference mismatch, incomplete uncertainty accounting, and the unintegrated certificate prevent a strong score. `components/decomposer/decompose.py:42-86`; `eval/run_obd_slice.py:171-223`; A2, A3, A8, A9, A11. |
| Innovation / Novelty | 20% | 3 | 0.60 | Goes beyond merely calling an OPE library through attribution, diagnostics, and an auditable protocol. It does not establish a new estimator or guarantee. The ADR's novelty self-scores of 4 are unsupported by the comparisons actually made. `architecture/adr/001-spike.md:10-17`; `research/landscape.md`, sections 2, 5, 6, 8; A12. |
| Clarity & Structure of Abstract | 10% | 3 | 0.30 | The required sections are present and techniques are specific. But it is a results inventory with ambiguous units, multiple meanings of "truth", and a "0 wrong" statement that does not mean what it says. `deliverables/round1-abstract.md:26-50`; A1, A3, A13. |
| Impact & Rigor of Evaluation Plan | 15% | 2 | 0.30 | Preregistration and disclosed bad results deserve credit. Reusing calibration runs as validation, counting repeated after-period estimates as separate successes/failures, and calling consistency coverage undermine the central evidence. `eval/preregistration_obd.md:56-65`; `eval/calibrate_gate.py:55-81`; A1, A4-A8, A10. |
| Team Fit & Readiness | 10% | 2 | 0.20 | One named person plus two TBD roles is not evidence of a three-person skill mix. October lacks an explicit MVP/validation freeze schedule. `deliverables/round1-abstract.md:52-55`; A14. |
| **Total** | **100%** | | **2.95 / 5 = 59 / 100** | |

Calculation: `4*0.20 + 3*0.25 + 3*0.20 + 3*0.10 + 2*0.15 + 2*0.10 = 2.95`; multiply by 20 for /100.

**Shortlist:** unlikely on this version in a competitive field of 25-30 finalists across all problems, not 25-30 for Problem 3 (`_briefs/perceptron.txt:239-255`). This is a judging opinion, not a measured admission probability. Actual applicant quality, score normalization, and the shortlist cutoff are **UNVERIFIED**. The MVP itself is appropriate: the brief permits synthetic known-counterfactual data and asks for standard OPE plus a concrete disagreement with naive before/after (`:61-80`). Do not inflate the claims to compensate for the MVP being deliberately modest.

## 2. Methodology: what is valid, and what it actually identifies

### The 2x2 calculation is valid under stated identification conditions

Define, for period $t$ and policy $p$,

$$
V_{tp} = E_{X\sim P_t}\left[\sum_a \pi_p(a\mid X)m_t(X,a)\right].
$$

This requires well-defined policy versions, reward consistency/no relevant interference, appropriate conditional exchangeability, and action support in each log used for OPE. Estimated nuisances require their corresponding consistency/regularity assumptions. A deterministic logger cannot identify unsupported target actions just because an ESS number can be printed.

Let $D_0=V_{01}-V_{00}$ and $D_1=V_{11}-V_{10}$. Then

$$
S_\pi=\tfrac12(D_0+D_1),\qquad
I=D_1-D_0,\qquad
S_E=\tfrac12[(V_{10}-V_{00})+(V_{11}-V_{01})].
$$

Consequently $V_{11}-V_{00}=S_\pi+S_E$. These are exactly the policy and interaction formulas in `components/decomposer/decompose.py:73-86`. The code correctly constructs differences **on the same rows** before computing their standard errors, preserving within-period covariance. Combining the two periods in quadrature is appropriate if those period samples can be treated as independent and nuisance estimation does not introduce omitted first-order dependence.

**The interaction is meaningful as effect modification by the realized environment.** It says the policy contrast differs between periods. It is not automatically an experimentally identified causal effect of "season", nor evidence that the policy caused the season. Shapley allocates half the interaction to each main contribution. Do **not** add interaction as a third waterfall bar on top of both Shapley contributions. The diagram's written identity gets this right; its claimed integrated mix split is the problem in A3.

### Direct versus total effect under feedback

$D_1$ is the reward contrast between policies **holding the realized after-period traffic distribution fixed**. Calling this a short-run, traffic-standardized policy contrast is safer than an unqualified "direct causal effect". A natural/direct-effect mediation interpretation needs further causal assumptions about post-treatment contexts.

If deploying the new policy changes who arrives, total effect instead compares the new policy on its induced audience with the old policy on the audience that would have arrived had it remained deployed. The latter after-period distribution is not supplied by a before-period sample without additional assumptions. The simulator explicitly constructs it through `Xa_cf` (`components/simulator/sim.py:94-111`); real logs do not.

The feedback table correctly distinguishes these targets: at feedback 1, the after-period contrast is about +8.9 percentage points and the total effect about +14.6, while DR averages +9.1 (`eval/results/decomposer_review.md`, feedback `1.00` row). **Credit for saying total effect is unidentified.** But $S_\pi$ is an average of before- and after-population contrasts, not simply that after-population direct effect. The abstract must not use those labels interchangeably.

### The DR density-ratio formula has the right orientation and population identity

For old-policy before logs, let $\rho=dP_1/dP_0$, let $\widehat\rho$ estimate that ratio, and let $\widehat q$ estimate before-period reward. The transport functional is

$$
T(\widehat q,\widehat\rho)=E_{P_1}\left[\sum_a\pi_0(a\mid X)\widehat q(X,a)\right]
+E_{P_0,A\sim\pi_0}\left[\widehat\rho(X)\{R-\widehat q(X,A)\}\right].
$$

For fixed nuisance functions, its bias is $E_{P_0}[(\rho-\widehat\rho)\sum_a\pi_0(a\mid X)(\widehat q-m_0)(X,a)]$, a product of density-ratio and reward-model errors. Thus the population expression is correct if either nuisance is correct, subject to support/integrability and the specified old-policy logging distribution. Estimated nuisances additionally require the appropriate sample-splitting or empirical-process argument. **No action weight is missing in that particular on-policy-before setting.** For an arbitrary before logger $\mu_0$, the correction would additionally need $\pi_0(A\mid X)/\mu_0(A\mid X)$.

`_density_ratio` correctly adjusts classifier odds by the training sample prior, `tr.sum()/len(X_after)` (`components/decomposer/decompose.py:29-39`). This is not a reversed-ratio bug. Implementation and validation limitations remain in A9.

### The OBD re-enactment is a legitimate benchmark, not a real rollout experiment

Masking two cells of concurrent A/B logs is a useful retrospective test of whether OPE can reconstruct an observed within-period contrast. The official OBD README actually calls the dataset an A/B test [S4]. That satisfies a reasonable interpretation of the MVP, **provided** policy definitions, populations, timestamps, slots, and reward semantics are aligned.

It does not demonstrate what happens when an entire system is switched, when its audience changes, or when an adaptive policy would learn a different history. "Both arms observed" is not "all causal assumptions verified". Empirical concurrent CTR differences are noisy reference estimates, not known population parameters. A2, A7, and A8 are the material qualifications.

### S1's cancellation is correct; the label attached to it is not

In the deploy direction, with $B_2$ the after-period BTS reward mean and $R_2$ the concurrent Random mean,

$$
\widehat D=B_2-\widehat V_R(B_2),\quad
\widehat D_{\rm ref}=B_2-R_2,\quad
\widehat D-\widehat D_{\rm ref}=R_2-\widehat V_R(B_2).
$$

`eval/run_obd_slice.py:212-217` correctly cancels the shared $B_2$ term and combines the remaining OPE/reference uncertainties, rather than blindly adding two full effect variances. For a fixed target and independent arm samples, this is the right first-order construction. In the rollback direction the target is estimated from the reference BTS data, so the independence assumption needs additional work (A8).

A confidence interval for **estimate minus noisy reference** containing zero is a non-rejection of inconsistency. It is neither proof of accuracy nor the event that the estimator's own interval contains the reference point. The reporting code substitutes the former for the latter.

## 3. Numbered issues

### A1 - blocker: "6/10 cases with 0 wrong" changes the endpoint

**Evidence:** `eval/apply_gate_obd.py:57-67` imports Analysis 2 `consistent` and Analysis 3 `S1_ci_contains_0`; `:73-80` relabels these booleans as `dr_ci_contains_truth`, "answered, correct", and "WRONG (CI missed truth)". `eval/build_headline.py:70-78,114-121` and `deliverables/round1-abstract.md:30` carry that interpretation into the pitch.

**Concrete counterexample from the committed JSON:** deviation `2019-11-24→2019-11-25`, rollback direction:

| Quantity | Clicks per 1,000 |
|---|---:|
| Concurrent reference effect | -1.711185 |
| DR effect estimate | -0.884493 |
| DR's own nominal 95% interval | [-1.681243, -0.087744] |
| S1 interval for estimate minus reference | [-0.050005, +1.703388] |

The gate answers this case. S1 passes, but the estimator's interval **does not contain the reference point**. Source: `eval/results/obd_slice_deviation_floor.json`, that pair's `B_rollback_to_Random` object; the gate table labels it "answered, correct".

If "wrong" literally means failing containment of the reported reference point, one of the six answered rows fails, not zero. If it means a confident wrong **sign**, that is a third endpoint requiring separate computation. The negative estimate here has the right reference sign; I am not calling it a proved wrong causal decision. The present label is invalid under its own stated definition.

**Required correction:** separate `s1_nonrejection`, `reference_point_in_interval`, and `confident_wrong_sign`; never label non-rejection "correct". Add this exact case as a regression fixture. This is not a cosmetic wording preference.

### A2 - blocker: the 0.1% "accuracy" claim lacks a matched-policy reference

**Evidence:** `eval/preregistration_obd.md:18-20,31-38` evaluates both a static initial-prior policy and an hourly empirical policy against the same BTS CTR. `eval/run_obd.py:28-38` constructs the static policy solely from prior beta parameters. `eval/results/obd_slice_summary.md`, Analysis 1, reports strong within-window propensity changes and only 0.631 correlation between window-average frequencies and the static-prior probabilities. Nevertheless `deliverables/round1-abstract.md:26` calls the static estimate accurate to 0.1% of "its on-policy truth".

The arithmetic is real: the static DR value is `0.004886863168247104`; its reported relative discrepancy from the BTS mean is `0.0007002354580625852`, or **0.0700%**, rounded to 0.1%. The target-policy equivalence is not established. Two different policies can have nearly identical average CTRs.

This is not just my suspicion about a library: the opened upstream `BernoulliTS` documentation describes `is_zozotown_prior` as parameters used **at the start** of data collection, and exposes subsequent reward-count updates [S5]. It does not prove that this static prior equals the complete deployed schedule.

Hourly frequencies are a useful approximation, not a magic repair: they discard within-hour changes and any relevant history; differing traffic weights between arms also matter. **Withdraw "0.1% accurate" until the evaluated policy and on-policy reference are actually matched.** Report a discrepancy against a reference, or label this an approximate-target diagnostic.

### A3 - major: the advertised decomposer mixes two different estimands and two different implementations

**Evidence:** `decompose()` returns $D_1$ and an old-policy-ordered environment split (`components/decomposer/decompose.py:52-66`). `shapley()` returns $S_\pi$, $S_E$, and interaction, with **no mix split** (`:73-86`). `architecture/contracts/contracts.py:135-153` gives these different output types, and `Verdict` still accepts only the v0 `Decomposition`. The abstract and diagram present a unified Shapley-plus-DR-mix system (`deliverables/round1-abstract.md:18`; `deliverables/architecture.md`, Decomposer node).

If $E_{\rm old}=V_{10}-V_{00}$, then

$$
S_E=E_{\rm old}+\tfrac12 I.
$$

The implemented old-policy mix plus response terms sum to $E_{\rm old}$, **not** $S_E$, unless interaction vanishes. Attaching them to the Shapley environment bar would misallocate half the interaction.

The real-data headline uses after-effect estimate +1.3984 against reference +1.2559 per 1,000. The corresponding Shapley policy estimate/reference are +1.3448/+1.4361 (`eval/results/obd_slice_summary.md`, halves and Shapley tables). These are different questions, not competing roundings.

The diagram also says the verdict abstains if a log behind **either** OPE cell fails the gate. The committed gate application evaluates after-log weights only (`eval/apply_gate_obd.py:60-67`). It does not establish a two-cell Shapley certificate.

**Required correction:** pick an explicit primary estimand, preferably $D_1$, and label Shapley secondary. Keep the ordered mix split separate, or implement a coherent environment allocation for both policy paths. Enforce the gate on every cell required by the reported functional. The core Shapley identity itself is not wrong.

### A4 - major: numerical calibration used only simulations, but experimental design was post-OBD

**Evidence:** `eval/results/gate_obd_posthoc.md:3` explicitly admits OBD outcomes and ESS values were seen before calibration. Git history confirms:

| Evidence | Commit | Author time, IST | Committer time, IST |
|---|---|---|---|
| OBD preregistration | `f88de64` | 13:06:47 | 13:06:48 |
| Preregistered OBD results | `3cec249` | 13:16:04 | 13:17:00 |
| Deviation/day-pair failures | `fd89d9c` | 13:31:23 | 13:31:24 |
| Gate calibration and rule | `b4e95ae` | 13:39:56 | 13:39:58 |
| Post-hoc OBD gate application | `0c255ec` | 13:41:36 | 13:41:37 |

The gate JSON records an earlier run timestamp of 13:39:26. No consequential issue turns on the preregistration's one-second author/committer difference; it plainly precedes committed results.

**Credit:** `calibrate_gate.py` does not read OBD, and the post-hoc report discloses the chronology. **No credit for prospective validation:** choosing the diagnostics, reward sparsity, propensity-noise model, search grid, acceptance targets, or story after seeing OBD failures is still data-informed design. Freezing the result before reapplying it to already-inspected data does not create a holdout.

Moreover, all 56 ESS/reward-threshold combinations are selected and scored on the same simulator runs (`eval/calibrate_gate.py:37-38,69-81`). The reported 0.96 is training/calibration performance. The novelty sentence "thresholds fixed on simulation before being checked on real truth" (`round1-abstract.md:39`) suppresses the crucial chronology.

**Required correction:** call both the gate design and current OBD application exploratory. Freeze a revised protocol, then evaluate once on unexamined settings/data.

### A5 - major: 5% ESS/n is a selected heuristic, not a reliability certificate

**Evidence:** the threshold is a genuine optimum of the committed 56-rule search under its chosen constraints. Recomputing `gate_calibration_runs.csv` gives **339/720 answered, 326/339 covered = 0.96165**. Thus I do not allege an invented threshold or invented count.

But the calibration has one world seed, `n=10,000`, 10 actions, two policy temperatures, three reward offsets, and no null/harmful policy configurations (`eval/calibrate_gate.py:32-36`; `architecture/contracts/contracts.py:162-176`). All 720 true effects are positive, ranging approximately 0.00741-0.27076. There are **zero confident wrong-sign outcomes even before any filtering**. This bank cannot demonstrate that the gate reduces wrong-direction deployment decisions.

The chosen `tau_r=0` means the advertised rewarded-row threshold is **disabled** (`eval/gate_rule.json:2-4`). ESS/n also ignores the reward/residual distribution relevant to DR, absolute effective sample size, and clustering. A 5% rule learned at 10,000 rows does not have a universal interpretation at millions of rows. The successful halves deploy example has ESS about 25,395, but the gate refuses it because its fraction is only 0.0092 (`eval/results/gate_obd_posthoc.md`, halves A row). That refusal must accompany the highlighted success.

There is a smaller baseline bug: `ungated = evaluate(df, 0, 0)` **retains** the mean-weight z filter (`eval/calibrate_gate.py:55-56,77`). Truly unfiltered coverage is **660/720 = 0.91667**, whereas the stored "ungated" calculation is **637/693 = 0.91919**. Both round to 0.92, hiding the denominator change.

The opened ESS methodological paper explicitly describes substantial approximations behind the usual importance-sampling ESS [S8]. A mean-weight check is a diagnostic, not a proof of correct propensities, exchangeability, or adequate support.

**Required correction:** evaluate selective coverage and decision error on independent null, near-null, negative, sparse, shifted, and misspecified settings, with varying sample sizes/action counts. Report absolute ESS and effective reward information, and label an empirical threshold empirical.

### A6 - major: repeated after-period estimates and forking paths inflate the apparent evidence

**Evidence:** in `eval/results/obd_slice_deviation_floor_summary.md`, both `2019-11-24→2019-11-26` and `2019-11-25→2019-11-26` use the identical November 26 after logs, target, after-effect estimate, reference, CI, and gate decision. This follows directly from `eval/run_obd_slice.py:212-217` and `eval/apply_gate_obd.py:63-67`.

"3/3 deploy failures caught" therefore comprises **two distinct after-period failures**, one counted twice. The ten gate rows contain eight distinct evaluation instances after this exact duplication is removed; six answered rows become five distinct answered instances. Those remaining instances still share observations. Day-pair **naive gaps and Shapley values** can differ, so retaining the full pair table is appropriate; treating the repeated after-effect outcomes as independent validation is not.

The floor-start deviation is sensible and honestly disclosed: changing 47 ms adds a complete day (`eval/results/obd_slice_deviation_floor_summary.md:5`). It is not preregistered confirmation. Likewise the journal records that S1/S2 drift strengths were increased after smoke checks to achieve sign flips before freezing the bank (`thought_node.md:106-109`). That is fine for a constructed demonstration, not evidence that a generic deployment commonly fools naive evaluation.

DR was preregistered as primary, which limits estimator cherry-picking. Remaining multiplicities include two target reconstructions, directions, temporal splits, effect definitions, simulator configurations, and gate selection. Preregistration does not eliminate these. The S1 claim-withdrawal rule (`eval/preregistration_obd.md:63-65`) needs an explicit primary-versus-secondary interpretation, not retrospective rescue by a gate.

**Required correction:** identify the independent evaluation unit, preserve all rows, summarize unique after-period tests separately, and distinguish confirmatory, exploratory, and illustrative claims. Use a predeclared familywise procedure for confirmatory multiple tests, or explicitly avoid a familywise guarantee.

### A7 - major: sorted category shares do not establish population balance

**Evidence:** the preregistered balance check reports TVD about 0.36 for every feature. `eval/obd_balance_posthoc.py:25-38` collapses unmatched labels into "other" and compares sorted frequency vectors, then concludes this is a labelling artifact and the populations match. `eval/results/obd_balance_posthoc.md` states that conclusion without qualification.

The small label-free distances are evidence **consistent with** an encoding/missing-category problem, not proof. Sorting destroys category identity: populations assigning 90% and 10% to opposite categories have identical sorted shares despite TVD 0.8. Similar marginal shares also do not prove joint, outcome-relevant, or time-specific balance.

The slicer hashes pandas-inferred object values without an explicit canonical string/missing-value representation (`eval/obd_zip_slice.py:113-122`), so an ingestion artifact is plausible. Raw label correspondence is **UNVERIFIED** here. I am not asserting that OBD's A/B assignment was defective; its own documentation supports the A/B framing [S4].

**Required correction:** inspect original labels and missingness encodings, document any legitimate mapping, then recompute balance on canonical values and common time/slot weights. Until then retain the preregistered caveat as unresolved, not dismissed.

### A8 - major: real-data uncertainty omits dependence and target/model estimation uncertainty

**Evidence:** `eval/run_obd_slice.py:47-50` bootstraps already-computed row scores. The hourly target is estimated from all BTS action rows (`:123-127`), while the reference CTR uses BTS rewards. The reward-model folds are random rows (`:72-81`), and CTRs use row-level Wald standard errors (`:43-44`).

For a fixed target and cross-fitted DR with suitable independent data, score bootstrapping can be justified. It is not automatically valid for an adaptive logger, repeated users, multiple slots from the same recommendation, or a target estimated from the very reference sample. In the latter case, target-estimation variance and estimate/reference covariance are omitted. Not reading the click column when reconstructing a policy does not guarantee independence from reward history if the policy adapts to prior clicks.

There is also an unambiguous baseline issue: bootstrapping the DM predictions alone ignores reward-model training uncertainty. The near-zero-width DM intervals in Analysis 2 are not credible uncertainty for a fitted policy-value estimate. A cross-fitted prediction is not, by itself, a valid influence function for an arbitrary fitted DM estimator. `components/estimators/ope.py:61-71` similarly assigns the DM predictions and Switch-DR scores a generic interval interface without accounting for model-estimation error or truncation bias.

**Required correction:** specify the inferential target and sampling unit; use joint cluster/time-block score calculations or resampling appropriate to that target, with group-aware cross-fitting and target reconstruction handled explicitly. Give DM a justified variance calculation/refit bootstrap or stop displaying its prediction-only CI as sampling uncertainty. Preserve the correct S1 cancellation described above.

### A9 - major: the DR mix term is conditionally correct but under-tested and not fully cross-fitted

**Evidence:** `v_mix_old()` fits the outcome model on **all before rewards**, then evaluates residuals on those same rows (`components/decomposer/decompose.py:42-49`). Only the density-ratio classifier is cross-fitted. The test scenario changes Gaussian context means with common covariance (`components/simulator/sim.py:49-54`), a favorable family for logistic density-ratio estimation.

The +0.57 versus -0.01 percentage-point mix biases are real in the selected nonlinear-along-mix-axis setting (`eval/results/decomposer_review.md`, final misspecification row). They show one useful branch of robustness, not both: misspecified outcome regression with a favorable ratio model. They do not establish robustness to ratio misspecification or weak context overlap.

I am **not** claiming that an in-sample finite-dimensional logistic nuisance makes the estimator necessarily inconsistent; regular parametric arguments may suffice. I am saying the general cross-fitted/plug-in-any-model story and its finite-sample reliability are not established by this code.

**Required correction:** cross-fit the outcome residual correction as well, declare the before logger must equal the old policy, and test the four cases: reward correct/ratio wrong, reward wrong/ratio correct, both correct, both wrong. Exercise context-support failure separately. If accepting general before loggers, add the required action ratio.

### A10 - major: "exact truth" and "95% coverage" overstate a small, correlated simulator study

**Evidence:** `ground_truth()` averages conditional reward expectations over Monte Carlo contexts and latent variables, and the experiment drivers use `n_mc=200_000` (`components/simulator/sim.py:94-111`; `eval/run_decomposer_review.py:160`; `eval/run_sim_bank.py:108`). The DGP is known; its reported population expectations are **Monte Carlo references**, not exact integrals. No per-target Monte Carlo standard errors are committed in the reviewed result objects.

All 22 decomposer configurations use 20 sampling seeds and default `world_seed=7`; the drift -1.0 and feedback 0.0 configurations even duplicate the same run outputs. Pooled Shapley policy containment is **419/440 = 95.23%**; interaction containment is **409/440 = 92.95%**. Per-configuration policy containment ranges 90-100%; after-effect coverage falls to 80% and 85% in intermediate feedback settings. Those are empirical counts, not a universal 95% statement.

The project's own C7 target requires at least 200 seeds (`architecture/components.md:50`), not 20. Even 19 successes out of 20 independent repetitions has an approximate 95% Wilson interval of **[76.4%, 99.1%]**. Shared worlds/seeds across configurations mean pooling them is not 440 independent tests of generalization.

A further subtlety: even at `nonlinearity=0`, the outcome model is not exactly logistic-linear after integrating out the simulator's uniform latent reward term (`components/simulator/sim.py:55-63`); the `RewardModel` "well specified" docstring is too strong. Correct propensities can still protect DR. An oracle reward model is needed to isolate the reward-correct branch rigorously.

**Required correction:** call the references Monte Carlo approximations, record their uncertainty, test fresh world seeds, meet the per-condition seed budget for claimed coverage, and show conditional coverage/width rather than just pooled percentages.

### A11 - major: the sensitivity result is not a general DR/Shapley certificate

**Evidence:** `components/sensitivity/msm.py:27-50` bounds `mean(R) - V(target)` using Hajek/IPW, an odds-ratio box, and a percentile bootstrap. It does not consume arbitrary influence terms and does not construct joint sensitivity bounds for the two-cell Shapley functional. The ADR itself correctly calls DR sensitivity stretch (`architecture/adr/001-spike.md:22`), while the abstract's plug-compatible certificate language is broader.

The inverse-weight interval and reversing value-bound endpoints for a difference are sensible. Zhao et al. and Kallus-Zhou are real, relevant prior art [S6, S7]. But applicability of their full assumptions and guarantees to this precise adaptive/multi-action implementation is **UNVERIFIED** by an abstract-only literature check.

The ten successful MSM runs use the first grid value above a **sampled** maximum odds ratio: sampled `gamma_true=6.941931475580438`, hence Gamma 7 (`eval/run_sim_bank.py:36,63-67`; committed `MSM_HAJEK` rows). A Monte Carlo maximum is not the global bound required by an MSM. From this simulator's bounded `u` and exponential tilt, a conservative global odds-ratio bound is `exp(2*kappa)`; for kappa 1 this is about 7.389, so Gamma 10 is a safe existing grid point unless a tighter bound is proved. I am not claiming that 7.389 is the tight supremum.

Ten out of ten is a descriptive success, not validation of 95% coverage. Gamma-star 1.25 is the first crossing on a coarse grid, not an estimate of the actual confounding strength. Dense logged propensity values also do not automatically rule out unlogged overrides or wrong probability semantics.

**Required correction:** label this an after-period Hajek-MSM sensitivity analysis, state its assumptions, validate at a proved confounding bound, and report grid resolution and substantially more repetitions. Do not claim an integrated Shapley certificate until it exists.

### A12 - major: the novelty claim is an integration claim dressed as a methodological gap

**Evidence:** `architecture/adr/001-spike.md:10-11` awards novelty 4/5 on the basis of no matching tool found. `deliverables/round1-abstract.md:37-42` contrasts the proposal with a single-value baseline, while citing but not benchmarking pairwise OPE. `research/landscape.md`, section 6, already identifies the 2026 diagnostic-protocol paper as the closest framing, but the abstract omits it from its closest-work sentence.

Delta-OPE already makes policy **differences** the object of estimation and supplies variance reduction. Zhang et al. already combine importance weighting, cross-environment counterfactuals, and Shapley attribution. Oaxaca-Blinder-type decompositions already separate distribution/composition and response-structure changes. Standard ESS diagnostics are not a new certificate. The 2026 Lee et al. paper already sells an ordered diagnostic protocol against misleading offline lift, using a public OPE benchmark and a synthetic generator [S1-S3, S8-S9].

The bounded additional search found OPEN's explicit active/passive non-stationarity distinction [S10], directly relevant to the feedback story, and confirmed future-policy OPE [S11]. Neither abstract establishes the identical product combination; neither does absence of such wording prove firstness.

**Required correction:** claim a transparent, evaluated **integration/protocol** and demonstrate its incremental decision or explanatory value against paired DR/Delta-OPE with ordinary diagnostics. Stop treating a negative search result as evidence of algorithmic novelty.

### A13 - minor: presentation uses ambiguous units and a favorable word counter

**Evidence:** the template/rendered text matches exactly under an independent substitution check. The renderer's alphanumeric-token rule reports **885** words. The same body has **942 whitespace-separated tokens**; the whole Markdown file has 990. The brief says **suggested** 600-900 words, not a hard disqualification rule (`_briefs/perceptron.txt:267-305`), so I am not inventing a rules violation.

Nevertheless, trim the actual submission rather than defending a bespoke count. `round1-abstract.md:48` gives +0.09/+1.58/-0.01/+0.57 without saying **percentage points** or naming the selected setting. `:46` states drift thresholds as if universal rather than restricted to the tested grid. `deliverables/architecture.md` includes a dense graph plus two figures; actual one-page pagination is **UNVERIFIED**.

**Required correction:** use explicit units, identify selected settings, remove the generated-file maintenance preamble from the submission copy, and render one actual page for the optional diagram.

### A14 - major: team readiness is not established, and the October plan has no validation freeze

**Evidence:** `round1-abstract.md:53-54` names Ashish and two TBD teammates, with October summarized as full OBD plus confidence sequences. `_briefs/perceptron.txt:338-342` explicitly scores stated skills and milestones; `:374-376` gives October 15 registration close and October 31 Round-1 submission.

I cannot verify the named person's claimed skills from this repository; they are team-provided claims, not independently established credentials. I certainly cannot award readiness credit for two unnamed skill sets. The method is laptop-feasible, but a list of components is not a staffed execution plan.

**Required correction:** identify actual members and evidence of relevant work, or explicitly narrow the achievable scope until staffed. Prioritize repaired estimands, reference matching, and a frozen holdout before confidence sequences. Do not fabricate teammates or credentials.

## 4. Headline evidence audit

This checks every substantive numeric family in the abstract, not merely whether a matching string exists in `headline.json`. The rendering/allowlist mechanism (`eval/check_docs.py:35-54`) catches textual drift; it does not establish that a number measures the claim attached to it.

| Abstract claim | Committed evidence and independent check | Judgment |
|---|---|---|
| 660,904 Random rows; BTS CTR 4.89/1,000; DR within 0.1%, IPW within 1.1% | `obd_slice.json`, `window`, `a2`, `a2.P-static`; Analysis 2 table. Static DR relative discrepancy is 0.0700%, which rounds to 0.1%. | Arithmetic verified; policy-matched accuracy **not established** (A2). |
| Re-enacted +1.62 naive, +1.26 reference, +1.40 DR, 29% overstatement | `obd_slice.json`, `a3_halves.A_deploy_BTS`; exact after-effect values are +1.255914 and +1.398422/1,000, DR CI [1.128125, 1.668718]. | Correct rounded descriptive comparison. Not Shapley or total effect; gate abstains here (A3, A5). |
| Reverse -1.25 naive, -1.26 reference, -1.70 DR | `obd_slice.json`, `a3_halves.B_rollback_to_Random`; DR -1.702483, CI [-2.354830, -1.050137]/1,000. | Supported as a noisier, less accurate point comparison against the reference. "Naive is right" should remain descriptive. |
| 3/3 day failures, ESS/n 0.05%, 6/10 answered, 0 wrong | Deviation pair objects; `gate_obd_posthoc.json`; A1's explicit counterexample. Lowest fraction is about 799/1,479,442. | Counts derive from S1; repeated cases and endpoint substitution invalidate the claimed interpretation (A1, A6). |
| Synthetic -5.6 naive, +7.5 truth/DR, RMSE 0.6; wrong sign 30/30 | `sim_bank_runs.csv`, `scenario=S1_drift_masks_gain, estimator=DR`: naive -0.0557633; reference 0.0752486; DR 0.0748488; RMSE 0.0057613. | Arithmetic verified; designed simulator case and Monte Carlo reference. Its DR interval contains the reference in **28/30**, not a guarantee. |
| Shapley intervals cover 95% | `decomposer_review.json`, all 22 `shap_cover` fields, each 20 seeds: 419/440. Interaction: 409/440. | Correct pooled rounding; underspecified scope and precision (A10). |
| Hidden override: DR bias -6.9 points, coverage 0%; MSM 10/10; Gamma-star 1.25 | `sim_bank_runs.csv`, S4 DR: bias -0.0686425, 0/30; ten `MSM_HAJEK` rows all contain reference, median first-grid crossing 1.25. | Descriptive counts verified. Gamma level, Monte Carlo maximum, and estimator scope must be stated (A11). |
| 84 hours; top-cell median propensity ratio 16 | `obd_slice.json`, `window.hours`, `a1`: 20/20 cells exceed 1.5; median ratio 16.06. | Numeric statistic supported. It does not by itself reconstruct an adaptive evaluation policy or prove a particular update mechanism (A2). |
| 13 drift levels; sign thresholds -0.25/-0.75; DR RMSE <=0.6 points, naive up to 26.2 | `decomposer_review.md`, drift table; `decomposer_review.json`, drift records. At -0.50 naive is correct in only 5% of seeds. | Supported **on the tested grid/world**. Not a general threshold theorem. |
| Feedback +9.1 estimate, +8.9 direct, +14.6 total | `decomposer_review.json`, `feedback1.00`; feedback table. | Supported for that setting; intermediate feedback coverages are 80% and 85% (A10). |
| Misspecification +0.09 DR bias vs +1.58 DM; -0.01 mix bias vs +0.57 | `decomposer_review.json`, `nonlinmix2.0`; final misspecification table row. | Supported after multiplying reward rates by 100: **percentage points**, one selected setting (A9, A13). |
| Gate: 36 configurations, 0.96 answered coverage, worst 0.65, answer rate 47% | `gate_calibration_runs.csv`, `gate_rule.json`; recomputed 326/339 covered, 339/720 answered; worst cited config 13/20. | In-sample calibration, not held-out reliability. "Ungated" still has a z filter (A4-A5). |

## 5. Unsupported or over-strong abstract wording: safe replacements

These are replacements for specific statements, not a rewritten abstract. Preserve the result provenance when editing `round1-abstract.tmpl.md`; do not edit the rendered file directly.

| Quote / location | Why too strong | Safe replacement |
|---|---|---|
| "separate what the decision caused from what the world did anyway" (`:7`) | The environment bucket can include policy-induced audience changes. | "Separate the short-run policy contrast on observed traffic from changes in traffic and response; total effects through audience feedback are not identified." |
| "When the new policy is greedy, the old policy's actions are rare in the new logs" (`:10`) | Deterministic zero support is an identification failure, not just heavy tails. | "Near-greedy logging makes supported off-policy estimates unstable; unsupported target actions cannot be identified without additional modelling assumptions." |
| "each returning per-round influence terms, so any interval or sensitivity method plugs in" (`:17`) | DM uncertainty and the separate raw-log MSM implementation do not support this generality. | "Paired DR scores support asymptotic intervals; a separate Hajek-MSM module assesses confounding sensitivity of the after-period contrast." |
| "environment change (split into user-mix shift, via a doubly robust density-ratio estimate, and response drift)" (`:18`) | That split belongs to the old-policy ordering, not the implemented Shapley environment contribution. | "Shapley reports policy and environment contributions, with interaction already allocated between them. Separately, an old-policy-ordered decomposition splits environment change into mix and response terms." |
| "An overlap gate on ESS/n, effective number of rewarded rows, and a mean-weight test" (`:20`, formatting omitted) | The fitted effective-reward threshold is zero and therefore inactive. | "The current exploratory rule filters on ESS/n and mean-weight diagnostics; effective rewarded rows are reported but their fitted threshold is inactive." |
| "DR estimates the Thompson-sampling policy's click rate within 0.1% of its on-policy truth" (`:26`) | Static target and deployed reference are not matched. | "The static-prior DR estimate differs by 0.07% from the concurrent BTS CTR; this is an approximate-target diagnostic, not a verified policy-value accuracy result." |
| "against a true effect of +1.26, overstating it by 29%" (`:28`) | Noisy concurrent reference; after-period target, not total/Shapley effect. | "Against the concurrent after-period CTR contrast of +1.26/1,000, the naive point estimate is 29% larger. DR estimates +1.40/1,000, but the current gate abstains on this case." |
| "answers 6/10 cases with 0 wrong" (`:30`) | It counts non-rejections as correct; one answered interval misses the reference point. | "Six of ten listed cases pass the gate and all six pass S1; one of those six nominal intervals misses the reference point. Cases overlap and this analysis is post hoc." |
| "synthetic, exact truth, 30 seeds" (`:31`) | Known DGP, Monte Carlo expectations. | "Synthetic, known DGP with a Monte Carlo reference, 30 sampling seeds." |
| "Shapley intervals cover 95% in simulation" (`:34`) | Pooled, small per-condition samples; interaction differs. | "Shapley policy intervals contain the Monte Carlo reference in 419/440 runs over 22 settings of one world; independent-world coverage remains to be tested." |
| "The MSM bounds contain the truth in 10/10 runs" (`:35`) | Omits the selected Gamma and limited repetition count. | "At Gamma 7, Hajek-MSM intervals contain the Monte Carlo reference in 10/10 runs of one confounded setting; validation at a proved confounding bound is pending." |
| "thresholds fixed on simulation before being checked on real truth" (`:39`) | Hides that OBD failures were already known. | "The gate was designed after inspecting OBD failures, numerically calibrated on simulations, and retrospectively applied to OBD; fresh validation is planned." |
| "our arXiv search found no switch attribution with abstention" (`:42`) | Negative search is not substantiated novelty, and closest protocol work is omitted. | "We integrate existing pairwise OPE, Shapley attribution, and diagnostics into an auditable switch-analysis protocol; we do not claim a new estimator or a priority result." |
| "naive has the right sign for drift >= -0.25" (ASCII rendering of `:46`) | Reads beyond the measured range/model. | "On the tested 13-point drift grid in one simulator world, naive has the right sign at every tested point from -0.25 through +1.50." |
| "policy-term bias +0.09 for DR vs +1.58 for DM; doubly robust mix-term bias -0.01 vs +0.57" (ASCII rendering of `:48`) | Units and selected condition missing. | "At nonlinear strength 2 along the mix-shift axis, biases are +0.09 versus +1.58 percentage points for the policy contrast, and -0.01 versus +0.57 points for the ordered mix term." |
| "Everything above runs today on a laptop CPU" (`:52`) | Future confidence sequences/covariate benchmarking and an integrated Shapley verdict are not demonstrated. | "The committed batch estimators and evaluation scripts are CPU-based. Confidence sequences, covariate benchmarking, and the integrated interactive report remain planned." |

## 6. Novelty comparison and the ten highest-impact fixes

### What survives comparison with actually opened prior art

| Prior work | Verified overlap | What could still distinguish this entry |
|---|---|---|
| **Delta-OPE**, Jeunen & Ustimenko, RecSys 2024 [S1] | Pairwise policy-value estimation; exploiting covariance; variance-optimal additive control variate. The "we estimate a difference, not a value" pitch is already occupied. | Retrospective environment accounting and a clearly evaluated reporting protocol, not subtraction or shared-row variance reduction. |
| **Zhang et al., ICML 2023** [S2] | Distribution mechanisms as players; cross-environment counterfactual performance; importance weighting; Shapley attribution. | A policy-switch-specific implementation and benchmark with transparent failure/abstention semantics. No claim that Shapley plus weighting is new. |
| **Oaxaca-Blinder / decomposition methods** [S9] | Separating between-group or over-time outcome changes into explanatory distribution/response components is established. | Reliable estimation of the otherwise unavailable policy cells, useful diagnostics, and demonstrated decision support. The accounting identity itself is not novel. |
| **Standard importance-sampling ESS** [S8] | Long-established diagnostic with important approximations, not a distribution-free error certificate. | A prospectively validated selective-inference/decision protocol for this task. The present threshold search does not establish that. |
| **Lee et al., 2026, "When Offline Evaluation Misleads"** [S3] | Ordered diagnostics before trusting lift; public OPE benchmark plus synthetic generator; explicitly methodological rather than algorithmic contribution. | This entry focuses on before/after policy/environment attribution rather than delayed-reward alignment/learnability and personalization-premium interpretation. Its novelty paragraph should say so. |
| **OPEN**, Chandak et al., NeurIPS 2022; arXiv 2023 [S10] | Explicit active, passive, and hybrid non-stationarity; counterfactual OPE under action-dependent change. This is important prior framing for the feedback problem. | A simpler retrospective contextual-bandit attribution tool rather than prediction of future performance under a higher-order stationarity model. |
| **OPFV**, Shimizu et al., 2025 [S11] | OPE under non-stationarity using temporal structure and importance weighting; future policy value from past logs. | Retrospective attribution with observed after logs, rather than forecasting an unobserved future environment. This work is already in the landscape and is not a newly discovered omission. |

The additional search was deliberately bounded. I opened the selected records myself through the official arXiv API. The API confirms OPEN's NeurIPS 2022 venue in its comment; OPFV's venue is **UNVERIFIED**, so I call it a 2025 arXiv work. Full-text absence of an identical 2x2-plus-gate method is **UNVERIFIED**. No exhaustive novelty/priority claim follows from this search.

### Top 10 concrete fixes, ranked by expected score impact

These are feasible tasks before **31 October** for three students using a laptop CPU. Effort estimates are planning judgments, not measured runtimes. Do not spend the remaining time adding a fashionable estimator before repairing the measurements.

| Rank | Fix and exact deliverable | Issues addressed | Practical scope |
|---:|---|---|---|
| 1 | **Repair outcome semantics end to end.** Add distinct S1/noncoverage/wrong-sign fields to results, headline builder, and report; preserve the November 25 rollback fixture; replace "0 wrong" with the literal metric. Summarize eight unique evaluation instances separately from ten listed rows. | A1, A6 | Existing JSON/CSV suffices for the first correction; no dataset rerun needed. |
| 2 | **Withdraw the static-prior 0.1% accuracy headline.** Declare the precise target version/schedule and how its on-policy reference is matched. Until matched, use "discrepancy from concurrent BTS CTR". Make the known Uniform target the clean real-data reconstruction example; label empirical BTS targets approximations. | A2, A7 | Documentation plus a policy/probability/time audit on existing data. No need to fetch all campaigns to remove a false implication. |
| 3 | **Freeze the estimand and wire the report to it.** State "primary: after-period traffic-standardized contrast; secondary: symmetric Shapley attribution". Keep the ordered mix split separate, display interaction without double counting, and gate both counterfactual cells before reporting Shapley. Show the halves A example as abstained under the current rule. | A3, A5 | Small component/contract/report changes and deterministic identity fixtures. |
| 4 | **Turn the gate into a prospective experiment.** Freeze diagnostics, threshold search, loss function, and stop rule before new results. Hold out world seeds and configurations, not just additional samples of world 7. Include null, near-null, harmful, 80-action, rare-click, misspecified, and varying-n cases; report coverage, interval width, answer rate, and wrong-sign rate with denominators. | A4-A6, A10 | A bounded CPU bank; target at least 200 repetitions per claimed coverage condition, modest n, and one or two workers. Use unseen OBD campaigns/blocks only after verifying they were not already inspected. |
| 5 | **Fix uncertainty at the right sampling unit.** Preserve same-row delta covariance and S1 cancellation. Group folds/resampling by appropriate time/slate/user units where identifiable; handle estimated hourly policies and reference statistics jointly. Give DM a refit/justified variance calculation. Publish a side-by-side iid versus dependence-aware interval table. | A8 | Aggregate score/block sufficient statistics instead of bootstrapping millions of raw rows repeatedly. State limitations if user/slate identifiers are unavailable. |
| 6 | **Resolve, rather than explain away, the hash imbalance.** Compare raw values/dtypes/missing sentinels, canonicalize them before hashing, document mappings, and rerun TVD on common labels and common hour/slot weights. Retain the caveat if not resolved. | A7 | A targeted ingestion audit and small summary tables; no new modelling infrastructure. |
| 7 | **Validate both DR mix robustness branches.** Cross-fit outcome residuals; use an oracle reward mean and oracle density ratio to test a 2x2 nuisance-correctness matrix, including deliberately wrong-ratio distributions and support failures. Declare the before-logger restriction. | A9, A10 | Reuse the simulator; analytic conditional reward integration or accurate oracle predictions avoid inventing another learned model. Report bias/RMSE for every branch. |
| 8 | **Reposition novelty and compare against the right baseline.** Replace the "no tool found" claim with the integration claim in section 5. Add a baseline of paired DR/Delta-OPE plus ordinary ESS diagnostics and the same uncertainty method. Measure the incremental benefit of decomposition/gating at comparable answer rates; cite Lee 2026 and OPEN explicitly. | A12 | One comparison table and a narrower abstract; do not implement unrelated sequential algorithms merely to name-drop them. |
| 9 | **Make sensitivity claims numerically defensible.** Use a proved Gamma bound or the safe next grid value, report Monte Carlo reference uncertainty, increase confounded repetitions, and label Gamma-star a grid crossing for the after-period Hajek estimand. Test at Gamma 1 and around the crossing; keep Shapley sensitivity as future work unless implemented. | A10, A11 | Existing code paths; efficient binary-reward aggregation can keep bootstrap work small. |
| 10 | **Produce a credible submission, not an internal status dump.** Identify real team members/roles by registration close; schedule estimand/reference fixes by Oct 10, protocol freeze by Oct 15, held-out analysis by Oct 24, and final 600-900-word submission plus one rendered diagram by Oct 28. Cut confidence-sequence scope if it competes with these. Explicit units throughout; label future work future. | A13, A14 | Writing, staffing, and a realistic freeze schedule. These dates are proposed milestones, not existing commitments. |

## 7. Primary sources actually opened

Access date for all sources: **2026-10-04 IST**. ArXiv abstract pages often returned only titles through the text extractor, so I opened the official API records to read full abstracts and metadata. I did **not** treat cached landscape assertions or search snippets as independently verified papers. The paper comparisons above are limited to what these opened records establish.

- **S1:** Olivier Jeunen and Aleksei Ustimenko, *Delta-OPE: Off-Policy Estimation with Pairs of Policies*, [arXiv:2405.10024v2](https://arxiv.org/abs/2405.10024v2). Opened abstract/API: explicitly estimates policy differences, exploits positive covariance, and characterizes a variance-optimal additive control variate; RecSys 2024 short-paper venue in the comment.
- **S2:** Haoran Zhang, Harvineet Singh, Marzyeh Ghassemi, Shalmali Joshi, *"Why did the Model Fail?": Attributing Model Performance Changes to Distribution Shifts*, [arXiv:2210.10769v3](https://arxiv.org/abs/2210.10769v3). Opened API abstract explicitly defines a distribution-player cooperative game, importance-weighted counterfactual values, and Shapley contributions; ICML 2023 in the comment.
- **S3:** Sang Su Lee, Vineeth Loganathan, Shishir Dash, Vijay Raghavan, *When Offline Evaluation Misleads: A Diagnostic Protocol for Reward and Policy Selection in Delayed-Feedback Contextual Bandits*, [arXiv:2608.11560v1](https://arxiv.org/abs/2608.11560v1). Submitted Aug 12, 2026; API comment says accepted at the fifth Workshop on End-to-End Customer Journey Optimization, KDD 2026. Abstract explicitly distinguishes reward alignment and learnability and calls the contribution methodological rather than algorithmic.
- **S4:** Yuta Saito et al., *Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation*, [arXiv:2008.07146v5](https://arxiv.org/abs/2008.07146v5), and the opened [official dataset README](https://raw.githubusercontent.com/st-tech/zr-obp/master/obd/README.md). The README identifies an A/B test, item-position probability semantics, three display positions, and hashed user/item features. It does not establish this project's raw-category mapping.
- **S5:** Opened upstream [`obp/policy/contextfree.py`](https://raw.githubusercontent.com/st-tech/zr-obp/master/obp/policy/contextfree.py), `BernoulliTS` documentation, `select_action`, `update_params`, and `compute_batch_action_dist`. The prior is documented as the start-of-collection prior; sampled action ranks use current reward/action counts plus priors. This is a live `master` source, not a pinned production-logging implementation.
- **S6:** Nathan Kallus and Angela Zhou, *Confounding-Robust Policy Improvement*, [arXiv:1805.08593v3](https://arxiv.org/abs/1805.08593v3). Opened API abstract: worst-case regret against a baseline over propensity-weight uncertainty sets and associated guarantees. Direct full-text equivalence to this repository's implementation is **UNVERIFIED**.
- **S7:** Qingyuan Zhao, Dylan S. Small, Bhaswar B. Bhattacharya, *Sensitivity analysis for inverse probability weighting estimators via the percentile bootstrap*, [arXiv:1711.11286v2](https://arxiv.org/abs/1711.11286v2). Opened API abstract: marginal sensitivity model, asymptotically at-least-nominal confidence coverage, percentile bootstrap, and linear-fractional optimization.
- **S8:** Victor Elvira, Luca Martino, Christian P. Robert, *Rethinking the Effective Sample Size*, [arXiv:1809.04129v2](https://arxiv.org/abs/1809.04129v2), International Statistical Review 2022 per the API journal reference. Opened abstract critiques assumptions and approximations behind the standard importance-sampling ESS; it does not endorse a 5% threshold.
- **S9:** Nicole Fortin, Thomas Lemieux, Sergio Firpo, *Decomposition Methods in Economics*, [NBER Working Paper 16045](https://www.nber.org/papers/w16045), June 2010. Opened page metadata and abstract: surveys methods since Oaxaca and Blinder for decomposing between-group differences or changes over time, including identification assumptions. Used as a literature overview, not as an assertion that the original 1970s papers implemented contextual-bandit OPE.
- **S10:** Yash Chandak et al., *Off-Policy Evaluation for Action-Dependent Non-Stationary Environments*, [arXiv:2301.10330v1](https://arxiv.org/abs/2301.10330v1). Opened API abstract/comment: active/passive/hybrid non-stationarity, a higher-order stationarity assumption, OPEN, and importance-weighted instrumental-variable regression; NeurIPS 2022 venue.
- **S11:** Tatsuhiro Shimizu et al., *Off-Policy Evaluation and Learning for the Future under Non-Stationarity*, [arXiv:2506.20417v1](https://arxiv.org/abs/2506.20417v1). Opened API abstract: OPFV, temporal structure, importance weighting, and future-value evaluation/learning. No venue claim is made here.

Official API batches opened: [S1-S4](https://export.arxiv.org/api/query?id_list=2405.10024,2210.10769,2608.11560,2008.07146), [S6-S8](https://export.arxiv.org/api/query?id_list=1809.04129,1805.08593,1711.11286), [S10-S11](https://export.arxiv.org/api/query?id_list=2301.10330,2506.20417).

## 8. The three hardest finals questions

### 1. "Which causal quantity have you identified, and why should I believe the word 'policy' means the same thing in all four cells?"

A strong answer must write down $D_1$, $S_\pi$, and the total-feedback effect **as different targets**; state action support, exchangeability, reward consistency/interference, and policy-version/history assumptions; explain why the observed after audience does not identify the counterfactual old-policy audience; and show that interaction is already half-allocated in Shapley. It must identify which OBD cells are masked, what auxiliary BTS action traces are used, and why the reference matches the evaluated policy. It must acknowledge that an initial TS prior is not automatically the adaptive deployed schedule. Finally, derive the DR mix correction and explain exactly when omitting an action weight is legitimate. A pretty waterfall is not an answer. See A2, A3, A7, A9.

### 2. "You promise an honest 'can't tell'. Show me its out-of-sample error rate, and explain why your zero-error claim survives this November 25 row."

A strong answer must distinguish point-reference containment, consistency-test non-rejection, and confident wrong-sign decisions; reproduce A1's counterexample without evasion; disclose the pre-OBD/post-OBD design chronology; and present a genuinely frozen, independent assessment of the complete selection rule. It must include null/near-null/harmful cases, abstention cost, dependence-aware intervals, and coverage/decision-error uncertainty at an explicit sampling unit. Explain why 5% is an empirical choice, not a theorem, and why the headline halves success is currently refused. Even zero failures in six **independent** trials would leave a one-sided 95% binomial upper bound of about 39% on failure probability; these six rows are not independent. See A1, A4-A6, A8, A10.

### 3. "What have you contributed beyond Delta-OPE, Zhang's Shapley attribution, and the 2026 diagnostic protocol, and what experiment could falsify your claimed advantage?"

A strong answer must name the existing contributions correctly, claim integration rather than inventing priority, and show an apples-to-apples baseline: paired DR/Delta-OPE with the same interval construction and ordinary diagnostics, evaluated on the same frozen cases. It must predefine the increment being tested: fewer harmful accepted decisions at a matched answer rate, better attribution recovery, or a demonstrably clearer actionable audit. It must be willing to show that naive is adequate, the gate abstains, or the additional decomposition buys nothing in some regimes. An actual known-policy, matched-population benchmark and a small set of independently held-out worlds are stronger than ten more post-hoc configurations. If total feedback effects are the real business question, state the additional randomized/switchback or structural design needed instead of pretending one-step OPE answers it. See A6, A7, A11, A12.

**Bottom line:** keep the problem framing and the correct paired OPE/Shapley algebra. Remove the false semantics around truth and correctness, then earn the word "certificate" on data and settings the design has not already seen.

## Re-score of v3 (commit 2371208)

**Reviewer:** the same independent GPT-6 Astra hostile judge. **Clock:** started 2026-10-04 14:20:34 IST; assessment timestamp 2026-10-04 14:25:42 IST, both obtained from `TZ=Asia/Kolkata date`. **Pinned submission:** `237120839fefe66671f645cbfe2e17f9bad87616`. The requested fetch/rebase brought this worktree to `ceb93a6`; the relevant project, brief and PLAYBOOK files were unchanged between that commit and the pinned submission. Citations in this appendix refer to **v3**, not the original review snapshot. The original assessment above is preserved.

I read the dispositions as claims to check, not as evidence that the issues were resolved. I inspected the new preregistration, committed results and generating code, and independently recomputed small CSV/JSON aggregates and template substitution using the standard library. No project program, experiment, test, dataset download or external literature search was run for this re-score. Raw-data reproduction, the absence of unrecorded local experiments, and final one-page rendering remain **UNVERIFIED**. The previously opened literature supports the unchanged novelty assessment; this appendix makes no new literature-priority claim.

**New score: 69/100 = 3.45/5, up from 59/100. Shortlist judgment: borderline, still lean no.** V3 is materially better, not merely better at apologizing. It states distinct estimands, withdraws the static-policy accuracy claim, separates the main endpoints and adds a genuinely prospective simulator assessment on the available git evidence. However, the actual verdict still changes which estimand answers the question, the advertised near-null validation contains effects above ten percentage points, and two of the three team members still do not exist in the stated readiness evidence.

**Blocker status:** I retire the original A1/A2 submission blockers for the narrowed abstract claims. There is no new blocker-level finding in this re-score; there are substantial remaining **major** issues. This is not approval to call the complete product a validated certificate. In particular, A3 and A11 remain material report-contract defects, while new A15/A16 qualify the new validation claims. "ACCEPTED" in a disposition is not synonymous with "fixed".

### Official rubric

The same official weights and scale apply (`_briefs/perceptron.txt:308-354`). The brief explicitly says Round 1 judges the plan rather than requiring a completed prototype (`:305-307`). I score the now-coherent proposed method more highly without pretending the current reporting implementation is finished.

| Criterion | Weight | Original / 5 | V3 / 5 | V3 weighted / 5 | Hostile justification |
|---|---:|---:|---:|---:|---|
| Problem Understanding & Relevance | 20% | 4 | **4** | 0.80 | The primary after-period contrast, secondary Shapley allocation, separate ordered mix split and feedback limitation are now explicit (`deliverables/round1-abstract.md:9-20`). Strong understanding; no fifth point while the product's decision still changes the question after inspecting support (A3). |
| Technical Soundness & Feasibility | 25% | 3 | **4** | 1.00 | The proposed decomposition is coherent and CPU-feasible; both-cell gating and scoped after-period sensitivity are appropriate in principle. Cross-fitted mix residuals and the uncertainty corrections are real changes. This is a **plan** score, not a production-readiness score: the verdict/sensitivity mismatch and incomplete adaptive-data inference prevent a five (A3, A8, A9, A11). |
| Innovation / Novelty | 20% | 3 | **3** | 0.60 | Honest integration framing and inclusion of Lee/OPEN fix the sales pitch, not the absence of demonstrated incremental value. Paired DR plus ordinary diagnostics is named as a baseline but not yet beaten at a comparable answer rate (`deliverables/round1-abstract.md:39,48`). |
| Clarity & Structure of Abstract | 10% | 3 | **4** | 0.40 | Explicit units, scoped estimands, a disclosed refused flagship example and a substantially shorter body are genuine improvements. The pre-registration scope, wrong-sign denominator and near-null label still need surgery (`:28-43`; A4, A15, A16). |
| Impact & Rigor of Evaluation Plan | 15% | 2 | **3** | 0.45 | The frozen held-out test and honest DM correction earn a point. The holdout tests only the after-period DR gate, has eight seeds per setting, an uncontrolled "near-null" group, and no wrong-sign failures even without filtering. Real-data target/reference and dependence caveats remain (A5-A10, A15). |
| Team Fit & Readiness | 10% | 2 | **2** | 0.20 | The October freezes are now credible milestones. They do not supply the missing two members' skills or ownership. One named member plus two TBDs still cannot establish the skill mix the rubric asks for (`deliverables/round1-abstract.md:51-52`; `_briefs/perceptron.txt:338-342`). |
| **Total** | **100%** | **2.95 / 5** | | **3.45 / 5 = 69 / 100** | **+10 points: technical +5, clarity +2, evaluation +3.** |

Calculation: `4*0.20 + 4*0.25 + 3*0.20 + 4*0.10 + 3*0.15 + 2*0.10 = 3.45`. A 69 is not an estimated admission probability. The actual competition, normalization and cutoff remain **UNVERIFIED**; the shortlist still comprises only 25-30 teams across all problems (`_briefs/perceptron.txt:239-255`).

### New evidence: what earns credit, and what it does not prove

**The held-out test is not the old calibration table in a new wrapper.** Git records `d9de82e` at author time **14:10:45 IST**, committer time **14:10:48**, and the result commit `4e5ca34` at **14:17:14 / 14:17:15**. The registration **and the evaluation script** were already present at `d9de82e`; the result artifacts were not. The registration, script, numerical rule and fixed guard implementation are unchanged through v3. The available record supports prospective testing of the frozen procedure. It cannot prove that nobody ever ran an uncommitted experiment, and I do not invent such an allegation.

Independent recalculation from `eval/results/gate_holdout_runs.csv` gives:

| Readout | Exact count | Rate |
|---|---:|---:|
| Runs answered | 818 / 1,536 | 53.26% |
| Reference contained, answered | 771 / 818 | 94.25% |
| Reference contained, all runs | 1,404 / 1,536 | 91.41% |
| Reference contained, abstained | 633 / 718 | 88.16% |
| Confident wrong sign, answered | 0 / 818 | 0 observed |
| Confident wrong sign, all runs | 0 / 1,536 | 0 observed |

These agree with `eval/results/gate_holdout.json`, `pooled`, and `gate_holdout.md:6`. I checked every recorded containment event, wrong-sign event and gate decision against its numeric inputs. The published success criteria **are met**: pooled answered coverage at least 0.90; each adequately populated effect group at least 0.85; wrong-sign rate no worse than ungated (`eval/preregistration_gate_holdout.md:18-23`; `eval/validate_gate_holdout.py:72-75`). Do not retroactively replace those criteria because an inconvenient subgroup appeared.

But passing a predeclared **90%/85%** acceptance rule does not establish **95%** coverage, conditional reliability in every setting, or improvement in wrong-sign decisions. There were zero such decisions to prevent. The study evaluates `delta_vs_onpolicy("DR", ...)` on after logs, not the Shapley/before-period fallback used by the report (`eval/validate_gate_holdout.py:37-48`; `components/report/verdict.py:33-41`). Thus it does not validate the complete report-selection procedure.

Two post-hoc diagnostic breakdowns of the committed holdout illustrate its scope, not new confirmatory tests. At temperature 1 the gate answers **766/768**, with **724/766** containment; at temperature 4 it answers only **52/768**, with **47/52 = 90.38%** containment. Most difficult-temperature cases are refused. In sparse-reward settings, containment is **377/409 = 92.18%** among answered runs. With only eight sampling seeds per configuration and two `world_seed` values, do not treat 1,536 correlated cross-configuration runs as 1,536 independently sampled deployment environments. Source: `gate_holdout_runs.csv`, grouped by `_T1.0_`, `_T4.0_` and `_off-4.0_`; configuration construction in `eval/validate_gate_holdout.py:27-34`.

**The real-data corrections also matter.** The original November 25 rollback counterexample is now correctly reported as S1 non-rejection **yes**, own-interval reference containment **no**, confident wrong sign **no**. The aggregate table correctly distinguishes ten listed rows from eight distinct instances; its latter summary is five answered, four reference containments, and two distinct S1 failures refused (`eval/results/gate_obd_posthoc.md:5-9`, November 25 rollback row). These remain overlapping, noisy-reference comparisons, not causal coverage experiments.

The new hour-block interval for the deploy contrast is **[+0.934, +1.780] per 1,000**, compared with the old row-level **[+1.128, +1.669]**. Its point remains +1.398. The DM refit standard error is **0.195558 per 1,000**, versus **0.000735** previously: a **266.06-fold** change. The resulting DM-minus-reference interval is **[-0.560, +0.215] per 1,000**, so the old apparent DM inconsistency disappears under that refit calculation. Source: `eval/results/obd_block_bootstrap.json`, `halves_A` and `dm_refit`; corresponding Markdown rows and final paragraph.

These are useful robustness checks, not complete dependence corrections. `block_ci()` resamples exchangeable whole hours with fitted scores held fixed; it does not preserve dependence **between** hours. The hourly target is reconstructed once, and reference uncertainty is not jointly propagated in those DR block intervals. The separate DM refit resamples **rows**, not hours (`eval/obd_block_bootstrap.py:26-32,42-46,57-69,77-85`). No user IDs does not justify pretending that cross-hour dependence or target estimation disappeared.

### Disposition of every original A-item

"Fixed" below refers to the original defect, not proof that its entire surrounding method is valid. Remaining defects are major unless identified otherwise.

| Item | Status | Independent assessment of v3 |
|---|---|---|
| **A1** | **Fixed** | The original endpoint substitution is removed. S1, own-CI containment and wrong sign are computed separately; the counterexample no longer receives a false "correct" label (`eval/apply_gate_obd.py:58-67,83-98`; `eval/results/gate_obd_posthoc.md:5-9`). The new mixed-task wrong-sign denominator is a separate, narrower problem, A16 below. |
| **A2** | **Fixed** | The static-prior "0.1% of its on-policy truth" claim is withdrawn. V3 explicitly calls the target approximate and distinguishes it from the deployed-policy reference (`deliverables/round1-abstract.md:28`). This fixes the original overclaim by narrowing it, **not** by establishing matched-policy truth. "Differs from the arm CTR" remains safer than "estimates ... within 0.9%". |
| **A3** | **Partly fixed** | The abstract and diagram correctly separate the after contrast, Shapley allocation and old-policy mix split (`deliverables/round1-abstract.md:18-20`; `deliverables/architecture.md:38-44`). Both-cell gating exists. But the report chooses **Shapley** when both cells pass and **before-period effect** when only that cell passes, rather than maintaining the declared primary after-period target (`components/report/verdict.py:33-41`). The committed OBD deploy demo prints **worked**, using the before-period contrast, while the abstract says the gate abstains (`eval/results/demo_verdicts.md`, OBD A row). The output labels the fallback, so this is not concealed, but a labelled change of question is still a change of question. |
| **A4** | **Partly fixed** | Genuine prospective simulator evidence now exists, with frozen code and rule predating results. The OBD gate report honestly states the post-OBD design chronology (`eval/results/gate_obd_posthoc.md:3`). However, the abstract's claim that the **integrated abstaining protocol** was "tested pre-registered against real concurrent-arm references" still merges preregistered base analyses with later gate design (`deliverables/round1-abstract.md:39`). |
| **A5** | **Partly fixed** | Varying sample size/action count and harmful policies is real progress. The inactive reward floor, absolute ESS and corrected no-gate baseline are disclosed; zero-information/non-finite guards exist. The 5% rule remains a selected heuristic; there is no measured reduction in wrong-sign decisions, no proper near-null stratum (A15), and no held-out test of noisy propensities/feedback/hidden overrides in the complete verdict. `eval/preregistration_gate_holdout.md:4-12`; `eval/results/gate_holdout.md:6`; `components/report/gate.py:39-53`. |
| **A6** | **Partly fixed** | The evidence table reports eight distinct instances and shared observations. The abstract still spotlights **3/3** deploy failures and **6/10** answered rows without telling the reader that an after-period result is duplicated (`deliverables/round1-abstract.md:32`; `eval/results/gate_obd_posthoc.md:7-9`). The new holdout was preregistered; the old OBD cases did not become independent or confirmatory retroactively. |
| **A7** | **Partly fixed** | Raw-string inspection rules out the simplistic explanation that these differing labels were solely created by pandas' type inference. The new report correctly retains **UNRESOLVED**, and so does the abstract (`eval/obd_raw_labels.py:22-35`; `eval/results/obd_raw_labels.md`, final paragraph; `deliverables/round1-abstract.md:53`). The inspected prefixes are not a documented category mapping or a complete common-window joint-balance audit. Do not revive the old sorted-share conclusion. |
| **A8** | **Partly fixed** | Whole-hour resampling and DM refitting are genuine improvements, including a disclosed reversal of the DM consistency conclusion. They are not a joint adaptive-policy/cluster/model uncertainty procedure. The flagship abstract still shows the narrower unlabeled row-level half-width despite advertising hour-block intervals (`deliverables/round1-abstract.md:23,30`; `eval/obd_block_bootstrap.py:26-32,42-46,77-85`). |
| **A9** | **Partly fixed** | Outcome residuals are now out-of-fold and the on-policy-before restriction is explicit (`components/decomposer/decompose.py:42-56`). The refreshed nonlinear-mix bias, **-0.0237 percentage points**, supports the rounded -0.02 headline (`eval/results/decomposer_review.json`, `nonlinmix2.0.mix_dr_bias`). The reward-correct/ratio-wrong robustness branch and context-support failures are still untested; the four-way nuisance experiment is expressly deferred (`reviews/2026-10-04-dispositions.md:21`). |
| **A10** | **Partly fixed** | "Monte-Carlo reference" and **419/440** are accurate in the abstract. The count independently matches the refreshed CSV. However, it still comes from 22 settings with 20 seeds each, not the new held-out study of the after-period gate. No reference Monte Carlo SEs or adequate per-condition coverage precision are supplied. The diagram still says **exact truth / real truth** (`deliverables/architecture.md:22-23`), and C7 still asks for at least 200 seeds (`architecture/components.md:50`). |
| **A11** | **Partly fixed** | The abstract scopes sensitivity to the after-period contrast and calls the tipping point a grid crossing (`deliverables/round1-abstract.md:24,37`). Gamma 10 is defensible by the bound/nesting argument below. But the report still attaches that after-period curve to a Shapley verdict and says it "would overturn it" (`components/report/verdict.py:33-48`; `eval/demo_verdicts.py:44-47`; `eval/results/demo_verdicts.md`, S4 row). Ten runs remain descriptive, not general 95% coverage validation. |
| **A12** | **Partly fixed** | The abstract now claims integration and cites the closest protocol/non-stationarity work. That fixes the unsupported priority framing. Demonstrating value beyond paired DR plus ordinary diagnostics remains future work; naming that baseline is not conducting the comparison (`deliverables/round1-abstract.md:39,48`). Historical ADR self-scores do not establish originality. |
| **A13** | **Partly fixed** | Explicit units and ordinary word count are much better: **893 whitespace words** from the "Problem & theme" heading through the end, **910** including the project-title line. This is not a hard-limit violation: the brief's range is suggested and title conventions vary. Template substitution matches exactly. Maintenance instructions are outside the intended body. One-page diagram pagination is still **UNVERIFIED**, and its truth labels are not corrected (`deliverables/architecture.md:21-23`). |
| **A14** | **Partly fixed** | Estimand, protocol, holdout and submission milestones are now dated. Two unnamed teammates with no stated skill evidence remain two unnamed teammates (`deliverables/round1-abstract.md:51-52`). Credit the schedule, not fictional staffing. |

### New issues exposed by the new evidence

#### A15 - major: the "near-null" holdout group is a scorer-quality label, not a near-null effect test

`eval/validate_gate_holdout.py:27-33` defines `near_null` by new/old scorer qualities **0.45/0.40**. The policy perturbations are independently drawn, so nearby quality coefficients do not guarantee nearby policy values (`components/simulator/sim.py:40-42`). The committed group contains effects from **-0.1571 to +10.3803 percentage points**. Of its 64 configurations, **38** have absolute reference effect above **one percentage point**, and **60** are positive. None has an exactly zero reference.

Concrete maximum: `eval/results/gate_holdout_runs.csv:1226`, `w202_near_null_eps0.02_T4.0_off0.0_n5000_K40`, seed 0, has `truth=0.10380320239183344`. The minimum is at `:1186`, `truth=-0.001571441358319943`. Some cases are indeed small; the defect is presenting the entire design label as controlled near-null validation. This does **not** invalidate the aggregate arithmetic or its predeclared success criteria. It invalidates the stronger interpretation that a deliberately bounded near-zero regime has been stress-tested.

**Required correction:** call the existing group a **small scorer-quality-gap configuration**, report its actual effect range, and preserve this run. For a new, separately frozen test, construct distinct policies with a predeclared near-zero value contrast, using design-stage references rather than selecting on evaluation outcomes. Declare the near-null scale and include a meaningful null/near-null decision criterion. Do not rerun and rename until the safety story looks good.

#### A16 - major: "0/6 confident wrong signs" includes two cases for which the code disables the sign endpoint

`eval/apply_gate_obd.py:60` sets `confident_wrong_sign` to false whenever `kind != "effect"`. The two answered Analysis 2 rows are **absolute policy-value** estimates, not switch-effect decisions (`:63-67`). Nevertheless the aggregate divides by every answered row (`:93-98`).

There are **four** answered effect rows, not six; after removing the repeated after-period estimate there are **three** distinct answered effect instances. They have **zero** observed confident wrong signs. Both of the additional value-estimation rows are assigned false by construction. A denominator padded with tasks on which the event is not evaluated is not evidence about safe policy decisions. It also makes the passage under "Whole-day pairs" confusing: the ten-row denominator spans Analysis 2, halves and day pairs, not just the six day-pair rows.

**Required correction:** use **N/A** for wrong-sign policy decisions on absolute-value rows. Report **0/4 listed effect rows, or 0/3 distinct effect instances**, explicitly against noisy reference signs and without an independence claim. Retain **5/6** own-interval containments as a separately defined all-answered-row statistic, or report its distinct-instance counterpart **4/5**. The original A1 non-rejection/coverage substitution is fixed; this narrower denominator problem is not.

### Remaining overclaims and exact safe wording

| Location and quote | Judgment | Safe rewrite / exact change |
|---|---|---|
| `deliverables/round1-abstract.md:43`: "with positive, near-null and harmful effects" | **A15, major.** "Near-null" is not enforced on the effect. | "Across two new world seeds and 192 settings spanning positive and harmful effects plus a small scorer-quality-gap configuration, the gate answered 818/1,536 runs; 771/818 answered intervals contained the reference, versus 1,404/1,536 overall." |
| `:39`: "an auditable switch-attribution protocol that abstains when logs cannot answer, tested pre-registered against real concurrent-arm references" | **A4, major.** This grammatically grants the full abstaining protocol the provenance of the earlier OBD analyses. | "The base OPE analyses were preregistered against concurrent-arm references. The gate was designed after inspecting OBD, applied there retrospectively, and then assessed in a separately preregistered simulator holdout." |
| `:32`: "3/3 deploy cases ... 6/10 ... 0/6 confident wrong signs" | **A6/A16, major.** Duplicate after-period tests and mixed endpoint eligibility still inflate the apparent decision evidence. | "Across eight distinct, overlapping OBD instances, the post-hoc gate answered five; four intervals held the reference. It refused both distinct deploy S1 failures. Among three distinct answered policy-contrast instances, no interval had the confident wrong reference sign." |
| `:18,30`: "Primary estimand: the after-period policy contrast" / "our gate abstains here" | **A3, major integration mismatch.** These are defensible only for the after-period functional, not the current overall product decision. | "The primary after-period contrast is withheld if its gate fails; any before-period contrast is a separate secondary result, never a replacement worked/hurt decision." Implement that contract. In particular, the OBD A demo must not present a primary **worked** result after refusing the primary estimand. |
| `:28`: "DR estimates the Thompson-sampling arm's click rate ... within 0.9%" | **A2 residual wording risk; original blocker retired.** The approximate-target parenthesis is essential, but numeric agreement still is not matched-policy accuracy. | "For an hourly empirical target, DR estimates 4.936 clicks per 1,000 versus the concurrent BTS CTR of 4.890, a 0.935% discrepancy; this is an approximate-target comparison, not verified policy-value accuracy." |
| `:23,30`: "Intervals: Wald and hour-block bootstrap" / "+1.40 ± 0.27" | **A8, major qualification.** The reader cannot tell that the displayed half-width is the narrower row-level result. | "DR gives +1.40 per 1,000; the row-level interval is [+1.13, +1.67] and the post-hoc hour-block interval [+0.93, +1.78]. Both contain the reference and dashboard point; the primary gate abstains." Do not convert the asymmetric block interval into a misleading symmetric half-width. |
| Related output, `components/report/verdict.py:48`: "Hidden confounding of Γ = ... would overturn it" | **A11, major.** The curve pertains to the after-period Hajek contrast, not whichever Shapley/before term was selected. A confidence interval reaching zero also does not show that such a confounder exists or would reverse the effect. | "For the separate after-period Hajek-MSM contrast, the uncertainty interval first includes zero at tested Gamma 1.25." Attach explicit estimand metadata and refuse cross-target reuse. |
| Related diagram, `deliverables/architecture.md:22-23`: "Simulator, exact truth" / "Open Bandit Dataset, real truth" | **A10, major claim inconsistency.** V3's diagram retains the semantics its abstract disowns. | "Simulator, Monte Carlo reference" / "OBD, noisy concurrent-arm reference; policy matching and balance limitations disclosed." The full deliverable must tell one story. |

**Do not withdraw a supported Gamma claim just because the stored bank selected Gamma 7.** For the hidden-override construction, action tilts lie in $[e^{-\kappa},e^\kappa]$. The action-odds ratio is its tilt divided by the nominal-probability-weighted average tilt of the other actions, hence lies in $[e^{-2\kappa},e^{2\kappa}]$ (`components/simulator/sim.py:73-80`). At $\kappa=1$, the conservative cap is $e^2=7.3891<10$. The bootstrap uses identical resampled indices at each Gamma, and the admissible weight boxes expand monotonically (`components/sensitivity/msm.py:27-49`). Therefore containment at Gamma 7 implies containment at Gamma 10 for these same curves. The new **10/10 at Gamma 10** wording is a defensible mathematical implication of the committed results, **not** ten new runs or a coverage guarantee. The outstanding issue is scope and replication, not that arithmetic.

**What would materially raise this score next:** enforce one primary decision target and its own sensitivity statement; replace the mislabeled near-null/pooled safety story with a properly scoped, frozen decision assessment; complete the joint uncertainty and matched-reference audit; and name the real three-person skill mix. The brief's MVP is already satisfied in substance. The remaining score is not hiding in another estimator acronym.
