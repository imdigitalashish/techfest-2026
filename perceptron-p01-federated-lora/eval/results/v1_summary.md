# Results `v1` (auto-generated: `python -m eval.summarize --tag v1`)

## Scenario `clean` (`v1_clean.jsonl`)

HuggingFaceTB/SmolLM2-135M, LoRA on q_proj, v_proj, r_max 16, α 32.0, 12 rounds, batch 4×128, lr 0.001. Untuned model: macro **2.7063**, micro 3.2463. Code: `n/a`. Loss = next-token cross-entropy (nats/token) on held-out blocks.

| Strategy | n | macro ↓ (mean ± sd) | Δ macro vs starter, 95 % CI | worst domain ↓ | micro ↓ | c0 share (proj.) | c0 share (norm) | agg. error | max spike | upload MB / device |
|---|---|---|---|---|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 1 | 2.6995 ± 0.0000 | — | 3.3334 | 3.0347 | 1.032 | 0.000 | 8.8 % | 0.0138 | 22.12 |
| HetLoRA-style: FedAvg on A,B, zero-padded device ranks | 1 | 2.6873 ± 0.0000 | -0.0122 | 3.3059 | 3.0481 | 1.246 | 0.000 | 36.2 % | 0.0042 | 18.80 |
| Ablation: frozen shared A + device ranks, n_k weights only | 1 | 2.7427 ± 0.0000 | +0.0432 | 3.3747 | 3.1113 | 0.994 | 0.000 | 0.0 % | 0.0215 | 7.52 |

**AnchorLoRA vs each baseline** (paired by seed; Δ = AnchorLoRA − baseline; negative = AnchorLoRA better):

| Baseline | shared seeds | Δ macro, 95 % CI | Δ worst domain, 95 % CI | Δ micro, 95 % CI | Δ per seed (macro) |
|---|---|---|---|---|---|

**Per-domain gain vs the untuned model** (untuned − final, nats/token; mean [95 % CI] over seeds; device data volume: wiki 2400, pycode 300, cheaders 300, readmes 300, manpages 300 blocks):

| Strategy | wiki | pycode | cheaders | readmes | manpages | domains with CI > 0 |
|---|---|---|---|---|---|---|
| fedavg_ab_homo | +0.358 | -0.082 | -0.066 | -0.075 | -0.100 | — / 5 |
| fedavg_ab_het | +0.326 | -0.064 | -0.050 | -0.045 | -0.073 | — / 5 |
| anchor_naive | +0.257 | -0.129 | -0.095 | -0.093 | -0.121 | — / 5 |

## Scenario `dropout` (`v1_dropout.jsonl`)

HuggingFaceTB/SmolLM2-135M, LoRA on q_proj, v_proj, r_max 16, α 32.0, 12 rounds, batch 4×128, lr 0.001. Untuned model: macro **2.7063**, micro 3.2463. Code: `n/a`. Loss = next-token cross-entropy (nats/token) on held-out blocks.

| Strategy | n | macro ↓ (mean ± sd) | Δ macro vs starter, 95 % CI | worst domain ↓ | micro ↓ | c0 share (proj.) | c0 share (norm) | agg. error | max spike | upload MB / device |
|---|---|---|---|---|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 3 | 2.7476 ± 0.0112 | — | 3.4524 | 3.0483 | 1.018 | 0.000 | 5.7 % | 0.0601 | 14.13 |
| HetLoRA-style: FedAvg on A,B, zero-padded device ranks | 1 | 2.7046 ± 0.0000 | -0.0301 | 3.3599 | 3.0438 | 1.040 | 0.000 | 25.4 % | 0.0942 | 14.47 |
| Ablation: frozen shared A + device ranks, n_k weights only | 1 | 2.7616 ± 0.0000 | +0.0270 | 3.3847 | 3.1138 | 0.996 | 0.000 | 0.0 % | 0.0350 | 5.79 |
| **AnchorLoRA (ours)** | 3 | 2.6649 ± 0.0003 | -0.0827 [-0.1109, -0.0544] | 3.5142 | 3.1604 | 0.216 | 0.000 | 0.0 % | 0.0000 | 6.59 |

**AnchorLoRA vs each baseline** (paired by seed; Δ = AnchorLoRA − baseline; negative = AnchorLoRA better):

| Baseline | shared seeds | Δ macro, 95 % CI | Δ worst domain, 95 % CI | Δ micro, 95 % CI | Δ per seed (macro) |
|---|---|---|---|---|---|
| Starter: FedAvg on A,B, rank 8 everywhere | 0,1,2 | -0.0827 [-0.1109, -0.0544] | +0.0619 [-0.0208, +0.1445] | +0.1121 [+0.0974, +0.1268] | s0: -0.0696, s1: -0.0884, s2: -0.0900 |
| HetLoRA-style: FedAvg on A,B, zero-padded device ranks | 0 | -0.0395 | +0.1554 | +0.1172 | s0: -0.0395 |
| Ablation: frozen shared A + device ranks, n_k weights only | 0 | -0.0966 | +0.1305 | +0.0472 | s0: -0.0966 |

**Per-domain gain vs the untuned model** (untuned − final, nats/token; mean [95 % CI] over seeds; device data volume: wiki 2400, pycode 300, cheaders 300, readmes 300, manpages 300 blocks):

| Strategy | wiki | pycode | cheaders | readmes | manpages | domains with CI > 0 |
|---|---|---|---|---|---|---|
| fedavg_ab_homo | +0.369 [+0.347, +0.391] | -0.124 [-0.148, -0.100] | -0.106 [-0.119, -0.093] | -0.126 [-0.162, -0.091] | -0.219 [-0.298, -0.140] | 1 / 5 |
| fedavg_ab_het | +0.346 | -0.080 | -0.067 | -0.063 | -0.127 | — / 5 |
| anchor_naive | +0.267 | -0.157 | -0.118 | -0.117 | -0.152 | — / 5 |
| anchor_full | +0.118 [+0.113, +0.122] | +0.014 [+0.012, +0.016] | +0.007 [+0.003, +0.011] | +0.027 [+0.022, +0.032] | +0.041 [+0.033, +0.049] | 5 / 5 |

**Per-domain paired Δ, AnchorLoRA − starter** (negative = AnchorLoRA better):

| wiki | pycode | cheaders | readmes | manpages |
|---|---|---|---|---|
| +0.251 [+0.233, +0.269] | -0.138 [-0.161, -0.116] | -0.113 [-0.121, -0.104] | -0.154 [-0.190, -0.118] | -0.260 [-0.341, -0.179] |

