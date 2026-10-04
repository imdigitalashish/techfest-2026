# Results `v2` (auto-generated: `python -m eval.summarize --tag v2`)

## Scenario `dropout` (`v2_dropout.jsonl`)

HuggingFaceTB/SmolLM2-135M, LoRA on q_proj, v_proj, r_max 16, α 32.0, 12 rounds, batch 4×128, lr 0.001. Untuned model: macro **2.7063**, micro 3.2463. Code: `046b2cdabf9a, 3e3ba2b4f5ff, 5f9586f5fb62, d2fb92971156`. Loss = next-token cross-entropy (nats/token) on held-out blocks.

Provenance (commit · code_sha · data_digest · model_revision) per strategy: anchor_full: 0e6aead·3e3ba2b4f5ff·n/a·n/a, 2d3bf42·5f9586f5fb62·n/a·n/a, 8514bea·046b2cdabf9a·n/a·n/a; fedavg_ab_homo: 0e6aead·3e3ba2b4f5ff·n/a·n/a, 8514bea·d2fb92971156·n/a·n/a, 92d5b7e·5f9586f5fb62·n/a·n/a; ffa_lora: 8514bea·d2fb92971156·n/a·n/a, 92d5b7e·5f9586f5fb62·n/a·n/a; flexlora: 2d3bf42·5f9586f5fb62·n/a·n/a, 7653f0a·3e3ba2b4f5ff·n/a·n/a. Different code hashes are accepted only because `git diff` between them touches analysis scripts and new strategy registrations, and reruns across revisions are bit-identical (thought node 11:45).

Columns: macro = mean domain loss; micro = data-volume-weighted loss (the objective n_k-weighted FedAvg optimises); c0 share (proj.) = <c_0,P>/‖P‖² (unbounded); c0 share (norm) = ‖c_0‖/Σ‖c_j‖ (bounded, fair share 0.2); agg. error = ‖P−Σc_k‖/‖Σc_k‖ of the full update; max spike = largest rise between evaluations every 3 rounds; upload = logical fp32 uplink only.

| Strategy | n | macro ↓ (mean ± sd) | Δ macro vs starter, 95 % CI | worst domain ↓ | micro ↓ | c0 share (proj.) | c0 share (norm) | agg. error | max spike | upload MB / device |
|---|---|---|---|---|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 3 | 2.7476 ± 0.0112 | — | 3.4524 | 3.0483 | 1.018 | 0.885 | 5.7 % | 0.0601 | 14.13 |
| FFA-LoRA (ICLR 2024): frozen A, FedAvg on B, rank 8 | 2 | 2.7164 ± 0.0031 | -0.0276 [-0.1196, +0.0643] | 3.4040 | 3.1175 | 0.992 | 0.884 | 0.0 % | 0.0192 | 5.68 |
| FlexLoRA (arXiv 2402.11505): product average + SVD, device ranks | 2 | 2.7448 ± 0.0120 | +0.0008 [-0.0110, +0.0125] | 3.4267 | 3.0500 | 0.947 | 0.801 | 0.0 % (served trunc. 0.5 %) | 0.0321 | 14.52 |
| **AnchorLoRA (ours)** | 3 | 2.6649 ± 0.0003 | -0.0827 [-0.1109, -0.0544] | 3.5142 | 3.1604 | 0.216 | 0.216 | 0.0 % | 0.0000 | 6.59 |

**AnchorLoRA vs each baseline** (paired by seed; Δ = AnchorLoRA − baseline; negative = AnchorLoRA better):

| Baseline | shared seeds | Δ macro, 95 % CI | Δ worst domain, 95 % CI | Δ micro, 95 % CI | Δ per seed (macro) |
|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 0,1,2 | -0.0827 [-0.1109, -0.0544] | +0.0619 [-0.0208, +0.1445] | +0.1121 [+0.0974, +0.1268] | s0: -0.0696, s1: -0.0884, s2: -0.0900 |
| FFA-LoRA (ICLR 2024): frozen A, FedAvg on B, rank 8 | 0,1 | -0.0513 [-0.0791, -0.0236] | +0.1113 [+0.0810, +0.1415] | +0.0435 [+0.0143, +0.0727] | s0: -0.0492, s1: -0.0535 |
| FlexLoRA (arXiv 2402.11505): product average + SVD, device ranks | 0,1 | -0.0798 [-0.1877, +0.0282] | +0.0886 [-0.1371, +0.3143] | +0.1111 [+0.0129, +0.2092] | s0: -0.0713, s1: -0.0882 |

**Per-domain gain vs the untuned model** (untuned − final, nats/token; mean [marginal 95 % CI] over seeds; device data volume: wiki 2400, pycode 300, cheaders 300, readmes 300, manpages 300 blocks). Last column: domains whose lower bound is > 0, marginal / Bonferroni-simultaneous over the 5 domains (exploratory; the pre-specified primary comparison is the paired macro Δ vs the starter):

| Strategy | wiki | pycode | cheaders | readmes | manpages | domains > 0 (marg. / Bonf.) |
|---|---|---|---|---|---|---|
| fedavg_ab_homo | +0.369 [+0.347, +0.391] | -0.124 [-0.148, -0.100] | -0.106 [-0.119, -0.093] | -0.126 [-0.162, -0.091] | -0.219 [-0.298, -0.140] | 1 / 1 of 5 |
| ffa_lora | +0.228 [+0.197, +0.259] | -0.089 [-0.100, -0.078] | -0.063 [-0.075, -0.052] | -0.053 [-0.072, -0.034] | -0.074 [-0.163, +0.016] | 1 / 1 of 5 |
| flexlora | +0.364 [+0.272, +0.456] | -0.131 [-0.198, -0.064] | -0.105 [-0.128, -0.082] | -0.127 [-0.305, +0.051] | -0.194 [-0.420, +0.033] | 1 / 0 of 5 |
| anchor_full | +0.118 [+0.113, +0.122] | +0.014 [+0.012, +0.016] | +0.007 [+0.003, +0.011] | +0.027 [+0.022, +0.032] | +0.041 [+0.033, +0.049] | 5 / 4 of 5 |

**Per-domain paired Δ, AnchorLoRA − starter** (negative = AnchorLoRA better):

| wiki | pycode | cheaders | readmes | manpages |
|---|---|---|---|---|
| +0.251 [+0.233, +0.269] | -0.138 [-0.161, -0.116] | -0.113 [-0.121, -0.104] | -0.154 [-0.190, -0.118] | -0.260 [-0.341, -0.179] |

