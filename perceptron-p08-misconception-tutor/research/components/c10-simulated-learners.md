# C10 Simulated learners

**Responsibility:** Provide learners with known misconceptions to test diagnosis and policies (SYNTHETIC).
Contracts: [`architecture/components.md`](../../architecture/components.md). Sources are listed with full trails in [`research/notes/`](../notes/) and the [landscape](../landscape.md).

## State of the art / existing practice
- Prompt-only LLM students stay correct regardless of profile (96.8–100% on 379 SAT items; [SSKG](https://arxiv.org/abs/2608.21668v1)); MathDial LLM students ([repo](https://github.com/eth-nlped/mathdial)); Scarlatos et al. AIED 2025 ([2503.06424](https://arxiv.org/abs/2503.06424)).

## Innovation candidates (1–5: impact · novelty · feasibility · measurability · demo)
| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| Program learners executing bug switches with consistency, slip, learning, relapse (done) | 4 | 3 | 5 | 4 | 4 | 20 |
| LLM students conditioned on a hidden programmatic state (answer = bug output when it fires) | 4 | 4 | 4 | 3 | 4 | 19 |
| Fit simulator parameters to Eedi option-choice statistics | 5 | 4 | 3 | 5 | 2 | 19 |

## Isolated metric — current value
Fidelity vs real option statistics: to do. Current parameters are assumptions, swept in 2 settings.

## Next
Calibrate on real data.

## Update (4 Oct)
- The tracing test used these program learners. The tracer shares their generative family, so its result (64.0% vs gpt-5.4-mini 66.0%) is an upper bound on its advantage.
- Calibrating the simulator to real Eedi option statistics remains open.
