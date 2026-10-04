# P3 live demo — "the evaluator that says I don't know"

A single offline page for the finals. It shows the project on **real** data (Open Bandit Dataset, ZOZOTOWN's A/B test of a uniform-random policy against Bernoulli Thompson sampling, "BTS"). A concurrent A/B arm serves as the check. A **pre-registered** knob lets a judge move a candidate policy away from the logs. The evaluator either answers or says "can't tell from these logs", and the real check line shows when that was right.

## Run

```bash
perceptron-p03-off-policy-eval/demo/run.sh      # builds (≈0.2 s) and opens demo/index.html; offline
perceptron-p03-off-policy-eval/demo/smoke.sh    # headless checks; exits 0 on PASS
```

- **Python.** `run.sh` and `smoke.sh` use `$P3_PYTHON`, else `perceptron-p03-off-policy-eval/.venv/bin/python` if it exists, else `python3`.
  - `build.py` needs only the standard library (Python ≥ 3.8). If no Python is found, or the build fails, `run.sh` opens the committed `index.html`.
  - `smoke.sh` and `knob.py` also need numpy.
- **No `.data` and no network** are needed. Everything comes from committed files.
- `P3_NO_OPEN=1` skips opening a browser.
- **Keys:**
  - <kbd>1</kbd>–<kbd>4</kbd> switch sheets.
  - <kbd>←</kbd>/<kbd>→</kbd> move α (<kbd>Shift</kbd> moves by 0.05).
  - <kbd>[</kbd>/<kbd>]</kbd> change period.
  - <kbd>i</kbd> switches IPS/SNIPS; <kbd>c</kbd> switches row-level/hour-cluster intervals.
- **Deep links:** `index.html#s3:a=43,p=W2,e=IPW,iv=row,src=SB+SR`.
- **Talk track:** [`SCRIPT.md`](SCRIPT.md). **Fallback screenshots:** [`fallback/`](fallback/).

## The four sheets

| sheet | label | shows |
|---|---|---|
| 1 | REAL · POST-HOC gate | Re-enacted policy switch: dashboard +1.62 vs concurrent A/B check +1.26 vs doubly robust +1.40 from logs alone. The real waterfall (+0.36 is the week). The gate's refusal (ESS/n 0.92%), the 26 Nov failure, and the 8-instance track record. |
| 2 | REAL | When the logs can tell: from the Random arm's logs, DR 4.936 vs the BTS arm's 4.890. Approximate target, and the DM caveat. |
| 3 | REAL · PRE-REGISTERED | The knob: π_α = (1 − α)·BTS + α·uniform, from BTS logs (exact weights) and Random logs (approximate target). The A/B check line, IPS/SNIPS intervals, ESS/n, the frozen gate's verdict, and all 12 series × 101 α at once. |
| 4 | SYNTHETIC | Simulator: a 13-level drift slider (truth vs naive vs DR) and the S1 waterfall. |

## Pre-registration and results (sheet 3)
- **Registration:** [`preregistration_knob.md`](preregistration_knob.md), committed and pushed **2026-10-04 21:07:33 IST** (commit `10209ca`), before any knob computation.
  - Its predictions come from committed results only, via [`prereg_predictions.py`](prereg_predictions.py).
  - The gate rule is frozen at `eval/gate_rule.json` (b4e95ae).
- **Results**, reported in full: [`results/knob_summary.md`](results/knob_summary.md) and [`results/knob_results.json`](results/knob_results.json), from [`knob.py`](knob.py).
  - 58/58 reproduction checks against committed cells.
  - Closed forms match `gate.py` on per-row arrays in 12/12 series.
  - 31/33 predictions hit. The two misses: Nov 25's crossing came at 0.46 rather than 0.43, and Nov 24's condition abs(z) ≤ 3 failed (z = +4.52).
- **IPS, row-level intervals, over 1,212 points:**
  - 681 answered with the check inside.
  - **12 answered with the check outside**, all on Nov 26 from BTS logs at α 0.28–0.39, at most 0.036 per 1,000 beyond the interval, and 0 with hour-cluster intervals.
  - 403 refusals where the check was inside.
  - 116 refusals where it was outside.
- **Read honestly:** much of this follows algebraically from the α = 1 endpoints, and the page says so. The gate is conservative on these data. With Random logs it answers, and holds the check, at every α.

## Data and licence
- **Source:** Open Bandit Dataset © ZOZO, Inc., licensed **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/). The licence line is in the README inside the official zip, read 2026-10-04.
- **Citation:** Saito, Aihara, Matsutani, Narita, *A Large-scale Open Dataset for Bandit Algorithms*, arXiv:2008.07146.
- **Vendored extract:** `data/obd_bts_all.csv.gz` and `data/obd_random_all.csv.gz`, 0.76 MB in total.
  - Campaign All, 2019-11-24 00:00 → 2019-11-27 12:00 UTC.
  - Counts per hour × item × position × exact propensity × click. User features and timestamps are dropped, and nothing is rounded.
  - Attribution and the list of changes are in [`data/NOTICE.md`](data/NOTICE.md); sha256 and checks in [`data/extract_manifest.json`](data/extract_manifest.json).
- **Regenerating** needs the raw slices in gitignored `.data/` (fetch commands are in the header of [`make_extract.py`](make_extract.py)). Then run `nice -n 10 .venv/bin/python demo/make_extract.py`.

## Where every number comes from
`build.py` writes each number on the page with a `data-src` (file → key), shown on hover. It asserts 32 formatted numbers equal to `eval/results/headline.json`, the abstract's numbers. `smoke.sh` re-derives the core numbers from the extract with independent standard-library code.

| on screen | source (committed) | computed by |
|---|---|---|
| Sheet 1: cells 4.892 / 3.273 / 3.636; dashboard +1.62 ± 0.21; check +1.26 ± 0.23; the week +0.36; 11%; 29% | `eval/results/obd_slice.json` → `a3_halves.cells`, `A_deploy_BTS.naive / truth / true_env_old` | `eval/run_obd_slice.py` (pre-registered) |
| Sheet 1: DR +1.40 (+1.13 … +1.67) | `obd_slice.json` → `a3_halves.A_deploy_BTS.DR` | same |
| Sheet 1: hour-block +0.93 … +1.78 | `eval/results/obd_block_bootstrap.json` → `halves_A` | `eval/obd_block_bootstrap.py` (post hoc) |
| Sheet 1: ESS/n 0.92%, 25,395 of 2,769,425, max weight 12,500, z | `eval/results/gate_obd_posthoc.json` → `cases['halves · A deploy BTS']` | `eval/apply_gate_obd.py` (post hoc) |
| Sheet 1: 26 Nov DR +1.48 vs +1.06 | `obd_slice.json` → `a3_daypairs['2019-11-25→2019-11-26']` | `eval/run_obd_slice.py` |
| Sheet 1: 5/8, 4/5, 2/2, 0/3 | `gate_obd_posthoc.json` → `summary.unique_instances` | `eval/apply_gate_obd.py` |
| Sheet 1: reverse switch −1.25 / −1.26 / −1.70 | `obd_slice.json` → `a3_halves.B_rollback_to_Random` | `eval/run_obd_slice.py` |
| Sheet 2: forest plot, 4.936, 4.890 ± 0.056, 0.9% | `obd_slice.json` → `a2` | `eval/run_obd_slice.py` |
| Sheet 2: 20/20, 16× | `obd_slice.json` → `a1` | same |
| Sheet 2: DM refit SE 0.196 | `obd_block_bootstrap.json` → `dm_refit` | `eval/obd_block_bootstrap.py` |
| Sheet 3: every knob value | `demo/results/knob_results.json` (from `demo/data/*.csv.gz`) | `demo/knob.py` (pre-registered) |
| Sheet 3: gate floor and z limit | `eval/gate_rule.json` | frozen b4e95ae |
| Sheet 4: drift sweep | `eval/results/decomposer_review.json` → `drift±x.xx` | `eval/run_decomposer_review.py` |
| Sheet 4: S1 waterfall, −5.6 / +7.5 / 30/30 | `eval/results/sim_bank_runs.csv` (S1, DECOMP rows) | `eval/run_sim_bank.py` |

## Files
- `run.sh`: one command.
- `build.py`: page builder, standard library only.
- `page.template.html`: the page's HTML, CSS and JS.
- `index.html`: the built page, committed.
- `make_extract.py`: vendors the extract. `data/` holds the extract, NOTICE and manifest.
- `preregistration_knob.md` and `prereg_predictions.py`: the registration.
- `knob.py` and `results/`: the knob analysis.
- `smoke.sh` and `smoke_check.py`: the smoke test.
- `SCRIPT.md`: the talk track. `fallback/`: 12 screenshots, 3.1 MB.

## Design
The page is an engineering computation pad. A ruled title block on every sheet names who "checked" it (the A/B arms), results are boxed, and ink stamps mark REAL / SYNTHETIC / POST HOC / PRE-REGISTERED. A slide-rule cursor reads every scale at one α.

It is a light surface for projector rooms and uses system fonts only (DIN Alternate / Bahnschrift for display, the system sans for text, the system mono for data). The direction is recorded in the HTML comment at the top of `page.template.html`.
