# Eval harness — v0

All numbers below come from committed runs. Each row names the script, the split and the command that reproduces it. Machine: Apple M5, 24 GB, CPU only. The machine was heavily overloaded during these runs (load ≈65–80, swap ≈49.5/50 GB), so **timings are pessimistic**.

## Data and split
- NASA TechPort public API, seeded random sample of 11,427 of 21,046 projects (fetched 2026-10-04) → 8,587 rows with a description of at least 200 characters and a TRL ([`data/techport/`](../data/techport/)).
- Text = title + description + benefits. **No metadata features.**
- Grouped 80/20 split by normalised title (removes "Phase I/II", "SBIR/STTR", years), seed 20261004. Test ids are frozen in [`splits/`](splits/).

## Results — label `trl_current` (train 6,352 / test 1,657)
Script `eval/baseline_numpy.py` (committed in 287a7a3; run recorded HEAD d06a304). Features: hashed unigram+bigram (D=4096) log-TF·IDF, L2. Ridge alpha=1.0. Fit 201.7 s; predict 13.7 ms/doc (overloaded machine).

| Model | Exact | Within-1 | MAE ↓ | QWK | Macro precision* |
|---|---|---|---|---|---|
| Majority class (TRL 4) | 0.291 | 0.701 | 1.112 | 0.000 | 0.291 |
| Ridge on TRL value, rounded | 0.297 | 0.745 | 1.053 | **0.314** | 0.325 |
| Threshold-ridge (8× P(TRL>k)) → mode | 0.309 | 0.696 | 1.151 | 0.235 | 0.287 |
| Threshold-ridge → median | **0.312** | 0.745 | 1.042 | 0.302 | 0.335 |
| Threshold-ridge → expectation | 0.303 | **0.754** | **1.034** | 0.298 | **0.445** |

\*Macro precision over the classes the model actually predicts.

Reproduce (from `apctt-trl-assessor/`):
```
python data/techport/fetch_techport.py      # resumable; the sample above = first 11,427 of the seeded order
python data/techport/build_dataset.py
python eval/baseline_numpy.py --label trl_current --label trl_begin --label trl_end
```
Raw outputs: `results/baseline_np_v0_<label>.json`, ledger `results/results_numpy.tsv`, log `results/baseline_np_v0.log`.

**Reading (v0).** Text-only proposal-style descriptions carry a real but weak ordinal signal: QWK ≈0.30 against 0.00 for the majority class, and MAE 1.03–1.05 against 1.11. Within-1 is already 0.70 for the majority class because labels cluster at TRL 3–5, so **QWK and MAE are the informative metrics here, not within-1**. Decoding moves metrics in opposite directions (mode → exact; expectation → MAE / within-1; rounded regression → QWK). This is why C5 (metric-aware decoding) is a spike: the choice must follow the official metric. These are deliberately weak hashed-ridge baselines. The sklearn TF-IDF + logistic / cumulative-logit run (`eval/baseline_tfidf.py`) is pending: the overloaded machine could not import scipy in time.

## Results — `trl_begin` and `trl_end` (same script, run, split method and hyper-parameters)
| Label | Model | Exact | Within-1 | MAE ↓ | QWK | Macro precision* |
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
