# Hostile review: Round-1 abstract and H1

**Reviewer:** GPT-6 Astra. **Date:** 4 October 2026.
**Evidence cutoff:** `e76a4b6f17c05e6b4d29efab458e3cd640371448`, including P5 update `892b97e` and E8. The abstract is still draft v0.1. E7, E9 and E10 results are not available at this cutoff; their registration is not a result. File references below are relative to `perceptron-p05-impact-execution/`.

**Verdict: do not submit this abstract unchanged.** The E6 arithmetic supports a small, simulator-specific comparison of a frozen legacy policy. It does not establish successful impact-sensitive braking, a certified live ghost book, unchanged simulator dynamics, or a resolved feedback mechanism. E8 now fails to reproduce the E6 improvement on the validation block. The abstract advertises several of those stronger conclusions anyway.

Severity means: **blocker** = remove or substantiate before submitting the claim; **major** = material methodological/evaluation defect; **minor** = narrower reporting or presentation defect. These are findings about claims and evidence, not instructions to discard an otherwise valid E6 measurement.

## Numbered issues

### 1. [blocker] The winning policy is not the controller described in the abstract, and E8 does not rescue the mechanism

**Evidence:** `deliverables/round1-abstract.md:18,23,30`; `eval/policies/confirm.json:64-75`; `components/execution_agent/execution_agent/policies.py:136-178`; `eval/results/code-review-2026-10-04.md:5-13`. The confirmed arm has QP and legacy feedback enabled, but limit orders disabled. Its before-trade impact estimate is compared with a post-trade reference. The reported brake fires in only 0.02-0.04% of the reviewed decisions; the multiplier is usually approximately 1.2. The schedule feedback reads past own fills, not a measured residual between the observed book and a validated counterfactual.

The new E8 result is **+0.0056 bps [-0.0284, +0.0393]**, not a replication of E6's negative point estimate (`eval/results/E8_ablation_val_attribution.md:9`). Corrected feedback versus QP-only is -0.0122 [-0.0388, +0.0116]; every IS attribution contrast includes zero. There is no demonstrated successful braking mechanism to describe.

**Fix:** identify the measured arm as **"propagator-QP schedule plus legacy front-loading, market orders only."** "Impact-model-based" is defensible as a design description; "the agent detects its footprint and brakes successfully" is not an established result. Put E6 and E8 together, explicitly state that attribution is unresolved, and report E10/H2 regardless of outcome. Do not silently transfer E6's result to the corrected-feedback or touch-limit controller.

### 2. [blocker] The certified, live "ghost book" is unsupported, and its displayed SELL sign is wrong

**Evidence:** `deliverables/round1-abstract.md:17,26,30`; `deliverables/architecture.md:14,29`; `eval/results/calibration.json:95-105`. The committed model has held-out mean-path R2 **-4.1913 for PROBE and -2.8930 for TWAP**; per-seed R2 is also negative, with RMSE approximately **19.4-19.8 cents**. Printing tau = 60 seconds while suppressing those failures is selective reporting. Negative R2 does not prove that random-stream decorrelation, rather than model misspecification, is the sole problem.

For the positive-adverse SELL convention used in `components/tca/tca/metrics.py:55-57`, impact is `twin_mid - observed_mid`. Therefore the estimated no-order mid is **observed mid plus estimated impact**, not minus. `research/components/spike-twins-and-ghost-book.md:24` already states the correct SELL sign. More fundamentally, a scalar mid estimate is not a reconstruction of depth, queues, spreads or a full order book; `components/sim_env/sim_env/world.py:97-98,114-125` defaults to depth-one logs and extracts the touch.

**Fix:** call this an **unvalidated counterfactual-mid estimator prototype**, correct and test the side convention, and distinguish a simulated twin book from the live estimator's actual output. E9's mean-path R2 > 0 would be a preliminary calibration result, not a deployment certificate. Require per-episode/decision prediction error, uncertainty, comparisons against zero-impact/simple baselines, and held-out schedules/regimes before claiming useful live estimation. Either implement a book-level target and evaluation or stop calling the estimator a book.

### 3. [major] RNG synchronization is a coupling choice, not a proof of unchanged market physics or unique causal ground truth

**Evidence:** `components/sim_env/sim_env/world.py:61-106`; `research/components/spike-twins-and-ghost-book.md:8-19`; `architecture/adr/001-spike.md:24-28`. Synchronization replaces each agent's stream at wake-up and separates timing draws. It is applied to treatment worlds too, not merely to an otherwise unchanged null-world evaluator.

A no-order trajectory is an exact counterfactual **conditional on this simulator and this exogenous-randomness mapping**. That does not identify a unique real-world no-order path. Keeping each draw's marginal distribution is not, by itself, a proof that temporal, cross-agent and state-conditional joint distributions are preserved. Wake-up counts can be state-dependent; message-handler draw alignment is not addressed by a per-wakeup reset. The sparse global-oracle exception and seed-collision checks do not establish all these properties.

With genuinely unchanged marginal laws, common random numbers can reduce the variance of a paired difference without biasing its expectation. I am **not** claiming that variance reduction itself biases H1. The missing argument is that these wrappers preserve the relevant laws. If they do not, both the market and average own-impact estimand can change. The primary paired IS comparison also runs inside the modified treatment markets; it is not independent validation of the modification.

E4's own-impact standard deviations really are 0.971447 and 0.164356 bps. But their means are 0.131892 and 0.214429 bps. The mean difference is not evidence of bias at n = 30, and the smaller standard deviation is not proof of unbiasedness. At +60 seconds the synchronized gap standard deviation actually rises from 2.83 to 4.77 cents (`eval/results/nsr_E4_nsr_naive_vs_E4_nsr_sync.md:5-6`).

**Fix:** specify the structural intervention and coupling precisely; audit semantic random draws, wake-up schedules and message-driven randomness. Compare native versus synchronized **null-world** return distributions, autocorrelations, spread/depth distributions, volume and order flow with uncertainty/equivalence tolerances. Separately compare treatment-response curves and primary policy effects under both engines. Say "conditional simulator counterfactual" and "observed paired-dispersion reduction" until those checks are established. Do not optimize NSR alone: its denominator can improve merely because mean impact increases.

### 4. [major] The committed "bit-identical" integrity check accepts a whole tick of error

**Evidence:** `eval/run_experiment.py:46,60,65` samples mids once per second before the window and uses `np.allclose(..., equal_nan=True)`. At the approximately 100,000-cent price, its default relative tolerance permits approximately **one cent**, or **0.1 bp**, already larger than the claimed 0.034 bp saving. The read-only check `np.allclose([100000.0], [100001.0])` returns `True`.

Thus the CSV flag means "sampled mids pass an approximate comparison," not that the worlds, books or even every recorded mid are bit-identical. Matching missing values also passes. This does not demonstrate actual pre-treatment divergence; it demonstrates that the cited test cannot certify the advertised property.

**Fix:** use exact comparisons on appropriate integer/half-tick representations, fail on unexpected missing quotes, and compare event-level pre-intervention book/state digests, including relevant agent/oracle/queue state. Preserve separate labels for sampled-mid equality and full-state identity. Until strengthened evidence is committed, remove "bit-identical" from the abstract and diagram and do not multiply that label across all CSV rows.

### 5. [major] The IS identity is algebraically sound; the causal interpretation of its three terms is not

**Evidence:** `components/tca/tca/metrics.py:32-52` associates a fill with the latest earlier decision and evaluates both mids at that decision time. For a SELL, the code adds and subtracts those mids, so the three terms necessarily sum to arrival-mid IS. The E6 CSV residual is at most approximately **1.01e-5 bps**, consistent with CSV rounding.

For a passive fill at a later time, however, `decision_mid - fill_price` includes the intervening price move, adverse selection and latency as well as spread/book walking. Calling all of it "instantaneous cost" is wrong. A smaller residual does not by itself prove a spread-capture mechanism. Also, the quantity-weighted "drift" component changes with the strategy's timing and fill weights, even when the null path is exogenous. The statement that only the last two terms are controllable (`architecture/adr/001-spike.md:36`) confuses an exogenous price path with endogenous exposure to that path.

An identity would still hold if the supplied twin mids were wrong. The identity test therefore cannot validate counterfactual accuracy.

**Fix:** name the existing terms as decision-time accounting components. Preserve them for E6 reproducibility, but add order-ID/placement-time attribution and fill-time diagnostics separating placement-to-fill movement from execution-price concession against the pre-fill mid. Show decision-time and fill-time results side by side. Do not claim that the passive arm's entire residual saving is spread capture, or that the decomposition alone proves which causal mechanism generated the IS gain.

### 6. [major] The experiment-selection history must be disclosed; E6 is a narrow confirmation, not an untouched end-to-end test

**Evidence and chronology:**

| Record | What it establishes |
|---|---|
| `thought_node.md:103-136` | E3 was inspected at 18 finished seeds: IA_full -0.60 bps [-1.12, -0.10]. At 60 seeds the apparent win disappeared: -0.056 [-0.441, +0.339]. The correction is documented. |
| `thought_node.md:139-167`; E3/E5 CSVs | Synchronization was selected after inspecting the earlier results. E5 reused seeds 1000-1059. IA_sched_only was selected after four comparisons; the log acknowledges that none survived the stated Bonferroni check. |
| Commit `6f6fb2328d5bbdfdb89268f6d363bba502e4c81c`, committed 08:26:53 IST | Contains the H1 hypothesis in `thought_node.md` and the frozen `confirm.json`: n = 200, seeds 1060-1259, one-sided alpha = 0.05, IA_sched_only versus TWAP. The human-readable log heading says 08:30. |
| Commit `b87051e`, committed 09:43:35 IST | First committed E6 CSV/verdict. The intervening feedback fix retains the legacy default; `confirm.json` is unchanged from registration. |
| Commit `416aaa2`, committed 12:53:49 IST | Creates the dedicated `eval/preregistration.md`, after E6. Its H1 entry refers back to the earlier log; this later file is not itself the original registration. |
| Commit `892b97e`; E8 attribution result | The selected policy gives +0.0056 [-0.0284, +0.0393] on validation seeds 100-199. |

The CSV audit finds 800 unique E6 seed-policy rows, exactly four arms on every seed 1060-1259, no missing component metrics, and full completion. None of those seeds occurs in the supplied E1/E3/E4/E5 CSVs. Pairing in `eval/summarize.py:57-60,73-76` is by seed, not by child fill: this avoids fill-level pseudoreplication.

The correct inference is conditional: **if the fixed n and no-E6-peeking rule were followed, selecting a hypothesis on E3/E5 does not invalidate its independent E6 confirmation.** There is no need to Bonferroni-adjust the one preselected H1 merely because exploratory arms exist. It does not license confirmatory claims for every secondary component, policy or newly selected mechanism. Git chronology supports advance recording relative to committed results, but does not independently attest the first run start or every interim inspection.

E8 is a failure to reproduce the improvement on that block, not proof of a sign reversal or genuine seed-regime heterogeneity. An exploratory independent seed bootstrap of E8 minus E6 gives approximately **+0.03963 [-0.00023, +0.07972] bps**; the discrepancy itself is not resolved at 95%.

**Fix:** explicitly retire E3/E5 as exploratory selection data; identify E6 as the first frozen confirmatory comparison and E8 as non-replicating validation evidence. Pin code/config/analysis hashes, seed manifests, run start/end and stopping rules. Report E10 regardless of outcome. Its proposed E5+E6+E10 pool (`eval/preregistration.md:77-79`) includes discovery-selected E5 data and is explicitly descriptive: do not use it as a replacement confirmatory success, and do not hide E8 or report the pool only when it tells the preferred story.

### 7. [minor] The bootstrap supports the narrow mean comparison, but the quoted tail number is not a calibrated p-value

**Evidence:** `eval/summarize.py:39-42`; `eval/results/E6_H1_verdict.md:5-11,22`; `thought_node.md:82,193`. Resampling paired seed differences is the appropriate bootstrap unit under the intended independent-seed model. I independently applied the committed function to the committed CSV:

| E6 quantity | Recomputed value |
|---|---:|
| Mean IA_sched_only minus TWAP IS | -0.03403852 bps |
| Paired-difference sample standard deviation | 0.15692099 bps |
| Percentile 95% CI, 10,000 resamples, RandomState(0) | [-0.05615270, -0.01254960] bps |
| One-sided 95% upper bound, same resamples | -0.01572595 bps |
| Fraction of those bootstrap means at or above zero | 0.0010 |
| Wins | 103/200, or 51.5% |
| Mean own-impact difference | -0.04139410 bps |

The verdict's [-0.0563, -0.0127], -0.0160 and 0.0006 are not the exact output of that resampling specification. These are small discrepancies consistent with a different bootstrap draw sequence; they do **not** overturn the sign result. The newly added `eval/claims.py:17-19,36-47` also uses a fresh RandomState(0), so the reporting paths should be unified.

`P(bootstrap mean >= 0)` from resampling the empirical distribution is a bootstrap tail fraction, not automatically a null-calibrated frequentist p-value or a posterior probability of H1. Six tail draws in 10,000 would also be a noisy basis for strong decimal precision.

**Fix:** publish one deterministic H1 adjudicator with the exact seed order/resampling scheme, assertions for all registered pairs, and the one-sided CI rule. Keep the current CI-based conclusion appropriately qualified. If reporting a p-value, specify a justified null-centered test; otherwise label the value only as the bootstrap tail fraction. Do not turn the rounded 52% win rate into a claim of reliable episode-by-episode dominance.

### 8. [major] Statistical detectability is being substituted for economic importance and baseline strength

**Evidence:** `eval/results/E6_confirm_sync_summary.md:3-12`; `research/landscape.md:55`; `eval/policies/confirm.json`. At a $1,000 share price:

**0.034 bps = $0.0034/share = 0.34 cents/share = 0.34 tick = about $13.60 on a 4,000-share, $4 million parent order.** The reported E6 CI corresponds to approximately **$5.08-$22.52 per parent**. The effect is below one tick but is not mathematically invalid: an average execution price can improve by a fraction of a tick.

The approximately 19% reduction is in the decision-weighted own-impact component, not total shortfall or peak book displacement. Recomputed own-impact means give a 19.03% reduction; an exploratory paired ratio bootstrap gives approximately [9.59%, 29.15%]. Calling the IS saving approximately 10% of own-impact-plus-instantaneous cost uses a selected component denominator. TWAP's total mean IS is actually -0.1984 bps because favorable drift dominates.

There is no committed evidence that the gain survives **incremental** fees, latency changes, liquidity regimes or a matched-front-loading baseline. Equal per-share fees for both market-order policies would cancel; one cannot honestly say that any fee necessarily destroys the difference. The break-even incremental friction is only $0.0034/share.

There is also no demonstrated win against VWAP: the exploratory E6 IA_sched_only-minus-VWAP comparison is **-0.01815 [-0.04009, +0.00425] bps**. An Almgren-Chriss/Obizhaeva-Wang-style benchmark is promised, not present in these result tables.

**Fix:** report dollars, ticks, absolute IS and exposure/tail-risk beside the percentage. Predefine an economically meaningful improvement threshold, not just zero. Compare against a simple front-loaded TWAP matched on inventory-time exposure, QP-only and a calibrated classical schedule; keep the same tactic and completion constraints. Demonstrate buy/sell, size and market-parameter robustness before generalizing beyond this single SELL task.

### 9. [major] E7 can still certify a favorable realism story from unresolved or selectively retained slopes

**Evidence:** current `eval/realism.py:40-70`; `eval/preregistration.md:46-57`. The initial reviewed version lacked the registered paired slope CI; `892b97e` adds it. That old defect is therefore **not** a current finding. The replacement still drops bootstrap draws unless mean impact is positive at every size, then computes a percentile CI only on retained slopes. It reports `boot_valid_frac` but imposes no adequacy gate. This is a distribution conditional on positivity, not an unconditional 95% interval when exclusions are material.

The registration also says non-increasing impact must be flagged, but the current verdict branches never test monotonicity. Finally, overlap of a slope CI with [0.3, 0.7] is not evidence of equivalence to a square-root law: a very wide, uninformative interval passes. A single scaling exponent in one modified simulator cannot validate its joint dynamics or establish native/synchronized equivalence.

**Fix:** assert the complete registered seed-by-size matrix; define and disclose how nonpositive/undefined slope resamples are handled, with an "unresolved" outcome rather than a success claim when the slope is not reliably estimable. Implement the stated non-increasing-impact flag. Use a predeclared precision/equivalence criterion for stronger realism language, and report the full impact curve, amplitude and decay uncertainty. Any changed decision rule must be an explicit amendment, not a silent rewrite of the original registration.

### 10. [major] E8's attribution rule mistakes "not significant" for "not a cause"

**Evidence:** `eval/preregistration.md:22-32`; `eval/attribution.py:25-29,46-55`. The factorial contrasts are interpretable paired contrasts, but the verdict says "QP schedule" when A excludes zero and B does not, and conversely for front-loading. Significance in one contrast and non-significance in another does not establish that their effects differ or that one mechanism is absent. A positive, harmful A also satisfies the code's "QP schedule" condition. The interaction is calculated but ignored by the classification.

E8 currently supports **unresolved effects**, not "front-loading caused the E6 gain," "QP caused it," or "neither matters." Its interaction CI extends to +0.0548 bps; the contrasts have not all been bounded within +/-0.03 bps.

**Fix:** report signed effect sizes, paired joint uncertainty, conditional/simple effects and the interaction. Require a predeclared equivalence margin to claim a component is negligible; do not infer exclusion from failure to reject zero. Keep validation attribution descriptive, as the registration says. Amend the same overstrong rule before interpreting E10 attribution; registering an invalid inference rule does not make it valid.

### 11. [major] E9 does not implement its registered training/holdout split

**Evidence:** `eval/preregistration.md:63` promises fitting seeds 0-19 and evaluating seeds 20-39. `eval/run_experiment.py:73` writes unpadded `seed_<n>.pkl`; `eval/calibrate.py:15-19,44-46` sorts those filenames lexicographically and takes the first half.

For seeds 0-39, the actual fit set is **0, 1, 10-19, 2, 20-26**. The actual holdout is **27-29, 3, 30-39, 4-9**. Seven promised holdout seeds move into fitting. This is directly reproducible by sorting those 40 names; no simulation is necessary.

This does not leak E6 seeds 1060-1259 into calibration. It does invalidate the claim that the named E9 split is implemented. A positive mean-path R2 on the wrong half would not satisfy the registered protocol as written.

**Fix:** select by the numeric `r["seed"]`, assert exact fit/evaluation membership and disjointness, and persist both manifests. Refit/recompute from existing raw episodes under the registered split. If the intended split is changed instead, record an amendment and what was already inspected. Preserve the old E1 calibration for E3-E6 reproduction.

### 12. [major] The novelty pitch repackages known simulation tools and overstates the literature comparison

**Evidence:** `deliverables/round1-abstract.md:30`; `architecture/adr/001-spike.md:16,28,31-33`; opened sources in the source ledger below. Paired experiments, common random numbers, stream/substream synchronization and keyed/counter-based random generation already exist. Reactive market-impact simulation is not new; MarS includes controllable market-impact generation, and ABIDES-MARL studies endogenous strategic liquidity. Olby et al. explicitly decompose slippage into impact and execution risk.

The blanket claim that the named prior papers report "beats TWAP" is also inaccurate: Karpe et al.'s opened abstract says the agent **converges toward TWAP in some scenarios**. Neither the opened abstracts nor a short unsuccessful search establishes that no one has previously synchronized randomness in LOB simulations.

**Fix:** claim an **ABIDES-specific engineering/evaluation contribution**: a documented coupling intervention, quantified finite-sample variance behavior, failure cases, reproducibility and a genuinely validated observable-only estimator if one is eventually achieved. Compare precisely against existing tools, not against the caricature "they merely beat TWAP." Mark priority/absence claims **UNVERIFIED** unless supported by a much stronger search. Do not call a standard variance-reduction idea itself the research invention.

### 13. [major] End-of-run inventory differences are not a demonstrated multi-step feedback mechanism

**Evidence:** `eval/results/E3_test_feedback.md:3-14`; `thought_node.md:135,199`; `deliverables/architecture.md:21,29`. The committed table aggregates positions at 10:05. TWAP momentum-agent change is -1,302 shares with CI [-3,185, +636]; the touch-limit-minus-TWAP momentum difference is +1,221 [-495, +2,836]. Neither resolves the claimed amplification story.

Net holdings do not identify who directly filled each child order or establish the temporal chain "our order -> MM repricing -> momentum response -> later execution cost." Removing an agent population also changes the background market, so an ablation needs a matched null and a careful estimand.

**Fix:** report timestamped response paths, direct counterparties where available, spread/depth changes and response uncertainty. Distinguish direct absorption, subsequent inventory redistribution and price mediation. Treat momentum amplification and the advantage of finishing ahead of it as hypotheses; retain the full matched baseline when ablating an agent type.

### 14. [major] "Keep only significant gains" is not a valid adaptive-search guarantee

**Evidence:** `deliverables/round1-abstract.md:19`; `deliverables/architecture.md:25`; `components/execution_agent/autoresearch/program.md:5-7`; `thought_node.md:201-203`. The keep rule compares against half the incumbent's CI half-width and requires the new policy's CI against TWAP to exclude zero. That is not a paired significance test of candidate minus incumbent. Repeated candidate searches on the same validation seeds also select noise; repeatedly rechecking the same 140-199 block does not make it fresh again. The first ratchet attempt crashed, and no PPO result is committed here.

**Fix:** describe the ratchet as development-time search, not a significance-certified optimizer. Compare candidates directly with the incumbent using paired seed differences, log every attempt, cap/register the search, and reserve genuinely untouched confirmation seeds. Explicitly mark PPO as deferred. Neither a frozen evaluator nor a CI gate removes adaptive overfitting.

### 15. [minor] Simulator scale and completion status are inflated by imprecise wording

**Evidence:** `deliverables/round1-abstract.md:14,19,26,36-50`; `deliverables/architecture.md:5,14-25`; `eval/run_experiment.py:24`; `thought_node.md:97,104-105`. The pinned upstream rmsc04 configuration has **1,116 background trading agents plus one exchange**, not an exchange plus 1,117 trading agents. The runner uses 09:30-10:05: a **35-minute episode**, not a full trading day. The approximately one-second timing is an idle-machine anecdote, not the elapsed cost of paired multi-policy confirmation under load.

The single diagram makes a failed/unvalidated ghost estimator, classical baselines, feedback analysis, a ratchet and the confirmed legacy arm look like one completed pipeline. The text even schedules n = 200 testing as future work after already citing E6.

**Fix:** correct counts and episode duration, give a reproducible throughput measurement with world/seed/policy accounting, and mark every box or sentence **implemented**, **evaluated**, **failed/unresolved**, or **planned**. Keep the E6 arm separate from the proposed full controller. Drop breadth that cannot be supported rather than borrowing credibility from a long roadmap.

### 16. [minor] The team-fit section supplies placeholders, not execution capacity

**Evidence:** `deliverables/round1-abstract.md:3,41,43-50`. Two of three roles are unnamed; no committed evidence establishes ownership or availability for simulator validation, execution theory/statistics and RL. One systems background is not evidence of a staffed quant/RL team. The exam freeze and multiple simulator/RL ambitions make capacity part of feasibility, not an administrative footnote.

**Fix:** replace placeholders with actual confirmed people, relevant evidence and concrete ownership/availability. If the team is currently one person, say so and narrow the scope. Do not award hypothetical teammates credit.

## Rubric score

This scores the committed draft and evidence at the cutoff, not promised fixes or pending E10 results.

| Criterion | Weight | Score / 5 | Weighted points / 5 | One-line justification |
|---|---:|---:|---:|---|
| Problem understanding | 20% | 4 | 0.80 | Addresses endogenous impact, but conflates accounting identities, counterfactual identification and controllable timing exposure. |
| Technical soundness and feasibility | 25% | 3 | 0.75 | A measured legacy policy exists; the advertised braking/ghost pipeline and simulator-law preservation remain unestablished. |
| Innovation beyond starter baseline | 20% | 2 | 0.40 | CRN, keyed randomness and reactive execution simulation are prior art; the proposed distinguishing estimator has failed its available OOS check. |
| Clarity | 10% | 2 | 0.20 | Contradictory signs, built-versus-planned ambiguity and a mechanism description contradicted by the authors' own log. |
| Rigor of evaluation plan | 15% | 3 | 0.45 | E6 has an advance-recorded paired comparison, but discovery reuse, E8 non-replication and protocol/interpretation defects limit its reach. |
| Team fit | 10% | 2 | 0.20 | One identified lead and two placeholders do not substantiate the claimed quant/RL delivery capacity. |
| **Total** | **100%** | | **2.80 / 5** | **56 / 100.** |

## The five changes most likely to raise the score

1. **Replace the mechanism story with an auditable result, and finish the frozen replication.** Put E6 and E8 together now; report E10/H2 either way. Separate legacy front-loading, QP-only, corrected feedback and touch-limit arms. Add a simple front-loaded baseline matched on execution exposure before claiming that learned impact information earns the gain.
2. **Make the counterfactual instrument defensible.** Strengthen pre-intervention identity checks, justify the RNG coupling, test native/synchronized market distributions and response curves, and repair the E7 positivity/monotonicity/precision handling. More seeds cannot repair an unidentified or changed estimand.
3. **Validate a narrowly specified counterfactual-mid estimator instead of claiming a live book.** Correct the SELL sign and E9 numeric seed split; show held-out per-episode prediction error and downstream policy utility against simple alternatives. Publish failure if it fails.
4. **Evaluate the economic objective rather than just a favorable component.** Add fill-time timing/adverse-selection diagnostics, dollars/ticks and incremental-friction sensitivity, risk-matched classical/simple baselines, and a small prespecified buy/sell/size robustness grid. Do not infer causal attribution from an algebraic identity or a non-significant contrast.
5. **Rewrite the submission around one deliverable and an honest novelty/team boundary.** Replace "certified," "exact" and "live" with supported scope; explicitly credit CRN/MarS/ABIDES-MARL and related decomposition work. Confirm people and ownership. Defer PPO/MarS implementation rather than presenting planned breadth as completed sophistication.

## Sentence-level claim audit

The rows below flag sentences or separately identifiable clauses containing an unsupported assertion, a wrong interpretation, or a material qualification omission. Locations refer to the unchanged draft at the cutoff. Explicitly future-facing ambitions are not treated as fabricated results; they must not be rendered as completed architecture.

| Location | Sentence or claim to flag | Required correction |
|---|---|---|
| Abstract:3 | "Numbers marked [dagger] come from committed runs ... reproducible with the commands..." | Link each claim to a versioned artifact and exact analysis; the quoted H1 tail/bounds do not exactly match the committed default resampling calculation, and the one-second full-"day" claim is not the registered task throughput. |
| Abstract:11 | "When we sell ... momentum traders join, value traders absorb." | State this as a possible mechanism; committed net-position evidence does not establish the momentum amplification chain. |
| Abstract:11 | "Part of that displacement decays and part persists..." | Distinguish the assumed propagator model from established simulator evidence; the available failed OOS fit does not identify permanent/transient components reliably. |
| Abstract:11 | "... are bit-identical until our first trade (80/80 runs)." | The cited implementation checks approximate one-second sampled mids, not bit-identical worlds. |
| Abstract:11 | "... decorrelate ... while our systematic impact is only ~3-5 [cents]." | Tie numbers to E1's horizon/arm/statistic; growing gap dispersion is not itself a proof of chaos or an identified universal permanent-impact scale. |
| Abstract:14 | "... exchange plus 1,117 ... agents" and "One simulated day takes [approximately] 1 s..." | Use 1,116 background traders plus exchange; label the measured 35-minute episode and timing conditions. |
| Abstract:15 | Re-keying means twins "differ only through causal responses to our orders." | Qualify by the chosen simulator/coupling and unproved law-preservation assumptions. Native same-seed worlds also differ only after intervention; smaller dispersion is not proof of unique causal truth. |
| Abstract:15 | "This cuts the own-impact noise 6x..." | Report the observed E4 own-impact-component standard deviation on 30 seeds, not blanket removal of impact measurement error; disclose the early-horizon counterexample. |
| Abstract:16 | "Exact cost decomposition ... instantaneous cost (spread, book walking)." | Exact decision-time accounting, not an exact physical/causal split; passive-fill waiting movement is in that residual. |
| Abstract:17 | "The current fit ... gives [tau approximately] 60 s." | Numerically supported but materially incomplete: report its negative held-out R2 beside the parameter. |
| Abstract:17 | "The deployable ghost book (observed mid minus estimated own impact)..." | Wrong SELL sign; scalar estimator, not book reconstruction; observable-only inputs do not certify useful deployment. |
| Abstract:18 | "... feedback that slows down ... above its steady state..." | Not the successful behavior established for the legacy H1 arm. Describe legacy and corrected references separately. |
| Abstract:18 | "... child orders capped at the touch, with the remainder posted passively." | This is the full/tactic variant, not the H1 winning arm, which has `use_limit=false`. |
| Abstract:19 | "... autoresearch ratchet ... (keep only significant gains); PPO ... as a challenger." | Mark development/proposed status; the ratchet rule does not test candidate-versus-incumbent significance and no PPO result is supplied. |
| Abstract:23 | "Agent ... built and confirmed." | Restrict to the specific E6 comparison; do not imply a confirmed full controller or a robust replicated advantage after E8. |
| Abstract:23 | "Synchronised twins make paired CIs 7.5x tighter." | Scope to the observed E3/E5 comparison on reused seeds and modified markets, not a general precision guarantee. |
| Abstract:23 | "... our propagator-optimised schedule beats TWAP by 0.034 bps ... own impact 19%." | The E6 numbers are supported to reporting precision, but the tested arm includes legacy front-loading. State the task, ticks/dollars, decision-weighted component and E8 non-replication. |
| Abstract:23 | "A touch-limited variant cuts instantaneous cost by a third but gives it back in timing." | The decision-time residual falls; drift offsets part of it and the net IS interval includes zero. Do not claim an isolated spread/timing mechanism or complete cancellation. |
| Abstract:26 | "... exact 'book without our order'." | Exact only relative to the specified simulator intervention; distinguish available touch/path data from a validated complete live book. |
| Abstract:26 | "The ghost-book estimator reproduces it live, scored by RMSE..." | Unsupported completion/deployment claim contradicted by available prediction performance; rewrite as an evaluation goal. |
| Abstract:30 | "Prior work ... reports 'beats TWAP' (Karpe ...)." | Karpe's opened abstract reports convergence toward TWAP in some settings; describe each prior contribution accurately. |
| Abstract:30(a) | "We add ... paired twin evaluation with an exact own-impact decomposition..." | CRN/pairing and algebra are not themselves new; define the narrower implementation contribution and conditional estimand. |
| Abstract:30(b) | "... a fix ... which we have not found in the literature." | Stream synchronization is established. Any narrower LOB priority/absence inference remains UNVERIFIED. |
| Abstract:30(c) | "... a deployable counterfactual estimator certified against ground truth." | Delete "certified" and "deployable" as achieved claims; report the failed held-out estimator metric. |
| Abstract:30(d) | "... ablations that attribute savings to schedule, tactic and feedback." | E8 now exists but leaves IS and own-impact attribution unresolved; calculation of contrasts is not successful attribution. |
| Abstract:35,55 | "disjoint train ... validation ... test" / "a held-out test set" | Numeric category separation alone hides test-block reuse: distinguish exploratory E3/E5 from fresh, frozen E6 and planned E10. |
| Abstract:36-38 | Classical baselines, realism and multi-regime/MarS robustness | Acceptable as a plan, not completed evidence. E7/E9 are pending and there is no committed buy-side, classical-baseline or MarS result at this cutoff. |
| Abstract:41 | Team plus two placeholder roles | Explicitly unconfirmed; cannot substantiate team-fit scoring until actual ownership and evidence are supplied. |
| Architecture:5,14-16 | Agent count, `ghost mid = mid - I`, slow-down feedback, touch tactics | Correct the count/sign and distinguish the evaluated legacy arm from the proposed full pipeline. |
| Architecture:20-25 | Exact TCA, feedback analysis, ground-truth labels, AC comparison, significant-gain ratchet | Mark conditional accounting/labels, unresolved mechanism analysis, and planned components. Do not draw them as one evaluated system. |
| Architecture:29 | "both worlds start bit-identical" / "Every difference ... yields the exact counterfactual book ... and per-agent-type feedback" | The integrity check is weaker; coupling-dependent trajectory differences and end holdings do not establish full-book identity or multi-step mediation. |
| Architecture:29 | "... so the same agent could run on a live venue." | Input availability is a portability argument, not evidence of production readiness, useful counterfactual estimation or external validity. |

The basic reactive-market motivation, TWAP implementation, training-only VWAP profile, E6 mean difference, and clearly labeled future ambitions are not rejected simply for being ordinary or incomplete. The defects are the additional causal, novelty, reliability and completion claims attached to them.

## Opened-source ledger and novelty boundary

All external sources below were opened during this review. Paper evidence is **official abstract-level evidence**, read through the arXiv API; no full-text method, theorem or priority claim is inferred from an abstract. Software examples/README excerpts were opened directly. No models, datasets or PDFs were downloaded.

| Source and URL | Verified content relevant to this review | Boundary |
|---|---|---|
| SSJ author-maintained [InventoryCRN example](https://raw.githubusercontent.com/umontreal-simul/ssj/master/src/main/docs/examples/tutorial/InventoryCRN.java) and [stream package documentation](https://raw.githubusercontent.com/umontreal-simul/ssj/master/src/main/java/umontreal/ssj/rng/package-info.java) | Compares two policies with independent versus common random numbers, resets separate streams/substreams between policies, and reports a variance ratio. | Direct primary software evidence that paired CRN and deliberate stream synchronization are established; not a claim that this implements the identical ABIDES wrapper. |
| D. E. Shaw Research [Random123 README](https://raw.githubusercontent.com/DEShawResearch/random123/main/README.md) | Describes stateless keyed/counter-based random generation and reproducible outputs for a key/counter tuple. | Keying randomness is not a new invention. I did not open the linked SC11 paper and do not rely on its unread details. |
| Li et al., [MarS, arXiv:2409.07486v2](https://arxiv.org/abs/2409.07486v2); [official README](https://raw.githubusercontent.com/microsoft/MarS/main/README.md) | Abstract describes interactive, controllable order generation with market impact; README includes a market-impact analysis example and stylized-fact reporting. | Prior art for what-if/reactive impact simulation, not proof of exact, identified real-market counterfactuals or of a better RNG coupling. |
| Cheridito, Dupret and Wu, [ABIDES-MARL, arXiv:2511.02016v2](https://arxiv.org/abs/2511.02016v2) | Describes multiple learning agents, endogenous liquidity, synchronized decision periods and failure of exogenous-impact strategies against strategic market makers. | First submitted in 2025; opened abstract is the 2026 revision. Synchronized decision periods are not the same as this submission's RNG synchronization. |
| Olby et al., [Right Place, Right Time, arXiv:2510.22206v1](https://arxiv.org/abs/2510.22206v1) | Reactive ABM execution RL; slippage decomposition into market impact/execution risk; comparison on an Almgren-Chriss efficient frontier. | "Reactive simulation plus cost decomposition" is already occupied territory; the abstract does not establish an identical three-term twin decomposition. |
| Karpe et al., [arXiv:2006.05574v2](https://arxiv.org/abs/2006.05574v2); Hafsi and Vittori, [arXiv:2411.06389v2](https://arxiv.org/abs/2411.06389v2) | ABIDES-based RL execution precedes this work. Karpe reports TWAP convergence in some scenarios; Hafsi/Vittori reports outperforming standard strategies. | Do not rewrite those distinct claims as a uniform result that all papers "beat TWAP." |
| Balch et al., [arXiv:1906.12010v1](https://arxiv.org/abs/1906.12010v1) | Explains replay versus interactive simulation, impact evaluation for different order sizes, and the realism weakness of artificial markets. | The central need for a responsive simulator and its realism caveat are not new. |
| Sato and Kanazawa, [arXiv:2411.13965v3](https://arxiv.org/abs/2411.13965v3) | Reports high-precision square-root-impact evidence across liquid TSE stocks/accounts over eight years. | A benchmark for E7, not a proof that a five-size simulated confidence interval overlapping 0.5 validates this market. |
| Pinned upstream [rmsc04.py at f9cbe51](https://raw.githubusercontent.com/jpmorganchase/abides-jpmc-public/f9cbe51/abides-markets/abides_markets/configs/rmsc04.py) | Header/config list 1 exchange, 2 adaptive MMs, 102 value, 12 momentum and 1,000 noise agents; fundamental reference price 100,000 cents. | Supports count/scale corrections only, not calibration to a real venue. |

The official abstract responses were opened at [arXiv API batch 1](https://export.arxiv.org/api/query?id_list=2409.07486,2511.02016,2510.22206,2006.05574,2411.06389) and [batch 2](https://export.arxiv.org/api/query?id_list=2411.13965,1906.12010&max_results=2).

**UNVERIFIED:** the attempted primary page at <https://pubsonline.informs.org/doi/10.1287/mnsc.38.6.884> returned HTTP 403; no paper-specific assertion here relies on it. The legacy SSJ HTML URL returned 404 and was replaced by the opened author-maintained source above. The claimed absence of prior LOB RNG-rekeying work remains **UNVERIFIED**, not a novelty finding.

## Review scope and reproducibility

No simulations were run. Numerical checks read only committed CSVs using NumPy 2.2.6/pandas 2.3.3: exact seed/arm coverage and disjointness, full completion, accounting residuals, the committed bootstrap function, monetary conversions, E8's result and an explicitly exploratory E8-minus-E6 comparison. E6's leave-one-seed-out mean remains negative, approximately -0.03673 to -0.03005 bps; the objection is not a fabricated numerical failure or one dominating seed.

The E7/E9 implementation findings come from code and deterministic input/split inspection, not from pretending pending experiments have already failed. Later results or a revised abstract require a new evidence cutoff and re-score.
