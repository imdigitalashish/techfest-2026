# NullahNet — InnovateX 2026, Theme 3: Rising plastic pollution in coastal cities (Mumbai)

A measured, tide-aware layer for Mumbai's existing nullah trash booms. It senses how full each boom pocket is, times clearance crews to the tide and the forecast, retrofits a one-way pocket and a fail-open fuse so a boom keeps its catch and never raises flood levels, and keeps signed evidence records so contractors are paid per verified kilogram.

**Status:** a complete, documented *alternative* to the team's Delhi-zonal theme (Theme 1 was chosen).

## Where to start

| You want… | Open |
|---|---|
| The project journal: current state, decisions, selection memo | [`thought_node.md`](thought_node.md) |
| The Round-1 package (deck, Q&A, presenter card, prototype plan) | [`deliverables/zonal-pitch.md`](deliverables/zonal-pitch.md) |
| Every cited number with URL and quote | [`research/fact-check.md`](research/fact-check.md) |
| Every result with its reproduce command | [`eval/RESULTS.md`](eval/RESULTS.md) |
| State of the art and what companies ship | [`research/landscape.md`](research/landscape.md) · [`research/companies.md`](research/companies.md) |
| Architecture, contracts, spike decision | [`architecture/components.md`](architecture/components.md) · [`architecture/contracts/`](architecture/contracts/) · [`architecture/adr/001-spike.md`](architecture/adr/001-spike.md) |
| Cross-model reviews | [`reviews/`](reviews/) |

## Components (code)

| Folder | What | Reproduce |
|---|---|---|
| [`components/twin_sim/`](components/twin_sim/) | Digital twin of four outfalls (real rain, archived forecasts, fitted tide; SIMULATED plastic), dispatch policies, analysis | `cd components && python -m twin_sim.run` · `python -m twin_sim.analysis` |
| [`components/detection/`](components/detection/) | Floating-litter detector (YOLO11n) and flux counter | see its README |
| [`components/mrv_ledger/`](components/mrv_ledger/) | Signed, hash-chained evidence records with reconciliation | `cd components && python3 -m mrv_ledger.evaluate` |
| [`components/dashboard/`](components/dashboard/) | Offline operations dashboard | `python3 components/dashboard/build_bundle.py`, then serve `components/dashboard/site` |

Rebuild the deliverables with `bash deliverables/build.sh`; it must end with `check_docs: 0 problem(s)`.

## Third-party models, data and code: licences

Every licence below was checked at the source on 2026-10-04.

| Item | Used for | Licence | Source checked |
|---|---|---|---|
| Ultralytics `ultralytics` 8.4.12 and YOLO11n weights | detector training and inference | **AGPL-3.0** (strong copyleft, including network use); commercial terms not checked (UNVERIFIED) | https://raw.githubusercontent.com/ultralytics/ultralytics/main/LICENSE; local package metadata; details in [`components/detection/README.md`](components/detection/README.md) |
| TUD-GV floating-litter images (Jia et al. 2024) | detector training and held-out test | **CC BY 4.0**; cite the paper | https://zenodo.org/records/13730228 |
| Groningen floating-litter images (Jia et al. 2024) | cross-site test | **CC BY 4.0** | https://zenodo.org/records/13730384 |
| Open-Meteo APIs (ERA5 archive, previous-runs forecasts, marine sea level) | twin forcing, dashboard | **CC BY 4.0**; attribution link required where the data are shown (now in the dashboard footer) | https://open-meteo.com/en/licence |
| NASA POWER climatology | solar sizing | Free to use; NASA asks for a reference with service name, version and access date, and notification of publications | https://power.larc.nasa.gov/docs/referencing/ |
| OpenStreetMap data and tiles | site coordinates, dashboard map | **ODbL**; credit "OpenStreetMap contributors" | https://www.openstreetmap.org/copyright |
| Leaflet 1.9.4 (vendored) | dashboard map | **BSD-2-Clause** | `components/dashboard/site/vendor/leaflet/LICENSE` |
| UTide 0.4.0 | harmonic tide fit | **MIT** | local package metadata |
| Marp CLI 4.5.1 | deck export | **MIT** | local package metadata |

**Before any use beyond research and competition:** AGPL-3.0 obliges anyone serving a modified Ultralytics model over a network to release its source. Either comply, obtain a commercial licence, or swap to a permissively licensed detector.

**Required attributions:**
- POWER reference: "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
- Weather data by Open-Meteo.com (CC BY 4.0).
- Map data © OpenStreetMap contributors.
