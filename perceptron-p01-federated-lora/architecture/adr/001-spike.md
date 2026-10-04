# ADR 001: Spike choice — the aggregator ("AnchorLoRA")

- **Status:** accepted (first version, 4 Oct 2026 07:10 IST); revisit at the 12 Oct selection gate.
- **Deciders:** project lead. Antithesis by an independent `rubber-duck` agent (verbatim points summarised below). The planned First Principles agent and research agents failed on network timeouts, so first principles are lead-written.

## Context
Problem 1 asks that (a) weak devices meaningfully contribute, (b) training stays stable when devices drop out mid-run, and (c) a data-rich device can't quietly dominate. The starter baseline is PEFT LoRA + Flower FedAvg. All three properties are decided where updates are combined, so the **aggregator (C6)** carries the most judging weight (understanding, soundness, innovation, evaluation = 80%). Other components stay best-practice (`architecture/components.md`).

## Options (scored in `research/components/aggregator.md`)
A. **AnchorLoRA** (23/25) · B. exact product-space + SVD with caps (19) · C. learned/loss-aware weights (17) · D. async buffered aggregation (17) · E. seed-based zeroth-order updates (16).

## First principles (lead)
1. LoRA's update ΔW = BA is bilinear. Averaging factors averages the wrong object. With A fixed and shared, ΔW = ΔB·A is **linear** in the trained variable, so every linear FL tool (weighted averaging, FedNova normalisation, MIFA memory, clipping) becomes exact for LoRA. The idea's value is that it turns FL theory back on for LoRA.
2. Nested ranks under a shared A cost nothing to aggregate. A rank-2 device trains 2 columns of B and uploads 2·d_out floats per layer; nothing is padded or diluted in the averaging.
3. "Dominance" is an objective choice. n_k weights optimise the pooled-sample loss (micro), uniform weights optimise the per-device loss (macro). The brief asks that no device dominate, so the macro objective is the principled target, and we report the micro loss too so the trade-off is visible.
4. Dropout is a bias problem before it is a variance problem. Devices that disappear shift the effective objective toward always-on devices. Memory of absent devices and acceptance of partial work restore their weight; the cost is staleness.

## Six Thinking Hats
- **White (facts, tonight's runs, seed 0, 12 rounds):** FedAvg over A and B has a 5.5–36.2% aggregation error, the data-rich device's influence share is 1.02–1.25, and **weak devices' domains end worse than the base model** (weak gain −0.06 to −0.13 nats). Exactness alone (anchor_naive, n_k weights) is *worse*: macro 2.762, c0 share 1.00. **anchor_full** (dropout scenario): macro **2.665** vs 2.735 starter / 2.705 HetLoRA-style / 2.706 untuned; every domain improves; c0 share 0.20; aggregation error 0.000; no loss rise between evaluations. Trade-off: the data-rich wiki domain improves less (3.515 vs 3.265). Full table: `eval/results/v1_summary.md`.
- **Red (gut, judges):** "Exact for any rank mix, in one line of algebra" plus a live dominance meter is memorable and easy to explain to Optiver engineers.
- **Black (risks):** frozen A limits expressiveness (RoLoRA, NeurIPS 2025, argues for trainable A); each ingredient is published (FFA-LoRA, FedNova, MIFA), so novelty sits in the integration; 12-round single-seed evidence is thin; the local-text domains are a proxy.
- **Yellow (benefits):** exactness, ~2–8× less upload than FedAvg on A and B, devices of any rank, no extra server memory beyond B, auditability.
- **Green (alternatives):** anchor refresh (periodically merge ΔW into the base and redraw A); rotating rank masks; RoLoRA-style alternation on strong devices only; loss-aware (q-FFL) weights; FedBuff-style async for the demo.
- **Blue (process):** keep A as the spike, run the ablation ladder and the antithesis experiments below, and ratchet on the dropout scenario with a frozen evaluator.

## Thesis → antithesis → synthesis
**Thesis.** AnchorLoRA (frozen shared A, nested ranks, FedNova normalisation, macro weights, median-norm clip, memory, partial work) makes weak devices count, survives dropouts, and stops quiet domination. Every round is audited.

**Antithesis (independent rubber-duck, 07:05 IST; abridged):**
1. *Confounded design:* hardware class, rank, steps, data volume and domain move together, so the macro gain might come from uniform weighting alone. Simulation also says nothing about RAM, energy or deadlines.
2. *Straw-man baseline:* FedAvg over A and B is known to be invalid, so a 9–25% aggregation error "does not validate your method". Compare against exact product-space aggregation + SVD, zero-padded LoRA, fixed A without extras, and per-mechanism ablations.
3. *Normalisation risk:* scaling a 1-step partial update by the *planned* mean steps "pretends that an early noisy gradient completed several steps".
4. *Structural ownership:* with prefix ranks only high-rank devices touch columns > r_k, and a frozen random A confines updates to a fixed input subspace.
5. *Stale replay* counts one computation several times at an obsolete model; "MIFA-style" doesn't inherit MIFA's guarantees.
6. *Median clipping* with five clients is brittle.
7. *Metric:* s_k > 1 just means other shares are negative, shares blow up when updates cancel, and uniform weights are Sybil-sensitive.

**Synthesis (what changes):**
| Objection | Decision |
|---|---|
| 1 | Add a **Latin-square rotation** (each domain on each device budget across runs), an IID control, ≥ 5 seeds, and longer runs (≥ 50 rounds on Azure GPU). Log peak RAM and tokens/s per device class. Physical-device runs are a stretch goal (an M-series Mac + a phone/Pi via Flower). |
| 2 | Baselines become: FedAvg(A,B) [starter] · **anchor_naive = FFA-LoRA-style** · **exact ΔW averaging + truncated SVD (FlexLoRA-style)** · FedEx-LoRA · RoLoRA. Plus an ablation ladder that toggles each anchor mechanism. Tonight only the first two run. |
| 3 | Ratchet item #1: τ_eff from **actual** vs **planned** steps vs none. Measure update variance and cosine to a fresh full-step update. |
| 4 | Ratchet items: rotating rank masks; an A-seed sweep (≥ 5 seeds); anchor refresh every k rounds. |
| 5 | Ratchet items: decayed replay (weight × γ^age) vs renormalisation over active devices. Report post-rejoin spikes and credited vs actual work. |
| 6 | Keep κ·median only with ≥ 5 reporters; otherwise clip to a running median. Compare with ΔW-space clipping. |
| 7 | Primary dominance ground truth = **leave-one-device-out marginal loss**. s_k is reported together with ‖P‖ (conditioning) and a bounded norm share ‖c_k‖/Σ_j‖c_j‖. Add a **Sybil test** (rich device split into two identities) and report sqrt-n weights as the Sybil-robust middle ground. |

## Decision
Spike = **C6 aggregator (AnchorLoRA)**, with the claim scoped to: *exact rank-heterogeneous aggregation as the substrate that makes step normalisation, device memory and macro weighting exact for LoRA, evaluated with an influence audit and a leave-one-out ground truth.* Second spike candidate (if capacity allows after the midway check): C8 contribution accountant with online influence caps.

## Consequences
- The frozen evaluator (`components/aggregator/autoresearch/eval.py`) uses the dropout scenario and the macro loss. Contract tests guard exactness.
- The abstract must not claim the frozen-A/nested-rank trick as novel (prior-art search inconclusive, see `research/landscape.md` §2). It claims the integration and the evaluation.
