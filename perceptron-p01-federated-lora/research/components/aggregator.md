# C6 Aggregator — component research (SPIKE)

**Contract:** payloads `{device → {layer → tensor}}` + metas (n_examples, planned_steps, steps_done) → new global adapter + `AggregationReport` (weights, influence shares, aggregation error). **Isolated metric:** macro held-out loss after 12 rounds of the fixed *dropout* scenario (SmolLM2-135M, 5 devices; `components/aggregator/autoresearch/eval.py`). Secondary: aggregation error, dominance index, worst-domain loss.

## State of the art (sources verified 2026-10-04 — see `research/landscape.md` §2)
- Naive FedAvg over A and B is inexact; FFA-LoRA (ICLR 2024) names the "discordance" and freezes A; FedEx-LoRA (ACL 2025) adds a residual for exactness; FedSA-LoRA (ICLR 2025) shares selectively (A general, B client-specific); LoRA-FAIR (ICCV 2025) refines aggregation and initialisation; Fed-SB (2025) targets communication; RoLoRA (NeurIPS 2025) alternates A/B and argues for trainable A; heterogeneous ranks: HetLoRA, FlexLoRA, FLoRA (2024), FedRoRA (Sep 2026, personalised); newest: iFLoRA (ACL Findings 2026), CLAIR (May 2026).

## Innovation candidates (scored 1–5: impact on judging · novelty · feasibility · measurability · demoability)
| Candidate | Idea | I | N | F | M | D | Total |
|---|---|---|---|---|---|---|---|
| **A. AnchorLoRA (chosen)** | Frozen seed-generated A + nested ranks ⇒ exact mixed-rank aggregation; on top: FedNova normalisation, macro weights, median-norm clip, MIFA memory, partial-work acceptance; ΔW-space influence audit | 5 | 3 | 5 | 5 | 5 | **23** |
| B. Product-space aggregation + SVD re-factorisation (FlexLoRA-like) with influence caps | Average ΔW_k = B_k A_k exactly, then truncated SVD to each rank | 4 | 2 | 4 | 5 | 4 | 19 |
| C. Learned aggregation weights (meta-learned / loss-aware q-FFL) | Weights from per-device validation loss | 4 | 3 | 3 | 4 | 3 | 17 |
| D. Async buffered (FedBuff) with staleness discount | Event-driven rounds | 3 | 2 | 3 | 4 | 5 | 17 |
| E. Zeroth-order / seed-based updates for ultra-weak devices (FedKSeed-like) | Devices send seeds + scalars | 3 | 3 | 2 | 4 | 4 | 16 |

## Why A beats the obvious baseline (first principles)
- Exactness: with A fixed, ΔW_k = ΔB_k A is linear in the trained variable, so any weighted average of updates is the update of the weighted average — no cross terms, for any rank mix (proved trivially; unit-tested: `test_anchor_is_exact_for_mixed_ranks`).
- Because the space is exact and linear, *classic* FL theory (FedNova's normalisation, MIFA's memory) applies to LoRA without approximation — which is what makes weak, intermittent devices count.
- Communication: a rank-r_k device uploads r_k·d_out floats per layer (A regenerated from the seed), i.e. 2.5× less than A+B for q_proj/v_proj on SmolLM2-135M (r·768 vs r·1,920 floats per layer pair). Measured over 12 rounds of the dropout scenario with identical participation: anchor_naive 17.7 / 6.6 / 1.8 / 1.7 / 1.1 MB (c0…c4) vs fedavg_ab_het 44.2 / 16.6 / 4.6 / 4.1 / 2.8 MB (`eval/results/v1_summary.md`).
- Cost: frozen A reduces expressiveness (RoLoRA's critique) → mitigations to test in the ratchet: larger r_max for strong devices, periodic A re-draw ("anchor refresh") merged into the base, or RoLoRA-style alternation on strong devices only.

## Ratchet backlog (program.md)
server learning rate / momentum (FedOpt), memory max-age, clip κ, sqrt-n vs uniform weights, q-FFL-style loss-aware weights, anchor refresh every k rounds, per-layer rank allocation.
