# India @71/100 · Theme 3: Financial inclusion & meaningful banking access — Thought Node

> Journal for `india71-t3-finance/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** RESUMED 2026-10-04 13:53 IST (Supervisor; batch slot). Finishing T3 to its definition of done. T1 is ✅ completed and the default India@71 pick; this project must make an honest case for or against T3.
- **Definition of done (Supervisor, 13:52):** (1) final proposal PDF `deliverables/India71_100_[TeamID].pdf` — ≤ 6 A4 pages, all text ≥ 11 pt, fonts embedded; (2) verify the remaining UNVERIFIED facts at primary sources (browser where fetchers are blocked); (3) evidence honesty — beat the best-arm rule in a **pre-registered** test or ship the transparent rule with the model as a gated challenger; every SYNTHETIC result labelled; numbers rendered from committed results with a doc-drift check (`eval/check_docs.py`); (4) cross-model reviews as child sessions (gpt-6-astra max: hostile judge on the proposal; gpt-6-sol max: code + eval incl. reproducing headline numbers) → `reviews/` + `reviews/ledger.tsv`; (5) final selection memo; push; message "DONE — slot free".
- **Plan (in order):** pre-register C6 v0.2 (transparent rule + gated challenger) test on fresh seeds → run (nice, one heavy job) → `eval/check_docs.py` → browser verification pass → proposal v1.0 + PDF → child-session reviews (≤ 2 at a time) → apply accepted fixes → final memo → DONE.
- **Doing:** this plan; no child sessions yet.
- **Rules in force:** child sessions only (no `task`), ≤ 2 at a time; no `git stash`/`--autostash` (push helper fixed); clock timestamps; heavy jobs `nice -n 10`, one at a time, only when `kern.memorystatus_level` ≥ 30; no GPU; small requests.
- **Needs from user:** (1) Theme choice by 15 Oct (Supervisor default: T1). (2) If T3: team name/ID, up to 4 members, and 3–5 short field conversations (BC agent / BC Sakhi, rural branch manager, Lead District Manager) before 1 Nov.
- **Risks:** account-level results are SYNTHETIC; learned targeting currently trails the best-arm rule (0.33 vs 0.37); NPCI/PIB block automated fetchers.

## Brief → what we must be able to show (Phase 0, 02:55 IST)
Hard constraints: one theme per team, fixed at registration (15 Oct); team ≤4; Round 1 = ≤6 pages A4, 1-inch margins, Arial ≥11 pt, single PDF `India71_100_[Team ID].pdf` via Google Form by 1 Nov; must be a concrete technical architecture (targeting model / interoperable access layer / governance dashboard), not a financial product; original work. Round 2 (16–18 Dec): 10-min talk + 5-min Q&A.

| Judging criterion | What we must show |
|---|---|
| Problem identification | One named gap for one named community, stated as a measurable number (scorecard value vs lived-reality value). |
| Evidence & context | A cited numbers table (PMJDY, inoperative accounts from Parliament answers, FI-Index, Findex 2025, NFHS-5, DBT, NPCI) + our own analysis of real public data. |
| Existing ecosystem | Map of schemes and rails (PMJDY, DBT/APBS/NPCI mapper, BC/BC Sakhi/IPPB, AePS, UPI 123PAY, AA, re-KYC drives, UDGAM, NSFI/FI-Index/SLBC) + an evidenced root-cause tree of why the gap persists. |
| Proposed solution | Architecture diagram + component contracts + data-governance matrix (who sees what, at what granularity, on what legal basis) + working demo. |
| Feasibility & roadmap | Owners per component (DFS, RBI, NPCI, banks, SLBC/LDM, DBT Mission), legal basis, pilot design (randomised, 1 district), timeline, costs (labelled estimates), risk register. |
| Impact & scalability | Evidence-based effect sizes, simulated impact (labelled), KPIs, scale path over existing rails. |

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** The India @71/100 Challenge — Techfest IIT Bombay. Prize pool ₹1,00,000.
- **Official statement:** [`_briefs/india71.pdf`](../_briefs/india71.pdf) (text: [`_briefs/india71.txt`](../_briefs/india71.txt)).
- **Challenge question (verbatim):** "Identify one measurable gap between India's development scorecard and the lived reality of an underserved group (including socially marginalised groups) within one of the three competition themes, and design a solution that could be realistically implemented and scaled in the real world."
- **Round 1 — due 1 Nov:** a proposal of **at most 6 pages** (A4, 1-inch margins, Arial ≥11 pt, single PDF named `India71_100_[Team ID].pdf`, via the official Google Form): team info · problem identification (the gap and the underserved community) · evidence & context · existing-ecosystem analysis (why the gap persists) · proposed solution · expected impact. A **concrete technical architecture** (data pipeline, decision-support model or platform design) is expected — not a policy recommendation alone. No prototype required. Top 10 teams per theme shortlisted on **8 Nov**.
- **Round 2 — 16–18 Dec at IIT Bombay:** 10-min presentation + 5-min jury Q&A covering problem validation & stakeholders, ecosystem analysis, detailed solution, implementation roadmap, feasibility, scalability and impact assessment.
- **Judging:** problem identification · evidence & context · existing-ecosystem analysis · proposed solution · feasibility & implementation roadmap · impact & scalability.
- **Rules:** students, team ≤4 (cross-institute allowed); **one theme per team** (fixed at registration, by 15 Oct); original work.
- **Round-1 deliverable for the morning package:** `deliverables/round1-proposal.md` (fits 6 pages when rendered) + an architecture diagram. A small working demo of the architecture is a bonus that will strengthen the finals.

**Theme 3 — Financial Inclusion & Meaningful Banking Access.** Problem (verbatim): "From a data governance and policy-implementation perspective, design a technologically robust solution that uses existing financial-inclusion data - PMJDY account and transaction status, DBT Mission records, RBI FI-Index indicators - to move beneficiaries from merely holding a formal account to actively and meaningfully using financial services." Engage with at least one of:
1. **Data-driven targeting & governance** — how should dormancy, DBT-linkage and usage data be governed and shared, within applicable RBI/NPCI/DBT Mission data-protection norms, to identify and prioritise specific inactive-account segments for intervention?
2. **Interoperable last-mile infrastructure** — how can Aadhaar-enabled payment systems, UPI and Business Correspondent networks be better integrated with existing account data to reduce friction for low-literacy or rural users?
3. **Policy feedback & accountability** — how should account-activity data feed back into the National Strategy for Financial Inclusion targets so implementers can be held accountable for usage, not just enrolment?

Context from the statement: PMJDY brought over 56 crore people into the formal system, yet roughly a quarter of these accounts remain inactive. The statement expects a concrete technical architecture — "not a new financial product concept alone". Suggested sources: PMJDY dashboards (DFS, Ministry of Finance), the RBI FI-Index, RBI's National Strategy for Financial Inclusion, DBT Bharat dashboards, NPCI UPI/AePS data, the DPDP Act 2023.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Account Aggregator framework (Sahamati) for consented data flows; RBI rules on inoperative accounts and the UDGAM unclaimed-deposits portal.
- Low-literacy rails: UPI 123PAY, voice-based UPI ("Hello! UPI"), Business Correspondent network performance data.
- Uplift modelling for targeted nudges.
- What others ship: bank and fintech reactivation programmes and DPI case studies — find published results.

## Key decisions
- 2026-10-04 — **Gap:** inoperative PMJDY accounts 5.94 crore (14.1%, Mar 2021) → 15.09 crore (26.4%, Dec 2025) while the RBI FI-Index rose to 70.0 (Mar 2026, "mainly on account of uptick in Usage"); gender/rural breakdowns "not centrally maintained" (Parliament answers). Community: rural, low-literacy and women account holders. ([landscape §1](research/landscape.md))
- 2026-10-04 — **Solution name and shape:** *Sakriya*, a usage-data governance, targeting and accountability layer on existing rails; no new financial product. ([components](architecture/components.md))
- 2026-10-04 — **Spikes:** A = C6 targeting engine (uplift, budget, equity, holdout); B = C10 usage scorecard + attribution with C11 DP. ([ADR 001](architecture/adr/001-spike.md))
- 2026-10-04 — **Evaluation data:** real public data for state/district layers; a labelled synthetic simulator (C14) calibrated to the official 23% inoperative share for account-level components. (Assumption: no account-level PMJDY/DBT data is public.)
- 2026-10-04 — **Lean mode** from 06:00 IST on Supervisor order (network saturation): no sub-agents; the ADR antithesis was written by the lead and needs an independent re-run.

- 2026-10-04 — **Legal pattern** (verified texts [P13]–[P16] in `research/verification-law.md`): accountability statistics designed for the DPDP s.17(2)(b) statistics exemption (aggregate only, separate token key, DP); person-level targeting stays with the account-holding bank; identity only via UIDAI Aadhaar Data Vault reference keys, HMAC-ed per purpose.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Usage feature extractor | CBS ledger → `AccountMonth` | bank MIS | — | contract; fed by simulator | feed conformance |
| C2 | Usage-state classifier | `AccountMonth` → `AccountUsage` | RBI inoperative rule | — | **built** (rules v0) | macro-F1 vs truth |
| C3 | Tokeniser + person linker | accounts + identity ref → `PersonUsage` | NPCI mapper | — | **built** (HMAC, purpose-scoped) | pairwise linkage F1 |
| C4 | Regulated clean room | encrypted inputs → approved outputs | DEPA / cloud clean rooms (UNVERIFIED) | — | designed | red-team leaks |
| C5 | Purpose & policy engine + audit | `AccessRequest` → `AccessDecision` | AA consent artefact | — | contract | scenario accuracy |
| C6 | Targeting engine | `PersonUsage` + budget → plan | blanket drives | **A** | **built** (T-learner + Lagrangian allocation) | normalised policy value |
| C7 | Fraud & safety gate | plan + risk → allow/verify/hold | bank AML; MuleHunter.AI (UNVERIFIED) | — | designed | mule recall @1% FPR |
| C8 | Last-mile orchestrator | plan → tasks → events | camps, bulk SMS | — | designed | completions per BC-day |
| C9 | Outcome & experiment service | events + usage → `EffectEstimate` | before/after counts | — | simulated pilot in C14 | effect RMSE, CI coverage |
| C10 | Usage scorecard & attribution | persons + effects → `ScorecardRow` | SLBC enrolment tables | **B** | **built v0** (holdout incremental, EB, gaming flag); ρ 0.90 SYNTHETIC | Spearman ρ under gaming |
| C11 | DP publisher | rows → `DPRelease` | small-cell suppression | — | **built v0** (Laplace, budget ledger, suppression) | MAE at ε = 1 |
| C12 | Dashboards | releases → views | PMJDY reports | — | designed | data latency |
| C13 | Public-data gap mapper | public data → gap rows | national averages | — | **partial** (state inoperative data parsed) | coverage |
| C14 | Simulator (eval only) | config → synthetic world | — | — | **built** | calibration error |

## Selection memo
_First version 4 Oct 2026 07:55 IST; final by 12 Oct. Scores 1–5._
- **Winnability — 4.** The gap rests on the Ministry's own Parliament answers (inoperative share 14.1% → 26.4% while the FI-Index rose; breakdowns "not centrally maintained"), which maps exactly onto the challenge's "scorecard vs lived reality" question; we answer all three sub-questions with a concrete architecture. Risk: a policy jury may reward simpler, ground-validated proposals.
- **Innovation headroom — 4.** Spike A replaces blanket dormancy-first outreach with uplift-based, budget- and equity-constrained allocation with holdouts (SYNTHETIC, 3 seeds, corrected evaluator: status quo captures 4% of achievable gain above random, risk ranking −7%, our learner 33% after one ratchet iteration, best-arm rule 37%, oracle 100%). Spike B turns enrolment counts into person-level, causal, DP-protected usage accountability (SYNTHETIC test with 20% gaming units: Spearman ρ with true contribution 0.90 vs 0.04 for enrolments and 0.16 for account-level operative share).
- **Feasibility — 5.** Round 1 needs only a proposal; the skeleton runs on the Mac; little user time before 1 Nov (review + interviews); finals after the 19–25 Nov exams.
- **Demo strength — 4.** Real state data + a live policy comparison and a district scorecard; weakness: account-level data is synthetic.
- **Fit with the user's strengths — 4.** Large-scale data systems, privacy engineering and ML; confidential computing is close to the user's Microsoft/Azure context.
- **Biggest risk:** account-level claims rest on a simulator and several ecosystem facts are still UNVERIFIED tonight; mitigation: verification pass, public uplift benchmarks, 3–5 field conversations, and pilot design with a randomised holdout.
- **Overall — 4.2** (mean of the five scores). Candid comparison for the one-theme choice: T2 also reports 4.2. T3's edge is a hard, primary-source gap (the Ministry's own Parliament answers) and a governance architecture that answers all three sub-questions; its weakness is that account-level results are SYNTHETIC and several ecosystem facts are still UNVERIFIED. Recommend deciding on 12 Oct after both themes finish their verification passes.
- **One-line pitch:** "Jan Dhan opened 59 crore accounts; one in four now lies unused and the State cannot say whose. Sakriya governs the data banks already hold to find the people behind those accounts, reach them at the least cost, and hold implementers accountable for usage — without a central surveillance database."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:55 IST — Phase 0 done; Phase 1 launched
Read PLAYBOOK, seeded brief and `_briefs/india71.txt`; brief verified against the official text (constraints and the judging→evidence map are in *Brief → what we must be able to show*). Launched 8 background agents: r1 evidence numbers, r2 regulation and governance, r3 last-mile and what is deployed today, r4 intervention evidence and uplift/targeting methods, r5 privacy-preserving computation, r6 practitioner/social signal, r7 NSFI and accountability metrics, d1 real public-data fetcher. Assumption (no user input tonight): the demo uses real public aggregates for the district/state layer and a labelled synthetic simulator for account-level targeting, because no account-level PMJDY/DBT data is public.

### 2026-10-04 03:00–05:40 IST — Component map, contracts and walking skeleton
Wrote `architecture/components.md` (14 components, dependency graph, isolated metric each) and typed pydantic contracts with JSON Schema exports. Built C14 simulator (SYNTHETIC; calibrated so 22.5% of accounts are inoperative vs the official ~23%), C2 usage-state rules, C3 HMAC person linker, C6 targeting engine (T-learner + Lagrangian budgeted allocation with a women's-share floor) and `eval/targeting_eval.py` comparing six policies against an oracle. First run (seed 0, 20,000 persons, SYNTHETIC): normalised policy value status quo 0.04, risk ranking −0.09, uplift 0.32, best-arm-for-all 0.39, oracle 1.0 — dormancy-first outreach wastes most of the budget, but our first learner does not yet beat the simple rule.
All eight research agents and three retries failed at turn 0 on upstream 408/ETIMEDOUT errors; none produced files except a partial leads note from d1 (`eval/public_data/research_sources.md`).

### 2026-10-04 06:05–07:10 IST — Session died on a model 408; resumed on Supervisor message (lean mode)
Supervisor: lean mode (no sub-agents, small requests, push every 30 min). Moved stray root downloads into the gitignored `.data/stray/`.

### 2026-10-04 07:10–07:55 IST — Primary evidence, landscape, ADR, proposal
Opened and parsed three Ministry of Finance Parliament answers (RS USQ 2636, LS USQ 4090, LS USQ 1333) and the PIB "12 Years of PMJDY" backgrounder (27 Aug 2026): inoperative PMJDY accounts 5.94 crore (14.1%, Mar 2021) → 15.09 crore (26.4%, Dec 2025); state-wise table reproduced exactly (`eval/public_data/parse_ls4090.py`). Wrote `research/landscape.md` (with "What is deployed today" and a verification backlog), `architecture/adr/001-spike.md`, `deliverables/round1-proposal.md` (~2,400 words) and `deliverables/architecture.md`. Re-ran the targeting benchmark on 3 seeds single-threaded (load ≈ 110 on the Mac).

### 2026-10-04 07:55–08:00 IST — Tests, a real bug, ratchet loop started
Added contract tests (`tests/test_contracts.py`: simulator, C2, C3 incl. purpose-scoped unlinkability, C6 allocation). They caught a real bug: the women's-share floor only rewarded women and never dropped marginal men, so it could not bind (it never bound in the benchmark, where women already exceeded their eligible share, so the published numbers are unaffected). Fixed with the proper Lagrangian term μ·(female − s); all 5 tests pass. Per-component innovation notes in `research/components/README.md`. Ratchet loop on C6 scaffolded (`components/targeting/autoresearch/`: program, frozen eval, ledger with the 0.3396 baseline); experiment 1 (shrink per-person uplift toward arm means, κ = 0.5) is running locally and is not committed until it wins.

### 2026-10-04 08:02 IST — Ratchet loop, iteration 1 kept
Experiment 1 (shrink per-person uplift toward each arm's pilot average, κ = 0.5): METRIC 0.3396 → 0.3514 (+0.012; seed s.d. 0.040 → 0.020), kept per `program.md` (> 0.01). The simple best-arm rule (0.3835) is still ahead; next: hybrid policy (cheap arm for all + targeted expensive arms) and policy selection by doubly-robust value. Ledger: `components/targeting/autoresearch/results.tsv`.

### 2026-10-04 08:06 IST — FI-Index verified at RBI
Opened RBI press releases 2025-2026/759 (22 Jul 2025: FI-Index 67.0 for March 2025 vs 64.2) and 2026-2027/686 (16 Jul 2026: **70.0 for March 2026**, "mainly on account of uptick in Usage"). Sharpens the gap: the national usage signal improved while inoperative PMJDY accounts rose from 11.94 crore (Mar 2025) to 15.09 crore (Dec 2025 answer). PIB's Aug 2026 backgrounder says "67 in 2026" — we use RBI's figure. Landscape, proposal, ADR updated; weights (Access 35 / Usage 45 / Quality 20) still UNVERIFIED at RBI.

### 2026-10-04 08:10–08:25 IST — Evaluator bug found and fixed; Findex reframes the gap
- **Bug (mine):** the women's-share search in `allocate` stopped at the first feasible μ instead of the smallest, and the evaluator's *oracle* called the editable engine — so engine changes moved the yardstick (experiment 2 showed a spurious 0.59). Fixed: smallest-feasible-μ binary search; the oracle now uses the frozen `eval/frozen_allocate.py`. Re-measured (SYNTHETIC, 3 seeds): T-learner 0.2992 → shrinkage 0.3349 (kept); hybrid 0.3496 rejected (seed s.d. 0.21); best-arm rule 0.3655; status quo 0.0353; risk ranking −0.0734. Earlier ledger rows marked SUPERSEDED; `targeting_baseline.json` removed; proposal table regenerated from `c6_exp1.json`.
- **Findex 2025 (primary data file):** adults with an inactive account fell 27.4% (2021) → 14.3% (2024) while PMJDY account-level inoperativity rose — the accounts-vs-people disagreement is now the core of the problem statement. Who is left behind (share of owners inactive, 2024): women 19.6% vs men 12.6%; poorest 40% 23.2% vs richest 60% 11.6%; rural ≈ urban. Proposal §1–2 and landscape §1 rewritten accordingly.

### 2026-10-04 08:30–09:05 IST — Verification pass, real-RCT check, proposal v0.2 (5 pages)
- Verified at primary: RBI circular RBI/2023-24/105 (inoperative accounts; **DBT/scholarship accounts are exempt from the inoperative flag**, so the flag is not a usage measure); UPI 123PAY modes, AA scale (310 million+ accounts linked) and MuleHunter.AI pilot (via verification agent v1, `research/verification-rails.md`). Still UNVERIFIED: AePS/NPCI mapper/Hello! UPI/BC Sakhi numbers (npci.org.in and pib.gov.in block automated fetchers).
- Real-data check of the C6 learner on the Hillstrom randomised e-mail experiment (64,000 people; `eval/hillstrom_eval.py`): beats "best arm to a random subset" by 2.5–3.2 per 1,000 at 10–20% budgets (CIs include zero in 2 of 3 splits), loses at full coverage → design rule: target *who* when contacts are scarce; personalise *which* cautiously (ratchet backlog item 7).
- **Error fixed:** the morning draft said state inoperative shares range "16.3% (West Bengal) to 39.0% (Goa)"; West Bengal is the lowest only among the 16 large states (Lakshadweep 12.5% overall). Corrected.
- Proposal v0.2: rewritten tighter; rendered A4 PDF (Arial 11 pt, 1-inch margins) = **5 pages**, all text ≥ 11 pt including the diagram (`deliverables/render_html.py`; draft PDF `deliverables/India71_100_DRAFT.pdf`).

### 2026-10-04 09:20–10:05 IST — Spike B measured; law verified; paused
- **Spike B (C10 + C11)** built (`components/scorecard/`, `components/dp_publisher/`) and evaluated in a SYNTHETIC accountability world (`eval/scorecard_eval.py`, 5 seeds, 200 implementer units, 20% gaming via token credits and duplicate accounts → `eval/results/scorecard_spikeB.json`): Spearman ρ with true contribution — enrolments 0.04 (top-20 units are 100% gamers), account-level operative share 0.16 (≈ 50% gamers in the top 20), person meaningful-use rate 0.16, **Sakriya holdout-based incremental 0.71 (1 quarter) → 0.90 (4 quarters)** with gamers at their base rate in the top 20; 95% CI coverage 0.94–0.95. Empirical-Bayes shrinkage toward district means did not help (contribution is not district-structured in this world). The gaming flag caught every gaming unit with 0 false positives — by construction of the simulated gaming; real gaming will be subtler. DP at ε = 1: MAE 0.018 pp per unit (~12,000 persons), 0.002 pp per district; small cells still to test.
- **Law verified** by agent v2 at primary sources (`research/verification-law.md`): DPDP Act ss. 7(b), 8(7), 10, 17(2)(b); commencement G.S.R. 843(E) (substantive provisions ~May 2027); Rules notified 14 Nov 2025; Aadhaar Act s. 29; UIDAI Circular 14 of 2025 (Aadhaar Data Vault + Reference Key). Folded into landscape, proposal §4.2 and `deliverables/architecture.md` (legal-anchor table).
- **Hygiene:** a 09:15 local commit had swept in the law agent's scratch files (`._scratch_*`, incl. a 6 MB PDF) via `git add -A`; caught before push, removed from the unpushed commit, and `india71-t3-finance/.gitignore` now ignores `._scratch*`.
- **09:55 — paused** on the user's decision (Supervisor message). Resume point recorded in *Now*.

### 2026-10-04 13:53 IST — Resumed (Supervisor message)
Batch slot freed; resumed with a five-point definition of done (see *Now*). Removed `--autostash` from my push helper (PLAYBOOK §6 now bans stash).
