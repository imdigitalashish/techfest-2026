# C6 — Linking + small-area estimation

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Coherent block/district estimates with intervals, benchmarked to PARAKH/ASER.

**State of the art / what is deployed.** Fay–Herriot / hierarchical Bayes with benchmarking (World Bank poverty mapping; R `emdi`, `sae`) — `sources/methods-sae-audit.md`.

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| FH with 2 covariates (≈ 6 blocks/district) + precision-weighted benchmarking with anchor variance propagated | 4·3·4·5·3 |
| Hierarchical Bayes over block → cluster → school (PyMC) | 4·3·3·5·3 |
| MRP using UDISE+ composition (SC/ST, single-teacher) | 3·3·3·4·3 |

**Status.** Now a Fay–Herriot model on the **reporting bias** (direct = block's HT-weighted re-test residual; synthetic = risk-stratified model; τ² by an adjusted likelihood that stays positive with ~6 blocks), then precision-weighted benchmarking to a same-construct survey only. Covered by the pre-registered test (see C5).

**Isolated metric.** Block RMSE (pp); 90 % CI coverage; |aggregate − anchor|.
