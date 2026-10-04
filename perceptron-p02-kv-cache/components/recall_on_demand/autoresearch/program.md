# Autoresearch program — C7 Recall-on-Demand (spike A)

**Goal.** Maximise the share of questions whose needle block is among the m blocks that RoD chooses to re-prefill, at a fixed byte budget. Then confirm that end-to-end recall improves on a held-out split.

**Frozen evaluator:** `eval.py` (never edited by the loop). It prints one scalar, `hit_at_m` (mean over calibration questions), plus secondary metrics: sketch bytes per token and ms per question.
- Calibration split: seeds 100–104, 4k-token contexts, 4 needles each (up to 20 questions; only needles that fall in the evicted region count).
- Resident policy: StreamingLLM at 5% of T. Recall budget: m = 3 blocks.
- Held-out check (lead, periodically): `eval/kvbench.py --seed 200 --n 12` end-to-end recall for `rod` vs `snapkv`/`streaming` at equal answer-time bytes.

**Knobs the loop may change** (in `components/recall_on_demand/rod.py` once extracted; today `rod_answer` in `eval/kvbench.py`):
1. Sketch layer(s): single layer 0–15; vote across 2–3 layers (bytes scale linearly).
2. Sketch bits: 1, 2, 3, 4. Group size: 32 or 64.
3. Relevance aggregation: softmax-sum vs raw-max over heads and question positions; ignore chat-template tokens.
4. Block size: 32, 64, 128. Block scoring: max vs top-3 mean.
5. PCA-projected sketch (16 or 32 of 64 dims), with the projection fitted on WikiText *train*, never on the calibration contexts.

**Constraints.**
- Sketch + IDs ≤ 1% of full KV bytes per token (≤ 327 B/token for Llama-3.2-1B).
- No access to the question before compression (query-agnostic).
- Contract tests pass.
- Keep a change only if `hit_at_m` improves by ≥ 1 question **and** does not drop on a second seed set (105–109).

**Ledger:** `results.tsv` — timestamp · commit · hypothesis · hit_at_m · delta · kept? · notes.
**Status (2026-10-04 08:15 IST):** scaffolded, not yet run. The machine is under heavy swap (lean mode); the first iteration runs after compute is staggered.
