# Autoresearch program: C7 Recall-on-Demand (spike A)

**Goal.** Maximise the share of questions whose needle block is among the m blocks RoD re-prefills (needle-block hit@m), at RoD's own byte budget. End-to-end recall is confirmed only on the pre-registered test splits ([`../../../eval/PREREG.md`](../../../eval/PREREG.md)).

**Frozen evaluator:** [`eval_torch.py`](eval_torch.py) (PyTorch; the loop never edits it).
- Split: **dev seeds 100–109 only**, both needle styles (literal, paraphrase), ~4k-token contexts, 4 needles each. Only needles that fall in the evicted region count. The evaluator refuses seeds 0–1, which are test seeds.
- Budget: keep fractions 0.10 (primary, m = 3 under the 2-bit budget formula) and 0.25.
- Output: one JSON table over all variants (`dev_sweep.json`) and `hit_at_m=<float>` for `--variant`.
- The superseded MLX evaluator [`eval.py`](eval.py) was never run end to end (Linux MLX CPU is too slow) and is kept for the Apple-silicon port.

**Knobs searched (iteration 1, 2026-10-04):**
- scorer: {softmax_sum, max_logit, lift_mean, lift_max, softmax_lift}
- question tokens: {all, content}
- sketch bits: {2, 4}
- sketch layer: {0..15}
- plus the lexical IDF control

That is 322 variants, all computed from one prefill per context.

**Result** (ledger: [`results.tsv`](results.tsv)):
- a-priori config softmax_sum / all / 2-bit / layer 8: hit@3 = 0.24
- best, softmax_lift / content / 4-bit / layer 5: 0.95
- lexical control: 0.91

Selecting the best of 322 variants on 80 questions is optimistic; the unbiased numbers come from test seeds 0–2.

**Next knobs** (finals; each run on dev seeds, then confirmed on a fresh split):
1. Per-channel (KIVI-style) key quantisation for a 2-bit sketch at 0.5% of the KV.
2. Multi-layer voting (layers 1, 5, 6).
3. Top-k-mean block scoring.
4. Adaptive m (stop when the block-score margin is large).
5. A halo, if S4 shows that isolated recompute costs recall.

**Constraints.**
- Sketch + window queries + ids are charged to RoD's own KV budget.
- No question access before compression.
- A change is kept only if dev hit@m rises by more than 1 question **and** the next pre-registered test confirms it.
