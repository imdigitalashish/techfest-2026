# C7 — Teacher point-of-use (Spike 1)

> Per-component innovation scan (lead, 4 Oct 2026). Contract: `architecture/contracts/fln_contracts.py`. Evidence lives in `research/sources/`; anything not opened at a primary source is marked UNVERIFIED. Scores 1–5: impact · novelty · feasibility · measurability · demoability.

**Responsibility.** Monday plan: TaRL groups + one activity per group as WhatsApp / ≤ 3 SMS / IVR in the local language.

**State of the art / what is deployed.** Delivery channels already used by states: SwiftChat bots (14 states, vendor figures); WhatsApp-based Rocket Learning (early years). Shiksha Copilot: 789 of 1,043 teachers used it; Kannada quality gap shows generation needs QA (`sources/deployed-states-ngos.md`).

**Innovation candidates**

| Candidate | Scores (I·N·F·M·D) |
|---|---|
| Retrieve activities from a curated, competency-coded catalogue (state/DIKSHA IDs); no free generation | 5·2·5·4·5 |
| IVR menu per group for teachers without smartphones | 4·3·4·3·4 |
| Plan acknowledgement + recheck date written to the action ledger | 4·3·5·4·3 |

**Status.** Implemented: `components/teacher_view/`. First run (synthetic class of 60): Hindi WhatsApp plan 659 bytes; SMS 3 segments; IVR script.

**Isolated metric.** Payload bytes / SMS segments; group–level match rate; (pilot) plans acted on.
