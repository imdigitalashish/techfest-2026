# P3 live demo — "the evaluator that says I don't know"

A single offline page for the finals, built on **real** data: the Open Bandit Dataset, ZOZOTOWN's A/B test of a uniform-random policy against Bernoulli Thompson sampling ("BTS").

- **The comparison** is a noisy concurrent-A/B reference: the arms' observed click rates, not known truth. Arm comparability is unresolved.
- **The knob** is **pre-registered**. It lets a judge move a candidate policy away from the logging policy.
- **The evaluator** either answers or says "can't tell from these logs". The reference line shows where its answers and refusals land.

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
  - <kbd>1</kbd>–<kbd>4</kbd> switch sheets. On sheet 3, a second <kbd>3</kbd> (or its tab) brings the knob into view; a third goes back to the sheet's top.
  - **Presets** set the period, α, estimator (IPS), interval (row-level), endpoint (E1) and both log sources together, then scroll to the knob. The same three are buttons above the chart.
    - <kbd>5</kbd> W2 · α 0.42
    - <kbd>6</kbd> W2 · α 0.43
    - <kbd>7</kbd> Nov 26 · α 0.33
  - <kbd>←</kbd>/<kbd>→</kbd> move α (<kbd>Shift</kbd> moves by 0.05); <kbd>[</kbd>/<kbd>]</kbd> change period.
  - <kbd>i</kbd> switches IPS/SNIPS; <kbd>c</kbd> switches row-level/hour-cluster intervals; <kbd>e</kbd> switches the endpoint shown (E1/E2).
  - <kbd>Esc</kbd> closes a source tooltip.
- **Deep links:** `index.html#s3:a=33,p=D26,e=IPW,iv=cluster,ep=E2,src=SB+SR`.
- **Talk track:** [`SCRIPT.md`](SCRIPT.md), with a measured rehearsal. **Fallback screenshots:** [`fallback/`](fallback/).

## The four sheets

| sheet | label | shows |
|---|---|---|
| 1 | REAL · POST-HOC gate | A re-enacted policy switch using concurrent A/B logs: the dashboard's +1.62 vs the concurrent A/B reference's +1.26 vs doubly robust +1.40 from logs alone. The real waterfall: +0.36 is the week. The gate's refusal (weight ESS 0.92% of rows), the 26 Nov failure, and the 8-instance track record: 2/2 S1 rejections refused; 2/3 own-CI misses refused. |
| 2 | REAL | When the logs can tell: from the Random arm's logs, DR 4.936 vs the BTS arm's observed 4.890. An approximate target, with the DM caveat. |
| 3 | REAL · PRE-REGISTERED | The knob: π_α = (1 − α)·BTS + α·uniform, scored from BTS logs (exact weights) and from Random logs (approximate target). It shows the noisy A/B reference line, IPS/SNIPS intervals, weight ESS, the frozen gate's verdict, E1 and E2 side by side, and all 12 series × 101 α at once. |
| 4 | SYNTHETIC | The simulator. A 13-level drift slider shows the Monte-Carlo reference (200,000 draws) vs naive vs DR. The S1 waterfall is a separate fixed case (mix shift 0.5, 30 seeds) that the slider does not control. |

**Endpoints:**
- **E1:** the reference lies inside the estimate's own 95% CI.
- **E2** (= S1): the 95% CI of (estimate − reference) contains 0. The difference SE accounts for the arm the two share.

## Pre-registration and results (sheet 3)
- **Registration:** [`preregistration_knob.md`](preregistration_knob.md), committed and pushed **2026-10-04 21:07:33 IST** (commit `10209ca`), before the knob curves were computed.
  - It discloses the α = 1 endpoints already seen, so this is pre-registered reuse of OBD, not an untouched real-data holdout.
  - Its predictions come from committed results only, via [`prereg_predictions.py`](prereg_predictions.py).
- **The gate rule** is frozen at `eval/gate_rule.json` (b4e95ae). It was selected using simulator runs after OBD failures had informed its design.
- **Results**, reported in full: [`results/knob_summary.md`](results/knob_summary.md) and [`results/knob_results.json`](results/knob_results.json), from [`knob.py`](knob.py).
  - 58/58 reproduction checks against committed cells.
  - Closed forms match `gate.py` on per-row arrays in 12/12 series.
  - **31/33 endpoint-derived checks** matched. The curves are determined by endpoint statistics, so these checks mainly test algebra and implementation, not independent forecasts:
    - IPS(λ) = (1 − λ)·p + λ·u
    - SNIPS(λ) = [(1 − λ)·p + λ·u] / [(1 − λ) + λ·m]
    - λ is the far-end share; p is the logging arm's click rate; u is IPS at the far end; m is the far end's mean weight.
  - The two misses: Nov 25's crossing came at 0.46 rather than 0.43, and Nov 24's condition |z| ≤ 3 failed (z = +4.52).
- **Registered primary: IPS, row-level, BTS logs, 606 grid points.**
  - The gate answered **87/606**, and E1 held at **75/87**.
    - 6 of the 87 are at α = 0, the logging end, where the estimate equals the reference by construction. At α > 0, E1 held at 69/81.
    - The 12 answered misses are all on Nov 26 at α 0.28–0.39, at most 0.036 per 1,000 beyond the interval.
  - With hour-cluster intervals, E1 holds at all 87. **E2 still rejects** at all 39 answered nonzero α on Nov 26, in both interval modes; at α 0.33 hour-cluster the difference CI is −0.290 … −0.008.
  - E2 over the 87 answered points: 48 consistent, 39 rejecting.
  - The gate refused **519/606**: 403 with the reference inside the own CI, 116 outside.
  - Ungated IPS on the same points: E1 holds at 478/606.
- **Secondary: Random logs** (approximate target, 606 points).
  - The gate answers at all 606; IPS's E1 and E2 hold at all 606.
  - SNIPS's do not everywhere. On Nov 25, row-level, E1 misses at 24 points and E2 rejects at 100; there are no misses with hour-cluster intervals.
- **Secondary: pooled**, not the registered primary: 681 answered inside, 12 answered outside, 403 refused inside, 116 refused outside.
- **Read honestly:**
  - The counts are correlated grid locations (overlapping periods, deterministic α steps), not independent decisions.
  - Under this point-containment diagnostic the gate trades fewer answers for a lower observed miss fraction: 12/87 answered vs 128/606 ungated. Its deployment value remains untested, and the 5% floor is a frozen heuristic, not a theorem.

## Data and licence
- **Source:** Open Bandit Dataset © ZOZO, Inc., licensed **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/). The licence line is in the README inside the official zip, read 2026-10-04.
- **Citation:** Saito, Aihara, Matsutani, Narita, *A Large-scale Open Dataset for Bandit Algorithms*, arXiv:2008.07146.
- **Vendored extract:** `data/obd_bts_all.csv.gz` and `data/obd_random_all.csv.gz`, 0.76 MB in total.
  - Campaign All, 2019-11-24 00:00 → 2019-11-27 12:00 UTC.
  - Counts per hour × item × position × exact propensity × click. User features and timestamps are dropped, and nothing is rounded.
  - Attribution and the list of changes are in [`data/NOTICE.md`](data/NOTICE.md); sha256 and checks in [`data/extract_manifest.json`](data/extract_manifest.json).
- **Regenerating** needs the raw slices in gitignored `.data/` (fetch commands are in the header of [`make_extract.py`](make_extract.py)). Then run `nice -n 10 .venv/bin/python demo/make_extract.py`.

## Where every number comes from
- **The page renders committed results.**
  - `build.py` gives every number a `data-src` (file → key). Dotted numbers, including the knob readouts, show it on hover.
  - It asserts 33 formatted numbers equal to `eval/results/headline.json`, the abstract's numbers.
- **`smoke.sh` replays the grid with the same code and independently checks five quantities:**
  - The replay: `knob.py` re-runs from the extract, and its output must match byte for byte.
  - The independent checks use separate standard-library code on the extract: the BTS and Random click rates, the halves' dashboard and reference differences, and the halves' IPW effect.
- The committed files name a few keys `truth`; on this page they hold the concurrent A/B reference (or, on sheet 4, the simulator's Monte-Carlo reference), not ground truth.

| on screen | source (committed) | computed by |
|---|---|---|
| Sheet 1: cells 4.892 / 3.273 / 3.636; dashboard +1.62 ± 0.21; A/B reference +1.26 ± 0.23; the week +0.36; 11%; "29% above the concurrent A/B point estimate" | `eval/results/obd_slice.json` → `a3_halves.cells`, `A_deploy_BTS.naive / truth / true_env_old` | `eval/run_obd_slice.py` (pre-registered) |
| Sheet 1: DR +1.40 (+1.13 … +1.67) | `obd_slice.json` → `a3_halves.A_deploy_BTS.DR` | same |
| Sheet 1: hour-block +0.93 … +1.78 | `eval/results/obd_block_bootstrap.json` → `halves_A` | `eval/obd_block_bootstrap.py` (post hoc) |
| Sheet 1: weight ESS 0.92% (about 25,395 of 2,769,425 rows), mean-weight z; the hypothetical weight 12,500 (a click at the smallest logged propensity) | `eval/results/gate_obd_posthoc.json` → `cases['halves · A deploy BTS']` (`ess`, `ess_frac`, `z`, `max_w`) | `eval/apply_gate_obd.py` (post hoc) |
| Sheet 1: largest weight on an actual click ≈ 139 (propensity 9e-05) | `demo/data/obd_bts_all.csv.gz`, clicked BTS rows in hours 42–83 | `build.py` `max_clicked_weight()` |
| Sheet 1: 26 Nov DR +1.48 vs +1.06 | `obd_slice.json` → `a3_daypairs['2019-11-25→2019-11-26']` | `eval/run_obd_slice.py` |
| Sheet 1: 5/8, 4/5, 0/3; 2/2 S1 rejections refused; 2/3 own-CI misses refused | `gate_obd_posthoc.json` → `summary.unique_instances`: `abstained_s1_rejected / s1_rejected_total`; `(abstained − abstained_ref_in_ci) / (listed − answered_ref_in_ci − abstained_ref_in_ci)` | `eval/apply_gate_obd.py` |
| Sheet 1: reverse switch −1.25 / −1.26 / −1.70 | `obd_slice.json` → `a3_halves.B_rollback_to_Random` | `eval/run_obd_slice.py` |
| Sheet 2: forest plot, 4.936, 4.890 ± 0.056 (the BTS arm's observed rate), 0.9% | `obd_slice.json` → `a2` | `eval/run_obd_slice.py` |
| Sheet 2: 20/20, 16× | `obd_slice.json` → `a1` | same |
| Sheet 2: DM refit SE 0.196 | `obd_block_bootstrap.json` → `dm_refit` | `eval/obd_block_bootstrap.py` |
| Sheet 3: every knob value, interval, weight ESS, max weight, z, and E1/E2 status; the E2 difference CI = (v − ref) ± 1.96·`d_se` (or `d_se_cl`) | `demo/results/knob_results.json` → `series[…].rows[i]` (`ref`, `se_ref`, `IPW`/`SNIPW` → `v`, `se`, `se_cl`, `d_se`, `d_se_cl`, `E1`, `E2`, …); built from `demo/data/*.csv.gz` | `demo/knob.py` (pre-registered) |
| Sheet 3: registered primary, Random secondary and pooled counts | `knob_results.json` → `series[*].summary` and `rows` | `knob.py`; counted again by `build.py` `primary_block()` |
| Sheet 3: gate floor and z limit | `eval/gate_rule.json` | frozen b4e95ae |
| Sheet 4: drift sweep (Monte-Carlo reference, naive, DR); wrong sign from drift −0.75; DR RMSE ≤ 0.6 | `eval/results/decomposer_review.json` → `drift±x.xx` | `eval/run_decomposer_review.py` |
| Sheet 4: 200,000 Monte-Carlo draws; mix shift 0.5 (S1) and 0.0 (sweep); 10,000 rounds per period | `eval/run_sim_bank.py:108`, `:28`; `eval/run_decomposer_review.py:160`, `:33`, `:29` | parsed from committed code by `build.py` `code_const()` |
| Sheet 4: S1 waterfall, −5.6 / +7.5 / 30/30 | `eval/results/sim_bank_runs.csv` (S1, DECOMP rows) | `eval/run_sim_bank.py` |

## Rehearsal
[`rehearsal/`](rehearsal/) times the talk track; the measured total is in `SCRIPT.md`.
- `speech.py` counts the spoken words and times each beat with macOS `say` at 150 wpm, writing `speech.json`.
- `drive.js` is a Playwright page function. It performs the talk track's clicks in Chromium at 1600×900 against a local server and asserts the state each beat must show, writing `result.json`. It runs in segments that stop only at beat boundaries, because the browser tool limits a request to about 3 minutes.
- `smoke.sh` checks that `result.json` and `fallback/states.json` were made on the committed `index.html` (sha256).

## Files
- `run.sh`: one command.
- `build.py`: page builder, standard library only.
- `page.template.html`: the page's HTML, CSS and JS.
- `index.html`: the built page, committed.
- `make_extract.py`: vendors the extract. `data/` holds the extract, NOTICE and manifest.
- `preregistration_knob.md` and `prereg_predictions.py`: the registration.
- `knob.py` and `results/`: the knob analysis.
- `smoke.sh` and `smoke_check.py`: the smoke test.
- `SCRIPT.md`: the talk track. `rehearsal/`: its timing.
- `fallback/`: 11 screenshots at 1600×900, 3.4 MB.
  - 01–09 follow the talk track beat by beat; 10–11 are Q&A views.
  - `capture.js` took them through the page's normal controls (clicks, keys and scrolling; no deep links). It checked each on-screen state against its file name, and `states.json` records each state with the file's sha256.
  - They were re-captured for review item D12. The previous 08 had shown Nov 25 selected, consistent with its readout.

## Design
The page is an engineering computation pad. A ruled title block on every sheet names what it is compared with (the noisy concurrent A/B reference). Results are boxed, and ink stamps mark REAL / SYNTHETIC / POST HOC / PRE-REGISTERED. A slide-rule cursor reads every scale at one α.

It is a light surface for projector rooms and uses system fonts only (DIN Alternate / Bahnschrift for display, the system sans for text, the system mono for data). The direction is recorded in the HTML comment at the top of `page.template.html`.
