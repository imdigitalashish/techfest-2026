# India @71/100 · Theme 3: Financial inclusion & meaningful banking access — Thought Node

> Journal for `india71-t3-finance/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** DEMO (resumed 2026-10-04 22:22 IST, Supervisor; PLAYBOOK §11). Round-1 package is done (proposal PDF, reviews, memo — see Log 15:20).
- **Definition of done (§11 + Supervisor 22:21):** `demo/run.sh` one command, offline, first visual ≤ 60 s, CPU only; **opens on REAL data** (state-wise inoperative PMJDY tiles from Lok Sabha USQ 4090, verified FI-Index and AePS facts) and only then a labelled SYNTHETIC one-bank drill-down; baseline side by side; at least one judge knob; every on-screen number from committed results or live committed code; the "crazy" element; `demo/SCRIPT.md` (3-min talk track); `demo/fallback/`; `demo/smoke.sh`; one gpt-6-astra demo review in `reviews/` + `ledger.tsv`; lead verifies from a clean checkout → "DEMO DONE".
- **Plan:** spawn ONE demo-builder child session → it proposes the crazy element (Supervisor's suggestion: "try to break it" — DP ledger refuses a double-spend, a BC cannot see another bank's customer, the gate refuses the smarter challenger, women's floor as a hard constraint) → I approve → it builds → gpt-6-astra demo review (2nd child) → fixes → clean-checkout verification → DEMO DONE.
- **Doing:** spawning the builder (plan mode for the approval gate, then autopilot for the build).
- **Rules:** ≤ 2 child sessions; CPU only; `nice -n 10` + memory guard (start ≥ 30, pause < 25); clock timestamps; no stash.
- **Needs from user:** unchanged (theme choice by 15 Oct — recommendation T1; if T3: team details, partner bank, field conversations).
- **Risks:** C7 fraud gate and C8 outreach exist only as designs — the demo must either build labelled prototypes or not show them as working; simulation must never look like field evidence.

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

- 2026-10-04 — **C6 ships a transparent default rule; the learned model is a gated challenger** ([ADR 002](architecture/adr/002-transparent-default-gated-challenger.md)); pre-registered SYNTHETIC test: challenger +0.079 (95% CI 0.058–0.100) over the rule, 10/10 seeds; gate never deployed it (pilot too small).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Usage feature extractor | CBS ledger → `AccountMonth` | bank MIS | — | contract; fed by simulator | feed conformance |
| C2 | Usage-state classifier | `AccountMonth` → `AccountUsage` | RBI inoperative rule | — | **built** (behavioural `no_use_24m` vs legal `regulatory_inoperative`, DBT-purpose exemption) | macro-F1 vs truth |
| C3 | Tokeniser + person linker | accounts + identity ref → `PersonUsage` | NPCI mapper | — | **built** (HMAC, purpose-scoped) | pairwise linkage F1 |
| C4 | Regulated clean room | encrypted inputs → approved outputs | DEPA / cloud clean rooms (UNVERIFIED) | — | designed | red-team leaks |
| C5 | Purpose & policy engine + audit | `AccessRequest` → `AccessDecision` | AA consent artefact | — | **prototype v0.3** (31/31 scenarios, 0 false allows; 95/95 log attacks; identity registry, basis codes, derived own-customer scope, decide-and-log) | scenario accuracy |
| C6 | Targeting engine | `PersonUsage` + budget → plan | blanket drives | **A** | **v0.3** (rule default + gated challenger; registered: +0.086 [0.057, 0.115], H1–H3 pass; SYNTHETIC) | share of reference gain |
| C7 | Fraud & safety gate | plan + risk → allow/verify/hold | bank AML; MuleHunter.AI [P12, P22] | — | **prototype** (rules only; demo) | mule recall @1% FPR |
| C8 | Last-mile orchestrator | plan → tasks → events | camps, bulk SMS | — | **prototype** (tasks + per-BC cap ASSUMPTION; demo) | completions per BC-day |
| C9 | Outcome & experiment service | events + usage → `EffectEstimate` | before/after counts | — | simulated pilot in C14 | effect RMSE, CI coverage |
| C10 | Usage scorecard & attribution | persons + effects → `ScorecardRow` | SLBC enrolment tables | **B** | **built v0** (holdout incremental, insufficient-data status, no BC-level release); ρ 0.90 SYNTHETIC, IID stylised | Spearman ρ under gaming |
| C11 | DP publisher | rows → `DPRelease` | small-cell suppression | — | **built v0.3** (secret noise; locked, persistent, composed ledger) | MAE at ε = 1 |
| C12 | Dashboards | releases → views | PMJDY reports | — | designed | data latency |
| C13 | Public-data gap mapper | public data → gap rows | national averages | — | **partial** (state inoperative data parsed) | coverage |
| C14 | Simulator (eval only) | config → synthetic world | — | — | **built** | calibration error |

## Selection memo (FINAL — 2026-10-04 15:14 IST; theme decision 12 Oct, registration by 15 Oct)
_Honest case for or against T3 against T1 (✅ completed, 4.2/5, the default pick). Scores 1–5, one line of evidence each._
- **Winnability — 3.5/5.** The gap is primary-sourced and is a *data-governance* gap — the theme's own framing:
  - inoperative PMJDY accounts rose from 14.1% to 26.4% (Parliament answers);
  - DBT-purpose accounts are exempt from RBI's flag;
  - the NPCI mapper routes DBT to the last-seeded bank;
  - breakdowns are "not centrally maintained".
  But the hostile judge (gpt-6-astra) scored v1.0 at 7/7/6/5/4/5 out of 10 on the six criteria and ranked **T1 higher**. The fixes (bank-local first, explicit legal gates, rights capsule) make v1.1 narrower and safer, but it has not been re-reviewed.
- **Innovation headroom — 4/5.** Transparent targeting rule with a learned challenger behind a gate; after the code review, a corrected pre-registered test (SYNTHETIC, seeds 20–29) gave challenger − rule = +0.086 (95% CI 0.057–0.115, 9/10 worlds), rule − best-arm-only = +0.16, budgets and holdout held and the floor passed the registered check (a strict re-check found one world one woman short — rounding, fixed); the gate certified the challenger in 1/10 worlds. Usage accountability resists gaming in a stylised test (ρ 0.90 vs 0.04 for enrolment counts, SYNTHETIC). C5 policy engine: 31/31 governance scenarios, 0 false allows, 95/95 log attacks detected — a tested prototype, not an enforcement boundary (scenarios written with the rules: fidelity, not legality).
- **Feasibility by the deadline — 5/5.** The final-format PDF exists today and its checks pass. Round 1 needs no more user time beyond team details and optional field conversations.
- **Demo strength at finals — 3/5.**
  - Have: real state-level and Findex analyses, reproducible command-line evaluations, the registered tests.
  - Missing: a dashboard UI; all account-level evidence is SYNTHETIC.
  - T1's end-to-end demo is stronger today.
- **Fit with the user's strengths — 4/5.** Data systems, privacy engineering, causal ML; Azure confidential computing for a later clean-room phase.
- **Overall — 3.9/5** (mean of the five) vs **T1 4.2**.
- **Biggest risk:** the institutional ask. A partner bank must own the pilot, and cross-bank person counts need an identity-translation service nobody has authorised. Jurors may also read targeting as exclusion.
- **Recommendation: keep T1.** T3 is a credible reserve if the user prefers finance and can secure a partner bank and real (consented, bank-internal) data before 1 Nov.
- **One-line pitch:** "Jan Dhan counts 15 crore inoperative accounts but cannot say whose they are. Sakriya starts inside each bank: it counts customers, not accounts, sends scarce field visits where they change behaviour, and holds banks and districts to usage, not enrolment — with person lists never leaving the bank."

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

### 2026-10-04 13:55–14:13 IST — Pre-registered test, verification pass, proposal v1.0, reviews launched
- **C6 v0.2** (`components/targeting/policy_v02.py`): transparent default rule + learned two-stage challengers + IPW gate. Dev seeds 0–2 showed the losses came from unspent budget and noisy per-person *arm* choice; a "who-only" challenger (rule fixes the arm, model picks whom) beat the rule on all 3 dev seeds. **Pre-registered** at 14:00 IST (`eval/preregistration/c6_v02.md`, pushed as `9a092e9` before the run), run on fresh seeds 10–19 (SYNTHETIC): **H1 PASS** challenger_who − rule = +0.079 (95% CI 0.058–0.100, p = 6×10⁻⁶, 10/10); **H2 PASS** rule − best-arm-only = +0.092; gate passed 0/10 (~840 validation persons); rule collapsed in 2/10 worlds (pilot ranked arms wrongly). Results: `eval/preregistration/c6_v02_results.md`; decision: ADR 002.
- **Verified at primary sources** (browser where fetchers were blocked; closed afterwards): NPCI AePS cash withdrawals 92.64 million in Sept 2026 [P18]; NPCI mapper — DBT to the latest-seeded bank, seeding only with written informed consent (APB SOP v3.0.2) [P20]; 65,949 BC Sakhis deployed FY 2022-23–June 2025 (LS USQ 1598) [P19]; MuleHunter.AI "implemented across banks" + I4C MoU (PIB 12 May 2026) [P22] — bank count still UNVERIFIED; FI-Index weights 35/45/20 and 97 indicators (RBI PR 2021-2022/70) [P17] — **this exposed a PIB error I had carried: "53.9 in 2018" is RBI's March 2021 value; corrected**; DEPA CCR is a reference implementation "not for production" (GitHub) [P21]. Hello! UPI stays UNVERIFIED (NPCI URLs now 404).
- **Proposal v1.0**: targeting rewritten (rule default, gated challenger, pre-registered evidence, pilot-sizing caution), verified rails and DEPA maturity added; numbers rendered from committed results; **`eval/check_docs.py` 23/23** (it caught a real rounding drift: UP 27.5% vs 27.6%); final PDF `deliverables/India71_100_[TeamID].pdf` **PASS** via `deliverables/check_pdf.py` (6 A4 pages, Arial only — ₹ replaced by "Rs" and the Devanagari name glossed because Arial lacks those glyphs — every glyph ≥ 11 pt, 6/6 fonts embedded, 1-inch margins). 8/8 tests pass.
- **Reviews launched** as child sessions: gpt-6-sol (code, eval, reproduction) and gpt-6-astra (hostile judge).

### 2026-10-04 14:20 IST — C5 policy engine built (closing a design-only gap)
The proposal described a purpose/policy engine with a hash-chained audit log that existed only as a contract. Built v0 (`components/policy_engine/engine.py`): deny-by-default allow rules and explicit denials, each citing a verified source (Aadhaar Act s.29, UIDAI ADV, DPDP s.17(2)(b) + Rules r.16, RBI/2023-24/105), and 22 scenarios from the governance matrix (`scenarios.json`). Result (`eval/policy_engine_eval.py` → `eval/results/policy_engine.json`): 22/22 correct, 0 false allows. Caveat recorded in the file: the scenarios were written alongside the rules, so this shows the engine implements the published matrix, not that the matrix is lawful. The tamper test caught a real gap: a hash chain alone missed deletion of the newest entry (64/65). Fixed with a published checkpoint (length + head hash) → 65/65. Also verified the DPDP Rules 2025 (G.S.R. 846(E)) rule 16 + Second Schedule standards for the statistics exemption [P23]. check_docs 24/24; 9/9 tests.

### 14:32–15:14 IST — Cross-model reviews, fixes, corrected pre-registration, proposal v1.1
- **gpt-6-astra (hostile judge, max):** 15 issues, 3 blocking — cross-bank identity premise (UIDAI vaults are entity-segregated; Aadhaar hashing banned as reference keys — I verified para 7(a), 7(k)), legal boundary described by recipient, and my renderer silently dropping the team block. Scores 7/7/6/5/4/5 of 10; **ranks T1 above T3**. All accepted (PDF rename rejected: no Team ID yet).
- **gpt-6-sol (code + eval, max):** reproduced every headline number exactly; 18 issues, 4 blocking — v0.2 challenger ≠ its registered description in seeds 12/15; DP noise invertible (public seed); women's floor off on the deployable rule; C5 customer-scope bypass. All accepted (BC task cap deferred; checkpoint publication qualified).
- **Fixes:** C2 behavioural vs legal status; observable proxies with error; PMJDY cohort/calibration; C6 v0.3 (identical plans except whom to upgrade, stratified floors, holdout, same-model gate, cheapest-not-harmful stage 1 after dev showed small-pilot collapses); C11 secret noise + composed persistent ledger; C10 insufficient-data status; C5 v0.2 (basis codes, scope at all granularities, no BC-level tables, decide-and-log, HMAC chain, anchored/unanchored verification); reference allocator replaces "oracle".
- **Corrected pre-registration** 14:57 IST (`c6_v03.md`, pushed `28c80bb` before the run), seeds 20–29, 50k persons, 30% pilot: H1 +0.086 (0.057–0.115, 9/10), H2 +0.161, H3 pass, gate 1/10, perfect-linkage +0.102 (`c6_v03_results.md`). v0.2 results keep a dated caveat.
- **Proposal v1.1** (bank-local phase 1, per-flow legal table, two measures not one label, rights capsule, RACI + gates + power calc 6,507/arm, NSFI 2025-30, June 2025 BC re-KYC) generated from committed results; PDF PASS. Verified new sources: RBI/2025-26/51 and /52, NSFI 2025-30, PIB backgrounder URL, UIDAI 7(a)/7(k).

### 15:20–15:29 IST — Fix-verification round; final package
- **gpt-6-astra re-review:** 11/15 resolved, 4 partial, 0 new blocking; T1 still ranked higher (narrower gap). Partial 5/8/9 fixed in text (rights floor vs targeting objective; annual DP cap; time-bounded, appealable fraud holds).
- **gpt-6-sol re-review:** reproduced v0.3 seeds 20–22 exactly; found H3 strict-floor shortfall (seed 29, one woman — holdout rounding; every available woman was treated), caller-asserted own-customer scope in C5, and a NEW blocking DP-ledger double-spend across clients. All fixed after the run (not re-run, per registration): holdout rounding + strict `floor_ok`; C5 identity registry (31/31, 95/95; now called a prototype); ledger lock + re-read transaction; gate holdout aligned. Dated note in `c6_v03_results.md`; decisions and ledger updated.
- **Final:** proposal v1.1 regenerated (28/28 drift checks), PDF PASS (6 pp, Arial only, ≥ 11 pt, embedded), 17/17 tests. Selection memo final: T3 3.9/5 vs T1 4.2 → **recommend T1**.

### 2026-10-04 22:22 IST — Demo phase started (Supervisor)
Read PLAYBOOK §11. Inbox empty. Plan: one demo-builder child session (proposal → my approval → build), then a gpt-6-astra demo review, clean-checkout verification, DEMO DONE.

### 2026-10-04 22:54 IST — Demo plan approved (child session "T3 demo builder")
Crazy element: **"Try to break Sakriya"**, a live red-team console against the committed code.
- (A) A BC Sakhi claims another bank's customer: C5 refuses with D5 and logs it; erasing the log breaks the HMAC seal.
- (B) "One more statistic": the C11 ledger refuses it; two forums racing for the last ε, exactly one wins; the spend persists across restarts.
- (C) "Ship the smarter model": +0.086 [0.057, 0.115], but certified in 1/10 worlds, so the rule ships. A point-estimate toggle would ship it in 4/10, including world 23 where it was worse (I re-derived 4/10 and loose 0.488 vs gated 0.469 vs rule 0.462).
- (D, optional) Scorecard gaming: ρ 0.04 vs 0.90.
Screens: REAL tile grid first (USQ 4090) → SYNTHETIC registered results plus a women's-floor knob → one person end to end, with C7/C8 as labelled PROTOTYPES → live/replay attacks. Offline page; stdlib backend only for live attacks; replay from file://.
My corrections: screen-1 headline says "as accounts, not people" instead of "nobody can say whose"; bank-local honesty (registered worlds link across banks, a Phase-2 assumption; the drill-down and funnel are same-bank); RBI's FI-Index dates (53.9 = Mar 2021); no "exactly" without a computed equality; no browser download over 200 MB; ASSUMPTION labels on the C7/C8 values.
Note: I used plan mode for the approval gate and then switched the builder to autopilot (the Supervisor asked for autopilot; plan mode only enforces the "approve before build" rule).
