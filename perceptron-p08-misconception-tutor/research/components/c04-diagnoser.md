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
MVP closed set (real, n=129): majority **30.2%**, TF-IDF **38.0%**, exec->TF-IDF hybrid **45.7%**, GPT-4.1-mini zero-shot **86.0%** (95% CI 79.8–92.2), exec->LLM hybrid **86.8%** (80.6–92.2; +1 item, not significant). Exec path right 21/21 when it fires. Open set (real, 904 held-out pairs, 388 questions, 27.9% unseen labels): BM25 MAP@25 **0.093**, TF-IDF **0.120**, kNN over training labels **0.326**, TF-IDF+kNN Recall@25 **0.654**.

## Next
Add the LLM leg (Azure OpenAI) and a dense retriever; report hybrid gains with bootstrap CIs.

## Update — pre-registered LLM-gap tests (4 Oct, `eval/llm_gap_protocol.md`)
- **Real Eedi data** (131 positives, 152 same-domain negatives, NONE allowed):

  | Diagnoser | Positives correct | False claims on negatives |
  |---|---|---|
  | Engine | 19.1% | 0.0% |
  | gpt-4.1-mini | 55.7% | 15.8% |
  | gpt-5.4-mini | 69.5% | 0.0% |
  | gpt-5.5 | 79.4% | 0.0% |

  The gated hybrid helps only gpt-4.1-mini: balanced accuracy 70.0% → 78.2%.
- **Decision:** C4 becomes an **exact-first cascade** (engine claim, else LLM). It has no accuracy edge over reasoning models.
  - On real items (post hoc), GPT-5.5 cost per 1,000 diagnoses falls $6.50 → $6.10 (−6.2%), because the engine explains only 26/304.
  - On engine-native probability items, LLM calls halve by design. Cost per 1,000 falls only $7.32 → $5.08 (−30.5%), because routed slip answers cost more. This is a construction-guaranteed accounting demonstration, not independent evidence.
  - Costs are summed over the items actually routed (a review fix; earlier versions wrongly multiplied average cost by the routed fraction).
  - The engine gave identical outputs on 304/304 items over two passes (median 0.06 ms). GPT-5.5 changed 2 of 40 repeated diagnoses.
