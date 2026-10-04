# Simulator bank v0 — results (SYNTHETIC data, exact ground truth)

Reproduce: `.venv/bin/python eval/run_sim_bank.py --seeds 30` (from `perceptron-p03-off-policy-eval/`).

Policy effect = V_after(new, as deployed) − V_after(old): what the switch did, on the same after-period traffic.

## S1_drift_masks_gain
Truth: V_before(old)=0.3435 · V_after(new)=0.2886 · V_after(old)=0.2133 · **policy effect=+0.0752** · expected naive=-0.0549 · mix=+0.0162 · drift=-0.1464 · Γ_true=1.00
Naive before/after: mean -0.0558 (sd 0.0061); sign matches truth in 0% of seeds; RMSE vs policy effect 0.1311

| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |
|---|---|---|---|---|---|---|---|
| IPW | +0.0748 | -0.0005 | 0.0064 | 0.97 | 0.0240 | 100% | 3159 |
| SNIPW | +0.0747 | -0.0006 | 0.0062 | 0.93 | 0.0219 | 100% | 3159 |
| DM | +0.0743 | -0.0010 | 0.0046 | 0.97 | 0.0173 | 100% | 3159 |
| DR | +0.0748 | -0.0004 | 0.0058 | 0.93 | 0.0210 | 100% | 3159 |
| SwitchDR | +0.0754 | +0.0001 | 0.0048 | 0.93 | 0.0164 | 100% | 3159 |

Decomposition (DR policy term + DM mix/drift split): mix̂ +0.0156 vs true +0.0162; drift̂ -0.1463 vs true -0.1464

## S2_drift_fakes_gain
Truth: V_before(old)=0.4333 · V_after(new)=0.5226 · V_after(old)=0.6063 · **policy effect=-0.0837** · expected naive=+0.0893 · mix=-0.0001 · drift=+0.1731 · Γ_true=1.00
Naive before/after: mean +0.0892 (sd 0.0061); sign matches truth in 0% of seeds; RMSE vs policy effect 0.1731

| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |
|---|---|---|---|---|---|---|---|
| IPW | -0.0841 | -0.0004 | 0.0096 | 0.97 | 0.0370 | 100% | 4477 |
| SNIPW | -0.0826 | +0.0012 | 0.0052 | 0.90 | 0.0199 | 100% | 4477 |
| DM | -0.0809 | +0.0028 | 0.0047 | 0.93 | 0.0193 | 100% | 4477 |
| DR | -0.0822 | +0.0016 | 0.0048 | 0.93 | 0.0186 | 100% | 4477 |
| SwitchDR | -0.0814 | +0.0023 | 0.0052 | 0.90 | 0.0180 | 100% | 4477 |

Decomposition (DR policy term + DM mix/drift split): mix̂ -0.0006 vs true -0.0001; drift̂ +0.1720 vs true +0.1731

## S3_stationary_control
Truth: V_before(old)=0.3435 · V_after(new)=0.4592 · V_after(old)=0.3436 · **policy effect=+0.1156** · expected naive=+0.1157 · mix=+0.0001 · drift=+0.0000 · Γ_true=1.00
Naive before/after: mean +0.1169 (sd 0.0067); sign matches truth in 100% of seeds; RMSE vs policy effect 0.0067

| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |
|---|---|---|---|---|---|---|---|
| IPW | +0.1169 | +0.0014 | 0.0066 | 0.90 | 0.0251 | 100% | 3768 |
| SNIPW | +0.1154 | -0.0001 | 0.0073 | 0.87 | 0.0220 | 100% | 3768 |
| DM | +0.1142 | -0.0014 | 0.0046 | 0.97 | 0.0191 | 100% | 3768 |
| DR | +0.1153 | -0.0002 | 0.0058 | 0.93 | 0.0207 | 100% | 3768 |
| SwitchDR | +0.1152 | -0.0003 | 0.0051 | 0.93 | 0.0179 | 100% | 3768 |

Decomposition (DR policy term + DM mix/drift split): mix̂ -0.0006 vs true +0.0001; drift̂ +0.0022 vs true +0.0000

## S4_hidden_override
Truth: V_before(old)=0.3813 · V_after(new)=0.4151 · V_after(old)=0.3324 · **policy effect=+0.0827** · expected naive=+0.0338 · mix=+0.0001 · drift=-0.0489 · Γ_true=6.94
Naive before/after: mean +0.0330 (sd 0.0062); sign matches truth in 100% of seeds; RMSE vs policy effect 0.0501

| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |
|---|---|---|---|---|---|---|---|
| IPW | +0.0097 | -0.0730 | 0.0732 | 0.00 | 0.0224 | 97% | 5734 |
| SNIPW | +0.0170 | -0.0656 | 0.0658 | 0.00 | 0.0167 | 100% | 5734 |
| DM | +0.0138 | -0.0689 | 0.0690 | 0.00 | 0.0188 | 100% | 5734 |
| DR | +0.0140 | -0.0686 | 0.0688 | 0.00 | 0.0166 | 100% | 5734 |
| SwitchDR | +0.0140 | -0.0687 | 0.0689 | 0.00 | 0.0158 | 100% | 5734 |

Decomposition (DR policy term + DM mix/drift split): mix̂ -0.0006 vs true +0.0001; drift̂ +0.0195 vs true -0.0489
MSM (Hajek, joint bootstrap B=100, 10 seeds): truth inside bounds at Γ ≥ Γ_true in 100%; Γ* (interval first contains 0): median 1.25 (10/10 seeds reach 0 within Γ ≤ 10.0)

## S5_low_overlap
Truth: V_before(old)=0.2926 · V_after(new)=0.5160 · V_after(old)=0.2492 · **policy effect=+0.2667** · expected naive=+0.2234 · mix=+0.0005 · drift=-0.0439 · Γ_true=1.00
Naive before/after: mean +0.2212 (sd 0.0072); sign matches truth in 100% of seeds; RMSE vs policy effect 0.0461

| estimator | mean Δ̂ | bias | RMSE | 95% Wald coverage | mean CI width | sign correct | mean ESS |
|---|---|---|---|---|---|---|---|
| IPW | +0.2747 | +0.0079 | 0.0339 | 0.90 | 0.1503 | 100% | 79 |
| SNIPW | +0.2690 | +0.0022 | 0.0400 | 0.93 | 0.1528 | 100% | 79 |
| DM | +0.2630 | -0.0038 | 0.0118 | 0.57 | 0.0199 | 100% | 79 |
| DR | +0.2750 | +0.0083 | 0.0429 | 0.90 | 0.1420 | 100% | 79 |
| SwitchDR | +0.2645 | -0.0023 | 0.0116 | 0.63 | 0.0230 | 100% | 79 |

Decomposition (DR policy term + DM mix/drift split): mix̂ -0.0008 vs true +0.0005; drift̂ -0.0530 vs true -0.0439
