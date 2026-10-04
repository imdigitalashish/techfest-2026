# Data attribution

- **StockNet** (Xu & Cohen, ACL 2018; https://github.com/yumoxu/stocknet-dataset, MIT licence): tweets and prices for 87 US stocks.
  This bundle contains only *derived* features (price/volatility features, per-post sentiment and trust scores) for the
  calibration and test periods, plus the original tweet texts and account metadata for the 3 showcased days that have posts
  (`showcase.json`). The full tweet corpus is not redistributed here.
- **Twitter Financial News Sentiment** (`zeroshot/twitter-financial-news-sentiment`, MIT licence): training data for the
  logistic-regression sentiment head in `scorer_head.json`.
- **all-MiniLM-L6-v2** (`sentence-transformers/all-MiniLM-L6-v2`, Apache-2.0): the frozen sentence encoder (not bundled;
  loaded from the local Hugging Face cache).
- **VADER** (Hutto & Gilbert, ICWSM 2014; `vaderSentiment`, MIT licence): fallback scorer only.

Regenerate with `demo/export.py` (see its docstring).
