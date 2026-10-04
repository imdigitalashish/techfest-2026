<!-- GENERATED from deliverables/templates/round1-abstract.md by `python -m eval.render_docs`; edit the template, not this file. -->
# Round-1 abstract — Perceptron 2026, Theme 5 · Problem 8

**Title:** *Name the rule, check it, verify the practice — an exact-first cascade tutor*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8. A learner who writes 1/8 + 1/8 = 2/16 may not be missing a fact: the answer is exactly what the rule "add the tops, add the bottoms" produces. A tutor should test that hypothesis and target it. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Inverse problem.** One wrong answer can come from different misconceptions, from two interacting ones, from an unmodelled rule, or from a slip. A rule that reproduces the answer is evidence, not proof, so a discriminating follow-up question is needed.
2. **Trust before coverage.** Naming the wrong misconception misleads. Diagnosers must therefore be tested on same-domain wrong answers caused by *other* misconceptions; Eedi's Kaggle metric (MAP@25) scores positives only.
3. **Executable coverage is limited.** Our parser and key-agreement gate cover only 29 of 131 real Eedi distractors labelled with our five misconceptions (or equivalent labels).
4. **Practice must be correct and targeted,** and learning claims need controls.

## What we measured first (pre-registered)
Before any run, we committed the hypotheses, prompts and decision rules for six experiments against GPT-4.1-mini, GPT-5.4-mini and GPT-5.5.
- **Real Eedi conditional benchmark** (131 positives; 152 same-domain negatives with other labels):
  - GPT-5.5 diagnosed 79.4% of positives, with 0 false claims (exact 95% upper bound 2.4%).
  - Our engine diagnosed 19.1%, also with 0.
  - GPT-4.1-mini over-claimed on 15.8% of negatives.
- **Synthetic inversion** (4–8 operators; interacting misconceptions or slips): GPT-5.5 100.0%, GPT-4.1-mini 11.7%.
- **Synthetic tracing:** exact held set, our tracer 64.0% vs GPT-5.4-mini 66.0%.
- **Probability problems** (key and misconception answer both exact): GPT-5.5 100.0%, GPT-4.1-mini 36.7%.

**Plainly:** no pre-registered gap was detected against the reasoning models; only GPT-4.1-mini failed. We make no accuracy claim and design around cost, latency, determinism and verified practice.

## Proposed approach — exact-first cascade
1. **Executable engine (stage 1).** Each misconception is a bug switch in an exact rational interpreter (Python `fractions`, SymPy), and switches compose.
   - When exactly one known misconception reproduces the answer, the engine issues a checkable certificate: "2/16 is exactly what adding tops and bottoms gives". This takes 0.06 ms (median) and is deterministic: 304/304 identical repeat outputs.
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
  - Simulated learners (synthetic, equal learning rates for all feedback): 28.0% of misconceptions remain after four sessions, vs 58.4% under random practice.
  - Then the pilot below.

## Novelty / differentiation
Executable misconceptions are prior art: Sleeman's mal-rules, and MalruleLib (ACL 2026). Ours is a bounded integration-and-evaluation contribution:
1. **A pre-registered comparison** against frontier LLMs, with same-domain negatives.
2. **An honestly measured cascade.**
   - On engine-native probability items (half explainable by design), GPT-5.5 cost per 1,000 diagnoses falls $7.32 → $5.08. Calls halve, but the routed answers cost more.
   - On real Eedi items (post hoc) it falls $6.50 → $6.10, because the engine explains only 26 of 304.
   - GPT-5.5 changed 2 of 40 repeated diagnoses.
3. **Verified practice,** whichever LLM is deployed.

The falsifiable claim we will test: *our tutor reduces targeted errors at least as much as a GPT-5.5 tutor, at lower cost.*

## Evaluation plan
- **Diagnosis (real Eedi):** accuracy, false claims, exact and question-clustered CIs (done; repeated each milestone). Open-set MAP@25: 0.326 (kNN).
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
