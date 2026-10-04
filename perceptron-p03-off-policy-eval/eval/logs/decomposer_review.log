# Decomposer review — results (SYNTHETIC simulator, exact ground truth)

Reproduce: `nice -n 10 .venv/bin/python eval/run_decomposer_review.py --seeds 20` (from `perceptron-p03-off-policy-eval/`). 10,000 logged rounds per period; new-policy quality 0.7, old 0.3; DR = doubly robust with a cross-fitted logistic reward model; ± = 95%.

## (d) Drift sweep — where naive is right and where it is wrong (mix shift 0)

| response drift (logit) | true effect (after) | naive mean | naive sign correct | naive RMSE | DR mean | DR RMSE | DR coverage | Shapley policy est vs truth | interaction est vs truth |
|---|---|---|---|---|---|---|---|---|---|
| -1.50 | +0.0531 | -0.1443 | 0% | 0.1975 | +0.0530 | 0.0032 | 0.95 | +0.0642 vs +0.0646 | -0.0224 vs -0.0230 |
| -1.25 | +0.0579 | -0.1137 | 0% | 0.1717 | +0.0581 | 0.0030 | 1.00 | +0.0667 vs +0.0670 | -0.0173 vs -0.0182 |
| -1.00 | +0.0625 | -0.0810 | 0% | 0.1436 | +0.0626 | 0.0039 | 0.95 | +0.0690 vs +0.0693 | -0.0128 vs -0.0136 |
| -0.75 | +0.0667 | -0.0451 | 0% | 0.1120 | +0.0666 | 0.0040 | 0.95 | +0.0710 vs +0.0714 | -0.0088 vs -0.0093 |
| -0.50 | +0.0704 | -0.0068 | 5% | 0.0775 | +0.0703 | 0.0038 | 1.00 | +0.0728 vs +0.0733 | -0.0051 vs -0.0056 |
| -0.25 | +0.0735 | +0.0337 | 100% | 0.0402 | +0.0730 | 0.0037 | 1.00 | +0.0742 vs +0.0748 | -0.0024 vs -0.0026 |
| +0.00 | +0.0758 | +0.0756 | 100% | 0.0046 | +0.0758 | 0.0040 | 1.00 | +0.0756 vs +0.0760 | +0.0004 vs -0.0003 |
| +0.25 | +0.0773 | +0.1189 | 100% | 0.0418 | +0.0775 | 0.0042 | 1.00 | +0.0764 vs +0.0767 | +0.0021 vs +0.0012 |
| +0.50 | +0.0779 | +0.1630 | 100% | 0.0852 | +0.0768 | 0.0045 | 1.00 | +0.0761 vs +0.0770 | +0.0014 vs +0.0018 |
| +0.75 | +0.0776 | +0.2077 | 100% | 0.1302 | +0.0767 | 0.0054 | 1.00 | +0.0760 vs +0.0768 | +0.0013 vs +0.0015 |
| +1.00 | +0.0764 | +0.2509 | 100% | 0.1746 | +0.0762 | 0.0057 | 0.95 | +0.0758 vs +0.0762 | +0.0008 vs +0.0003 |
| +1.25 | +0.0743 | +0.2926 | 100% | 0.2183 | +0.0743 | 0.0058 | 0.95 | +0.0749 vs +0.0752 | -0.0010 vs -0.0017 |
| +1.50 | +0.0715 | +0.3335 | 100% | 0.2620 | +0.0717 | 0.0058 | 0.95 | +0.0735 vs +0.0738 | -0.0037 vs -0.0046 |

Naive has the right sign in every seed at drifts -0.25, +0.00, +0.25, +0.50, +0.75, +1.00, +1.25, +1.50; the wrong sign in every seed at -1.50, -1.25, -1.00, -0.75. DR's RMSE stays in 0.0030–0.0058 across the sweep; naive's ranges 0.0046–0.2620.

## (a) Feedback — the policy changes who shows up (drift −1.0)

| feedback | direct effect (truth) | total effect (truth) | population effect (truth) | DR mean | DR − direct | DR − total | DR coverage of direct |
|---|---|---|---|---|---|---|---|
| 0.00 | +0.0625 | +0.0625 | +0.0000 | +0.0626 | +0.0001 | +0.0001 | 0.95 |
| 0.25 | +0.0637 | +0.0753 | +0.0116 | +0.0650 | +0.0014 | -0.0103 | 0.80 |
| 0.50 | +0.0683 | +0.0933 | +0.0250 | +0.0700 | +0.0017 | -0.0233 | 0.85 |
| 1.00 | +0.0890 | +0.1462 | +0.0571 | +0.0906 | +0.0015 | -0.0556 | 0.95 |

The logs identify the direct effect. The audience the policy attracted (population effect) is booked as mix shift, and the total effect is not identified from the after-period logs alone.

## (c) Misspecification — reward term the logistic model cannot fit (drift −1.0, mix 0.5)

| nonlinearity | true effect | DR policy term (bias) | DM policy term (bias) | true mix | DM-mix bias (RMSE) | DR-mix bias (RMSE) | DR coverage |
|---|---|---|---|---|---|---|---|
| 0.0 | +0.0752 | +0.0761 (+0.0009) | +0.0746 (-0.0006) | +0.0162 | -0.0002 (0.0029) | -0.0001 (0.0028) | 0.95 |
| 1.0 | +0.0797 | +0.0809 (+0.0012) | +0.0766 (-0.0031) | +0.0154 | -0.0002 (0.0025) | -0.0001 (0.0029) | 0.95 |
| 2.0 | +0.0810 | +0.0826 (+0.0016) | +0.0767 (-0.0043) | +0.0132 | -0.0008 (0.0024) | -0.0004 (0.0030) | 0.95 |
| along mix axis, 1.0 | +0.0625 | +0.0635 (+0.0010) | +0.0703 (+0.0078) | +0.0174 | +0.0034 (0.0043) | -0.0003 (0.0028) | 0.85 |
| along mix axis, 2.0 | +0.0511 | +0.0519 (+0.0009) | +0.0668 (+0.0158) | +0.0179 | +0.0057 (0.0061) | -0.0002 (0.0026) | 1.00 |

## (b) Shapley coverage summary

Mean 95% coverage across all experiments: Shapley policy 0.95; interaction 0.93; after-effect (v0 term) 0.95.

