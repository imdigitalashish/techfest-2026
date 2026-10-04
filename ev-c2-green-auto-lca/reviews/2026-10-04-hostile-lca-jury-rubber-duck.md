# Review record — hostile LCA-jury review (rubber-duck, harness-default model)

- **Date:** 4 Oct 2026 ~09:55 IST · **Artifacts:** Round-1 methodology + roadmap drafts v0.1, landscape, architecture, data, engine v1, eval v1 (commit `657edd1`) · **Reviewer:** `rubber-duck` agent (default model of the harness; model id not exposed), via `task` before the sessions-only directive.
- **Raw review:** verbatim in [`deliverables/jury-review-hostile-lca.md`](../deliverables/jury-review-hostile-lca.md) (§1 issues, §2 questions, §3 ICCT wording).

## Status note (superseding, 4 Oct 2026 11:00 IST)
Item 1's resolution was later changed by the gpt-6-sol review (its item 1): the grid CO2e adders now use **AR5** GWPs in the case studies (not AR6). AR5 and AR6 are separate gas-basis families, so the car case is harmonized on AR5 GWP100 and the scooter case remains mixed. The rows below are kept as originally decided, for the record.

## Lead decisions
| # | Issue (short) | Decision | Reason / action |
|---|---|---|---|
| 1 | Unharmonized gas bases | **ACCEPTED** (partly done) | Every record declares its gas basis; the engine flags mixed totals. The central case uses an AR6 GWP100 grid CO2e (CEA CO2 + IPCC CH4/N2O + BUR-4 coal-mine CH4). Car case harmonized on GWP100 (AR5/AR6, <1 % effect); 2W flagged (ICCT 20-year-methane production factor). An elementary-flow inventory (CO2/CH4/N2O separately) is a roadmap item. |
| 2 | Boundary not defined | **ACCEPTED** | Methodology §3 boundary matrix and cut-off rule; maintenance added to both cases; exclusions listed. |
| 3 | Functional units underdefined | **ACCEPTED** | §3: FU with reference flows per case; declared units for materials and components; lifetime throughput for batteries. |
| 4 | No allocation policy | **ACCEPTED** | §4 hierarchy; `allocation` field on records (inherited-unspecified flagged); process/exchange layer in the roadmap. Roadmap no longer claims allocation is done. |
| 5 | EOL undefined | **ACCEPTED** | §5 three non-mixable EOL models; `eol_included` flag prevents double counting; battery EOL data plan. |
| 6 | "India 2026" overstated | **ACCEPTED** | Renamed "illustrative 2026-grid case using legacy ICCT 2021 vehicle data". Decision scenarios use uniform source-ambiguity ranges instead of benchmark-implied values. Maintenance added; E0 kept only as a sensitivity. E20 WTW and on-road data in the roadmap. |
| 7 | Average/OM/BM conflated | **ACCEPTED** | Average = attributional central; OM/BM labelled decision sensitivities. |
| 8 | Monte Carlo not defensible | **ACCEPTED in part** | Done: honoured source distributions, fixed GWP, scorer/rationale fields. Not yet: quantity-specific basic factors, correlation groups, second scorer (roadmap). |
| 9 | Variance share / DQI overclaim | **ACCEPTED** | Renamed "screening importance (normalized squared Spearman)" and "pedigree screening score". |
| 10 | Circular validation | **ACCEPTED** | Called "arithmetic implementation verification". Added three independent Indian car LCAs (TERI 2026, IITG 2025, IITK 2023) as a plausibility band (petrol and BEV inside; CNG and diesel not, reported as findings). Fact-sheet wording corrected (only overlapping stage values match). |
| 11 | State map ≠ state mix | **ACCEPTED** | Relabelled; state/prospective deferred (ADR v2). |
| 12 | AI ingestion not built | **ACCEPTED** | Honest status in methodology §9; extractor, gold set and metrics in roadmap stage 2. |
| 13 | Roadmap overpromises | **ACCEPTED** | Roadmap v1.0 freezes a credible minimum with stretch goals marked. |
| 14 | Stale metadata | **ACCEPTED** | Results tables rendered from `latest.json`; `check_docs.py` drift test; rebase-stable inputs id. |
| C | ICCT wording | **ACCEPTED** (adapted) | Used in methodology §1 and landscape. |

Accepted 14 (one in part), rejected 0.
