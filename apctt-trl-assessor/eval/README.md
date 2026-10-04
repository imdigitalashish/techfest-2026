# Eval harness — v0

All numbers below come from committed runs. Each row names the script, the split and the command that reproduces it. Machine: Apple M5, 24 GB, CPU only. The machine was heavily overloaded during these runs (load ≈65–80, swap ≈49.5/50 GB), so **timings are pessimistic**.

## Data and split
- NASA TechPort public API, seeded random sample of 11,427 of 21,046 projects (fetched 2026-10-04) → 8,587 rows with a description of at least 200 characters and a TRL ([`data/techport/`](../data/techport/)).
- Text = title + description + benefits. **No metadata features.**
- Grouped 80/20 split by normalised title (removes "Phase I/II", "SBIR/STTR", years), seed 20261004. Test ids are frozen in [`splits/`](splits/).

## Results — label `trl_current` (train 6,352 / test 1,657)
Script `eval/baseline_numpy.py` (committed in 287a7a3; run recorded HEAD d06a304). Features: hashed unigram+bigram (D=4096) log-TF·IDF, L2. Ridge alpha=1.0. Fit 201.7 s; predict 13.7 ms/doc (overloaded machine).

| Model | Exact | Within-1 | MAE ↓ | QWK | Precision over predicted classes* |
|---|---|---|---|---|---|
| Majority class (TRL 4) | 0.291 | 0.701 | 1.112 | 0.000 | 0.291 |
| Ridge on TRL value, rounded | 0.297 | 0.745 | 1.053 | **0.314** | 0.325 |
| Threshold-ridge (8× P(TRL>k)) → mode | 0.309 | 0.696 | 1.151 | 0.235 | 0.287 |
| Threshold-ridge → median | **0.312** | 0.745 | 1.042 | 0.302 | 0.335 |
| Threshold-ridge → expectation | 0.303 | **0.754** | **1.034** | 0.298 | **0.445** |

\*Averaged only over the classes the model predicts — **not** standard macro precision (which counts never-predicted classes as 0; e.g. the majority class scores 0.032 under the standard definition, see the sklearn table). Fixed in `baseline_numpy.py` for future runs (`macro_precision` = standard).

Reproduce (from `apctt-trl-assessor/`):
```
python data/techport/fetch_techport.py      # resumable; the sample above = first 11,427 of the seeded order
python data/techport/build_dataset.py
python eval/baseline_numpy.py --label trl_current --label trl_begin --label trl_end
```
Raw outputs: `results/baseline_np_v0_<label>.json`, ledger `results/results_numpy.tsv`, log `results/baseline_np_v0.log`.

**Reading (v0).** Text-only proposal-style descriptions carry a real but weak ordinal signal: QWK ≈0.30 against 0.00 for the majority class, and MAE 1.03–1.05 against 1.11. Within-1 is already 0.70 for the majority class because labels cluster at TRL 3–5, so **QWK and MAE are the informative metrics here, not within-1**. Decoding moves metrics in opposite directions (mode → exact; expectation → MAE / within-1; rounded regression → QWK). This is why C5 (metric-aware decoding) is a spike: the choice must follow the official metric. These are deliberately weak hashed-ridge baselines. The sklearn TF-IDF + logistic / cumulative-logit run (`eval/baseline_tfidf.py`) is pending: the overloaded machine could not import scipy in time.

## Results — `trl_begin` and `trl_end` (same script, run, split method and hyper-parameters)
| Label | Model | Exact | Within-1 | MAE ↓ | QWK | Precision over predicted classes* |
|---|---|---|---|---|---|---|
| `trl_begin` (train 6,794 / test 1,766) | Majority (TRL 2) | 0.357 | 0.746 | 1.008 | 0.000 | 0.357 |
| | Ridge, rounded | 0.360 | 0.828 | 0.860 | **0.263** | 0.296 |
| | Threshold-ridge → mode | 0.381 | 0.781 | 0.908 | 0.234 | 0.313 |
| | Threshold-ridge → median | **0.394** | 0.822 | **0.837** | 0.251 | 0.319 |
| | Threshold-ridge → expectation | 0.366 | **0.834** | 0.847 | 0.235 | 0.372 |
| `trl_end` (train 6,651 / test 1,719) | Majority (TRL 4) | 0.291 | 0.716 | 1.124 | 0.000 | 0.291 |
| | Ridge, rounded | 0.289 | 0.749 | 1.042 | **0.319** | 0.310 |
| | Threshold-ridge → mode | **0.328** | 0.691 | 1.138 | 0.258 | 0.294 |
| | Threshold-ridge → median | 0.321 | 0.756 | 1.029 | 0.315 | 0.464 |
| | Threshold-ridge → expectation | 0.289 | **0.767** | **1.024** | 0.297 | 0.471 |

Fit 320.3 s (begin) / 141.9 s (end); predict 17.8 / 21.4 ms/doc (overloaded machine). The majority class is the training mode.

**Reading.** All three label definitions show the same pattern: QWK ≈0.26–0.32 for text-only hashed ridge, a 0.12–0.17 MAE gain over the majority class, and decoding trading exact accuracy against MAE and QWK. `trl_begin` is the easiest by MAE because its labels concentrate at TRL 2–3. The primary label stays `trl_current` until the 10 Oct guide defines the target.

## Walking skeleton — end-to-end check (2026-10-04 08:12 IST)
`python -m components.skeleton.runner --train` fits the v0 threshold-ridge model on the TechPort `trl_current` **train** split (4.8 s). Then `python -m components.skeleton.runner --in .data/examples_in --out .data/examples_out` runs file → ParsedDocument → evidence → distribution → decision → gap analysis → `Assessment`, validated against `architecture/contracts/contracts.schema.json`. Contract tests: `python -m components.skeleton.test_skeleton` (6/6 pass, including empty, non-English and 200 kB inputs).

| Held-out TechPort doc (random, seed 7) | Gold `trl_current` | Predicted (median) | 80% interval | Evidence items | Latency |
|---|---|---|---|---|---|
| 96214 | 3 | 3 | [1, 6] | 0 | 8 ms |
| 17919 | 5 | 5 | [3, 6] | 1 | 13 ms |
| 103122 | 6 | 3 | [2, 4] | 0 | 27 ms |

3 docs in 0.11 s (26 docs/s, CPU, numpy only). Three examples are anecdotes, not a metric; the held-out metrics are the tables above. **Finding:** the rubric-wording lexicon (C3 v0) fires on only 0–1 sentences per TechPort description, so recall is the first target for C3's isolated metric and its ratchet.

## Results — sklearn TF-IDF baselines, `trl_current` (same frozen split; train 6,352 / test 1,657)
Script `eval/baseline_tfidf.py` (run recorded HEAD 27a87a3). Word 1–2-gram TF-IDF (sublinear, min_df 2, max_df 0.9, ≤200k features), C=4. Machine heavily loaded, so the logistic-regression fit took 2,373 s — timings not representative.

| Model | Exact | Within-1 | MAE ↓ | QWK | Macro-P (standard) | Macro-F1 |
|---|---|---|---|---|---|---|
| Majority class | 0.291 | 0.701 | 1.112 | 0.000 | 0.032 | 0.050 |
| Multinomial logreg → mode | **0.346** | 0.736 | 1.042 | 0.279 | 0.213 | 0.143 |
| Multinomial logreg → median | 0.342 | 0.757 | 0.981 | 0.283 | **0.277** | 0.126 |
| Ridge on value, rounded | 0.308 | **0.777** | 0.981 | **0.350** | 0.214 | 0.125 |
| Cumulative logit (Frank & Hall) → mode | 0.344 | 0.757 | 0.994 | 0.343 | 0.212 | **0.145** |
| Cumulative logit → median | 0.339 | 0.773 | **0.961** | 0.342 | 0.255 | 0.132 |
| Cumulative logit → expectation | 0.314 | 0.775 | 0.979 | 0.311 | 0.137 | 0.113 |

Full TF-IDF beats the 4,096-bin hashed features on every metric: QWK 0.314 → 0.350, MAE 1.034 → 0.961, exact 0.312 → 0.346. **Leakage caveat (from the 08:30 adversarial review):** about 14% of TechPort texts mention "TRL" explicitly, and some test descriptions or benefits duplicate training records. These numbers are therefore optimistic. A redacted, content-deduplicated v1 benchmark is next.

## Genre / source-shift study v0 (`eval/genre_shift.py` → `results/genre_shift_v0.json`)
Same numpy threshold-ridge model and features as the skeleton (hashed, D=4096). Label `trl_current`.

**A. Cross-source shift inside TechPort** (frozen split; SBIR/STTR = 54.6% of rows):
| Train on → test on | n train | n test | QWK (ridge) | MAE (ridge) | QWK (thr-median) |
|---|---|---|---|---|---|
| all → SBIR/STTR | 6,352 | 907 | 0.219 | 1.030 | 0.218 |
| SBIR/STTR → SBIR/STTR | 3,505 | 907 | 0.195 | 1.004 | 0.222 |
| NASA-internal → SBIR/STTR | 2,847 | 907 | **0.092** | 1.168 | 0.075 |
| all → NASA-internal | 6,352 | 750 | 0.332 | 1.081 | 0.317 |
| NASA-internal → NASA-internal | 2,847 | 750 | 0.345 | 1.053 | 0.340 |
| SBIR/STTR → NASA-internal | 3,505 | 750 | **0.126** | 1.319 | 0.085 |

**B. Input-length stress test** (model trained on full texts):
| Test input | QWK (ridge) | MAE (ridge) | QWK (thr-median) |
|---|---|---|---|
| full (title + description + benefits) | 0.314 | 1.053 | 0.302 |
| description only | 0.292 | 1.062 | 0.258 |
| first 60 words of description (abstract-length) | 0.192 | 1.149 | 0.157 |
| benefits only | 0.189 | 1.139 | 0.169 |
| title only | 0.109 | 1.188 | 0.112 |

**C. Paired genre test** — 204 papers DOI-linked from 98 TechPort projects (OpenAlex title + abstract, `data/openalex/fetch_linked_papers.py`). Each paper gets its project's `trl_current` as a noisy proxy label (TRL 2–8, mostly 3). The model is trained on 7,909 rows, excluding those projects and their title groups.
| Input for the same 204 items | Exact | Within-1 | MAE | QWK |
|---|---|---|---|---|
| Project description (thr-median) | 0.402 | 0.877 | 0.740 | 0.414 |
| Linked paper title + abstract (thr-median) | 0.348 | 0.755 | 0.941 | 0.212 |
MAE (ridge) paper − description = **+0.196** (bootstrap 95% CI [0.069, 0.319]). Correlation between the two expected-TRL predictions = 0.289.

**Reading.** Shift is the dominant risk, and it is large even inside one agency. A model trained on one writing source loses 60–75% of its QWK on the other. Abstract-length inputs lose about 40%. The same projects described in their papers lose about half their QWK. Robustness to genre and length must be the primary Round-1 objective. Training on pooled sources helps: "all" is best or near-best on both test sources, which argues for diverse training text, length augmentation and genre-invariant features. Caveat: paper labels are a project-level proxy (a paper can report an earlier stage than the project's current TRL).
