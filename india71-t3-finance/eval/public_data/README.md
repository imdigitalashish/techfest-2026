# Real public data (india71-t3-finance)

All files in `derived/` are transcribed or parsed from official documents opened on 2026-10-04. Raw PDFs are kept in the gitignored `.cache/src/` and `.data/`.

| File | What | Source (opened 2026-10-04) | How produced |
|---|---|---|---|
| `derived/pmjdy_inoperative_by_state_2025-07-31.csv` | State/UT-wise PMJDY accounts and inoperative accounts as of 31 Jul 2025 (36 rows; totals 56,03,84,490 and 13,04,52,845 match the annexure's Total row) | Lok Sabha Unstarred Q. 4090, answered 18 Aug 2025, Ministry of Finance (DFS): https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU4090_LCDFLT.pdf?source=pqals | `curl` the PDF to `.cache/src/ls_au4090_2025.pdf`; text via pdfplumber; rows parsed with a regex (see `eval/public_data/parse_ls4090.py`) |
| `derived/pmjdy_inoperative_trend.csv` | PMJDY accounts, women's accounts and inoperative accounts, Mar 2021 – Dec 2025 | Rajya Sabha Unstarred Q. 2636 (12 Aug 2025) Annexure-II; Lok Sabha USQ 4090 (18 Aug 2025); Lok Sabha USQ 1333 (8 Dec 2025) | Transcribed by hand from the annexures (7 rows); shares computed |

| `derived/findex2025_india_account_inactive.csv` | India, 2021 and 2024: account ownership and inactive-account share (% of adults 15+) by group; `inactive_share_of_owners` = inactive_t_d / account_t_d (derived) | World Bank, Global Findex Database 2025 (GlobalFindexDatabase2025.csv; indicators account_t_d, inactive_t_d). https://thedocs.worldbank.org/en/doc/be6615202d1f08a25855c8ac2d615122-0050012025/related/GlobalFindexDatabase2025.csv (download page https://www.worldbank.org/en/publication/globalfindex/download-data) — downloaded and read 2026-10-04. | read the CSV (`.data/findex/`, 17.6 MB, gitignored) with pandas; filter `codewb == 'IND'` |

Caveats: the definition wording differs across answers (USQ 4090 cites the RBI 2009 guideline "no transactions ... over two years"; USQ 1333 says "no customer induced transactions ... over a period of two years"). The as-of date of the USQ 1333 counts is not stated. Gender-wise and range-wise inoperative data are "not maintained centrally" (USQ 2636 Annexure-II footnote; USQ 1333).

Reproduce: `python eval/public_data/parse_ls4090.py` (from `india71-t3-finance/`).
