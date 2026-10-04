# Poshan Setu: the live demo

```bash
cd india71-t1-nutrition
demo/run.sh        # opens demo/index.html: offline, no install, first screen in under a second
demo/smoke.sh      # headless checks (needs python3 + node; the export check needs the project .venv)
```
Talk track: [`SCRIPT.md`](SCRIPT.md) (3 minutes, plus a 30-second version). Fallback screenshots and a GIF of the knobs: [`fallback/`](fallback/).

## What it shows (7 screens, about 3 minutes)

| # | Screen | Label | Live in the page | Precomputed by committed code |
|---|---|---|---|---|
| 1 | India, state by state: tile grid (no boundaries) + reported vs surveyed scatter | **REAL** | toggles, selection | `research/sources/state_gap_verified.csv` (V4: LS USQ 2668 annexure, RS USQ 477 annexure I) |
| 2 | Districts: 706 NFHS-5 districts, wasting and stunting; presets Nandurbar, Amravati (Melghat) | **REAL** | state/district pick | `eval/fetch_nfhs5.py` → 4 under-5 indicators; 24/24 spot-checked (V5); Sahibganj excluded (conflicting duplicate rows) |
| 3 | Find every child: RCH-ID coverage × extra typos knobs; shared-ID join vs pooled name matching vs Bloom-filter PPRL; the 1,000-bit encodings | **SYNTHETIC** benchmark | knob snapping (no interpolation), bit grids | 35 runs (7 × 5) of `components/identity_linkage` on 5,000 children; the 35% / +0% run equals `eval/results/identity_linkage.json` |
| 4 | One child: Poshan Tracker + RCH + U-WIN on one timeline | **SIMULATED children, REAL district rates** | cohort switch | simulator calibrated to the district (`demo/calibrate_district.py`), ranks from `eval_v1.flag`, identities + PPRL link computed and checked against truth |
| 5 | This week: 5 slots, programme rule vs lowest-WHZ rule, K knob, reveal | same | K 1–10, reveal, AWC-month browser | frozen `eval_v1` protocol re-run on the calibrated simulator (K = 1–10); reference K = 5 equals `eval/results/early_warning_v1.json` |
| 6 | The worker's SMS: ≤ 80 characters, no names; queue, overflow, escalation | same | none | `action_router.route/escalate`, `frontline_worklist.render` |
| 7 | Try to break it: six access requests; ledger tamper (edit, re-seal, truncate) | same | **SHA-256 re-verification in the browser** (`js/ledger.js`) | `policy_gate.gate.decide`; `audit_ledger.Ledger` + Python verdicts on the same tamper scenarios |

The "crazy" element is screen 3: drop the shared ID to 0% and add 40% extra typos. The ID join finds nobody (true by definition, and the screen says so). Bloom-filter linkage still re-joins 3,907 of 4,531 children (F1 0.89) without either department seeing the other's names. Pooled plaintext matching falls to 0.70.

## Regenerate the data (`demo/data/demo_data.js`)

```bash
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python eval/fetch_nfhs5.py                       # REAL district data -> .data/raw/nfhs5 (about 11 MB download)
nice -n 10 .venv/bin/python -m demo.export                  # all sections, about 15 min on an M-series Mac (memory guard between jobs)
.venv/bin/python -m demo.export --only sim --districts amravati   # one section; others kept
.venv/bin/python -m demo.export --check                     # quick re-derivation against the committed file (also in smoke.sh)
python3 demo/capture_fallback.py                            # screenshots + GIF (needs demo/requirements-demo.txt)
```
`.cache/demo/` (gitignored) holds simulator builds so re-runs take seconds.

## Honesty rules this demo follows

- Every number is either copied from `eval/results/*.json` (checked equal by `check_data.py`) or computed by committed code via `demo/export.py`. A source line sits under each chart.
- REAL data are labelled REAL; the benchmark is SYNTHETIC; child-level screens carry the banner *SIMULATED children, REAL district rates* with achieved vs target. Severe wasting is not calibrated and is shown as such (Nandurbar 4.8% vs 13.5%).
- The reported-vs-surveyed gap is shown as an *unexplained discrepancy* (different years, ages and denominators).
- No worker-level scores or identifiers anywhere (ADR 002; asserted by `check_data.py`). Linkage is never presented as improving prediction (0.384 vs 0.384, committed), only as care coordination.
- The example child is chosen by a stated rule (screen 4 source line); its link is computed and verified against simulator truth, and the aggregate recall (39%, so most episodes are missed) sits next to it.

## Assumptions and limits

- 35% RCH-ID coverage, the noise model and the PPRL thresholds are synthetic-benchmark assumptions; the knob shows the full range.
- The capacity squeeze on screen 6 (prevention visits overflow a 10-item weekly list) follows the committed renderer's ordering and the pipeline's capacity of 10. It is a simulation finding, not a field observation.
- Tile positions are approximate by design (no map boundaries).
- **UNVERIFIED:** Hindi reason strings (from `frontline_worklist/render.py`) have not been reviewed by a native speaker in this pass. The page is not yet tested on a real projector, nor on browsers other than Chromium (headless) and macOS. The 3-minute timing is estimated, not rehearsed with a presenter. The Ministry quote on screen 1 is from a news report of a Rajya Sabha reply (as in the proposal).
