# C12 Open-set catalogue retrieval

**Responsibility:** Rank Eedi's catalogue for any question/distractor the executable library doesn't cover.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Eedi 2024 winning recipe (retrieval + rerank, synthetic data) ([Eedi blog](https://www.eedi.com/news/from-wrong-answers-to-real-insights-how-we-used-a-kaggle-challenge-to-map-student-misconceptions)); leaderboard scores UNVERIFIED tonight.

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Lexical + kNN baselines (done) | 2 | 1 | 5 | 5 | 1 | 14 |
| Dense retriever (Qwen3-Embedding) + LLM rerank | 3 | 1 | 4 | 5 | 2 | 15 |
| Bug-compiler-generated synthetic distractors as training data | 4 | 4 | 3 | 5 | 2 | 18 |

## Isolated metric — current value
MAP@25 on 904 held-out pairs: kNN **0.326**, TF-IDF+kNN Recall@25 **0.654** (`eval/results/diagnosis.json`).

## Next
Dense + rerank.
