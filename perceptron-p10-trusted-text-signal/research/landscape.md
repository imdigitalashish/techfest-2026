# P10 landscape — trusting a signal extracted from messy, manipulated text

_Lead synthesis, 4 Oct 2026 07:15 IST. Raw notes (with every URL the research agents opened): [`notes/`](notes/). Tags: **[L]** = re-opened and checked by the lead tonight · **[A]** = opened by a research agent (URL in its note) · **UNVERIFIED** = not opened by anyone; do not cite until checked. Overnight the network was saturated, so several agents stopped early; gaps are listed at the end rather than filled from memory._

## Bottom line (what changes our design)
1. **Conformal for time series is mature and moving fast** — ACI (2021) → AgACI (2022) → conformal PID (2023) → decaying step sizes (2024) → gradient equilibrium (2025) → universal-portfolio OCP (Feb 2026). All give *long-run* coverage on arbitrary sequences; none gives per-day protection against an adversary who edits the inputs. **[A]** R1 §2.1; UP-OCP **[L]** arXiv:2602.03168.
2. **Robust conformal exists, but for images / norm-bounded noise.** The line RSCP (ICLR 22) → RSCP+ (ICLR 24) → VRCP (NeurIPS 24, first with regression) → CAS (ICML 24, evasion + poisoning, discrete data) → binary-certificate RCP (ICLR 25) → RCP1 (NeurIPS 25, "applicable to classification and regression") certifies ℓp or smoothing-style perturbations of one input. **Our searches found no work that certifies conformal coverage against a budget of injected *documents* feeding a text + time-series regressor.** **[A]** R2 §2.1, §2.3; RCP1 **[L]** arXiv:2506.16553. This is the gap our spike targets — stated as "not found in our searches", not "does not exist".
3. **Text rarely adds directional accuracy; don't pitch on it.** NeurIPS 2024 spotlight: removing the LLM from three LLM-for-time-series methods "does not degrade forecasting performance — in most cases, the results even improve" **[L]** arXiv:2406.16964. Our own committed baseline agrees (fusion ≈ price-only; see `eval/results/`).
4. **LLM backtests on old news leak the future.** "Lookahead Propensity" is "materially positive throughout the in-sample period and collapses essentially to zero right after the training-data cutoff" **[L]** arXiv:2512.23847. → For 2014–2016 data we use scorers that cannot have seen returns (VADER lexicon; FinBERT fine-tuned on labelled sentences) and treat any LLM scorer as suspect unless tested post-cutoff.
5. **Manipulation is real and measured.** Tweet-concatenation attack on StockNet-family models: "additional loss of $3200 (32%) over two years" on a $10,000 simulated portfolio **[L]** github.com/yonxie/AdvFinTweet README (Xie et al., NAACL 2022, arXiv:2205.01094). Invisible headline manipulation of LLM-sentiment trading systems can "reduce annual returns by up to 17.7 percentage points" **[L]** arXiv:2601.13082 (IEEE SaTML 2026).
6. **No vendor we could open publishes a calibrated interval on its text signal or a manipulation guarantee** — they publish point scores, z-scores and classifier confidence (RavenPack/Bigdata.com, AlphaSense, LSEG MarketPsych). **[A]** R5 §3.1.

## 1. Conformal prediction for non-exchangeable data
| Method | Guarantee (one line) | Status |
|---|---|---|
| Split CP / CQR (Romano et al. 2019) | finite-sample marginal coverage if calibration and test are exchangeable | MAPIE `SplitConformalRegressor`, `ConformalizedQuantileRegressor` **[L]** (installed v1.5.0) |
| ACI — Gibbs & Candès 2021, arXiv:2106.00170 | long-run miscoverage → α "irrespective of the true data generating process" | **[A]** R1; MAPIE `TimeSeriesRegressor.adapt_conformal_inference` **[L]** |
| AgACI — Zaffran et al. 2022, arXiv:2202.07282 | expert aggregation over ACI step sizes (no tuning); electricity-price case study | **[A]** R1 |
| Conformal PID — Angelopoulos, Candès, Tibshirani 2023, arXiv:2307.16895 | control view of online CP; experiments include "market returns" | **[A]** R1; code repo frozen since 2023-11-30 **[A]** |
| EnbPI / SPCI — Xu & Xie 2021/2023 | asymptotic (conditional) coverage under extra assumptions; SPCI narrower intervals | **[A]** R1 |
| Decaying step sizes — Angelopoulos, Barber, Bates 2024, arXiv:2402.01139 | retrospective guarantee on arbitrary sequences; near per-time coverage when stable | **[A]** R1 |
| Gradient equilibrium — Angelopoulos, Jordan, Tibshirani 2025, arXiv:2501.08330 | quantile recalibration under shift with constant steps | **[A]** R1 |
| UP-OCP — arXiv:2602.03168 (Feb 2026) | OCP as two-asset universal-portfolio selection; parameter-free | **[L]** |
| Conditional CP — Gibbs, Cherian, Candès (2023) | coverage over a chosen function class (e.g. regime groups) | MAPIE 1.5.0 `ConditionalSplitConformalRegressor` **[A]** R1 §2.3 (release notes) |

MAPIE 1.5.0 was released 2026-08-05 (1,600 stars, BSD-3) and also ships exchangeability tests (v1.4.0); no conformal-PID implementation appears in its release notes **[A]** R1 §2.3. **How we judge calibration:** coverage, width, Winkler score, Kupiec POF and Christoffersen independence tests (finance's standard interval backtests) — implemented in `eval/metrics.py`; primary-source citations for Kupiec (1995) and Christoffersen (1998) still to be opened (**UNVERIFIED** references).

## 2. Robustness: adversarial inputs, poisoning, certified text, robust aggregation
- **Robust CP:** RSCP (Gendler et al., ICLR 2022) — later shown "flawed when used in practice" by RSCP+ (Yan, Romano, Weng, arXiv:2404.19651) **[A]**; PRCP (UAI 2023, arXiv:2307.16360) for "most" perturbations **[A]**; VRCP (arXiv:2405.18942, NeurIPS 2024) via NN verification, ℓ1/ℓ2/ℓ∞ "as well as regression tasks" **[A]**; COLEP (arXiv:2403.11348, ICLR 2024) **[A]**; Zargarbashi et al. ICML 2024 (arXiv:2407.09165) bounds "the worst-case change in conformity scores" under evasion *and* poisoning, continuous and discrete **[A]** — the closest mechanism to ours; ICLR 2025 binary certificate (arXiv:2503.05239) **[A]**; RCP1 NeurIPS 2025 (arXiv:2506.16553) **[L]**.
- **Certified text robustness:** IBP for word substitutions (Jia et al., EMNLP 2019, arXiv:1909.00986: 75% certified accuracy on IMDB vs 8%/35%) **[A]**; SAFER randomized smoothing (ACL 2020, arXiv:2005.14424) **[A]**; Text-CRS (arXiv:2307.16630) adds insertion/deletion/reordering **[A]**. None of these is combined with conformal coverage in what the agent found **[A]** R2 §2.3.
- **Robust aggregation:** coordinate-wise median / trimmed mean are order-optimal under a Byzantine fraction (Yin et al., ICML 2018, arXiv:1803.01498) **[A]**. Our certificate needs only the 1-D order-statistic monotonicity of the trimmed mean (proved in `components/robust_conformal/certify.py` docstring), not their rates.

## 3. Fusing text with prices
- **Text scorers:** two different "FinBERT"s — `ProsusAI/finbert` (Araci 2019, Financial PhraseBank) and `yiyanghkust/finbert-tone` (Huang, Wang & Yang, CAR 2023; 4.9B-token corpus) **[A]** R3 §2.1. VADER is the social-media lexicon baseline we run tonight. LLM return-predictability headline numbers (Lopez-Lira & Tang, arXiv:2304.07619) are **UNVERIFIED** (only a search summary was seen).
- **Multimodal TS:** Time-MMD + MM-TSFlib (NeurIPS 2024 D&B; LLM token outputs pooled with TS attention) **[A]**; From News to Forecast (NeurIPS 2024; LLM agents select relevant news) **[A]**; Context-is-Key benchmark **UNVERIFIED** (page blocked).
- **TS foundation models with quantiles** (candidate price branch / baseline): Chronos → Chronos-Bolt (Amazon), TimesFM 3.0 (covariates), Moirai 2, TiRex (35M xLSTM), Toto, Sundial (ICML 2025 oral) **[A]** R3 §2.4. Not used tonight (download budget).
- **Direction vs magnitude:** our hypothesis that text explains volatility better than direction is **untested by literature review tonight** (agent search rate-limited) — it is tested empirically in our ratchet loop instead.

## 4. Manipulation in the wild
- 23 Apr 2013: hacked @AP tweet; "the Dow plunged more than 140 points" (CNBC) **[A]** R4b.
- 9 Jan 2024: hacked @SECGov post on spot-bitcoin ETFs, up "about 30 minutes"; bitcoin "spiked near $48,000 but has since fallen to around $45,700" (TechCrunch) **[A]** R4b. sec.gov returned HTTP 403 to the agent.
- Attacks on text-driven predictors: Xie et al. 2022 (victims include StockNet; $3,200 / 32% extra loss) **[L]**; Rizvani, Apruzzese, Laskov 2026 (homoglyphs + hidden text; −17.7 pp annual return) **[L]**; 2026 preprints on market-signal injection against LLM pricing agents (arXiv:2609.18357) and multi-agent contagion (arXiv:2609.19789) **[A]**.
- SEBI/SEC enforcement on social-media pump-and-dumps, bot detection and machine-text detectors: **not reached tonight** (agent died) — **UNVERIFIED**, next pass.

## 5. What companies ship today
| Company | What ships (public material) | Credibility / novelty handling | Uncertainty per prediction? | Tag |
|---|---|---|---|---|
| RavenPack / Bigdata.com | Entity Sentiment API (daily) + real-time Sentiment Tearsheet; daily score = event sentiment weighted by `(relevance/100)² × (novelty/90)²`; "sentiment pressure" z-score; abnormal-attention z-score | explicit relevance and novelty weights; source ranking is a vendor claim | no — point values and z-scores | [A] R5 (Bigdata.com blog, 20 Jul 2026) |
| AlphaSense | sentence-level pos/neg/neutral "with an explicit confidence value"; document score normalised to [−99, +99] vs a 2-year distribution | phrase highlighting (attribution) | classifier confidence only, not a calibrated interval on returns | [A] R5 |
| LSEG MarketPsych | "Text Tagging Engine": "Unlike LLMs, it's deterministic" | disambiguation-first | not stated | [A] R5 |
| Dataminr | "Multi-Modal Fusion AI" over >1M sources for event/risk alerts | not public | not stated | [A] R5 |
| Bloomberg, S&P Kensho, Dow Jones, Accern | pages blocked or not reached | — | — | UNVERIFIED |

**Where we borrow / beat them:** borrow RavenPack's relevance×novelty weighting and abnormal-attention z-score (our aggregator already computes attention); beat all of the above on *calibrated per-prediction intervals with a stated manipulation budget* — none we opened publish one.

## 6. Data (lead-verified)
- **StockNet** (Xu & Cohen, ACL 2018) — github.com/yumoxu/stocknet-dataset, MIT, 681 stars, last push 2019-03-06 **[L]**; locally: 87 tickers with tweets, 119,641 raw tweets (with user metadata), prices 2012-09-04 → 2017-09-01 **[L]** (`eval/prepare.py` output).
- **FNSPID** (KDD 2024) — HF `Zihan1004/FNSPID`: `All_external.csv` 5,731 MB, `nasdaq_exteral_data.csv` 23,233 MB, `full_history.zip` 590 MB **[L]**. Finals dataset (stream-filter by ticker; never store whole).
- Kaggle "Daily News for Stock Market Prediction" — no Kaggle credentials on this machine; mirror **UNVERIFIED**.

## 7. Not verified tonight (do not cite yet)
Lopez-Lira & Tang numbers · Chen, Kelly & Xiu (SSRN) · CiK benchmark · Kupiec 1995 / Christoffersen 1998 primary pages · SEBI finfluencer rules and pump-and-dump orders · Binoculars / Fast-DetectGPT detection numbers · TextAttack maintenance status · Bloomberg / S&P / Dow Jones product pages · social signal (X/HN/Reddit) — the R7 agent produced no file.
