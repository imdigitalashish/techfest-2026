# E10_replication_test: pre-registered attribution (eval/preregistration.md, E8)

n = 400 validation seeds (1260–1659), synced twins. Integrity: pre-window identical True, all filled True. Values: mean in bps with 95% paired-bootstrap CI.

| arm | ΔIS vs TWAP | Δown impact | Δinstant | Δdrift |
|---|---|---|---|---|
| QP_only | -0.0126 [-0.0292, +0.0027] | -0.0139 [-0.0294, +0.0002] | +0.0035 [+0.0004, +0.0065] | -0.0022 [-0.0071, +0.0027] |
| TWAP_legacy_fb | -0.0016 [-0.0153, +0.0114] | -0.0016 [-0.0150, +0.0113] | -0.0003 [-0.0033, +0.0024] | +0.0003 [-0.0019, +0.0024] |
| IA_sched_only | -0.0127 [-0.0285, +0.0026] | -0.0148 [-0.0294, -0.0011] | +0.0045 [+0.0017, +0.0073] | -0.0023 [-0.0074, +0.0028] |
| IA_sched_fixed | -0.0150 [-0.0313, +0.0007] | -0.0188 [-0.0336, -0.0046] | +0.0057 [+0.0028, +0.0089] | -0.0019 [-0.0071, +0.0032] |

| contrast | IS | own impact | instant | drift |
|---|---|---|---|---|
| A_qp_main | -0.0118 [-0.0247, +0.0006] | -0.0136 [-0.0252, -0.0022] | +0.0041 [+0.0019, +0.0065] | -0.0024 [-0.0073, +0.0025] |
| B_frontload_main | -0.0008 [-0.0096, +0.0078] | -0.0013 [-0.0095, +0.0069] | +0.0003 [-0.0017, +0.0022] | +0.0001 [-0.0019, +0.0021] |
| C_interaction | +0.0016 [-0.0162, +0.0199] | +0.0007 [-0.0168, +0.0188] | +0.0012 [-0.0024, +0.0052] | -0.0004 [-0.0014, +0.0005] |
| D_fixed_feedback | -0.0024 [-0.0132, +0.0086] | -0.0049 [-0.0152, +0.0055] | +0.0022 [-0.0004, +0.0052] | +0.0003 [-0.0004, +0.0011] |

**Amendment A1 labels** (signed; 'negligible' = CI within ±0.02 bps):

| contrast | IS | own impact |
|---|---|---|
| A_qp_main | unresolved | detected (−) |
| B_frontload_main | negligible | negligible |
| C_interaction | negligible | negligible |
| D_fixed_feedback | negligible | negligible |

Legacy classifier (pre-A1; not used in deliverables): IS → unattributed at this n; own impact → QP schedule.
