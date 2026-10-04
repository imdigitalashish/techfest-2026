# Round-1 abstract — Perceptron Hackathon 2026, Theme 1, Problem 2

**Title:** *Recall-on-Demand: treating the KV cache as a cache, so that eviction stops causing forgetting*

## Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 2: *Squeezing Long-Context Inference into Less Memory*. Llama-3.2-1B keeps 32 KiB of key/value (KV) cache per token: a 32k-token chat holds 1 GiB, more than its 4-bit weights. That decides whether long-context assistants fit on laptops and phones.

## Understanding of the challenge
Eviction methods (StreamingLLM, H2O, SnapKV) must choose what to delete **before the question exists**, and a deleted token is gone for good. Later questions target content nobody scored highly; SCBench reports such methods "suffer in multi-turn scenarios". Quantisation never deletes, but its saving is bounded by bit-width. Query-aware selection (Quest) keeps the full cache resident. The crux: high compression **and** robustness to questions that arrive after compression.

## Proposed approach
**Recall-on-Demand (RoD)** turns eviction into a *cache miss*. Per context we keep three tiers:
1. A small **resident** KV cache: StreamingLLM's sinks plus recent tokens.
2. A **key index**: one layer's keys at 4 bits (layer 5, chosen on development data; 288 B/token, 0.88% of the cache) plus the context's last 64 queries (256 KiB).
3. The **token ids** (4 B/token).

A question's *own* layer-5 queries score evicted 64-token blocks against the index. The score is contrastive (question attention minus the context's generic attention), which cancels sink-like tokens. The top blocks are **re-prefilled** from ids at their original positions. This is position-preserving but approximate, since each block sees only the sinks and itself. The model answers, and the recalled KV is dropped.

- **Model:** frozen Llama-3.2-1B-Instruct (Qwen2.5-3B next).
- **Data:** RULER-style needles in WikiText-103 with literal, paraphrased and synonym-aliased keys.
- **Tools:** PyTorch, Apple MLX (demo), NVIDIA kvpress (published baselines).

## Minimum Viable mapping
1. **Existing techniques with measured memory savings:** StreamingLLM, H2O, SnapKV, K-norm and int8/4/2 KV in one harness. Every retained byte after prefill (KV, scales, index, ids) is counted and checked against the retained tensors.
2. **Accuracy drop on a recall task:** each method's paired recall drop vs the full cache, with 95% CIs, at 50%, 25% and 10% memory on 4k-token contexts.

Both run today (results below).

## Stretch ambitions
- **Modify a method:** RoD extends StreamingLLM, with its scorer tuned by a keep-only-if-better loop on development seeds.
- **2+ baselines:** our implementations plus kvpress's StreamingLLM, SnapKV, ObservedAttention (H2O), Knorm, ExpectedAttention and TOVA.
- **Next:** multi-turn chat, KVzip baseline, 16–32k contexts, memory-bounded prefill.

## Novelty / differentiation
Query-scored key indices (Quest, ArkVale) and token recomputation (CacheBlend, HCache) are known. Offload systems (InfiniGen, ShadowKV, ArkVale) keep evicted KV in host memory, which shrinks GPU memory but not the total stored. We test their combination *without* any backing store of evicted KV: ids plus a one-layer index, recomputing only the blocks the live question selects. We also contribute a stricter evaluation:
- Compression happens before any question is seen.
- RoD pays for its index from its own memory budget.
- A lexical-index control, a question-aware oracle and aliased-key splits test whether retrieval is mere word matching.

## Evaluation plan
- **Pre-registered** before running (`eval/PREREG.md`):
  - primary: RoD vs StreamingLLM at 25% memory;
  - non-inferiority vs the full cache (5-point margin);
  - every tested query-agnostic baseline;
  - paraphrased and aliased splits, and a recompute-context ablation.
- **Statistics:** 12 held-out contexts per split, context-clustered bootstrap CIs; scorer tuned only on development seeds (exploratory best of 322).
- **Metrics:** recall, retained bytes, needle-block hit rate, latency.
- **Preliminary results:** <!-- p2:headline:begin -->
On 12 held-out ~4k-token contexts (48 questions; Llama-3.2-1B-Instruct) the full cache recalls 83%. At 25% of the KV memory, ten query-agnostic baselines recall 0%–35% and RoD 58%: +0.40 over StreamingLLM (95% CI +0.25 to +0.54; pre-registered), yet 0.25 below the full cache. At 10% memory RoD recalls 85% (baselines ≤6%); on fresh paraphrased contexts it recalls 69% vs the full cache's 46% (+0.23, 95% CI +0.10 to +0.38), but 12 of the full cache's 26 misses are answers cut off by our 10-token limit.
<!-- p2:headline:end -->
- **Controls:** <!-- p2:caveats:begin -->
RoD minus a lexical index over the same ids at 25%: +0.04 (-0.04 to +0.12) on literal and +0.27 (+0.10 to +0.44) on paraphrased needles; accuracy given a recalled needle falls from 98% (10%) to 55% (25%), mostly naming another needle's value; exact KV for the same blocks gives 90% and recalling only the top-2 blocks 85% (exploratory), so approximately recomputed extra blocks cause the loss; synonym-aliased keys defeat even the full cache (10%), so meaning-based retrieval is untested (RoD's block hit there is 23% vs 73% for lexical); CPU answer time 6.2× StreamingLLM's.
<!-- p2:caveats:end -->

## Feasibility and risks
- **Team:** three students [names to be added]: systems/inference (RoD store, demo), ML (attention scoring, quantisation), evaluation (benchmarks, statistics).
- **Feasibility:** a CPU prototype runs everything today.
- **Milestones:**

  | Weeks | Milestone |
  |---|---|
  | 1–2 | 3B model and QA |
  | 3–4 | Multi-turn chat and 16k contexts |
  | 5–6 | Streamed scorer and GPU latency |
  | 7 | MLX demo |
  | Before exams (19–25 Nov) | Freeze |
  | December | Ablations |
- **Risks and mitigations:**
  - Recomputation adds latency. *Mitigation:* we report it.
  - Re-prefilled KV is approximate. *Mitigation:* an exact-KV oracle and a halo ablation measure the cost.
  - Literal needles flatter retrieval. *Mitigation:* the aliased split and the lexical control.
  - Only 12 test contexts. *Mitigation:* a larger confirmation set for the finals.
