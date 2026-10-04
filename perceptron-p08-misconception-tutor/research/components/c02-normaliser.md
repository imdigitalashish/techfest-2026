# C2 Answer normaliser

**Responsibility:** Turn raw learner input into a canonical exact value comparable with bug predictions.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Exact rational parsing (`fractions.Fraction`); SymPy `parse_expr` for algebraic answers.
- Khan Academy routes numeric work through a backend calculator rather than trusting the LLM ([blog](https://blog.khanacademy.org/why-were-deeply-invested-in-making-ai-better-at-math-tutoring-and-what-weve-been-up-to-lately/)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Rational/mixed-number/decimal/option-letter parsing (done) | 3 | 1 | 5 | 5 | 2 | 16 |
| Handwriting/photo input via a vision model, verified by re-parse | 3 | 2 | 3 | 3 | 5 | 16 |
| Free-text explanation parsing (MAP-2025-style) into a step trace | 4 | 3 | 3 | 3 | 4 | 17 |

## Isolated metric — current value
Canonicalisation accuracy on labelled strings: **8/8** contract cases (`components/tests`). To grow to a 200-string labelled set.

## Next
Add explanation parsing so diagnosis can use *why* as well as *what*.
