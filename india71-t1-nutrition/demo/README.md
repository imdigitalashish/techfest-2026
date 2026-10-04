# Poshan Setu: the live demo

```bash
cd india71-t1-nutrition
demo/run.sh        # opens demo/index.html: offline, no install, first screen in under a second
demo/smoke.sh      # headless checks (python3 + node; the exporter check needs the project .venv)
```
Talk track: [`SCRIPT.md`](SCRIPT.md) (3 minutes, a 30-second version, the jury's hard questions). Fallback screenshots at 1280×720 and a GIF of the knobs: [`fallback/`](fallback/).

The page is built for a 1280×720 projector. Every screen shows its primary comparison, verdict and caveat without scrolling (smoke-tested at 1280×720 and 1440×900); secondary evidence sits behind **Details** (`d`).

## What it shows (7 screens, about 3 minutes)

| # | Screen | Label | Live in the page | Precomputed by committed code |
|---|---|---|---|---|
| 1 | India: tile grid (no boundaries) + reported-vs-surveyed scatter; 36/36 | **REAL** | toggles | `research/sources/state_gap_verified.csv` (V4: LS USQ 2668 annexure; RS USQ 477 annexure I) |
| 2 | Districts: 706 NFHS-5 districts; presets Nandurbar, Amravati (Melghat) | **REAL** | pickers | `eval/fetch_nfhs5.py` → 4 under-5 indicators; 24/24 spot-checked (V5); Sahibganj excluded (conflicting rows) |
| 3 | Find every child: RCH-ID coverage × extra typos; shared IDs vs pooled names vs encoded linkage (default and precision-matched), as **correct and false links** | **SYNTHETIC** | knob snapping (35 runs, no interpolation) | `components/identity_linkage`: Bloom-filter linkage runs through `pprl.encode_department` (each side) → `pprl.match_encoded` (encodings only); 35% / +0% equals `eval/results/identity_linkage.json` |
| 4 | One child: first-ever wasting episode, Poshan Tracker + RCH (+ U-WIN) on one timeline | **SIMULATED children, REAL district rates** | district switch | simulator calibrated to the district (`demo/calibrate_district.py`); ranks `eval_v2` (infant gate); encoded link checked against truth |
| 5 | This month: K slots, programme rule vs lowest-WHZ rule, reveal; infants and SAM/MAM not ranked | same | K 1–10, reveal, AWC-month browser | frozen `eval_v2` re-run at K = 1–10; reference K = 5 equals `eval/results/early_warning_v2.json` |
| 6 | The worker's SMS (featured week, K = 5): ≤ 80 characters, no names; capacity gate | same | none | `action_router.route` + `mark_undelivered` (blocked, no worker clock, LS capacity exception), `frontline_worklist.render`, day-8 `escalate` |
| 7 | Break it: six access requests; ledger tamper | same | **SHA-256 re-verification in the browser** | `policy_gate.gate.decide` (recorded at export); `audit_ledger.Ledger` + Python verdicts on the same tamper scenarios |

The "crazy" element is screen 3. Remove the shared ID and add 40% more typos: the ID join finds nobody (true by definition, and said so). Each department encodes its own records, and the matcher sees only bit-strings and keyed hashes. At pooled name matching's precision (98.6%), encoded linkage re-joins 2,250 of 4,531 children with 31 false links. Pooled matching re-joins 2,456, but only by sharing names. The loose threshold's 3,907 comes with 366 false links, and the screen shows that.

## Regenerate the data (`demo/data/demo_data.js`)

```bash
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python eval/fetch_nfhs5.py                       # REAL district data -> .data/raw/nfhs5 (about 11 MB download)
nice -n 10 .venv/bin/python -m demo.export                  # all sections, about 12 min on an M-series Mac (memory guard between jobs)
.venv/bin/python -m demo.export --only sim --districts amravati   # one section; others kept
.venv/bin/python -m demo.export --check                     # quick re-derivation against the committed file (also in smoke.sh)
python3 demo/capture_fallback.py                            # screenshots + GIF (needs demo/requirements-demo.txt)
```
`.cache/demo/` (gitignored) holds simulator builds so re-runs take seconds.

## Honesty rules this demo follows

- Every number is copied from `eval/results/*.json` (checked equal by `check_data.py`) or computed by committed code via `demo/export.py`. A source line sits under every screen.
- REAL data are labelled REAL; the benchmark is SYNTHETIC; child-level screens carry the banner *SIMULATED children, REAL district rates*, with achieved vs target. Severe wasting is not calibrated and is shown as such (Nandurbar 4.8% vs 13.5%).
- The reported-vs-surveyed gap is an *unexplained discrepancy*, not evidence about any worker. National stunting is close; the state-level spread is in Details.
- Linkage is judged on correct **and false** links, including at matched precision; the bit-string pair is a fixed illustration. Linkage is never presented as improving prediction (0.429 vs 0.430 in `early_warning_v2.json`), only as coordination.
- The example child is chosen by a stated rule: first-ever episode, rankable, listed in time, linked correctly through the encoded boundary. The aggregate recall (most episodes missed) sits next to it.
- No worker-level scores or identifiers (ADR 002; asserted by `check_data.py`). Undelivered work is a capacity exception, never the worker's overdue task.
- Screen 7 separates what is recorded (policy decisions at export), live (hash verification) and simulated (the external checkpoint), and states the replace-both limit.

## Assumptions and limits

- 35% RCH-ID coverage (nominal: share of children in both registries; the realised share of all Poshan Tracker records is shown), the typo model and the PPRL thresholds are synthetic-benchmark assumptions; the knobs show the full range.
- The encoded matcher still learns token equality (shared blocks, IDs, sex). Bloom filters are open to known attacks, so the key must stay with the departments. Hardening is a pilot item.
- The SMS screen is precomputed for the featured week at K = 5; when screen 5 is set otherwise, a notice says so. Infants under six months go to an infant pathway that this prototype does not route.
- Tile positions are approximate by design (no map boundaries).
- **UNVERIFIED:** the Hindi reason strings (from `frontline_worklist/render.py`) have not been reviewed by a native speaker. The page is untested on a real projector and on browsers other than Chromium (headless) and macOS. The 3-minute timing is estimated, not rehearsed. The Ministry quote in Details comes from a news report of a Rajya Sabha reply.
