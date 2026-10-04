# ADR 001 — Spike components

- **Status:** accepted (v1, 4 Oct 2026 05:45 IST; update 06:15 below). Revisit at the selection gate (7 Oct) and after the first flume test.
- **Deciders:** project lead, with an independent adversarial review ([antithesis](../../research/reviews/adr001-antithesis.md), rubber-duck agent) and a [first-principles review](../../research/reviews/adr001-first-principles.md) (First Principles agent), both run 05:15–05:55 IST and stored verbatim.
- **Context:** [components.md](../components.md) · [thought node](../../thought_node.md). Facts marked **[V]** are leads still being verified by the research sessions. Do not quote them in a pitch until they carry a citation in `research/`.

## Context
The theme asks us to monitor, intercept and reduce plastic leaking from Mumbai's nullahs (stormwater drains) and creeks, for one specific source. Judges score novelty, robustness under tides, monsoon and corrosion, cost, feasibility, scalability, quantified impact and design. Bonus points go to Mumbai-specific insight. BMC already runs trash booms and manual clearance on nullahs and the Mithi **[V]**. So "put a boom in the river" is not novel.

**Working source (narrowed after review):** floating single-use *flexible* packaging (carry bags, films, multilayer sachets) from market and dense-settlement catchments. It enters nullahs and leaks at tidal outfalls into Mahim, Malad and Mahul creeks. Bottles and thermocol are caught incidentally and are not designed for.

## First principles (summary of the review)
- The leak is a **stock that builds and flushes**. Dry-season dumping builds a stock in drains. The first monsoon storms flush it.
- `kg_to_sea = Σ_events A_e · (1 − η_capture(u, h) · η_retain(V, tide, release))`.
- **Binding constraint 1 (physics):** plastic flux peaks exactly when barriers fail. High velocity drags plastic under the skirt. Flexible films get mixed into the water column. Pockets overflow. Flood-safety rules force booms open. So capture weighted by plastic flow is far below capture averaged over time.
- **Binding constraint 2 (institutions):** money follows *claimed wet tonnes removed*, not *kg prevented*. Mumbai's 2025 police probe into Mithi desilting quantities **[V]** shows how weak the verification is.
- **Single most useful reading per outfall:** pocket fill %. Its trend gives time to overflow. The same camera also sees water level, flow direction and before/after clearance.
- **North-star number:** *flux-weighted capture efficiency* (FWCE) = verified kg captured and retained ÷ kg arriving, over a monsoon. It turns "removed" into "prevented" and caps what any outfall intervention can claim.
- **Tide depends on site type.** Behind tide-locked flap gates the water is near-still and debris concentrates: the best window to capture and clear. At open tidal outfalls the flood tide re-floats debris **[V]**.

## Candidates
| | Candidate | Component(s) |
|---|---|---|
| A | Forecast- and tide-aware clearance dispatch driven by pocket-fill sensing (clear before forecast surges; use gate-closed / low-velocity windows; prioritise by predicted overflow) | C9 + C10 |
| B | Signed, hash-chained evidence records reconciling claimed kg against sensor evidence; pay per verified kg; EPR routing | C11 (+ C13) |
| C | Camera-based plastic flux and fill sensing (YOLO-class detector, tracking, line-crossing) | C5 + C6 + C7 |
| D | **Ratchet pocket + fail-open fuse** retrofit for existing booms: a one-way pocket that keeps the catch when the tide reverses, and a hinged release that opens at a set head so the barrier never raises upstream water level | new hardware component H1, modelled by C4 |
| E | Ward-level source attribution for targeted collection and enforcement | C14 |

## Six Thinking Hats
- **White (facts):** booms exist in Mumbai **[V]**. The barrier physics is known: skirt entrainment at roughly 0.35–0.5 m/s normal velocity (oil-boom experience **[V]**). A trash-trap with a one-way flap that rises and falls with the water is prior art (Bandalong Litter Trap **[V]**). Free real data we can use tonight: ERA5 rain, archived forecasts, tide. No public imagery of Mumbai nullahs exists, so detector metrics come from a proxy dataset.
- **Red (gut, judges):** a physical model in a reversible-flow flume with water rising, a gate flipping and trash staying put will be remembered. A dashboard alone will not. A credible Mumbai story (gates, high-tide days, Mithi, desilting probe) wins the bonus.
- **Black (risks):** A can be circular, because the twin computes escaped kg from the same assumptions the policy exploits. Fixed-schedule baselines are straw men, and ERA5 gives hindsight. B is detecting fraud we invented ourselves. Pay-per-kg rewards wet loads and importing waste. "Blockchain" framing invites ridicule, and hashes do not make inputs true. C is commoditised YOLO: blind at night, in rain and to submerged films, and count→kg is unreliable. D has prior art (one-way flap traps), the flaps foul with hyacinth, rags and barnacles, and the fuse opens at peaks by design. Its benefit exists only at ungated sites. E is weak where wards ≠ drainage catchments.
- **Yellow (benefits):** A is cheap, needs no new hardware, and gives a ratchetable scalar tonight. D is visible, central to *interception*, and testable cheaply (gutter flume, pump, phone video). C supplies the measurements that make A, B and D calibratable. B makes the money flow honest and unlocks EPR / recycler revenue.
- **Green (alternatives):** prioritise pre-monsoon stock removal along nullah banks. Put full-depth screens at pumping stations, where velocity is controlled **[V]**. Release tagged items to measure escape. Calibrate fill from a painted depth gauge in the camera view.
- **Blue (process):** choose by the scores below. Require each spike to have a scalar metric and an honest validation path. Re-decide at the 7 Oct gate with the flume and twin numbers.

## Thesis → antithesis → synthesis
- **Thesis (lead, 05:10):** spikes A + B (both software, measurable tonight in the twin and on synthetic records).
- **Antithesis (independent rubber-duck):** A and B fit the team's skills but leave the central risk untouched: *intercepting without worsening flooding*. The twin may manufacture its own success, and the MRV metric rewards detecting fraud we invented ourselves. The reviewer proposes D as the primary spike, with C as instrumentation, A as a later rule layer and B reduced to plain signed records. It also says to narrow the source to flexible film.
- **First principles:** the leverage is measurement, timing and verification. Hardware only pays at a few big sites, and D's upside is limited to ungated sites. The number to prove is FWCE.
- **Synthesis (decision):**
  1. **Spike 1 — C10/C9 forecast- and tide-gate-aware dispatch (software, now).** Hardened against the antithesis:
     - archived real forecasts, not ERA5 hindsight;
     - P1 fill-threshold as the strong baseline and a perfect-foresight oracle as the upper bound, with gains reported as a share of the oracle gap;
     - Monte Carlo over every ASSUMPTION;
     - held-out monsoons (2024–25) never used in the ratchet;
     - claims stated as *relative, conditional on the process model*, with a Round-2 field-calibration protocol.

     Metric: escaped kg on held-out monsoons at equal crew-hours. Also report FWCE.
  2. **Spike 2 — H1 ratchet pocket + fail-open fuse (hardware, Round 2; design + flume tests from now).** We do not claim the one-way flap is novel. The claim is a *retrofit for tidal outfalls*: one-way retention under flow reversal, a calibrated fail-open threshold with a measured head-rise envelope, and an instrumented pocket (fill camera). Metric (flume): retained fraction after N flow reversals, subject to upstream head rise ≤ a set cap at the design flow. Tonight it appears only as a labelled SENSITIVITY in the twin.
  3. **C is best-practice instrumentation**, not a novelty claim. The detector still gets an autoresearch loop (held-out mAP50), because its error bars feed FWCE.
  4. **B is a supporting feature:** signed, hash-chained evidence records with reconciliation. Report precision at realistic prevalence; use no blockchain language.
  5. **E is deferred** to Round 2.

## Scores (1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by deadline | Measurable (scalar) | Demoable | Total |
|---|---|---|---|---|---|---|
| A dispatch | 4 | 3 | 5 | 4 | 4 | **20** |
| D ratchet + fuse | 5 | 3 | 3 | 4 | 5 | **20** |
| C flux/fill sensing | 3 | 2 | 4 | 5 | 4 | 18 |
| B evidence records | 3 | 2 | 5 | 3 | 3 | 16 |
| E attribution | 2 | 3 | 3 | 2 | 3 | 13 |

## Consequences
- The twin owns Spike 1 and its ratchet. The detection session owns C's ratchet. The lead adds H1 to the component map and the prototype plan, including the flume protocol.
- **Needs from user (before 10 Oct, optional but high-value):** a 1–2 hour tabletop flume test (PVC gutter or clear box, small pump, film samples, phone video). It compares a straight boom, an angled boom and the ratchet pocket under forward and reversed flow, and does one deliberate-jam fuse test. A ~₹3–5k estimate is **UNVERIFIED** until the BOM research lands.
- **Cheapest risk-reducers:**
  - Before 10 Oct: the reversible-flow flume; the deliberate-jam fuse test; a blinded fill-alert test (glare, dark, spray).
  - Round 2: a tagged-item release at 1–3 real outfalls to measure FWCE, and a load–duration curve per outfall. Does most plastic arrive below the boom-failure velocity? If not, move money to pre-monsoon stock removal and nullah-bank collection.
- **Kill criteria:**
  - Spike 1: drop it if P2 does not beat P1 by more than the Monte Carlo spread on held-out years.
  - Spike 2: drop the "ratchet" claim if reversed-flow flume tests show no retention gain over an angled boom, or if the fuse cannot keep head rise under the cap.

## Update 17:53 IST — numbers after the leak-free tide refit (supersede the 16:25 and 17:10 figures; SIMULATED / SENSITIVITY)
The code review (gpt-6-sol #2) found the tide fit used sea level from the held-out years. The twin child refitted the tide on 2022-11-23 to 2023-12-31 only (Mithi out-of-sample RMSE 0.09 m on 2024–25 model sea level, not a gauge) and re-ran `run.py` and `analysis.py` with nothing retuned (481f0d1). Every decision below is unchanged.
- **Paired, held-out 2024–25, 40 parameter draws:**
  - P2 vs P1: −5.2% (central 90% scenario range −15.9% to −0.8%), lower in 39 of 40.
  - P2 vs P0: −1.9% (−12.5% to +1.3%).
  - P1 vs P0: +3.0% (−0.1% to +5.7%).
- **Ablations:** tide timing alone −3.6% (−15.1% to +0.5%); forecasts −0.7%; kg ranking −2.1% (−4.0% to +0.2%); P2 vs the kg-ranked rule −2.8% (−12.5% to +0.9%). None clears zero alone.
- **Escape split (P2):**
  - Under or through the boom: 93.1% of escaped. Of all escape, 51% is the assumed still-water leak and 40% is speed-driven.
  - Overflow: 5.5%. Release: 0.5%.
  - 14.1% of arriving plastic comes at high speed.
- **Hardware SENSITIVITY:**
  - Fuse alone −0.1%.
  - Pocket ×0.5 −5.1% (−9.6% to −1.5%); pocket ×0.2 −9.3%.
  - Angle 45° −10.5%, 30° −15.3%, 20° −17.8% (2.9× channel width); 20° + fuse + pocket −23.9%.
- **FWCE:** P0 45.8%, P1 44.4%, P2 49.0%.

All four deck statements still hold: (a) the full policy vs the fill-fraction rule clears zero; (b) no single ingredient does; (c) P2 vs P0 crosses zero; (d) escape under or through the boom dominates. Source: [`analysis.json`](../../components/twin_sim/results/analysis.json); the deck renders these from it.

## Update 17:10 IST — ablations, the twin's leak decomposition, hostile review (SIMULATED / SENSITIVITY; numbers superseded by the 17:53 update)
Sources: [`analysis.json`](../../components/twin_sim/results/analysis.json) (reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`); [hostile review](../../reviews/2026-10-04-final-deck-gpt-6-astra.md); [lead response](../../reviews/2026-10-04-final-deck-lead-response.md).

**Dispatch ablations (held-out 2024–25, paired):**
- tide timing alone −3.2% (central 90% scenario range −12.0% to +0.6%);
- forecasts alone −0.4%;
- ranking by kg alone −2.0%.

None clears zero alone. Only the full policy vs the fill-fraction rule does (−5.6%). Spike 1 is therefore claimed only as a *combined* policy in one model, and a cheap kg-ranked sensor rule is the first field comparator.

**What "escape under the boom" is made of:**
- 51% of all escape is the (1 − e_max) still-water leak we *assumed*;
- 38% is speed-driven;
- only 13.2% of arriving plastic comes at speeds above the capture curve's midpoint.

The largest modelled loss is therefore an assumption. **The first tow-tank measurement is a real boom's still-water leak (T1), then capture vs speed (T6).**

**Boom angle (SENSITIVITY, a consequence of the assumed curve, not a confirmation):**
- 45°: −10.4%;
- 30°: −15.0%;
- 20°: −17.2%. A 20° boom is about 2.9× the channel width, which may not fit narrow nullahs.

**FWCE definition (fixes an inconsistency the reviewer found).** Use the analysis's definition everywhere: (cleared + stored at season end) ÷ *unique* catchment load, with re-arrivals of re-floated debris excluded. Stored material is temporary retention, not final diversion. The first-principles section above used "kg arriving"; that denominator double-counts re-arrivals and is superseded.

**Reviewer verdict:** NOT READY unchanged (1 blocker, 11 major, 4 minor); agrees T3 should not replace T1. All 16 items were addressed (15 accepted, 1 partly); see the lead response. The spike framing stands, but the pitch now presents every hardware lever as a test to run, not a result.

## Update 08:00 IST — prior art for Spike 2 (lead check)
Passive floating litter traps for tidal waterways already exist. The Bandalong Litter Trap is a floating device that collects and retains floating litter and is "suitable for most waterways wider than 2 metres, including waterways subject to tidal action" (bandalong.com.au). It is built from HDPE and marine-grade aluminium and adapts to water-level changes (stormwatersystems.com); both pages were opened 2026-10-04. A one-way flap mechanism is described only by a search summary, so it is UNVERIFIED.

**Consequences.**
- The "ratchet pocket" is not novel as a concept.
- Spike 2's claim narrows to a **fail-open fuse retrofit** for Mumbai's existing steel-net conveyor booms, plus an **instrumented pocket** that feeds dispatch and evidence.
- The flume must still show a retention gain under reversal; otherwise we adopt an off-the-shelf trap design and drop the retention claim.

## Update 16:25 IST — escape split, paired comparisons, fuse/pocket sensitivity (SIMULATED; numbers superseded by the 17:53 update)
Source: [`components/twin_sim/results/analysis.json`](../../components/twin_sim/results/analysis.json). Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`. Same held-out years, draws, seed and crew budget as before; nothing retuned.

**Findings:**
- **Why plastic escapes (P2).** The twin's capture curve is an ASSUMPTION.
  - Under or through the boom: 92.5% of escaped (interval 64.6–100%). This includes the (1 − e_max) floor that leaks even at slack water.
  - Overflow: 5.9%.
  - Flood release: 0.7%.
- **Paired, same draws.**
  - P2 vs P1: −5.6% escaped (interval −15.8% to −0.3%). P2 is better in 39 of 40 draws.
  - P2 vs P0: −2.1% (−12.5% to +1.5%).
  - P1 vs P0: +3.1%.
  - Reading: tide-aware timing robustly beats the sensor-only "clear when full" rule. Against today's schedule its gain is small and uncertain.
- **Fail-open fuse alone: −0.1%.** Release is rare on the ERA5 rain scale, so the fuse is a **flood-safety feature, not a capture lever**.
- **One-way pocket (SENSITIVITY).** Re-float ×0.5 gives −5.0% (−9.9% to −1.4%; 40/40 draws). Re-float ×0.2 gives −9.4%.

**Decision.**
- Spike 2 is now framed as:
  - **capture geometry**: boom angle (sensitivity requested; tow-tank test T6);
  - the **one-way pocket**: retention, flume test T2;
  - the fuse, for safety.
- The deck says plainly that dispatch is a supporting lever.
- Kill criteria are unchanged:
  - drop the retention claim if T2 shows no gain over an angled boom;
  - drop dispatch as a selling point if field calibration erases the P2-vs-P1 gap.
- **Prototype method changed** from a pumped flume to a **tow tank**. Pumping 0.3–0.6 m/s even through a small channel needs thousands of litres per hour, while towing gives exact speed and free reversal. Ohmsett tests booms this way (fact F28).

## Update 07:15 IST — first twin result: timing alone is a small lever (SIMULATED)
Source: [`components/twin_sim/results/metrics.json`](../../components/twin_sim/results/metrics.json). Reproduce with `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run`.

**Setup.**
- 4 outfall sites; 2 crews × 8 h/day for every policy; 40 Monte Carlo draws over the ASSUMPTION parameters.
- Real forcing: ERA5 rain, archived JMA day-ahead forecasts, and a UTide tide fit to Open-Meteo Marine sea level. The fit has RMSE ≈ 0.08 m at all four sites.
- Held-out monsoons: 2024 and 2025.

**Results (held-out):**
- **P2 (forecast- and tide-aware) vs P0 (fixed schedule):** median **2.1% less escaped plastic**. The 90% interval runs from 1.5% *more* to 12.5% less. P2 is better in 28 of 40 draws. Most of the gain comes from tide-aware timing: removing it worsens the tuning metric by 3.7%, while forecast terms move it ≤0.5%. The held-out evaluation was run twice; the first run had a forecast look-ahead bug in the 48 h horizon, which was fixed by a causal 24 h horizon. Both runs are disclosed in [twin.md](../../research/components/twin.md) §4.
- **P1 (fill threshold) vs P0:** median 3.1% *more* escaped (interval +0.01% to +6.0%). P1 ranks booms by fill % rather than by kg at risk.
- **Captured fraction:** 0.46 (P0) → 0.49 (P2).

**Reading.** Under our process model, dispatch timing moves escape only a few percent. About half the arriving plastic is not captured whatever the schedule. This matches the first-principles review: the binding constraint is capture physics at high flow, not crew timing.

**Decision.**
- Spike 1 stays as a **support layer**, not the headline. Its kill criterion is not yet met: P2 beats P1 by about 5 percentage points at the median, but P2's own interval spans zero. The pitch will say "a few percent, uncertain".
- The headline shifts to **Spike 2**: angled boom + ratchet pocket + fail-open fuse, the capture-physics lever.
- The twin's next job is to quantify how escape splits between entrainment, overflow and bypass, and to run the ratchet SENSITIVITY.
- Re-decide at the 7 Oct gate.

## Update 06:15 IST — The Ocean Cleanup is already in Mumbai (strengthens this decision)
Sources: [mumbai-context.md](../../research/mumbai-context.md), [companies.md](../../research/companies.md).

**The facts:**
- **Origin of the 5,000 t/yr figure.** It comes from The Ocean Cleanup's "Smart Rivers Survey" (press release, Mumbai, 10 Feb 2026). It covers the whole metropolitan region.
- **The brief's "Malad or Trombay" outlets.** These are Malad Creek and Trombay Creek, The Ocean Cleanup's two pilot Interceptor sites:
  - MCGM Storm Water Drain permits and an MPCB MoU (press release, 30 Apr 2026);
  - Plastic Fischer runs operations on the ground;
  - the first systems are expected to recover 61–92 t/yr.
- **Scale.** 61–92 t/yr is about 1.2–1.8% of 5,000 t/yr (derived). Mumbai has 186 storm-water outfalls (BRIMSTOWAD, via a secondary summary — [mumbai-context.md](../../research/mumbai-context.md) S7). A press report on the same survey says the plastic leaks "through around 50 drains and nullahs" (S4).

**Consequences:**
- **(a) Spike 2 must target the long tail of small nullah outfalls**, not the big creek mouths, which are now Interceptor territory. A low-cost retrofit for existing BMC booms fits that.
- **(b) The measurement / dispatch / evidence layer is complementary** to Interceptors and Plastic Fischer's per-kg verification. It is not a competitor. Pitch it as the network layer that makes hundreds of small booms accountable.
- **(c) Never pitch "a barrier at Malad".** That is already being done.
