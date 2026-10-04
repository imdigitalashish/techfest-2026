# C3 text_scorer — research note

_Lead, 4 Oct 2026. Sources: [`../notes/R3-text-timeseries-fusion.md`](../notes/R3-text-timeseries-fusion.md) §2.1, [`../landscape.md`](../landscape.md) §3._

- **Tonight's baseline:** VADER (Hutto & Gilbert, ICWSM 2014; social-media lexicon) plus a hand-set 40-term finance lexicon (`components/text_scorer/vader.py`, labelled heuristic). It scores 119,641 tweets in 4.3 s.
- **Next:** `ProsusAI/finbert` (Araci 2019; Financial PhraseBank) and `yiyanghkust/finbert-tone` (Huang, Wang & Yang, CAR 2023; 4.9B-token corpus). The wrapper `finbert.py` (MPS, text-hash cache) is ready; its weights (~440 MB) were deferred under lean mode.
- **LLM scorers** (e.g. small instruction models via MLX) only with a look-ahead test. A date-only recall probe ("Lookahead Propensity", arXiv:2512.23847) shows LLMs recall pre-cutoff outcomes. For 2014–2016 data, any LLM trained after 2016 is suspect.
- **Isolated metric (to run):** macro-F1 on a labelled financial-tweet set (`zeroshot/twitter-financial-news-sentiment` on HF — size and licence **UNVERIFIED**), plus the information coefficient of daily mean sentiment with next-day returns on the training period.
- **Innovation room:**
  - Calibrated per-document uncertainty (temperature scaling) feeding the trust weight.
  - Robustness to homoglyph / hidden-text manipulation, which Rizvani et al. (SaTML 2026) used to cut returns by up to 17.7 pp: Unicode normalisation (NFKC) and invisible-character stripping before scoring — cheap and testable.
  - Cashtag-collision filtering ($TOT, $UN and similar tickers are common words).
