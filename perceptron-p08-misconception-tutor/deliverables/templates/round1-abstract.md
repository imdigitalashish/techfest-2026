# Round-1 abstract — Perceptron 2026, Theme 5 · Problem 8 (final draft)

**Title:** *Name the rule, prove it, verify the practice — an exact-first cascade tutor for misconceptions*

*Every number below is rendered from committed results by `python -m eval.render_docs` and checked by `python -m eval.check_docs`. [TEAM] marks text the team must supply.*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8. A learner who writes 1/8 + 1/8 = 2/16 is not missing a fact. They are running a wrong rule, "add the tops, add the bottoms", and will repeat it until someone names it. [TEAM: why this matters to us.]

## Understanding of the challenge
1. **Inverse problem.** One wrong answer can come from different misconceptions, from two interacting ones, or from a slip. Often only a better next question tells them apart.
2. **Trust before coverage.** Naming the wrong misconception misleads. A diagnoser must be tested on same-domain wrong answers caused by *other* misconceptions, not only on positives; Eedi's Kaggle metric, MAP@25, scores positives only.
3. **Real errors are rarely pure computations.** Only 29 of {{real.n_pos}} real Eedi distractors labelled with our five misconceptions come from questions an exact engine can evaluate, so an engine alone covers little.
4. **Practice must be correct and must actually target the misconception.**
5. **Proving learning** needs counterfactual controls.

## What we already measured (pre-registered before any run)
- **Real data:** {{real.n_pos}} real Eedi positives and {{real.n_neg}} same-domain negatives, five categories plus NONE.

  | Diagnoser | Positives correct | False claims on negatives |
  |---|---|---|
  | GPT-5.5 | {{real.gpt-5.5.accP}} | {{real.gpt-5.5.fcr}} |
  | GPT-5.4-mini | {{real.gpt-5.4-mini.accP}} | {{real.gpt-5.4-mini.fcr}} |
  | GPT-4.1-mini | {{real.gpt-4.1-mini.accP}} | {{real.gpt-4.1-mini.fcr}} |
  | Our executable engine | {{real.exec_accP}} | {{real.exec_fcr}} |

- **Deep synthetic expressions** (7–8 operators; one or two interacting misconceptions, or a slip), share inverted exactly: GPT-5.5 {{inv.gpt-5.5.L3}}, GPT-5.4-mini {{inv.gpt-5.4-mini.L3}}, GPT-4.1-mini {{inv.gpt-4.1-mini.L3}}. GPT-4.1-mini also blamed a misconception for {{inv.gpt-4.1-mini.slipfa}} of the slips.
- **Plainly stated:** frontier reasoning models already diagnose these errors as safely as an exact engine. Our engine fixes only a cheap model's over-claiming: balanced accuracy goes from {{real.gpt-4.1-mini.ba}} to {{real.gated.gpt-4.1-mini.ba}}. So we do not compete on diagnostic accuracy. We design around cost, determinism and verified practice.

## Proposed approach — an exact-first cascade
1. **Executable misconception engine (stage 1).** Each misconception is a bug switch in an exact rational interpreter (Python `fractions` + SymPy), and switches compose. When exactly one known misconception reproduces the answer, the engine names it with checkable evidence in {{cons.engine_ms}}, the same way every time, at no cost: "2/16 is exactly what adding tops and bottoms gives". Otherwise it abstains.
2. **Frontier LLM (stage 2).** Abstentions go to GPT-5.5 with a NONE option and retrieval over Eedi's misconception catalogue (CC BY 4.0).
3. **Discriminative, verified generation.** The generator searches parameters until the target misconception fires and competing misconceptions give pairwise-distinct wrong answers. SymPy re-verifies every key, and the distractors are the bug outputs.
4. **Set-level Bayesian tracer.** An exact posterior over *sets* of held misconceptions across sessions, with remission and relapse. It picks the most informative next item, then switches to targeted practice.
5. **Packs.** School arithmetic (five Eedi-linked misconceptions), and probability / expected value for quantitative reasoning (equiprobability, base-rate neglect, ignoring dependence, adding probabilities, E[X²] vs E[X]²).

## Minimum Viable mapping
| MV bullet | Demoable by the deadline |
|---|---|
| Classify a wrong answer into 3–5 categories | Five categories per pack; exact-first cascade with a posterior, slip/abstain, and feedback that names the rule |
| Generate a targeted practice problem | Discriminative generator; every key SymPy-verified; target firing checked by execution |

## Stretch ambitions
- **Cross-session tracking:** the tracer prototype already runs across sessions.
- **Evidence that targeted practice reduces errors:**
  - Simulated learners (synthetic): {{sim.ours_left}} of initial misconceptions remain after four sessions, vs {{sim.random_left}} under random practice.
  - Then a consented pilot with ~30 learners (pre/post isomorphic items, random-practice control) before the finals.

## Novelty / differentiation
Executable misconceptions are not new: Sleeman's mal-rules, and MalruleLib (ACL 2026). Our contributions:
1. **Evaluation.** Misconception tutors measured against frontier LLMs, with same-domain negatives and pre-registered decision rules.
2. **An exact-first cascade.** TODO-CASCADE
3. **Verified, discriminative generation.** TODO-GEN
4. **Joint tracing of interacting misconceptions** with information-gain item choice. TODO-TRACE

## Evaluation plan
- **Diagnosis (real Eedi):** accuracy, false claims on same-domain negatives, balanced accuracy and bootstrap CIs against three GPT baselines (done, above). Open-set MAP@25 over the catalogue: today {{open.map25_knn}} (kNN).
- **Cascade:** LLM calls, cost and latency per 1,000 diagnoses vs LLM-only; run-to-run consistency.
- **Generation:** key and distractor correctness vs LLM-only; blinded teacher ratings of 50 items.
- **Tracing:** exact-set accuracy and Brier score vs an LLM reading the same history (synthetic now); next-answer log-loss on real Eedi option-level sequences.
- **Learning:** simulation sweep, then the pilot.

## Feasibility and risks
[TEAM: three members and skills.] Twelve components with typed contracts and tests already run end to end on a laptop.

**Milestones:**
- to 31 Oct: packs, cascade service
- to 15 Nov: real-data tracing, web demo
- 19–25 Nov: exams (buffer)
- to 1 Dec: pilot and midway report
- to 15 Dec: demo rehearsals

**Risks and mitigations:**
- Frontier LLMs keep improving, and our edge is not accuracy → re-run the pre-registered benchmark at every milestone.
- Pilot recruitment → start consent early.
- Simulated learning ≠ real learning → the pilot.
- Eedi data via a community mirror → official download.
