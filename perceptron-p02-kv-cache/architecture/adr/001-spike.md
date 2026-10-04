# ADR 001 — Spike choice: Recall-on-Demand (C7), with the scorer (C3) as secondary

- **Status:** accepted (v1, 2026-10-04 08:20 IST). Revisit at the 12 Oct selection gate with measured numbers.
- **Deciders:** project lead. Lean mode was on, so there were no sub-agents. The antithesis below is self-adversarial; an independent `rubber-duck` review is scheduled after 08:30 IST.

## Context
- **The brief asks to shrink the cache "while barely hurting the model's ability to recall earlier content"** ([brief](../../../_briefs/perceptron.txt)). Its stretch goal is a modification of an existing method plus ≥ 2 baselines.
- **The bytes [OPENED: configs].** Llama-3.2-1B keeps 32 KiB of fp16 KV per token. The same token's ID is 4 B.
- **Multi-turn evidence [OPENED: abstract].** SCBench (2412.10319): "sub-O(n) memory methods suffer in multi-turn scenarios". Every eviction method decides what to forget *before* later questions exist.
- **Production [OPENED: docs + worker report].**
  - Providers cut KV with GQA/MLA/sliding windows, FP8/int8 quantisation, and lossless prefix reuse with paging and offload.
  - Lossy eviction ships only in research tooling (kvpress).
  - Cache-hit economics are explicit: Anthropic cache reads cost "the standard 0.1x multiplier".

## Candidates (score 1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasibility by Dec | Measurable (scalar) | Demoable | Total |
|---|---|---|---|---|---|---|
| **A. C7 Recall-on-demand (RoD):** resident StreamingLLM/SnapKV cache; evicted spans keep token IDs + a 2-bit key sketch of one layer; at question time the question's queries pick blocks to re-prefill | 5 | 4 (prior-art check pending) | 4 | 5 (needle-block hit rate@m; recall at equal answer-time bytes) | 5 | **23** |
| B. C3 query-agnostic scorer (sketch-attention / learned probe) | 3 | 2 (Expected Attention, KVzip, Q-Filters exist) | 5 | 5 (needle retention@budget) | 3 | 18 |
| C. C6 demote-not-delete (2-bit for low-score tokens) | 3 | 2 (MiKV 2402.18096 [OPENED] covers importance-aware mixed precision) | 5 | 5 | 3 | 18 |
| D. C4 per-head budgets (DuoAttention / Ada-KV style) | 3 | 2 | 4 | 4 | 2 | 15 |
| E. Learned eviction retrofit (DMS-style) | 4 | 2 (DMS: "1K training steps to achieve 8× compression" [OPENED]) | 2 (needs training GPUs) | 4 | 3 | 15 |

## Six Thinking Hats (candidate A)
- **White (facts).**
  - Sketch cost = 8 KV heads × (64 dims × 2 bits / 8 + 4 B scale/bias) = 160 B/token, which is 0.49% of 32 KiB.
  - Token IDs cost 4 B/token.
  - Re-prefilling m blocks of 64 tokens costs m × 64 tokens of forward compute, against T for the full prefill (e.g. 192 vs 4096).
  - A 7-digit answer carries about 23 bits. Recall is a *locate* problem, not a *store* problem.
- **Red (gut).** "Eviction becomes a cache miss" is a systems story that Optiver-style judges get instantly. The live demo, where StreamingLLM forgets and RoD remembers, is visceral.
- **Black (risks).**
  1. A recomputed block attends only to sinks plus itself, not to its true prefix. Its KV is approximate, which can hurt answers that need cross-block context.
  2. One sketch layer may not localise the needle; retrieval heads may sit in other layers.
  3. Two passes per question add latency.
  4. Novelty: close relatives may exist. ArkVale-style page recall (UNVERIFIED) keeps the evicted KV offloaded; Quest tracks per-page min/max keys and loads Top-K pages (2406.10774 [OPENED]); CacheBlend reuses precomputed KV of non-prefix chunks (2405.16444 [OPENED]; its recompute details UNVERIFIED).
  5. NIAH needles are lexically distinctive, so this is easy mode for any retriever.
  6. The sketch is still O(T) bytes (0.5%): sub-linear in practice, but not constant.
- **Yellow (benefits).**
  - Robust to questions that arrive after compression, which is the chat-history case.
  - Composes with any resident policy, including quantisation.
  - Training-free, with clean byte accounting.
  - Steady-state footprint is the resident cache only.
- **Green (alternatives).**
  - Multi-layer sketch voting; a PCA-projected sketch (16 of 64 dims).
  - Re-prefill with neighbour context; recall at decode time too.
  - Adaptive recall (stop when retrieval confidence is high).
  - A 4-bit resident cache plus RoD.
- **Blue (process).** Choose A as the primary spike, with B folded into A's ratchet (sketch layer, scorer). Gates for 12 Oct:
  - (i) Needle-block hit rate@m ≥ 0.8 at 10% resident on 4k contexts.
  - (ii) RoD recall ≥ SnapKV-agnostic recall *at equal answer-time bytes*.
  - (iii) Prior-art check clear, or the novelty claim narrowed.
  - If (i) or (ii) fails, fall back to C (demote-not-delete), which is safe but incremental.

## Thesis → antithesis → synthesis
- **Thesis.** Eviction hurts recall because importance is predicted before the question exists. RoD defers the decision to question time for about 0.5% extra memory. It fixes the failure at its root instead of predicting better.
- **Antithesis (self-adversarial).** "This is RAG over your own context with extra steps. Quest and ArkVale already keep everything and pick pages per query. Recomputing a block in isolation gives the *wrong* KV. Latency doubles. And an O(T) sketch is an index, not compression."
- **Synthesis.** Present RoD honestly as a **tiered cache** and make only claims that can be measured:
  1. At **equal answer-time bytes**, RoD beats query-agnostic eviction (StreamingLLM, H2O, SnapKV, K-norm) on multi-question recall, with roughly half the steady-state bytes.
  2. Report the extra latency per question.
  3. Count sketch and ID bytes.
  4. Compare with a keep-everything, select-per-query upper bound (the full cache / `snapkv_qa`) to show how much of its accuracy we retain at a fraction of its memory.
  5. Ablate isolated vs neighbour-context recompute to quantify the approximate-KV error.
  6. Novelty claims are limited to: (a) no evicted KV kept anywhere, only IDs plus a 2-bit single-layer sketch; (b) re-prefill at original positions, driven by the model's own question queries; (c) the paired multi-question, every-byte-counted protocol.

## First principles
The bottleneck is not bytes as such but the *irreversibility of eviction under uncertainty about future queries*. The answer is tiny; *finding* it needs an index. The cheapest faithful backing store is the token stream. Recomputation trades plentiful on-chip compute for scarce memory, which is the right trade for memory-bound long-context decoding.

## Decision
Build **C7 Recall-on-Demand** as spike A on top of a StreamingLLM resident cache, with SnapKV as the second resident policy. Run an autoresearch ratchet on C7: sketch layer, sketch bits, block size, and recall/resident split. The scalar is needle-block hit rate@m on a calibration split, confirmed by recall on a held-out split. Every other component stays best-practice.

## Consequences
- The harness already contains `rod_answer` (`eval/kvbench.py`).
- Next:
  1. Measure (after 08:30).
  2. Add a held-out seed split.
  3. Add non-literal needles (NoLiMa-style) to defuse the lexical-match objection.
  4. Run the prior-art pass.
  5. Add a latency table.

## Update v2 (2026-10-04 15:25 IST): what changed after the first measurements
- **Backend.**
  - MLX's Linux CPU backend measured 3.5 GFLOP/s on an fp32 GEMM on the Azure VM; PyTorch reached 599 GFLOP/s there. All measured numbers therefore come from a PyTorch twin of the harness, [`eval/kvbench_torch.py`](../../eval/kvbench_torch.py), running the *same* weights (the MLX 4-bit model, dequantised).
  - Parity: engine vs HF reference, max |Δlogit| 2e-5 with fp32 KV and 0.011 with fp16 KV; MLX vs torch 5e-5 ([`eval/results/parity_torch.json`](../../eval/results/parity_torch.json)). The MLX harness stays as the Apple-silicon demo path.
- **The a-priori RoD scorer failed.** A 2-bit sketch at layer 8, scored by softmax-sum, reached needle-block hit@3 of only 0.24 on dev seeds: block 0 (system prompt plus instruction) soaked up the attention.
- **Dev sweep** (seeds 100–109, 322 variants; [`results.tsv`](../../components/recall_on_demand/autoresearch/results.tsv)) chose:
  - **Scorer `softmax_lift`:** the question's attention distribution over the evicted keys *minus* that of the context's last 64 tokens. This cancels keys that every query attends to, such as sinks and formatting tokens.
  - Content question tokens only; **4-bit sketch at layer 5**.
  - Result: hit@3 = 0.95 (best of 322; exploratory, so optimistically biased). The lexical IDF control reached 0.91. Layer 5 dominates (the next-best layer reaches 0.69); 2-bit sketches top out at 0.60.
- **Cost of the final store per token:** 288 B sketch + 4 B id (0.89% of 32 KiB), plus 256 KiB of window queries per context. All of it is charged to RoD's own KV budget.
- **Confirmation.** The choice is frozen in [`eval/PREREG.md`](../../eval/PREREG.md), committed 15:14 IST before any test run. Test splits:
  - T1: literal needles, seed 0.
  - T2: paraphrased templates, seed 1.
  - T3: synonym-aliased keys, seed 2 (amendment 1, 15:18).
  - S4: halo ablation.

  Baselines include NVIDIA kvpress's reference presses (StreamingLLM, SnapKV, ObservedAttention, Knorm, ExpectedAttention, TOVA), run on CPU.
- **Novelty claim, narrowed** (prior-art report, `research/components/recall-on-demand-prior-art.md`): to our knowledge, no published KV-recall scheme keeps *no* KV for evicted tokens, only token ids plus a single-layer low-bit key sketch, and recovers by position-faithful re-prefill of the blocks the live question selects. ArkVale's digest mechanism remains UNVERIFIED.

## Corrections (2026-10-04 15:38 IST, from the gpt-6-astra phase-1 review; earlier text kept as written)
- **v1 Black hat item 6.** "Sub-linear in practice" is wrong. The index is **linear** in T with a small coefficient (288 B/token at 4 bits plus 4 B/token of ids), plus a constant 256 KiB of window queries.
- **v1 Yellow hat.** "Steady-state footprint is the resident cache only" is wrong. The steady state is resident KV **plus** the index, ids and window queries, and the harness counts all of them.
- **v2 dev numbers.** These are qualified by the sweep's simplified budget: 2-bit sketch cost, no window-query cost, m = 3 at keep 0.10. Under that budget:
  - "next-best layer 0.69" refers to `softmax_lift`/content/4-bit; the best other configuration is `max_logit`/all/4-bit/layer 1 at 0.70;
  - the best 2-bit variant reaches 0.60 at keep 0.10 and 0.84 at keep 0.25.
- **v2 heading.** It says 15:25, but its commit `75d1152` is at 15:20 IST.
- **Wording.** Re-prefill is **position-preserving but approximate**, not "position-faithful". The novelty is the narrow combination stated in the abstract, not "first" or "zero footprint".

