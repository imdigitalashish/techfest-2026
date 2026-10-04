# C8 Policy — information-gain diagnosis, targeted remediation (spike B)

**Responsibility:** Choose the next item: maximise expected information gain while uncertain; target the top misconception once P >= 0.75.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- EduLoop-Agent: diagnosis -> adaptive testing -> LLM feedback on ASSISTments ([2510.22559](https://arxiv.org/abs/2510.22559)).
- Exact-phrase searches for EIG in misconception diagnosis returned nothing (not proof of absence).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| EIG over the set-level joint + targeted remediation (done) | 5 | 4 | 5 | 5 | 5 | 24 |
| Generate the max-EIG item directly (optimise generator parameters for EIG) instead of picking from a pool | 5 | 5 | 4 | 5 | 4 | 23 |
| Spacing/interleaving schedule across sessions | 3 | 2 | 4 | 3 | 3 | 15 |

## Isolated metric — current value
Initial misconceptions still held after 4 sessions (SYNTHETIC, 450 learners/arm): ours **5.5%** vs random+generic **58.4%**, oracle **1.1%**; pessimistic setting (named feedback no better) **28.0%** vs 58.4%.

## Next
EIG-optimal generation; run on LLM-simulated students with a hidden programmatic state.

## Update (4 Oct)
- The inversion test shows reasoning models can also identify interacting misconceptions exactly: gpt-5.5 100.0% at 7–8 operators, gpt-5.4-mini 95.0%, gpt-4.1-mini 11.7%.
- The policy's value is therefore item choice and cost, not identification accuracy. Its simulated-learning result (5.5% vs 58.4% of misconceptions left) remains synthetic until the pilot.
