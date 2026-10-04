# Pre-registration — does text add value? (unseen data: Kaggle DJIA news)

- **Registered:** 4 Oct 2026, 12:55:28 IST (commit `dd8bcd1`), by the P10 lead. The git commit that adds this file also freezes the analysis code, `eval/text_utility_djia.py`; its timestamp precedes any run on the real data.
- **Why:** the strongest critique of P10 (independent review, `research/notes/review-adr001-rubber-duck.md`) is "drop the text". On StockNet, price-only matches fusion (pinball 0.3513 vs 0.3518). StockNet's test period has been looked at several times, so the question is tested once, on data we have not analysed.

## Data
- Kaggle "Daily News for Stock Market Prediction" (aaron7sun/stocknews): the top 25 r/worldnews headlines per day, plus DJIA OHLCV, 2008-08-08 → 2016-07-01 (1,989 trading days). It is the organisers' named starter resource type ("financial news + price dataset widely available on Kaggle").
- Obtained from a GitHub mirror (no Kaggle credentials): `eval/fetch_djia.sh` verifies git blob SHAs. The news file is byte-identical in two independent mirrors.
- **Looks taken before registration (integrity only):**
  - file hashes;
  - DJIA closes vs Yahoo ^DJI: all 1,989 days match, max relative difference 7.0e-11;
  - the dataset's `Label` vs same-day price direction: 99.9% agreement, which shows `Label` is *contemporaneous* with the headlines and unusable as a forecast target;
  - news dates == price dates.
- No statistic relating text to returns has been computed. A synthetic dry run (`--synthetic`, random prices and headlines, no real data) checked the code path only.

## Target and timing
y(t+1) = 100·log(Close(t+1) / Open(t+1)), the next session's open-to-close log return. Headlines carry dates without times; every headline dated t is public before the 09:30 ET open of t+1. So all features are known at the open of t+1, and the forecast is causal and tradeable at the open.

## Models (no tuning; hyperparameters frozen as in `components/fusion/lgbm_quantile.py` at this commit)
- **price_only** — 14 features known at the open of t+1: r0–r4 (close-to-close log-return lags), rv5, rv20, Parkinson range of t, log-volume z-score, intraday return of t, overnight gap (open(t+1) vs close(t)) and its absolute value, 20-day volatility of open-to-close returns, day of week. The gap already prices overnight news, so this baseline is deliberately strong.
- **fusion** — price features plus 5 text features of day t from frozen MiniLM-L6 embeddings and a logistic-regression sentiment head trained on Twitter Financial News Sentiment (`components/text_scorer/minilm.py`; never trained on returns):
  - mean and standard deviation of per-headline sentiment (p_bullish − p_bearish);
  - share of bearish headlines;
  - max |sentiment|;
  - novelty = 1 − cosine(day-t mean embedding, mean of days t−20…t−1).
- Both are LightGBM quantile models (5%, 50%, 95%), wrapped in symmetric split-CQR, α = 0.1.

## Splits (by feature date t; frozen)
Train ≤ 2012-12-31 · calibration 2013-01-01 → 2014-06-30 · test 2014-07-01 → 2016-06-30 (≈ 500 days, incl. the Aug-2015 and Jan-2016 sell-offs and Brexit week).

## Primary hypothesis and decision rule
- **H1:** fusion has a lower mean Winkler interval score (α = 0.1) than price_only on the test period.
- **Test:** paired daily differences d_t = W_price − W_fusion. Circular moving-block bootstrap of the mean (block 10 days, 10,000 resamples, seed 0); one-sided p = P*(mean* − mean ≥ mean).
- **Decision (pre-committed):** "text adds value" iff mean d > 0, p < 0.05, and fusion test coverage ≥ 0.85. Otherwise "no evidence that text adds value". In that case the pitch is reframed around trust and coverage guarantees: text enters only through the certified channel with an explicit budget k, and dropping text is the legitimate k = ∞ end of the price-of-robustness curve.
- **Power caveat:** one index and ≈ 500 test days. Small effects (a few % of Winkler) may be undetectable, so a null result means "no evidence", not "no effect".

## Reported without decision weight
- **Secondary:** coverage, width, high-volatility coverage, pinball loss per quantile, Spearman IC of the median, and our ACI loop's coverage, for both models.
- **Model-family check:** the same comparison with linear quantile regression.
- **Exploratory:** Spearman correlation of |y| with each text feature (the volatility channel).

## Deviations policy
The result is reported whichever way it comes out. No re-runs with changed features, target, splits or hyperparameters. Any later analysis is labelled exploratory. Bugs found after the run are fixed, documented below, and re-run once, with both runs reported.

## Deviations
- Header correction only (before the real run): the registration time was first written as an estimate ("~13:20 IST"); the registration commit is `dd8bcd1` at 12:55:28 IST. No change to hypotheses, code or data.
