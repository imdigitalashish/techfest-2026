# Green Auto India — India-specific automotive LCA (Techfest 2026 × MHI × ICAT, EV Challenge 2)

Journal and current state: [`thought_node.md`](thought_node.md). Method: [`../PLAYBOOK.md`](../PLAYBOOK.md).

## Quickstart (from this folder; Python 3.11 with numpy, pydantic, pyyaml, pytest; pdfplumber for the digitizer)
```bash
python3 data/fetch/fetch_sources.py              # re-download raw sources into .data/raw/ (gitignored)
python3 -m pytest components/lca_engine/tests -q # contract tests (10)
python3 eval/eval.py                             # frozen eval: ICCT replication + India-2026 case study -> eval/results/
python3 components/dashboard/build.py            # -> deliverables/dashboard/index.html (open in a browser, offline)
python3 components/ingestion/autoresearch/eval.py # spike-A quote verifier metric
```

## Map
| Path | What |
|---|---|
| `data/sources/` · `data/factors/` | The database: every number is a cited record (source, locator, verbatim quote, pedigree, status) |
| `data/vehicles/` | Product systems and scenarios (case study 1: petrol vs electric scooter) |
| `data/benchmarks/` · `data/fetch/` | Published results used for validation; fetch / parse / digitize scripts |
| `components/lca_engine/` | Engine (`greenauto`): record store, paired Monte Carlo, DQI, data-gap ranking, grid-factor service |
| `components/ingestion/` | Spike A: fail-closed quote verifier + autoresearch ledger |
| `components/dashboard/` | Static dashboard generator |
| `eval/` | Frozen end-to-end evaluation and results |
| `research/` · `architecture/` | Landscape, per-component notes, components + contracts, ADRs |
| `deliverables/` | Round-1 methodology and roadmap drafts, dashboard |
