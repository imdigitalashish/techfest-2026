# Round-1 abstract (draft v1, 4 Oct 2026) — Perceptron 2026, Theme 5 · Problem 8

**Title:** *Find the rule you're actually using — a tutor that executes misconceptions*

*Team placeholders are marked [TEAM]. Every number is from a committed run in `perceptron-p08-misconception-tutor/eval/results/`.*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8: *a tutor that finds the real reason you're stuck*. A learner who writes 1/8 + 1/8 = 1/8 is not missing a fact. They are reliably running a wrong rule ("add the tops, add the bottoms"), and will keep producing that class of error until someone names it. [TEAM: 1–2 sentences on why this matters to us.]

## Understanding of the challenge
The task is an **inverse problem**, not plain text classification.
1. **Ambiguity.** One wrong answer can come from different misconceptions, from several interacting ones, or from a slip. For (−3)², "doubling instead of squaring" gives −6 and "negative × negative is negative" gives −9. One response often cannot identify the cause; a better *next question* can.
2. **Targeting is testable.** A problem targets a misconception only if a learner holding it answers *differently* from one who doesn't. So every generated item must be checked, not trusted.
3. **Long tail.** Eedi's public catalogue has 8,117 misconceptions; in our held-out split, 27.9% of test labels never appear in training.
4. **Proving learning** needs counterfactuals: practice effects and regression to the mean fake improvement.

## Proposed approach
- **Executable misconception library.** Each misconception is a *bug switch* that changes one rule of an exact rational interpreter (Python `fractions` + SymPy). Switches compose, so sets of misconceptions can be modelled. The MVP pack has five categories linked to Eedi's catalogue: left-to-right order of operations, squaring = doubling, subtracting a negative, adding fractions top-and-bottom, and negative × negative = negative.
- **Diagnoser.** Bayesian inversion of the programs: P(misconception set | answer), with a consistency rate and an explicit *slip* hypothesis, so the system abstains instead of guessing. Answers outside the library go to an LLM plus retrieval over Eedi's catalogue.
- **Discriminative generator.** It searches problem parameters until the target bug fires and every competing bug gives a different wrong answer. The distractors are the bug outputs, so each generated item is itself a diagnostic question. SymPy re-verifies the key independently.
- **Set-level tracer and policy.** An exact Bayesian filter over *sets* of held misconceptions (2^K states) with remission and relapse between sessions — Bayesian Knowledge Tracing generalised to interacting bugs. While uncertain, the policy picks the item with **maximum expected information gain**. Once P ≥ 0.75, it switches to targeted practice whose feedback names the rule.
- **Bug compiler (scaling).** An LLM turns Eedi misconception text into bug programs. A program is accepted only if it reproduces real, labelled Eedi distractors.
- **Stack.** Python, pydantic, SymPy, scikit-learn, Azure OpenAI; Eedi Misconceptions Graph (CC BY 4.0), Kaggle Eedi 2024 data; web demo with a teacher heat-map.

## Minimum Viable mapping
| MV bullet | What will be demoable |
|---|---|
| Classify a wrong answer into 3–5 categories | 5 executable categories; posterior + slip/abstain; feedback that names the rule |
| Generate a targeted practice problem | Discriminative generator; every item SymPy-verified; target firing checked by execution |

## Stretch ambitions
- **Cross-session tracking:** persisted set-level tracer, already prototyped.
- **Evidence of reduced errors:** simulated learners now; a ~30-learner pilot before the finals.
- **Quant-reasoning pack:** probability/expected-value misconceptions (equiprobability, base-rate neglect): executable, verifiable, Optiver-relevant.

## Novelty / differentiation
The obvious baseline prompts an LLM to classify and then to "write a problem about X". We measured it, and it is strong on simple arithmetic: 86.0% classification and 40/40 valid targeted items. So our claim is *not* "beats the LLM at labelling". Executable misconceptions aren't new either: Sleeman's mal-rules (1980s) and MalruleLib (ACL 2026, 101 mal-rules). What no source we opened offers, and the LLM baseline lacks:
- **(i) Exactness and auditability.** Misconception programs are validated against **real student distractors**: when our executable path fires, it has been right 21/21 times.
- **(ii) Separation of the learner's *current* competing hypotheses.** The policy chooses the most informative next question over interacting misconceptions, and generation enforces pairwise-distinct wrong answers for exactly those hypotheses.
- **(iii) Slip abstention.**

## Evaluation plan
- **Classification (real Eedi data).** 129 distractors labelled with our five misconceptions: majority 30.2%, TF-IDF 38.0%, GPT-4.1-mini zero-shot 86.0% (95% CI 79.8–92.2), executable→LLM hybrid 86.8% (not a significant gain). Next: harder packs and the open-set leg (MAP@25; kNN today 0.326).
- **Generation.** Verified-targeted yield and discriminative rate, ours vs LLM-only, on harder families (word problems, probability); blinded teacher ratings of 50 items.
- **Bug programs.** Real-distractor reproduction: 15.5% → 19.0% (dev split) after the first automated improvement loop.
- **Tracing.** Next-answer log-loss on real Eedi option-level sequences vs BKT and Option Tracing.
- **Learning (simulated, labelled synthetic).** Selection {random, information-gain} × feedback {generic, names the rule} + oracle, 450 learners per arm. Share of initial misconceptions still held after 4 sessions: 5.5% (ours) vs 58.4% (random practice); 28.0% if naming the rule adds nothing. Then a consented pilot with pre/post isomorphic items and a random-practice control.

## Feasibility and risks
[TEAM: three members and skills — e.g. ML/LLM systems, maths education, front-end.] Twelve components behind typed contracts already pass contract tests and run end to end in under 0.5 s per turn.

**Milestones:**
- to 31 Oct: LLM baselines and bug compiler
- to 15 Nov: real-data tracing, quant pack
- 19–25 Nov: exams, buffer
- to 1 Dec: pilot and midway report
- to 15 Dec: web demo and rehearsals

**Risks and mitigations:**
- Parser recovers only ~45% of real Eedi items → widen the grammar; LLM extraction checked by SymPy.
- Small executable coverage → hybrid with the LLM and retrieval, plus the bug compiler.
- Simulation ≠ learning → assumption sweeps and the pilot.
- LLM outages → cached runs; the executable path needs no LLM.
