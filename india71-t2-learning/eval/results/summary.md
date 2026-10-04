# SYNTHETIC evaluation summary

Command: `nice -n 10 python3 eval/run_eval.py` (coverage runs: see `eval/preregistration/2026-10-04-coverage.md`).

| Run (held-out seeds 101-130, 180 blocks) | 90% coverage | Wilson 95% | MAE moderated (pp) | MAE raw (pp) | mean half-width (pp) | allocation gain shown |
|---|---:|---:|---:|---:|---:|---|
| language_b10 | 0.967 | 0.929–0.985 | 2.16 | 4.31 | 5.97 | False |
| numeracy_b10 | 0.928 | 0.880–0.957 | 2.55 | 6.13 | 6.47 | False |
| language_b05 | 0.928 | 0.880–0.957 | 3.50 | 4.31 | 8.34 | False |
| language_b20 | 0.939 | 0.894–0.966 | 1.76 | 4.31 | 4.24 | False |
| language_b10_needcorr | 0.967 | 0.929–0.985 | 2.48 | 3.72 | 6.07 | False |

Post hoc: world-level bootstrap 95% CI for held-out coverage 0.967: 0.933–0.989.
Post hoc separation (child-weighted district average): 97/180 blocks have intervals entirely below/above it; 1.00 of those on the correct side; point estimates on the correct side: moderated 0.97 vs raw 0.98; median true within-district spread 24.9 pp.
Detection AUC (held-out): 0.777 ± 0.021.
C4 (seeds 101-105): CAT@8 exact level accuracy 0.538; full-test Bayesian IRT 0.592; ASER rule 0.486.
C7: Hindi WhatsApp plan 801 bytes for a class of 60; SMS 3 segments.
C12: 42/42 policy cases pass.
