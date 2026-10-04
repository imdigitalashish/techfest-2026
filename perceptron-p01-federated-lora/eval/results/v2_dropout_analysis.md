# Dropout stretch analysis `v2` (auto-generated: `python -m eval.dropout_analysis --tag v2`)

Scenario `dropout`: device c4 (manpages) is offline in rounds 5–9 (1-based), on top of random offline rounds and deadline cut-offs. Status per round: o = full work, p = partial work accepted, x = cut off and discarded, - = offline. Untuned-model loss on its domain: **3.2330**.

| Strategy | seed | c4 status r1–r12 | manpages loss at evaluations | peak vs untuned | final vs untuned |
|---|---|---|---|---|---|
| anchor_full | 0 | `pppo-----oo-` | r3: 3.2143 · r6: 3.2025 · r9: 3.1988 · r12: 3.1942 | -0.0187 | -0.0388 |
| anchor_full | 1 | `op-o-----o--` | r3: 3.2100 · r6: 3.1971 · r9: 3.1966 · r12: 3.1886 | -0.0230 | -0.0443 |
| anchor_full | 2 | `oppo-----o-o` | r3: 3.2116 · r6: 3.2019 · r9: 3.1993 · r12: 3.1941 | -0.0214 | -0.0388 |
| fedavg_ab_homo | 0 | `xxxo-----oo-` | r3: 3.3037 · r6: 3.4059 · r9: 3.4818 · r12: 3.4183 | +0.2488 | +0.1854 |
| fedavg_ab_homo | 1 | `ox-o-----o--` | r3: 3.3124 · r6: 3.4156 · r9: 3.5172 · r12: 3.4574 | +0.2842 | +0.2244 |
| fedavg_ab_homo | 2 | `oxxo-----o-o` | r3: 3.3051 · r6: 3.4000 · r9: 3.5382 · r12: 3.4814 | +0.3052 | +0.2484 |
| ffa_lora | 0 | `xxxo-----oo-` | r3: 3.2388 · r6: 3.2666 · r9: 3.3001 · r12: 3.2995 | +0.0672 | +0.0665 |
| ffa_lora | 1 | `ox-o-----o--` | r3: 3.2361 · r6: 3.2700 · r9: 3.3010 · r12: 3.3136 | +0.0806 | +0.0806 |
| flexlora | 0 | `xxxo-----oo-` | r3: 3.3255 · r6: 3.4037 · r9: 3.4439 · r12: 3.4089 | +0.2109 | +0.1759 |
| flexlora | 1 | `ox-o-----o--` | r3: 3.3214 · r6: 3.3944 · r9: 3.4693 · r12: 3.4445 | +0.2363 | +0.2115 |

Rounds in which each device's work entered the aggregate (mean over seeds; + memory = rounds its last update was reused while absent):

| Strategy | c0 (wiki) | c1 (pycode) | c2 (cheaders) | c3 (readmes) | c4 (manpages) |
|---|---|---|---|---|---|
| anchor_full | 12.0 | 10.7 + 1.0 | 9.7 + 2.0 | 10.0 + 2.0 | 5.3 + 5.7 |
| fedavg_ab_homo | 12.0 | 9.3 | 6.0 | 7.7 | 3.3 |
| ffa_lora | 12.0 | 9.0 | 5.0 | 9.5 | 3.0 |
| flexlora | 12.0 | 9.0 | 5.0 | 9.5 | 3.0 |

Peak rise of the outage device's domain loss above the untuned model (mean over seeds): anchor_full -0.0210 (n=3); fedavg_ab_homo +0.2794 (n=3); ffa_lora +0.0739 (n=2); flexlora +0.2236 (n=2)

