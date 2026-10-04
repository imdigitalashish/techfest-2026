# ADR 001 — Spike components: recharge-verifier (primary) and ingest-qc (data integrity)

- **Status:** accepted (v1, 4 Oct 2026, lean mode). Revisit at the 7 Oct selection gate.
- **Deciders:** project lead. The adversarial review came from an independent `rubber-duck` agent (antithesis below, condensed faithfully). The first-principles agent did not report before the cut-off; physics checks are the lead's own, with arithmetic shown.

## Context
- The theme lets us pick one specific problem: levels, contamination, illegal extraction, leakage or recharge (`_briefs/innovatex.txt`).
- Delhi governs groundwater through three paper loops (`research/landscape.md` §1):
  1. illegal borewells identified but not traced or sealed (20,297 identified, 15,962 sealed, 4,000+ untraceable — HT, 10 Jun 2025);
  2. RWH rebates paid against self-certification (₹204.46 cr, 2017–24; annual self-certification announced Apr 2026; "there was a rule but no real checking" — HT, 21 Apr 2026);
  3. a public DWLR stream that is 23.3 % exact zeros and 17.4 % missing slots (our run).
- Judges reward novelty, robustness, cost, scalability, quantified impact and local depth.

## Options
| Option | Spike | Scalar metric |
|---|---|---|
| A | **Recharge-verifier**: per-storm pit water balance → infiltration volume + clogging index + verdict | event-volume MdAPE; clogging precision/recall |
| B | Extraction fingerprinting on DWLR (24 h harmonic / step drawdown) | detection AUC at fixed false-alarm rate on injected signals |
| C | SealGuard: tamper/vibration/current node on sealed borewells | alarm precision |
| D | Ingest-QC for public DWLR + our nodes | F1 on injected faults; % usable data recovered |

## Six Thinking Hats (on option A, the front-runner)
- **White (facts):**
  - The RWH mandate (≥100 m²), 10 %/15 % rebate, 1.5× penalty, ₹204.46 cr disbursed and the self-certification announcement are all sourced (HT 21 Apr 2026).
  - DJB plans to restore 1,000 non-functional systems (Indian Express 2026).
  - Pit stage is directly measurable. A 100 m² roof in a 50 mm storm at runoff 0.8 (**assumed**) delivers 4.0 m³, while ±15 mm stage on a 2.25 m² pit is ±0.034 m³. The signal is ≫ sensor error.
  - Incumbent CGWA DWLRs log 2 readings/day at about ₹38,000 (Acorn page). That is too slow for storm events and priced for industry.
- **Red (gut / judges):** "Measured, not self-declared" is a sentence a Delhi judge will remember. A drum-and-drain demo you can pour water into is tangible.
- **Black (risks):**
  - Stage is not recharge. You need inflow, overflow and Δstorage, and bypass can't be seen.
  - Silt clogs the sensor port.
  - The owner pays for a device that may cost them a rebate (perverse incentive).
  - DJB may prefer cheap random inspections.
  - ERA5 rain is smooth, so a local gauge is needed.
  - No real pit data tonight: the simulation is ours.
- **Yellow (benefits):**
  - Cooperative install (the owner wants the rebate).
  - A cheap BOM, because the sensor sits ≤3 m deep.
  - Event data double as maintenance alerts (clogging), which is where real recharge is lost.
  - It scales to every Indian city with an RWH bylaw.
  - It links to aquifer outcome data (DWLR) for the city-level story.
- **Green (alternatives):**
  - Fakes can be caught by cross-checking against rain and neighbours.
  - An EC channel can spot polluted inflow.
  - A "recharge credit" ledger lets builders offset CGWA/DJB obligations with verified m³ (future, not pitched as fact).
  - Option D makes the city-scale view honest.
- **Blue (process):** Choose A plus D. Evaluate on a simulated fleet driven by real Delhi rain now and on a physical rig in Round 2. Keep B as a labelled "zone influence index" only. Drop C.

## Thesis → antithesis → synthesis
- **Thesis (lead):** A wins on every judged axis that B and C struggle with: physical observability, cooperative deployment, a direct policy hook, measurability and demo. D is cheap, uses real data we hold, and protects every downstream claim.
- **Antithesis (independent rubber-duck review, condensed):**
  - "Three roles in one node is marketing fiction". Pick one hero.
  - "Water level is not recharge volume": without measured or calibrated inflow and overflow, "verified recharge volume" is indefensible; report infiltration with uncertainty.
  - "Six-hourly DWLR cannot identify illegal pumping": aliasing and confounders mean injected-Theis AUCs would be "impressive but meaningless".
  - SealGuard is bypassable and legally fraught.
  - ₹204 cr is rebates, not a procurement budget.
  - Owners face a perverse incentive.
  - Adoption needs a protocol, installers, calibration and an appeals process.
  - Must-not-claims: pressure + rain directly measures aquifer recharge; DWLR identifies illegal borewells; one universal tamper-proof node is ready for city-wide deployment.
- **Synthesis (decision):**
  1. Hero = **RechargeMeter, an audit instrument for Delhi's RWH incentives**. It converts self-certification into measured storm-event evidence (inflow, overflow, infiltration with an uncertainty band, clogging index, verdict) and ranks inspections.
  2. Inflow is estimated from the stage rise during the storm, cross-checked against rain × catchment × runoff prior. Overflow is bounded by the spill stage. The commissioning test (one metered fill) fixes pit area and k_as_built. Everything is reported with an uncertainty band, never as aquifer recharge.
  3. Spike 2 = **data integrity** (ingest-qc + signed logs), real-data first.
  4. DWLR analytics appear only as the **outcome map** (QC'd levels, monsoon rise). Any pumping signal is shown as a "zone influence index" with explicit caveats.
  5. The business model is pitched as a **verification-fee + rebate-linked pilot** (RWA / institutional campuses first, then DJB's 1,000 restorations), not as "₹204 cr market".

## Scores (1–5)
| Option | Impact on criteria | Novelty | Feasibility by 1 Dec | Measurability | Demo | Total |
|---|---|---|---|---|---|---|
| A recharge-verifier | 5 | 5 | 4 | 5 | 5 | **24** |
| D ingest-qc | 4 | 3 | 5 | 5 | 4 | 21 |
| B extraction fingerprint | 4 | 4 | 3 | 2 | 3 | 16 |
| C SealGuard | 3 | 2 | 3 | 2 | 3 | 13 |

## Update (09:50 IST, 4 Oct)
- **Ratchet v1** (kept): monsoon-2024 holdout event MdAPE 10.3 % → 3.0 %, fake recall 0.3 → 1.0.
- **Frozen evaluator v2** (drain-law mismatch + imperfect gauge): v1 scores 13.0 %. Three drain-law variants reach 4.9–5.3 % on v2 but worsen v1 by 15–31 % relative. Under the pre-registered keep rule they are **not kept**.
- The spike choice stands. The metric is working as intended: it caught an overfit before we adopted it.

## Consequences
- The walking skeleton implements C0 (simulator on Open-Meteo archive rain, default model; originally mislabelled "real ERA5"), C5 (verifier baseline) and C4 (QC on real DWLR) first. The autoresearch loop targets C5's event-volume MdAPE with a frozen evaluator.
- The Round-2 prototype must include a physical rig with a metered inflow (ground truth) and blind trials.
- The pitch never claims the must-not-claims above.

## Update (12:30 IST, 4 Oct; final-deck review)
- C5 now **defers** instead of judging when inputs are missing: rain coverage < 90 %, or a stage gap > 60 min. Contracts v0.3.1; 7 unit tests.
- Evaluator v3 adds sensor realism: kept v1 scores 14.5 % on holdout.
- The product boundary is **maintenance screening** (drain rate). Infiltrated volume is a model-based estimate; a per-event band is planned.
- The spike choice stands.
