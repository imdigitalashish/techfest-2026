# ADR 001 — Spike choice: executable misconceptions → verified discriminative generation, plus set-level Bayesian tracing

- **Status:** accepted (first version, 4 Oct 2026 06:30 IST). Independent adversarial review by a separate agent is **pending**: the Supervisor ran lean mode after the overnight network outage. The antithesis below was written by the lead, deliberately against our own interest.
- **Deciders:** P8 lead. **Evidence:** [`research/landscape.md`](../../research/landscape.md), [`eval/results/`](../../eval/results/).

## Context
The brief's MVP has two parts: (1) classify a wrong answer into one of 3–5 misconception categories; (2) generate a new practice problem targeted at that category. The stretch has two more: (3) track misconceptions across sessions; (4) show the targeted problems reduce that error type. The obvious baseline is an LLM prompted to classify and then to "write a problem about X". Judges weight innovation beyond the starter baseline at 20% and evaluation rigour at 15%. In this competition the finals need a working demo.

## Candidates (scored 1–5: judged impact · novelty vs SOTA · feasibility by 15 Dec · measurability · demoability)

| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| **A. Executable misconceptions → exact diagnosis + SymPy-verified *discriminative* generation; validated against real Eedi distractors** | 5 | 4 | 5 | 5 | 5 | **24** |
| **B. Set-level Bayesian misconception tracer (2^K joint) + expected-information-gain item choice + slip abstention** | 4 | 4 | 5 | 4 (simulation now; real option data at finals) | 4 | **21** |
| C. Eedi-winner-style retrieval + LLM rerank over the 2,587/8,117 catalogue | 3 | 1 (it *is* the SOTA recipe) | 4 (GPU-hungry to match winners) | 5 (MAP@25) | 2 | 15 |
| D. Fine-tuned LLM student simulators (MalAlgoPy-style) | 3 | 2 | 3 | 3 | 3 | 14 |
| E. Deep KT (pyKT AKT/SAKT) on ASSISTments | 2 | 1 | 4 | 4 | 2 | 13 |
| F. LLM "bug compiler": misconception text → executable program, auto-validated on Eedi distractors | 5 | 5 | 3 | 4 | 4 | 21 → **stretch of A** |

**Decision:** spike **A** (C3 bug library, C4 diagnoser, C6 generator), with **F** as its autoresearch extension (scale the library beyond hand-written bugs). Second spike **B** (C7 tracer, C8 policy). C is kept as the open-set fallback, implemented with best existing practice. D and E are rejected.

## Six Thinking Hats (A + B)
- **White — facts and data (all ours are from committed runs):**
  - On 129 real Eedi distractors labelled with our five misconceptions, the bug programs reproduce the exact labelled wrong answer in 16.3% of cases overall, and in 39.6% when our LaTeX parser recovers the expression. They **never** attribute a distractor to the wrong one of our five (0.0%).
  - On 165 distractors labelled with *other* misconceptions they claim a pack misconception 1.8% of the time. 2 of those 3 cases are Eedi labels that state the same rule in other words ("Multiplies by the index" vs SQ_DOUBLE).
  - Exec→TF-IDF hybrid: **45.7%** closed-set accuracy, vs TF-IDF 38.0% and majority class 30.2%.
  - **The LLM baseline is strong:** GPT-4.1-mini zero-shot gets **86.0%** (95% bootstrap CI 79.8–92.2); exec→LLM hybrid 86.8% (80.6–92.2) — a gain of one item, not significant. When the executable path fires it is right 21/21 (LLM 20/21 on those items).
  - LLM-only *generation* (GPT-4.1-mini, 40 calls) produced **40/40** items with correct keys whose target bug fires. On simple arithmetic the generation edge is control and verification, not validity.
  - Generator: 400/400 items verified by SymPy, target fires in all of them, all discriminative — **true by construction**, so the interesting comparison is the LLM-only baseline (pending, see below).
  - Simulation (SYNTHETIC): EIG + named feedback leaves 5.5% of initial misconceptions after 4 sessions, vs 58.4% for random practice + generic feedback.
  - Prior art: executable mal-rules exist (MalruleLib, ACL 2026: 101 mal-rules over 498 templates; Sleeman's LMS). LLMs are weak at anticipating real students' errors (UMass 2024).
- **Red — gut feel and the judges:** an Optiver/IITB panel will like *exactness*: "your answer 1/8 is exactly what adding tops and bottoms gives" is a crisp, auditable moment. A math-verified, abstaining system contrasts with chatbots that hallucinate arithmetic. Risk to that impression: it looks like "just rules".
- **Black — risks:**
  1. Hand-written bugs don't scale to Eedi's 8,117 misconceptions, many of them conceptual or visual (geometry, graphs).
  2. Our LaTeX parser recovers only 41% of real items.
  3. The simulation shows the *policy* works under *our* learning assumptions, not that students learn. Its effect is partly mechanical: targeting creates more feedback opportunities. The pessimistic setting isolates this and still shows half the remaining misconceptions vs random (28.0% vs 58.4%).
  4. MalruleLib narrows the novelty claim.
  5. 2^K joint states blow up beyond K≈12. It must be factored per topic.
- **Yellow — benefits:** one artefact (the bug program) drives three things: diagnosis likelihood, distractor choice and verification. Generated items are correct by verification, not by trust. Every prediction is explainable ("this is the rule you applied"). Exact inference gives calibrated posteriors and principled abstention (a slip is recognised as a slip). Compute is cheap (ms per item on the Mac). The same design works for probability/EV (Optiver-relevant) and Python "predict the output" packs.
- **Green — alternatives and wild ideas:**
  - LLM bug compiler with execution feedback (F).
  - Use real Eedi option-level responses (1.38M rows) to fit consistency and slip and to test tracing on real sequences.
  - A probability/expected-value pack for an Optiver-flavoured demo.
  - Active learning: generated items whose responses disagree with every bug become candidates for *new* misconceptions, routed to a teacher.
- **Blue — decision process:** pick the spikes that maximise (judged impact × measurability). Keep the open-set LLM path as a fallback so coverage never depends on the executable library. Re-decide at the 12 Oct selection memo with the LLM baselines and the bug-compiler loop results.

## Thesis → antithesis → synthesis
- **Thesis.** Diagnosis is an inverse problem. Wrong answers are outputs of procedures, so the most faithful model of a misconception is the procedure itself. Executing it gives exact likelihoods, verified keys, and items designed to separate competing hypotheses. That is what Eedi's human authors do by hand, and what LLMs are measurably bad at.
- **Antithesis** (strongest case against).
  1. Real student errors are messy: half of the real items we parsed have a key that our evaluator doesn't reproduce (47% key agreement), because the question isn't a pure evaluation ("where do the brackets go?").
  2. Executable coverage is tiny next to an LLM that "knows" thousands of misconceptions.
  3. A rule engine with a Bayesian layer is 1980s ITS technology. Judges may see it as old.
  4. The headline learning result is simulated.
  5. MalruleLib already did executable misconceptions at scale.
- **Synthesis.**
  - **Post-baseline update (07:45 IST):** the LLM-only baselines are strong on this pack (86.0% classification; 40/40 valid generation). Spike A's value therefore lies in *exactness* (21/21 when it fires), *auditability*, *zero-cost offline operation*, and being the substrate for spike B. It is not raw accuracy. Spike B (set-level tracing + information gain), plus evaluation on harder packs (word problems, probability), carries the innovation claim.
  - Make the *hybrid* the product: executable where we can verify, LLM retrieval where we can't, and say which applied in every diagnosis ("evidence: bug_exact" vs "retrieval").
  - Claim novelty only where the sources leave room: validation against real distractors, discriminative verified generation, joint set-level tracing with EIG, slip abstention.
  - Grow coverage with the LLM bug compiler (F), whose output is *checked* against Eedi distractors rather than trusted.
  - Present the simulation as a policy test with an assumption sweep, and plan a small real pilot (pre/post isomorphic items, random-practice control) before the finals.
  - Frame the 1980s lineage as a strength: 2026 frontier work (CoLearn, PLCD, SLOW) is converging on exactly this — LLMs as evidence functions inside classic psychometric models.

## First principles
The real bottleneck is **identifiability**, not classification capacity. One wrong answer is usually consistent with several misconceptions and with a slip. No classifier can resolve that from one observation; only a *better next question* can. Hence the information-gain policy and discriminative generation. Second bottleneck: **trust in generated items**. An unverified "targeted" problem may neither be correct nor trigger the misconception. Hence execution-based verification.

## Consequences
- C3, C4, C6, C7 and C8 get autoresearch loops (first: generator / diagnosis coverage).
- Contracts expose `predicted` answers and `p_slip` so any diagnoser can be swapped in.
- Next evidence to collect: LLM-only baselines for classification and generation (Azure OpenAI being provisioned), bug-compiler validation rate on Eedi, real option-level tracing (Eedi NeurIPS-2020-style data), a small human pilot.

## Revision 1 — 2026-10-04 16:23 IST, after the pre-registered LLM-gap tests
The protocol and runner were committed before any run: [`eval/llm_gap_protocol.md`](../../eval/llm_gap_protocol.md). Every number below is from `eval/results/` and reproduces offline with `--offline`.

| Pre-registered test | Engine / tracer | GPT-4.1-mini | GPT-5.4-mini | GPT-5.5 |
|---|---|---|---|---|
| Real Eedi: positives correct / false claims on 152 same-domain negatives | 19.1% / 0.0% | 55.7% / 15.8% | 69.5% / 0.0% | 79.4% / 0.0% |
| Synthetic inversion, 7–8 operators: exact set | 100% (by construction) | 11.7% | 95.0% | 100.0% |
| Synthetic tracing: exact held set after 12 answers | 64.0% | 16.0% | 66.0% | 60.0% (tracer 66.0% on the same 50) |
| Synthetic probability: key and misconception answer both exact | 100% (by construction) | 36.7% | 96.7% | 100.0% |

**Decision.**
- **Spike A as framed above** ("executable diagnosis beats LLM diagnosis") is **refuted for reasoning models**: every pre-registered gap (H1–H7) holds only against gpt-4.1-mini.
- **Spike A is re-scoped** as stage 1 of an *exact-first cascade* and as the generator's verifier. Its claims are now determinism, zero marginal cost, millisecond latency and exact, checkable evidence. Accuracy is no longer claimed.
- **Spike B (set-level tracer)** is statistically indistinguishable from GPT-5.4-mini and GPT-5.5 reading the same history, even on synthetic learners drawn from its own model family. It stays, for cost (GPT-5.5 cost $0.146 per learner here) and for information-gain item choice, with no accuracy claim.

**Hats, revised.**
- **White:** the table above.
- **Red:** much less impressive than the overnight framing.
- **Black:** a judge will ask "why not GPT-5.5 everywhere?". The honest answer is cost, latency, determinism and verification guarantees, not accuracy.
- **Yellow:** exact evidence, and items that are verified rather than trusted.
- **Green:** the only remaining differentiator a judge would weigh heavily is *real learning evidence* (the pilot).
- **Blue:** at the 12 Oct selection, P8 should not be the Perceptron pick unless the team values the education theme and can run the pilot.

## Revision 2 — 2026-10-04 17:15 IST, after the cross-model reviews ([responses](../../reviews/2026-10-04-responses.md))
- **Wording corrections to Revision 1.**
  - "Refuted for reasoning models" should read "not supported by these tests". No equivalence margin was registered, and non-detection is not equivalence.
  - "Exact inference gives calibrated posteriors" (Hats, Yellow) is not established. The tracer showed only a Brier-score comparison under the simulated distribution.
- **Corrected economics.** Costs are now summed over the routed items:
  - Probability items (engine-native; routing fixed by construction): $7.32 → $5.08 per 1,000 diagnoses (−30.5%, not −50%).
  - Real items (post hoc): $6.50 → $6.10 (−6.2%).
- **Decision.**
  - **A becomes dependable infrastructure:** certificates ("this rule reproduces this answer"), deterministic and verified arithmetic practice. It is not presented as diagnosing the learner's true belief.
  - **B stays a bounded adaptive policy,** to be compared with simpler policies and with an LLM tutor given the same history.
  - **The new spike is learner benefit:** a randomised pilot of our tutor vs a GPT-5.5 tutor, with matched items, time and interface.
  - **Scope cut:** the bug compiler (F), catalogue-to-tracer integration and the probability pack are stretch goals; the MVP is the five-misconception arithmetic pack.
