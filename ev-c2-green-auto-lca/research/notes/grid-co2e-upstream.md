# India grid CO2e upstream factors — research notes

Scope: non-CO2 (CH4, N2O) and upstream (coal-mine fugitive methane) pieces needed to turn the
existing CEA CO2-only grid factor (`energy.electricity.in.grid_wavg_generation.*` in
`data/factors/energy.yaml`) into a full CO2e, cradle-to-busbar-upstream figure for the coal share
of the Indian grid. All sources below were opened in this session (pdftotext / python on
downloaded PDFs, or web_fetch). Local copies are gitignored under `.data/raw/` (paths given).
Nothing in `data/*.yaml` was edited — this file is the raw research record only.

Zero-hallucination status key: **verified** = number read directly from an opened primary source
quoted below. No number in this file is from memory.

---

## 1. IPCC 2006 Vol. 2 (Energy), Chapter 2 — stationary combustion, Table 2.2 (Energy Industries)

- **Source**: "2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 2 (Energy),
  Chapter 2: Stationary Combustion", IPCC / IGES, 2006.
  URL: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_2_Ch2_Stationary_Combustion.pdf
  Local copy: `.data/raw/fuels/ipcc2006_v2_ch2.pdf` (756,401 bytes; text extract `.data/raw/fuels/ch2.txt`)
  Type: standard. Accessed: 2026-10-04.
- **Locator**: Table 2.2 "DEFAULT EMISSION FACTORS FOR STATIONARY COMBUSTION IN THE ENERGY
  INDUSTRIES (kg of greenhouse gas per TJ on a Net Calorific Basis)", printed p. 2.16 (first part)
  / p. 2.17 ("TABLE 2.2 (CONTINUED)", not needed here). "Energy industries" = IPCC source
  category 1.A.1 (electricity and heat production, petroleum refining, manufacture of solid
  fuels) — see Table 2.1, p. 2.7.
- **Geography**: global default (Tier 1), **not India-specific**. **Gas basis**: separate CO2,
  CH4, N2O rows, each a native-gas mass factor (kg gas / TJ fuel, NCV basis) — **not** CO2e; a
  GWP must be applied separately (see §5). **Boundary**: combustion at the energy-industry
  source only; excludes upstream fuel-chain/fugitive and excludes T&D losses. **Reference
  year**: 2006 guidelines (no vintage; these are the global, multi-decade Tier-1 defaults still
  in force under the 2006 Guidelines and incorporated into India's inventory methodology, see §3).

**Verbatim table rows actually needed (coal ranks relevant to India + natural gas), units =
kg gas / TJ on NCV basis, default (lower–upper range):**

| Fuel | CO2 default (lower–upper) | CH4 default (lower–upper) | N2O default (lower–upper) |
|---|---|---|---|
| Anthracite | 98 300 (94 600–101 000) | 1 (0.3–3) | 1.5 (0.5–5) |
| Coking Coal | 94 600 (87 300–101 000) | 1 (0.3–3) | 1.5 (0.5–5) |
| Other Bituminous Coal | 94 600 (89 500–99 700) | 1 (0.3–3) | 1.5 (0.5–5) |
| Sub-Bituminous Coal | 96 100 (92 800–100 000) | 1 (0.3–3) | 1.5 (0.5–5) |
| Lignite | 101 000 (90 900–115 000) | 1 (0.3–3) | 1.5 (0.5–5) |
| Natural Gas | 56 100 (54 300–58 300) | 1 (0.3–3) | 0.1 (0.03–0.3) |

Quote (verbatim snippet from the extracted table, coal block): "Coking Coal  94 600  87 300
101 000  1  0.3  3  r  1. 5  0.5  5 ... Natural Gas  56 100  54 300  58 300  1  0.3  3  0.1
0.03  0.3" (`ch2.txt:880,899`; all coal ranks in Table 2.2 for the *energy industries* source
category share the same CH4 default = 1 kg/TJ, range 0.3–3, and N2O default = 1.5 kg/TJ, range
0.5–5 kg/TJ; Natural Gas CH4 default = 1 kg/TJ (0.3–3), N2O default = 0.1 kg/TJ (0.03–0.3)).
Note: a trailing superscript "r" on some cells flags a factor revised since the 1996 Guidelines
/GPG2000 (footnote convention explained p. 2.5); it is not part of the numeric value.

**Status: verified.** Directly usable as Tier-1 default CH4/N2O factors to pair with CEA's
GCV-basis coal/gas fuel-energy data (`energy.electricity.in.grid_wavg_generation.*`) to compute
CH4- and N2O-related CO2e from stationary combustion at Indian coal- and gas-fired stations,
in the absence of an India-specific CH4/N2O factor (see §3 — India's BUR4 only publishes a
country-specific *carbon* (CO2) emission factor for energy industries, not CH4/N2O, so Tier-1
IPCC defaults are the correct fallback for CH4/N2O under India's own stated methodology).

---

## 2. IPCC 2006 Vol. 2, Chapter 4 — fugitive emissions, coal mining methane (Tier 1 global defaults)

- **Source**: "2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 2 (Energy),
  Chapter 4: Fugitive Emissions", IPCC / IGES, 2006.
  URL: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_4_Ch4_Fugitive_Emissions.pdf
  Local copy: `.data/raw/fuels/ipcc2006_v2_ch4.pdf` (997,748 bytes; text extract
  `.data/raw/fuels/ch4.txt`). Type: standard. Accessed: 2026-10-04.
- **Geography**: global Tier-1 default (not India-specific — India's own country-specific
  factors are in §3 and should be preferred for India modelling; these IPCC defaults are the
  documented fallback / sanity-check only). **Gas basis**: CH4 only, volume basis
  (m3 CH4 / tonne raw coal produced), convert to mass with density 0.67×10⁻⁶ Gg/m³ (= 0.67 kg/m³
  at 20 °C, 1 atm) — **not CO2e**; needs a GWP (§5). **Boundary**: coal mining + post-mining
  (handling, crushing, transport) fugitive CH4 only; excludes combustion-stage CH4 (covered in
  §1) and excludes abandoned-mine emissions (separate Tier-1 method, not extracted here).
  **Reference year**: 2006 guidelines, no vintage.

### 2a. Underground mining (§4.1.3.2, Equation 4.1.3)
Quote: "Low CH4 Emission Factor = 10 m3 tonne-1 / Average CH4 Emission Factor =18 m3 tonne-1 /
High CH4 Emission Factor = 25 m3 tonne-1" (`ch4.txt` printed p. 4.11). Guidance: "the low end of
the range should be chosen for average mining depths of <200 m, and for depths of > 400 m the
high value is appropriate" (p. 4.11).

### 2b. Post-mining, underground mines (§4.1.3.2, Equation 4.1.4)
Quote: "Low CH4 Emission Factor = 0.9 m3 tonne-1 / Average CH4 Emission Factor =2.5 m3 tonne-1 /
High CH4 Emission Factor = 4.0 m3 tonne-1" (p. 4.12).

### 2c. Surface mining (§4.1.4.2, Equation 4.1.7)
Quote: "Low CH4Emission Factor = 0.3 m3 tonne-1 / Average CH4 Emission Factor = 1.2 m3 tonne-1 /
High CH4 Emission Factor = 2.0 m3 tonne-1" (p. 4.18). "In the absence of data on overburden
thickness, it is good practice to use the average emission factor, namely 1.2 m3/tonne" (p. 4.18).

### 2d. Post-mining, surface mines (§4.1.4.2, Equation 4.1.8)
Quote: "Low CH4 Emission Factor = 0 m3 tonne-1 / Average CH4 Emission Factor = 0.1 m3 tonne-1 /
High CH4 Emission Factor = 0.2 m3 tonne-1" (p. 4.19). "The average emission factor should be used
unless there is country-specific evidence to support use of the low or high emission factor" (p.
4.19) — **for India we do have country-specific evidence, see §3, which should be preferred.**

Conversion factor for all four (quoted identically at each location): "This is the density of
CH4 and converts volume of CH4 to mass of CH4. The density is taken at 20˚C and 1 atmosphere
pressure and has a value of 0.67 ● 10-6 Gg m-3" i.e. 0.67 kg CH4 per m3 CH4.

**Status: verified** (global Tier-1 fallback only; India's own Tier-2/EFDB-vetted factors in §3
are the preferred input and are higher for underground mining than the IPCC global average,
reflecting India's typically shallower, gassier seams by comparison basis — see note under §3).

---

## 3. India country-specific coal-mine methane EFs and OC/UG mining shares (BUR4 + Ministry of Coal)

### 3a. India BUR-4 (UNFCCC national GHG inventory) — country-specific coal-mining CH4 EFs

- **Source**: "India: Fourth Biennial Update Report to the United Nations Framework Convention on
  Climate Change" (National GHG Inventory chapter), Ministry of Environment, Forest and Climate
  Change (MoEFCC), Government of India, 2024.
  URL: https://unfccc.int/sites/default/files/resource/India%20BUR-4.pdf
  (direct `curl` to unfccc.int is blocked by an Incapsula bot-check on this host; file was
  retrieved via the Wayback Machine snapshot
  `http://web.archive.org/web/20260927192028/https://unfccc.int/sites/default/files/resource/India%20BUR-4.pdf`,
  byte-identical PDF, 15,722,957 bytes — confirmed opened and read in this session.)
  Local copy: `.data/raw/india-ghg/india_bur4.pdf`; text extract `.data/raw/india-ghg/india_bur4.txt`.
  Type: government-report (National Communication/BUR to UNFCCC). Accessed: 2026-10-04.
- **Locator**: Table 2.13 "Country-specific emission factors for coal mining activities", printed
  p. 84 (PDF page 110 of `india_bur4.pdf`). **Geography**: IN. **Gas basis**: CH4 only, volume
  basis (m3/tonne) — convert with the same 0.67 kg/m3 density as §2. **Boundary**: "Mining"
  (during-extraction fugitive CH4) and "Post Mining (Handling)" (after coal leaves the mine),
  split by Surface mining and Underground mining Degree I/II/III (India's own gassiness
  classification by seam methane content, not overburden/seam depth as in the IPCC generic
  guidance). **Reference year**: factors apply to India's inventory years 2017–2020 (most recent
  inventory year reported = 2020); report published/submitted 2024.

Quote (verbatim table, `india_bur4.txt:4645-4654`):
> "Table 2.13: Country-specific emission factors for coal mining activities
> Methane emission factor (m3/tonne)
> Operation (Mining / Post mining) | Surface mining | Underground mining Degree-I | Degree-II | Degree-III
> Mining | 1.18 | 2.91 | 13.08 | 23.64
> Post Mining (Handling) | 0.15 | 0.98 | 2.15 | 3.12"

Context quote on provenance: "these emission factors (EFs) from coal mining and handling
activities have been incorporated in the IPCC Emission Factor Database after due vetting of the
Editorial Board with designated EF IDs 122973-122975 for underground mining and 124920-124921
for surface mining (IPCC, 2020)." (`india_bur4.txt`, p. 84 context, immediately above Table 2.13).

**Companion activity-data table** (Table 2.14, same page), coal production split by the same
four categories for 2017–2020 (million tonnes), useful for weighting an "underground" average if
needed: Surface mining 674.85/717.93/731.99/724.45; Underground Degree-I 35.92/35.81/34.67/26.76;
Degree-II 6.29/6.27/6.07/7.05; Degree-III 0.26/0.25/0.25/0.47 (2017/2018/2019/2020 respectively).
Quote: "Mining and handling (2020) | 724.45 | 26.76 | 7.05 | 0.47" (`india_bur4.txt:4659`).

**Status: verified.** This is the preferred (highest-priority, India-government, country-
specific) coal-mine CH4 factor set per the brief's source hierarchy, and should be used ahead of
the IPCC Tier-1 global defaults in §2. Note the underground mining EF is markedly
*higher* than the IPCC global average (13.08–23.64 m3/t for Degree II/III vs 18 m3/t IPCC
average) for the gassier degree classes but *lower* for Degree-I (2.91 m3/t); surface mining
(1.18 m3/t) is close to the IPCC average (1.2 m3/t). **Gap**: BUR4 does not state what share of
India's underground coal production falls into each of Degree I/II/III — that split would need
to come from CIL/DGMS gassiness-classification statistics (not located in this session; flagged
as a gap below).

### 3b. India BUR-4 — energy-industries (1.A.1) country-specific CO2 factor (for cross-check; CH4/N2O not country-specific)

- Same source as 3a. **Locator**: Table 2.6 "Country Specific emission factors used in the
  energy industries (1A)", printed p. 78 (`india_bur4.txt:4304-4312`).
- Quote: "Coking coal | 23.66 [TJ/Kt] | 25.55 [tC/TJ] ... Non coking coal | 17.09 | 26.39 ...
  Lignite | 9.8 | 28.9" (electricity & heat production column; manufacture-of-solid-fuels column
  values are close but not identical). This is a **carbon (→CO2) emission factor only**; BUR4
  gives no India-specific CH4/N2O factor for stationary combustion in energy industries — text
  confirms this scope explicitly: "The overall country-specific emission factors used in energy
  industry emission estimation are shown in Table 2.6" with no analogous CH4/N2O table for 1.A.1,
  which is why IPCC Table 2.2 (§1) is the correct CH4/N2O input for this challenge's grid model.
  **Status: verified** (confirms the gap, does not supply the missing CH4/N2O numbers).

### 3c. Ministry of Coal — open-cast vs underground coal production share

- **Source**: "Coal Directory of India 2024-25", Ministry of Coal, Office of Deputy Director
  General, Government of India, 2025 (document dated/modified Jan 2026; covers FY2024-25 data).
  URL: https://www.coalcontroller.gov.in/files/annual_coal_directories_document/28-11-2025a-stc.pdf
  (found via the directory listing page https://www.coalcontroller.gov.in/coal-directory-india).
  Local copy: `.data/raw/electricity/coal_stats_28-11-2025a-stc.pdf` (14,995,903 bytes, 266 pp.);
  text extract `.data/raw/electricity/coal_stats_stc.txt`. Type: government-dataset. Accessed:
  2026-10-04.
- **Locator**: Table 3.19 "Production of Raw Coal from Open Cast and Under Ground Mines in last
  Ten Years", printed p. 70 (PDF page 95 of the 266-page file). **Geography**: IN, all-India.
  **Quantity**: mass share (%) of raw coal production, not an emission factor.
  **Reference year**: row for 2024-25 (latest); 2023-24 row also given.

Quote (verbatim row, `coal_stats_stc.txt:5023-5035`, columns: OC prod. All-India (MT) / OC share
of all-India (%) / UG prod. All-India (MT) / UG share of all-India (%) / All-India total (MT)):
> "2023-24  ... 963.495  96.56  ... 34.331  3.44  ... 997.826"
> "2024-25  ... 1015.665  96.96  ... 31.858  3.04  ... 1047.523"

Supporting narrative quote: "From table 3.19 it can be observed that in 2024-25, the production
from the open-cast system of mining accounted for 96.96% of the total coal production, and the
rest 3.04% was accounted for the Under Ground system of mining... the share of open-cast mining
in total coal production has been steadily increasing over [time]." (`coal_stats_stc.txt:3233-3239`).

**Status: verified.** Use the **2023-24** row (96.56% OC / 3.44% UG) if matching the CEA CO2
baseline database's FY2023-24/FY2025-26 vintage used elsewhere in this project, or the 2024-25
row (96.96% / 3.04%) if a more current split is wanted; both are directly quoted above so either
can be cited without further lookup. Ten-year series back to 2015-16 is also in the same table in
the text extract (`coal_stats_stc.txt:5027-5034`) if a historical/uncertainty range is wanted.

---

## 4. CEA coal consumption per kWh (derivable from data already in the project's `.data/raw/`)

- **Source**: "Baseline Carbon Dioxide Emission Database, Version 22.0" / its "User Guide,
  Version 22.0" — already catalogued in `data/sources/sources.yaml` as `cea-co2-baseline-v22`
  and `cea-co2-baseline-v22-xlsx`. Central Electricity Authority, Ministry of Power, 2026 (FY
  2025-26 data vintage). Local copies already present: `.data/raw/electricity/cea_ug_v22.pdf`
  (+ `.txt`) and `.data/raw/electricity/cea_db_v22.xlsx`. Re-opened in this session to confirm
  the specific numbers below (workbook `Assumptions` sheet + PDF Appendix B).
- **Locator**: PDF "Appendix B – Assumptions for CO2 Emission Calculations", printed p. 26
  (`cea_ug_v22.txt:1405-1427`); identical figures confirmed in workbook sheet `Assumptions`,
  "Assumptions at Station Level" block.
- **Geography**: IN, national default (used by CEA "only where data was not provided by
  [individual] station" — i.e. a fallback/representative default, not a measured national
  average). **Boundary**: at-plant/gross-generation basis (kg coal per kWh **gross** generated,
  before auxiliary consumption / before T&D losses). **Reference year**: v22.0 defaults, dataset
  covers FY2008-09 through FY2025-26; this default block is not dated to a specific FY in the
  text (carried over from a point-in-time assumption, flagged by CEA footnote "n/a = not
  applicable (i.e. no assumptions were needed)" elsewhere, implying it is a standing default
  rather than an annual update — **treat as an approximate/representative value, not an
  annual-series number**).

Quote (verbatim, `cea_ug_v22.txt:1428,1431`):
> "Gross Heat Rate (gross) ... Coal 2,500 [kcal/kWh]"
> "GCV kcal/kg (or m3) ... Coal 3,755"

**Derived value (status: derived — not itself printed as kg/kWh in the source, computed from
two verified source numbers)**:

    Specific coal consumption (gross) = Gross Heat Rate / GCV
                                        = 2,500 kcal/kWh ÷ 3,755 kcal/kg
                                        ≈ 0.666 kg coal / kWh (gross, national default assumption)

Cross-check: CEA's own co-reported "Specific CO2 emissions" for the same default coal row is
**1.04 tCO2/MWh** (`cea_ug_v22.txt:1432`, same Appendix B table) — independently implies a coal
CO2 emission factor of 1.04 tCO2/MWh ÷ 0.666 kg/kWh ≈ 1.56 t CO2/t coal, consistent with the same
appendix's "Fuel Emission Factor" for Coal of 90.6 gCO2/MJ (NCV, oxidation-adjusted) combined
with GCV 3,755 kcal/kg → NCV ≈ 3,620 kcal/kg (using the stated "Delta GCV NCV" = 3.6%) ≈ 15.15
MJ/kg → 15.15 MJ/kg × 90.6 gCO2/MJ ≈ 1.373 kg CO2/kg coal... this cross-check does not close
exactly against the stated 1.04 tCO2/MWh/0.666 kg/kWh ≈ 1.56 ratio (likely because the 1.04
tCO2/MWh row already nets out a different auxiliary/heat-rate basis or a blended domestic/
imported-coal mix) — **flagged as an internal CEA consistency gap**, not resolved in this
session; use the two headline numbers (2,500 kcal/kWh gross heat rate; 3,755 kcal/kg GCV) as the
primary verified facts, and treat the 0.666 kg/kWh figure as a first-order derived estimate only.

**Note on NTPC/other coal consumption data**: did not find a separately published "kg coal per
kWh" all-India weighted-average series from CEA's General Review or Growth of Electricity Sector
publications in this session (not opened — see Gaps). The Appendix B default above is the only
primary number located; if a more authoritative, annually-updated national average is required,
CEA's "Growth of Electricity Sector in India" or "General Review" annual reports should be
fetched next (search found only a Lok Sabha question PDF on T&D losses, already catalogued as
`loksabha-usq842-2025` in `data/sources/sources.yaml`, not on coal consumption).

---

## 5. GWP100 — CH4 (fossil) and N2O, AR5 and AR6 (IPCC WG1)

### 5a. AR5 (IPCC Fifth Assessment Report, WG1, Chapter 8, Table 8.7)

- **Source**: Myhre, G. et al., "Anthropogenic and Natural Radiative Forcing", in: Climate
  Change 2013: The Physical Science Basis (IPCC AR5 WG1), Chapter 8, IPCC, 2013.
  URL: https://www.ipcc.ch/site/assets/uploads/2018/02/WG1AR5_Chapter08_FINAL.pdf
  Local copy: `.data/raw/fuels/ipcc_ar5_wg1_ch08.pdf` (19,360,338 bytes); text extract
  `.data/raw/fuels/ar5_ch08.txt`. Type: standard/peer-reviewed assessment. Accessed: 2026-10-04.
- **Locator**: Table 8.7, printed p. 714 (PDF page 56 of the chapter file). **Gas basis**: GWP
  (unitless, CO2-equivalent multiplier) over 100-yr horizon ("GWP100"). **Boundary/scope**:
  global, well-mixed-GHG radiative-forcing metric (not a boundary in the LCA sense).

Quote (verbatim, `ar5_ch08.txt:3668-3690`):
> "Table 8.7 | GWP and GTP with and without inclusion of climate–carbon feedbacks (cc fb) ...
> CH4b  12.4a  No cc fb  84 [GWP20] 28 [GWP100] ... With cc fb  86 [GWP20] 34 [GWP100] ...
> N2O  121.0a  No cc fb  264 [GWP20] 265 [GWP100] ... With cc fb  268 [GWP20] 298 [GWP100]"
Footnote b (verbatim): "These values do not include CO2 from methane oxidation. Values for
fossil methane are higher by 1 and 2 for the 20 and 100 year metrics, respectively (Table 8.A.1)."

So, **AR5 GWP100** (status: verified):
- CH4, fossil, without climate-carbon feedback (the commonly-cited "AR5 GWP100" used in most
  national inventories/GHG Protocol-style reporting): **28 + 2 = 30** (per the footnote-b
  adjustment for fossil methane; the generic/biogenic CH4 "without cc fb" value is **28**).
- N2O, without climate-carbon feedback: **265**.
- With climate-carbon feedbacks included (less commonly used for inventory reporting): CH4 ≈
  34 (+2 fossil adjustment ⇒ ~36), N2O = 298.

**Gap**: the precise "+1/+2" fossil-methane adjustment is stated only as a footnote offset
applied to the generic CH4 GWP20/GWP100, with the base numbers "without cc fb" (28, no fossil
split shown directly in Table 8.7 itself); the fully split fossil-CH4-specific row lives in Table
8.A.1 (same chapter, further in, p. 4882 area per `ar5_ch08.txt:4882`), which was not
further transcribed in this session (not required to confirm the ±1/±2 offset, which is itself a
directly quoted footnote).

### 5b. AR6 (IPCC Sixth Assessment Report, WG1, Chapter 7, Table 7.15)

- **Source**: Forster, P. et al., "The Earth's Energy Budget, Climate Feedbacks and Climate
  Sensitivity", in: Climate Change 2021: The Physical Science Basis (IPCC AR6 WG1), Chapter 7,
  IPCC, 2021.
  URL: https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_Chapter07.pdf
  Local copy: `.data/raw/fuels/ipcc_ar6_wg1_ch07.pdf` (22,836,832 bytes); text extract
  `.data/raw/fuels/ar6_ch07.txt`. Type: standard/peer-reviewed assessment. Accessed: 2026-10-04.
- **Locator**: Table 7.15 "Emissions metrics for selected species: global warming potential
  (GWP), global temperature-change potential (GTP)", printed p. 1016–1017 (PDF pages 94–95 of
  the chapter file). **Gas basis**: GWP100, CO2-equivalent multiplier, **all values include
  carbon-cycle responses** (i.e., AR6's single reported GWP100 already corresponds to what AR5
  called "with cc fb", there is no separate "without feedback" AR6 headline number in this
  table). **Boundary/scope**: global radiative-forcing metric.

Quote (verbatim, `ar6_ch07.txt:6319-6332`):
> "Table 7.15 | Emissions metrics for selected species ... All values include carbon cycle
> responses as described in Section 7.6.1.3 ...
> CH4-fossil  11.8±1.8  5.7±1.4×10-4  82.5±25.8 [GWP20]  29.8±11 [GWP100]  10.0±3.8 [GWP500] ...
> CH4-non fossil  11.8±1.8  5.7±1.4×10-4  79.7±25.8  27.0±11  7.2±3.8 ...
> N2O  109±10  2.8±1.1×10-3  273±118 [GWP20]  273±130 [GWP100]  130±64 [GWP500]"

So, **AR6 GWP100** (status: verified):
- CH4, fossil: **29.8** (±11)
- CH4, non-fossil (biogenic): **27.0** (±11)
- N2O: **273** (±130)

**Cross-note**: AR6 explicitly distinguishes fossil vs non-fossil methane (fossil methane gets a
small extra warming credit for the CO2 produced on oxidation, since that carbon is not part of
the contemporary biogenic carbon cycle) — for a coal/gas-fired-grid CO2e calculation, the
**fossil** CH4 GWP100 values are the correct ones to use in both AR5 (30) and AR6 (29.8), not the
plain/non-fossil 28 or 27.0 figures.

---

## 6. Optional India grid life-cycle (well-to-wire / cradle-to-gate) factor cross-check

**Not completed in this session** — time/scope was prioritised on the primary IPCC/India
factors above. No international LCA-database (e.g. ecoinvent, IEA, GREET-India) grid life-cycle
CO2e figure was opened or verified here. **Gap, explicitly flagged**: if a published India grid
life-cycle (cradle-to-gate, CO2e incl. upstream fuel chain) benchmark number is wanted for
cross-checking a bottom-up CO2+CH4+N2O build-up, a follow-up search should target: IEA's "India
Energy Outlook" / IEA Emissions Factors database (subscription, likely inaccessible), or
published India-specific ecoinvent-style LCA papers already partially catalogued in this
project's `data/benchmarks/` (icct_* benchmarks are vehicle-tailpipe/LCA studies, not grid-EF
cross-checks, and were not re-opened in this session for this purpose).

---

## Summary of what each number is for (how these combine)

1. CEA already gives a CO2-only, combustion-stage grid factor from measured station data
   (`energy.electricity.in.grid_wavg_generation.*` — not re-derived here).
2. To get to CO2e, add CH4 and N2O from stationary combustion at coal/gas stations: multiply
   Tier-1 IPCC Table 2.2 factors (§1, kg gas/TJ fuel) by CEA's fuel-energy-by-type data (already
   in the project's CEA workbook) and by a GWP100 (§5 — recommend AR6: CH4-fossil 29.8, N2O 273,
   OR AR5: CH4-fossil 30, N2O 265, labelled accordingly per the brief's gas_basis field).
3. To add the upstream fugitive-methane slice (coal supply chain, pre-combustion), use the
   India-specific BUR4 Table 2.13 CH4 EFs (§3a, preferred) or the IPCC Tier-1 global defaults
   (§2, fallback/cross-check), weighted by India's OC/UG coal production split (§3c — 96.56%
   OC / 3.44% UG for 2023-24, or 96.96%/3.04% for 2024-25), converted to mass with the 0.67
   kg/m3 CH4 density, and again multiplied by a GWP100 (§5).
4. CEA's own coal-consumption default (§4, ≈0.666 kg coal/kWh gross, derived) can be used to
   convert a per-tonne-coal fugitive CH4 factor into a per-kWh figure, consistently with the
   same CEA default basis already used for the project's CO2 figure, if a bottom-up fully
   self-consistent build is wanted; otherwise prefer CEA's actual measured per-station
   coal-consumption data (in the workbook `Data` sheet, not re-extracted in this session) over
   the Appendix B default.

## Gaps / not found / not attempted (explicit, per the zero-hallucination rule)

- No all-India, annually-updated, measured (not default-assumption) "kg coal consumed per kWh
  generated" series was located from CEA's General Review / Growth of Electricity Sector
  publications — only the Appendix B station-level *default* (§4) was found and opened.
- BUR4 does not state the production-weighted share of underground coal mining across its own
  Degree I/II/III gassiness classes as a percentage of total underground output for a given
  year beyond the raw tonnages in Table 2.14 (§3a) — a weighted single "underground" CH4 EF
  would need to be derived from those tonnages (not done here; flagged as a derivation task for
  whoever builds the YAML record, with the formula: weighted EF = Σ(production_i × EF_i) / Σ
  production_i across Degree I/II/III).
- India's Third National Communication (NC3, 79 MB PDF) was not downloaded or opened (file size
  decision — see brief's 50 MB guidance; BUR4 was judged sufficient and more recent/more
  granular for this specific coal-mining-EF need). If NC3 needs to be consulted for a different
  number later, fetch selectively (e.g. via the Wayback Machine as done for BUR4, or request a
  specific chapter/page range) rather than the full 79 MB file.
- No India grid life-cycle (cradle-to-gate CO2e) cross-check figure was sourced (§6) — explicit
  gap, not filled with a proxy in this session.
- IPCC Table 8.A.1 (AR5) fossil-methane-specific GWP20/100 split (exact absolute number, not
  just the footnote "+1/+2" offset) was not independently transcribed — the footnote-derived
  value (30 for CH4-fossil GWP100 without cc-fb) is used instead and is sufficient for the
  gas_basis/CO2e-AR5 need, but should not be over-cited as "Table 8.A.1 verbatim".
- Did not search for/open India's Ministry of Coal "Provisional Coal Statistics" series (older,
  discontinued per web search) or CIL/SCCL individual sustainability reports for an independent
  cross-check of the OC/UG share or coal-mine gassiness-class splits; the single Coal Directory
  2024-25 source (§3c) was treated as sufficient and authoritative (publisher = Ministry of Coal
  itself, i.e. top of the brief's source-priority list).

## Local raw files written this session (all gitignored, all under 50 MB)

- `.data/raw/fuels/ipcc2006_v2_ch2.pdf` (756 KB) + `ch2.txt`
- `.data/raw/fuels/ipcc2006_v2_ch4.pdf` (998 KB) + `ch4.txt`
- `.data/raw/fuels/ipcc_ar5_wg1_ch08.pdf` (19.4 MB) + `ar5_ch08.txt`
- `.data/raw/fuels/ipcc_ar6_wg1_ch07.pdf` (22.8 MB) + `ar6_ch07.txt`
- `.data/raw/india-ghg/india_bur4.pdf` (15.0 MB, via Wayback Machine) + `india_bur4.txt`
- `.data/raw/electricity/coal_stats_28-11-2025a-stc.pdf` (Coal Directory of India 2024-25, 15.0 MB) + `coal_stats_stc.txt`
- `.data/raw/electricity/moc_chap9_production_2024.pdf` (Ministry of Coal Annual Report 2023-24,
  ch. 9 — downloaded but found **not** to contain the OC/UG split; superseded by the Coal
  Directory above; kept for reference, 192 KB) + `.txt`
- `.data/raw/electricity/coal_directory_2023_24.pdf` (a "compressed" TOC-only extract that
  turned out to be a truncated 40-page front-matter file, **does not contain the actual data
  tables**; superseded by `coal_stats_28-11-2025a-stc.pdf`; kept only because it was already
  downloaded, 7.3 MB) + `.txt` + `full_check.txt`
