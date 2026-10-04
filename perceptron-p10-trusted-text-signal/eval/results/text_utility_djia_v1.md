# Text-utility test on unseen data — Kaggle DJIA news (pre-registered)

Pre-registration: [`eval/preregistration/2026-10-04-text-utility-djia.md`](../preregistration/2026-10-04-text-utility-djia.md) (commit `dd8bcd1`, 12:55:28 IST, before any run on the real data). Code: `eval/text_utility_djia.py` (unchanged since registration).

Reproduce: `bash eval/fetch_djia.sh && PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/text_utility_djia.py && PYTHONPATH=. .venv/bin/python eval/exploratory_djia_gap.py && PYTHONPATH=. P10_DEVICE=cpu nice -n 10 .venv/bin/python eval/exploratory_djia_v2.py && PYTHONPATH=. .venv/bin/python eval/report_djia.py`

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
- Why price-only is so strong (IC 0.36): the overnight gap continues into the open-to-close return (Spearman gap vs y: train 0.34, test 0.40; the open equals the previous close on 4.4% of test days). This pattern is consistent with stale index opening prints (the mechanism is UNVERIFIED: no source opened), so absolute intraday predictability here is not a tradeable claim. Both arms include the gap, so the registered comparison is fair *conditional on the open*; without the gap (exploratory B below) the estimate changes sign and size but stays null.


## Timing qualification (after review; registered result unchanged)
The registration called the target "tradeable at the open", but two price features (gap, |gap|) use the next session's official open, which is not known before the open. The registered comparison is therefore *conditional on seeing the open print*, and it is not an executable-at-open test (gpt-6-sol review B3). Follow-ups B and C below are exploratory (`eval/exploratory_djia_v2.py`).

## Exploratory follow-ups (no decision weight)

| Variant | Winkler price-only → fusion | Improvement | One-sided p | Coverage price-only / fusion |
|---|---|---|---|---|
| A. registered spec re-run (sanity) | 3.524 → 3.520 | +0.1% | 0.463 | 91.9% / 92.1% |
| B. pre-open: no gap features (market-on-open decision) | 3.670 → 3.693 | -0.6% | 0.728 | 90.7% / 90.5% |
| C. positive control: synthetic useful feature, noise 0.5·sd(|y|) | 3.524 → 2.943 | +16.5% | 0.001 | 91.9% / 86.1% |
| C. positive control: synthetic useful feature, noise 1.0·sd(|y|) | 3.524 → 3.134 | +11.1% | 0.019 | 91.9% / 89.7% |
| C. positive control: synthetic useful feature, noise 2.0·sd(|y|) | 3.524 → 3.388 | +3.9% | 0.111 | 91.9% / 90.9% |

B: text does not help even when the model cannot see the open (so the gap was not hiding a text effect). C: the same test detects a genuinely useful channel when it improves the interval score by about 11% or more, and misses one of about 4% — this is the test's power.

## Reading
- One index, ≈500 test days: a null result is "no evidence", not proof that text never helps.
- Together with StockNet (fusion ≈ price-only on pinball and coverage), we found no setting where text measurably improved calibrated intervals. The pitch is therefore reframed (see the abstract): trust and coverage guarantees for a text channel, with the separately fitted price-only model as the zero-exposure alternative (not the k = ∞ end of the curve).
