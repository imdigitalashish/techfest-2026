# Pre-registration — P2 main comparison (Recall-on-Demand vs query-agnostic eviction)

- **Registered:** 2026-10-04 15:14 IST. This equals the commit time of this file (PLAYBOOK §6). No test-split run had started at registration.
- **Status:** frozen. Later changes are appended under *Amendments* with a date; the registered text is never edited.

## Question
Does Recall-on-Demand (RoD) recover the long-context recall that query-agnostic KV-cache eviction loses, at **equal answer-time KV bytes**?

## Fixed setup
- **Model and engine.**
  - Weights: `mlx-community/Llama-3.2-1B-Instruct-4bit` (snapshot `08231374…`), dequantised to fp16 weights.
  - Compute: fp32 on CPU (PyTorch 2.10, Azure Standard_D16ds_v5); KV stored as fp16 (32 KiB/token).
  - Engine parity vs the HF reference forward: max |Δlogit| 2e-5 with fp32 KV and 0.011 with fp16 KV; argmax equal ([`results/parity_torch.json`](results/parity_torch.json)).
  - Environment: venv `~/venv_kvp` on the VM (kvpress 0.5.5, transformers 5.2.0).
- **Workload** ([`kvbench_torch.py`](kvbench_torch.py)).
  - Haystack: WikiText-103 (validation + test) text, contexts of about 4,096 tokens (actual T recorded).
  - Needles: 4 synthetic needles per context, at depths 5–95%.
  - Answering: greedy decoding, ≤ 10 new tokens. An answer is correct iff the 7-digit value appears in it.
- **Protocol: query-agnostic, shared-context multi-query.** Every method builds its store from the context *before* any question is seen; the same 4 questions are then answered from that store (paired across methods). This is not a multi-turn dialogue.
- **Test splits** (never used for tuning):
  - **T1:** seed 0, literal needles, 12 contexts (48 questions).
  - **T2:** seed 1, paraphrased needle/question templates, 12 contexts (48 questions). Keys stay literal.
- **Tuning used only the dev seeds 100–109** ([`../components/recall_on_demand/autoresearch/dev_sweep.json`](../components/recall_on_demand/autoresearch/dev_sweep.json), ledger `results.tsv`).
- **Disclosures.**
  - A pre-tuning smoke test used seed 0 at 1,024 tokens: one context, 2 needles, with the old RoD config, which failed.
  - The kvpress smoke used seed 999.
- **RoD config, frozen from the dev sweep:**
  - Scorer `softmax_lift` on question content tokens.
  - Sketch: 4-bit, layer 5. Block 64, halo 0.
  - Resident cache: StreamingLLM (4 sinks + recent tokens) holding half of the KV budget left after extras.
  - Every extra byte is deducted from the KV budget: sketch, context-window queries (256 KiB) and int32 token ids.
  - `rodlex` (control) is the same store with no sketch, choosing blocks by IDF overlap with the question's content tokens.
- **Methods.**
  - Own implementations: `full`, `int8`, `int4`, `int2`, `streaming`, `random`, `h2o`, `snapkv`, `knorm`, `snapkv_qa` (oracle: sees the question), `rod`, `rodlex`, at keep fractions 0.10, 0.25 and 0.50.
  - NVIDIA kvpress 0.5.5 reference presses (`kvp_streaming`, `kvp_snapkv`, `kvp_observed` ≈ H2O, `kvp_knorm`, `kvp_expected`, `kvp_tova`), at keep fractions 0.10 and 0.25.

## Primary comparison (one test)
**RoD − StreamingLLM** (own implementation, which is RoD's resident policy) recall at **keep fraction 0.25** on **T1**.
- **Statistic:** mean over contexts of the per-context recall difference.
- **Interval:** 95% CI by paired context bootstrap (2,000 resamples, seed 0).
- **Success** iff the lower CI bound > 0.

Why 0.25 rather than 0.10: with RoD's extras charged to its own budget, the a-priori half/half split leaves only about 2 recall blocks at 0.10 on 4k contexts. 0.25 is the strongest compression where every method has a non-trivial budget. This was decided from the dev data and the seed-999 smoke only.

## Secondary comparisons (reported with CIs; no multiplicity correction claimed)
- **S1:** RoD vs **each** query-agnostic eviction baseline at 0.25 on T1:
  - own `h2o`, `snapkv`, `knorm`;
  - kvpress `streaming`, `snapkv`, `observed`, `knorm`, `expected`, `tova`.

  "RoD beats every query-agnostic baseline" is claimed only if **every** lower CI bound > 0.
- **S2:** RoD − `rodlex` at 0.25 on T1 and T2. Does the attention sketch beat a lexical index?
- **S3:** the primary comparison replicated on T2 (paraphrase templates).
- **S4:** halo ablation. RoD with `--halo 64` vs halo 0 on T1, paired: how much does isolated block recompute cost?
- **S5:** all of the above at keep fractions 0.10 and 0.50.
- **MVP (descriptive):** recall and stored bytes (compression ×) of every method vs the full cache on T1, including int8/int4/int2.

## Memory accounting
- **Analytic KV bytes** = layers × kv_heads × kept tokens × head_dim × 2 (K, V) × 2 bytes, plus quantisation scales/biases, and for RoD the sketch, window queries and token ids.
- **Measured:** the sum of `nbytes` over every retained tensor. For the full cache this is asserted equal to the analytic value.
- **Answer-time bytes:** for RoD, stored bytes plus the recalled blocks' KV. RoD's budget makes its answer-time bytes ≤ the baselines' bytes at the same keep fraction.
- **Process peak RSS:** reported for context only; it is dominated by the fp32 weights.

## Decision rules (what we will say)
- **Primary succeeds:** the abstract may state "RoD beats StreamingLLM at equal answer-time KV memory (keep 25%)", with the CI.
- **Primary fails:** we report it, and the selection memo lowers P2's innovation score.
- **S2's CI includes 0:** we do not claim the sketch beats lexical retrieval. RoD is presented as the store-and-recompute design, with a swappable block scorer.
- **RoD's T2 recall falls > 0.15 below its T1 recall while the baselines' don't:** we report that RoD's retrieval is helped by lexical overlap.
- **Latency:** CPU latency is reported only as overhead relative to the other methods on the same machine, not as GPU timings.

## Commands (run on the VM in `~/p02` with `~/venv_kvp/bin/python`, `HF_HUB_OFFLINE=1`)
```
M=full,int8,int4,int2,streaming,random,h2o,snapkv,knorm,snapkv_qa,rod,rodlex,kvp_streaming,kvp_snapkv,kvp_observed,kvp_knorm,kvp_expected,kvp_tova
R="--rod_scorer softmax_lift --rod_qsel content --rod_layer 5 --rod_bits 4 --lex_qsel content"
T1: python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 0 --style literal    --fracs 0.1,0.25,0.5 --kvp_fracs 0.1,0.25 --methods $M $R --name T1_literal_s0
T2: python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 1 --style paraphrase --fracs 0.1,0.25,0.5 --kvp_fracs 0.1,0.25 --methods $M $R --name T2_paraphrase_s1
S4: python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 0 --style literal    --fracs 0.1,0.25,0.5 --methods rod $R --halo 64 --name S4_halo64_s0
```
Run order: T1, then T2, then S4, one job at a time.

## Amendments
### Amendment 1: 2026-10-04 15:18 IST
Committed while T1 was running, before any test-split result had been seen.
- **Why.** T2 paraphrases only the templates. Its keys stay literal (e.g. "silent-tiger"), so a lexical index can still match them, and T2 cannot separate the attention sketch from lexical retrieval. This was raised in the Supervisor's 15:17 spot-check.
- **New split T3:** seed 2, style `alias`, 12 contexts (48 questions).
  - Each needle names its key with one word pair ("The vault of the big house opens with the code …").
  - The question uses synonyms ("Which code opens the vault of the large home?"), so key words share no tokens.
  - The template words are shared by all 4 needles.
- **Methods (lean):** `full`, `streaming`, `snapkv`, `kvp_expected`, `rod`, `rodlex` at keep fractions 0.10 and 0.25. The RoD config is unchanged.
- **S6:** RoD − `rodlex` on T3 at 0.10 and at 0.25, with paired context-bootstrap CIs. "The sketch retrieves by meaning where a lexical index cannot" is claimed only if a lower bound > 0.
  - Expected weakness, stated in advance: shared template words let `rodlex` recall several needle blocks at once, and its recall budget is not smaller than RoD's (at 0.10 it is larger: about 3 blocks vs 2), so S6 is a conservative test.
  - The full-cache ceiling on T3 is reported. If full-cache recall is < 0.5, T3 is reported as too hard for this 1B model and S6 as inconclusive.
- **Code.** The `alias` style is an additive change to `kvbench_torch.py`: literal and paraphrase behaviour and their RNG draws are unchanged.
  - T1, T2 and S4 run the pre-registered file as copied to the VM before registration (md5 `74029553e051e0b93d56af5cd51b3267`).
  - T3 runs after S4 with the amended file.
- **Command:**
  ```
  T3: python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 2 --style alias --fracs 0.1,0.25 --kvp_fracs 0.1,0.25 --methods full,streaming,snapkv,kvp_expected,rod,rodlex $R --name T3_alias_s2
  ```

### Amendment 2: 2026-10-04 15:30 IST
Committed while T1 was still running; no test-split result had been seen. It responds to the gpt-6-sol static review (`reviews/2026-10-04-code-eval-gpt-6-sol.md`). No run, seed, method or config changes; only how results are analysed and worded.
- **Analysis source.** Every registered contrast is computed by `eval/render_docs.py` from the per-question rows, joined by sample index across runs. This covers S1 vs `kvp_tova` and S4 (halo-64 rows from run S4 paired with the halo-0 RoD rows of T1, which share seed and contexts).
- **S5 scope.** The kvpress presses were registered only at keep 0.10 and 0.25, so S5 at 0.50 covers our own baselines only. Unrun cells are marked "not run", never omitted.
- **Memory wording.** "Answer-time bytes" means the **persistent store plus recalled KV**, not process peak memory. RoD's scoring pass also holds a transient, unchunked working set (dense sketch, score tensors), which is reported analytically and separately. No peak-memory-equality claim is made.
- **Byte check.** For every (context, keep fraction), RoD's answer-time bytes must be ≤ each baseline's stored bytes. Violations are counted and reported.
- **Development number.** The dev hit@3 of 0.95 was computed with the sweep's simplified budget (2-bit sketch, no window-query cost). It is reported only as "exploratory, best of 322 under the sweep budget". A production-budget dev table may be added after the test runs, as exploratory information; it cannot change the frozen config.
- **Protocol wording.** Results speak of *independent questions answered after one query-agnostic compression*, not sequential multi-turn chat.
- **Labels.** Our local `snapkv` is a sink-augmented variant (it pools over all keys and forces 4 sinks plus the window); `kvp_snapkv` is the reference.

### Amendment 3: 2026-10-04 15:35 IST
Committed while T1 was still running; no test-split outcome had been seen. It responds to the gpt-6-astra phase-1 review (`reviews/2026-10-04-spike-prereg-gpt-6-astra.md`). No change to the primary comparison, seeds, methods or config.
- **S7: non-inferiority vs the full cache (answers "barely hurting recall").** RoD − full recall at keep 0.25 on T1.
  - Paired context bootstrap as in the primary.
  - Margin: **−0.05** (5 points of absolute recall). "Near-lossless at 25% memory" is claimed only if the lower 95% bound > −0.05.
  - At 0.10 and 0.50 it is descriptive only.
  - Every method's paired recall drop vs full is reported (the MVP's "accuracy drop").
- **S6: one confirmatory fraction.** Keep **0.10** is confirmatory: it is the budget where RoD (about 2 blocks) and `rodlex` (about 3 blocks) cannot recall all four needles. Keep 0.25 becomes exploratory.
- **Small-sample reporting.** For the primary and S7, all 12 per-context paired deltas and the discordant question counts are published. Strict single-value accuracy is reported as a sensitivity check: correct, and naming no other needle's value from the same context.
- **Exploratory, after T3** (labelled exploratory, never confirmatory). All use T1's seed-0 contexts and the frozen config:
  - (E1) streamed scorer vs unchunked scorer: identical block choices? (`components/recall_on_demand/verify_streamed.py`);
  - (E2) exact-KV oracle: the same chosen blocks, but their exact KV gathered from the full prefill (needs a full backing store, so analysis only). This separates approximate re-prefill error from retrieval error;
  - (E3) oracle-block selection: the needle's block forced, plus the scorer's other picks, re-prefilled. This separates retrieval failure from reconstruction and read-out failure;
  - (E4, if time) the frozen winner and the lexical control re-scored on dev seeds under the production budget.
- **Wording commitments.**
  - "Position-preserving approximate re-prefill", not "faithful".
  - "Tested query-agnostic eviction policies on a fixed reusable context", not "query-agnostic compression in general".
  - Memory claims refer to **post-prefill retained state**: our prefill builds the full KV before compressing.
  - No absolute "first" or "zero footprint" claims; the sketch is KV-derived retained state.

### Amendment 4: 2026-10-04 16:21 IST
Committed after T1's results were seen (16:18) and before any T2 outcome had been seen: T2 started 16:18, and only its progress lines were read. Nothing registered above changes.
- **Observation from T1 (exploratory, not confirmatory).** At keep 0.10, RoD recalls 0.854 vs the full cache's 0.833 (RoD − full +0.021, 95% CI −0.15 to +0.19). At the registered 0.25 it recalls 0.583 (S7 failed).
  - Mechanism seen in T1's rows: the needle-block hit rate is 0.88 at 0.10 and 1.00 at 0.25, but accuracy given a hit falls from 0.98 to 0.55.
  - 16 of RoD's 20 wrong answers at 0.25 name another needle's value. Recalling more needle-like blocks causes key–value confusion.
- **R1: replication on T2** (fresh contexts, seed 1). RoD − full at keep 0.10, with a paired context bootstrap.
  - "Replicated" means the lower 95% bound is > −0.15, i.e. within 15 recall points of the full cache.
  - The margin is lenient because 12 contexts cannot resolve 5 points (T1's CI half-width is about 0.17). It is fixed now, before T2.
- **R2: mechanism on T2 (descriptive).** RoD's accuracy given a needle-block hit at 0.10 vs 0.25, and the share of wrong answers naming another needle's value.
- **E5 (exploratory, T1 contexts).** RoD with recall capped at **2 blocks** at keep 0.25 and 0.50 ("precision-first recall"). Added to the post-hoc job, which has not started.
- **Reporting.** The 0.10 result is reported with its status: exploratory on T1, and replicated or not on T2 under R1. It is never presented as the pre-registered primary.

### Amendment 5: 2026-10-04 17:39 IST (post hoc; added after T2's results were seen)
- **Issue** (Supervisor 17:37). On T2 the full cache often restates the question ("The seven-digit code issued to …") and is cut off by the harness's 10-token answer limit before the number.
  - Of the full cache's 26 wrong T2 answers, 17 contain no 7-digit number; 12 of those are cut-off preambles. Only 8 name another needle's value.
  - RoD at keep 0.10 has 9 of 15 wrong answers without a number (4 cut off) and 0 naming another needle.
  - T1 is unaffected: all 8 of the full cache's wrong answers name another needle's value.
- **R1 stays as registered** (it passes). But "RoD exceeds the full cache on T2" is **confounded by answer truncation**. The interpretation "fewer recalled blocks hide look-alike records" is withdrawn for T2. R2's T1 evidence (other-needle values) is unaffected.
- **E6 (exploratory, post hoc):** re-answer T2's contexts with `max_new=32` for full, StreamingLLM (0.10, 0.25), the question-aware SnapKV oracle (0.25) and RoD (0.10, 0.25).
  - Scoring: the registered lenient rule (the value appears anywhere) and a strict rule (the first 7-digit number equals the value).
  - Script: `components/recall_on_demand/posthoc_maxnew.py`, queued after the post-hoc job.
  - It is reported as a sensitivity analysis and cannot change any registered verdict.

