# Round-1 abstract — Perceptron 2026, Theme 5 · Problem 8

**Title:** *Name the rule, check it, verify the practice — an exact-first cascade tutor*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8. A learner who writes 1/8 + 1/8 = 2/16 may not be missing a fact: the answer is exactly what the rule "add the tops, add the bottoms" produces. A tutor should test that hypothesis and target it. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Inverse problem.** One wrong answer can come from different misconceptions, from two interacting ones, from an unmodelled rule, or from a slip. A rule that reproduces the answer is evidence, not proof, so a discriminating follow-up question is needed.
2. **Trust before coverage.** Naming the wrong misconception misleads. Diagnosers must therefore be tested on same-domain wrong answers caused by *other* misconceptions; Eedi's Kaggle metric (MAP@25) scores positives only.
3. **Executable coverage is limited.** Our parser and key-agreement gate cover only {{real.p_eval}} of {{real.n_pos}} real Eedi distractors labelled with our five misconceptions (or equivalent labels).
4. **Practice must be correct and targeted,** and learning claims need controls.

## What we measured first (pre-registered)
Before any run, we committed the hypotheses, prompts and decision rules for six experiments against GPT-4.1-mini, GPT-5.4-mini and GPT-5.5.
- **Real Eedi conditional benchmark** ({{real.n_pos}} positives; {{real.n_neg}} same-domain negatives with other labels):
  - GPT-5.5 diagnosed {{real.gpt-5.5.accP}} of positives, with 0 false claims (exact 95% upper bound {{real.gpt-5.5.fcr_hi}}).
  - Our engine diagnosed {{real.exec_accP}}, also with 0.
  - GPT-4.1-mini over-claimed on {{real.gpt-4.1-mini.fcr}} of negatives.
- **Synthetic inversion** ({{inv.L3.ops}} operators; interacting misconceptions or slips): GPT-5.5 {{inv.gpt-5.5.L3}}, GPT-4.1-mini {{inv.gpt-4.1-mini.L3}}.
- **Synthetic tracing:** exact held set, our tracer {{trace.tracer_exact}} vs GPT-5.4-mini {{trace.gpt-5.4-mini.exact}}.
- **Probability problems** (key and misconception answer both exact): GPT-5.5 {{prob.gen.gpt-5.5.both}}, GPT-4.1-mini {{prob.gen.gpt-4.1-mini.both}}.

**Plainly:** no pre-registered gap was detected against the reasoning models; only GPT-4.1-mini failed. We make no accuracy claim and design around cost, latency, determinism and verified practice.

## Proposed approach — exact-first cascade
1. **Executable engine (stage 1).** Each misconception is a bug switch in an exact rational interpreter (Python `fractions`, SymPy), and switches compose.
   - When exactly one known misconception reproduces the answer, the engine issues a checkable certificate: "2/16 is exactly what adding tops and bottoms gives". This takes {{ph.engine_ms}} (median) and is deterministic: {{ph.engine_identical}} identical repeat outputs.
   - It then asks a discriminating follow-up before labelling the learner. Otherwise it abstains.
2. **Frontier LLM (stage 2).** Abstentions go to GPT-5.5 with a NONE option. Labels outside the pack go to the teacher view; feeding them into the tracer is planned.
3. **Verified, discriminative generation (arithmetic).** Parameters are searched until the target fires and requested competitors give distinct wrong answers. SymPy re-verifies keys.
4. **Set-level Bayesian tracer.** It tracks which *combination* of misconceptions a learner holds across sessions, and picks the next item by expected information gain.
5. **Scope.** The MVP is the five-misconception arithmetic pack. The probability/expected-value pack (prototype exists) and catalogue-wide retrieval are stretch goals.

## Minimum Viable mapping
| MV bullet | Demoable by the deadline |
|---|---|
| Classify a wrong answer into 3–5 categories | Five arithmetic categories; certificate or LLM label, posterior, slip/abstain |
| Generate a targeted practice problem | Discriminative generator; SymPy-verified keys; target firing checked by execution |

## Stretch ambitions
- **Cross-session tracking:** the prototype already persists state.
- **Evidence that targeted practice reduces errors:**
  - Simulated learners (synthetic, equal learning rates for all feedback): {{sim.pess_ours_left}} of misconceptions remain after four sessions, vs {{sim.pess_random_left}} under random practice.
  - Then the pilot below.

## Novelty / differentiation
Executable misconceptions are prior art: Sleeman's mal-rules, and MalruleLib (ACL 2026). Ours is a bounded integration-and-evaluation contribution:
1. **A pre-registered comparison** against frontier LLMs, with same-domain negatives.
2. **An honestly measured cascade.**
   - On engine-native probability items (half explainable by design), GPT-5.5 cost per 1,000 diagnoses falls {{diag.gpt-5.5.cost1000_llm}} → {{diag.gpt-5.5.cost1000_cascade}}. Calls halve, but the routed answers cost more.
   - On real Eedi items (post hoc) it falls {{casc.real.gpt-5.5.cost1000_llm}} → {{casc.real.gpt-5.5.cost1000_cascade}}, because the engine explains only {{casc.real.engine_answers}} of {{casc.real.n}}.
   - GPT-5.5 changed {{cons.gpt-5.5.disagree}} of {{cons.n}} repeated diagnoses.
3. **Verified practice,** whichever LLM is deployed.

The falsifiable claim we will test: *our tutor reduces targeted errors at least as much as a GPT-5.5 tutor, at lower cost.*

## Evaluation plan
- **Diagnosis (real Eedi):** accuracy, false claims, exact and question-clustered CIs (done; repeated each milestone). Open-set MAP@25: {{open.map25_knn}} (kNN).
- **Cascade:** cost and latency of routed items; consistency (done).
- **Generation:** correctness vs LLM-only (done); blinded teacher ratings of 50 items.
- **Tracing:** next-answer log-loss on real Eedi option-level sequences.
- **Pilot (primary learning outcome):**
  - Design: ~30 consenting learners randomised to our tutor or a GPT-5.5 tutor, with the same items, time and interface.
  - Primary outcome: error rate on delayed, unseen isomorphic items for each learner's diagnosed misconception.
  - It is a pilot, not a powered trial.

## Feasibility and risks
[TEAM: three members, skills, and owners for engine, LLM/evaluation and UI/pilot.] Twelve components with typed contracts and tests run end to end on a laptop.

**Milestones:**
- to 31 Oct: cascade service
- to 15 Nov: web demo, consent, recruitment
- 19–25 Nov: exams (buffer)
- to 1 Dec: pilot and midway report
- to 15 Dec: rehearsals

**Risks and mitigations:**
- No accuracy edge → re-run the benchmark each milestone.
- Low executable coverage → measure it on pilot traffic.
- Recruitment → a smaller within-subject fallback.
- Eedi community mirror → official download.
