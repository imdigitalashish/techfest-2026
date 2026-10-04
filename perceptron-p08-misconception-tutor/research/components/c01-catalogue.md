# C1 Catalogue (misconception label space)

**Responsibility:** Hold the label space and link executable pack entries to Eedi ids.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Eedi Misconceptions Graph v1.0 (CC BY 4.0): 8,117 misconceptions x 2,258 constructs, 19,294 weighted edges ([card](https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph)).
- Kaggle Eedi 2024 corpus: 2,587 misconception names (mirror `cdtmc/eedi-ir`, research use).
- Algebra benchmark: 55 misconceptions, 220 examples ([2412.03765](https://arxiv.org/abs/2412.03765)); MalruleLib 101 mal-rules ([ACL 2026](https://aclanthology.org/2026.acl-long.690/)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Link pack entries to Eedi ids by exact name match (done: 5/5) | 3 | 1 | 5 | 5 | 3 | 17 |
| Embedding-based dedup/merge of near-synonym Eedi labels (e.g. 'Multiplies by the index' ~ SQ_DOUBLE) | 4 | 3 | 4 | 4 | 2 | 17 |
| Construct-graph walk to suggest which misconceptions co-occur (graph edge weights) as tracer priors | 4 | 4 | 4 | 3 | 3 | 18 |

## Isolated metric — current value
Link coverage = share of pack misconceptions with >=1 verified Eedi id: **5/5** (`components/bugs/school_math.py` EEDI_LINKS, checked against the downloaded files 2026-10-04).

## Next
Use graph co-occurrence weights as tracer priors; synonym clustering so evaluation counts equivalent labels.
