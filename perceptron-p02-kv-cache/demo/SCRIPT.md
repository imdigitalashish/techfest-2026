# P2 demo: talk track

**Run it** from `perceptron-p02-kv-cache/`:

| Command | What you get |
|---|---|
| `demo/run.sh` | REPLAY. Committed T1/T2/T3 rows in the browser. Instant, offline, no model loaded. |
| `demo/run.sh --live` | REPLAY plus LIVE. The 1B model loads on the first live request: fp16 in RAM (~3 GB), upcast to fp32 for every matmul, freed on exit. One-time prerequisite: `demo/fetch.sh`. |
| `demo/smoke.sh` | Headless checks. See the header of `demo/smoke.sh`. |
| `demo/fallback/` | Recorded screenshots `01`–`09`. |

**Pick a route and say which one you are showing.**
- **Route A** (3 minutes, Replay only) is the default.
- **Route B** (live) is optional and needs 2–3 extra minutes.
- If you fall back to `demo/fallback/`, say the screenshots are recorded, not live.

**What the MiB mean:** every budget and MiB on screen counts a method's *logical context state* (stored + recalled KV). That is not peak RAM/VRAM. The header says so at all times.

**Measured model-call timings** (M5 CPU, 4 threads, 4 Oct):
- Model load: 5–7 s.
- Compress a 2,990-token document: 27–33 s on a quiet Mac, up to 54 s under CPU contention.
- One question to all six methods: 15–18 s quiet, up to 45 s under contention.
- These cover only the model calls. Rehearse each route with a stopwatch, including typing and talking.

## Route A · 3 minutes · Replay only

### 0:00–0:30 · The problem and the idea (T1, 10%)

Say:
- "A 1B model holding a 4,000-token document keeps 129 MiB of KV cache."
- "Every eviction method decides what to forget before it knows the question."
- "We treat the KV cache as a cache. We keep a small part, index the rest with a 4-bit sketch of one layer's keys plus the token ids, and when a question arrives its own queries locate the 64-token blocks to reconstruct."

Point at:
- **The thesis line:** RoD answers 41 of 48; the best eviction baseline (kvpress TOVA) answers 3; the full cache answers 40.
- **The row of three cards under the token map:**
  - Full ✓, 129.1 MiB.
  - RoD ✓, 7.1 MiB stored and 11.1 MiB at answer time.
  - TOVA ✗, 12.9 MiB.

### 0:30–1:10 · The squeeze (budget control)

Click **100% → 50% → 25% → 10%** and watch the token map shrink.
- **At 100%:** full cache 40/48, int8 40, int4 37, int2 0.
  - Say: "int2 here is this harness's simple per-token quantiser on this workload, not a limit of 2-bit methods in general."
- **At 10%:**
  - Every query-agnostic eviction baseline answers ≤ 3/48, NVIDIA kvpress presses included.
  - RoD answers 41/48 with 7.1 MiB stored and 11.1 MiB at answer time, against 12.9 MiB for the baselines.
  - RoD pays for its sketch, ids and window out of its own budget.

Say: "Every number on this tab is a committed row. `smoke.sh` checks the page against `RESULTS.md` and renders all 528 page states."

### 1:10–1:50 · What doesn't work (the dip at 25%)

Click **Show this case at 25%**.
- RoD answers 28/48 at 25%.
  - The pre-registered primary passed: **+0.40 over StreamingLLM** (95% CI +0.25 to +0.54).
  - Non-inferiority to the full cache is **not shown** (−0.25).
- When the asked fact's block is recalled, accuracy falls from **98% at 10% to 55% at 25%**. The model answers with another fact's number.
- Post hoc (exploratory, amendment 3), in the same panel:
  - Exact KV for the same blocks gives 0.896, and recalling only the top 2 blocks gives 0.854.
  - So the dip comes from reconstructing many blocks approximately.

### 1:50–2:35 · Honesty: T2 and T3

Click **T2**. At every budget the page shows only this caveat:
- With 32-token answers (E6, exploratory): **full cache 32/48 vs RoD at 10% 36/48; paired +0.08 (95% CI −0.02 to +0.23): superiority not established.**
- Under the registered 10-token answer limit, the full cache's 22/48 is depressed by cut-off answers (amendment 5).
- What does replicate (S3): RoD beats StreamingLLM at 25%, +0.375 (95% CI +0.23 to +0.54).

Click **T3**:
- Aliased keys defeat even the full cache (5/48).
- At 10%, RoD's sketch finds the asked block 23% of the time, against 73% for the lexical control.
- S6, "the sketch beats lexical retrieval", is not shown.

### 2:35–3:00 · Close

Say:
- "Compress before the question, recall on demand. Every query-agnostic eviction baseline we ran, kvpress included, answers at most 3 of 48 at 10%."
- "The open problem is approximate reconstruction of many blocks. A 64-token halo did not fix it (S4)."
- "At 10%, RoD answers **41/48 vs the full cache's 40/48 on this literal-needle test; equivalence is not established.**"

## Route B · optional extended live (+2–3 minutes)

**Before the slot:**
- Run `demo/run.sh --live`, open the Live tab and press **Compress** with the default fact. This takes ~6 s to load and ~30 s to compress.
- Leave it at a 10% budget (m = 2).
- The engine refuses to load below 30% free memory, so close heavy apps first.

**During the slot:**
1. Say: "This document was compressed before any question existed. The fact is SYNTHETIC."
   - The full cache would hold 93.4 MiB; RoD keeps 5.2 MiB.
2. Have the judge type **one fresh question** in their own words, then press **Ask** (~15–18 s; up to 45 s under load).
   - While it runs, explain the *located (sketch score)* row: the question's layer-5 queries score every evicted block against the 4-bit sketch (`block_scores`, softmax_lift).
   - The page checks that these scores select exactly the blocks RoD reconstructs.
3. Point at the answers and the **LIVE · SINGLE EXAMPLE · NOT EVIDENCE** stamp, with the committed numbers below them.
   - RoD-lexical also gets the default fact right, with slightly fewer bytes.
   - Say: "This example does not show the sketch beating lexical retrieval."
4. Optional: drag the budget to 25%. The stores rebuild without re-reading the document, and the last question is re-asked (~15–25 s).
5. Offer to plant the judge's own fact afterwards: ~35 s to compress plus ~15 s per question.

## If something fails

- **Live will not load** (memory pressure or a missing fetch): stay on Route A. Every claim above is in Replay.
- **The browser or server fails:** open `demo/fallback/`, and say the screenshots are recorded. Use `01`–`06` for Route A and `07`–`09` for Route B.
- **Port busy:** `run.sh` picks the next free port and prints the URL.
