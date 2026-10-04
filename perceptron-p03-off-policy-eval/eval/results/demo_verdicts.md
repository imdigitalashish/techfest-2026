# Demo verdicts (what the product prints)

Reproduce: `nice -n 10 .venv/bin/python eval/demo_verdicts.py`. Simulator rows are SYNTHETIC (seed 0); OBD rows are REAL, with the gate applied POST HOC.

| case | decision | what the tool says | ground truth (not seen by the tool) |
|---|---|---|---|
| S1_drift_masks_gain | **worked** | Dashboard moved -5.35 points. Policy (Shapley) +7.07 points [+6.33 points, +7.80 points]; environment -12.42 points; interaction +1.43 points [-0.04 points, +2.90 points]. | truth: policy (Shapley) +7.57, after-period effect +7.52 points |
| S2_drift_fakes_gain | **hurt** | Dashboard moved +8.88 points. Policy (Shapley) -8.48 points [-9.16 points, -7.80 points]; environment +17.36 points; interaction +0.74 points [-0.62 points, +2.10 points]. | truth: policy (Shapley) -8.37, after-period effect -8.37 points |
| S3_stationary_control | **worked** | Dashboard moved +12.37 points. Policy (Shapley) +11.06 points [+10.31 points, +11.82 points]; environment +1.31 points; interaction +1.01 points [-0.50 points, +2.53 points]. | truth: policy (Shapley) +11.57, after-period effect +11.56 points |
| S5_low_overlap | **cant_tell** | Dashboard moved +22.49 points. Can't tell from these logs (V(after,old): ESS/n 0.0074 < 0.05; V(before,new): ESS/n 0.0064 < 0.05). | truth: policy (Shapley) +27.23, after-period effect +26.67 points |
| S4_hidden_override | **worked** | Dashboard moved +3.27 points. Policy (Shapley) +1.58 points [+1.00 points, +2.17 points]; environment +1.69 points; interaction -0.80 points [-1.97 points, +0.37 points]. Hidden confounding of Γ = 1.25 would overturn it. | truth: policy (Shapley) +5.22, after-period effect +8.27 points |
| OBD halves · A_deploy_BTS | **worked** | Dashboard moved +1.62 per 1,000. Policy effect in the before period +1.29 per 1,000 [+0.67 per 1,000, +1.91 per 1,000]; interaction not estimable (V(after,old): ESS/n 0.0092 < 0.05). | truth (concurrent arms): after-period effect +1.26, Shapley policy +1.44 per 1,000 |
| OBD halves · B_rollback_to_Random | **hurt** | Dashboard moved -1.25 per 1,000. Policy effect in the after period -1.70 per 1,000 [-2.35 per 1,000, -1.05 per 1,000]; interaction not estimable (V(before,new): ESS/n 0.0006 < 0.05, |mean-weight z| 6.1 > 3.0). | truth (concurrent arms): after-period effect -1.26, Shapley policy -1.44 per 1,000 |
