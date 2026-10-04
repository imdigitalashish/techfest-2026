# India@71 · Theme 1: Poshan Setu (maternal & early-childhood nutrition)

A data-governance and decision layer behind Poshan Tracker. Journal and current state: [`thought_node.md`](thought_node.md). Proposal: [`deliverables/round1-proposal.md`](deliverables/round1-proposal.md) → PDF [`deliverables/India71_100_[TeamID].pdf`](deliverables/). Architecture: [`architecture/components.md`](architecture/components.md), ADRs in [`architecture/adr/`](architecture/adr/). Research: [`research/landscape.md`](research/landscape.md). Reviews: [`reviews/`](reviews/).

## Demo (finals): one command, offline
```bash
cd india71-t1-nutrition && demo/run.sh      # opens demo/index.html; no venv, no server, no network
demo/smoke.sh                               # headless checks (needs the .venv below for step 4)
```
Seven screens: REAL state and district data (NFHS-5 vs Poshan Tracker), then SIMULATED children at REAL district rates (find every child, one child, this week's worklist, SMS, break it). Talk track: [`demo/SCRIPT.md`](demo/SCRIPT.md); fallback screenshots and GIF: [`demo/fallback/`](demo/fallback/); details: [`demo/README.md`](demo/README.md).

## Reproduce (macOS/Linux, Python 3.11)
```bash
cd india71-t1-nutrition
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m components.growth_standards.fetch_who          # WHO tables → .data/raw (SHA-256 checked)
.venv/bin/python -m pytest -q                                       # contract + component tests, incl. eval/check_docs.py
.venv/bin/python -m components.growth_standards.validate_who        # → eval/results/growth_standards.json (real WHO tables)
.venv/bin/python -m components.identity_linkage.eval_linkage        # SYNTHETIC
.venv/bin/python -m components.credibility_engine.eval              # SYNTHETIC (frozen v1 eval)
.venv/bin/python -m components.early_warning.eval_v1                # SYNTHETIC, leakage-free (~10 min)
.venv/bin/python -m eval.run_pipeline                               # SYNTHETIC end-to-end weekly district run
.venv/bin/python -m components.action_router.sim                    # illustrative ops simulation
.venv/bin/python -m eval.check_docs                                 # quoted numbers == eval/results
.venv/bin/python deliverables/build_pdf.py                          # print HTML → PDF via Chromium (A4, 1in margins)
```
Redirect each eval's stdout to the matching `eval/results/*.json` to refresh it. All synthetic outputs carry `"synthetic": true`. Real Poshan Tracker microdata isn't public, so real-data validation is a pilot item.
