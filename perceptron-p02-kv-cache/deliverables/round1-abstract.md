# Round-1 abstract (draft v1, 4 Oct 2026) — Perceptron Hackathon 2026, Theme 1, Problem 2

**Title:** *Recall-on-Demand: making KV-cache eviction safe for long-chat recall*

## Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 2: *Squeezing Long-Context Inference into Less Memory*. A 1-billion-parameter model such as Llama-3.2-1B stores 32 KiB of key/value (KV) cache for every token it has read. At 32k tokens that is 1 GiB, more than its 4-bit weights. Long documents and chat histories therefore hit a memory wall first, and that wall decides whether long-context AI can run on laptops and phones or only in data centres.

## Understanding of the challenge
Shrinking the cache is easy; shrinking it *without forgetting* is the hard part. Eviction methods (StreamingLLM, H2O, SnapKV) must decide which tokens to delete before they know what will be asked, and a deleted token can never be recovered. When the question is known up front, observation-window methods such as SnapKV select the right tokens. In a real chat, though, the 2nd, 3rd and 10th questions target content nobody scored highly at compression time. SCBench reports exactly this: memory-saving methods "suffer in multi-turn scenarios". Quantisation (KIVI, 2-bit) never deletes, but its saving stops at about 4–8×. Keep-everything methods (Quest) recover accuracy but do not reduce the bytes held. The crux is high compression **and** robustness to questions that arrive *after* compression.

## Proposed approach
We treat the KV cache as a *cache*, not a *store*, with three tiers:
1. **Resident tier:** a small compressed KV cache (StreamingLLM sinks + recent window, or SnapKV top-k), optionally 4-bit quantised.
2. **Index tier:** for evicted spans, a 2-bit quantised copy of the keys of a single layer. That is about 160 B/token, or 0.5% of the full cache.
3. **Backing store:** the raw token IDs, at 4 B/token.

When a question arrives, we run it against the resident cache, take its *own* attention queries at the index layer, score the evicted 64-token blocks against the sketch, and **re-prefill** (recompute) only the top blocks at their original positions. The question is then answered over the resident and recalled KV, and the recalled KV is dropped afterwards. Eviction becomes a cache miss that costs a little compute, instead of permanent data loss.

Tools: Apple MLX on an M5 laptop, with our own explicit-cache forward pass over frozen `Llama-3.2-1B-Instruct` weights (a 3B model and Qwen2.5 as second models), and NVIDIA kvpress as a reference implementation of the baselines. The data are RULER-style multi-key needle tasks built from WikiText-103 text, plus LongBench-style QA.

## Minimum Viable mapping
1. *Apply an existing technique and measure memory savings:* StreamingLLM, H2O, SnapKV and 2/4/8-bit KIVI-style quantisation run in one harness. "Memory" counts every retained byte (KV, quantisation scales, indices, sketches, token IDs) plus measured peak memory, against the uncompressed baseline.
2. *Show the accuracy drop on a small long-context recall task:* recall accuracy with 95% Wilson intervals at 2×, 4× and 10× compression, for 4k–16k contexts and needle depths from 5% to 95%.

## Stretch ambitions
- **Modification of an existing method:** Recall-on-Demand on top of StreamingLLM and SnapKV, tuned by an automated keep-only-if-better loop over sketch layer, sketch bit-width, block size and recall budget.
- **Benchmark against 2+ baselines:** StreamingLLM, H2O, SnapKV, K-norm and quantisation; a query-aware SnapKV serves as the upper reference.
- **Stretch beyond the brief:** a live chat demo with a memory meter, and a second model.

## Novelty / differentiation
The obvious entry applies StreamingLLM or H2O and plots a needle chart. We differ in three ways:
1. **No evicted KV is kept anywhere.** Offload methods move it to CPU memory; we keep only token IDs and a 0.5% sketch, and recompute on demand.
2. **Retrieval uses the model's own question-time attention queries,** so it needs no external embedding model.
3. **The evaluation is query-agnostic and multi-question.** We compress once, then ask several questions, compare methods at *equal answer-time bytes*, and count every byte.

We will state precisely how our design relates to the nearest prior work (ArkVale-style page recall, Quest page digests, CacheBlend selective recompute).

## Evaluation plan
- **Main metric:** recall accuracy vs retained bytes (a Pareto curve per method), 4 questions per context, paired across methods, with confidence intervals on held-out seeds.
- **Secondary metrics:** steady-state vs answer-time bytes; measured peak memory; latency per answer including recompute; needle-token retention (scorer) and needle-block hit rate (recall tier).
- **Controls:** full cache (ceiling); query-aware SnapKV (reference); non-literal needles, so a lexical matcher cannot game the task; a held-out split against overfitting.

## Feasibility and risks
**Team.** [names TBD]: (a) systems / inference engineering, (b) ML and attention mechanics, (c) evaluation and the demo. Everything runs on one 24 GB laptop; no paid GPU time.

**Milestones.**
- 6–12 Oct: baseline numbers (MVP).
- 13–19 Oct: Recall-on-Demand v1 and its tuning loop.
- 20–26 Oct: non-literal needles and QA; abstract.
- 27 Oct–9 Nov: second model; 16–32k contexts; latency.
- 10–16 Nov: demo app.
- 17–28 Nov: exams (automated runs only).
- 1 Dec: midway report.

**Risks and mitigations.**
- Recomputed blocks see only local context; we ablate adding neighbour context.
- One sketch layer may miss the needle; we tune it and vote across layers.
- The extra pass adds latency; we report it.
- If close prior art exists, we narrow the novelty claim.
