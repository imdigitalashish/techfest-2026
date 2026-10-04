# EV Infra Map India — Techfest 2026 (MHI × ICAT), Challenge 1

A national, evidence-first view of public EV charging in India. It links every public charger source we can legally use, measures how much of the official count those sources actually see, relates supply to VAHAN registrations down to RTO level, and estimates district gaps with honest ranges and reasons.

| Start here | |
|---|---|
| Round-1 submission | [methodology](deliverables/round1-methodology.md) · [roadmap](deliverables/round1-roadmap.md) |
| Journal (state, decisions, log, selection memo) | [thought_node.md](thought_node.md) |
| State of the art + what companies ship + verified facts | [research/landscape.md](research/landscape.md) · [research/fact-check.md](research/fact-check.md) |
| Architecture (14 components, typed contracts) and spike decision | [architecture/components.md](architecture/components.md) · [contracts](architecture/contracts/models.py) · [ADR 001](architecture/adr/001-spike.md) |
| Dashboard (open locally) | `components/dashboard_map/dist/index.html` (India) · `maharashtra.html` (districts) · screenshots in that folder |
| Cross-model reviews | [reviews/](reviews/) · [ledger](reviews/ledger.tsv) |

## Reproduce
```sh
cd ev-c1-infra-map-india
uv venv .venv && uv pip install --python .venv/bin/python -r pyproject.toml
# one-time data fetch (small; one source at a time) — see thought_node.md "Rebuild everything from scratch":
.venv/bin/python components/vahan_ingest/fetch_vahan.py --national --states --monthly --rto-state MH
.venv/bin/python components/vahan_ingest/fetch_vahan.py --rto-state CG --rto-years A
.venv/bin/python components/charger_ingest/fetch_osm.py
(cd .data && git clone --depth 1 --filter=blob:none --sparse https://github.com/openchargemap/ocm-export.git && cd ocm-export && git sparse-checkout set data/IN)
.venv/bin/python components/charger_ingest/fetch_ocm.py
.venv/bin/python components/charger_ingest/fetch_overture.py
sh components/admin_geo/fetch_boundaries.sh
python3 components/charger_ingest/fetch_sources.py components/charger_ingest/source_urls.txt
# every analysis + documents + checks, from cached data:
sh eval/run_all.sh
```
`eval/run_all.sh` ends with `eval/check_docs.py`. It fails if any number in the documents drifts from the committed results, or if a significant number in the Round-1 documents is neither rendered from a run nor verified in `research/fact-check.md`.

## Data and licences
- **VAHAN 4 dashboard** (MoRTH/NIC; public dashboard).
- **PIB releases** 2086533, 2118894, 2151390 (Government of India).
- **OpenStreetMap** (© OpenStreetMap contributors, ODbL 1.0; derived files carry the same licence).
- **Open Charge Map** export (licence per data provider).
- **Overture Maps** places 2026-09-23.1 (CDLA-Permissive-2.0 / Apache-2.0 / CC0 by source).
- **geoBoundaries** IND ADM1 (DataMeet/ECI, CC BY 2.5 IN) and ADM2 2021 (Pathways Data / LGD, ODbL). Not Survey of India–certified.

Raw data stays in gitignored `.data/` and `.cache/`; only derived results and code are committed. No synthetic data.
