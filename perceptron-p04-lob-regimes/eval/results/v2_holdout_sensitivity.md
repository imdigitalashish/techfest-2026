# v2 holdout — post-hoc sensitivity (EXPLORATORY)

- Command: `python eval/sensitivity_v2.py` (from `perceptron-p04-lob-regimes/`); inputs: `eval/results/v2_holdout.json`, `eval/results/v2_holdout_posthoc_ablation.json`
- Added after the holdout was read, in response to the cross-model reviews (`reviews/`). The registered analysis is `v2_holdout.md`.
- `clean21` excludes 2025-08-01, the one holdout day already evaluated in the v1 overnight run.
- Paired day-cluster bootstrap (4,000 resamples of days). 99% CI = Bonferroni over the five reported holdout hypotheses.

| comparison | role | 22 days: Δ [97.5% CI] | 22 days: 99% CI | days better | equal-day mean | leave-one-day-out range | 21 clean days: Δ [97.5% CI] | 21 clean: 99% CI |
|---|---|---|---|---|---|---|---|---|
| spike − static_snorm | H1 | -0.0010 [-0.0044, +0.0019] | [-0.0050, +0.0022] | 10/22 | -0.0019 | [-0.0014, -0.0002] | -0.0009 [-0.0045, +0.0021] | [-0.0051, +0.0025] |
| spike − ks_refit | H2 | -0.0278 [-0.0315, -0.0246] | [-0.0322, -0.0242] | 22/22 | -0.0287 | [-0.0284, -0.0269] | -0.0280 [-0.0320, -0.0245] | [-0.0325, -0.0241] |
| spike_gate − static_snorm | H1b | -0.0093 [-0.0129, -0.0063] | [-0.0137, -0.0061] | 22/22 | -0.0106 | [-0.0097, -0.0086] | -0.0093 [-0.0132, -0.0061] | [-0.0139, -0.0058] |
| spike_gate − ks_refit | H2b | -0.0361 [-0.0403, -0.0326] | [-0.0410, -0.0323] | 22/22 | -0.0374 | [-0.0367, -0.0352] | -0.0364 [-0.0408, -0.0326] | [-0.0417, -0.0322] |
| spike_gate − regime_gated | H3 | +0.0006 [+0.0003, +0.0009] | [+0.0003, +0.0010] | 4/22 | +0.0007 | [+0.0005, +0.0006] | +0.0006 [+0.0003, +0.0010] | [+0.0003, +0.0010] |
| regime_gated − static_snorm | secondary | -0.0099 [-0.0136, -0.0068] | [-0.0144, -0.0065] | 22/22 | -0.0113 | [-0.0103, -0.0092] | -0.0099 [-0.0140, -0.0067] | [-0.0146, -0.0063] |
| static_gbdt − static_snorm | secondary | -0.0052 [-0.0093, -0.0018] | [-0.0099, -0.0013] | 16/22 | -0.0060 | [-0.0057, -0.0042] | -0.0053 [-0.0097, -0.0018] | [-0.0104, -0.0014] |
| static_wf − static_snorm | secondary | -0.0009 [-0.0028, +0.0013] | [-0.0031, +0.0016] | 12/22 | +0.0002 | [-0.0013, -0.0005] | -0.0008 [-0.0028, +0.0016] | [-0.0031, +0.0021] |
| regime_gated − static_enorm | post-hoc ablation | -0.0083 [-0.0118, -0.0059] | [-0.0123, -0.0057] | 22/22 | -0.0097 | [-0.0087, -0.0073] | -0.0083 [-0.0121, -0.0057] | [-0.0131, -0.0054] |
| static_enorm − static_snorm | post-hoc ablation | -0.0016 [-0.0044, +0.0009] | [-0.0048, +0.0014] | 13/22 | -0.0016 | [-0.0020, -0.0008] | -0.0016 [-0.0047, +0.0010] | [-0.0052, +0.0014] |
| spike_gate − static_enorm | post-hoc ablation | -0.0078 [-0.0111, -0.0054] | [-0.0116, -0.0052] | 22/22 | -0.0090 | [-0.0081, -0.0068] | -0.0077 [-0.0113, -0.0052] | [-0.0121, -0.0050] |
