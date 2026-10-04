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
### Retrofit Mumbai's nullah trash booms: time clearance to the tide, test a boom that keeps its catch, and pay on evidenced kilograms

**Team:** ‹TEAM NAME› · **Team ID:** ‹ID› · **Theme 3:** Rising plastic pollution in coastal cities
‹Member 1 — role› · ‹Member 2 — role› · ‹Member 3 — role› · ‹Member 4 — role› · ‹email / phone›

<span class="tag">BUILT</span> software we ran · <span class="tag">SIMULATED</span> digital-twin output · <span class="tag">SYNTHETIC</span> generated test data · <span class="tag">SENSITIVITY</span> assumption-driven · <span class="tag">PLANNED</span> not built yet

<!--
TIME 0:00–0:25 (25 s). LOGISTICS: present zonal-deck.pdf from your own laptop; the dashboard open in a second tab (bash deliverables/serve_dashboard.sh, then http://localhost:8765); it runs offline except the map tiles.
SAY: "We're ‹team›. We picked one leak: floating single-use packaging escaping through Mumbai's storm-water outfalls. Mumbai already runs trash booms. We propose to make them measurable and better timed, and to test a retrofit that keeps more of what they catch."
LINE TO LAND: "Not another barrier: a way to make the city's existing barriers accountable."
DON'T SAY "we built a prototype". The software is built; the hardware is PLANNED.
-->

---

# The leak, and the plastic we target

| What | Value | Source |
|---|---|---|
| Plastic released to the sea by the metropolitan region | {{f:F01|an estimated 5 million kg a year}} | The Ocean Cleanup survey, 10 Feb 2026 (an estimate) |
| Main pathways | {{f:F04|"around 50 drains and nullahs"}} | Lokmat Times (2026), reporting the same study |
| What one wet spell brings back | BMC removed {{f:F07|2,498.66 t}} from {{f:F07|seven beaches in 11 days}}; BMC said the rain washed refuse "from drains and natural waterways into the Arabian Sea" and "high tides then carried the waste back" | Mumbai Live, Jul 2026 |
| What the litter is | Plastic was {{f:F09|75.5 %}} of {{f:F09|52,770}} beach litter items (Juhu, Aksa) | ICAR-CIFE study via HT, 2023 |

**Our source:** floating single-use *flexible* packaging (carry bags, films, multilayer sachets). It has almost no resale value: waste-picker groups report it is disregarded and sometimes given to cement kilns for free <span class="small">(Break Free From Plastic, 2023)</span>. It is light, so storms flush it into the nullahs.

<!--
TIME 0:25–1:25 (60 s).
SAY: "The 5-million-kilogram figure in the problem statement is The Ocean Cleanup's 2026 estimate for the region. BMC itself describes the cycle: July rain washed refuse from drains into the sea, and high tides carried it back onto the beaches. Most beach litter is plastic. We target the film and sachets that nobody is paid to collect."
LINE TO LAND: "We target the plastic nobody is paid to collect."
DON'T SAY the tonnage was measured. It is a survey estimate. DON'T SAY "pickers never collect film"; the source says it is disregarded and low-value.
-->

---

# NullahNet in one picture <span class="tag">CONCEPT · PLANNED</span>

![w:860](figures/fig_retrofit_concept.png)

<span class="small">**Every morning:** the ward engineer sees each boom's fill and tomorrow's tide and rain, and gets a clearance plan. **Crews** clear in safe tide windows. **Each clearance** produces a signed record (before/after photos, weighbridge slip, GPS) that is checked against the sensors. **The retrofit** (angle, one-way pocket, fail-open section) is a design to test, not a proven device.</span>

<!--
TIME 1:25–2:30 (65 s).
SAY: "Here is the whole idea on one drawing. Today's boom sits square across the nullah. We would angle it, lead the catch into a bank-side pocket with one-way flaps, and put a hinged section in the middle that is meant to swing open before the boom backs water up. A camera watches the pocket; an ultrasonic sensor watches the water level. In the morning, the engineer gets a plan; after each clearance, a signed record."
LINE TO LAND: "One operator decision changes: when the crew goes, and what proves what they removed."
DON'T SAY the release "can't fail" or that the pocket "keeps everything". The opening head, delay, fouling and retention during release are exactly what we test.
-->

---

# Mumbai already intercepts. Our gap is a hypothesis to test.

| Who | What they do | Scale (source) |
|---|---|---|
| **BMC** | Steel-net booms with conveyors at nullah mouths, since {{f:F13|July 2022}} on NGT directions; cleared daily by contractors | A May 2025 report: {{f:F12|9}} booms, expanding to {{f:F12|23}}, about {{f:F12|₹1 crore}} each, {{f:F12|1.5 t/day}} dry and {{f:F12|2.5–3 t/day}} monsoon per boom (HT; current count UNVERIFIED). Operations and maintenance: {{f:F13|₹14.5 crore}} for two years across six rivers and nullahs (FPJ, Jul 2026) |
| **The Ocean Cleanup + Plastic Fischer** | Interceptors at Malad and Trombay creeks (MCGM permits, MPCB MoU) | {{f:F02|61 to 92 tonnes}} a year expected from the first systems, ≈ {{f:D01|1.2–1.8 %}} of the estimate |
| **Plastic Fischer** | TrashBooms, including one at Usha Nagar, Bhandup; kilograms verified by third-party software | {{f:F16|3.2 million kg}} across {{f:F16|8}} sites in India and Indonesia |

**What we propose to test:** we found no public evidence that BMC's booms report their fill or are cleared by tide and forecast. Our hypothesis is that adding both, plus records checked against sensors, improves this existing workflow. Context, not proof of any contractor's conduct: in the Mithi desilting case, a police SIT's FIR alleges a loss to BMC of more than {{f:F11|₹65.54 crore}} (under investigation; The Hindu, May 2025).

<!--
TIME 2:30–3:25 (55 s).
SAY: "This is not an empty field. BMC has booms and a maintenance contract; The Ocean Cleanup is coming to Malad and Trombay; Plastic Fischer already runs booms and verifies kilograms. What we couldn't find in public is fill sensing or tide-timed clearance at BMC's booms. That's our hypothesis to test with BMC, not a claim that nobody does it."
LINE TO LAND: "We build on the city's booms and their verification norms; we don't compete with them."
DON'T SAY "the booms have no sensors" or "nobody does this". Say "we found no public evidence". DON'T SAY anything about guilt in the Mithi case.
-->

---

# Why booms leak, according to our twin <span class="tag">SIMULATED</span>

![bg right:48% fit](figures/fig_escape_split.png)

<style scoped>section { font-size: 20px; }</style>

Digital twin of four Mumbai outfalls: real rain, archived forecasts, fitted tide; assumed plastic and boom behaviour; held-out monsoons 2024–25; {{r:n_draws}} sampled parameter settings.
- **Assumed capture losses dominate:** {{r:ent_esc}} of escaped plastic passes under or through the boom (central 90% scenario range {{r:ent_esc_lo}}–{{r:ent_esc_hi}}). This includes a loss the model assumes even in still water.
- Overflow of a full pocket: {{r:over_esc}} · flood release: {{r:byp_esc}}
- Oil-spill boom guidance (an analogy, not a plastic threshold): booms lose their catch above about {{f:F14|0.35 m/s}} across the boom, irrespective of skirt depth

**So we test capture first:** boom angle and pocket retention, in a tow tank, before anything else.

<!--
TIME 3:25–4:20 (55 s).
SAY: "In our model, most plastic escapes by slipping under or through the boom, not by overflowing a full pocket. But that pattern comes from the capture curve we assumed, informed by oil-boom practice. It tells us what to test first: angle and retention."
LINE TO LAND: "The twin tells us where to look; the tow tank must tell us whether it's true."
DON'T SAY "booms fail because they're square to the flow" as a finding. It is a hypothesis built into the model.
-->

---

# Evidence 1 · Timing the crews <span class="tag">SIMULATED</span>

<style scoped>section { font-size: 20px; }</style>

![bg right:50% fit](figures/fig_levers.png)

Held-out monsoons 2024–25; equal crew-hours ({{r:crew_budget}}); paired over {{r:n_draws}} sampled parameter settings of one model.
- **The full policy** (rank booms by kilograms at risk; time crews to tide and forecast) vs **a fill-fraction-ranked fixed-shift rule:** escaped plastic **{{r:p2p1_med}}** (central 90% scenario range {{r:p2p1_lo}} to {{r:p2p1_hi}}); lower in {{r:p2p1_n}} of {{r:n_draws}} settings
- vs **an assumed fixed roster** (not BMC's real schedule): {{r:p2p0_med}} (range {{r:p2p0_lo}} to {{r:p2p0_hi}}), small and uncertain
- Fill-fraction rule vs assumed roster: {{r:p1p0_med}}
- Decisions use only forecasts archived before the fact

<!--
TIME 4:20–5:30 (70 s).
SAY: "Same two crews, same hours, one model with many parameter settings. Our full policy lets less plastic escape than a simple 'clear the fullest boom' rule in 39 of 40 settings. Against a fixed roster, which we assumed rather than observed, the gain is small and could be zero. The comparison bundles three changes (ranking by kilograms, tide timing, forecasts), so we don't credit any one of them alone."
LINE TO LAND: "In our model, a sensor without good timing can make things worse; the combination is what helps."
DON'T SAY "tide timing saves this much" or "39 of 40 seasons". It's 39 of 40 parameter settings of one model, and the gain belongs to the whole policy.
-->

---

# Evidence 2 · Retrofit levers <span class="tag">SENSITIVITY</span>

What-if runs in the same twin (full policy; each row relative to today's boom with the same dispatch):
- **Fail-open section alone:** {{r:fuse_med}}. Its job is flood safety, not capture, and that safety is unproven until we measure opening head, delay and reset.
- **One-way pocket**, assuming it halves the catch lifted out by the flood tide: {{r:pk5_med}} (range {{r:pk5_lo}} to {{r:pk5_hi}}); assuming a fifth: {{r:pk2_med}}.
- The retention factor is an **assumption**; the tow tank must measure it. Rows are separate what-ifs: don't add them up.

<!--
TIME 5:30–6:25 (55 s).
SAY: "These are what-ifs, not evidence. The fail-open section barely changes capture in the model; it's there for flood safety, which we still have to measure. A one-way pocket matters only if it really holds its catch when the tide reverses, and that is the first thing our tow tank measures."
LINE TO LAND: "We only claim what the tow tank shows."
DON'T SAY the pocket "cuts escape" as a fact. Say "if it retains half, the model says {{r:pk5_med}}".
-->

---

# Evidence 3 · Sensing and records

**Detector** <span class="tag">BUILT</span>: {{r:det_line}} Public river-litter images are not Mumbai nullah film; we treat detection as an aid, not proof.

**What measures fill:** the camera sees the mat area in the pocket; an ultrasonic sensor over open water gives water level. If the camera is degraded (night, rain, glare), fill is reported **unknown** and crews follow the roster.

**Evidence records** <span class="tag">SYNTHETIC test data</span>: across our synthetic fraud mixture (inflated, phantom and wetted claims), {{r:mrv_recall}} caught at {{r:mrv_ff}} false flags. Inflated claims alone: {{r:mrv_infl}}; small inflations only {{r:mrv_small}}. If debris is a quarter denser than assumed, honest false flags rise to {{r:mrv_dens125}}, so density must be calibrated per site. Tampering is caught {{r:mrv_trunc_anchor}} only with an external anchor; the chain alone misses tail truncation ({{r:mrv_trunc_chain}}). A flag triggers **review, never automatic penalty**.

<!--
TIME 6:25–7:25 (60 s).
SAY: "The camera is an aid; when it can't see, we say so and fall back to the roster. The records system catches most inflated claims in synthetic tests, misses small ones, and its false flags depend on knowing the debris density, so a flag means a second look, never a penalty."
LINE TO LAND: "We report our weak numbers as plainly as our strong ones."
DON'T SAY "AI detects all plastic" or "tamper-proof". Hashes make edits detectable; they cannot make inputs true.
-->

---

# Built for Mumbai's conditions, priced from real parts

| Challenge | Design answer (status) |
|---|---|
| Tides reverse the flow twice a day | Twin models each site's tide; dispatch uses tide windows (BUILT); one-way pocket to keep the catch on the flood tide (PLANNED, test T2) |
| Monsoon surges | Fail-open section intended to limit extra head rise within a tested flow and blockage envelope (PLANNED, test T3) |
| Salt, silt, hyacinth | HDPE floats, SS316 fittings, node on a pole above the high-water mark; floating traps already use HDPE and marine aluminium ({{f:F21|Bandalong}}) |
| Monsoon power | Sized for July: {{f:F15|3.79 kWh/m²/day}} vs {{f:F15|7.09}} in May (NASA POWER); the load is an assumption until bench-measured |
| Cost (listed parts only) | Sensor node {{f:D04|₹83,481.98}}, enclosure included, ≈ {{f:D03|0.8 %}} of one boom's reported price. Excludes installation, anchoring, the retrofit itself, connectivity and servicing |

<!--
TIME 7:25–8:20 (55 s).
SAY: "Every hardware line is priced from a real Indian retailer page, with link and date in the prototype plan. That's listed parts, not an installed cost; installation, anchoring and servicing come on top. Even so, a sensor node is under one percent of a boom's reported price."
LINE TO LAND: "Small add-on, large existing asset."
DON'T SAY it "pays for itself"; the effect size is unmeasured. DON'T divide the maintenance contract per boom; we don't have its asset list.
-->

---

# What we will deliver, the pilot we ask for, who pays

- **By 1 Dec (committed):** a closed-loop rig, with no field permissions needed. A tow-tank boom model (straight, angled, pocket, fail-open) + the sensor node + the twin + signed records, with measured retention, head rise and fill error.
- **Field pilot (conditional on permission, safety and a site survey):** one existing open-tidal BMC boom first, e.g. the ML Complex nullah, Dahisar, which a 2025 report says catches the most ({{f:F12|highest volume}}). It is unsurveyed and uncontacted, and its gate status is UNVERIFIED. Gated outfalls come later.
- **Who pays:** the existing boom maintenance budget ({{f:F13|₹14.5 crore}} for two years); EPR is upside (Category II covers {{f:F22|"carry bags, plastic sachet or pouches"}}, but drain-plastic eligibility is not settled); verified-kilogram credits already sell (Plastic Fischer).
- **Hook:** BMC's proposed {{f:F24|₹13,000 crore}} flood plan adds {{f:F24|8 to 10 feet}} mesh screens and expands water-level sensors beyond {{f:F24|seven}} pilot sites. Compatibility with those works is UNVERIFIED.

<!--
TIME 8:20–9:15 (55 s).
SAY: "By December we commit to a working closed loop on the bench: tow tank, sensor node, twin and records. With permission, our first field site would be one existing BMC boom. We ask for one site survey and one conversation with the storm-water drain department."
LINE TO LAND: "Give us one existing boom to measure, and we'll show whether timing, a better pocket and honest records move the numbers."
RESERVE 45 s for overrun.
-->

---

# Backup · The dashboard <span class="tag">BUILT</span> · values <span class="tag">SIMULATED</span>

![h:400](../components/dashboard/screenshot-desktop.jpg)

<span class="small">Real rain (ERA5) and tide (harmonic fit) with provenance badges; boom fill and escape hatched SIMULATED; Marathi and Hindi labels; runs offline except map tiles.</span>

<!--
Use if asked "show us the software". Walk: map → a site → rain + tide → fill and escape (SIMULATED) → tomorrow's plan → ledger tab with signature check → tamper demo.
-->

---

# Backup · How the twin works and what it leaves out

- **Inputs (real):** hourly ERA5 rain; JMA day-ahead forecasts as archived (the value issued 24 h before); tide from a UTide fit to Open-Meteo Marine model sea level. Fit RMSE {{r:tide_rmse_mithi}} m at the Mithi is an in-sample residual against model data (fit window through Sep 2025), not gauge validation.
- **Process (assumed):** litter builds between storms and washes off with rain; capture falls with flow speed; pockets overflow; the flood tide lifts part of the catch; crews clear.
- **Uncertainty:** the main process parameters are drawn across ranges in {{r:n_draws}} settings; site geometry, crew rules and some structures are fixed. Policy tuning used 2019–2023 only.
- **Circularity:** escaped kilograms come from the same assumed model the policies act on. Results guide experiments; they are not field evidence.
- **Not modelled yet:** flap-gated outfalls, travel time between sites, minimum clearance duration, a perfect-foresight upper bound.

<!-- Use for "your results are simulated". Parameter table with sources: research/components/twin.md. -->

---

# Backup · Limits we state up front

| Claim we do **not** make | Why |
|---|---|
| Tonnes diverted per year | The twin's absolute kilograms rest on assumed load and capture curves |
| The pocket keeps its catch | A SENSITIVITY until the tow tank measures retention under reversal |
| The boom cannot raise flood levels | The fail-open section's opening head, delay, fouling and reset are untested |
| The camera counts all plastic | Night, rain, glare and submerged film; fill is "unknown" when the camera is degraded |
| Item counts are accurate | On SYNTHETIC drifting-item video, the line-crossing counter over-counts by {{r:flux_err}}% (cause not yet diagnosed); counts are not used for kilograms |
| Records stop fraud | Hashes make edits detectable; they cannot make inputs true; flags trigger review |
| Drain plastic earns EPR certificates | Not found in the rules; upside only |

<!-- Use for any "too good to be true" question. -->

---

# Backup · More Mumbai context

- An independent global model ranks Malad Creek #30 of {{f:F05|31,819}} modelled outfalls ({{f:F05|2,724 t/yr}}, modelled, not measured; Meijer et al. 2021)
- A historical BRIMSTOWAD summary lists {{f:F06|186 outfalls}}, with legacy drains built for {{f:F06|about 25 mm/h of rain at low tide}}; BMC's 2026 plan says drains handle about {{f:F24|50 mm}} per hour today, aiming at {{f:F24|100–120 mm per hour}}
- The 2018 plastic ban is weakly enforced: in 2024 BMC acted against {{f:F10|44,448}} establishments and confiscated {{f:F10|2,148 kg}}
- An older BMC estimate: {{f:F08|500 t/day}} of waste goes uncollected and "ends up in the storm water drains"

<!-- Use for "how well do you know Mumbai?" -->

---

# Backup · Sources

- The Ocean Cleanup, press releases, 10 Feb and 30 Apr 2026 · Lokmat Times (2026) · Plastic Bank river pages (Meijer et al. 2021)
- Hindustan Times: trash booms (May 2025), beach litter (2023) · Free Press Journal, 30 Jul 2026 · Mumbai Live (2026) · The Hindu, 7 May 2025 · Citizen Matters
- ITOPF TIP 3 (booms) · NASA POWER climatology · Bandalong / Storm Water Systems · Break Free From Plastic (2023) · Ohmsett (TEAMER)
- PWM Rules 2016 as amended (UNEP LEAP text) · Pinwheel (Plastic Fischer)
- Every number with URL, quote and who opened it: `research/fact-check.md`. Every result with its reproduce command: `eval/RESULTS.md`.

<!-- Point judges to the repo files if they ask for evidence. -->
