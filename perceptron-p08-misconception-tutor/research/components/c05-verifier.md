# C5 Verifier

**Responsibility:** Independently check every generated item: key by SymPy, well-formedness, target fires, discrimination.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Khanmigo: calculator + regression tests on tutoring examples ([blog](https://blog.khanacademy.org/why-were-deeply-invested-in-making-ai-better-at-math-tutoring-and-what-weve-been-up-to-lately/)).
- Verified-generation literature (GSM-Symbolic, MathCAMPS): research thread failed tonight — to do.

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| SymPy re-evaluation from a machine-readable expression, never from the generator's own key (done) | 4 | 2 | 5 | 5 | 4 | 20 |
| Mutation testing: inject wrong keys/duplicates/non-firing targets and measure detection | 3 | 3 | 5 | 5 | 2 | 18 |
| Ambiguity check: alternative readings of the stem (e.g. -3^2) must not change the key | 4 | 4 | 4 | 4 | 3 | 19 |

## Isolated metric — current value
Contract test catches an injected wrong key (`components/tests`). Fault-detection rate on a mutation suite: to build.

## Next
Mutation suite + ambiguity check.
