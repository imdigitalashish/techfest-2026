# POST-HOC: dependence-aware intervals for the real OBD headline numbers (reviews A8, C3)

Reproduce: `nice -n 10 .venv/bin/python eval/obd_block_bootstrap.py`. Hour-block bootstrap: 2,000 resamples of whole hours. Units: clicks per 1,000 impressions.

| quantity | estimate | row-level 95% CI (as reported) | hour-block 95% CI | hours | reference | reference inside block CI? |
|---|---|---|---|---|---|---|
| halves · deploy BTS: DR after-period effect | +1.40 | +1.13 … +1.67 | +0.93 … +1.78 | 42 | +1.26 | yes |
| halves · roll back: DR after-period effect | -1.70 | -2.35 … -1.05 | -2.46 … -0.96 | 42 | -1.26 | yes |
| Analysis 2 · V(BTS) DR, P-static | 4.887 | 4.461 … 5.312 | 4.260 … 5.567 | 84 | 4.890 | yes |
| Analysis 2 · V(BTS) DR, P-hourly | 4.936 | 4.453 … 5.419 | 4.338 … 5.565 | 84 | 4.890 | yes |

**DM (P-static) with the reward model refitted in each of 80 resamples:** SE 0.1956 per 1,000 vs 0.000735 reported (the fixed-prediction bootstrap ignored model uncertainty). The 95% CI of DM − truth is -0.560 … +0.215, so the reported "NO" consistency becomes **yes**. The pre-registered table is left as is; this row corrects its interpretation.
