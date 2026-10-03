# R5 — What Companies Ship Today (Public Material Only) + Lessons from Competitions

Status: IN PROGRESS (incremental write-up; skeleton created first per operating constraints)
Research window target: ~30 min / ~25 sources, whichever first.
Date of research: 2026-10-04 (IST)

## 1. TL;DR
(pending — fill in after sources gathered)

## 2. "What companies ship today" table

| Company | Product | Outputs | Dedup / Novelty / Credibility | Uncertainty published? | Source |
|---|---|---|---|---|---|
| (pending) | | | | | |

## 3. Details
(pending)

### 3.1 News/alt-data analytics vendors

**RavenPack / Bigdata.com** (vendor claim + verified primary doc). Bigdata.com is RavenPack's newer "AI grounding layer for finance" product, built on RavenPack's EDGE Analytics engine [S5.1]. Verified concretely from their own engineering blog [S5.2] (dated July 20, 2026 — within the research window, so treat as current):
  - Two shipped signal products: (1) **Entity Sentiment API** (`/v1/entity-sentiment/`), daily, historical, for backtesting/monitoring; (2) **Sentiment Tearsheet**, real-time (90-day rolling window), chunk-level, for "what's driving sentiment right now" inside chat agents (Claude/ChatGPT/Copilot).
  - **Daily sentiment formula (exact, published)**: day's sentiment is a weighted average of event-level sentiment where weight = `(relevance/100)² × (novelty/90)²` — i.e., relevance and novelty are first-class, explicit multiplicative weights on every event, squared to suppress marginal/repetitive stories. This is a direct, public answer to "how do you combine relevance+novelty+sentiment."
  - **Sentiment pressure**: z-score of the 90-day moving average of sentiment against the company's own trailing-year distribution, normalized to [-1,1]; |pressure| > 0.9 flagged "statistically unusual."
  - **Abnormal media attention**: same z-scoring treatment applied to coverage *volume* instead of tone (dedup/novelty-adjacent — catches volume spikes from either bad news spreading or neutral news like product launches).
  - Chunk-level sentiment (Bigdata.com's own addition on top of RavenPack EDGE): a transformer trained on financial news/corporate-event coverage scores each document *chunk* from -1 to +1, explicitly described as measuring "likely market impact, not linguistic tone."
  - **No published prediction interval / confidence bound** on any of these three signals in this post — outputs are point values (floats) and z-scores, not distributions. This is a concrete gap: RavenPack publishes a stable, reproducible *signal* pipeline but not an uncertainty band per prediction, which is exactly what conformal prediction could bolt on top of (e.g., calibrate residuals of a price-impact model conditioned on `sentiment_pressure` bucket).
  - Source ranking / credibility: product literature (vendor claim, not independently verified by us this session) states sources are weighted by quality/timeliness/historical reliability [S5.1 summary via search, unopened primary]; the WRDS RavenPack Analytics documentation PDF is the normal citable primary source for this but was not opened directly in this session (see Leads not verified).

**LSEG MarketPsych Analytics (LMA)** — verified from LSEG's own product page [S5.3]: the core engine is now called the "Text Tagging Engine" (formerly "NLP Engine"). Key verified claim, directly quoted: *"Unlike LLMs, it's deterministic and built for disambiguation, delivering consistent results essential for financial AI workflows."* This is a vendor positioning itself explicitly AGAINST generative LLM non-determinism for production financial tagging — relevant evidence for the hackathon's "trust" angle: industry's own framing is that determinism/reproducibility of entity+sentiment tagging is a selling point, separate from any generative layer. Backed by "20+ years of expert-built libraries." Per unopened secondary summaries (not independently verified this session, flagged below): >100 proprietary scores per entity, 60-second update cadence, spam/dedup filtering, coverage of 100,000+ companies / 252 countries, history to 1998.

**Bloomberg / BloombergGPT + Terminal AI**: Bloomberg's own press release was blocked by bot-detection on fetch this session (see Leads not verified) — claims below are from the arXiv paper only, which IS a primary Bloomberg-authored source (BloombergGPT paper, Wu et al., arXiv:2303.17564, Bloomberg-affiliated authors), not yet re-opened directly this session (queued next). Bloomberg Terminal's AI product page (professional.bloomberg.com/products/bloomberg-terminal/ai/) rendered almost no static content (JS-gated) [S5.4] — could not verify specifics of "AI-powered news summaries" beyond the tagline "Reimagine the way you discover, analyze and act on information on the Terminal with Bloomberg AI." Treat Jan-2025 "AI summaries" / earnings-call-summary claims as UNVERIFIED (search-engine-reported only) until a primary Bloomberg page is opened.

**AlphaSense** — verified directly from AlphaSense's own Help Center [S5.5], which is unusually transparent for a vendor. Exact quoted methodology:
  - Per-sentence classification: positive/negative/neutral **with an explicit confidence value** (example given: "99% confidence this statement is positive"). This is the clearest example found this session of a vendor publishing a genuine per-prediction confidence number (model classification confidence, not a calibrated conformal interval).
  - Document score = (count positive − count negative) / total statements, then **normalized** two ways: (a) by the confidence of each prediction, (b) against the mean/stdev of all transcripts in the trailing 2 years, rescaled to an interpretable **[-99, +99]** band where 0 = average, ±40 = top/bottom 20%, ±99 = top/bottom 2%.
  - Explainability: model highlights the specific phrases/sentences driving each prediction (a form of attribution, not a statistical bound).
  - Applied mainly to earnings-call transcripts ("Event Transcripts"), with visual red/green underlining in-product and a company-profile-level "Earnings Call Sentiment" trend.
  - This is the strongest "uncertainty-adjacent" vendor feature found in thread 1 so far — it's classification confidence propagated into a normalization step, not a prediction interval on a future return, so still a gap vs. what the hackathon brief wants (conformal coverage guarantee on a price-relevant target).

**Dow Jones Factiva / DNA**: developer.dowjones.com confirms (thin static content, [S5.6]) the existence of Factiva Analytics APIs with a company-identity endpoint feeding other analytics APIs; full taxonomy/methodology detail was not retrievable as rendered static text this session (likely JS/auth-gated docs) — treat deeper claims (industry/region/topic taxonomy codes, dedup logic) as UNVERIFIED pending direct doc access.

**Dataminr** — confirmed directly from dataminr.com/ai-platform/ [S5.7]: markets itself as "Multi-Modal Fusion AI" fusing >1M public sources (text in 150 languages + images/video/audio/sensor) for "Event, Threat, and Risk Discovery" — positioned for speed/breadth (real-time alerting), not for financial sentiment scoring per se. No relevance/novelty/credibility scoring methodology or uncertainty measure was visible in the static page content retrieved; deeper claims (50+ proprietary LLMs, "99.5% accuracy," $318M DoD contract) come only from the search-engine summary and are UNVERIFIED (not opened directly this session) — flagged below.

**Permutable AI** — confirmed directly from permutable.ai homepage [S5.8]: positions itself as turning "global information flows into research signals across macro, commodities and geopolitical risk," claims Hedgeweek "Technology Provider of the Year: Innovation" award, and explicitly separates "news/narratives/events" into "structured, explainable data" as "an additional predictive input." No methodology specifics (index construction, -1/+1 scaling, dedup) or uncertainty measure visible on the homepage itself — deeper claims about composite -1..+1 indices and point-in-time backtesting rigor are search-summary-only and UNVERIFIED this session.

**Accern, Alexandria Technology, Context Analytics (Amareos), StockTwits** — not yet independently fetched this session (searches for the latter two were rate-limited); see Leads not verified. Search-summary-only claim for Accern (unverified): 5-step pipeline (ingest → NLP extraction → sentiment/relevance/entity scoring → story/event clustering → impact+source-rank scoring) delivered via no-code platform + REST API, docs at docs.accern.com (not opened this session).

**S&P Global / Kensho Textual Data Analytics**: spglobal.com product page returned **HTTP 403** on fetch this session — not independently verified. Search-reported (unverified) claim: 800+ descriptive/predictive metrics from earnings-call transcripts (Net Positivity, Positivity-to-Negative, language complexity, transparency), built on bag-of-words/TF-IDF/cosine-similarity techniques; no published per-signal confidence score in public docs per the search summary. Flagged UNVERIFIED below pending a successful direct fetch.



### 3.2 Quant funds / market makers — public NLP/LLM + decay material
(pending)

### 3.3 Shipped uncertainty quantification in forecasting products
(pending)

### 3.4 Integrity / manipulation-detection products
(pending)

### 3.5 Competitions
(pending)

## 4. Where a student build can borrow from or beat them
(pending)

## 5. Source table

| # | URL | Title | Org | Date | Maturity | Claim used |
|---|---|---|---|---|---|---|
| S5.1 | https://bigdata.com/ | Bigdata.com – The AI grounding layer for finance | RavenPack | accessed 2026-10-04 (page dated "Oct 2, 2026") | in production | Product scope: RAG grounding layer over news/filings/transcripts/alt-data; 25+ yrs history, 200+ premium sources |
| S5.2 | https://docs.bigdata.com/blog/market-data/entity-sentiment-signals | Sentiment in Bigdata.com: The Trend and the Story | RavenPack (Bigdata.com docs/blog) | July 20, 2026 | in production (live API, reproducible numbers shown) | Exact formulas for daily_sentiment weighting `(relevance/100)²×(novelty/90)²`, sentiment_pressure z-score, abnormal_media_attention; no published confidence interval |
| S5.3 | https://www.lseg.com/en/data-analytics/market-data/quantitative-economic-data-solutions/marketpsych-analytics-and-models | MarketPsych: NLP & Predictive Analytics in Finance | LSEG | undated, accessed 2026-10-04 | in production | "Text Tagging Engine... deterministic and built for disambiguation" vs. LLMs; 20+ yr libraries |
| S5.4 | https://professional.bloomberg.com/products/bloomberg-terminal/ai/ | AI on Bloomberg (product page) | Bloomberg | undated, accessed 2026-10-04 | in production (marketing page; JS-gated, minimal static content retrieved) | Confirms existence of "Bloomberg AI" terminal feature set; no technical detail retrievable this session |
| S5.5 | https://help.alpha-sense.com/hc/en-us/articles/41711901352211-Sentiment-Analysis | Sentiment Analysis (Help Center) | AlphaSense | undated, accessed 2026-10-04 | in production | Exact scoring formula, per-sentence confidence value, [-99,+99] normalized scale |
| S5.6 | https://developer.dowjones.com/site/docs/factiva_apis/index.gsp | Factiva APIs (Developer Platform) | Dow Jones | undated, accessed 2026-10-04 | in production (docs portal; thin static content) | Confirms Factiva Analytics APIs incl. company-identity endpoint exist; no deep methodology retrieved |
| S5.7 | https://www.dataminr.com/ai-platform/ | AI Platform | Dataminr | undated, accessed 2026-10-04 | in production | "Multi-Modal Fusion AI," >1M public sources, 150 languages + image/video/audio/sensor fusion |
| S5.8 | https://permutable.ai/ | Permutable (homepage) | Permutable AI | undated, accessed 2026-10-04 | in production | Positioning: news/narratives/events → "structured, explainable data" as predictive input; Hedgeweek award claim |

## 6. Leads not verified (UNVERIFIED)
(pending — list items not opened this session)
