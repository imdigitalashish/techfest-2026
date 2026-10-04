# C11 Tutor orchestrator + session store

**Responsibility:** Run sessions end to end and persist learner state between them.
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Khanmigo A/B: learning-history signals improved next-item correctness +6.1% over 20 tests ([blog](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| CLI with JSON state per learner (done) | 3 | 1 | 5 | 4 | 3 | 16 |
| Web UI with teacher dashboard (misconception heatmap per class) | 4 | 2 | 4 | 3 | 5 | 18 |

## Isolated metric — current value
End-to-end demo: `python -m components.tutor.cli --learner demo --simulate SUB_NEG,FRAC_ADD --items 8 --seed 1` (2 sessions run, state persisted).

## Next
Web UI for finals.
