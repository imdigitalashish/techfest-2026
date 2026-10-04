# Results `v2` (auto-generated: `python -m eval.summarize --tag v2`)

## Scenario `dropout` (`v2_dropout.jsonl`)

HuggingFaceTB/SmolLM2-135M, LoRA on q_proj, v_proj, r_max 16, α 32.0, 12 rounds, batch 4×128, lr 0.001. Untuned model: macro **2.7063**, micro 3.2463. Code: `046b2cdabf9a, 21f6f0e3f351, 3e3ba2b4f5ff, 5f9586f5fb62, d2fb92971156`. Loss = next-token cross-entropy (nats/token) on held-out blocks.

Provenance (commit · code_sha · data_digest · model_revision) per strategy: anchor_full: 0e6aead·3e3ba2b4f5ff·n/a·n/a, 2d3bf42·5f9586f5fb62·n/a·n/a, 8514bea·046b2cdabf9a·n/a·n/a, e9c4a2c·21f6f0e3f351·cb0a1228cf1b·93efa2f097d5; fedavg_ab_homo: 0e6aead·3e3ba2b4f5ff·n/a·n/a, 8514bea·d2fb92971156·n/a·n/a, 92d5b7e·5f9586f5fb62·n/a·n/a, e9c4a2c·21f6f0e3f351·cb0a1228cf1b·93efa2f097d5; ffa_lora: 8514bea·d2fb92971156·n/a·n/a, 92d5b7e·5f9586f5fb62·n/a·n/a, c20275f·21f6f0e3f351·cb0a1228cf1b·93efa2f097d5, e9c4a2c·21f6f0e3f351·cb0a1228cf1b·93efa2f097d5; flexlora: 2d3bf42·5f9586f5fb62·n/a·n/a, 7653f0a·3e3ba2b4f5ff·n/a·n/a, e9c4a2c·21f6f0e3f351·cb0a1228cf1b·93efa2f097d5. Different code hashes are accepted only because `git diff` between them touches analysis scripts and new strategy registrations, and reruns across revisions are bit-identical (thought node 11:45).

Columns: macro = mean domain loss; micro = data-volume-weighted loss (the objective n_k-weighted FedAvg optimises); c0 share (proj.) = <c_0,P>/‖P‖² (unbounded); c0 share (norm) = ‖c_0‖/Σ‖c_j‖ (bounded, fair share 0.2); agg. error = ‖P−Σc_k‖/‖Σc_k‖ of the full update; max spike = largest rise between evaluations every 3 rounds; upload = logical fp32 uplink only.

| Strategy | n | macro ↓ (mean ± sd) | Δ macro vs starter, 95 % CI | worst domain ↓ | micro ↓ | c0 share (proj.) | c0 share (norm) | agg. error | max spike | upload MB / device |
|---|---|---|---|---|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 5 | 2.7467 ± 0.0095 | — | 3.4565 | 3.0442 | 1.019 | 0.883 | 5.8 % | 0.0601 | 14.45 |
| FFA-LoRA (ICLR 2024): frozen A, FedAvg on B, rank 8 | 5 | 2.7148 ± 0.0024 | -0.0319 [-0.0438, -0.0200] | 3.3976 | 3.1131 | 0.993 | 0.879 | 0.0 % | 0.0193 | 5.78 |
| FlexLoRA (arXiv 2402.11505): product average + SVD, device ranks | 5 | 2.7478 ± 0.0068 | +0.0011 [-0.0072, +0.0094] | 3.4409 | 3.0445 | 0.948 | 0.800 | 0.0 % (served trunc. 0.5 %) | 0.0557 | 14.75 |
| **AnchorLoRA (ours)** | 5 | 2.6653 ± 0.0008 | -0.0815 [-0.0930, -0.0700] | 3.5133 | 3.1599 | 0.215 | 0.215 | 0.0 % | 0.0000 | 6.62 |

**AnchorLoRA vs each baseline** (paired by seed; Δ = AnchorLoRA − baseline; negative = AnchorLoRA better):

| Baseline | shared seeds | Δ macro, 95 % CI | Δ worst domain, 95 % CI | Δ micro, 95 % CI | Δ per seed (macro) |
|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 0,1,2,3,4 | -0.0815 [-0.0930, -0.0700] | +0.0567 [+0.0243, +0.0892] | +0.1158 [+0.1074, +0.1241] | s0: -0.0696, s1: -0.0884, s2: -0.0900, s3: -0.0736, s4: -0.0859 |
| FFA-LoRA (ICLR 2024): frozen A, FedAvg on B, rank 8 | 0,1,2,3,4 | -0.0496 [-0.0531, -0.0461] | +0.1156 [+0.1093, +0.1219] | +0.0468 [+0.0418, +0.0518] | s0: -0.0492, s1: -0.0535, s2: -0.0492, s3: -0.0504, s4: -0.0457 |
| FlexLoRA (arXiv 2402.11505): product average + SVD, device ranks | 0,1,2,3,4 | -0.0826 [-0.0913, -0.0739] | +0.0724 [+0.0463, +0.0985] | +0.1154 [+0.1049, +0.1259] | s0: -0.0713, s1: -0.0882, s2: -0.0873, s3: -0.0857, s4: -0.0805 |

**Per-domain gain vs the untuned model** (untuned − final, nats/token; mean [marginal 95 % CI] over seeds; device data volume: wiki 2400, pycode 300, cheaders 300, readmes 300, manpages 300 blocks). Last column: domains whose lower bound is > 0, marginal / Bonferroni-simultaneous over the 5 domains (exploratory; the pre-specified primary comparison is the paired macro Δ vs the starter):

| Strategy | wiki | pycode | cheaders | readmes | manpages | domains > 0 (marg. / Bonf.) |
|---|---|---|---|---|---|---|
| fedavg_ab_homo | +0.375 [+0.362, +0.389] | -0.128 [-0.139, -0.116] | -0.103 [-0.110, -0.095] | -0.123 [-0.141, -0.106] | -0.224 [-0.256, -0.191] | 1 / 1 of 5 |
| ffa_lora | +0.234 [+0.226, +0.243] | -0.090 [-0.094, -0.086] | -0.060 [-0.066, -0.054] | -0.051 [-0.054, -0.048] | -0.076 [-0.085, -0.067] | 1 / 1 of 5 |
| flexlora | +0.376 [+0.360, +0.391] | -0.139 [-0.150, -0.128] | -0.108 [-0.113, -0.102] | -0.129 [-0.142, -0.116] | -0.208 [-0.231, -0.184] | 1 / 1 of 5 |
| anchor_full | +0.119 [+0.113, +0.124] | +0.013 [+0.011, +0.016] | +0.006 [+0.004, +0.009] | +0.027 [+0.025, +0.029] | +0.040 [+0.036, +0.043] | 5 / 5 of 5 |

**Per-domain paired Δ, AnchorLoRA − starter** (negative = AnchorLoRA better):

| wiki | pycode | cheaders | readmes | manpages |
|---|---|---|---|---|
| +0.257 [+0.243, +0.270] | -0.141 [-0.152, -0.130] | -0.109 [-0.116, -0.103] | -0.150 [-0.168, -0.133] | -0.263 [-0.296, -0.230] |

