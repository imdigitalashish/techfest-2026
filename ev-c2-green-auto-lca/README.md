# Green Auto India — India-specific automotive LCA (Techfest 2026 × MHI × ICAT, EV Challenge 2)

Journal and current state: [`thought_node.md`](thought_node.md). Method: [`../PLAYBOOK.md`](../PLAYBOOK.md).

## Quickstart (from this folder; Python 3.11 with numpy, scipy, pydantic, pyyaml, openpyxl, pytest; pdfplumber for the digitizers)
```bash
bash eval/run_all.sh                                # tests -> eval -> render docs -> dashboard -> drift check
open deliverables/dashboard/index.html              # offline, self-contained
python3 data/fetch/fetch_sources.py                 # optional: re-download the 18 raw public files into .data/raw/ (gitignored)
python3 components/ingestion/autoresearch/eval.py   # spike-A quote verifier metric (needs the raw files)
python3 components/ingestion/value_check.py         # every verified value appears in its own quote
```
<!-- headline:begin -->Central results (CEA FY2025-26 average grid, CO2e GWP100 (AR5, as ICCT inputs), partial upstream): e-scooter vs petrol scooter saving **38.1 % (32.0 to 43.2)**; e-Verito-class BEV sedan vs petrol sedan **10.0 % (-10.1 to 25.6)** (90 % intervals; inputs id `a2d73529af`).<!-- headline:end -->

Results tables in the documents are rendered from `eval/results/latest.json`; `eval/check_docs.py` (part of the tests) fails if any document drifts from the run. Reviews and lead decisions: [`reviews/`](reviews/).

## Map
| Path | What |
|---|---|
| `data/sources/` · `data/factors/` | The database: every number is a cited record (source, locator, verbatim quote, pedigree, status) |
| `data/vehicles/` | Product systems and scenarios (case 1: petrol vs electric scooter; case 2: sedan petrol/diesel/CNG/BEV) |
| `data/benchmarks/` · `data/fetch/` | Published results used for validation; fetch / parse / digitize scripts |
| `components/lca_engine/` | Engine (`greenauto`): record store, paired Monte Carlo, DQI, data-gap ranking, grid-factor service |
| `components/ingestion/` | Spike A: fail-closed quote verifier (v5), value-in-quote check, autoresearch ledger |
| `components/dashboard/` | Static dashboard generator |
| `eval/` | Evaluation harness (v2), results, doc renderer and drift check |
| `research/` · `architecture/` | Landscape, per-component notes, components + contracts, ADRs |
| `deliverables/` | Round-1 methodology + roadmap (v1.0), hostile-jury review, dashboard |
| `reviews/` | Independent and cross-model reviews with ACCEPTED/REJECTED decisions; `ledger.tsv` |
