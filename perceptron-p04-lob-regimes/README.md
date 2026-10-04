# Perceptron P4 · Order-book forecasting under regime shifts

A forecaster for the 10-second direction of the Binance BTCUSDT mid-price, with two additions:
- a **calibrated, harm-aware shift monitor**, which flags when the market has changed in a way that hurts the model;
- **volatility-regime heads**, which adapt to the change instead of silently degrading.

Everything is evaluated under a pre-registered, leakage-tested protocol on real tick data.

| Start here | |
|---|---|
| Round-1 abstract | [`deliverables/round1-abstract.md`](deliverables/round1-abstract.md) · diagram [`deliverables/architecture.md`](deliverables/architecture.md) · Q&A [`deliverables/qa-prep.md`](deliverables/qa-prep.md) |
| Held-out results | [`eval/results/v2_holdout.md`](eval/results/v2_holdout.md), produced under [`eval/PREREGISTRATION.md`](eval/PREREGISTRATION.md) |
| Design | [`architecture/components.md`](architecture/components.md) · [ADR 001](architecture/adr/001-spike.md) · [`research/landscape.md`](research/landscape.md) |
| Journal and selection memo | [`thought_node.md`](thought_node.md) |
| Cross-model reviews | [`reviews/`](reviews/) |

## Reproduce (Apple-silicon Mac, Python 3.11; ~1.1 GB download, ~10 min compute)

```bash
cd perceptron-p04-lob-regimes
python data/fetch_tardis.py --types book_snapshot_5 --days 2024-05-01   # one day, to try
data/fetch_batches.sh book_snapshot_5        # all 46 free first-of-month days, 2023-01 … 2026-10 (MD5s: data/manifest.csv)
python -m pytest -q tests                    # contract and leakage tests (causality, label delay, KS == SciPy)
nice -n 10 python eval/run_v2.py --stage dev --tag v2_dev --extra-specs eval/tuning_v2.json --workers 3
nice -n 10 python eval/run_v2.py --stage dev --tag v2_dev_amend1 --policies static_snorm regime_gated --extra-specs eval/tuning_v2_amend1.json --workers 3
nice -n 10 python eval/run_v2.py --stage holdout --tag v2_holdout --workers 3
python eval/plot_day.py 2024-05-01           # FOMC-day replay figure → deliverables/figures/
python eval/check_numbers.py                 # every number quoted in the docs exists in eval/results/*
```

The overnight v1 results (6 days) remain reproducible with `python eval/run_baseline.py` (results in `eval/results/baseline.md`).

## Layout

| Path | Contents |
|---|---|
| `components/` | One package per component. Typed contracts live in `components/contracts.py`. |
| `components/shift_detector/autoresearch/` | The C6 ratchet: frozen `eval.py`, `program.md`, `results.tsv`. |
| `eval/` | Harnesses (`run_baseline.py` v1, `run_v2.py` v2), configs, pre-registration, results, number check. |
| `data/` | Fetch scripts, `manifest.csv` (MD5 per file), `events.csv` (FOMC times verified at federalreserve.gov). |
| `.data/` | Raw downloads and caches. Gitignored; rebuilt by the fetch scripts. |

Data: Tardis.dev free datasets (first day of each month) for Binance USD-M futures. Fees: Binance's official USDⓈ-M fee page (accessed 2026-10-04).
