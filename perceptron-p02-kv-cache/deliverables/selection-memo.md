# Selection memo: Perceptron P2 (KV-cache compression), v2

*Scores are rendered from committed results by `eval/render_docs.py` using rules fixed before the T2/T3 outcomes were seen:*
- *Winnability is 4 only if the pre-registered primary passed **and** the 10%-memory observation replicated on fresh contexts (R1); 3 if only the primary passed; else 2.*
- *Innovation is 4 if the sketch beats the lexical index at 10% memory (lower CI bound > 0); else 3.*
- *Demo is 4 if R1 replicated; else 3.*

The brief allows a team to submit only **one of Problem 1 or Problem 2**; this memo states the case for and against P2 honestly against P1.

<!-- p2:memo-scores:begin -->
| Criterion | Score | Evidence |
|---|---|---|
| **Winnability** | 4 | Pre-registered primary passed: RoD − StreamingLLM +0.40 (95% CI +0.25 to +0.54) at 25% memory, and RoD beats all nine tested query-agnostic baselines there, including NVIDIA kvpress's reference presses. Non-inferiority vs the full cache at 25% was not shown. The 10% observation replicated on fresh contexts (R1), though T2's full-cache ceiling is depressed by a 10-token answer limit (amendment 5). |
| **Innovation headroom** | 4 | A narrow but real combination: token-backed selective recomputation guided by a single-layer 4-bit key index with a contrastive scorer. Its constituents are prior art (hostile judge: 3/5). At 10% memory the sketch beats a lexical index over the same ids by +0.42 (95% CI +0.31 to +0.52). With synonym-aliased keys (too hard even for the full cache) its block hit is 23% vs 73% for lexical, so meaning-based retrieval is not shown. Headroom: precision-first recall, a streamed scorer, per-channel sketches, multi-turn. |
| **Feasibility** | 4 | The whole pre-registered evaluation runs end to end on one CPU VM, with logit parity, identity checks, reference baselines and reviews. The Apple-silicon (MLX) demo path is not yet validated; CPU answer time is 6.2× StreamingLLM's at 25% memory. The 19–25 Nov exams are left free. |
| **Demo strength** | 4 | Live: a 1B model answers questions about a long document holding 10% of its KV. RoD 85% vs ≤6% for every tested eviction baseline (full cache 83%), with a memory meter. Synthetic needles are less visual than a real chat. |
| **Fit with the user** | 5 | Inference systems: cache hierarchy, recompute vs memory trade-off, kernels. This is core Microsoft-style systems work. |

**Overall: 4.2 / 5**, the unweighted mean (4 + 4 + 4 + 4 + 5 = 21).
<!-- p2:memo-scores:end -->

## Pre-registered results (rendered)
<!-- p2:verdicts:begin -->
- **Primary** (RoD − StreamingLLM, keep 0.25, T1): +0.396 (95% CI +0.25 to +0.54, 12 contexts) → **SUCCESS** (lower bound > 0)
- **S7** (RoD − full cache, keep 0.1, T1) (descriptive): +0.021 (95% CI -0.15 to +0.19, 12 contexts)
- **S7** (RoD − full cache, keep 0.25, T1) (confirmatory, margin −0.05): -0.250 (95% CI -0.42 to -0.08, 12 contexts) → non-inferiority **not shown**
- **S7** (RoD − full cache, keep 0.5, T1) (descriptive): -0.229 (95% CI -0.40 to -0.06, 12 contexts)
- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): beats **all** 9 baselines; weakest margin kvpress TOVA +0.229 (95% CI +0.04 to +0.40, 12 contexts)
- **S2** (RoD − RoD-lexical, keep 0.25, T1 literal): +0.042 (95% CI -0.04 to +0.12, 12 contexts) → no evidence the sketch beats lexical retrieval
- **S2** (RoD − RoD-lexical, keep 0.25, T2 paraphrase): +0.271 (95% CI +0.10 to +0.44, 12 contexts) → sketch beats lexical
- **R1** (replication on T2: RoD − full at keep 0.10, margin −0.15): +0.229 (95% CI +0.10 to +0.38, 12 contexts) → **replicated** (lower bound > −0.15)
- **R1 caveat (amendment 5):** of the full cache's 26 wrong T2 answers, 17 contain no 7-digit number (12 cut off by the 10-token limit); RoD at 0.10: 9 of 15 (4 cut off). 'RoD exceeds full on T2' is confounded by answer truncation.
- **E6 (exploratory, T2, max_new=32; lenient / strict first-number):** full@1.0 0.667 / 0.667; rod@0.1 0.750 / 0.750; rod@0.25 0.604 / 0.604; snapkv_qa@0.25 0.729 / 0.729; streaming@0.1 0.021 / 0.021; streaming@0.25 0.208 / 0.208
- **R2 mechanism T1** (RoD): keep 0.1: block hit 0.88, accuracy given hit 0.98, 4/7 wrong answers name another needle's value; keep 0.25: block hit 1.00, accuracy given hit 0.55, 16/20 wrong answers name another needle's value; keep 0.5: block hit 1.00, accuracy given hit 0.53, 10/19 wrong answers name another needle's value
- **R2 mechanism T2** (RoD): keep 0.1: block hit 0.85, accuracy given hit 0.82, 0/15 wrong answers name another needle's value; keep 0.25: block hit 0.93, accuracy given hit 0.59, 10/20 wrong answers name another needle's value; keep 0.5: block hit 1.00, accuracy given hit 0.35, 15/26 wrong answers name another needle's value
- **S3** (primary replicated on T2 paraphrase): +0.375 (95% CI +0.23 to +0.54, 12 contexts) → replicated
- **S4** (halo 64 − halo 0, RoD, keep 0.1, T1): +0.000 (95% CI +0.00 to +0.00, 12 contexts)
- **S4** (halo 64 − halo 0, RoD, keep 0.25, T1): -0.083 (95% CI -0.17 to +0.00, 12 contexts)
- **S4** (halo 64 − halo 0, RoD, keep 0.5, T1): -0.062 (95% CI -0.17 to +0.04, 12 contexts)
- **S5** (RoD − baseline, keep 0.1, T1): StreamingLLM (ours) +0.833 (95% CI +0.71 to +0.94, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.854 (95% CI +0.73 to +0.96, 12 contexts); H2O-style (ours) +0.854 (95% CI +0.73 to +0.96, 12 contexts); RoD-lexical (control) +0.417 (95% CI +0.31 to +0.52, 12 contexts); kvpress ExpectedAttention +0.854 (95% CI +0.73 to +0.96, 12 contexts)
- **S5** (RoD − baseline, keep 0.5, T1): StreamingLLM (ours) +0.167 (95% CI +0.02 to +0.31, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.375 (95% CI +0.21 to +0.56, 12 contexts); H2O-style (ours) +0.333 (95% CI +0.15 to +0.50, 12 contexts); RoD-lexical (control) +0.000 (95% CI -0.08 to +0.08, 12 contexts); kvpress ExpectedAttention not run
- **Byte check T1**: RoD answer-time bytes > a baseline's stored bytes in 0 of 36 (context, keep) cells
- **Byte check T2**: RoD answer-time bytes > a baseline's stored bytes in 0 of 36 (context, keep) cells
- **Byte check T3**: RoD answer-time bytes > a baseline's stored bytes in 0 of 24 (context, keep) cells
- **S4 pairing**: 12 contexts; context lengths identical to T1's: yes
- **S6** (RoD − RoD-lexical, keep 0.1, T3 synonym-aliased keys; confirmatory): +0.062 (95% CI -0.02 to +0.15, 12 contexts) → not shown
- **S6** (RoD − RoD-lexical, keep 0.25, T3 synonym-aliased keys; exploratory): -0.021 (95% CI -0.15 to +0.08, 12 contexts)
- **T3 ceiling** (full cache): recall 0.104 (< 0.5: T3 too hard; S6 inconclusive)
<!-- p2:verdicts:end -->

## Biggest risks
1. **Not near-lossless at the pre-registered budget.** At 25% memory RoD loses about a quarter of the full cache's recall. The mechanism is key–value confusion when several needle-like blocks are recalled as approximate KV; E2 and E5 test whether exact KV or precision-first recall fix it.
2. **Small, synthetic evidence.** 12 contexts per split, synthetic needles and a 1B model. A larger confirmation set, a QA benchmark and a 3B model are planned.
3. **CPU-only prototype.** Memory claims are post-prefill retained state. The prefill still builds the full KV first, and GPU latency is untested.
4. **Novelty is a narrow combination**, with strong neighbours (Quest, ArkVale, InfiniGen, ShadowKV, CacheBlend, HCache, KVzip).

## P2 vs P1 (facts from P1's memo on `main`; the ranking is the Supervisor's call)
- **P1** (federated LoRA, overall 4.2/5):
  - its spike *replicated* across 5 paired seeds with bit-identical reruns;
  - every one of its 5 domains improved (Bonferroni);
  - it is cross-model reviewed (code 13/14, abstract 12/12 accepted);
  - but it is a systems recipe with close prior art (innovation 3/5).
- **P2** has:
  - a pre-registered primary that passed with a large effect, plus wins over NVIDIA's own reference implementations;
  - a dramatic 10%-memory result whose status is given by R1 above;
  - the more visual demo.

  But its evidence base is smaller: one pre-registered split per question and 12 contexts. It also failed non-inferiority at its registered budget.
- **Lead's recommendation:**
  - If R1 replicated: P2 matches P1 on winnability and beats it on demo and innovation headroom, while P1 has the more mature evidence. That is a close call.
  - If R1 did not replicate: **P1**.

## One-line pitch
<!-- p2:memo-pitch:begin -->
"Treat the KV cache as a cache: keep one layer's keys at 4 bits plus the token ids, and recompute only the blocks a question asks for. With a tenth of the memory, every tested eviction method forgets the needle; RoD finds it, on two independent test splits."
<!-- p2:memo-pitch:end -->
