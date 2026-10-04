# NOTICE — Open Bandit Dataset extract

The files `obd_bts_all.csv.gz` and `obd_random_all.csv.gz` in this folder are derived from the **Open Bandit Dataset**. The dataset was built by **ZOZO, Inc.** from an A/B test on the ZOZOTOWN fashion e-commerce platform.

- **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
  - The `README` inside the official zip says: "This dataset is licensed under CC BY 4.0. https://creativecommons.org/licenses/by/4.0/".
  - Read on 2026-10-04 21:09 IST with an HTTP range request on the zip, using `eval/obd_zip_slice.py`.
  - The project lead verified the same line earlier that day.
- **Source:** https://research.zozo.com/data_release/open_bandit_dataset.zip (linked from https://research.zozo.com/data.html).
  - Members used: `open_bandit_dataset/random/all/all.csv` (complete) and `open_bandit_dataset/bts/all/all.csv` (a time-ordered prefix).
- **Citation** (as the dataset README requests): Yuta Saito, Shunsuke Aihara, Megumi Matsutani, Yusuke Narita. *A Large-scale Open Dataset for Bandit Algorithms.* arXiv:2008.07146 (2020). https://arxiv.org/abs/2008.07146
- **No endorsement:** neither ZOZO, Inc. nor the authors endorse this project or its findings.

## Changes made (CC BY 4.0 §3(a)(1)(B))

1. **Subset.**
   - Campaign "All" only.
   - Policies: Random (uniform) and Bernoulli Thompson Sampling (BTS).
   - Impressions with timestamps in [2019-11-24 00:00, 2019-11-27 12:00) UTC only.
2. **Aggregation.** Rows are collapsed into counts of identical records:
   - BTS: `hour, item, position, propensity, click, count`.
   - Random: `hour, item, position, click, pre_t0, count`.
   - `hour` is whole UTC hours since 2019-11-24 00:00.
   - `pre_t0` flags the 3 Random impressions logged before the first BTS impression (2019-11-24 00:00:00.047846 UTC).
3. **Dropped fields.** Exact timestamps, user features 0–3, user–item affinities and `item_context.csv` are not included.
4. **Propensities.**
   - Kept exactly as parsed from the CSV by pandas into float64, and written as Python's shortest round-trip repr.
   - Not rounded.
   - The Random arm's propensity is 0.0125 for every row, so it is not stored.

The regeneration command, the sha256 of each file, the row counts and the equality checks against the raw rows and the committed results are in `extract_manifest.json`. The script that produces them is `../make_extract.py`.
