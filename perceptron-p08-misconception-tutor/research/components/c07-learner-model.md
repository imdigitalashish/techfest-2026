# C7 Learner model — set-level Bayesian tracer (spike B)

**Responsibility:** Maintain an exact posterior over which *set* of misconceptions a learner holds, across sessions.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Deep KT not reliably better than BKT/logistic ([2112.15072](https://arxiv.org/abs/2112.15072)); pyKT 441 stars, active ([repo](https://github.com/pykt-team/pykt-toolkit)).
- Option Tracing ([2104.09043](https://arxiv.org/abs/2104.09043)); CoLearn soft-evidence BKT with an LLM observation function ([2609.21154](https://arxiv.org/abs/2609.21154)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Exact 2^K joint with composite-bug emissions, remission/relapse between sessions (done) | 5 | 4 | 5 | 4 | 4 | 22 |
| Per-topic factorisation to scale K; graph priors from C1 | 4 | 3 | 4 | 4 | 2 | 17 |
| Fit consistency/slip on real Eedi option-level responses (1.38M rows) and test next-answer log-loss vs option tracing | 5 | 3 | 3 | 5 | 3 | 19 |

## Isolated metric — current value
Exact-set diagnosis accuracy after 4 sessions x 8 items (SYNTHETIC): **0.836** with EIG + named feedback vs 0.658 random (`eval/results/simulation.json`); confounded by how many misconceptions remain, so also report log-loss on real data (to do).

## Next
Real-data validation on option-level sequences.

## Update — pre-registered tracing test (synthetic; home-field for the tracer)
- **Exact held set after 12 answers:** tracer 64.0% (Brier 0.066) vs gpt-5.4-mini 66.0% (Brier 0.073; Δ −2 pp, CI −7 to +3) and gpt-5.5 60.0% (tracer 66.0% on the same 50; n.s.); gpt-4.1-mini 16.0%.
- The tracer has no accuracy edge over reasoning models. It is kept because it is free per learner (GPT-5.5 cost $0.146 per learner in this test) and drives information-gain item choice.
- **Next:** real option-level sequences.
