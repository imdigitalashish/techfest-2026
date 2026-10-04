# Agent brief — EV Challenge 2 · Green Auto India (read this first, every agent)

**Project:** Techfest 2026 (IIT Bombay) × Ministry of Heavy Industries (MHI) × ICAT — *EV Infra & Green Mobility AI Challenge*, **Challenge 2: Green Auto India** — "Creation of an India-Specific Life Cycle Assessment Database for the Automotive Sector".
Official statement: `_briefs/ev-infra.txt` (repo root). Method: `PLAYBOOK.md` (repo root). Journal: `ev-c2-green-auto-lca/thought_node.md` (lead-owned; do not edit).

**What we are building:** an India-specific automotive LCA database (materials, components, manufacturing processes, energy, logistics, use phase, end-of-life, impact indicators) + a calculation engine + a web dashboard, demonstrated on a case study (first: Indian 2-wheeler petrol scooter vs battery-electric scooter; later 3W, cars, buses). Judges (MHI/ICAT officials, LCA experts) score "the intelligence, transparency, and defensibility of the approach rather than access to premium or proprietary datasets". Round 2 weights: technical & analytical robustness 25%, data quality & integration 20%, relevance & usability 20%, innovation 15%, scalability 10%, presentation 10%.

## Non-negotiable rules
1. **Zero hallucination.** Only cite a source you actually opened in this session (web_fetch / curl + pdftotext / python). Never cite from memory. If you cannot open it, either do not use it or mark the record `status: UNVERIFIED` and say why.
2. **Every number carries: value, unit, source (URL + title + publisher + year), locator (page/table/sheet/cell), a short verbatim quote, reference year, geography, and scope/boundary notes.** Emission factors must state gas basis (CO2 only vs CO2e, and which GWP set: AR4/AR5/AR6) and boundary (combustion-only, cradle-to-gate, well-to-wheel, ...).
3. Prefer, in order: (1) Indian government/official statistics (CEA, MoSPI, Ministry of Steel, BEE, PPAC, MoRTH, MHI, NITI Aayog); (2) Indian company disclosures (SEBI BRSR filings, sustainability/annual reports, EPDs); (3) peer-reviewed India-specific studies; (4) international datasets with an India region (IEA, IAI, worldsteel, GREET with India settings); (5) global proxies — label them `proxy` and say why no India value was used.
4. Newest first (2024–2026), but record older canonical sources when they are still the reference.
5. Synthetic or assumed values are allowed only when labelled `status: assumption` (or `synthetic`) with the reasoning.
6. If a search finds nothing, say so explicitly. Do not fill gaps.
7. **Do not run git commands that change state** (no add/commit/push/checkout/stash). The lead commits. Write only inside the paths you are assigned.
8. Large raw downloads (PDF/Excel > 1 MB) go to `ev-c2-green-auto-lca/.data/raw/<topic>/` (gitignored). Commit-able scripts that re-download them go to `ev-c2-green-auto-lca/data/fetch/`.
9. When done, **return a short summary (≤ 300 words)**: files written, record counts, the 5 most important findings, and open gaps. The full content lives in your files.

## Data record schema (YAML) — `data/factors/<layer>.yaml`
A YAML list. One record per number. Example (illustrative structure only — the value is a placeholder, not a fact):
```yaml
- id: energy.electricity.in.grid.cea_wavg.fy2023_24   # unique, lowercase, dot-separated: <layer>.<thing>.<geo>.<variant>.<year>
  layer: energy            # materials | components | processes | energy | fuels | logistics | use | eol | battery | vehicle | method
  name: India grid weighted-average CO2 emission factor (net generation basis)
  value: 0.000             # central value as published (number)
  unit: t CO2/MWh          # explicit unit, per reference quantity
  quantity: emission_factor  # emission_factor | energy_intensity | mass | mass_share | efficiency | consumption | distance | lifetime | share | price | other
  gas_basis: CO2           # CO2 | CO2e-AR6 | CO2e-AR5 | CO2e-AR4 | CO2e-unspecified | n/a
  boundary: combustion at power stations only; excludes upstream fuel chain and T&D losses
  geography: IN            # ISO-3166 (IN, CN, GLO, ...) or IN-<state code> (IN-MH)
  reference_year: "2023-24"
  technology: national grid-connected generation mix
  uncertainty:             # what the SOURCE gives; leave distribution: none if it gives nothing
    distribution: none     # none | range | normal | lognormal | triangular | uniform
    low: null
    high: null
    note: ""
  source_id: cea-co2-baseline-v20   # key into data/sources/<layer>.yaml
  locator: "User Guide v20.0, Table 4, p. 11"
  quote: "verbatim snippet (<= 300 chars) that contains the number; join non-contiguous fragments with ' ... '"
  accessed: 2026-10-04
  pedigree:                # 1 (best) .. 5 (worst), Weidema & Wesnaes / ecoinvent v3 pedigree matrix, judged for use as an INDIA value
    reliability: 1         # 1 verified measured data .. 5 non-qualified estimate
    completeness: 1        # 1 representative, all sites, adequate period .. 5 unknown
    temporal: 1            # 1 < 3 yrs from 2026 .. 5 > 15 yrs / unknown
    geographical: 1        # 1 India (or the exact state) .. 5 unknown / very different region
    technological: 1       # 1 same tech/route .. 5 related process, different tech
  status: verified         # verified (number seen in opened source) | derived (computed from verified records; give formula) | assumption | synthetic | UNVERIFIED
  derivation: ""           # for derived: formula with input record ids
  notes: ""
```
Sources — `data/sources/<layer>.yaml`:
```yaml
- id: cea-co2-baseline-v20
  title: "CO2 Baseline Database for the Indian Power Sector — User Guide, Version 20.0"
  publisher: Central Electricity Authority, Government of India
  year: 2024
  url: https://...
  type: government-dataset   # government-dataset | government-report | company-disclosure | peer-reviewed | grey-literature | standard | dataset | software | news
  accessed: 2026-10-04
  license: ""                # if stated
  local_copy: .data/raw/electricity/cea_v20_user_guide.pdf   # optional (gitignored)
  notes: ""
```
Benchmarks (published LCA results used for validation) — `data/benchmarks/<study-id>.yaml`: study metadata + list of reported results (value, unit, vehicle, powertrain, functional unit, boundary, geography, year, locator, quote) + the key input parameters the study states (lifetime km, grid EF, battery kWh and kg CO2e/kWh, fuel economy, energy use per km, mass) each with locator.

## Folder map (inside `ev-c2-green-auto-lca/`)
`research/notes/` raw research reports · `research/landscape.md` (lead) · `research/components/` per-component research · `architecture/` (lead: components, contracts, ADRs) · `data/` the database source of truth (YAML) · `components/<name>/` code · `eval/` harness · `deliverables/` round submissions · `.data/` gitignored downloads.
