# Dropout stretch analysis `v2` (auto-generated: `python -m eval.dropout_analysis --tag v2`)

Scenario `dropout`: device c4 (manpages) is offline in rounds 5–9 (1-based), on top of random offline rounds and deadline cut-offs. Status per round: o = full work, p = partial work accepted, x = cut off and discarded, - = offline. Untuned-model loss on its domain: **3.2330**.

| Strategy | seed | c4 status r1–r12 | manpages loss at evaluations | peak vs untuned | final vs untuned |
|---|---|---|---|---|---|
| anchor_full | 0 | `pppo-----oo-` | r3: 3.2143 · r6: 3.2025 · r9: 3.1988 · r12: 3.1942 | -0.0187 | -0.0388 |
| anchor_full | 1 | `op-o-----o--` | r3: 3.2100 · r6: 3.1971 · r9: 3.1966 · r12: 3.1886 | -0.0230 | -0.0443 |
| anchor_full | 2 | `oppo-----o-o` | r3: 3.2116 · r6: 3.2019 · r9: 3.1993 · r12: 3.1941 | -0.0214 | -0.0388 |
| anchor_full | 3 | `pop------o-o` | r3: 3.2143 · r6: 3.2013 · r9: 3.2016 · r12: 3.1956 | -0.0187 | -0.0374 |
| anchor_full | 4 | `ooop-----o-p` | r3: 3.2139 · r6: 3.2033 · r9: 3.2011 · r12: 3.1945 | -0.0191 | -0.0384 |
| fedavg_ab_homo | 0 | `xxxo-----oo-` | r3: 3.3037 · r6: 3.4059 · r9: 3.4818 · r12: 3.4183 | +0.2488 | +0.1854 |
| fedavg_ab_homo | 1 | `ox-o-----o--` | r3: 3.3124 · r6: 3.4156 · r9: 3.5172 · r12: 3.4574 | +0.2842 | +0.2244 |
| fedavg_ab_homo | 2 | `oxxo-----o-o` | r3: 3.3051 · r6: 3.4000 · r9: 3.5382 · r12: 3.4814 | +0.3052 | +0.2484 |
| fedavg_ab_homo | 3 | `xox------o-o` | r3: 3.3137 · r6: 3.4288 · r9: 3.5339 · r12: 3.4448 | +0.3009 | +0.2118 |
| fedavg_ab_homo | 4 | `ooox-----o-x` | r3: 3.3006 · r6: 3.3860 · r9: 3.4469 · r12: 3.4807 | +0.2477 | +0.2477 |
| ffa_lora | 0 | `xxxo-----oo-` | r3: 3.2388 · r6: 3.2666 · r9: 3.3001 · r12: 3.2995 | +0.0672 | +0.0665 |
| ffa_lora | 1 | `ox-o-----o--` | r3: 3.2361 · r6: 3.2700 · r9: 3.3010 · r12: 3.3136 | +0.0806 | +0.0806 |
| ffa_lora | 2 | `oxxo-----o-o` | r3: 3.2346 · r6: 3.2565 · r9: 3.2983 · r12: 3.3057 | +0.0727 | +0.0727 |
| ffa_lora | 3 | `xox------o-o` | r3: 3.2370 · r6: 3.2714 · r9: 3.3067 · r12: 3.3178 | +0.0848 | +0.0848 |
| ffa_lora | 4 | `ooox-----o-x` | r3: 3.2353 · r6: 3.2625 · r9: 3.2932 · r12: 3.3083 | +0.0753 | +0.0753 |
| flexlora | 0 | `xxxo-----oo-` | r3: 3.3255 · r6: 3.4037 · r9: 3.4439 · r12: 3.4089 | +0.2109 | +0.1759 |
| flexlora | 1 | `ox-o-----o--` | r3: 3.3214 · r6: 3.3944 · r9: 3.4693 · r12: 3.4445 | +0.2363 | +0.2115 |
| flexlora | 2 | `oxxo-----o-o` | r3: 3.3122 · r6: 3.3760 · r9: 3.4981 · r12: 3.4582 | +0.2651 | +0.2252 |
| flexlora | 3 | `xox------o-o` | r3: 3.3148 · r6: 3.4019 · r9: 3.4761 · r12: 3.4503 | +0.2432 | +0.2174 |
| flexlora | 4 | `ooox-----o-x` | r3: 3.3118 · r6: 3.3692 · r9: 3.4193 · r12: 3.4424 | +0.2094 | +0.2094 |

Rounds in which each device's work entered the aggregate (mean over seeds; + memory = rounds its last update was reused while absent):

| Strategy | c0 (wiki) | c1 (pycode) | c2 (cheaders) | c3 (readmes) | c4 (manpages) |
|---|---|---|---|---|---|
| anchor_full | 12.0 | 10.6 + 1.2 | 10.0 + 1.8 | 10.4 + 1.6 | 5.4 + 5.4 |
| fedavg_ab_homo | 12.0 | 9.0 | 6.4 | 8.4 | 3.4 |
| ffa_lora | 12.0 | 9.0 | 6.4 | 8.4 | 3.4 |
| flexlora | 12.0 | 9.0 | 6.4 | 8.4 | 3.4 |

Peak rise of the outage device's domain loss above the untuned model (mean over seeds): anchor_full -0.0202 (n=5); fedavg_ab_homo +0.2774 (n=5); ffa_lora +0.0761 (n=5); flexlora +0.2330 (n=5)

