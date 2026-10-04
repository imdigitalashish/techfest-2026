# P2 demo: talk track (3 minutes)

**Run it** from `perceptron-p02-kv-cache/`:

| Command | What you get |
|---|---|
| `demo/run.sh` | REPLAY. Committed T1/T2/T3 rows in the browser. Instant, offline, no model loaded. |
| `demo/run.sh --live` | REPLAY plus LIVE. The 1B model loads on the first live request: fp16 in RAM (~3 GB), upcast to fp32 for every matmul, freed on exit. One-time prerequisite: `demo/fetch.sh`. |
| `demo/smoke.sh` | Headless checks. See the header of `demo/smoke.sh`. |
| `demo/fallback/` | Screenshots of every step below, in case the live demo fails. |

**Before the judges arrive** (on `--live`):
- In the Live tab, press **Compress the document** once. This loads the model (~7 s) and prefills (~35 s).
- After that, an answer to a new question takes ~15 s. Re-compressing takes ~35 s.
- Close other heavy apps. The engine refuses to load below 30% free memory (`kern.memorystatus_level`).

**Timing (M5 CPU, 4 threads, measured 4 Oct):**
- Page: first visual in under 2 s.
- Model load: 7 s.
- Compress a 3,000-token document: 33 s.
- One question to all six methods: 15 s.

## 0:00–0:30 · The problem and the idea (Replay, T1, 10%)

Say:
- "A 1B model reading a 4,000-token document holds 129 MiB of KV cache."
- "Every eviction method decides what to forget before it knows the question."
- "We treat the KV cache as a cache. We keep a tiny resident set, plus a 4-bit sketch of one layer's keys, plus the token ids. When a question arrives, its own queries pick which 64-token blocks to recall."

Point at the thesis line: **RoD answers 41 of 48; the best eviction baseline (kvpress TOVA) answers 3; the full cache answers 40.**

Point at the track viewer:
- StreamingLLM keeps only the newest tokens.
- RoD's amber recalled block sits on the red fact it was asked about.

## 0:30–1:10 · The squeeze (the budget control)

Click **100% → 50% → 25% → 10%** and watch the StreamingLLM and RoD tracks shrink.
- **At 100%:** full cache 40/48, int8 40, int4 37, int2 0. Quantising every token stops working at 2 bits.
- **At 10%:**
  - Every query-agnostic eviction baseline answers ≤ 3/48, NVIDIA kvpress presses included.
  - RoD answers 41/48 from 7.1 MiB stored. That rises to 11.1 MiB at answer time, while the baselines hold 12.9 MiB.
  - RoD pays for its sketch, ids and window out of its own budget.

Say: "Every number on this tab is a committed row. `smoke.sh` checks the page against `RESULTS.md`, word for word."

## 1:10–1:40 · What doesn't work (the dip)

Click **Show this case at 25%** in the "Why RoD dips" panel.
- At 25%, RoD recalls 7 blocks instead of 2 and keeps a longer tail. A look-alike fact (vivid-glacier) is now in view, and the model answers with its number.
- Accuracy when the right block was recalled falls from **98% (10%) to 55% (25%)**.
- Post hoc (exploratory, amendment 3), in the same panel:
  - Exact KV for the same 7 blocks gives **0.896**, and recalling only the top-2 gives **0.854**.
  - So the dip comes from re-prefilling many blocks approximately (each block sees only the sinks and itself), not from missing the right block.
- The pre-registered primary passed: **+0.40 over StreamingLLM at 25%** (95% CI +0.25 to +0.54).
- Non-inferiority to the full cache at 25% was **not shown** (−0.25).

Click **T2**. RoD at 10% scores above the full cache (33 vs 22 of 48). The caveat says why: T2's full-cache ceiling is depressed by the 10-token answer limit (amendment 5; E6 sensitivity).

Click **T3**. Aliased keys defeat even the full cache (0.104). RoD's sketch finds the right block only 23% of the time, against 73% for the lexical control.

## 1:40–2:40 · Plant your own fact (Live)

Hand over the laptop: "Type any fact, anywhere."
- The default is "The judges' favourite dessert at Techfest 2026 is mango kulfi." The judge sets the position, then presses **Compress**.
- Say: "It reads the document once and builds every method's memory now, before any question exists."

Budget 10%. Point at step 2:
- **m = 2 recall blocks.** On a 3,000-token document RoD keeps 132 resident tokens.
- The knob stops at 10%. At 5% of a 3,000-token document, RoD's sketch, ids and window would leave m = 0, and the page would say "budget too small to recall".

Ask: as written, the **paraphrased** chip, or the judge's own words. Point at:
- **The X-ray row.** The question's layer-5 queries score every evicted block against the 4-bit sketch (`kvbench_torch.block_scores`). The block holding the fact lights up, and the page checks that these scores pick exactly the blocks RoD recalled.
- **The answers.** Full ✓ and RoD ✓, from about 9 MiB at answer time against 93 MiB. StreamingLLM, H2O and SnapKV make up other desserts or say there is none.

Drag the budget to 25%. The stores rebuild without re-reading the document, and the answers refresh.

Say: "This is a single live example, not evidence. The committed numbers sit right below it."

## 2:40–3:00 · Close

- "Compress before the question, recall on demand. At 10% of the KV memory, on literal needles, RoD recalls what the full cache recalls; every eviction baseline we ran, including kvpress, recalls almost nothing."
- "The open problem is look-alike confusion as more blocks come back. A 64-token halo did not fix it (S4)."

## If something fails

- **Live will not load** (memory pressure or a missing fetch): stay on Replay. Every claim above is there.
- **The browser or server fails:** open `demo/fallback/` (`01`–`09` follow this script in order).
- **Port busy:** `run.sh` picks the next free port and prints the URL.
