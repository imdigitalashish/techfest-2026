# Dropout stretch analysis `v1` (auto-generated: `python -m eval.dropout_analysis --tag v1`)

Scenario `dropout`: device c4 (manpages) is offline in rounds 5–9 (1-based), on top of random offline rounds and deadline cut-offs. Status per round: o = full work, p = partial work accepted, x = cut off and discarded, - = offline. Untuned-model loss on its domain: **3.2330**.

| Strategy | seed | c4 status r1–r12 | manpages loss at evaluations | peak vs untuned | final vs untuned |
|---|---|---|---|---|---|
| anchor_full | 0 | `pppo-----oo-` | r3: 3.2143 · r6: 3.2025 · r9: 3.1988 · r12: 3.1942 | -0.0187 | -0.0388 |
| anchor_full | 1 | `op-o-----o--` | r3: 3.2100 · r6: 3.1971 · r9: 3.1966 · r12: 3.1886 | -0.0230 | -0.0443 |
| anchor_full | 2 | `oppo-----o-o` | r3: 3.2116 · r6: 3.2019 · r9: 3.1993 · r12: 3.1941 | -0.0214 | -0.0388 |
| anchor_naive | 0 | `xxxo-----oo-` | r3: 3.2745 · r6: 3.3258 · r9: 3.3835 · r12: 3.3847 | +0.1517 | +0.1517 |
| fedavg_ab_het | 0 | `xxxo-----oo-` | r3: 3.2803 · r6: 3.3582 · r9: 3.5322 · r12: 3.3599 | +0.2992 | +0.1269 |
| fedavg_ab_homo | 0 | `xxxo-----oo-` | r3: 3.3037 · r6: 3.4059 · r9: 3.4818 · r12: 3.4183 | +0.2488 | +0.1854 |
| fedavg_ab_homo | 1 | `ox-o-----o--` | r3: 3.3124 · r6: 3.4156 · r9: 3.5172 · r12: 3.4574 | +0.2842 | +0.2244 |

Rounds in which each device's work entered the aggregate (mean over seeds; + memory = rounds its last update was reused while absent):

| Strategy | c0 (wiki) | c1 (pycode) | c2 (cheaders) | c3 (readmes) | c4 (manpages) |
|---|---|---|---|---|---|
| anchor_full | 12.0 | 10.7 + 1.0 | 9.7 + 2.0 | 10.0 + 2.0 | 5.3 + 5.7 |
| anchor_naive | 12.0 | 9.0 | 5.0 | 9.0 | 3.0 |
| fedavg_ab_het | 12.0 | 9.0 | 5.0 | 9.0 | 3.0 |
| fedavg_ab_homo | 12.0 | 9.0 | 5.0 | 9.5 | 3.0 |

Peak rise of the outage device's domain loss above the untuned model (mean over seeds): anchor_full -0.0210 (n=3); anchor_naive +0.1517 (n=1); fedavg_ab_het +0.2992 (n=1); fedavg_ab_homo +0.2665 (n=2)

