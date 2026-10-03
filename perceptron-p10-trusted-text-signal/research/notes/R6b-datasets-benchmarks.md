# R6b — Datasets & Benchmarks for Text+Price Fusion (FNSPID, Kaggle stocknews, sentiment eval sets, 2025–26 HF releases, price feeds)

Status: IN PROGRESS (skeleton created first per operating constraints; appended after every 2 sources)
Research window target: ~15 sources / ~20 min, whichever first.
Date of research: 2026-10-04 (IST)
Already verified by lead, NOT re-verified here: StockNet (yumoxu/stocknet-dataset, MIT, 88 stocks, tweets 2014–2015, prices 2012-09→2017-09); FNSPID on HF (Zihan1004/FNSPID — All_external.csv 5731MB, nasdaq_exteral_data.csv 23233MB, full_history.zip 590MB).

## 1. TL;DR + ranked recommendation
(pending — fill in after sources gathered)

## 2. Catalog table

| Dataset | URL | Text type | Dates | Size | License | Mirror? |
|---|---|---|---|---|---|---|
| (pending) | | | | | | |

## 3. Details

### 3.1 FNSPID
**Paper**: KDD 2024 Applied Data Science Track (confirmed by GitHub repo banner: "FNSPID has been selected as KDD2024 Applied Data Science Track Paper" [S6b.5]). arXiv:2402.06698, "FNSPID: A Comprehensive Financial News Dataset in Time Series", Zihan Dong, Xinyu Fan, Zhiyuan Peng (NC State + Sichuan Univ.), q-fin.ST, submitted Feb 2024 [S6b.1 tag on HF API; S6b.4 full abstract via huggingface.co/papers mirror].

**Exact abstract claim** [S6b.4, huggingface.co/papers/2402.06698, abstract text]: *"29.7 million stock prices and 15.7 million time-aligned financial news records for 4,775 S&P500 companies, covering the period from 1999 to 2023, sourced from 4 stock market news websites."* Three paper findings: (1) dataset size/quality boosts market-prediction accuracy; (2) adding sentiment scores modestly improves transformer-based models; (3) a reproducible update procedure is provided.

**Column schema of `Stock_news/All_external.csv`** — verified directly by a **3KB byte-range request** (`curl -r 0-3000`, not a full download) against the HF `resolve/main` URL [S6b.6]:
```
Date,Article_title,Stock_symbol,Url,Publisher,Author,Article,Lsa_summary,Luhn_summary,Textrank_summary,Lexrank_summary
```
Sample rows are dated 2020-05/06, ticker `A` (Agilent), `Publisher=Benzinga Insights`/analyst names, `Url` pointing to benzinga.com. **Notable**: in every sampled row the raw `Article` column is empty (full body not populated), while four pre-computed extractive-summary columns (LSA, Luhn, TextRank, LexRank — classic unsupervised summarization algorithms) are present as columns but also empty in this particular byte range (likely populated only for a subset of rows / this is literally row 1 of the file so may not be representative — only a 3KB sample was read, not the full file, so sparsity can't be generalized from this alone).

**#tickers / date range**: 4,775 S&P500 tickers, 1999–2023 per abstract [S6b.4]. Note this is broader than the already-verified per-file sizes (Stock_news/All_external.csv 5731MB, nasdaq_exteral_data.csv 23233MB, Stock_price/full_history.zip 590MB) — confirmed again via HF API `usedStorage: 47052993116` bytes (~43.8 GiB total across all three files) [S6b.1].

**License — IMPORTANT CONTRADICTION FOUND**: 
  - HF dataset README (`Zihan1004/FNSPID`, last modified 2024-04-09) [S6b.2] states: *"This dataset is available under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC-4.0) license... Commercial use of this code or dataset without explicit permission from the original authors is strictly prohibited."*
  - GitHub repo README (`Zdong104/FNSPID_Financial_News_Dataset`, banner dated 07/24/2025) [S6b.5] states: *"We will stop the maintainance for this repo. All the right for commercial use and research use are released. Feel free to use :)."* — immediately followed further down by an unchanged "Prohibition of Commercial Use" disclaimer section contradicting the banner.
  - **Practical read for hackathon use**: research/non-commercial use is unambiguously fine either way (CC BY-NC-4.0 explicitly permits non-commercial research). The "rights released" banner is ambiguous/inconsistent with the disclaimer text immediately below it in the same README, so do NOT rely on it for any commercial claim — treat the dataset as CC BY-NC-4.0 (research-only) for citation purposes.

**Per-ticker subsets**: not found as separate HF repos in the single search run so far (see §3.4 / Leads not verified) — FNSPID ships as 3 monolithic files, not pre-split per ticker; any per-ticker slicing would be a local `pandas` groupby on `Stock_symbol` after a partial/streaming read (duckdb/polars can filter the 23GB nasdaq_exteral_data.csv without loading fully).

**Underlying scraper source**: `data_processor/` folder in the GitHub repo contains `price_news_integrate.py`, `score_by_gpt.py` (GPT-based sentiment scoring — pre-existing LLM-sentiment-labeled subset may exist under `news_data_sentiment_scored_by_gpt/`), `summarize.py` [S6b.5 directory listing] — worth a follow-up fetch if time permits (not opened this session, see Leads not verified) since it may contain a much smaller, pre-sentiment-scored sample suitable for a walking skeleton instead of the 23GB raw file.

### 3.2 Kaggle Daily News for Stock Market Prediction (aaron7sun/stocknews)
**Kaggle page metadata** (og:description + JSON-LD schema.org Dataset description, fetched raw HTML directly — no Kaggle credentials needed for the public page) [S6b.8]: *"Using 8 years daily news headlines to predict stock market movement."* Full author-written description (exact quote):
  - **Two channels**: (1) News — Reddit `/r/worldnews` headlines, top-25-by-vote per date, **range 2008-06-08 to 2016-07-01**; (2) Stock — DJIA, **range 2008-08-08 to 2016-07-01**, "downloaded directly from Yahoo Finance."
  - **Three files**: `RedditNews.csv` (2 cols: date, headline, 25 rows/date); `DJIA_table.csv` (raw Yahoo Finance OHLCV); `Combined_News_DJIA.csv` (**27 columns**: Date, Label, Top1...Top25 — pre-joined for convenience).
  - **Label definition (exact)**: binary — `1` when DJIA Adj Close rose or stayed the same, `0` when it decreased.
  - **Author-recommended split**: train = 2008-08-08 → 2014-12-31, test = 2015-01-02 → 2016-07-01 (≈80/20), **evaluation metric: AUC**. This is a ready-made, non-leaky backtest split directly from the dataset author — reusable as-is for a baseline.

**GitHub mirror — verified working, with exact byte sizes** [S6b.10], repo `jonx0037/sentiment-regime-detector`, path `data/kaggle/stocknews/`:
  - `Combined_News_DJIA.csv` — **5,617,630 bytes** (~5.4 MB) — `https://raw.githubusercontent.com/jonx0037/sentiment-regime-detector/207b9b5fe65279c70b6f3dad98c8627f9957aad9/data/kaggle/stocknews/Combined_News_DJIA.csv`
  - `RedditNews.csv` — **9,099,659 bytes** (~8.7 MB) — same path pattern
  - `upload_DJIA_table.csv` — **167,083 bytes** (~163 KB) — same path pattern
  - A companion file in the same repo, `data/datasets_inventory.csv` [S6b.9, found via GitHub code search `"Combined_News_DJIA" extension:csv`], independently documents row counts consistent with the above: RedditNews ~76,600 rows (2008-06-08→2016-07-01), Combined_News_DJIA ~3,973 rows (2008-08-08→2016-07-01), DJIA table 1,988 rows — all matching the Kaggle author's stated date ranges. This repo also inventories other relevant Kaggle sets in the same manifest: `equinxx/stock-tweets-for-sentiment-analysis-and-prediction` (stock_tweets.csv, 17MB, 2021-09-30→2022-09-29) and `ankurzing/sentiment-analysis-for-financial-news` (Financial PhraseBank `all-data.csv`, 656KB) — both candidate leads, not yet independently opened this session (see Leads not verified).
  - **Caveat**: this is a third-party research repo's data folder, not an official/blessed mirror — treat the byte-identical match to Kaggle's known file sizes (publicly reported elsewhere as ~5.4MB/8.7MB/163KB) as good corroborating evidence of fidelity, but there's no checksum cross-check performed this session.

### 3.3 Labelled financial sentiment eval sets
**zeroshot/twitter-financial-news-sentiment** [S6b.11, HF API]: **MIT license**. 11,932 documents (per dataset description text), 3-class: `Bearish`/`Bullish`/`Neutral`. Files: `sent_train.csv`, `sent_valid.csv`, `sent_dataset_meta.txt`. Size category tag `10K<n<100K`. `usedStorage: 19,190,537` bytes (~18.3 MB total). Collected via Twitter API (per description). Split-level row counts not yet pulled (README full text or CSV header not yet fetched this session — queued next if time allows).
(Financial PhraseBank + FiQA — pending next batch)

### 3.4 2025–2026 HF releases + manipulation-labelled sets
(pending)

## 4. Price sources (yfinance reliability 2025–26, Stooq)
(pending)

## 5. Source table

| # | URL | Title | Org | Date | Maturity | Claim used |
|---|---|---|---|---|---|---|
| S6b.1 | https://huggingface.co/api/datasets/Zihan1004/FNSPID | HF dataset API metadata | HF / Zihan1004 | lastModified 2024-04-09, accessed 2026-10-04 | stable (frozen since 2024) | File list, arxiv tag 2402.06698, usedStorage=47,052,993,116 bytes |
| S6b.2 | https://huggingface.co/datasets/Zihan1004/FNSPID/raw/main/README.md | FNSPID dataset card | HF / Zihan1004 | accessed 2026-10-04 | stable | CC BY-NC-4.0 license text, citation, 10M<n<100M size category |
| S6b.4 | https://huggingface.co/papers/2402.06698 | FNSPID paper mirror (full abstract) | arXiv via HF Papers | submitted 2024-02-13 | published (KDD'24) | Exact abstract: 29.7M prices, 15.7M news, 4,775 tickers, 1999–2023, 4 news sites |
| S6b.5 | https://github.com/Zdong104/FNSPID_Financial_News_Dataset (README via GitHub API) | FNSPID_Financial_News_Dataset repo | Zdong104 (author) | banner dated 07/24/2025, accessed 2026-10-04 | maintenance stopped (per banner) | KDD2024 selection confirmation; license-banner vs. disclaimer contradiction; data_processor/ folder contents (GPT sentiment scoring scripts) |
| S6b.6 | https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/Stock_news/All_external.csv (byte range 0-3000 only) | All_external.csv header+sample | HF / Zihan1004 | accessed 2026-10-04 | stable | Exact column schema: Date,Article_title,Stock_symbol,Url,Publisher,Author,Article,Lsa_summary,Luhn_summary,Textrank_summary,Lexrank_summary |
| S6b.8 | https://www.kaggle.com/datasets/aaron7sun/stocknews (raw HTML: meta tags + JSON-LD) | Daily News for Stock Market Prediction | Kaggle / aaron7sun | undated, accessed 2026-10-04 | stable (classic dataset, unchanged for years) | Full author description: 2 channels, 3 files, 27-col schema, binary label rule, train/test split recommendation, date ranges |
| S6b.9 | GitHub code search `"Combined_News_DJIA" extension:csv` → jonx0037/sentiment-regime-detector `data/datasets_inventory.csv` | datasets_inventory.csv | jonx0037 (GitHub user) | repo accessed 2026-10-04 | third-party research repo | Independent row-count/date-range manifest for RedditNews/Combined_News_DJIA/DJIA_table + leads for stock_tweets and Financial PhraseBank Kaggle mirrors |
| S6b.10 | https://github.com/jonx0037/sentiment-regime-detector/tree/main/data/kaggle/stocknews (dir listing via API) | sentiment-regime-detector repo data folder | jonx0037 (GitHub user) | accessed 2026-10-04 | third-party research repo (working mirror) | Exact byte sizes of all 3 mirrored CSVs; raw.githubusercontent.com download URLs |
| S6b.11 | https://huggingface.co/api/datasets/zeroshot/twitter-financial-news-sentiment | HF dataset API metadata | HF / zeroshot | lastModified 2024-02-23, accessed 2026-10-04 | stable | MIT license, 11,932 docs, 3-class Bearish/Bullish/Neutral, file list, usedStorage=19,190,537 bytes |

## 6. Leads not verified (UNVERIFIED)
(pending — list items not opened this session)
