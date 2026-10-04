# C9 Feedback

**Responsibility:** Tell the learner which rule they applied, Socratically, without giving away answers prematurely or stating unverified numbers.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- LearnLM pedagogy evaluation ([2412.16429](https://ar5iv.labs.arxiv.org/html/2412.16429)); Claude Learning mode ([launch](https://www.anthropic.com/news/introducing-claude-for-education)); Eedi x DeepMind human-in-the-loop trial ([Eedi](https://www.eedi.com/news/new-exploratory-research-from-eedi-and-google-deepmind-reveals-human-in-the-loop-ai-tutoring-outperforms-human-only-support)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Template feedback naming the rule (done) | 3 | 2 | 5 | 3 | 4 | 17 |
| LLM Socratic dialogue grounded in the bug trace; every number re-verified by C5 | 4 | 3 | 4 | 3 | 5 | 19 |
| Refutation/contrasting-case item pairs generated from the bug (worked example of the bug vs the rule) | 4 | 4 | 4 | 3 | 5 | 20 |

## Isolated metric — current value
Rubric pass rate: to define (names misconception; no premature answer; numbers verified).

## Next
LLM version once access is restored.
