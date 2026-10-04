# Text-utility test on unseen data — Kaggle DJIA news (pre-registered)

Pre-registration: [`eval/preregistration/2026-10-04-text-utility-djia.md`](../preregistration/2026-10-04-text-utility-djia.md) (commit `dd8bcd1`, 12:55:28 IST, before any run on the real data). Code: `eval/text_utility_djia.py` (unchanged since registration).

Reproduce: `bash eval/fetch_djia.sh && PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/text_utility_djia.py && PYTHONPATH=. .venv/bin/python eval/exploratory_djia_gap.py && PYTHONPATH=. .venv/bin/python eval/report_djia.py`

Target 100*log(Close[t+1]/Open[t+1]) (next session open-to-close, %). Train 2008-09-08→2012-12-31 (1087) · calibration 2013-01-02→2014-06-30 (376) · test 2014-07-01→2016-06-30 (505 days). α = 0.1.

## Primary result (decision rule applied by the script)

**Decision: no evidence that text adds value.** Mean Winkler improvement of fusion over price-only = +0.0034 (+0.10% relative); one-sided block-bootstrap p = 0.46; 90% CI of the mean difference [-0.064, +0.068].

| Model | Winkler | Coverage | Mean width | Cov. high-vol | Pinball q05 / q50 / q95 | IC (median) | Our ACI: coverage / width | Linear QR: Winkler / coverage |
|---|---|---|---|---|---|---|---|---|
| price_only | 3.524 | 91.9% | 2.878 | 96.2% | 0.0946 / 0.3204 / 0.0822 | 0.355 | 90.1% / 2.743 | 6.234 / 79.6% |
| fusion | 3.520 | 92.1% | 2.836 | 96.2% | 0.0965 / 0.3191 / 0.0815 | 0.350 | 90.1% / 2.727 | 6.411 / 77.2% |

Model-family check (linear quantile regression): improvement -0.176, one-sided p = 0.995 (text makes the linear model worse).

## Exploratory (after the run; no decision weight)
- Volatility channel: Spearman correlation of |y| with each text feature on the test period: sent_mean +0.046, sent_std +0.088, frac_bear +0.066, abs_max +0.100, novelty +0.045.
- Why price-only is so strong (IC 0.36): the overnight gap continues into the open-to-close return (Spearman gap vs y: train 0.34, test 0.40; the open equals the previous close on 4.4% of test days). This pattern is consistent with stale index opening prints (the mechanism is UNVERIFIED: no source opened), so absolute intraday predictability here is not a tradeable claim. Both arms include the gap, so the text comparison is unaffected.

## Reading
- One index, ≈500 test days: a null result is "no evidence", not proof that text never helps.
- Together with StockNet (fusion ≈ price-only on pinball and coverage), we found no setting where text measurably improved calibrated intervals. The pitch is therefore reframed (see the abstract): trust and coverage guarantees for a text channel, with dropping text as the k = ∞ end of the price-of-robustness curve.
