# C6 Item generator (spike A)

**Responsibility:** Produce new practice items where the target misconception fires and competing misconceptions give different wrong answers; distractors are bug outputs.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Eedi diagnostic questions: each distractor tied to one misconception, human-authored ([card](https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph)).
- DiVERT, overgenerate-and-rank: LLM distractors need real-student alignment ([2406.19356](https://arxiv.org/abs/2406.19356), [2405.05144](https://arxiv.org/abs/2405.05144)).
- Khanmigo Practice My Knowledge: teacher-reviewed targeted MCQs ([blog](https://blog.khanacademy.org/new-ai-tools-bring-interactive-diagrams-and-targeted-practice-thanks-to-khan-academys-partnership-with-google-org/)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Rejection-sampling over parameterised families with target-fires + pairwise-distinct constraints (done) | 5 | 4 | 5 | 5 | 5 | 24 |
| Difficulty control via IRT fitted on Eedi option data | 3 | 3 | 3 | 4 | 3 | 16 |
| LLM proposes *new families* (word problems, contexts); bug programs + SymPy verify them | 5 | 4 | 3 | 4 | 5 | 21 |

## Isolated metric — current value
Template generator: 400/400 items SymPy-verified, target fires 100%, discriminative 100%, 0.4–3 ms/item (`eval/results/generation.json`; true by construction). LLM-only baseline: pending (LLM access).

## Next
Run the LLM-only baseline; add LLM-proposed families verified by the same checks.
