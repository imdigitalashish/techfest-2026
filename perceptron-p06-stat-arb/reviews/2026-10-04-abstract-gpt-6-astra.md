# P6 raw hostile-judge review: final Round-1 abstract

Reviewer: GPT-6 Astra (`gpt-6-astra`), TASK 2 under PLAYBOOK section 10.

Reviewed snapshot: `9ad4ac9`, 2026-10-04. Primary artifact: `deliverables/round1-abstract.md`. Paths below are relative to `perceptron-p06-stat-arb/` unless stated otherwise. The optional rendered architecture is considered separately, not used to lower the abstract's score.

## Verdict

**62/100 (3.10/5), up from 53/100. Not yet submission-ready.** The new version supports a simulator-sensitivity benchmark, not a validated trading edge. The disclosure of collision filtering and inconclusive transfer/attribution under stricter fills earns the improvement. The remaining most serious overclaims are the supposed lifetime bounds and what live paper fills can establish. There is also a definite denominator error in the collision percentage.

The primary and amendment pass/fail statements match the registered numerical rules. I am not overturning those outcomes because a lower bound is small. Nor does numerical passage establish that the assumptions behind the intervals or execution models hold.

## Evidence checked and what changed since TASK 1

Read the rendered abstract, headline builder/data, twelve-day results, Amendment 1 and its erratum, both sensitivity-run summaries, provenance note, dispositions, appended ADR status, strict simulator/cell construction, sensitivity analysis, decay-bound construction, timing/latency results and the relevant legacy-ranking code.

`python3 -B eval/check_docs.py` passes and counts **879 body words**, within the brief's suggested 600-900. This establishes rendering consistency, not correctness of the interpretation attached to a number. I independently recomputed the collision denominator from committed JSON and compared V1/V2 gate statistics across the two committed runs; they agree within floating-point rounding (maximum difference approximately 6e-14). I did not rerun the full quote simulations or independently observe live execution.

| Result | Evidence-based reading |
|---|---|
| Frozen twelve-date primary: +$298.9, t-CI [+$129.6, +$468.3] | Passes the declared rule; all twelve date-level differences are positive. Five dates were previously inspected, which the abstract now discloses. |
| Previously unseen seven-date primary subset: +$342.8, t-CI [+$69.7, +$615.9] | Matches the committed result. This is the frozen-simulator subset, not a seven-date validation of strict fills. |
| V1 next-quote, basis mark: +$72.6, t-CI [+$10.4, +$134.8] | Passes after training and testing policies on V1 labels. |
| V2 next-quote, 1-second mid mark: +$70.1, t-CI [+$0.18, +$140.07] | Passes after retraining on V2 labels. Its bootstrap lower bound is also positive. |
| V2 collision-filtered: +$40.2, t-CI [-$12.0, +$92.3] | Does not establish superiority under the declared joint-interval criterion; the abstract reports this rather than hiding it. |
| V4 frozen-trained policies on strict outcomes: -$7.8, t-CI [-$147.5, +$131.8] | "Has no established advantage" is the right wording. It does not prove zero benefit or certain failure to transfer. |
| V2 LEV versus classifier / no-latency LEV | Neither t-interval excludes zero. The abstract correctly labels attribution exploratory and does not claim these comparisons establish a strict-world advantage. |

Sources: `eval/results/falsification_walkforward_12d_prereg.md`; `eval/results/sensitivity_amendment1.{md,json}`; `eval/results/sensitivity_amendment1_run1.json`; `eval/results/sensitivity_amendment1.provenance.md`.

TASK 1's economic-profit wording objection is substantially addressed by renaming the score and explicitly identifying its six-scenario aggregation. Residual-survival features are no longer advertised in the abstract. Same-asset cross-venue BTC remains a permitted MVP; no BTC/ETH expansion is needed to satisfy the starter-resource provision. Accepted dispositions are not, however, proof that every corresponding limitation is solved.

## Round-1 scores

Rubric: `_briefs/perceptron.txt:313-354`. This is a plan-stage score, not a demand for production trading before Round 1.

| Criterion | Weight | Score / 5 | Points / 100 | One-line evidence |
|---|---:|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | 16 | Abstract identifies the decision/latency crux, quotes costs and observability limits, and maps both MVP requirements. |
| Technical soundness and feasibility | 25% | 3 | 15 | A buildable ranker/replay design is demonstrated, but lifetime identification and paper-fill validation are still overclaimed. |
| Innovation / novelty | 20% | 3 | 12 | The simulator-sensitivity benchmark is a concrete differentiation; the abstract now correctly says it is not a new learner. |
| Clarity and structure | 10% | 4 | 8 | The 879-word submission has explicit components, outcomes and failure cases, though legacy-model and latency units need labelling. |
| Impact and evaluation rigour | 15% | 3 | 9 | Registered rules, provenance, collision and transfer sensitivities materially improve the plan; no fresh strict-world confirmation or executable fill ground truth exists here. |
| Team fit and readiness | 10% | 1 | 2 | Motivation and skills are still `[TEAM]`; dates do not establish the required three-member capability or ownership. |
| **Total** | **100%** | **3.10 weighted / 5** | **62** | **Nine-point improvement; not a selection probability.** |

## Remaining issues

Severity meanings: **blocker** = remove or qualify the unsupported headline before submission; **major** = material methodological, evidence or readiness correction; **minor** = bounded but real precision error.

### P6-A01 | blocker | The publication-time interval is not a demonstrated bound on true lifetimes

**Quote.** Abstract `:30`: "publication times bound it to", followed by the 11.3-147.1 ms interval. Abstract `:15` also says a lifetime is known within its venues' publication intervals.

**Evidence.** `eval/decay_report.py:72-105` assumes each observed episode has one true opening and closing in the previous publication intervals, computes endpoint durations and runs ordinary Kaplan-Meier on each endpoint. `eval/results/decay_report.md:7` then says these bracket the true curve.

**Problem.** Those assumptions do not follow from asynchronous, possibly throttled quotes. The same published observations can be compatible with an uninterrupted cross, several hidden close/reopen events, or a false cross against a stale counter-leg that was never simultaneously executable. The code does not identify which latent episode the observed episode represents. Independently right-censoring endpoint durations is also not, by itself, an interval-censored identification argument. The number is reproducible, but a guaranteed bound on the true median is not established.

**Fix.** Replace the bound claim with: **"The observed median is 90.5 ms; shifting episode endpoints within assumed publication intervals gives an illustrative 11.3-147.1 ms sensitivity range, not a bound on executable lifetime."** Identify the 84-100 ms interval as an hour-block CI for the *observed-quote* statistic, not coverage of latent lifetime. Proving stronger bounds needs an explicit observation model and assumptions excluding hidden episode changes. Likewise, call next-quote fills a stress scenario, not an adverse bound: the next quote can improve as well as worsen, and cannot reveal the book at arrival. Moving a receiver nearer an exchange does not itself change that feed's publication cadence.

### P6-A02 | major | A recorder is not the paper trader, and paper fills do not measure actual fillability

**Quotes.** Abstract `:34`: "the live recorder feeds the same pipeline"; `:47`: "The MVP and both stretch simulators run"; `:55`: "We will measure it with live paper fills."

**Evidence.** `components/feed/live_recorder.py:1-8` explicitly records raw websocket messages and says parsing/normalisation happens offline. `components/paper/__init__.py` is empty. No paper-trading implementation was found in the project's Python files inspected/searched. The abstract itself schedules paper trading for 1-14 December (`:49`). A working live paper-trading path is **UNVERIFIED**, not established by the recorder or latency report.

**Problem.** The current implementation claim overstates the inspected evidence. More fundamentally, simulated fills on a live feed remain simulated fills: they do not reveal matching-engine acceptance, competing orders, missed liquidity or realised unwind costs. Finer forward data can reduce some modelling error; changing historical replay into paper trading does not turn labels into execution ground truth.

**Fix.** Say **"Historical replay and latency-budget analysis run; live recording is available; paper-trading integration is planned."** Replace the final promise with forward, time-stamped evaluation and explicit fill-model uncertainty. If no authenticated execution feedback is available, retain the narrower paper-benchmark claim. Actual execution validation, if pursued, needs separately authorised execution data and risk controls, not just a dashboard.

### P6-A03 | major | The one-day ranking claim quietly switches LEV variant and latency units

**Quote.** Abstract `:37`: "At 50 ms, with the frozen simulator, the top decile by LEV earned +0.89 bp per trade, against +0.04 bp ranked by gap size." The adjacent method describes the +/-30-bp ranker conditioned on end-to-end `L` (`:22`).

**Evidence.** `eval/headline.py:59-65` takes these numbers and the 0.83/0.05 correlations from `baseline_0901_to_1001.json`; its report `:5,298-307` defines delta as the **one-way** feed/order delay. That nine-leg experiment fits `LEV()` in `eval/run_baseline.py:190`; `components/decision/lev.py:20,34-49` specifies 300 iterations, +/-50-bp labels and log latency. The five-leg registered model is `rules.fit_gbm_reg`, maximum 200 iterations, +/-30-bp labels and linear `L_ms`.

**Problem.** These numbers are not fabricated, but they do not belong to the model just described. In that frontier, 50 ms means feed = order = 50 ms, approximately 100 ms total plus compute; it is not end-to-end `L = 50 ms`. The same unit ambiguity affects the earlier correlation sentence. The source is one test date at 1 bp/leg, not a twelve-date ranking result.

**Fix.** Either remove this legacy ranking example or label its date, nine-market cohort, model variant, fee and **one-way** latency. Prefer one consistent model/result family in the abstract. Keep the compiled timing explicitly as in-kernel decision timing; its quoted 6.1/41.5-us figures themselves match the inspected timing report.

### P6-A04 | major | The laptop latency range is a selected, uncalibrated timestamp-gap statistic

**Quote.** Abstract `:33`: "From our laptop in India, the fastest 5% of messages arrive", followed by 69-107 ms.

**Evidence.** `eval/headline.py:109-110` selects only Binance futures, Coinbase BTC, Kraken BTC and Deribit BTC before taking the minimum/maximum p05. `eval/results/live_latency.md` also contains OKX p05 values near 24-25 ms and a negative Bybit p05. Its definition is receive time minus venue timestamp, including clock offset; the attached SNTP logs have uncertainties on the order of 170-554 ms.

**Problem.** This is not the range of the fastest messages across the advertised twelve venues. It is a range of four selected per-feed fifth-percentile timestamp differences, with clock uncertainty that is material relative to the quoted values. A fifth percentile is a cutoff, not an interval containing all of the fastest 5% of messages. The data do not isolate propagation latency from timestamp offset, publication delay and local processing.

**Fix.** Omit the range, or say **"Across four selected BTC feeds, fifth-percentile receive-minus-venue timestamp differences were 69-107 ms; clock offsets were not resolved."** Specify selection criteria in the supporting report. Do not infer a reliable geographical latency floor from these numbers.

### P6-A05 | minor | "18% of trades" uses the wrong denominator; the 24% retention also needs its world

**Quote.** Abstract `:44`: "(18% of LEV's trades)".

**Evidence.** `eval/sensitivity.py:153` computes the unweighted mean of twelve *daily* flagged fractions. In `sensitivity_amendment1.json`, V2 has **1,843 flagged of 8,493 selected intents**, or **21.7%** overall; the mean daily fraction is **18.3%**. The quoted collision-filtered +$40/day and interval themselves match the result.

**Fix.** Write **"18% mean daily collision rate"**, or use **"22% of selected intents across all test dates"**. Retain "selected intents" rather than implying all were executed trades. `check_docs` cannot detect this semantic denominator error because the 18% token really is in the headline data.

Also, `eval/headline.py:124` computes 24% from V1's 72.64/298.93; V2's 70.12/298.93 is 23.46%. After discussing both, use **"roughly a quarter remains"** or distinguish V1 and V2. This is not a material change to the conclusion.

### P6-A06 | minor | State clipping as part of the training target, not a clipped expected value

**Quote.** Abstract `:22`: "a gradient-boosted estimate of expected execution surplus, clipped at".

**Evidence.** `components/decision/autoresearch/rules.py:84-89` clips individual target observations before squared-error fitting.

**Problem.** The target is the conditional mean of clipped basis-point labels, not the raw expected surplus clipped afterwards. Those operations differ when tails matter. The new wording is much closer than TASK 1's expected-realised-P&L claim, but can be made exact without adding a derivation.

**Fix.** Use **"a regressor trained on execution-surplus labels clipped to +/-30 bp"**. Keep the zero-action rule as a tested policy, not a guarantee of positive expected raw value. The widened-clipping V2 comparison is +$72.3/day with t-CI [-$1.1, +$145.7]; it does not establish insensitivity of the *gate* to clipping even though the point estimate is similar.

### P6-A07 | major | Final submission still lacks the actual team

**Quote.** Abstract `:7`: "[TEAM: why it matters to us.]", and the skills placeholder at `:47`.

**Evidence.** `_briefs/perceptron.txt:299-303,338-342` explicitly requires relevant skills across three members and a credible execution plan. `reviews/2026-10-04-dispositions.md` correctly defers this to user input rather than fabricating it.

**Fix.** Before submission, supply truthful member-specific skills, motivation and ownership of systems/data, modelling/evaluation and demo integration. Add a short feasibility gate for suitable feed access and forward evaluation. Keeping placeholders is honest during drafting, but it does not satisfy a final judged criterion. Do not invent credentials.

### P6-A08 | major | Optional architecture attachment contradicts the corrected abstract

**Quotes.** `deliverables/architecture.md:3`: "fills happen on what the exchange *actually had* when our order arrived"; its C8 box `:21` advertises expected P&L, survival input and act/wait.

**Evidence.** The diagram links survival directly into LEV, shows an act/wait choice, and headlines +$299/day without the collision/strict-world limitation. The appended ADR says residual-survival inputs remain future work; inspected registered features contain none. The abstract itself no longer claims actual exchange-book ground truth.

**Fix.** If submitting this optional page, regenerate it with observed versus unobserved state distinguished, the clipped-label ranker, future features clearly marked, and a short simulator-sensitivity result. Otherwise omit it. **This companion-file warning is not an additional deduction in the abstract-only score.**

## Statistical reading that must survive the final edit

- Say **twelve sampled dates at monthly intervals**, not twelve months of trading; say seven dates were unexamined **before the original registration**, not that they are still unseen. Amendment 1 reuses the already analysed dates. Registration before a sensitivity run fixes that run's choices, but does not create fresh market evidence.
- The amendment tests **separately retrained policies** in V1 and V2 (`eval/sensitivity.py:145-149`). The failed-to-establish V4 transfer is precisely why "same trained policy remains robust" would be wrong. The current text does not explicitly make that stronger claim; add "retrained in each scenario" to remove ambiguity.
- Treat the t/bootstrap intervals as conditional on the day-level sampling assumptions. Twelve dates, a reused test/training chain and possible regime dependence are not cured by another run on another architecture. V2's mean is $70.1246 and standard error $31.7772; increasing that standard error by just **0.263%**, holding the mean and t critical value fixed, makes its lower endpoint reach zero. This is sensitivity arithmetic, not an estimated dependence correction or grounds to change the registered verdict.
- V2's seven-date subset is +$112.2 with t-CI **[-$7.8, +$232.3]**, not the positive interval displayed for the frozen seven-date subset. The collision-filtered result also fails the joint gate despite a positive percentile-bootstrap interval. The abstract's caution is justified; do not promote whichever secondary statistic happens to pass.
- Mark-to-mid accounting is not liquidation at executable prices. Fees remain counterfactual uniform levels, opening inventory is pre-positioned, and a collision-dropping diagnostic is not a depth- and inventory-constrained strategy. These are acceptable limitations for the proposed benchmark if retained, not evidence of profitable deployment.

The shortest defensible conclusion is: **"The learned policy improves this quote-replay benchmark under some execution assumptions, but strict fill and shared-liquidity sensitivities do not establish a deployable or uniquely latency-driven edge."** Publish that result rather than replacing it with an unconditional robustness claim.
