# Round-1 abstract — Perceptron Hackathon 2026, Theme 1, Problem 2

**Title:** *Recall-on-Demand: treating the KV cache as a cache, so that eviction stops causing forgetting*

## Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 2: *Squeezing Long-Context Inference into Less Memory*. Llama-3.2-1B keeps 32 KiB of key/value (KV) cache per token, so a 32k-token chat holds 1 GiB of cache, more than its 4-bit weights. As builders of inference systems, we care because this limit decides whether long-context assistants can run on laptops and phones.

## Understanding of the challenge
Shrinking the cache is easy; shrinking it *without forgetting* is hard. Eviction methods (StreamingLLM, H2O, SnapKV) must choose what to delete **before the question exists**, and a deleted token is gone for good. In a chat, later questions target content nobody scored highly at compression time; SCBench reports such methods "suffer in multi-turn scenarios". Quantisation never deletes, but its saving is bounded by bit-width. Keep-everything selection (Quest) leaves the full cache resident. The crux: high compression **and** robustness to questions that arrive after compression.

## Proposed approach
**Recall-on-Demand (RoD)** turns eviction into a *cache miss*. Per context we keep three tiers:
1. A small **resident** KV cache: StreamingLLM's sinks plus recent tokens.
2. A **sketch**: 4-bit keys of one layer (layer 5, chosen on development data; 288 B/token, 0.88% of the cache) plus the context's last 64 queries (256 KiB).
3. The **token ids** (4 B/token).

When a question arrives, its *own* layer-5 queries score evicted 64-token blocks against the sketch. The score is contrastive: question attention minus the context's generic attention, which cancels sink-like tokens. The top blocks are **re-prefilled** from ids at their original positions, the model answers, and the recalled KV is dropped.

- **Model:** frozen Llama-3.2-1B-Instruct (Qwen2.5-3B next).
- **Data:** RULER-style needles in WikiText-103 with literal, paraphrased and synonym-aliased keys; LongBench QA for breadth.
- **Tools:** PyTorch, Apple MLX for the laptop demo, NVIDIA kvpress for the published baselines.

## Minimum Viable mapping
1. **Existing techniques with measured memory savings:** StreamingLLM, H2O, SnapKV, K-norm and int8/4/2 KV run in one harness. Every stored byte (KV, scales, sketch, ids) is counted analytically and checked against the retained tensors.
2. **Accuracy drop on a recall task:** recall with 95% CIs at 50%, 25% and 10% memory on 4k-token contexts, needles at 5–95% depth.

Both run today (results below).

## Stretch ambitions
- **Modify a method:** RoD extends StreamingLLM, and its scorer is tuned by an automated keep-only-if-better loop on development seeds.
- **2+ baselines:** our implementations plus kvpress's reference StreamingLLM, SnapKV, ObservedAttention (H2O), Knorm, ExpectedAttention and TOVA.
- **Next:** multi-turn cache updates, 16–32k contexts, per-channel quantised sketches, and a live laptop demo with a memory meter.

## Novelty / differentiation
The obvious entry plots StreamingLLM or H2O on a needle test. Offload systems (InfiniGen, ShadowKV; ArkVale per its README) park evicted KV in CPU memory. RoD keeps **no KV** for evicted tokens, only ids and a one-layer sketch, and recomputes exactly the blocks the live question needs. To our knowledge, after checking 19 papers, this combination is unpublished. The evaluation is also stricter than usual:
- Compression happens before any question is seen.
- RoD pays for its sketch from its own memory budget.
- A lexical-index control, a question-aware oracle, and paraphrase/alias splits test whether retrieval is mere word matching.

## Evaluation plan
- **Design:** pre-registered before running (`eval/PREREG.md`). The primary comparison is RoD vs StreamingLLM at 25% memory on 12 held-out contexts (48 questions), with context-clustered bootstrap CIs. Secondary comparisons cover every baseline, the paraphrased and aliased splits, and a recompute-context ablation. Scorer tuning used only development seeds (an exploratory best of 322 variants).
- **Metrics:** recall, stored and answer-time bytes, compression ratio, needle-block hit rate and latency overhead.
- **Preliminary results:** <!-- p2:headline:begin -->
_Measured results pending (pre-registered runs in progress)._
<!-- p2:headline:end -->
- **Controls:** <!-- p2:caveats:begin -->
_Controls pending._
<!-- p2:caveats:end -->

## Feasibility and risks
- **Team:** three students [names to be added]: systems/inference (RoD store, demo), ML (attention scoring, quantisation), evaluation (benchmarks, statistics).
- **Feasibility:** the harness and the pre-registered evaluation already run on a single CPU VM.
- **Milestones:**

  | Weeks | Milestone |
  |---|---|
  | 1–2 | 3B model and QA |
  | 3–4 | Multi-turn protocol and 16k contexts |
  | 5–6 | Cheaper sketches and latency |
  | 7 | MLX demo |
  | Before exams (19–25 Nov) | Freeze |
  | December | Ablations and rehearsal |
- **Risks and mitigations:**
  - Recompute adds latency per question. *Mitigation:* we report it.
  - Re-prefilled blocks see only sinks plus themselves. *Mitigation:* the halo ablation measures the cost.
  - Literal needles flatter retrieval. *Mitigation:* the aliased split and the lexical control.
  - A close prior system may appear. *Mitigation:* we narrow the claim to the store design and the evaluation.
