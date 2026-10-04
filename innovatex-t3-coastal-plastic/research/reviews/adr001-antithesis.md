# ADR 001 review — antithesis (independent adversarial agent)

> Verbatim output of an independent `rubber-duck` agent, run 05:15–05:50 IST on 4 Oct 2026, with no web access. It was given the thesis (spikes A = forecast/tide-aware dispatch, B = hash-chained MRV) and the alternatives C, D and E. Its factual premises are unverified unless the research files cite them. Synthesis: [001-spike.md](../../architecture/adr/001-spike.md).

## Hostile verdict

**A and B look selected because they fit the team's software skills—not because they retire the project's central risk.** The decisive question is whether plastic can be intercepted **without worsening flooding**. Neither spike proves that.

## 1. Strongest case against A and B

### Blocking issues

**A. The digital twin could manufacture its own success.**

- "Escaped kg" will probably be calculated, not observed. If the same assumed relationships—fill level → blockage → overflow → escape—both drive the policy and score it, the result is circular.
- ERA5 is reanalysis, not necessarily what an operator would have known at dispatch time. Using realized rainfall gives the policy hindsight. You need archived forecasts with actual forecast errors.
- Astronomical tide data is not outfall water level. Backwater, surge, local rainfall, gate condition, drain geometry and blockage matter.
- Seven monsoons is a tiny evaluation set, especially with an "autoresearch ratchet" repeatedly optimizing against it. Held-out years can quietly become a validation set.
- A fixed schedule is an easy straw-man. Compare against current operator heuristics, threshold clearance and an oracle upper bound.
- Equal crew-hours ignores travel, access, truck capacity, disposal queues, night work and low-tide-window feasibility.
- Critical calibration data—site geometry, flow, plastic-arrival rates, boom capacity, clearance duration and crew records—may not be obtainable. **Verify access before pitching the twin as empirical.**

**B. The MRV metric rewards detection of fraud you invented.**

- Synthetic inflated claims will reflect the assumptions used to generate them. A detector can achieve impressive recall simply by learning those assumptions.
- "Recall at ≤5% false flags" omits fraud prevalence and precision. At low prevalence, most alerts could still accuse honest contractors.
- A hash chain makes records difficult to alter; it does not make inputs true. Cameras, timestamps, scales and identities can be spoofed or collude.
- Pay-per-verified-kg incentivizes wet loads, soil contamination, duplicate weighing, moving previously collected waste and prioritizing heavy bottles over leakage risk.
- Camera fill cannot reliably infer kilograms without composition, waterlogging and compaction calibration.
- Adoption requires procurement changes, contractor cooperation, chain-of-custody authority, evidence-retention rules and dispute resolution. BMC may see this as an audit/liability system rather than a useful drain intervention.
- Invoking an **unverified** corruption allegation is politically risky and distracts from engineering evidence.

### Non-blocking but damaging

Forecast-aware dispatch is sensible operations research, but not obviously novel. Hash-chained MRV is also familiar and may trigger a "blockchain looking for a problem" reaction.

Your "specific source" is not specific: flexible bags, MLP sachets, thermocol and bottles differ in material, buoyancy, capture behaviour and end-of-life route.

## 2. Where an IIT Bombay judge may break the pitch

Expect questions such as:

- "Show me measured upstream head rise at increasing blockage and flow."
- "What happens at peak rain plus high tide? Does your fuse dump everything into the sea precisely then?"
- "Why does flood tide push waste deeper into the pocket rather than back upstream?"
- "Which exact polymer and catchment are you targeting?"
- "Where did plastic-arrival, outfall-flow and clearance-time data come from?"
- "Did you use archived forecasts or actual rainfall?"
- "How is this better than BMC's existing booms and manual inspection?"
- "Can the camera work with glare, darkness, muddy water, rain, occlusion and biofouling?"
- "Who accepts wet, contaminated flexible film, and at what net cost?"
- "How did one simulated outfall become a Mumbai-wide impact number?"

The pitch collapses if the answer is repeatedly "the twin assumes…" or "we will validate later."

## 3. Better spike choice

Pick **D as the primary spike, with a minimal version of C as test instrumentation and fill alerting**.

Narrow the source to something defensible, such as **floating LDPE carry bags and film from one market-drain catchment**. Drop bottles, thermocol and generic MLP.

Build a modular **ratchet-pocket/fail-open attachment to a conventional angled boom**. Score it on:

1. capture efficiency;
2. re-escape under reversed flow;
3. upstream head rise by flow and blockage;
4. fail-open threshold and recovery;
5. clearance time;
6. coarse camera fill-alert accuracy.

This is visible, central to interception, memorable in a ten-minute pitch and testable cheaply. Use software where it helps measurement; do not make YOLO itself the novelty. Keep A as a later rule-based operational layer and replace B with ordinary signed evidence records.

However, **verify prior art** before claiming novelty. Also be ready to abandon the "tidal ratchet" claim if reversible-flow tests disprove its hydrodynamics.

## 4. Three cheapest risk-reducing experiments

### 1. Reversible-flow tabletop flume
**Before 10 Oct:** PVC gutter/transparent box, pump, phone video and film samples. Compare straight boom, angled boom and ratchet pocket under ebb/flood directions, two flows and partial blockage. Measure capture, re-escape and water-level rise.
**By 1 Dec:** repeat at larger scale with silt, irregular pulses and dimensional-similarity justification.

### 2. Deliberate jam and fuse-abuse test
**Before 10 Oct:** fully block the pocket, ramp flow, record maximum head, opening threshold, released mass and whether it resets. Run repeated cycles.
**By 1 Dec:** add saline soaking, grit, tangled cloth, hinge fouling and 100+ release cycles. Never claim "cannot flood"; specify a measured operating envelope.

### 3. Blinded fill-alert test
**Before 10 Oct:** have one teammate create unseen fill states under glare, darkness, spray and partial occlusion; another scores empty/half/full alerts.
**By 1 Dec:** test outdoors over multiple days and calibrate alerts against dry plastic mass and clearance time—not object counts alone.

All Mumbai quantities, outfall counts, current installations, recycling routes, forecast archives and novelty claims need explicit verification.
