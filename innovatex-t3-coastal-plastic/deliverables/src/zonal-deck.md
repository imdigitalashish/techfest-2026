---
marp: true
theme: default
paginate: true
size: 16:9
header: "NullahNet · InnovateX 2026 · Theme 3 · Delhi zonal"
footer: "Every number: research/fact-check.md or eval/RESULTS.md"
style: |
  section { font-size: 23px; }
  h1 { font-size: 36px; }
  table { font-size: 18px; }
  .small { font-size: 15px; color: #555; }
  .tag { font-size: 14px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: #eef2f5; }
---

<!-- _class: lead -->
# NullahNet
### Make Mumbai's nullah trash booms accountable: clear them at the right tide, stop them leaking, pay per verified kilogram

**Team:** ‹TEAM NAME› · **Team ID:** ‹ID› · **Theme 3:** Rising plastic pollution in coastal cities
‹Member 1 — role› · ‹Member 2 — role› · ‹Member 3 — role› · ‹Member 4 — role› · ‹email / phone›

<span class="tag">BUILT</span> software we ran · <span class="tag">SIMULATED</span> digital-twin output · <span class="tag">SYNTHETIC</span> generated test data · <span class="tag">SENSITIVITY</span> assumption-driven · <span class="tag">PLANNED</span> not built yet

<!--
TIME 0:00–0:30 (30 s). LOGISTICS: present zonal-deck.pdf from your own laptop; the dashboard (components/dashboard/site, served with python3 -m http.server) open in a second tab, offline.
SAY: "We're ‹team›. Our problem is one specific leak: floating single-use packaging escaping through Mumbai's small storm-water outfalls. Mumbai already has trash booms; we make them work harder and make their numbers trustworthy."
LINE TO LAND: "We don't propose another barrier. We make the city's existing barriers accountable."
DON'T SAY "we built a prototype". The software is built; the hardware is PLANNED.
-->

---

# The leak: one city, millions of kilograms a year

| What | Value | Source |
|---|---|---|
| Plastic released to the sea by the metropolitan region | {{f:F01|an estimated 5 million kg a year}} | The Ocean Cleanup survey, 10 Feb 2026 |
| Damage footprint | {{f:F01|220 km of coastline, 152 km² of mangroves}} | same |
| Main pathways | {{f:F04|"around 50 drains and nullahs"}} | Lokmat Times (2026), reporting the same study |
| Independent global model | {{f:F05|Malad Creek ranked #30 of 31,819 outfalls worldwide}} | Meijer et al. 2021 (modelled, not measured) |
| The network that carries it | {{f:F06|186 outfalls}}; most drains built for {{f:F06|about 25 mm/h of rain at low tide}} | BRIMSTOWAD, via a secondary summary |
| What one storm brings back | BMC removed {{f:F07|2,498.66 t}} of marine waste from {{f:F07|seven beaches in 11 days}} (July 2026) | Mumbai Live, Jul 2026 |

<!--
TIME 0:30–1:40 (70 s).
SAY: "The 5-million-kilogram figure in the problem statement comes from The Ocean Cleanup's 2026 survey of Mumbai. An independent global model puts Malad Creek alone among the top 30 river mouths on Earth. The plastic reaches the sea through drains like these: about 186 outfalls, built for modest rain at low tide."
LINE TO LAND: "In July 2026, BMC pulled {{f:F07|2,498.66 t}} of waste off seven beaches in 11 days. That is the sea handing back what the drains gave it."
DON'T SAY the tonnage was measured. It is a survey estimate. If asked, the model (Meijer) and the survey disagree on exact tonnage; both put Mumbai among the largest urban sources.
-->

---

# Our specific source: floating single-use flexible packaging

- Plastic is {{f:F09|75.5 %}} of {{f:F09|52,770}} litter items counted on Juhu and Aksa beaches <span class="small">(CIFE study, HT 2023)</span>
- Carry bags, films and multilayer sachets have almost no resale value. Waste-picker groups report companies ignore them (about {{f:F25|60%}} of one group's dry waste), and that sachets are sometimes **given to cement kilns for free** <span class="small">(Break Free From Plastic, 2023, pp. 40–41)</span>
- The 2018 ban hasn't stopped them. In 2024 BMC fined {{f:F10|44,448}} establishments but confiscated only {{f:F10|2,148 kg}} <span class="small">(Mumbai Live)</span>
- An older BMC estimate: {{f:F08|500 t/day}} is never collected and "ends up in the storm water drains" <span class="small">(Citizen Matters)</span>

**Why this source:** it is light, so the first monsoon storms flush it; it is the residue that collection misses; and it slips under booms.

<!--
TIME 1:40–2:30 (50 s).
SAY: "Bottles have a price, so someone picks them up. Films and sachets don't, so they are what's left for the rain to wash into the nullahs."
LINE TO LAND: "We target the plastic nobody is paid to collect."
DON'T SAY "pickers never collect film". The source says companies disregard low-value plastics and only a small fraction of MLP is collected under EPR.
-->

---

# Mumbai already intercepts. The gap is accountability.

| Who | What they do | Scale (source) |
|---|---|---|
| **BMC** | Steel-net trash booms with conveyors at nullah mouths, cleared daily by contractors | {{f:F12|9}} booms, growing to {{f:F12|23}}; {{f:F12|≈ ₹1 crore}} each; {{f:F12|1.5 t/day}} dry, {{f:F12|2.5–3 t/day}} monsoon per boom (HT, May 2025) |
| | Two-year operations and maintenance contract | {{f:F13|₹14.5 crore}} for six rivers and nullahs (FPJ, 30 Jul 2026) |
| **The Ocean Cleanup + Plastic Fischer** | Interceptors at Malad and Trombay creeks, MCGM permits, MPCB MoU | {{f:F02|61 to 92 tonnes}} a year expected from the first systems ≈ {{f:D01|1.2–1.8 %}} of the estimated leak |
| **Plastic Fischer** (elsewhere) | Low-tech TrashBooms; kilograms verified by third-party software | {{f:F16|3.2 million kg}}, {{f:F16|71}} booms, {{f:F16|8}} sites in India and Indonesia |

**The gap:** the booms have no sensors, clearance follows the contract rather than the tide or the rain, and payment follows claimed loads. In the Mithi desilting case, the SIT's FIR cites a {{f:F11|₹65.54 crore}} loss to BMC (allegations under investigation; The Hindu, May 2025).

<!--
TIME 2:30–3:30 (60 s).
SAY: "This is not an empty field. BMC is going from 9 to 23 booms at about a crore each, and The Ocean Cleanup is coming to Malad and Trombay — the two outlets in your problem statement. What nobody has is a way to know when a boom is about to fail, and whether the tonnage on the invoice was really caught."
LINE TO LAND: "Two Interceptors cover two creeks. NullahNet is for the other booms."
DON'T SAY anything about guilt in the Mithi case: it is a police investigation into alleged inflated quantities.
-->

---

<style scoped>section { font-size: 20px; }</style>

# Where plastic gets past a boom <span class="tag">SIMULATED</span>

![bg right:48% fit](figures/fig_escape_split.png)

Digital twin of four Mumbai outfalls, held-out monsoons 2024–25, {{r:n_draws}} Monte Carlo draws:
- **{{r:ent_esc}}** of escaped plastic slips **under or through the boom** (interval {{r:ent_esc_lo}}–{{r:ent_esc_hi}}), including the leak the twin assumes even in still water
- Overflow of a full pocket: {{r:over_esc}} · flood release: {{r:byp_esc}}
- Booms lose their catch above about {{f:F14|0.35 m/s}} across the boom, whatever the skirt depth <span class="small">(ITOPF)</span>
- The flood tide lifts back {{r:refloat_arr}} of arrivals, to re-arrive on the ebb

**Levers:** angle the boom · stop the flood tide emptying the pocket · time clearance · measure

<!--
TIME 3:30–4:40 (70 s).
SAY: "We built a twin of four real outfalls, driven by real rain, archived forecasts and fitted tides. Most of what escapes slips under the boom when the flow is fast, not over the top. That matches oil-spill boom practice: above about a third of a metre per second, booms leak."
LINE TO LAND: "Booms don't mainly fail by filling up; they fail by being too square to the flow."
DON'T SAY the twin "measured" anything. It computes with assumed curves; it ranks levers, it does not promise tonnes. The capture curve's midpoint is an ASSUMPTION based on oil-boom practice.
-->

---

# NullahNet: retrofit the booms Mumbai already owns

| Layer | What it is | Status |
|---|---|---|
| **1 · Fill eye** | Solar camera + ultrasonic range sensor over each boom pocket: how full, how fast it's filling | node designed and priced (PLANNED) |
| **2 · Tide-and-rain twin** | Per outfall: real ERA5 rain, archived JMA day-ahead forecasts, harmonic tide (fit RMSE {{r:tide_rmse_mithi}} m at the Mithi) | BUILT |
| **3 · Crew dispatch** | Each morning: which boom to clear and when, timed to tide windows and the next 24 h of forecast rain | BUILT (in the twin) |
| **4 · Hardware retrofit** | Angle the boom; add a one-way pocket so the flood tide can't lift the catch out; add a **fail-open fuse** so a jammed boom never raises upstream flood levels | PLANNED (flume test) |
| **5 · Signed evidence records** | Every clearance: before/after fill, weighbridge, GPS; hash-chained and signed; paid per verified kg | BUILT |

Prior art we build on: passive floating litter traps for tidal waterways already exist (Bandalong, {{f:F21|"wider than 2 metres, including waterways subject to tidal action"}}). Our contribution is the retrofit for BMC's booms, plus the operations and the evidence.

<!--
TIME 4:40–5:40 (60 s).
SAY: "Five layers, all bolted onto what exists. Eyes on the pocket, a twin that knows the tide and tomorrow's rain, a dispatch plan, a hardware retrofit, and records nobody can quietly edit."
LINE TO LAND: "No new civil works. We change when crews go, how booms sit, and how contractors are paid."
DON'T SAY "our trap is novel". One-way floating traps exist; our claim is the retrofit plus the fail-open safety and the instrumentation, and only what the flume shows.
-->

---

<style scoped>section { font-size: 20px; }</style>

# Evidence 1 · Timing the crews <span class="tag">SIMULATED</span>

![bg right:52% fit](figures/fig_levers.png)

Held-out monsoons 2024–25; equal crew-hours ({{r:crew_budget}}); paired over {{r:n_draws}} draws:
- **Tide-aware vs clear-when-full:** escaped plastic **{{r:p2p1_med}}** (90% interval {{r:p2p1_lo}} to {{r:p2p1_hi}}); better in **{{r:p2p1_n}} of {{r:n_draws}}** draws
- **vs today's fixed schedule:** {{r:p2p0_med}} (interval {{r:p2p0_lo}} to {{r:p2p0_hi}}): small and uncertain
- Clear-when-full alone is *worse* than the fixed schedule ({{r:p1p0_med}})
- Decisions use only forecasts archived before the fact

<!--
TIME 5:40–6:50 (70 s).
SAY: "Same two crews, same hours. Timing work to the tide beats the obvious 'clear it when it looks full' rule in 39 of 40 simulated seasons. Against today's fixed schedule the gain is a couple of percent and could be zero."
LINE TO LAND: "Sensors alone don't help; sensors plus tide-aware timing do. And dispatch is not our biggest lever — capture is."
DON'T SAY "we cut plastic" without "in our simulation, against a sensor-threshold rule". Never quote absolute tonnes from the twin.
-->

---

# Evidence 2 · Hardware levers, sensing, records

**Retrofit levers in the twin** <span class="tag">SENSITIVITY</span> (P2 dispatch, relative to today's boom):
- Fail-open fuse alone: {{r:fuse_med}}. It is a **flood-safety** feature, not a capture feature.
- One-way pocket that halves tidal re-floating: {{r:pk5_med}} (interval {{r:pk5_lo}} to {{r:pk5_hi}}); cut to a fifth: {{r:pk2_med}}. These rest on an assumed retention factor that the flume must measure.

**Detector** <span class="tag">BUILT</span>: {{r:det_line}}

**Evidence records** <span class="tag">SYNTHETIC test data</span>: inflated claims caught {{r:mrv_recall}} at {{r:mrv_ff}} false flags (a claimed-vs-sensor ratio check: {{r:mrv_base}}; today's slip check: {{r:mrv_slip}}). Tampering detected: {{r:mrv_tamper}}. Precision is only {{r:mrv_prec5}} when one claim in twenty is fraudulent, so **a flag triggers a review, never an automatic penalty**.

<!--
TIME 6:50–7:50 (60 s).
SAY: "The fuse is there so the boom is never the reason a street floods; in the twin it barely changes capture. The one-way pocket is the capture lever we must prove in the flume. The camera is instrumentation, not our novelty. The records system catches most inflated claims in synthetic tests, but at low fraud rates many flags are false, so a flag means a second look, not a penalty."
LINE TO LAND: "We report our weak numbers as plainly as our strong ones."
DON'T SAY "AI detects all plastic". Night, rain, glare and submerged film are real limits; fill from a range sensor is the primary reading.
-->

---

# Built for Mumbai's conditions, priced from real parts

| Challenge | Design answer |
|---|---|
| Tides reverse the flow twice a day | Twin models each site's tide; dispatch uses tide windows; the one-way pocket stops the flood tide lifting the catch |
| Monsoon surges | Fail-open fuse at a set head; the pocket sits outside the fuse path so stored catch stays |
| Salt, silt, hyacinth | HDPE floats, SS316 fittings, node on a pole above the high-water mark (traps already use HDPE and marine-grade aluminium: {{f:F21|Bandalong}}) |
| Monsoon power | Sized for July: {{f:F15|3.79 kWh/m²/day}} vs {{f:F15|7.09}} in May <span class="small">(NASA POWER)</span> |
| Cost | One sensor node: {{f:D04|₹83,481.98}} of priced parts, enclosure included, ≈ {{f:D03|0.8 %}} of one boom; boom O&M runs ≈ {{f:D02|₹1.2 crore}} per site-year (our arithmetic from the FPJ contract) |

<!--
TIME 7:50–8:40 (50 s).
SAY: "Every hardware line is priced from a real Indian retailer page, with the link and the date in our prototype plan. A sensor node costs less than one percent of a boom, and the boom's yearly upkeep is about a crore."
LINE TO LAND: "If NullahNet makes even a sliver of that upkeep better targeted or better verified, it pays for itself."
DON'T SAY a payback period as fact. It depends on the effect size, which the pilot must measure.
-->

---

# Who pays, the pilot we ask for, and the road to December

- **Who pays:** BMC already funds booms and drains (budget {{f:F23|₹80,952.56 crore}} for 2026-27; roads and storm-water drains take more than half). Producers under EPR: Category II covers {{f:F22|"carry bags, plastic sachet or pouches"}}; low-value film can go to cement-kiln co-processing. *Whether drain-recovered plastic earns EPR certificates is not settled in the rules: we treat it as upside.* Verified-kilogram credits already sell (Plastic Fischer).
- **Hook:** BMC's flood plan adds {{f:F24|8 to 10 feet}} mesh screens and water-level sensors at {{f:F24|seven}} pilot sites. NullahNet is the measurement and dispatch layer for exactly such assets.
- **Pilot ask:** 2–3 small outfalls in one ward (one gated, one open), away from the Interceptor sites.
- **Roadmap:** Oct, reversed-flow flume + fuse tests → Nov, edge node on the flume (before exams) → 1 Dec, report + working prototype → Dec, live flume + dashboard demo.

<!--
TIME 8:40–9:15 (35 s).
SAY: "The money exists: BMC already pays for booms and their upkeep. We ask for one ward and three outfalls to prove it."
LINE TO LAND: "Two Interceptors cover two creeks. Give us three small outfalls, and we'll show the city's booms can be measured, timed and trusted."
RESERVE 45 s for overrun.
-->

---

# Backup · The dashboard <span class="tag">BUILT</span> · values <span class="tag">SIMULATED</span>

![h:400](../components/dashboard/screenshot-desktop.jpg)

<span class="small">Real rain (ERA5) and tide (harmonic fit) with provenance badges; boom fill and escape hatched SIMULATED; Marathi and Hindi labels; runs offline.</span>

<!--
Use if asked "show us the software". Walk: map → a site → rain + tide → fill and escape (SIMULATED) → tomorrow's plan → ledger tab with signature check → tamper demo.
-->

---

# Backup · How the twin works and what it leaves out

- **Inputs (real):** hourly ERA5 rain; JMA day-ahead forecasts as archived; tide = UTide fit to Open-Meteo Marine sea level (RMSE {{r:tide_rmse_mithi}} m, {{r:tide_var_mithi}} of variance at the Mithi).
- **Process (assumed):** litter stock builds between storms and washes off with rain; boom capture falls with flow speed; pocket overflows; the flood tide re-floats part of the catch; crews clear.
- **Every assumed parameter** is drawn across a range in {{r:n_draws}} Monte Carlo draws; tuning used 2019–2023 only; 2024–25 were held out.
- **Circularity:** escaped kilograms are computed by the same assumed model the policies act on. Results rank options *under stated assumptions*; field calibration (tagged-item releases at real outfalls) is the Round-2 plan.
- **Not modelled yet:** flap-gated outfalls, travel time between sites, minimum clearance duration, a perfect-foresight upper bound.

<!-- Use for "your results are simulated". Parameter table with sources: research/components/twin.md. -->

---

# Backup · Limits we state up front

| Claim we do **not** make | Why |
|---|---|
| Tonnes diverted per year | The twin's absolute kilograms rest on assumed load and capture curves |
| The one-way pocket works | Its effect is a SENSITIVITY until the reversed-flow flume measures retention |
| The camera counts all plastic | Night, rain, glare and submerged film; fill from the range sensor is the primary reading |
| Records stop fraud | Hashes make edits detectable; they cannot make inputs true; flags trigger review |
| Drain plastic earns EPR certificates | Not found in the rules; upside only |

<!-- Use for any "too good to be true" question. -->

---

# Backup · Sources

- The Ocean Cleanup, press releases, 10 Feb and 30 Apr 2026 · Lokmat Times (2026) · Plastic Bank river pages (Meijer et al. 2021)
- Hindustan Times: trash booms (May 2025), beach litter (2023) · Free Press Journal, 30 Jul 2026 · Mumbai Live (2026) · The Hindu, 7 May 2025 · Citizen Matters
- ITOPF TIP 3 (booms) · NASA POWER climatology · Bandalong / Storm Water Systems · Break Free From Plastic (2023)
- PWM Rules 2016 as amended (UNEP LEAP text) · OpenCity on the BMC budget 2026-27 · Pinwheel (Plastic Fischer)
- Every number with URL, quote and who opened it: `research/fact-check.md`. Every result with its reproduce command: `eval/RESULTS.md`.

<!-- Point judges to the repo files if they ask for evidence. -->
