# ADR 001 — Spike components

- **Status:** accepted (v1, 4 Oct 2026 07:45 IST) · revisit after the first pilot-design review and an independent adversarial review (see *Process note*).
- **Deciders:** project lead (india71-t3-finance).
- **Context documents:** [`../components.md`](../components.md), [`../../research/landscape.md`](../../research/landscape.md).

## Context

The measurable gap: inoperative PMJDY accounts rose from 5.94 crore (14.1%, Mar 2021) to 15.09 crore (26.4%, Dec 2025) while the FI-Index rose to 67, and the Ministry told Parliament that inoperative accounts by gender, by rural/semi-urban area, accounts under ₹500, and credit to PMJDY holders are "not centrally maintained" ([landscape §1](../../research/landscape.md)). Two things are missing: **knowing whom to help with scarce outreach**, and **holding implementers accountable for usage, not openings**. Everything else in the architecture uses existing rails and best practice.

## Options (one per candidate spike)

| ID | Component | Idea |
|---|---|---|
| A | C6 Targeting engine | Uplift-based allocation of outreach arms (IVR/SMS, BC visit with re-KYC, assisted UPI 123PAY, small incentive) under budget and equity constraints, with a randomised holdout |
| B | C10 Usage scorecard + attribution (+ C11 DP) | Person-level, gaming-resistant meaningful-usage rates and causal "incremental usage" per district / bank / BC, released with differential privacy into SLBC/DLCC reviews and NSFI monitoring |
| C | C3 Privacy-preserving person linkage | Purpose-scoped pseudonymous tokens + clean-room linkage to count people instead of accounts |
| D | C8 Voice-first last-mile orchestration | Local-language IVR/voice flows into UPI 123PAY and BC task lists |
| E | C2 Meaningful Usage Score | A transparent usage-state machine and 0–100 score replacing "operative/inoperative" |

## Scoring (1–5; evidence in one line each)

| Criterion | A | B | C | D | E |
|---|---|---|---|---|---|
| Impact on judged criteria | 5 — answers sub-question 1 ("identify and prioritise segments") with a model | 5 — answers sub-question 3 (usage accountability) and the "not centrally maintained" finding | 4 — enabler for both; judges value governance | 3 — sub-question 2, but rails already exist | 3 — necessary but simple |
| Novelty vs what is deployed | 4 — outreach today goes to all inoperative accounts ([P2] in landscape) | 4 — forums review openings and totals; no implementer-level causal usage metric found tonight | 3 — clean rooms/tokenisation exist elsewhere | 2 — channels exist (UPI 123PAY, IVR) | 2 |
| Feasibility by 1 Nov (and 18 Dec) on a Mac | 5 — simulator + scikit-learn, running today | 4 — needs simulated gaming and DP; straightforward | 3 — real PSI/TEE adds engineering | 3 — voice demo needs telephony | 5 |
| Measurability (isolated scalar) | 5 — normalised policy value vs oracle | 4 — Spearman ρ with true contribution; DP MAE | 4 — linkage F1 | 2 — completion rate needs field data | 3 — F1 vs simulated truth |
| Demoability at finals | 5 — "same budget, N more people actively banking" | 5 — district dashboard with gaming flags and CIs | 3 — hard to show | 4 — a phone call is vivid | 2 |
| **Total** | **24** | **22** | **17** | **14** | **15** |

## Six Thinking Hats (A and B)

- **White (facts).** Inoperative share 14.1% → 26.4% (Mar 2021 → Dec 2025) [landscape §1]. Existing outreach is blanket: alerts to all accounts about to become inactive and quarterly contact of all inoperative holders [P2]; a nationwide campaign ran Jul–Sep 2025 [P1, P2] — yet the Dec 2025 count was higher than the Jul 2025 count. No account-level data is public, so A and B are evaluated on a labelled synthetic simulator calibrated to the 23% inoperative share. First synthetic run (seed 0, 20,000 persons): status-quo account-level drive captured 4% of the oracle's incremental value above random; dormancy-risk targeting −9% (worse than random); our first uplift model 32%; "best average arm to everyone" 39%.
- **Red (gut; what impresses judges).** "With the same money, reach N more people who will actually use their account — and prove it with a holdout" is memorable. A district scorecard that cannot be gamed by ₹1 deposits answers the "accountability for usage, not enrolment" question head-on. Judges from banks or RBI may distrust black-box ML; explainability and the governance story must lead.
- **Black (risks).** (1) Simulator results depend on assumed effects — they show the *mechanism*, not real impact; a real pilot with a randomised holdout is required. (2) Our first uplift model lost to a simple rule: small pilot arms make per-person uplift noisy (winner's curse). (3) Targeting can look like exclusion ("why did my neighbour get a visit?"); equity constraints and published criteria are needed. (4) Scorecards invite gaming (token credits, account churn) and noise in small units. (5) Legal basis for linking bank, mapper and DBT data must be explicit (DPDP, Aadhaar Act) — UNVERIFIED section-level analysis pending.
- **Yellow (benefits).** Fewer wasted BC visits to duplicates, migrants and the deceased; women and low-literacy holders can be guaranteed a share; outreach learns what works; accountability shifts from counting accounts to counting people who use them.
- **Green (alternatives).** Shrink per-person uplift toward arm averages; hybrid policy (cheap universal nudge + targeted expensive arms); Thompson-sampling bandit over arms per segment; DR-learner; use BC Sakhi presence as an arm modifier; scorecard with synthetic-control comparators.
- **Blue (process).** Build both in the skeleton; run the ratchet loop on A first (scalar exists today); B gets its metric and simulated gaming next; revisit after an independent adversarial review and with the user before the 12 Oct selection memo.

## Thesis → antithesis → synthesis (A, the riskier claim)

- **Thesis.** Dormancy is not persuadability. Ranking accounts by dormancy wastes visits on people who cannot or will not respond; ranking persons by *expected incremental* usage per rupee, under budget and equity constraints, reaches more real users for the same money, and a standing holdout keeps it honest.
- **Antithesis** (lead's adversarial pass — an independent agent could not be run tonight). (i) With realistic pilot sizes, per-person uplift estimates are too noisy to beat simple rules — our own first run shows that. (ii) The gain depends on heterogeneity that we assumed in the simulator; if real effects are homogeneous, a universal cheap nudge is optimal and the model adds complexity and opacity. (iii) Banks will not run a model they cannot explain to an auditor or a Parliament question. (iv) Targeting adds a new exclusion risk.
- **Synthesis.** Make the spike a *policy-learning system*, not a black-box score: (1) always include the universal-nudge and best-average-arm policies as candidates and deploy the model's allocation only where its estimated policy value beats them on held-out pilot data with a confidence bound; (2) shrink uplift toward arm averages and allocate expensive arms by lower confidence bounds; (3) keep a 10% randomised holdout per district; (4) enforce a women's-share floor and publish reason codes per decision; (5) evaluate on the simulator *and* on public uplift benchmarks before any field claim, and present simulator gains strictly as SYNTHETIC.

## First principles

What is scarce? Not accounts (59.09 crore exist) and not rails (UPI, AePS and BCs exist). Scarce are (1) field contacts — a BC visit costs real money and time, while 15.09 crore accounts are inoperative; even at an assumed ₹100 per visit (ASSUMPTION), visiting every inoperative account once would cost about ₹1,509 crore; and (2) trustworthy information about *people*, which today is "not centrally maintained". Hence the two spikes: A allocates the scarce contacts; B produces the missing information and ties incentives to it. C (linkage) is the enabler both need and stays best-practice (keyed tokens in a clean room).

## Decision

- **Spike A = C6 Targeting & Prioritisation Engine** (uplift + budgeted, equity-constrained allocation + holdout). First auto-research loop runs here: metric = normalised policy value on held-out synthetic persons, averaged over seeds.
- **Spike B = C10 Usage Scorecard & Attribution with C11 DP publication.** Metric = Spearman ρ between implementer ranking and true causal contribution under simulated gaming; DP MAE at ε = 1.
- Everything else is best practice behind fixed contracts.

## Consequences

- The proposal leads with governance (who sees what, on what legal basis) and accountability, with targeting as the engine that makes outreach affordable.
- Every result from A and B is labelled SYNTHETIC until a field pilot; the pilot design (randomised, one district) is part of the roadmap.
- Open item: independent adversarial review of this ADR (rubber-duck agent) once sub-agents are available again.

## Process note

Overnight, the playbook's independent adversarial agent and per-component research agents failed on upstream network timeouts; the Supervisor then ordered lean mode (no sub-agents). The antithesis above was therefore written by the lead and must be re-run independently.
