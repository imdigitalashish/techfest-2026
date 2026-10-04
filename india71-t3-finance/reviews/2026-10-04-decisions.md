# Review decisions — 4 Oct 2026 (lead: india71-t3-finance)

Reviews: [`2026-10-04-proposal-gpt-6-astra.md`](2026-10-04-proposal-gpt-6-astra.md) (hostile judge, 15 issues, 3 blocking) and [`2026-10-04-code-gpt-6-sol.md`](2026-10-04-code-gpt-6-sol.md) (code + eval + reproduction, 14 issues + 4 in the C5 addendum, 4 blocking). Feedback is advisory; the lead decides (PLAYBOOK §10). Fixes were applied in proposal v1.1 and code committed with the C6 v0.3 pre-registration (`eval/preregistration/c6_v03.md`). Neither reviewer has re-reviewed the fixes.

## gpt-6-astra — proposal (hostile judge)

| # | Sev. | Issue (short) | Decision | Action / reason |
|---|---|---|---|---|
| 1 | blocking | UIDAI reference keys are entity-specific; no cross-bank identity | **ACCEPTED** | Verified UIDAI Circular 14/2025 para 7(a) "complete logical segregation of ADV for each requesting entity", 7(k) "Hashing of Aadhaar numbers is not allowed to be used as Reference keys". Phase 1 is bank-local (customer IDs within one bank); cross-bank linkage is an explicit, unbuilt dependency needing a separately authorised translation service. |
| 2 | blocking | Legal boundary by recipient, not lawful processing | **ACCEPTED** | Per-flow legal table; targeting runs inside the bank under its duty to review inactive accounts (RBI/2023-24/105); a cross-bank clean room only after a legal go/no-go naming operator, fiduciary roles, processor contracts, notice and basis. |
| 3 | major | "Not centrally maintained" over-attributed | **ACCEPTED** | Now quoted precisely: range-wise inoperative data, closures by women and area, accounts < Rs 500, credit to PMJDY holders; gender split of the inoperative *stock* was asked and not provided. |
| 4 | major | Indicators not comparable; gap overstated | **ACCEPTED** | Stated that the three indicators measure different things and cannot be netted; absolute claims softened ("we found no published …"). |
| 5 | major | Score turns poverty / cash access into failure | **ACCEPTED** | Two measures: regulatory status (with DBT exemption) and analytical descriptors; primary outcome = successful, safe access when wanted; cash withdrawal of a benefit is legitimate use; "pass-through" is a description, never a failure. Code: `no_use_24m` vs `regulatory_inoperative`. |
| 6 | major | Women's floor ≠ protection from exclusion/coercion | **ACCEPTED** | Rights capsule: outreach optional, never conditions benefits; standard service for all incl. holdouts; targeting allocates only extra outreach; grievance route. |
| 7 | major | BC accountability → surveillance of BC Sakhis | **ACCEPTED** | No individual BC scores; BC-level data only for liquidity/connectivity/workload support. C5 rule D6 denies BC-area tables to forums. |
| 8 | major | DP needs a release contract | **ACCEPTED** | Contribution bounds, one cumulative budget across overlapping tables per period, suppression; code: secret noise, validated persistent ledger, composed budget. |
| 9 | major | KYC gap outdated (June 2025 BC re-KYC) | **ACCEPTED** | Verified RBI/2025-26/51 (para 38(a)(iia)) and RBI/2025-26/52 (12 Jun 2025); root cause rewritten as uneven operationalisation. |
| 10 | major | No funded delivery model | **ACCEPTED** | Proposed RACI with one partner bank owning permissions, BC payment and budget; no new NPCI/RBI roles until a cross-bank phase is approved. |
| 11 | major | Pilot not powered | **ACCEPTED** | Gates, not dates; worked sample-size example from a committed calculation (`eval/power_calc.py`); clusters, pre-registration, consent. |
| 12 | major | Scorecard headline inaccurate | **ACCEPTED** | Now "gamers 23% of the top 20 against 21.4% overall"; labelled a stylised independent-row mechanism test. |
| 13 | major | Scale claims contradict maturity | **ACCEPTED** | Readiness conditions; DEPA optional and experimental; "not new infrastructure" removed for the cross-bank phase. |
| 14 | minor | Citations not followable; NSFI 2025-30 missing | **ACCEPTED** | References hyperlinked; P4 URL recovered and re-verified (PIB NoteId 159721); NSFI 2025-30 (RBI, 1 Dec 2025) verified and cited; P19 kept as a cumulative cohort. |
| 15 | blocking | Renderer drops the team block; filename placeholder | **ACCEPTED (renderer)** / **REJECTED (rename)** | Renderer bug fixed (the regex consumed the team paragraph); team block restored with visible placeholders. Rename rejected: no Team ID exists before registration, and the Supervisor asked for a placeholder filename — listed under *Needs from user*. |

## gpt-6-sol — code and evaluation (incl. C5 addendum)

| # | Sev. | Issue (short) | Decision | Action / reason |
|---|---|---|---|---|
| 1 | blocking | H1 (v0.2) did not test the registered upgrade-only policy in seeds 12/15 | **ACCEPTED** | v0.2 results stand as recorded with this caveat appended; v0.3 challenger is an exact copy of the rule's plan except whom to upgrade (tested), and a corrected test was pre-registered (seeds 20–29). |
| 2 | blocking | DP release invertible (public seed) | **ACCEPTED** | Secret OS-entropy noise by default; seeds only in simulations/tests; test added. |
| 3 | blocking | Women's floor not enforced on deployable policies | **ACCEPTED** | Floor-stratified lotteries and ranked picks in rule and challenger; `floor_ok` asserted per plan; reviewer's 2-person case tested; H3 registered. |
| 4 | major | Gate validates a different model | **ACCEPTED** | One 70/30 split; deployment uses the same fitted effects and model the gate evaluated. |
| 5 | major | Holdout and BC cap only contract fields | **ACCEPTED (holdout)** / **DEFERRED (BC cap)** | 10% gender-stratified holdout implemented and tested; per-BC task cap stated as a design requirement, not implemented. |
| 6 | major | Model sees true covariates | **ACCEPTED** | Bank-observable proxies with stated error rates (`eval/pipeline.py`). |
| 7 | major | Calibration vs tested cohort not PMJDY | **ACCEPTED** | Simulator calibrates on PMJDY accounts; cohort = Jan Dhan holders. |
| 8 | major | "Inoperative" ≠ RBI legal status for DBT-purpose accounts | **ACCEPTED** | State renamed `no_use_24m`; `regulatory_inoperative` carried from CBS; simulator models the DBT-purpose exemption. |
| 9 | major | Ledger: no composition, NaN accepted | **ACCEPTED** | Validated, persistent, atomic ledger; unit + district releases charged to one budget; tests. |
| 10 | major | "Oracle" is not an upper bound | **ACCEPTED** | Renamed *reference* (Lagrangian + greedy fill), "share of the reference gain"; no upper-bound language. |
| 11 | major | Scorecard test is IID, not longitudinal | **ACCEPTED (as a limitation)** | Documents call it a stylised mechanism test; a longitudinal end-to-end test is future work. |
| 12 | major | Incomplete linkage → optimistic value | **ACCEPTED (sensitivity)** | Perfect-linkage sensitivity registered and reported per seed. |
| 13 | minor | Small units → silent NaN | **ACCEPTED** | `status = insufficient_data` with a minimum count; test. |
| 14 | minor | "No more common" false | **ACCEPTED** | Same fix as astra 12. |
| 15 | blocking | C5: non-customer records at coarse granularity | **ACCEPTED** | D5 now denies any bank/BC request outside own customers at every granularity; scenarios S24–S25. Role/customer binding to authenticated identity stated as a production requirement. |
| 16 | major | C5: legal basis not checked | **ACCEPTED** | Each allow rule lists accepted basis codes; empty (D0) or mismatched (D7) bases denied; scenarios S26–S29. |
| 17 | major | C5: decisions not obligatorily logged; checkpoint not published | **ACCEPTED (logging)** / **QUALIFIED (publication)** | `PolicyEngine.request` decides and logs in one fail-closed call; external checkpoint publication stated as a production requirement, not claimed. |
| 18 | major | C5: forged uncheckpointed suffix verifies | **ACCEPTED** | Keyed (HMAC) entries; `verify` reports anchored vs unanchored entries; forged-without-key and keyed-after-checkpoint attacks tested. |

## Fix-verification round — 2026-10-04 15:29 IST

**gpt-6-astra (Addendum v1.1):** 11 resolved, 4 not fully, 0 new blocking; T1 still ranked higher, with a narrower gap.
| # | Remaining point | Decision | Action |
|---|---|---|---|
| 5 | Targeting still optimises a legacy "meaningful use" endpoint | **ACCEPTED** | §4.1: successful, safe access is a rights floor no outreach may worsen; meaningful use is the targeting objective measured beside it; §5 co-primary outcomes. |
| 8 | Privacy composition across quarters | **ACCEPTED** | Release contract: one cumulative budget across all overlapping tables, capped per year; ledger now transactional (see sol 19). |
| 9 | Fraud holds lack time-bounded review/appeal | **ACCEPTED** | §4.3: every hold resolved within a fixed service time and appealable via the bank's grievance channel. |
| 15 | Registration details pending | **ACCEPTED as user action** | Team name/ID and PDF rename under *Needs from user*. |

**gpt-6-sol (Addendum, fix verification):** 2 fixed, 2 not fully, 1 new blocking; all reproductions matched.
| # | Remaining point | Decision | Action |
|---|---|---|---|
| 3 | Seed 29 one woman short of a strict floor; tolerance hid it | **ACCEPTED** | Holdout rounds women down; strict `floor_ok`; regression test; dated note in `c6_v03_results.md`; proposal states H3 with the qualification. |
| 15 | Caller can still assert own-customer scope | **ACCEPTED** | Identity registry (stand-in for authentication): role must match, own-customer scope derived from subject bank; scenarios S30–S31; C5 now 31/31, 95/95; documents call C5 a prototype, not an enforcement boundary. |
| 19 (new, blocking) | Two ledger clients double-spend the budget | **ACCEPTED** | Exclusive file lock + re-read inside the check-and-charge transaction; regression test. |
| minor | Gate validated with 0% holdout vs 10% at deployment | **ACCEPTED** | Gate plan uses the same 10% holdout. |
| minor | Duplicate contacts still scored by maximum true uplift | **ACCEPTED as limitation** | Perfect-linkage sensitivity reported (+0.102); joint-contact model left as future work. |
