# ADR 001: Spike components

- **Status:** accepted (first version, 4 Oct 2026 08:00 IST). Revisit by 12 Oct with real-data feedback.
- **Context:** The theme asks for a "technologically robust" data-governance and decision-support layer. Judges score problem, evidence, ecosystem, solution, feasibility and impact. Our verified gap: Poshan Tracker reports **5.46%** wasting (June 2025, 0–5 y) against **19.3%** in NFHS-5, while stunting agrees (37.07% vs 35.5%) ([landscape §1](../../research/landscape.md)). Most components should be best practice (WHO z-scores, Fellegi–Sunter linkage, policy-as-code, hash-chained audit). One or two spikes carry the innovation.

## Candidates (scored 1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by 1 Nov | Scalar metric | Demoable | Total |
|---|---|---|---|---|---|---|
| **A. Credibility engine** (AWC/worker-level measurement credibility from routine data; credibility-weighted prevalence; targeted re-measurement) | 5: speaks directly to the 19.3 vs 5.46 gap | 4: survey DQ tools exist (SMART, WHO/UNICEF 2019), but none at AWC level, longitudinally, on admin data | 5: built tonight | 5: AUROC vs synthetic truth; prevalence bias | 5 | **24** |
| **B. Capacity-constrained early warning** (90-day incident-wasting risk + reason codes, top-k per AWC) | 5: "flag before, not after" is the theme's own wording | 3: child-level early warning is rare ([L6](../../research/sources/L6-ews-models.md)), but risk models are familiar to judges | 4 | 5: recall@capacity | 5 | **22** |
| C. Indic-name PPRL linkage (ICDS ↔ RCH/U-WIN) | 4: interoperability, sub-area 1 | 4: no Indic benchmark found ([L12](../../research/sources/L12-pprl-dp-audit.md)) | 4: synthetic F1 0.968 tonight | 5: pairwise F1 | 3: less visual | 20 |
| D. Decision-rights-as-code (policy gate + SLA escalation + audit) | 4: sub-areas 2 and 3 | 2: standard patterns (OPA, hash chains) | 5 | 4 | 4 | 19 |
| E. DP aggregate publication | 2 | 3 | 4 | 5 | 2 | 16 |

## Six Thinking Hats (on A + B together)
- **White (facts):** Stunting agrees between survey and admin data; weight-based indicators diverge 2–3.5× [P1, P2]. ki cohorts: South Asia at-birth wasting 18.9%, 52.2% cumulative incidence by 24 mo, 71.1% of episodes recover within 90 days ([L5](../../research/sources/L5-growth-epi.md)). ICDS-CAS improved process but not feeding practices (Patil 2022).
- **Red (gut, judges):** "Your data says 5%, the survey says 19%; we can tell you *which Anganwadis* to trust, and which children to see this week." That is memorable and fits a 10-minute pitch.
- **Black (risks):**
  - The synthetic validation may flatter us; the real fabrication pattern is unknown.
  - Credibility scores could be used punitively against AWWs and drive more falsification.
  - A risk model could miss migrant children who are never measured.
  - Without Poshan Tracker microdata, every metric is simulated.
- **Yellow (benefits):** A works on data the state already has, needs no new hardware and makes every downstream number more trustworthy. B converts monthly weighing into a weekly, capacity-sized action list.
- **Green (alternatives):** Smartphone anthropometry (Wadhwani AI) to reduce measurement error at source. Complementary, not ours. Random independent re-measurement audits as ground truth: we fold this into A as the "remeasure_sample" action, which also generates labels.
- **Blue (process):** Build A first (done tonight); B on 5 Oct on the same simulator; ratchet loops on both frozen evals; seek real data via a state partnership as a Round-2 item.

## Thesis → antithesis → synthesis
- **Thesis:** The binding constraint isn't missing data but *untrusted* and *unlinked* data. A credibility engine plus a capacity-aware early-warning list is the smallest addition that turns Poshan Tracker from retrospective reporting into weekly action.
- **Antithesis** (written by the lead playing adversary; an independent adversarial agent review is pending because the overnight infrastructure blocked sub-agents):
  - "Measurement error is a training and equipment problem; statistics can't fix a bad scale."
  - "Scoring workers will be resented by unions already protesting FRS."
  - "A 90-day risk model on simulated data is a toy."
- **Synthesis:**
  - (1) Credibility is used for *supportive supervision and re-measurement*, never for pay or punishment. It is scored at AWC level for the LS, not published by name. Its first action is an equipment check.
  - (2) Re-measurement of a random sample creates the ground truth that both A and B need. Validation therefore becomes part of the operating model, not an afterthought.
  - (3) B is pitched with its metric and its honest synthetic label, plus a pilot evaluation design (stepped-wedge by sector) for real data.

## First principles
What must be true for a child to be helped *before* SAM? (a) A measurement that reflects reality; (b) a signal that reaches someone with capacity to act; (c) an owner and a deadline. Poshan Tracker supplies the measurement step but not its credibility. Dashboards supply the signal, but not sized to capacity. Neither supplies (c). A addresses (a), B addresses (b), and C6/C7 address (c).

## Decision
**Spikes: A (credibility engine) and B (capacity-constrained early warning).** C–E stay best practice. A already has a frozen evaluator ([`components/credibility_engine/eval.py`](../../components/credibility_engine/eval.py)); its baseline is synthetic AUROC 0.694 for copy-forward AWCs and 1.0 for any non-good worker, and it is the first auto-research loop target. B gets a frozen evaluator next (recall@capacity), with the "no weight gain in 2 months" rule as its baseline.

## Consequences
- We need a re-measurement protocol (LS samples 10 children per flagged AWC) in the proposal.
- Real-data validation needs a state partner. This is listed under *Needs from user*.
- Legal-basis citations were verified on 4 Oct 2026 (V1, V3); the children's-data regime commences 13 May 2027 (G.S.R. 843(E)). See ADR 002 for the legal go/no-go.
