# R3 — Fusing Text and Time Series for Financial Prediction: What Works in 2024–2026

Status: IN PROGRESS (incremental write; skeleton first, filled per-source)
Scope: Perceptron P10 "Trusting a Signal Extracted from Messy, Manipulated Text" — survey of text sentiment extractors, multimodal text+TS fusion architectures, stock movement benchmarks (StockNet etc.), TS foundation models w/ quantile outputs, text→direction vs. text→magnitude evidence, and Apple Silicon throughput notes.
Accessed: 2026-10-04 (IST). All "accessed" stamps below are 2026-10-04 unless noted otherwise.

---

## (1) TL;DR

_(to be filled last, after findings)_

---

## (2) Findings by sub-topic

### 2.1 Text signal extractors (FinBERT, FinGPT, zero-shot LLMs, ChatGPT-forecast, look-ahead bias)

**There are TWO distinct, commonly-confused "FinBERT" checkpoints** — important to disambiguate for our writeup:
- **`ProsusAI/finbert`** (HF model card, opened directly) — pretrained BERT further trained on a financial corpus then fine-tuned on the **Financial PhraseBank** (Malo et al. 2014) for 3-way sentiment (positive/negative/neutral, softmax output). Underlying paper is **Araci (2019), "FinBERT: Financial Sentiment Analysis with Pre-trained Language Models," arXiv:1908.10063** — NOT the Contemporary Accounting Research paper. Built/maintained by Prosus (contacts: Dogu Araci, Zulkuf Genc). [huggingface.co/ProsusAI/finbert, accessed 2026-10-04]
- **`yiyanghkust/finbert-tone`** (HF model card, opened directly) — this is the one actually tied to **Huang, Wang & Yang, "FinBERT: A Large Language Model for Extracting Information from Financial Text," Contemporary Accounting Research (2022/2023 online; Vol 40 Issue 2, pp. 806–841 per web-search secondary confirmation)**. Pretrained on a 4.9B-token corpus: 10-K/10-Q corporate reports (2.5B tokens) + earnings call transcripts (1.3B) + analyst reports (1.1B), then fine-tuned on 10,000 manually annotated (pos/neg/neutral) analyst-report sentences. 3-way `transformers` pipeline, trivial to call. [huggingface.co/yiyanghkust/finbert-tone, accessed 2026-10-04]
- **Practical implication for P10:** if the brief says "FinBERT," check which checkpoint — `finbert-tone` is domain-pretrained on a much larger/more diverse finance corpus (earnings calls + analyst reports, not just phrasebank) and is likely the stronger zero-shot sentiment feature extractor for news/tweets; `ProsusAI/finbert` is simpler/more ubiquitous in tutorials. Both are drop-in HF `BertForSequenceClassification`, so trying both as competing text-feature branches is cheap.
- GitHub repo `yya518/FinBERT` (linked from the finbert-tone card, not yet opened directly this session) hosts "more technical details" — listed under leads.

**Lopez-Lira & Tang, "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models" (arXiv:2304.07619).** Verified directly by opening the **ar5iv HTML rendering** (`ar5iv.labs.arxiv.org/html/2304.07619`, appendix section) — confirms paper structure: GPT score is a simple 3-way encoding (**+1 = model says YES/good news, 0 = UNKNOWN, −1 = NO/bad news**), with **Table 4** reporting "Average Next Day's Return by Prediction Score" and robustness split **Table OA3** into **small vs. non-small stocks** (small = below 10th percentile NYSE market cap), plus cross-LLM alpha comparisons (Table OA4) including a comparison against a cited prior strategy that "uses the first 15-minute returns to select overnight news to trade" (likely Ke/Kelly/Xiu-style). [ar5iv.labs.arxiv.org/html/2304.07619, accessed 2026-10-04 — I could **not** load `arxiv.org/abs/2304.07619` itself after 3 attempts (consistent TimeoutError), so the official abstract/latest-version (v6, Oct 2025 per secondary report) metadata is **not independently confirmed by me**.]
- **UNVERIFIED precise headline numbers** (reported only via the web_search tool's own synthesis, citing arxiv.org/abs/2304.07619 + advisoranalyst.com, neither of which I could successfully open myself — transport/timeout errors both times): "~90% hit rate for initial market reaction direction," "93.3% daily hit rate overnight / 88.8% intraday," "~34 bps/day long-short alpha pre-cost, Sharpe ≈ 3," "profitability decays as LLM-strategy adoption spreads." **Treat these exact figures as unverified until a direct primary fetch succeeds** — logged in §5.

**Look-ahead bias / training-cutoff leakage (direct hit — exactly the brief's ask, and recent: Dec 2025).** Opened directly: **`ar5iv.labs.arxiv.org/html/2512.23847`** (mirror) and **`arxiv.org/html/2512.23847v2`** — paper on detecting **lookahead bias in LLM forecasts** via a **"Lookahead Propensity" (LAP)** score:
  - Method: ask the LLM a **date-only recall query** with NO contemporaneous context (just firm name + ticker + target date), forcing it to answer "up / down / unknown" for a future realized outcome (next-day stock return direction, or next+2-quarter capex direction). A model with no memorization should mostly answer "unknown"; confident up/down answers on a bare date-only prompt reveal memorization rather than reasoning.
  - **Concrete example given:** Kodak's +318% intraday move on 2020-07-29 (COVID-loan news, heavy press coverage) — when Llama-3.3-70B is asked *only* "did Kodak's stock close up or down on 2020-07-29" with zero other context, it assigns **P(up) ≈ 0.9999** (P(down), P(unknown) both <1e-5) — i.e., essentially perfect, saturated recall, not forecasting skill.
  - **Second example:** Amazon Q1 2020 earnings call → asked (no transcript/context) about Q3 2020 capex direction, model assigns **P(up) ≈ 0.97**; realized capex-to-assets did rise 5.5%→9.0% (+62%) from Q2→Q3 2020 — again consistent with memorized press coverage, not inference from the (withheld) transcript.
  - **Core implication:** the paper's broader claim (confirmed via intro, opened directly) is that "forecast accuracy is artificially boosted on high-LAP [high-memorization] examples; performance collapses on strictly post-training-cutoff examples" — i.e. much of the literature's claimed LLM-forecasting "alpha" on in-sample-era news may be contamination, not skill. Paper explicitly flags that **masking firm identifiers / anonymizing context only partially mitigates** this, and that the issue is **task-specific, not a fixed LLM property** (citing an earlier ref [5] in the paper, not yet independently opened). [arxiv.org/html/2512.23847v2 + ar5iv.labs.arxiv.org/html/2512.23847, accessed 2026-10-04]
  - **Direct actionable takeaway for P10:** we should (a) only backtest on news dated after our chosen LLM/embedding model's training cutoff, or (b) run our own LAP-style date-only-recall probe on whatever text model we pick, to quantify how much of our fusion model's apparent skill is memorization vs. genuine text-signal extraction — this is exactly the kind of "trusting a signal extracted from messy, manipulated text" framing judges will likely probe.
  - Title note: the paper is referred to as **"Detecting Lookahead Bias in LLM Forecasts"** in its own running headers (confirmed directly in the HTML), while a conference/working-paper listing (abfer.org, not opened by me) titles it "A Test of Lookahead Bias in LLM Forecasts" — likely the same paper under two title variants (preprint vs. conference submission); **not fully reconciled**, logged in §5.

**Chen, Kelly & Xiu, "Expected Returns and Large Language Models."** **UNVERIFIED by direct fetch** — SSRN abstract page not opened this session (only summarized by the web_search tool itself, citing `papers.ssrn.com/sol3/papers.cfm?abstract_id=4416687`). Reported (not independently confirmed): LLM text embeddings of full news articles outperform bag-of-words/Word2Vec for cross-sectional return prediction; news-momentum effect concentrated in small stocks; validated across 16 global equity markets / 13 languages; analyst-related news topic shows strongest signal. **Do not cite these specific numbers/claims as verified — logged under Leads not verified.**

### 2.2 Multimodal time-series forecasting with text (Time-MMD/MM-TSFlib, From News to Forecast, CiK, negative results)

**Time-MMD (Liu, Xu, Zhao, Kong, Kamarthi, Sasanur, Sharma, Cui, Wen, Zhang, Prakash — arXiv:2406.08627, NeurIPS 2024 D&B track).** Opened directly (`github.com/AdityaLab/Time-MMD` README + `arxiv.org/html/2406.08627v4` §2.2): first **multi-domain multimodal TS dataset**, 9 domains, each with (a) numerical CSVs and (b) two paired text streams per domain — **"report" text** (1-2 manually curated authoritative series per domain, e.g. the CDC's weekly influenza report) and **"search" text** (top-10 Google results/week for 2-3 domain keywords, back to 1980). Key methodological point directly relevant to P10's "messy, manipulated text" framing: they explicitly engineer around **data contamination** by using **Llama3-70B to (1) filter for relevance, (2) "disentangle facts from predictions"** (i.e. strip out text that is itself a forward-looking forecast, which would leak future information) **and (3) summarize**, with prompt-level guards against hallucination (require source citation; allow an explicit "not available" output rather than fabricating). This "fact vs. prediction" disentanglement step is a reusable idea for our own news/tweet cleaning pipeline.
- **Companion library MM-TSFlib** (`github.com/AdityaLab/MM-TSFlib`, opened directly): benchmarks fusion of classical/deep TS backbones with text encoders including **LLAMA2, LLAMA3, GPT2/GPT2M/GPT2L/GPT2XL, BERT, Doc2Vec, and closed-source LLMs (e.g. GPT-3.5, used offline to pre-generate text-based predictions to save cost)**. Fusion mechanism is **attention-based pooling of LLM token outputs, weighted by the time-series model's attention scores** (`--pool_type attention`, vs. plain avg/min/max pooling) — i.e. a **learned cross-modal attention gate**, not naive concatenation. The repo's own README is unusually candid: **"this Lib is only a first-step attempt... many of the designs are naive, such as pre-stored matching and independent multimodal modeling... which can be improved through better solutions such as carefully designed retrieval matching and multimodal fusion"** — i.e. the dataset authors themselves flag that fusion-architecture innovation room is wide open, which directly supports the hackathon's "innovation room" framing. **Did not reach a quantitative results table in the arXiv HTML fetch (page content exhausted at ~9000 chars before reaching the benchmark section) — exact per-fusion-design accuracy/MSE deltas are NOT verified; logged in §5.**

**"From News to Forecast: Integrating Event Analysis in LLM-Based Time Series Forecasting with Reflection"** (Xinlei Wang, Maike Feng, Jing Qiu, Jinjin Gu, Junhua Zhao — U. Sydney / CUHK-Shenzhen / Shenzhen Institute of AI and Robotics for Society; arXiv:2409.17515; NeurIPS 2024). Opened directly (`github.com/daydreamer-amelia/From_News_to_Forecast` README): uses **LLM-based generative agents** to (1) automatically filter/select which news is relevant to a given forecasting window, (2) fine-tune on paired (news, time-series) data, and (3) **iteratively reflect** — an evaluation agent checks prediction quality and searches for *missed* influential news to feed back in, refining future selection. Domains tested: **Australian electricity demand (AEMO half-hourly data), Bitcoin price, exchange rates, traffic** — **no direct equity/stock-news experiment reported** in what I opened (the finance-adjacent domains are crypto/FX/electricity, not single-stock equities). Architecture figure referenced (`img/framework.png`) but not independently inspected (image, not parsed). **Quantitative improvement numbers not reached in this fetch — logged in §5.**

**"Are Language Models Actually Useful for Time Series Forecasting?"** (Tan, Merrill, Gupta, Althoff, Hartvigsen — arXiv:2406.16964, **NeurIPS 2024 Spotlight**). Opened directly (`github.com/BennyTMT/LLMsForTimeSeries` README) — this is the **negative result** flagged in the brief, confirmed firsthand: ablating 3 recent LLM-based TSF methods by **removing the LLM entirely or swapping it for a plain attention layer did not hurt performance, and often improved it**. The paper's own simple baseline, **"PAttn"** (patching + attention, no pretrained LLM at all), **"outperformed most LLM-based TSF models."** Explicit scope limitation stated by the authors themselves in bold on the README: this result is about **numerical-only autoregressive-token TSF** ("Time Series Forecasting Models mentioned in this paper are Not [using context to reason]") — they **explicitly point to a different line of work, "time series reasoning (forecasting) through text"** (`github.com/behavioral-data/TSandLanguage`, not opened this session) as the place where LLM-as-text-reasoner (rather than LLM-as-numeric-sequence-model) might still add value. **This is an important nuance for P10**: the "LLMs don't help time series" negative result is about **repurposing an LLM's token-prediction machinery to directly model numeric sequences** (e.g. LLMTime-style digit tokenization), NOT about **using a text/sentiment feature as an auxiliary input/covariate to a separate TS model** — our fusion design (text sentiment branch + separate TS branch + fusion head) is architecturally the latter, so this negative result does not directly contradict the hackathon's MVP approach, but it is strong evidence to **avoid designs that ask an LLM to literally forecast price digits from text alone**, and to **always keep/benchmark a strong non-text TS-only baseline (e.g. PAttn-style patch+attention) to prove the text branch earns its keep**, exactly mirroring how STLAT (price-only) beat text-using baselines on StockNet (§2.3).

**Context is Key (CiK)** (Williams, Ashok, Marcotte, Zantedeschi, et al. — arXiv:2410.18959, NeurIPS 2024 D&B track). **Not independently opened this session** — `openreview.net/forum?id=ReSNVjuPpw` returned a bot-check page ("Verifying your browser...") instead of content, and I did not fetch the GitHub repo (`ServiceNow/context-is-key-forecasting`) or arXiv HTML directly this pass (time/source-budget tradeoff). Reported only via the web_search tool's own synthesis (**not independently confirmed — treat as UNVERIFIED**): benchmark pairs numerical series with textual context (background knowledge, explicit numeric constraints, future known events, causal explanations) where **solving the task requires the text** (pure-numeric models cannot win by construction); claimed finding is that **"a straightforward LLM prompting approach outperforms all other tested baselines"** including TS foundation models and classical stats models, but with caveats (hallucination, prompt sensitivity, inference cost). **Flagged for direct verification in a follow-up pass** — logged in §5.

### 2.3 Text+price stock movement prediction (StockNet, HAN, MAN-SF, SEP WWW'24, 2025 successors)

**StockNet dataset (Xu & Cohen, ACL 2018, "Stock Movement Prediction from Tweets and Historical Prices").** Opened directly: `github.com/yumoxu/stocknet-dataset` README — confirms dataset is **2-year price movements (01/01/2014–01/01/2016) for 88 US stocks** (8 Conglomerates-sector stocks + top-10-by-market-cap in each of 8 other sectors), paired with tweets; original model is a **deep generative model with recurrent continuous latent variables + neural variational inference** (to handle stochasticity) and a **hybrid objective with a temporal auxiliary task**. Companion code repo: `github.com/yumoxu/stocknet-code` (not opened this session). [github.com/yumoxu/stocknet-dataset, accessed 2026-10-04]

**Benchmark numbers — opened directly via a reproduction repo (`github.com/lukasabdallah/ACL18-Stocknet`)**, which reports a "Table 2: Further comparison with strongest approaches" (values rendered as text in the README, table 1 itself did not render in markdown fetch):

| Model | Specificity (%) | Precision (%) | Sensitivity (%) | F1 (%) |
|---|---|---|---|---|
| Adv-ALSTM (val-selected) | 59 | 59 | 56 | 57 |
| Adv-ALSTM (test-selected) | 58 | 60 | 58 | 59 |
| MAN-SF | 58.11 | 61.44 | 58.16 | 59.75 |
| **STLAT (2022)** | **63.14** | **65.15** | **63.19** | **64.15** |

This repo also states (its own claim, citing the STLAT paper) that **"the best two baselines on the ACL18 (StockNet) Dataset are Adv-ALSTM and MAN-SF,"** and that **STLAT does not use tweets at all** (price-only) yet beats the text-using baselines on this benchmark — a useful cautionary data point that text features don't automatically beat a well-tuned price-only sequence model on this particular dataset/split. [github.com/lukasabdallah/ACL18-Stocknet, accessed 2026-10-04]
- **UNVERIFIED (reported only via web_search synthesis, not seen directly in my own fetch of the same repo)**: original StockNet model ACC≈58.2%, MCC≈0.081; MAN-SF up to ACC≈60.8%, MCC≈0.195; an unnamed non-tweet method up to ACC≈64.56%, MCC≈0.297. The underlying "Table 1" did not render as data in my fetch (image/plot, not text), so **treat these specific accuracy/MCC figures as unverified** — logged in §5.
- **MAN-SF (multi-pronged attention stock-forecasting, Sawhney et al.) and SEP (WWW 2024)**: web_search calls for both were rate-limited (github-mcp-server shared rate-limit bucket) and not yet retried successfully — see §2.7 hit/miss log and §5.

### 2.4 Time-series foundation models w/ quantile outputs (Chronos family, TimesFM 2.x/3.0, Moirai, TiRex, Toto, Sundial)

This sub-topic turned out to be the **richest vein for P10's TS branch** — several of these models ship native probabilistic/quantile output and (critically) native **covariate support**, which is directly usable as the fusion mechanism for injecting a text-derived sentiment score into the TS branch rather than hand-rolling a gating network. All opened directly (GitHub READMEs / HF model cards):

- **Chronos family (`github.com/amazon-science/chronos-forecasting`, opened directly).** Timeline from the repo's own changelog: original **Chronos** paper/code 13 Mar 2024 (arXiv:2403.07815) → **Chronos-Bolt** 26 Nov 2024 (patch-based; **5% lower error, up to 250× faster, 20× more memory-efficient** than original Chronos at the same size) → **Chronos-2** released **20 Oct 2025** (arXiv:2510.15821 technical report), with **zero-shot univariate, multivariate, AND covariate-informed forecasting in one model**, best performance on fev-bench/GIFT-Eval/Chronos Benchmark II among pretrained models, and a **>90% pairwise win rate vs. Chronos-Bolt**.
  - **Chronos-2 HF model card** (`huggingface.co/amazon/chronos-2`, opened directly): **120M params, encoder-only (T5-encoder-inspired), group-attention mechanism for in-context learning across related series/covariates**, trained on real + large-scale synthetic data. Explicit capability table:
    | Capability | Chronos-2 | Chronos-Bolt | Chronos (orig) |
    |---|---|---|---|
    | Multivariate forecasting | ✅ | ❌ | ❌ |
    | Past-only covariates | ✅ | ❌ | ❌ |
    | Known-future covariates | ✅ | 🧩 (partial) | 🧩 (partial) |
    | Max context length | 8192 | 2048 | 512 |
    Throughput claim (card text): **>300 forecasts/second on a single A10G GPU**; supports both GPU and CPU inference. **This covariate-informed mode is a plausible off-the-shelf fusion point for P10**: feed a daily text-sentiment score in as a known covariate channel instead of building a custom cross-attention fusion network.
- **TimesFM (`github.com/google-research/timesfm`, opened directly).** Latest is now **TimesFM 3.0** (supersedes 2.x) — adds **native multivariate forecasting + both past-only and past-and-future covariate support**; claims **#1 rank on fev-bench (100 tasks), #1 on "TIME Benchmark" (50 domains/98 tasks), #1 among foundation models on GIFT-Eval**. **License caveat (important for hackathon use):** source code stays Apache-2.0, and weights **up to v2.5** stay Apache-2.0, but **TimesFM 3.0 pretrained weights are under a separate `timesfm-non-commercial-license-v1.0`** — non-commercial/non-production only when self-hosted (commercial use only via Google Cloud/BigQuery ML). For a hackathon prototype this is fine, but worth flagging if judges ask about productionization.
- **Moirai family (`github.com/SalesforceAIResearch/uni2ts`, opened directly).** Library now exposes **three selectable model families: `moirai`, `moirai-moe`, `moirai2`** (i.e., a Moirai 2.0 exists alongside the original Moirai (arXiv:2402.02592) and Moirai-MoE (arXiv:2410.10469)). Uses GluonTS for data plumbing; zero-shot forecasts configurable by model size (`small`/`base`/`large`), patch size, context/prediction length.
- **TiRex (`github.com/NX-AI/tirex`, opened directly).** **35M-parameter**, **xLSTM-based** (not transformer) pretrained zero-shot forecaster; outputs **both point estimates and quantile estimates** natively; claims top scores on GIFT-Eval and the "ChronosZS" (fev) leaderboard for both long- and short-horizon forecasting. **TiRex-2** now exists (arXiv:2607.01204) adding native multivariate + past/future-known covariates — same covariate-fusion trend as Chronos-2/TimesFM 3.0. Explicitly notes it is **"currently only tested on Linux and MacOS"** — i.e. Apple Silicon/macOS is a supported platform.
- **Toto (`huggingface.co/Datadog/Toto-Open-Base-1.0`, opened directly).** Decoder-only transformer, **Proportional Factorized Space-Time Attention** for high-dimensional multivariate series, **probabilistic predictions via a Student-T mixture model** (point + uncertainty in one forward pass). Pretrained on **>2 trillion time series points** ("largest pretraining dataset for any open-weights TS foundation model to date" per the card — Datadog's own claim, not independently cross-checked). Domain focus is observability metrics (server/infra telemetry) rather than finance — relevance to stock data is **unverified/likely weak** without further evidence.
- **Sundial (`github.com/thuml/Sundial`, opened directly).** THUML (Tsinghua), **ICML 2025 Oral (top 1%)**, arXiv:2502.00816. **Generative** TS FM pretrained on "TimeBench" (**10^12 time points**), using a novel **"TimeFlow Loss"** that predicts the next patch's *distribution* without discrete tokenization — supports arbitrary statistical outputs (any quantile, or full sample-based confidence intervals) by drawing multiple generated samples rather than fixed quantile heads. Claims **#1 MASE on GIFT-Eval (May 2025)**. **Directly gives an Apple-Silicon throughput number** (see §2.6).

### 2.5 Direction vs. magnitude/volatility: does text predict vol/volume better than direction?

_(pending — searches rate-limited this pass, retrying)_

### 2.6 Apple Silicon throughput for FinBERT / small LLMs / embedding models

**Only a TS-foundation-model data point found so far (not FinBERT/LLM yet).** Sundial GitHub README (`github.com/thuml/Sundial`, opened directly) publishes a wall-clock latency table explicitly labeled **"Inference Time on Apple M1 Pro CPU (16 GB)"** (single-sample zero-shot generation, `sundial-base-128m`):

| Lookback | Forecast horizon | # samples generated | Wall-clock | Attributed to |
|---|---|---|---|---|
| 672 | 16 | 1 | 249 ms | (baseline) |
| 2880 | 16 | 1 | 510 ms | FlashAttention |
| 2880 | 720 | 1 | 510 ms | Multi-Patch Prediction |
| 2880 | 1440 | 1 | 789 ms | KV Cache |
| 2880 | 720 | 20 | 949 ms | Shared Condition (20 Monte-Carlo samples for a full predictive distribution) |

**Why this matters for P10:** generating a **20-sample empirical predictive distribution** (enough for reasonable quantile/CI estimation) for a 720-step horizon from a 2880-length lookback takes **<1 second on an M1 Pro CPU** (no GPU) — i.e., CPU-only, Apple-Silicon, sample-based uncertainty quantification from a TS foundation model is cheap enough to run live on the target M5 Mac. This is a *proxy*, not a direct M5 measurement, and it's for the **TS branch**, not FinBERT/LLM text encoding — the brief's specific ask (FinBERT / mlx-lm / embedding-model throughput on Apple Silicon) is still **unanswered**; searches for it were rate-limited this pass and are queued for retry. No fabricated numbers inserted in the interim.

### 2.7 Explicit prior-art searches (hit / nothing-found log)

- `web_search`: "FinBERT yiyanghkust finbert-tone Huang Wang Yang Contemporary Accounting Research" → **hit** (confirmed via direct HF card fetch).
- `web_search`: "Time-MMD MM-TSFlib NeurIPS 2024 ... github" → **hit**, confirmed via direct GitHub fetch.
- `web_search`: "From News to Forecast" NeurIPS 2024 → **hit**, confirmed via direct GitHub README fetch.
- `web_search`: "Are Language Models Actually Useful for Time Series Forecasting" Tan NeurIPS 2024 → **hit**, confirmed directly (GitHub `BennyTMT/LLMsForTimeSeries`, NeurIPS 2024 **Spotlight**, "PAttn" baseline).
- `web_search`: "Context is Key" CiK NeurIPS 2024 → found arXiv:2410.18959 + OpenReview id `ReSNVjuPpw` + GitHub `ServiceNow/context-is-key-forecasting`; **OpenReview forum fetch blocked by bot-check ("Verifying your browser")** — not independently confirmed via direct fetch this session (logged §5).
- `web_search`: "StockNet Xu Cohen ACL 2018 ... accuracy MCC" → **hit**, cross-checked against 2 directly-opened GitHub repos.
- `web_search`: "SEP WWW 2024 stock prediction ... large language model" → **rate-limited twice**, not yet resolved.
- `web_search`: "MAN-SF multi-pronged attention stock prediction Sawhney" → **rate-limited**, not yet resolved.
- `web_search`: "news sentiment tweet volume predicts stock volatility not direction" → **rate-limited**, queued for retry.
- `web_search`: "FinBERT inference throughput Apple Silicon ... mlx benchmark" → **rate-limited**, queued for retry.
- Direct fetch attempts that **failed outright** (logged so the next pass doesn't repeat them blindly): `arxiv.org/abs/2304.07619` (×3, TimeoutError), `export.arxiv.org/abs/2512.23847` and `/2304.07619` (TimeoutError), `arxiv.org/html/2304.07619v6` (transport failure), `advisoranalyst.com/...` (transport failure), `alphaarchitect.com/...` (403), `openreview.net/forum?id=ReSNVjuPpw` (bot-check page, not the content). Working alternative pattern discovered: **`ar5iv.labs.arxiv.org/html/<id>`** loads when `arxiv.org/abs/<id>` times out.

---

## (3) Implications / innovation room / pitfalls for our design

_(pending)_

---

## (4) Source table

| URL | Title | Date | Maturity | Claim used |
|---|---|---|---|---|
_(pending)_

---

## (5) Leads not verified (UNVERIFIED — not opened this session)

_(pending)_
