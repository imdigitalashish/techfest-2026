# Hostile Round-1 abstract and methodology review

**Reviewer:** GPT-6 Astra (`gpt-6-astra`), hostile judge / methodology, PLAYBOOK section 10.

**Date:** 2026-10-04. **Status:** advisory; the project lead decides.

**Reviewed snapshot:** repository `3cbeb67e1a8cc447a3b81e4aabac171d2e6006ab`; the abstract's latest project commit is `92ac9b6`. Paths below are relative to `perceptron-p09-agent-guardrail/`.

**Bottom line: 3.10/5, or 62/100.** This is a credible, unusually concrete Round-1 proposal, but its strongest evidence is an exploratory intervention trade-off, not demonstrated safety or novel argument verification. The biggest technical problem is not the small model: the proposed resolver cannot reach the wrong-entity calls that Tier 0 already allows. The biggest methodological problem is treating benchmark DB equivalence as a safety oracle.

I read the [official brief](../../_briefs/perceptron.txt), abstract, companion architecture, replay protocol, miss audit, prior Sol review and lead responses, landscape and relevant archived source excerpts, independent Astra suite documentation, and the result JSONs. I recalculated result counts and selected intervals without loading a model. Round 1 explicitly judges a plan, not a finished prototype; unfinished stretch work is not itself a defect. The `[TEAM]` fields are intentional, not accidental omissions to be filled with invented credentials.

## 1. Hostile score

| Criterion | Weight | Score / 5 | Contribution / 100 | Single biggest reason it loses points |
|---|---:|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | 16 | It still blurs a value's existence in trusted data with the user's authority to select that value for this particular action. |
| Technical soundness and feasibility | 25% | 3 | 15 | The model-residue architecture cannot repair already-allowed wrong-entity calls, while quote matching does not establish semantic support. |
| Innovation / novelty | 20% | 2 | 8 | It contrasts itself with a weak LLM-only baseline rather than the brief's framework-plus-KB baseline and existing runtime policy/provenance systems. |
| Clarity and structure | 10% | 4 | 8 | Results from different versions and cohorts are presented as though they describe one consistently evaluated checker. |
| Impact and rigour of evaluation plan | 15% | 3 | 9 | DB-effect labels and an overlapping-scenario, post-review test cannot establish the claimed safety benefit or its generalisation. |
| Team fit and readiness | 10% | 3, provisional | 6 | Milestones are credible, but ownership and relevant skills for implementation, annotation/statistics and integration are not yet assessable. |
| **Total** | **100%** | **3.10 weighted** | **62** | |

Arithmetic: `4*0.20 + 3*0.25 + 2*0.20 + 4*0.10 + 3*0.15 + 3*0.10 = 3.10`. The provisional team score recognises the schedule and existing artifacts; it is not a finding that the eventual team is unqualified.

## 2. Quantitative claim ledger

Here, **DB-good** means the committed `good` label; **DB-harmful** means `bad_harmful`. Neither is an independently adjudicated safety label. Unless stated otherwise, retail evidence is in `eval/results/taubench/`; synthetic evidence is in `eval/results/`.

| Abstract claim | Check against evidence | Judgment / required qualification |
|---|---|---|
| Four desk actions; seven retail write tools; at least one verifiable action class | `components/tools/desk.py`, `eval/taubench/replay.py::WRITE`, and the scripted `eval/demo_mvp.py` support these counts. The demo produced allow, block, block, block, hold, block for its six proposals. | **Supported as scope and scripted interception.** Not an autonomous agent or human-resumption demonstration. |
| 2,018 calls; 991 test calls; 167 harmful | Development has 1,027 calls; test has **702 DB-good + 167 DB-harmful + 122 tool-rejected = 991**. Together they give 2,018. | **Arithmetic correct.** Say historical benchmark proposals, not production incidents; distinguish tool rejection from accepted DB mismatch. |
| Rules tuned on half the tasks and tested on held-out tasks | Parity split, even/odd task IDs, is documented. Current full-test results contain **55 task IDs**, with repeated trials across models. | **Task-ID holdout only.** It is not a customer/order/scenario-disjoint holdout. |
| One rerun after review fixed six bugs | `74d2128` records the post-review corrections and rerun; first-run reports are archived. Sol reports 11 findings, accepted wholly or partly, not a uniquely defined six-bug taxonomy. | **Rerun disclosed, but not a pristine test.** Remove the unnecessary “six”; code corrections used test examples. |
| Schema catches 0% | `schema__test.json`: **0/167** DB-harmful calls stopped. | **Correct on this corpus.** Schema checks do not necessarily miss every possible hallucinated call; enums, registries and constraints can reject some. |
| Untuned checker stops 68% [57–77], blocks 7% good, holds 56% good | `t0_v0__test.json`: **113/167** stopped, comprising **6 blocks + 107 holds**; **51/702** good blocked, **392/702** held. Task-bootstrap catch interval **[0.5689, 0.7721]**. | **Correct rounding.** Most of the catch is deferral, not an automatic harmful-call diagnosis. |
| Tuned checker stops 41% [28–55], blocks 2.0% good, holds 30%; only three hard blocks | `t0_balanced__test.json`: **68/167**, comprising **3 blocks + 65 holds**; **14/702** good blocked and **213/702** held. Catch interval **[0.2834, 0.5506]**. | **Correct rounding.** “Three” refers to the DB-harmful stops, not all stopped calls. There are also good and tool-rejected hard blocks. |
| Tuned setting does not beat untuned score | Stored scores are **0.2355 versus 0.3248**, using `catch - false_block - 0.5*good_hold`. | **Correct and commendably candid.** This scalar is a chosen surrogate, not demonstrated economic utility. v0 already includes provenance, so this is not a provenance ablation. |
| 0.4 ms p95; Tier 0 is sub-millisecond | Balanced retail p95 is **0.419 ms**. Current Astra-suite Tier-0 p95 is **1.008 ms**. The retail cascade's sample p95 is **3506.505 ms**. | **Keep 0.4 ms only as measured in-process retail-check time.** Delete the blanket sub-millisecond description. It excludes framework, model and human latency. |
| 300-call LLM comparison: good stops 27% versus 28%, harmful stops 28% versus 48% | Same item IDs and labels: **120 good / 120 harmful / 60 rejected**. Judge: **32/120** good stops and **34/120** harmful stops. Balanced: **33/120** and **57/120**. | **Arithmetic and common sample correct.** This is a small-model, unequal-information comparison; it is not a matched economic-cost comparison or general LLM superiority result. |
| Resolver settled 11 of 85 held calls: six harmful, five good; released none | The **85 tool-accepted holds** comprise **54 DB-harmful + 31 DB-good**. Eleven became blocks: **6 + 5** respectively. No allow was added; harmful-call catch stayed **57/120**. There is also one held tool-rejected call outside that denominator. | **Counts correct.** “Correctly” and “wrongly” inherit the disputed DB labels. This converted deferrals to blocks; it did not catch additional harmful calls. |
| Twenty audited misses: eight user-requested, eight wrong-entity | The audit sampled the **first run's 107 misses**, not the current **99**. One sampled A case, `sonnet-35-new/t37/r5/m26.0`, now escalates. All eight B cases remain allowed. Four B cases are trials of task 79. | **Correct historical tally, stale current-cohort description.** Label it first-run, single-reader diagnosis. Do not extrapolate a population ceiling or assume B cases reach the resolver. |
| Independent red team: 160 cases, 100 bad / 60 good; 82% [73–88] catch, 8% blocks, 20% holds | Both versions stop **82/100** and block **5/60** good. **12/60 = 20%** holds is the archived first run. Current `t0__test__astra_redteam.json` has **14/60 = 23.3%** holds. Catch Wilson interval **[0.7333, 0.8830]** matches. | **Mixed-version claim.** First-run reporting is legitimate if labelled; otherwise use the post-fix counts. Cases 0002 and 0031 changed from allow to hold. |
| Own synthetic suite: 100% caught, 0% false blocks | Current `t0__test.json`: **153/153** bad stopped, comprising **130 blocks + 23 holds**, and **0/30** good blocked. Six omitted-account seeds were relabelled after review. | **Correct for revised self-authored labels, not a general safety result.** Even an IID Wilson calculation gives an upper false-block endpoint of **11.35%** for 0/30; the template assumptions are weaker than IID. |
| Qwen3-1.7B / 8B, one laptop, no paid APIs, dated milestones, conformal bounds | Model identifiers exist in `components/checker/llm.py`. The retail model result uses 1.7B, not an evaluated 8B careful tier. Runtime hook, human workflow and calibrator are planned in `architecture/components.md`. | **Separate configuration and plans from measured evidence.** Dates are commitments, not results; a miss-rate guarantee has not been demonstrated. |

The body is **876 words** by `eval.check_docs`' counting rule; the complete file is **934** under the same tokenisation, including titles and the internal draft note. The brief calls 600–900 a suggested length, so this is not evidence of automatic disqualification. Remove the administrative note from the submitted artifact.

### A. The label oracle measures the wrong primary construct

DB-effect equivalence is reproducible and useful for benchmark task fidelity. It is not sufficient or necessary for a safe, authorised action:

- A GT-equivalent call can contradict the actual user's payment request or lack required confirmation. Sol finding 2 documents the PayPal/credit-card example `sonnet-35-new/t13/r4/m18.0`.
- A non-equivalent call can faithfully execute the simulated user's visible instruction while disagreeing with that user's hidden task script.
- Matching one expected write's effect does not independently certify consent, policy compliance, action sequencing, factual provenance or final task success.

Fast-labeller/full-hash agreement validates an implementation of this oracle, not its safety meaning. The prior reviewer independently rebuilt the corpus and checked all 2,018 labels; I did not download and rebuild the raw trajectories again.

**Demand:** retain the DB-effect results as exploratory task-fidelity evidence. For the primary future comparison, independently adjudicate visible intent/consent, policy, factual support and observability, separately from DB effect. Do not “correct” the denominator by deleting inconvenient errors after looking at the results.

### B. The holdout and uncertainty claims need a narrower target

Sol's independently reproduced overlap analysis found **43/57 odd tasks sharing a development user**, **41/57 sharing an order**, and **786/991 test proposals** belonging to an order-sharing task. Those overlap counts come from that review, not a new raw-data reconstruction here. Freezing parity before writing rules prevents one form of leakage, not transfer between near-duplicate scenarios.

The current deterministic bootstrap correctly groups a task across both models and trials. It still assumes task clusters are exchangeable; related tasks can share customers, orders and wording. It does not account for code/label selection after inspecting the test, uncertainty in safety labels, or deployment shift. Use connected scenario/customer/order groups for the next split, and keep the calibration and final evaluation groups untouched.

There is also an actual **incomplete CI migration**: the stored LLM result still reports **91 model/task clusters** and catch CI **[0.1500, 0.4113]**. Its rows contain **54 task IDs**. Recomputing with the current `cluster_ci` gives **[0.1250, 0.4397]**. `frontier.py` copies the stale stored interval. No new model generation is needed to repair this. A blanket assertion that all reported CIs follow the current task-only method is false.

### C. Bug correction is legitimate; a corrected test is still a reused test

The rerun is transparent, and preserving the first-run results is good practice. But “same frozen configurations” does not freeze the implementation: confirmation timing, option handling and other behaviours changed after test inspection. This need not be dishonest or deliberate score tuning to invalidate pristine-holdout language.

`eval/taubench/README.md` still says test was run once, that only baselines/audit followed, and that clusters are `(model, task_id)`. The companion architecture also says all configurations were tested once. Both contradict the later code/result history. The Sol response claims some caveats were added to the abstract; important ones are absent from the reviewed final draft.

**Demand:** call the current numbers exploratory post-review results, reconcile the protocol and diagram, and pin code, label, dataset and prompt versions for the next measurement. Several reports' `2d3bf42-dirty` metadata is not an independently sufficient source-tree identifier. Do not silently mix the pre-fix Astra friction, post-fix retail results, and older synthetic LLM/cascade labels.

### D. The stratified comparison is not intrinsically unfair, but the information is unequal

Both guards see exactly the same sampled IDs. Stratifying by label does **not** invalidate the class-conditional catch and good-stop comparison. It does invalidate treating the 40/40/20 mixture as deployment prevalence when computing pooled precision, expected loss or workload without appropriate weighting.

There is a genuine positive signal within this limited comparison: on harmful calls, **36** are stopped only by Tier 0, **13** only by the judge, **21** by both, and **50** by neither. A paired task bootstrap gives a Tier-0-minus-judge catch difference of **19.17 percentage points**, with exploratory 95% interval **[2.83, 36.28]**. This uses 2,000 resamples, seed 0, and the same task-independence assumption criticised above. Therefore “the CIs overlap, so there is no difference” would be an incorrect attack.

The valid attack is **what that difference identifies**. `run.py::transcript` clips individual tool outputs to **700 characters**, then the whole transcript to its last **7,000 characters**. Tier 0 uses complete stored user turns/observations and direct DB/product records. The baseline is a 4-bit Qwen3-1.7B general model with thinking disabled and a fixed generation budget, not a representative 2026 LLM judge or specialised function-call verifier. Cheap local deployment is a legitimate baseline constraint, but not evidence of superiority to the method class.

Nor is equal good-call stopping equal cost: a hard block, a temporary human hold and a successful automatic repair have different costs. The abstract usefully distinguishes the decisions; the evaluation must price or report them separately.

Finally, do not replace the current direct-decision comparison with the frontier file's supposed “same-stop” judge catch. Its coarse risk thresholds select **0.8% catch at 0% good stops** because that fits under the balanced **27.5%** budget. That is a budget-feasible point, not equal use of that budget; discrete scores/ties need explicit treatment. Threshold selection on these same test labels is exploratory too.

### E. The proposed rescue mechanism cannot see its target errors

All eight audited wrong-entity cases are still `allow` in the current balanced rows. `taubench_cascade.resolve` returns immediately unless Tier 0 escalates, and only examines `UNVERIFIABLE` checks. Thus these errors are **not** the residue currently sent to Tiers 1–2. A larger model behind the same gate cannot catch them.

The code explains why this can happen: an order appearing in tool results can pass provenance without a user-named order, and a product name match need not resolve which same-name variant/order the user meant. Trusted existence is not intent binding.

Likewise, the quote verifier normalises strings and checks source occurrence, then accepts the model's supported/contradicted label. It does not independently establish that the quote concerns the right entity, field, time, negation or relation. The negative resolver result is useful evidence of this gap, not proof that scaling from 1.7B to 8B fixes it.

**Demand:** replace the “target for Tiers 1–2” assertion with a routing requirement: ambiguous entity/attribute bindings must first become unresolved checks. Describe verified quotes as a citation-occurrence constraint, not verified semantic inference.

### F. “Stopped” is an intervention decision, not established end-to-end risk reduction

Balanced stops **40.7%** of DB-harmful calls while stopping **32.3%** of DB-good calls when holds and blocks are both counted. v0's corresponding rates are **67.7%** and **63.1%**. The large catch number alone obscures limited discrimination and considerable task friction. These rates remain subject to the oracle problem; they are not safety precision estimates.

Replay evaluates proposals from the original ungated trajectory. Once a real guard blocks or asks a question, later proposals, DB states and user responses change. The proposed feedback/repair path and human `interrupt()` outcomes are not measured here. Holds avert immediate autonomous execution only if the runtime mediates every write; they do not prove a human will decide correctly.

The trading analogy is useful, but the objective's fixed `0.5` hold penalty is not an Optiver-style expected-loss model. State the cost assumption, report sensitivity and review workload, and eventually measure paired closed-loop task completion, repair and residual harmful execution. Do not market the replay percentage as an equivalent reduction in incidents or financial loss. This limitation is also explicit in the landscape's archived *What Can Be Enforced?* abstract.

### G. Independent authorship is valuable, not an IID sampling design

The Astra author was blinded to checker code and used only the allowed contracts, KB, policy and tool definitions. That is substantially better than self-written examples. It is nevertheless one model-authored, purposively designed challenge set, with related contrasts in **16 families**, shared fixtures and no independently double-coded safety oracle. A different model family is not a statistical independence guarantee.

Wilson intervals are mathematically reproducible under Bernoulli assumptions; they do not turn that suite into a random deployment sample. Likewise, the 20-case miss audit is one reader's categorisation, with repeated task-79 trials. “Eight are invisible to any transcript check” is too strong: a hidden-only preference can be unidentifiable, but a confirmed action can still violate earlier visible intent or policy. Indeed, one of those eight is now held for another concern.

The other committed challenge results should temper broad coverage claims. The post-fix white-box suite still allows **20/27** bad cases and holds **14/14** good cases. That suite was selected for failures, so those are not unbiased prevalence estimates either; they are evidence that “every intent-bearing argument” is not an established semantic coverage guarantee. Do not pool these deliberately different suites or foreground 100% self-authored performance.

### H. Conformal control must remain a conditional research plan

Specify which risk is controlled: harmful-call miss rate, joint harmful-and-allowed probability, or harmful fraction among allowed calls. These have different denominators and guarantees. Specify the loss, independent calibration unit, exchangeability assumption, threshold-selection procedure and review-budget constraint. Expected-risk control and a high-probability risk certificate are not interchangeable.

A hold-all rule trivially has no autonomous misses, so the review/utility constraint is essential. Repeated calls from a few related scenarios are not thousands of independent calibration examples. Adaptive agents and adversaries change the distribution after intervention. There is currently no basis for an unconditional safety bound; attempting carefully scoped calibration is a reasonable stretch goal.

## 3. Novelty attack

The brief's actual starter resource is **an agent framework plus a small grounding KB**. “We check values against a source before execution” meets the assignment; it is not itself the differentiator.

The following comparison uses `research/landscape.md` and the archived source excerpts in `research/notes/arxiv-abstracts.md` and `research/notes/companies-labs-clouds.md`. I did not independently reproduce these papers' performance or infer absent capabilities from an abstract.

| Prior work | What a knowledgeable reviewer will say is not new | Defensible remaining distinction |
|---|---|---|
| [ActGov](https://arxiv.org/abs/2609.24446) | Per-action pre-effect validation, runtime context, task-scoped authorisation and policy enforcement already exist; its policy updates have SMT checks. | A small, explicit intent-binding implementation and carefully measured cost/coverage could be useful; no stronger enforcement claim is established here. |
| [ContrAgent](https://arxiv.org/abs/2609.18128) | A reusable contract KB, deterministic low-latency online gating and offline replay evaluation are already the main story. | Field-level user-intent provenance differs in emphasis, but the proposal does not demonstrate ContrAgent's temporal-contract strength or a measured advantage. |
| [Closed-world resolution](https://arxiv.org/abs/2609.19425) | Registry/signature checks and their schema-indistinguishable borrowed-argument residue are explicitly identified. | Addressing that semantic residue is legitimate; recognising it is not a new discovery, and current entity-binding misses show it remains unsolved here. |
| [AgentSpec](https://arxiv.org/abs/2503.18666) | Runtime triggers, predicates, enforcement and low-overhead domain rules are already provided by a DSL. | Packaging provenance with these gates may improve auditability or usability; show the increment over policy-only predicates. |
| [ShieldAgent](https://arxiv.org/abs/2503.22738) | Verifiable policy reasoning, source-derived rule circuits and checks on agent trajectories predate this proposal. | Checking a model's literal citations is a simple constraint, not equivalent to formally verifying its conclusion. |
| [CaMeL](https://arxiv.org/abs/2503.18813) | Separating trusted user control from untrusted tool data, tracking flows and enforcing capabilities at tool calls are central prior art. | This lighter per-field adapter may be easier to deploy, but mention matching and supplied trust labels are not a stronger information-flow guarantee. |
| [Cedar gateway policies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-understanding-cedar.html) | The cited official example checks `context.input.amount < 500` before a refund tool executes. It directly checks an argument against an authoritative policy. | Source-to-intent binding is not automatically supplied by that example. But neither is it supplied automatically by a bare hook in this project; both require authored logic. |

The sentence “Shipping tools ... don't check argument values against a source” must go. The project's own company notes explicitly identify Cedar's argument check. Distinguishing a policy from a KB cannot rescue that claim while counting this project's own policy clauses as a verifiable source.

The other supposed novelties are also established patterns: three-way abstention/contradiction is familiar from selective prediction and NLI; the cited Claude hooks already have allow/deny/ask; [KnowNo](https://arxiv.org/abs/2307.01928) asks for help under calibrated uncertainty; cheap-to-careful routing is in both prior AI-control work and the problem's stretch goals. Confidence intervals and real-trajectory replay are good evaluation practice, not a new algorithm.

**Defensible novelty:** an auditable integration, plus an experiment that isolates the additional value of *intent binding* and *quote constraints* over policy-only and model-only alternatives at fixed review burden. An original evaluation design can earn Round-1 novelty credit. A first-of-its-kind gate or provenance guarantee is not supported.

## 4. Twelve exact text edits, ordered by expected score impact

These are a **single compatible edit set**, not extra paragraphs to append. All originals occur exactly once in the reviewed abstract. Applying all twelve gives **858 body words / 894 words including the remaining titles**, under the current whitespace/Markdown-marker counting rule; `[TEAM]` placeholders remain. The replacements are proposals for the lead, not edits made to the abstract by this review.

Literal assertions in `eval.check_docs` will need corresponding, truthful updates if these edits are adopted. Do not preserve misleading wording merely to satisfy its string matches, or disable the checks instead of updating them.

### 1. Define the oracle and disclose the reused, overlapping holdout

**Original →**
```markdown
**Real agent errors.** We replayed every write call in τ-bench's published gpt-4o and Claude-3.5-Sonnet retail runs: 2,018 calls, labelled by whether each call's database effect matches the task's ground truth. Rules were tuned on half the tasks and tested on held-out tasks (991 calls, 167 harmful). The test was re-run once after an external code review fixed six bugs. 95% CIs are clustered by task.
```
**Replacement**
```markdown
**Historical replay.** Published gpt-4o and Claude-3.5-Sonnet retail runs yielded 2,018 writes. Here, 'good' means ground-truth-equivalent DB effects; 'harmful' means accepted but non-equivalent, not adjudicated safety. Development-selected configurations were evaluated on parity-held-out task IDs within overlapping scenarios (991 calls: 702 good, 167 harmful, 122 tool-rejected). Code-review corrections used test evidence; these are exploratory results from one post-review rerun. The deterministic guards' 95% percentile CIs resample whole tasks across both models.
```

### 2. Replace the straw baseline and universal novelty claim with an isolating experiment

**Original →**
```markdown
The obvious baseline asks an LLM "is this call OK?". We differ in four ways:
1. per-argument provenance instead of one holistic judgement;
2. *unverifiable* (hold) kept separate from *contradicted* (block);
3. model verdicts admitted only with verified quotes;
4. evaluation on real agent errors, reporting the catch / false-block / hold trade-off with confidence intervals.

Shipping tools (pre-tool hooks, Cedar gateway policies, groundedness APIs that score response *text*) don't check argument values against a source.
```
**Replacement**
```markdown
The starter baseline already combines a framework and KB. ActGov, ContrAgent and AgentSpec supply rule gates; CaMeL separates trusted flows; Cedar checks arguments. Our proposed contribution combines intent provenance, abstention and source-checked model evidence. We will ablate provenance and quote checking against input-matched policy-only and model-only guards at a fixed review budget on freshly adjudicated, scenario-disjoint tasks.
```

### 3. Distinguish source occurrence from semantic verification

**Original →**
```markdown
- **Tiers 1–2.** Only the *unverifiable* residue goes to a model (Qwen3-1.7B, or 8B for high-risk calls). A verdict counts only if the user words or tool data it quotes are found verbatim, and a bare "yes" never counts.
```
**Replacement**
```markdown
- **Tiers 1–2 (experimental).** Route only *unverifiable* checks to Qwen3-1.7B; evaluate 8B for higher-risk cases. Require substantive source-matched quotes. This checks quote occurrence, not entailment; unsupported reasoning must still lead to a hold.
```

### 4. Correct the miss cohort and the resolver's claimed target

**Original →**
```markdown
**Misses.** In 20 audited misses, 8 were explicitly requested by τ-bench's simulated user (invisible to any transcript check) and 8 were wrong-entity choices ("like my other order") — the target for Tiers 1–2.
```
**Replacement**
```markdown
**Misses.** The first-run 20-miss audit found eight user-confirmed disagreements and eight wrong-entity choices. All eight wrong-entity calls still pass Tier 0 and never reach the resolver. Hidden-only preferences may be unobservable.
```

### 5. Retain the small-model observation without claiming equal information or equal cost

**Original →**
```markdown
- **LLM judge** (Qwen3-1.7B, same transcript and policy), on a 300-call sample: at almost the same good-call stop rate (27% vs our 28%), the judge stops 28% of harmful calls and ours 48%. The judge's stops are hard blocks; ours are mostly holds.
```
**Replacement**
```markdown
- **Small-model baseline:** same stratified 300 calls. Qwen3-1.7B stopped 34/120 harmful calls versus Tier 0's 57/120; good-call stops were 32/120 versus 33/120. Judge inputs were truncated; Tier 0 also accessed the database. The judge blocked; Tier 0 mostly held. This is exploratory.
```

### 6. Turn the unqualified conformal promise into a conditional stretch experiment

**Original →**
```markdown
1. **Risk-routed fast/careful models**, with hold thresholds set by conformal risk control so the miss rate is bounded at a stated level.
```
**Replacement**
```markdown
1. **Risk-routed fast/careful models**; attempt conformal control of harmful-call miss rate on untouched calibration scenarios, subject to exchangeability and a predeclared review budget.
```

### 7. State what the resolver actually changed

**Original →**
```markdown
- **Model tier, first try:** a 1.7B resolver with verified quotes settled 11 of 85 held calls (6 harmful correctly blocked, 5 good calls wrongly blocked) and released none. Tiers 1–2 need a stronger model.
```
**Replacement**
```markdown
- **Model tier:** Qwen3-1.7B converted 11/85 held, tool-accepted calls to blocks: 6 DB-mismatching, 5 DB-equivalent; none to allow. Catch did not improve. Model scale alone cannot fix Tier-0 misses.
```

### 8. Separate factual data from authority and remove the blanket latency claim

**Original →**
```markdown
- **Tier 0 (deterministic, sub-millisecond).**
  - Every intent-bearing argument must trace to the user's words, the reference database or trusted tool data. Email or ticket text is never a source of intent.
```
**Replacement**
```markdown
- **Tier 0 (deterministic).**
  - Bind each intent-bearing argument to the user's request or a specifically confirmed proposal; database and tool records supply facts, not authority. Email or ticket text cannot authorize actions.
```

### 9. Make the primary operating point auditable and scope its latency

**Original →**
```markdown
- The tuned setting cuts false blocks to **2.0%** and holds to 30%, stopping **41% (28–55)**, at **0.4 ms** at p95. Only 3 of its stops are hard blocks.
```
**Replacement**
```markdown
- The tuned checker stops **68/167** harmful-labelled calls (**41%; 95% CI 28–55**): **3 blocks, 65 holds**. Of 702 good-labelled calls, it blocks **14 (2.0%)** and holds **213 (30%)**. In-process retail checking took **0.4 ms p95**, excluding model, framework and human time.
```

### 10. Use a consistent post-fix red-team version and demote self-authored perfection

**Original →**
```markdown
**Independent red team.** 160 cases written by a different model family that never saw our rules: the checker stops 82% (73–88) of 100 bad calls, but blocks 8% and holds 20% of 60 good ones. Our own synthetic suite scores 100% caught, 0% false blocks; self-written tests flatter.
```
**Replacement**
```markdown
**Independent synthetic red team.** A different-family author, blinded to the checker, wrote 160 cases. After fixes, 82/100 bad calls were stopped (Wilson 95% CI 73–88); 5/60 good calls were blocked and 14/60 held. This is a designed challenge set, not a deployment sample; self-authored tests are regression checks.
```

### 11. Narrow the universal schema claim

**Original →**
```markdown
1. **Schema checks pass hallucinated calls by construction.** The check must be on argument *values* and where they came from.
```
**Replacement**
```markdown
1. **Schema validity does not establish grounding.** Check argument values and their sources, including schema-valid but unauthorized choices.
```

### 12. Remove the internal anti-drift boast from the submission

**Original →**
```markdown
*Final draft, 4 Oct 2026. Every number comes from a committed result; `python -m eval.check_docs` fails if this text drifts from `eval/results/`.*
```
**Replacement:** `""` (delete this paragraph).

The checker passes while deliberately sourcing Astra's old friction, retaining a stale miss cohort and not validating the baseline's CI migration. It is a useful literal-claim regression test, not a methodological endorsement.

## 5. Shortlist verdict and the single highest-value change

**Plausibly shortlisted, but borderline rather than a confident top-25–30 recommendation as written.** The problem fit, explicit architecture, public real-proposal replay and willingness to publish negative results are stronger than a generic plan-only submission. Conversely, a professor can challenge the oracle and independence assumptions, while a quant can challenge the intervention costs and weak comparator; those objections undermine the claimed differentiator, not just presentation.

There is no defensible probability or exact rank without seeing the other teams across all ten problems. Do not infer a shortlist threshold from this score.

**Single change most likely to improve its odds:** make a **fresh, scenario-disjoint, independently adjudicated ablation of intent provenance versus policy-only gating at a fixed human-review budget** the primary promised experiment, with identical information supplied to the compared guards. This turns “we assembled familiar guard components” into a falsifiable question about their incremental value. It can earn novelty, technical-soundness and evaluation credit without inventing a better result or promising that a larger model solves the failures.

## 6. Verification receipt and reproducible reanalysis

Only this review file was authored. The permitted CPU checks passed after restoring the missing environment with `uv sync --extra dev --frozen`: `python -m eval.check_docs` reported **18 claims, 0 problems, 876 body words**; `python -m pytest -q` passed **7 tests**; the deterministic MVP demo behaved as described above. No local LLM, MLX model, GPU computation, `llm_judge` run or `cascade_fast` run was started.

Stored rows, not fresh generations, support this review's derived statistics. The following CPU-only snippet reproduces the stale-CI finding, paired comparison and audited-miss routing check:

```bash
cd perceptron-p09-agent-guardrail
.venv/bin/python - <<'PY'
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from eval.taubench.run import cluster_ci, pct

root = Path("eval/results/taubench")
def report(name):
    return json.loads((root / f"{name}.json").read_text())

b = report("t0_balanced__test__sample300")
j = report("llm_judge__test__sample300")
print("Judge stored:", j["metrics"]["n_clusters"],
      j["metrics"]["ci95_cluster_bootstrap"]["catch_harmful"])
print("Judge task-only:", len({r["task_id"] for r in j["rows"]}),
      cluster_ci(j["rows"])["catch_harmful"])
bm = {r["item_id"]: r for r in b["rows"]}
jm = {r["item_id"]: r for r in j["rows"]}
assert bm.keys() == jm.keys()
assert all(bm[i]["kind"] == jm[i]["kind"] for i in bm)
by = defaultdict(list)
for r in b["rows"]:
    by[r["task_id"]].append(r["item_id"])
keys = sorted(by)
rng = random.Random(0)
deltas = []
for _ in range(2000):
    ids = [i for k in (rng.choice(keys) for _ in keys) for i in by[k]
           if bm[i]["kind"] == "bad_harmful"]
    assert ids
    deltas.append(sum((bm[i]["decision"] != "allow") -
                      (jm[i]["decision"] != "allow") for i in ids) / len(ids))
print("Paired delta CI, percentage points:",
      [round(100 * pct(deltas, q), 2) for q in (0.025, 0.975)])

current = {r["item_id"]: r for r in report("t0_balanced__test")["rows"]}
audit = Path("eval/taubench/audit-test-misses.md").read_text()
ids = re.findall(r"\| \d+ \| ([^|]+) \| B wrong entity \|", audit)
print("Audited wrong-entity routing:",
      [(i.strip(), current[i.strip()]["decision"]) for i in ids])
PY
```
