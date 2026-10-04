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
