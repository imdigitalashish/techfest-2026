# E8_ablation_val: pre-registered attribution (eval/preregistration.md, E8)

n = 100 validation seeds (100–199), synced twins. Integrity: pre-window identical True, all filled True. Values: mean in bps with 95% paired-bootstrap CI.

| arm | ΔIS vs TWAP | Δown impact | Δinstant | Δdrift |
|---|---|---|---|---|
| QP_only | -0.0077 [-0.0423, +0.0280] | -0.0101 [-0.0402, +0.0202] | +0.0021 [-0.0045, +0.0106] | +0.0003 [-0.0111, +0.0117] |
| TWAP_legacy_fb | -0.0062 [-0.0336, +0.0215] | -0.0062 [-0.0334, +0.0214] | -0.0024 [-0.0077, +0.0026] | +0.0024 [-0.0032, +0.0085] |
| IA_sched_only | +0.0056 [-0.0284, +0.0393] | +0.0005 [-0.0315, +0.0322] | +0.0019 [-0.0038, +0.0081] | +0.0033 [-0.0092, +0.0153] |
| IA_sched_fixed | -0.0199 [-0.0532, +0.0128] | -0.0224 [-0.0505, +0.0062] | -0.0006 [-0.0071, +0.0061] | +0.0031 [-0.0085, +0.0144] |

| contrast | IS | own impact | instant | drift |
|---|---|---|---|---|
| A_qp_main | +0.0020 [-0.0252, +0.0295] | -0.0017 [-0.0254, +0.0218] | +0.0032 [-0.0016, +0.0090] | +0.0006 [-0.0107, +0.0119] |
| B_frontload_main | +0.0036 [-0.0188, +0.0256] | +0.0022 [-0.0189, +0.0232] | -0.0013 [-0.0064, +0.0034] | +0.0027 [-0.0028, +0.0088] |
| C_interaction | +0.0194 [-0.0175, +0.0548] | +0.0167 [-0.0179, +0.0497] | +0.0021 [-0.0070, +0.0110] | +0.0006 [-0.0000, +0.0016] |
| D_fixed_feedback | -0.0122 [-0.0388, +0.0116] | -0.0123 [-0.0354, +0.0092] | -0.0027 [-0.0110, +0.0046] | +0.0028 [-0.0003, +0.0077] |

**Amendment A1 labels** (signed; 'negligible' = CI within ±0.02 bps):

| contrast | IS | own impact |
|---|---|---|
| A_qp_main | unresolved | unresolved |
| B_frontload_main | unresolved | unresolved |
| C_interaction | unresolved | unresolved |
| D_fixed_feedback | unresolved | unresolved |

Legacy classifier (pre-A1; not used in deliverables): IS → unattributed at this n; own impact → unattributed at this n.
