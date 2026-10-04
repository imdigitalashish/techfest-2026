# ADR 001 — Spike components

- **Status:** accepted (v1, 4 Oct 2026 06:00 IST). Revisit at the selection gate (7 Oct) and after the first flume test.
- **Deciders:** project lead, with an independent adversarial review (rubber-duck agent) and a first-principles review (First Principles agent), both run 05:20–05:50 IST.
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
