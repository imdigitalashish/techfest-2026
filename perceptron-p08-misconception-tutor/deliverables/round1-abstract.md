# Round-1 abstract (draft v1, 4 Oct 2026) — Perceptron 2026, Theme 5 · Problem 8

**Title:** *Find the rule you're actually using — a tutor that executes misconceptions*

*Team placeholders are marked [TEAM]. Every number is from a committed run in `perceptron-p08-misconception-tutor/eval/results/`.*

## Problem and theme
Theme 5 (AI That Teaches), Problem 8: *a tutor that finds the real reason you're stuck*. A learner who writes 1/8 + 1/8 = 1/8 is not missing a fact. They are reliably running a wrong rule ("add the tops, add the bottoms"), and will keep producing that class of error until someone names the rule. [TEAM: 1–2 sentences on why this matters to us.]

## Understanding of the challenge
The task is an **inverse problem**, not plain text classification.
1. **Ambiguity.** One wrong answer can come from different misconceptions, from several interacting ones, or from a careless slip. For (−3)², "doubling instead of squaring" gives −6 and "negative × negative is negative" gives −9. A single response often cannot identify the cause; a better *next question* can.
2. **Targeting is testable.** A follow-up problem targets a misconception only if a learner holding it answers *differently* from one who doesn't. LLM-written "targeted" problems can be wrong, or may not trigger the misconception at all. UMass/Eedi studies find LLMs weak at anticipating real students' errors.
3. **Long tail.** Eedi's public catalogue has 8,117 misconceptions; in our held-out split, 27.9% of test labels never appear in training.
4. **Proving learning** needs counterfactuals: practice effects and regression to the mean fake improvement.

## Proposed approach
- **Executable misconception library.** Each misconception is a *bug switch* that changes one rule of an exact rational interpreter (Python `fractions` + SymPy). Switches compose, so sets of misconceptions can be modelled. The MVP pack has five categories linked to Eedi's catalogue: left-to-right order of operations, squaring = doubling, subtracting a negative, adding fractions top-and-bottom, and negative × negative = negative.
- **Diagnoser.** Bayesian inversion of the programs: P(misconception set | answer), with a consistency rate and an explicit *slip* hypothesis, so the system abstains instead of guessing. Answers outside the library go to an open-set leg in the style of the Eedi Kaggle winners: dense retrieval (Qwen3-Embedding) + GPT-4.1-mini rerank over Eedi's 2,587/8,117 misconception names.
- **Discriminative generator.** It searches problem parameters until the target bug fires and every competing bug gives a different wrong answer. The distractors are the bug outputs, so each generated item is itself a diagnostic question. SymPy re-verifies the key independently.
- **Set-level tracer and policy.** An exact Bayesian filter over *sets* of held misconceptions (2^K states) with remission and relapse between sessions — Bayesian Knowledge Tracing generalised to interacting bugs. While uncertain, the policy picks the item with **maximum expected information gain**. Once P ≥ 0.75, it switches to targeted practice whose feedback names the rule.
- **Bug compiler (scaling).** An LLM turns Eedi misconception text into bug programs. A program is accepted only if it reproduces real, labelled Eedi distractors.
- **Stack.** Python, pydantic contracts, SymPy, NumPy, scikit-learn, Azure OpenAI; Eedi Misconceptions Graph (CC BY 4.0), Kaggle Eedi 2024 data, Eedi option-level responses; web demo with a teacher heat-map.

## Minimum Viable mapping
| MV bullet | What will be demoable |
|---|---|
| Classify a wrong answer into 3–5 categories | 5 executable categories; posterior + slip/abstain; feedback that names the rule |
| Generate a targeted practice problem | Discriminative generator; every item SymPy-verified; target firing checked by execution |

A command-line version of both already runs end to end on a laptop (<0.5 s per turn).

## Stretch ambitions
- **Cross-session tracking:** persisted set-level tracer, already prototyped.
- **Evidence of reduced errors:** program-simulated learners now; a consented pilot (~30 learners, pre/post isomorphic items, random-practice control) before the finals.
- **Quant-reasoning pack:** probability/expected-value misconceptions (equiprobability, conjunction fallacy, base-rate neglect). Executable, verifiable, and relevant to Optiver.

## Novelty / differentiation
The obvious baseline prompts an LLM to classify and then to "write a problem about X". Executable misconceptions alone are not new: Sleeman's mal-rules (1980s) and MalruleLib (ACL 2026, 101 mal-rules). What we add:
- validation of misconception programs against **real student distractors**;
- **discriminative, machine-verified** item generation;
- **joint tracing of interacting misconceptions** with information-gain item choice;
- **slip abstention**.

## Evaluation plan
- **Classification (real Eedi data).** 129 distractors labelled with our five misconceptions. Today: majority 30.2%, TF-IDF 38.0%, executable→TF-IDF hybrid 45.7%. The executable path never attributed a distractor to the wrong category (0/129) and over-claims on 1.8% of 165 other-labelled distractors. Baselines to add: LLM zero-shot and dense+rerank. Bootstrap CIs. Open set: MAP@25 on 904 held-out pairs (kNN today: 0.326).
- **Generation.** Verified-targeted yield and discriminative rate, ours vs LLM-only; blinded teacher ratings of 50 items.
- **Bug programs.** Real-distractor reproduction rate: 16.3% today, 39.6% where the expression parses.
- **Tracing.** Next-answer log-loss on real Eedi option-level sequences vs BKT and Option Tracing.
- **Learning (simulated, labelled synthetic).** 2×2 factorial (random vs information-gain selection × generic vs rule-naming feedback) plus an oracle, 450 learners per arm. Share of initial misconceptions still held after 4 sessions: 5.5% (ours) vs 58.4% (random practice). Even if naming the rule adds nothing, selection alone gives 28.0%. Then the pilot.

## Feasibility and risks
[TEAM: three members and skills — e.g. ML/LLM systems, maths education, front-end.] Twelve components behind typed contracts already pass contract tests.

**Milestones:**
- to 31 Oct: LLM baselines and bug compiler
- to 15 Nov: real-data tracing, quant pack
- 19–25 Nov: exams, buffer
- to 1 Dec: pilot and midway report
- to 15 Dec: web demo and rehearsals

**Risks and mitigations:**
- Parser recovers only 41% of real Eedi items → widen the grammar, add LLM extraction checked by SymPy.
- Executable coverage is small → hybrid with retrieval, plus the bug compiler.
- Simulation ≠ learning → assumption sweeps and the pilot.
- LLM outages → cached runs; the executable path needs no LLM.
- Data terms → Eedi graph is CC BY; Kaggle data used for non-commercial research only.
