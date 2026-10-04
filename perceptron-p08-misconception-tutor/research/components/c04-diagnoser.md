# C4 Diagnoser (spike A)

**Responsibility:** Map a wrong answer to a posterior over misconceptions plus a slip probability, or abstain.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Eedi 2024 winners: Qwen retrieval + rerank, LoRA/contrastive training on 10k synthetic + 1.8k real examples, Claude rationales ([Eedi blog](https://www.eedi.com/news/from-wrong-answers-to-real-insights-how-we-used-a-kaggle-challenge-to-map-student-misconceptions)).
- LLMs weak at anticipating real errors unless ranked on student data ([2404.02124](https://arxiv.org/abs/2404.02124)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Exact bug-likelihood Bayes with slip hypothesis (done) | 5 | 4 | 5 | 5 | 5 | 24 |
| Hybrid: exact where executable, retrieval/LLM otherwise (done with TF-IDF; LLM pending) | 5 | 3 | 5 | 5 | 4 | 22 |
| Calibrated abstention (temperature on LLM scores; slip prior learned from data) | 4 | 4 | 4 | 4 | 3 | 19 |
| Open-set dense retriever (Qwen3-Embedding) + LLM rerank to approach Eedi-winner MAP@25 | 3 | 1 | 4 | 5 | 2 | 15 |

## Isolated metric — current value
MVP closed set (real, n=129): TF-IDF **38.0%**, exec->TF-IDF hybrid **45.7%**, majority **30.2%**. Open set (real, 904 held-out pairs, 388 questions, 27.9% unseen labels): BM25 MAP@25 **0.093**, TF-IDF **0.120**, kNN over training labels **0.326**, TF-IDF+kNN Recall@25 **0.654**.

## Next
Add the LLM leg (Azure OpenAI) and a dense retriever; report hybrid gains with bootstrap CIs.
