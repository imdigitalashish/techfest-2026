# Results (rendered by `eval/render_docs.py` from committed rows; do not edit by hand)

Pre-registration: [`PREREG.md`](PREREG.md). Engine parity: [`results/parity_torch.json`](results/parity_torch.json).

## Pre-registered verdicts

- **Primary** (RoD − StreamingLLM, keep 0.25, T1): +0.396 (95% CI +0.25 to +0.54, 12 contexts) → **SUCCESS** (lower bound > 0)
- **S7** (RoD − full cache, keep 0.1, T1) (descriptive): +0.021 (95% CI -0.15 to +0.19, 12 contexts)
- **S7** (RoD − full cache, keep 0.25, T1) (confirmatory, margin −0.05): -0.250 (95% CI -0.42 to -0.08, 12 contexts) → non-inferiority **not shown**
- **S7** (RoD − full cache, keep 0.5, T1) (descriptive): -0.229 (95% CI -0.40 to -0.06, 12 contexts)
- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): beats **all** 9 baselines; weakest margin kvpress TOVA +0.229 (95% CI +0.04 to +0.40, 12 contexts)
- **S2** (RoD − RoD-lexical, keep 0.25, T1 literal): +0.042 (95% CI -0.04 to +0.12, 12 contexts) → no evidence the sketch beats lexical retrieval
- **S2** (RoD − RoD-lexical, keep 0.25, T2 paraphrase): pending
- **S3** (primary replicated on T2 paraphrase): pending
- **S5** (RoD − baseline, keep 0.1, T1): StreamingLLM (ours) +0.833 (95% CI +0.71 to +0.94, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.854 (95% CI +0.73 to +0.96, 12 contexts); H2O-style (ours) +0.854 (95% CI +0.73 to +0.96, 12 contexts); RoD-lexical (control) +0.417 (95% CI +0.31 to +0.52, 12 contexts); kvpress ExpectedAttention +0.854 (95% CI +0.73 to +0.96, 12 contexts)
- **S5** (RoD − baseline, keep 0.5, T1): StreamingLLM (ours) +0.167 (95% CI +0.02 to +0.31, 12 contexts); SnapKV-variant (ours, +4 sinks) +0.375 (95% CI +0.21 to +0.56, 12 contexts); H2O-style (ours) +0.333 (95% CI +0.15 to +0.50, 12 contexts); RoD-lexical (control) +0.000 (95% CI -0.08 to +0.08, 12 contexts); kvpress ExpectedAttention not run
- **Byte check T1**: RoD answer-time bytes > a baseline's stored bytes in 0 of 36 (context, keep) cells

## T1 — literal needles, seed 0

`python eval/kvbench_torch.py --ctx 4096 --n 12 --needles 4 --seed 0 --fracs 0.1,0.25,0.5 --methods full,int8,int4,int2,streaming,random,h2o,snapkv,knorm,snapkv_qa,rod,rodlex,kvp_streaming,kvp_snapkv,kvp_observed,kvp_knorm,kvp_expected,kvp_tova --style literal --rod_layer 5 --rod_bits 4 --rod_scorer softmax_lift --rod_qsel content --lex_qsel content --kvp_fracs 0.1,0.25 --halo 0 --threads 8 --name T1_literal_s0`

torch-cpu · Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz · torch 2.10.0+cpu · 8 threads · wall 3761.3 s · 12 contexts × 4 questions · mean context 4123 tokens

| Method | Keep | Recall | 95% CI | Stored KV MiB | Compression | Answer-time MiB | s/answer (CPU) | Needle-block hit |
|---|---|---|---|---|---|---|---|---|
| Full cache | 1.00 | 0.833 | 0.73–0.94 | 128.8 | 1.0× | 128.8 | 0.79 |  |
| int8 KV | 1.00 | 0.833 | 0.73–0.94 | 68.4 | 1.9× | 68.4 | 0.89 |  |
| int4 KV | 1.00 | 0.771 | 0.65–0.88 | 36.2 | 3.6× | 36.2 | 0.88 |  |
| int2 KV | 1.00 | 0.000 | 0.00–0.00 | 20.1 | 6.4× | 20.1 | 2.04 |  |
| StreamingLLM (ours) | 0.10 | 0.021 | 0.00–0.06 | 12.9 | 10.0× | 12.9 | 0.39 |  |
| Random (control) | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.40 |  |
| H2O-style (ours) | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.34 |  |
| SnapKV-variant (ours, +4 sinks) | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.40 |  |
| K-norm (ours) | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.35 |  |
| SnapKV, question-aware (oracle) | 0.10 | 0.833 | 0.73–0.94 | 12.9 | 10.0× | 12.9 | 0.87 |  |
| **RoD (ours)** | 0.10 | 0.854 | 0.73–0.96 | 7.1 | 18.2× | 11.1 | 1.31 | 0.88 |
| RoD-lexical (control) | 0.10 | 0.438 | 0.31–0.54 | 6.4 | 20.0× | 12.4 | 1.37 | 0.92 |
| kvpress StreamingLLM | 0.10 | 0.021 | 0.00–0.06 | 12.9 | 10.0× | 12.9 | 0.40 |  |
| kvpress SnapKV | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.40 |  |
| kvpress ObservedAttention (H2O) | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.34 |  |
| kvpress Knorm | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.50 |  |
| kvpress ExpectedAttention | 0.10 | 0.000 | 0.00–0.00 | 12.9 | 10.0× | 12.9 | 0.34 |  |
| kvpress TOVA | 0.10 | 0.062 | 0.00–0.12 | 12.9 | 10.0× | 12.9 | 0.35 |  |
| StreamingLLM (ours) | 0.25 | 0.188 | 0.12–0.25 | 32.2 | 4.0× | 32.2 | 0.46 |  |
| Random (control) | 0.25 | 0.000 | 0.00–0.00 | 32.2 | 4.0× | 32.2 | 0.43 |  |
| H2O-style (ours) | 0.25 | 0.083 | 0.02–0.15 | 32.2 | 4.0× | 32.2 | 0.38 |  |
| SnapKV-variant (ours, +4 sinks) | 0.25 | 0.062 | 0.00–0.12 | 32.2 | 4.0× | 32.2 | 0.41 |  |
| K-norm (ours) | 0.25 | 0.000 | 0.00–0.00 | 32.2 | 4.0× | 32.2 | 0.37 |  |
| SnapKV, question-aware (oracle) | 0.25 | 0.833 | 0.73–0.94 | 32.2 | 4.0× | 32.2 | 0.92 |  |
| **RoD (ours)** | 0.25 | 0.583 | 0.44–0.73 | 16.7 | 7.7× | 30.8 | 2.89 | 1.00 |
| RoD-lexical (control) | 0.25 | 0.542 | 0.38–0.71 | 16.1 | 8.0× | 31.4 | 2.82 | 0.95 |
| kvpress StreamingLLM | 0.25 | 0.188 | 0.12–0.25 | 32.2 | 4.0× | 32.2 | 0.46 |  |
| kvpress SnapKV | 0.25 | 0.062 | 0.00–0.12 | 32.2 | 4.0× | 32.2 | 0.41 |  |
| kvpress ObservedAttention (H2O) | 0.25 | 0.000 | 0.00–0.00 | 32.2 | 4.0× | 32.2 | 0.37 |  |
| kvpress Knorm | 0.25 | 0.000 | 0.00–0.00 | 32.2 | 4.0× | 32.2 | 0.39 |  |
| kvpress ExpectedAttention | 0.25 | 0.042 | 0.00–0.10 | 32.2 | 4.0× | 32.2 | 0.40 |  |
| kvpress TOVA | 0.25 | 0.354 | 0.27–0.46 | 32.2 | 4.0× | 32.2 | 0.43 |  |
| StreamingLLM (ours) | 0.50 | 0.438 | 0.35–0.52 | 64.4 | 2.0× | 64.4 | 0.55 |  |
| Random (control) | 0.50 | 0.125 | 0.04–0.23 | 64.4 | 2.0× | 64.4 | 0.49 |  |
| H2O-style (ours) | 0.50 | 0.271 | 0.19–0.35 | 64.4 | 2.0× | 64.4 | 0.46 |  |
| SnapKV-variant (ours, +4 sinks) | 0.50 | 0.229 | 0.08–0.38 | 64.4 | 2.0× | 64.4 | 0.50 |  |
| K-norm (ours) | 0.50 | 0.125 | 0.04–0.21 | 64.4 | 2.0× | 64.4 | 0.46 |  |
| SnapKV, question-aware (oracle) | 0.50 | 0.854 | 0.75–0.94 | 64.4 | 2.0× | 64.4 | 1.00 |  |
| **RoD (ours)** | 0.50 | 0.604 | 0.44–0.75 | 32.6 | 4.0× | 62.7 | 5.40 | 1.00 |
| RoD-lexical (control) | 0.50 | 0.604 | 0.44–0.75 | 32.2 | 4.0× | 63.3 | 5.28 | 1.00 |

## Recall drop vs the full cache (T1, paired by context; MVP)

| Method | Keep | Recall | Strict recall | Drop vs full (95% CI) |
|---|---|---|---|---|
| int8 KV | 1.00 | 0.833 | 0.833 | +0.000 (+0.00 to +0.00) |
| int4 KV | 1.00 | 0.771 | 0.771 | -0.062 (-0.12 to +0.00) |
| int2 KV | 1.00 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| StreamingLLM (ours) | 0.10 | 0.021 | 0.021 | -0.812 (-0.92 to -0.71) |
| Random (control) | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| H2O-style (ours) | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| SnapKV-variant (ours, +4 sinks) | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| K-norm (ours) | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| SnapKV, question-aware (oracle) | 0.10 | 0.833 | 0.833 | +0.000 (-0.08 to +0.10) |
| **RoD (ours)** | 0.10 | 0.854 | 0.854 | +0.021 (-0.15 to +0.19) |
| RoD-lexical (control) | 0.10 | 0.438 | 0.438 | -0.396 (-0.52 to -0.27) |
| kvpress StreamingLLM | 0.10 | 0.021 | 0.021 | -0.812 (-0.92 to -0.71) |
| kvpress SnapKV | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress ObservedAttention (H2O) | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress Knorm | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress ExpectedAttention | 0.10 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress TOVA | 0.10 | 0.062 | 0.062 | -0.771 (-0.88 to -0.67) |
| StreamingLLM (ours) | 0.25 | 0.188 | 0.188 | -0.646 (-0.75 to -0.54) |
| Random (control) | 0.25 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| H2O-style (ours) | 0.25 | 0.083 | 0.083 | -0.750 (-0.85 to -0.62) |
| SnapKV-variant (ours, +4 sinks) | 0.25 | 0.062 | 0.062 | -0.771 (-0.88 to -0.65) |
| K-norm (ours) | 0.25 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| SnapKV, question-aware (oracle) | 0.25 | 0.833 | 0.833 | +0.000 (-0.06 to +0.06) |
| **RoD (ours)** | 0.25 | 0.583 | 0.583 | -0.250 (-0.42 to -0.08) |
| RoD-lexical (control) | 0.25 | 0.542 | 0.542 | -0.292 (-0.48 to -0.08) |
| kvpress StreamingLLM | 0.25 | 0.188 | 0.188 | -0.646 (-0.75 to -0.54) |
| kvpress SnapKV | 0.25 | 0.062 | 0.062 | -0.771 (-0.88 to -0.65) |
| kvpress ObservedAttention (H2O) | 0.25 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress Knorm | 0.25 | 0.000 | 0.000 | -0.833 (-0.94 to -0.73) |
| kvpress ExpectedAttention | 0.25 | 0.042 | 0.042 | -0.792 (-0.92 to -0.65) |
| kvpress TOVA | 0.25 | 0.354 | 0.354 | -0.479 (-0.62 to -0.31) |
| StreamingLLM (ours) | 0.50 | 0.438 | 0.438 | -0.396 (-0.50 to -0.29) |
| Random (control) | 0.50 | 0.125 | 0.125 | -0.708 (-0.83 to -0.58) |
| H2O-style (ours) | 0.50 | 0.271 | 0.271 | -0.562 (-0.67 to -0.44) |
| SnapKV-variant (ours, +4 sinks) | 0.50 | 0.229 | 0.229 | -0.604 (-0.79 to -0.40) |
| K-norm (ours) | 0.50 | 0.125 | 0.125 | -0.708 (-0.83 to -0.56) |
| SnapKV, question-aware (oracle) | 0.50 | 0.854 | 0.854 | +0.021 (+0.00 to +0.06) |
| **RoD (ours)** | 0.50 | 0.604 | 0.604 | -0.229 (-0.40 to -0.06) |
| RoD-lexical (control) | 0.50 | 0.604 | 0.604 | -0.229 (-0.40 to -0.06) |

**Primary: RoD vs StreamingLLM at keep 0.25: per-context deltas** (12 contexts): [0.5, 0.0, 0.25, 0.5, 0.25, 0.25, 0.75, 0.75, 0.5, 0.75, 0.0, 0.25]; questions where only RoD is right: 21, only the comparator: 2 (of 48).

**S7: RoD (keep 0.25) vs full cache: per-context deltas** (12 contexts): [-0.25, -0.5, -0.5, 0.25, -0.5, -0.5, 0.25, 0.0, -0.5, 0.0, -0.5, -0.25]; questions where only RoD is right: 3, only the comparator: 15 (of 48).

## Identity / plumbing checks (dev seed 100; Supervisor 16:24 spot-check)

`HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/identity_check.py 4` · context 4149 tokens, 4 questions

| Keep | B | Resident | Recall budget m (blocks) | Evicted tokens | I3 partition exact | I1 exact-KV assembly: max abs Δlogit, answers = full | I2 one-pass re-prefill: max abs ΔKV, answers = full |
|---|---|---|---|---|---|---|---|
| 0.10 | 415 | 185 | 2 | 3964 | True | 0.0053, 4/4 | 0.0254, 4/4 |
| 0.25 | 1037 | 496 | 7 | 3653 | True | 0.0059, 4/4 | 0.0234, 4/4 |
| 0.50 | 2074 | 1014 | 15 | 3135 | True | 0.0057, 4/4 | 0.0234, 4/4 |
| 1.00 | 4149 | 2052 | 32 | 2097 | True | 0.0055, 4/4 | 0.0234, 4/4 |

Positions, masks, cache assembly and block bookkeeping reproduce the full cache whenever the evicted KV is restored exactly or recomputed with its true prefix, so RoD's recall loss is not a plumbing artifact.

## RoD's transient scoring working set (analytic, T1 mean context)

| Keep | Recall blocks m | Evicted tokens E | Persistent store MiB | Transient scoring set MiB (unchunked upper bound) |
|---|---|---|---|---|
| 0.10 | 2 | 3940 | 7.1 | 88.5 |
| 0.25 | 7 | 3630 | 16.7 | 81.5 |
| 0.50 | 15 | 3115 | 32.6 | 70.0 |

The scorer materialises a dense fp32 copy of the sketch and fp32 question/window score tensors over all evicted keys. A streamed implementation (online softmax over key chunks; the window term precomputed per key at compression) bounds this to O(chunk). It is reported here so that no peak-memory-equality claim is implied.

## Memory accounting

Stored KV MiB = analytic bytes = layers × kv_heads × kept tokens × head_dim × 2 (K,V) × 2 B (fp16), plus quantisation scales/biases and, for RoD, the 4-bit sketch, 256 KiB of window queries and int32 token ids. The harness asserts that the full cache's measured tensor bytes equal T × 32 KiB. Answer-time MiB adds RoD's recalled blocks. CPU seconds are relative only.

