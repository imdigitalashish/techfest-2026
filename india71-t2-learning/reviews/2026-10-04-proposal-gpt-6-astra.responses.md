# Lead responses — hostile-judge review of proposal v0.3 (gpt-6-astra, max)

Review: [`2026-10-04-proposal-gpt-6-astra.md`](2026-10-04-proposal-gpt-6-astra.md). Changes land in proposal v1.0 (`deliverables/round1-proposal.md`, `deliverables/India71_100_[TeamID].pdf`). Feedback is advisory; decisions below.

| # | Severity | Issue (short) | Decision | What changed / why |
|---|---|---|---|---|
| 1 | BLOCKING | ASER proxies presented as NIPUN attainment | ACCEPTED | §1 labels ASER figures "foundational-skill proxies, not measured NIPUN attainment"; dashboard and demo use the same label |
| 2 | MAJOR | Grade 3 vs Grade 2 endpoint unresolved | ACCEPTED | §1 quotes both (2021 document; 2024 Rajya Sabha AU523) and says the pilot follows its state's operative order |
| 3 | MAJOR | National deficit ≠ local bottleneck | ACCEPTED | §1 defines one pilot measure (below-level children getting an activity + recheck in 6 weeks; reported vs re-tested gap), baseline in phase 0; mechanism framed with verified evidence (MoE "working in silos", AU349) |
| 4 | MAJOR | Ecosystem weakened artificially | ACCEPTED | §3 column renamed "What the sources reviewed do not document"; novelty stated as adaptation (§4 Loop 2) |
| 5 | MAJOR | Real-data analysis is a concordance check | ACCEPTED | §2 concludes only that ASER and PARAKH are kept separate and never substituted |
| 6 | BLOCKING | Benchmark to PARAKH/ASER can erase progress | ACCEPTED | §4: benchmark only to an independent survey of the same construct, population and term; never to PARAKH scale scores or old ASER rounds |
| 7 | MAJOR | 10 % is a budget slogan | ACCEPTED | Pre-registered precision–budget curve on held-out data (±8.3 / ±6.0 / ±4.2 pp at 5 / 10 / 20 %); per-100-schools quantities in §5 |
| 8 | MAJOR | CRC not independent; retest timing | ACCEPTED | §4: frozen roster, two-week window, cross-cluster assessors, blinded scores, 20 % double assessment, coaching after recording, discrepancy ≠ proof of cheating |
| 9 | MAJOR | Sample cannot verify every child | ACCEPTED | "Cure verified" removed; routine teacher rechecks separated from sampled independent verification |
| 10 | MAJOR | Teacher workload contradictory | ACCEPTED | Termly check + weekly plan; the check replaces state-test data entry; time per child given as an explicit assumption; measured in phase 0 |
| 11 | MAJOR | TaRL effects attached to a thinner intervention | ACCEPTED | Protected daily level-grouped period + CRC mentoring restored (state order); "we do not claim TaRL's effects for software alone" |
| 12 | MAJOR | Cost claim | PARTLY ACCEPTED | Removed the tablet-cost comparison; added quantities per 100 schools and the sourced VSK budget line. REJECTED: inventing rupee unit prices — no source; "prices to be quoted in phase 0" |
| 13 | MAJOR | No authority/procurement chain | ACCEPTED | §5 responsibility table + phase-0 gates (state order, legal review, data-sharing/processor agreements, VSK slot, timetable release) |
| 14 | BLOCKING | Legal position not current | ACCEPTED | Verified G.S.R. 843(E) (s. 9 in force 18 months after 13 Nov 2025) and DPDP Rules 2025 Rule 12 / Fourth Schedule item 3 (conditional education exemption; s. 9(2) not exempt); purpose-by-purpose legal gate (`research/sources/verification-2026-10-04-pm.md`) |
| 15 | MAJOR | Data boundary contradicts architecture | ACCEPTED | §4 discloses central pseudonymised processing; added record/holds/who-sees/kept table |
| 16 | BLOCKING | Case/cure register: stigma, punitive use | ACCEPTED | Disease framing removed; time-limited, revisable learning-support record; no labels, quotas or teacher rankings; state-order firewall against personnel use; parent/teacher correction |
| 17 | MAJOR | Notification targets move Campbell's law | ACCEPTED | Dominant-strategy claim and quotas dropped; unmet need only as an uncertain aggregate for planning (ADR 001 updated) |
| 18 | MAJOR | Inclusion route unspecified | ACCEPTED | Printed default tool; no phone/APAAR/Aadhaar requirement; local temporary IDs |
| 19 | MAJOR | Language/disability safeguards postponed | ACCEPTED | "Not assessable with this instrument" outcome with human review; languages and accessible modes fixed with SCERT/DIET before launch |
| 20 | MAJOR | Posterior threshold as certainty | ACCEPTED | "≥ 90 % sure" wording removed; demo reports exact-level accuracy (0.546 at 8 items vs 0.597 full); "a model rule, not field certainty" |
| 21 | MAJOR | Two marginals don't validate the simulator | ACCEPTED | "Matched to two ASER 2024 marginals"; "stress tests of the method, not evidence about real states"; need-correlated inflation scenario run; failure regime (5 % budget worsens targeting) reported |
| 22 | MAJOR | Staggered start ≠ causal | ACCEPTED | Phase 0 = feasibility, no impact claims; phase 1 = cluster-randomised rollout with pre-specified independently assessed outcome |
| 23 | MAJOR | Allocation story undefined | ACCEPTED | Pre-registered test: allocation gain not shown (and worse at 5 %); allocation optimiser removed from value claims |
| 24 | MINOR | Dates / partial distributions | ACCEPTED | ANER and FLS partial distribution removed from the proposal; references 18–19 now point to the verified legal texts |
| 25 | MINOR | Submission preflight | ACCEPTED | `deliverables/India71_100_[TeamID].pdf`: 6 A4 pages, Arial only, all fonts embedded, minimum glyph 11 pt (`python3 deliverables/build_pdf.py --check`), vector diagram at natural size; team details remain user input |

Totals: 25 issues — 24 accepted (1 partly), 1 sub-item rejected (invented unit prices).
