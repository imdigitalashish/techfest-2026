# Prior-art check: Recall-on-Demand (RoD) KV-cache compression

> **Lead correction (2026-10-04 15:38 IST).** This report was written before the RoD design was frozen.
> - The frozen design uses a **4-bit** sketch of **layer 5**, chosen on dev seeds, not "arbitrarily". It costs 288 B/token plus 256 KiB of window queries.
> - Absolute "first" and "zero resident bytes" phrasing is withdrawn: the sketch is KV-derived retained state.
> - ArkVale's mechanism (CPU backup pages, bounding-volume key digests, importance scoring and recall) has since been **verified** from its official NeurIPS abstract by the gpt-6-astra review (`../../reviews/2026-10-04-spike-prereg-gpt-6-astra.md`).
> - Defensible claim: *token-backed selective recomputation, where a single-layer 4-bit key index chooses blocks whose approximate multilayer KV is rebuilt at original positions, without a backing store of evicted KV*. Its constituents are prior art.


All sources opened 2026-10-04 (arXiv API `export.arxiv.org/api/query`, arXiv abstract pages, or GitHub READMEs). OpenReview's HTML and API both returned a bot-verification challenge on every attempt and could not be opened; ArkVale's digest mechanism, relayed below via a search snippet quoting its OpenReview abstract, is marked **UNVERIFIED** on that basis — its title/venue/framing are confirmed separately via its opened GitHub README.

## Comparison table

(1) = keeps evicted KV *somewhere* (any device/precision) vs. none. (2) = uses the live question's own attention-query vectors to pick recall targets. (3) = recovers evicted KV by **recomputing** from raw token IDs (vs. fetching/reconstructing stored data).

| Paper | URL [opened] | Mechanism | (1) | (2) | (3) |
|---|---|---|---|---|---|
| ArkVale, NeurIPS'24 | github.com/pku-liang/ArkVale; abstract **UNVERIFIED** | Page "digests" (bounding-volume of keys) recall evicted pages from a CPU backup copy | Yes (CPU) | Yes | No — fetches |
| InfiniGen, OSDI'24 | arxiv.org/abs/2406.19707 | Next-layer query-weight "rehearsal" predicts & prefetches important KV from host | Yes (host) | Yes | No — fetches |
| OmniKV, ICLR'25 | github.com/antgroup/OmniKV | "Filter" layers pick tokens via attention sparsity; **all** KV retained, nothing evicted | Yes (all) | Partial | No |
| RetroInfer, VLDB'26 | arxiv.org/abs/2505.02922 | Attention-aware vector index over CPU-resident KV + GPU/CPU buffer | Yes (CPU) | Yes | No |
| Quest, ICML'24 | arxiv.org/abs/2406.10774 | Per-page min/max key proxy scored by the **query vector**; loads top-k pages | Yes | Yes | No — loads real pages |
| ShadowKV, 2024 | arxiv.org/abs/2410.21465 | Low-rank keys on GPU + offloaded values; "reconstructs...sparse KV on-the-fly" | Yes | Yes | No — reconstructs, not token-level recompute |
| MagicPIG, 2024 | arxiv.org/abs/2410.16179 | LSH hash tables; attention computed on CPU over sampled KV | Yes (CPU) | Yes | No |
| RetrievalAttention, 2024 | arxiv.org/abs/2409.10516 | ANNS vector index over CPU KV, retrieved via search | Yes (CPU) | Yes | No |
| CacheBlend, EuroSys'25 | arxiv.org/abs/2405.16444 | RAG chunk-fusion: recomputes KV for a small token subset to fix cross-attention | Chunks stored | Attention-deviation across chunks, not live query | **Yes** — only listed paper that truly recomputes from tokens (for RAG correctness, not GPU-memory eviction) |
| HCache, EuroSys'25 | arxiv.org/abs/2410.05004 | Restores from saved **intermediate activations**; names "recompute from original tokens" as a known, costly, pre-existing baseline | Partial (activations) | No | No — deliberately avoids it |
| ReadAgent | arxiv.org/abs/2402.09727 | Prompt-level: "gist memories" + on-demand lookup of raw passages | N/A (plain text) | Yes (LLM decides) | ~Yes, but a fresh whole-passage forward pass at a *new* prompt position, not a scoped original-position re-prefill |
| SpeCache, 2025 | arxiv.org/abs/2503.16163 | Offloads full KV to CPU; a **low-bit VRAM copy** drives speculative prefetch | Yes (CPU, full-precision) | Yes | No — fetches real CPU KV |
| LaCache, ICML'25 | arxiv.org/abs/2507.14204 | Ladder-shaped cross-layer KV layout + iterative compaction of older KV | Yes (compacted) | No (distance-based) | No |
| "Recycled Attention"→RefreshKV | arxiv.org/abs/2411.05787 [v2 retitled] | Alternates full/partial attention; periodically refreshes small cache from a full-attention pass | Ambiguous (needs full attn.) | No (schedule-based) | Partial — whole-sequence periodic, not targeted on-demand |
| FreeKV, 2025–26 | arxiv.org/abs/2505.13109 | Speculative retrieval off critical path + hybrid CPU/GPU layout + streamed recall | Yes | Yes | No |
| ClusterKV, 2024–25 | arxiv.org/abs/2412.03213 | Recalls evicted tokens at semantic-cluster, not page, granularity | Yes | Yes (implied) | No |
| KVP / "Learning to Evict", ICML'26 | arxiv.org/abs/2602.10238 | Per-head RL agents rank tokens by predicted future utility | **No** — permanent deletion, no recall path | Decode-state-driven | No |
| On-Demand Attention (ODA), 2026 | arxiv.org/abs/2609.20734 | Learned "recall head" gates global vs. local attention per step; explicitly **retains the complete historical KV cache** always | **Yes, always** | Yes | No — "recall" means re-scoping attention for the live step, not regenerating missing KV |
| "Spend Bits Where Queries Look" / NOVA-KV, 2026 | arxiv.org/abs/2608.04074 | Attention-distortion-optimal 2-bit/element quantizer for the **entire** resident KV cache | Yes (all, 2-bit) | Optimization criterion is attention-aware, not live per-query | No |

## Published vs. new

**Already published, reusable:** (a) query-aware scoring of a compact proxy to pick recall targets — Quest's min/max proxy, ArkVale's digest, SpeCache's low-bit VRAM copy; (b) offload-then-fetch as the dominant recall mechanism — ArkVale, InfiniGen, RetroInfer, ShadowKV, MagicPIG, RetrievalAttention, SpeCache, FreeKV, ClusterKV all retain real (if compressed/offloaded) KV; (c) recomputing real KV from original tokens for a selected subset — CacheBlend does this for RAG-chunk correctness, and HCache's own abstract names "recompute from original tokens" as a known, pre-existing (if costly) baseline it is explicitly positioned against; (d) attention-aware 2-bit KV vector quantization — NOVA-KV, applied to the whole cache; (e) a learned gate deciding when to pay for wider attention scope — ODA, which reuses "recall" language but never evicts anything.

**Not found in any of the 19 sources:** the combination of (i) **zero** resident bytes for evicted tokens — not even offloaded/compressed KV — versus every offload/compress paper above, which all keep a real KV footprint; (ii) a **single, arbitrarily-chosen transformer layer's** 2-bit-quantized keys (~0.5% of KV bytes) as a cross-layer sketch, scored against the live question's own query vectors at that one layer, to pick blocks for revival — existing proxies are used to decide what to *fetch*, never to license deleting KV outright and regenerating it later; (iii) recovery via a **position-faithful, sinks-only-scoped re-prefill** of just the selected 64-token blocks, distinct from ReadAgent's fresh whole-passage forward pass or CacheBlend's unscoped subset recompute.

## Defensible novelty claim

"RoD is, to our knowledge, the first KV-cache recall scheme that retains **no** KV footprint for evicted tokens — only raw token IDs plus a single-layer 2-bit key sketch (~0.5% of KV bytes) — and restores accuracy by **re-prefilling**, rather than fetching, exactly the blocks that sketch (scored against the live query) flags as relevant, using a sinks-only attention scope at their original positions."

## Gaps and uncertainties

- OpenReview (HTML + API) was bot-blocked throughout; ArkVale's digest/bounding-volume detail is relayed, not directly verified.
- Not opened: ArkVale's/ODA's/NOVA-KV's full PDFs (abstract-only, per instructions on congestion/PDF size); OpenReview-hosted abstracts for SinkQ and the "Learning to Evict" mirror.
- No targeted non-arXiv venue search (ACM DL, USENIX) was performed; a match there can't be ruled out.
- Exact phrases "lookahead recall" (0 arXiv hits) and "evict then recompute" (2 tangential systems hits: Spexis, Vosti) found no terminological match for RoD.
- SpeCache's abstract doesn't state whether its low-bit VRAM copy spans all layers or one — central to judging how novel RoD's single-layer sketch is — and is **UNVERIFIED** without its method section.
