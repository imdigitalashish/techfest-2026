# C3 Bug library — executable misconceptions (spike A)

**Responsibility:** Predict, for any item, the exact wrong answer each misconception (or set of them) produces.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Classical mal-rules: Sleeman's Leeds Modelling System ([ERIC ED258845](https://eric.ed.gov/?id=ED258845)); BUGGY/DEBUGGY (UNVERIFIED tonight).
- MalAlgoPy ([2410.12294](https://arxiv.org/abs/2410.12294)); MalruleLib: 101 mal-rules, 498 templates, LLM accuracy 66% -> 40% on cross-template misconception prediction ([ACL 2026](https://aclanthology.org/2026.acl-long.690/)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Bug *switches* on one exact interpreter so bugs compose (done: 5 bugs) | 5 | 4 | 5 | 5 | 5 | 24 |
| LLM bug compiler: misconception text -> switch/program, accepted only if it reproduces labelled Eedi distractors | 5 | 5 | 3 | 5 | 4 | 22 |
| Probability/EV pack (equiprobability, conjunction, base-rate neglect, independence) for an Optiver demo | 4 | 4 | 4 | 4 | 5 | 21 |
| Python 'predict the output' pack (aliasing, off-by-one, integer division) | 4 | 3 | 4 | 4 | 4 | 19 |

## Isolated metric — current value
Real-distractor reproduction rate on 129 Eedi distractors labelled with our 5 misconceptions: **16.3%** overall, **39.6%** where the expression parses; wrong-attribution **0.0%**; false-claim rate on 165 other-labelled distractors **1.8%** (`eval/results/diagnosis.json`).

## Next
Improve the LaTeX->expression parser (41% parse rate) and add the bug compiler; both are autoresearch targets.
