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

## Results — `trl_begin`, `trl_end`
Pending (run in progress); appended here when committed.
