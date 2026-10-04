# ADR 001 — Spike components (v2): (A) evidence-anchored ingestion + (D) one Indian material/component route comparison; national grid as a bounded foundation

- **Status:** accepted v2, 4 Oct 2026 (lead), superseding v1 (07:44 IST). Spike-D data gate decided by 7 Oct (roadmap stage 1a); the ADR as a whole is revisited at the 12 Oct selection gate.
- **Why v2:** an independent hostile-LCA-jury review (`deliverables/jury-review-hostile-lca.md`) and a cross-model ADR review by gpt-6-astra (`reviews/2026-10-04-adr001-gpt-6-astra.md`) both found that v1 over-weighted the grid service and over-claimed novelty and verification strength. Decisions per item are recorded in the review file.

## Context (committed run, `eval/results/summary.md`)
<!-- headline:begin -->Central results (CEA FY2025-26 average grid, partial upstream, inputs id `d337af61e1-dirty`, n = 10000 paired Monte Carlo draws, seed 20261004): the legacy-data sedan case is harmonized: GWP100-AR5 — e-Verito-class BEV vs petrol sedan saving **10.0 % (-10.1 to 25.6)**, P(lower) 0.81 (not decisive). The scooter calculation gives **38.1 % (32.0 to 43.2)** lower emissions in a **partial, mixed-basis GHG indicator** (GWP100-AR5, GWP20(CH4), unspecified), not yet a harmonized GWP100 comparison.<!-- headline:end -->
- Arithmetic implementation verification against the same source that supplies most inputs: ICCT 2021 two-wheeler table 0.06 %, India sedans 1.0 %. This verifies arithmetic, not accuracy.
- **Contribution:** grid electricity is the largest stage of every EV result. **Between-method scenarios:** the grid-accounting choice (CEA average vs operating vs build margin) moves the e-scooter saving from 16 % to 56 % and flips the sedan sign. **Within-method parameter uncertainty** is smaller and is driven by real-world consumption. These are three different statements. We no longer say "grid method dominates" without saying which one we mean.
- Independent Indian car studies (TERI 2026, IIT Guwahati 2025, IIT Kanpur 2023) bracket our petrol and BEV sedans but not our CNG or diesel. That makes Indian vehicle, material and consumption data the open question, not grid arithmetic.

## Candidates (scored by the lead after both reviews; 1 weak … 5 strong)
| Candidate | Impact R1/R2 | Novelty | Feasibility (2-person core, exams 19–25 Nov) | Measurability | Demoability | Decision |
|---|---|---|---|---|---|---|
| **A. Evidence-anchored ingestion** — extractor proposes records from Indian public documents; fail-closed checks: quote presence (number-boundary aware), value-in-own-quote, then field/unit/year/locator binding; human approval; measured reviewer effort | 4/5 | 3 | 3 | 4 | 5 | **Spike** |
| **D. One Indian material/component route comparison** — e.g. a steel part via BF-BOF vs coal-DRI-EAF vs scrap-EAF, or aluminium primary (coal captive power) vs recycled; battery cell origin vs Indian pack assembly; behind a source-availability gate (corporate BRSR ratios are not product LCI) | 5/5 | 3 | 3 | 4 | 5 | **Spike** (if the 4–7 Oct data gate passes) |
| B. Grid-factor service | 3/3 | 2 | 3 (national) / 2 (state, prospective) | 3 | 4 | **Bounded foundation:** harmonized national attributional factor (CO2e, partial upstream, built) + margins as labelled sensitivities. State and prospective factors are deferred until independently testable (rolling-origin back-tests vs persistence; consumption-based state accounting). |
| C. Harmonization + honest uncertainty | 4/4 | 2 | 3 | 3 | 3 | **Mandatory practice, not a spike:** gas-basis flags, honoured source ranges, paired MC, screening-only wording; no calibration claim until independent benchmarks exist |
| E. LLM chat copilot | 2/2 | 1 | 5 | 2 | 4 | Rejected — little judging value for its reliability burden |

## Six Thinking Hats (v2)
- **White:** the verifier checks quote presence and, since v5, the value-in-quote. It did not bind values to table headers, units or pages, and `0.675` used to match inside `10.675` (fixed in v5). Negative tests are synthetic, clustered and reused, so zero observed accepts is a regression result only — it does not estimate or bound the deployment false-accept rate.
- **Red:** the MHI/ICAT jury cares about manufacturers' choices ("which steel, which cell origin"). A route comparison with Indian sources lands harder than a state map.
- **Black:** D may fail its data gate (route-level Indian data can be thin or only corporate-level). A may look like "PDF search". Both risk numbers that look auditable but are not comparable — the biggest risk per the astra review.
- **Yellow:** A is the scalability answer (how ICAT and suppliers add data). D directly serves OEM and supplier decisions. B (national, harmonized) keeps every EV result honest.
- **Green:** reviewer-minutes per accepted record as A's product metric; a deliberate "rejected incompatible factor" moment in the demo; BRSR-to-LCI qualification rules as a reusable artefact.
- **Blue:** A + D as spikes; B national foundation; C mandatory; E rejected. Gate D on 7 Oct; fallback = harmonized national B plus one Indian-route material record set (no invented supplier detail).

## Thesis → antithesis → synthesis
- **Thesis (lead, v1):** trustworthy Indian data is the bottleneck. Ingestion with provenance plus a grid service for the dominant EV term wins.
- **Antitheses (independent):**
  - *Hostile jury (rubber-duck):* non-harmonized gas bases; undefined boundary, functional unit, allocation and EOL; circular validation; overclaimed metrics; "state" map is not a state mix.
  - *gpt-6-astra:* text presence ≠ verified factor; ratchet overfit; B's metrics don't validate geography; novelty overstated (carculator/premise handle India regions; LLM LCI extraction exists — Kumar et al. 2025, *ES&T*; Tang et al. 2026); manufacturing decisions undervalued.
- **Synthesis (v2):** keep A, but make it *semantic qualification with measured reviewer effort*, not quote search. Promote D so the database demonstrates a manufacturer-relevant Indian route choice end to end. Shrink B to a harmonized national foundation with labelled sensitivities. Make harmonization and honest uncertainty non-negotiable. Claim novelty narrowly: an openly auditable Indian corpus with machine-checked evidence anchoring, compatibility checks and measured curation effort — not "first-ever extraction or prospective India LCA".

## First principles
An LCA result is Σ (activity amount × emission factor). A comparison is only as credible as its least-comparable large term. The large terms today are grid electricity (EV), fuel (ICE) and, as Indian vehicle data replace European proxies, materials. A makes adding any term cheap and checkable. D proves the database can answer a manufacturing question with Indian evidence. B keeps the largest term consistent.

## Consequences
- **Metrics:**
  - *A:* document-macro F1 and complete-record precision/recall on a frozen document-level dev/test split (unseen publishers); abstention rate; reviewer minutes per usable record; harder negatives (wrong field, neighbouring cell, unit, year, scope). "Zero observed false accepts" stays a regression requirement, not a statistical guarantee; pre-declared complete-record recall ≥ 0.6 at precision ≥ 0.9 on unseen publishers, with a human-timing protocol.
  - *D:* reproduction of the source's route intensities (accounting test), then decision robustness, i.e. P(route X < route Y) under paired uncertainty.
  - *B:* national reconstruction as an accounting test only; prospective claims need rolling-origin back-tests vs persistence (MAE, signed bias).
- **Two-week plan (Round 1 due 30 Oct):**
  - 4–7 Oct: freeze one decision, functional unit, boundary and characterisation; run D's data gate.
  - 8–12 Oct: annotate a diverse document set with reserved unseen documents; benchmark extraction vs manual and rule baselines; dimensional tests for the grid upstream (done for the CO2e adder: the ratio form avoids the `/1000` slip in the research note).
  - 13–18 Oct: one complete source-to-comparison chain including a deliberately rejected incompatible factor; independent technical review.
- Round-1 documents distinguish demonstrated capability (4 Oct) from December commitments. Integration checkpoint before 19 Nov; feature freeze early December for offline rehearsals.
