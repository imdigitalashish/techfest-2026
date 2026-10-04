# V5: NFHS-5 district values spot-verified against IIPS fact sheets (lead, 2026-10-04 18:30 IST)

- **Data:** NFHS-5 (2019–21) district indicators for 707 districts (708 rows with a wasting value), rebuilt by [`eval/fetch_nfhs5.py`](../../eval/fetch_nfhs5.py) from the compilation https://github.com/SaiSiddhardhaKalla/NFHS (`India.csv`, last push 2022-05-19). **The compilation repo has no licence.** Cite the numbers to the official source (IIPS/MoHFW NFHS-5 District Fact Sheets) and don't redistribute its files (e.g. its `Districts.geojson`) wholesale.
- **Official PDFs:** the repo mirrors the IIPS district fact sheets under `pdfs/<state>/<district>`. Page 1 of the Hingoli PDF reads "District Fact Sheet", "National Family Health Survey", "International Institute for Population Sciences", "Ministry of Health and Family Welfare". The old rchiips.org URLs return 404; the new IIPS site (nfhsiips.in) has no direct links.
- **Spot check (lead, pypdf text extraction):** 4 districts drawn at random (`random.seed(20261004)`, one per state among Maharashtra, Jharkhand, Odisha, Uttar Pradesh), plus 2 purposive (Amravati, which contains Melghat, and Nandurbar). Four indicators each, children under 5: stunted, wasted, severely wasted, underweight. **24/24 exact matches.**

| District (State) | Stunted | Wasted | Severely wasted | Underweight | PDF sha256 (prefix) |
|---|---|---|---|---|---|
| Hingoli (MH) | 37.4 | 25.8 | 10.5 | 38.9 | 45042df572aa |
| Chatra (JH) | 42.2 | 17.2 | 3.9 | 39.8 | 87ab44de8b4e |
| Nuapada (OD) | 43.1 | 18.1 | 3.7 | 38.0 | 2e8c58e67268 |
| Kannauj (UP) | 43.0 | 21.5 | 10.8 | 33.5 | 924f00ce498c |
| Amravati (MH), contains Melghat | 29.0 | 26.2 | 10.7 | 38.0 | 995e6fd3a09e |
| Nandurbar (MH) | 45.8 | 30.7 | 13.5 | 57.2 | 1a0c37c66622 |

- **Note:** the earlier "12/12" in `fetch_nfhs5.py`'s docstring pointed to an R7b note that the (crashed) agent never wrote. This V5 check replaces it.
- **Context (REAL, [V4](V4-state-gap-verified.md)):** Maharashtra's NFHS-5 wasting is 25.6%; Poshan Tracker reported 4.01% for June 2025.
