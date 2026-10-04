# Round-1 abstract — Perceptron 2026, Theme 5 · Problem 8

**Title:** *Name the rule, prove it, verify the practice — an exact-first cascade tutor*

*Numbers are rendered from committed results (`python -m eval.render_docs`) and checked by `python -m eval.check_docs`. [TEAM] marks text the team supplies.*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8. A learner who writes 1/8 + 1/8 = 2/16 is not missing a fact. They are running a wrong rule ("add the tops, add the bottoms") and will repeat it until someone names it. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Inverse problem.** One wrong answer can come from different misconceptions, from two interacting ones, or from a slip. Often only a better next question separates them.
2. **Trust before coverage.** Naming the wrong misconception misleads. A diagnoser must therefore be tested on same-domain wrong answers caused by *other* misconceptions; Eedi's Kaggle metric (MAP@25) scores positives only.
3. **Real errors are rarely pure computations.** Only {{real.p_eval}} of {{real.n_pos}} real Eedi distractors labelled with our five misconceptions come from questions an exact engine can evaluate.
4. **Practice must be correct and must target the misconception,** and proving learning needs counterfactual controls.

## What we measured first (pre-registered)
Before running seven tests against GPT-4.1-mini, GPT-5.4-mini and GPT-5.5, we committed hypotheses, prompts and decision rules.
- **Real Eedi data** ({{real.n_pos}} positives, {{real.n_neg}} same-domain negatives):
  - GPT-5.5 diagnosed {{real.gpt-5.5.accP}} of positives, with {{real.gpt-5.5.fcr}} false claims.
  - Our exact engine diagnosed {{real.exec_accP}}, with {{real.exec_fcr}} false claims.
  - GPT-4.1-mini over-claimed on {{real.gpt-4.1-mini.fcr}} of negatives.
- **Synthetic inversion** (7–8 operators; interacting misconceptions or slips): GPT-5.5 {{inv.gpt-5.5.L3}}, GPT-4.1-mini {{inv.gpt-4.1-mini.L3}}.
- **Synthetic tracing** (12 answers per learner): our tracer {{trace.tracer_exact}} vs GPT-5.4-mini {{trace.gpt-5.4-mini.exact}}, not significantly different.
- **Probability answer keys:** exact for GPT-5.5 on {{prob.gen.gpt-5.5.both}} of problems and for GPT-4.1-mini on {{prob.gen.gpt-4.1-mini.both}}.

**Plainly:** reasoning models already match an exact engine on accuracy and safety, and only the cheaper non-reasoning model fails. So we compete on cost, latency, determinism and verified practice, not accuracy.

## Proposed approach — exact-first cascade
1. **Executable misconception engine (stage 1).** Each misconception is a bug switch in an exact rational interpreter (Python `fractions`, SymPy), and switches compose. When exactly one known misconception reproduces the answer, the engine names it with checkable evidence in {{cons.engine_ms}}, identically every time: "2/16 is exactly what adding tops and bottoms gives". Otherwise it abstains.
2. **Frontier LLM (stage 2).** Abstentions go to GPT-5.5, with a NONE option and retrieval over Eedi's CC-BY misconception catalogue.
3. **Discriminative, verified generation.** Parameters are searched until the target misconception fires and its competitors give pairwise-distinct wrong answers. SymPy verifies every key, and the distractors are the bug outputs.
4. **Set-level Bayesian tracer.** It tracks which *combination* of misconceptions a learner holds across sessions, picks the most informative next item, and then switches to targeted practice.
5. **Packs.** School arithmetic (five Eedi-linked misconceptions), and probability / expected value (equiprobability, base-rate neglect, dependence, adding probabilities, E[X²] vs E[X]²).

## Minimum Viable mapping
| MV bullet | Demoable by the deadline |
|---|---|
| Classify a wrong answer into 3–5 categories | Five categories per pack; cascade with a posterior, slip/abstain, and feedback that names the rule |
| Generate a targeted practice problem | Discriminative generator; SymPy-verified keys; target firing checked by execution |

## Stretch ambitions
- **Cross-session tracking:** the prototype already runs across sessions.
- **Evidence that targeted practice reduces errors:**
  - Simulated learners (synthetic): {{sim.ours_left}} of initial misconceptions remain after four sessions, vs {{sim.random_left}} under random practice.
  - Then a consented ~30-learner pilot with pre/post isomorphic items and a random-practice control.

## Novelty / differentiation
Executable misconceptions are not new: Sleeman's mal-rules, and MalruleLib (ACL 2026). What we add:
1. **A pre-registered evaluation against frontier LLMs, with same-domain negatives,** that shows where each approach wins.
2. **An exact-first cascade.** On practice items the engine can model, it halves GPT-5.5 calls and the cost per 1,000 diagnoses ({{diag.gpt-5.5.cost1000_llm}} → {{diag.gpt-5.5.cost1000_cascade}}) at unchanged accuracy, answering in milliseconds rather than {{cons.gpt-5.5.latency}}.
   - Determinism: GPT-5.5 changed its diagnosis on {{cons.gpt-5.5.disagree}} of {{cons.n}} repeated real items; the engine never changes.
   - On real Eedi items the saving is small, because the engine explains only {{casc.real.engine_answers}} of {{casc.real.n}}.
3. **Guaranteed-correct, discriminative practice,** whichever LLM is deployed.

## Evaluation plan
- **Diagnosis (real Eedi):** accuracy, false claims on same-domain negatives, balanced accuracy, bootstrap CIs (done). Open-set MAP@25: kNN {{open.map25_knn}} today.
- **Cascade:** LLM calls, cost and latency per 1,000 diagnoses, and run-to-run consistency (done; repeated at every milestone).
- **Generation:** key and distractor correctness vs LLM-only (done); blinded teacher ratings of 50 items.
- **Tracing:** next-answer log-loss on real Eedi option-level sequences.
- **Learning:** simulation sweep, then the pilot.

## Feasibility and risks
[TEAM: three members and skills.] Twelve components with typed contracts and tests already run end to end on a laptop.

**Milestones:**
- to 31 Oct: cascade service, probability-pack UI
- to 15 Nov: real-data tracing, web demo
- 19–25 Nov: exams (buffer)
- to 1 Dec: pilot and midway report
- to 15 Dec: rehearsals

**Risks and mitigations:**
- Our edge is not accuracy → re-run the benchmark at every milestone.
- Few executable errors limit the saving → grow the packs.
- Simulated learning ≠ real learning → the pilot.
- Eedi data via a community mirror → official download.
