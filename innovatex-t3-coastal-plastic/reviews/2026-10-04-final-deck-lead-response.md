# Lead response to the hostile-judge review (gpt-6-astra, max)

Review: [`2026-10-04-final-deck-gpt-6-astra.md`](2026-10-04-final-deck-gpt-6-astra.md), at snapshot `d6ce52d`, reviewed 16:47 IST. Response written 4 Oct 2026, 17:10 IST by the project lead. Feedback is advisory; the decisions below are the lead's.

**Totals:** 16 issues — 15 ACCEPTED, 1 PARTLY ACCEPTED, 0 REJECTED. The "against switching from T1" verdict is kept, and its reasoning is rewritten as the reviewer suggested.

| # | Severity | Decision | What changed |
|---|---|---|---|
| 1 | BLOCKER | ACCEPTED | Every flood-safety and retention guarantee removed. The release is "intended to limit extra head rise within a tested envelope"; retention during release is "unproven". Changed in the deck (slides 3, 7, 9 and notes), Q&A 6–7, presenter card, pitch index and prototype plan §2. T3 now measures opening head, delay, residual obstruction, reset after jams, and retention during release. Added a concept drawing (slide 3) showing pocket, release path and sensor roles, labelled CONCEPT · NOT TO SCALE · UNTESTED. |
| 2 | MAJOR | ACCEPTED | "Interval" became "central 90% scenario range"; "seasons" and "draws" became "parameter settings of one model". The ranking now "guides experiments", not "trust it". Tide RMSE is described as an in-sample residual against model sea level (fit through Sep 2025), not gauge validation. "Every assumed parameter" became "the main process parameters; geometry, crew rules and some structures fixed". |
| 3 | MAJOR | ACCEPTED | Policies renamed: assumed fixed roster / fill-fraction-ranked rule / full policy. Ablations run (twin child, 9e65ee1): tide timing alone −3.2% [−12.0, +0.6]; forecasts −0.4%; kg ranking −2.0%; full policy vs kg-ranked rule −2.7% [−12.6, +1.2]. Only the full combination vs the fill-fraction rule clears zero. "Sensors alone don't help" removed; Q&A 17 now says a kg-ranked rule may be enough and should be tested first. |
| 4 | MAJOR | ACCEPTED | Slide 5 rewritten as "assumed capture losses dominate this twin". It adds the floor/velocity split (51% of escape is the assumed still-water leak, 38% speed-driven) and exposure (13.2% of plastic arrives at high speed). ITOPF is labelled an oil-boom analogy; the lead verified its wording in the PDF, p. 3. Angle results are labelled a consequence of the assumed curve. |
| 5 | MAJOR | ACCEPTED | Sensing roles fixed everywhere: the camera's mat area = fill; the ultrasonic over open water = stage; a degraded camera → fill "unknown" → crews follow the roster. T4 gets thresholds (A). Shown in the concept drawing, slide 8, Q&A 10–11 and plan §1. |
| 6 | MAJOR | ACCEPTED | The 1 Dec commitment is a closed-loop bench rig needing no field permission. The field pilot is conditional on permission, safety and a survey. The candidate, ML Complex nullah boom in Dahisar (HT: highest volume), is marked unsurveyed and uncontacted, with gate status UNVERIFIED; gated sites are deferred. "No new civil works" removed. Scale is "repeated local engineering", not configuration. |
| 7 | MAJOR | ACCEPTED | The gap is framed as a hypothesis ("we found no public evidence that BMC's booms report fill or are tide-timed"). Plastic Fischer's Usha Nagar, Bhandup boom and its Mumbai TrashBoom are acknowledged (F12, F16). Universal negatives are listed under Don't say. |
| 8 | MAJOR | ACCEPTED | The node is "listed parts only", with exclusions shown. The per-boom division of the O&M contract is removed from deck and Q&A, the contract is quoted as a network figure, and there is no payback claim. |
| 9 | MAJOR | ACCEPTED | The lead re-opened OpenCity: it is the *general budget, which includes* roads and storm-water drains, that takes more than half. F23 corrected; the half-budget claim removed from the deck. |
| 10 | MAJOR | ACCEPTED | MRV is scoped to "our synthetic fraud mixture". Added: inflation-only 69.4%, small inflations 24.4%, false flags 17.8% if density is a quarter higher, tamper detection 100% with an external anchor vs 0% chain-only for tail truncation. Q&A 14 covers custody (keys, scales, batch IDs, audits; PLANNED). |
| 11 | MAJOR | ACCEPTED | The measurement boundary is defined once in plan §8: unique dry flexible-plastic input, cleared, stored (temporary), final treatment, escape against a matched baseline. FWCE is aligned with the analysis definition in ADR 001. Field tracers must be recoverable (counted out, recovered by a containment net, with permission). The wet-film chain is in Q&A 18. |
| 12 | MAJOR | ACCEPTED | Acceptance gates added: paired, randomised, ≥10 runs; minimum useful T2 effect of 15 percentage points (A); T3 cap rule; T4 error/availability thresholds (A); new T7 for power and outage. A second range sensor is priced (BOM C ₹5,264.12; flume total ₹39,222.11). The undersized buck converter and the unverified LiFePO4 controller support are flagged "fix before procurement". |
| 13 | MINOR | ACCEPTED | "A May 2025 report described nine units… current count UNVERIFIED". Legacy 25 mm/h is separated from "about 50 mm/h today" (F24) in the backup slide. |
| 14 | MINOR | ACCEPTED | "Fined 44,448" became "acted against 44,448"; F10 notes that the number actually fined is UNVERIFIED. |
| 15 | MINOR | PARTLY ACCEPTED | Restructured: the solution with its concept drawing is now slide 3 (at 1:25), evidence is split across three slides, and secondary Mumbai statistics moved to a backup slide. *Not done:* the dashboard stays a backup; a 10-minute slot cannot spare a live tour, and slide 3 now shows the operator's morning action instead. |
| 16 | MINOR | ACCEPTED | Memo v3 says "simulated" gains, acknowledges T1's prospective customer, drops the like-for-like node comparison and the "~7×" ratio, and calls the scores memo judgments. A tabletop test is a risk-reduction gate, not a reversal. |

**Facts the reviewer could not verify, now verified by the lead:**
- F14 (ITOPF PDF, p. 3, local copy);
- F16 (Pinwheel page HTML: 3.2 million kg, 71 TrashBooms, 98 jobs, 8 sites, Inclusiv by ASM).

F20 (the Interceptor's text-message claim) is not used in the deliverables.

**Pending framing, as advised:**
- The detector line uses only the committed held-out test (mAP50 0.857), shows the zero-shot reference (0.394) and the cross-site drop (0.524), and makes no edge-hardware throughput claim.
- Boom-angle rows are SENSITIVITY with same-hardware denominators, the 2.9× length factor at 20°, and "don't add rows".
