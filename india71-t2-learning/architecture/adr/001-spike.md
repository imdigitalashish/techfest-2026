# ADR 001 — Spike choice: one picture, two loops

- **Status:** Accepted v1 (4 Oct 2026, 05:50 IST). Revisit by 12 Oct after real-data checks and the selection memo.
- **Deciders:** project lead, with an independent adversarial review (`rubber-duck`) and a first-principles review (`First Prinicipals Agent`), both recorded below.
- **Context:** [architecture/components.md](../components.md) defines 12 components with contracts. Most stay best practice; PLAYBOOK §2 asks for 1–2 spike components that carry the innovation and have an isolated scalar metric for auto-research.

## Candidates
| ID | Candidate | Components | What it changes |
|---|---|---|---|
| A | **Classroom action loop** — a few-minute adaptive diagnostic per child → TaRL groups + one activity per group as a WhatsApp / ≤ 3-SMS / IVR "Monday plan" → recheck the same competency in 4–6 weeks | C4 → C7 → C11 (C3 codes) | What a teacher does next week for a specific child |
| B | **Measurement assurance** — a small, rotating, stratified sentinel sample of independent re-tests moderates teacher-administered results; small-area estimation turns them into block numbers with intervals, benchmarked to PARAKH/ASER | C5 + C6 | Whether a block/district number can be believed and acted on |
| C | Small-area estimation alone | C6 | Block numbers with intervals, but still built on unverified inputs |
| D | Allocation optimiser alone | C9 | Where camps/training go, but only as good as its inputs |

## Six Thinking Hats
| Hat | A — classroom loop | B — measurement assurance |
|---|---|---|
| **White** (facts) | The brief's engagement area 2 asks for exactly this; Teaching at the Right Level is the best-evidenced FLN approach (citations: `research/sources/evidence-*.md`); a diagnostic report on its own is a weaker lever than diagnosis plus a concrete grouped activity (to be confirmed against Muralidharan & Sundararaman 2010 in the evidence file). Skeleton numbers: CAT uses ~7.5 of 16 items per child (`components/diagnostics/evaluate.py`). | States already run census-style, mostly teacher-administered FLN assessments (see `research/sources/deployed-states-ngos.md`); national surveys are samples that cannot speak for blocks; inflated official learning data has been documented in India (to be cited from the evidence file — UNVERIFIED until then). |
| **Red** (gut; jury) | A teacher's Monday plan in Hindi on a basic phone is the most persuasive 30 seconds of a finals talk. | "Audit" and "forensics" read as policing teachers; "moderation" reads as professional practice. |
| **Black** (risks) | Content quality and teacher uptake; "another app" fatigue; diagnostic accuracy for children whose home language differs from the medium; a learning effect is not measurable before a pilot. | Surveillance framing and union resistance; Campbell's law moves gaming elsewhere; re-test logistics at national scale (10 % of schools ⇒ 100,000+ visits per round); a simulator can validate itself. |
| **Yellow** (benefits) | Directly changes classroom action; low bandwidth; teacher time per child is measurable now. | Makes every other dashboard trustworthy; gives officials honest intervals; directly addresses the brief's "data governance" lens and engagement areas 1 and 3. |
| **Green** (alternatives) | Use a branching (ASER-style) diagnostic where IRT calibration is missing; recheck items double as the next diagnosis. | Re-tests piggyback on CRC academic-support visits and *are* coaching visits: the CRC re-tests five children, then models the activity with that group. Select schools by *uncertainty and decision value* with a random floor, not by suspicion. |
| **Blue** (process) | Score below; adversarial review; decide; run auto-research where a frozen scalar exists. | Same. |

## Scores (1–5)
| Candidate | Impact on judged criteria | Novelty vs. state of the art | Feasibility by 1 Nov | Measurability (scalar) | Demoability | Total |
|---|---|---|---|---|---|---|
| A classroom loop | 5 | 3 | 5 | 4 | 5 | **22** |
| B measurement assurance | 4 | 4 | 4 | 5 | 3 | **20** |
| C small-area estimation alone | 3 | 3 | 4 | 5 | 3 | 18 |
| D allocation alone | 3 | 2 | 4 | 3 | 3 | 15 |

Novelty for B is provisional: the novelty check (has anyone combined design-based re-test moderation with small-area estimation for learning outcomes?) is in `research/sources/methods-sae-audit.md`.

## Thesis → antithesis → synthesis
**Thesis (lead, 05:15):** make C5 "trust & audit engine" the spike — forensic risk scores, a ~10 % risk-weighted re-test audit, bias correction — because untrusted administrative data is why officials cannot act.

**Antithesis (independent `rubber-duck`, 05:20; verbatim points condensed):**
1. The inflation diagnosis is *asserted, not demonstrated*; disagreement between ASER, PARAKH and state tests may be construct, cohort, language, mode or sampling differences.
2. It is designed as surveillance: risk scores and surprise re-tests imply fraud; honest schools serving harder populations get false suspicion; gaming moves elsewhere; CRCs are not independent.
3. A 10 % national audit is 100,000+ school visits per round; "a few children" saves testing time, not travel, training or supervision; AI reading scores need language- and device-specific validation.
4. On synthetic data the demo validates its own simulator; risk weighting gives unstable weights in small blocks.
5. A better block percentage is not classroom decision support; the binding constraint may be teacher time, multigrade pedagogy, attendance or language.
Best alternative offered: the C3 → C4 → C7 → C11 action loop, measured by minutes per child, expert agreement, plan completion, follow-up coverage and learning movement, broken down by language, SC/ST status, gender and single-teacher schools.

**Synthesis (decision):**
1. **Spike 1 (primary, demo centrepiece) = A, the classroom action loop.** Metric for auto-research: teacher time per child at accuracy parity (C4), plus payload bytes / SMS segments (C7). Learning movement is measured only in a pilot (C11) — we do not claim it from simulation.
2. **Spike 2 (secondary, governance spine) = B, recast as non-punitive *measurement assurance* (moderation).** Changes forced by the antithesis:
   - Sentinel schools are chosen by **uncertainty and decision value with a random floor**, rotating each round — not by suspicion. Forensic features are used only as stratifiers for sampling efficiency.
   - **No school-level trust labels are published.** C12 restricts school-level `TrustAssessment` to the moderation team; officials see block-level calibrated estimates with intervals.
   - Re-tests ride on existing CRC academic-support visits and end with the CRC coaching the group (verification visit = support visit).
   - The budget is a parameter, evaluated at 2.5–20 % of schools; the proposal costs the chosen level explicitly.
   - The simulator results are reported as a **sensitivity analysis across bias processes** (none / uniform / heterogeneous inflation), never as a measured real-world inflation rate. Real-data evidence of disagreement between instruments (ASER vs. PARAKH, state level) is reported separately, with the caveat that it mixes construct and population differences.
   - The question C5/C6 must answer: *does modest external moderation materially improve block estimates and targeting beyond the simple baseline?* If not at realistic budgets, B is dropped to best practice.
3. Both loops share C2 identifiers and C3 competency codes — that shared spine is what makes the teacher's, the block's and the state's pictures consistent (engagement area 1).

## First-principles review (`First Prinicipals Agent`, read 09:47 IST; condensed)
1. **Chain:** present → validly observed → honestly recorded → **owned** (a named person with a lever) → instruction changes (right level, protected time, enough weeks) → independently verified.
2. **Bottleneck = recorded → owned.** A recorded non-reader obligates no one — no owner, deadline, protected time or independent check. Every tier completes its own task (test, upload, review) and the child's day is unchanged. Consistent with our verified evidence: diagnostic feedback alone had no effect; MP school-improvement plans produced compliance with null learning effects; a dedicated TaRL hour worked (`research/sources/evidence-base.md`).
3. **Assumption that fails first:** "the indicator turns green only if the child does." On teacher-reported data, pressure moves the cheapest margin — a click, not a term of teaching. One number cannot serve diagnosis (low stakes) and accountability (high stakes) at once.
4. **Spike advice:** run C5 *as a visit, not a statistic* — re-test a few random children, reconcile the result with the teacher, model one group activity, log it. Minimum viable combination: C5 + C7 + C8 + C11 on a baseline C4, plus a state order protecting a daily level-grouped hour. Keep C5's estimation error as a guardrail, not the goal.
5. **Non-obvious insight — account for children the way a disease-control programme accounts for patients:**
   - **Notify:** every child found below level gets an owner and a group within a fixed window; *finding* a struggling child earns credit.
   - **Cure:** counts only when verified by someone other than the teacher.
   - **Missing cases:** survey-anchored prevalence (C6) × UDISE+ enrolment − notified children = the estimated number of struggling children nobody has notified.
   Prevalence targets ("% NIPUN") punish honesty — each truthfully reported non-reader lowers the score. Notification + verified cure + missing-case estimation makes truthful reporting the dominant strategy and makes *inaction*, not low levels, the visible failure. A cohort register also keeps a child owned after promotion, which a Grade 3 snapshot does not.
   _Citations the agent gave that we have not opened (UNVERIFIED): Aiyar & Bhattacharya (2016) on the block-level "post office" bureaucracy; Berry et al. (2020) on continuous and comprehensive evaluation in Haryana; Johnson & Parrado (2021) comparing NAS 2017 and ASER._

## Synthesis v2 (09:50 IST) — what changes
- **Accountability unit changes from prevalence to cases.** C11 becomes a *learning-case register*: child (pseudonym) → owner → group → start date → recheck date → verified status. Officials' headline indicators: (a) case-finding rate = notified ÷ estimated struggling children (C6 × UDISE+), (b) verified-cure rate (re-tested by a CRC or third party, C5), (c) overdue cases. "% NIPUN" stays an outcome measure, estimated with intervals — not a target any tier self-reports.
- **C5 is run as a visit.** The moderation sample doubles as a cure-verification and missed-case check, ending with the CRC coaching one group (already in synthesis v1).
- **Minimum viable pilot** = C4 (baseline ladder) + C7 + C8 + C11 + C5, plus a state order protecting a daily level-grouped hour; C6 and C9 follow once case data flows.
- **Metrics:** C5's block MAE stays a guardrail; the pilot's primary metrics are case-finding rate, verified-cure rate and time-to-owner.

## Addendum v3 (2026-10-04 16:04 IST) — after the pre-registered test and the hostile-judge review
- **Learning-support record replaces the case/cure register.** The TB-programme analogy and "cure" language are dropped (review issue 16): a time-limited, revisable, institution-owned record with no ability labels, no quotas, no teacher rankings, and a state-order firewall against personnel/progression use. The claim that notification "makes truthful reporting the dominant strategy" is **withdrawn** (issue 17: no incentive analysis supports it). Unmet need is reported only as an uncertain aggregate for planning.
- **Spike 2 measured.** Pre-registered held-out test (`eval/preregistration/2026-10-04-coverage.md`): conservative 90 % intervals (coverage 96.7 %, ±6.0 pp), block MAE 2.16 vs 4.31 pp raw. The interval method changed during development (dev seeds 1–30 only): misclassification correction from a double-assessed subsample, children-weighted HT bias, and a Fay–Herriot model on the reporting bias.
- **C9 allocation demoted.** Pre-registered: moderated numbers do **not** improve camp targeting (and worsen it at a 5 % budget). Allocation is no longer a value claim; moderated numbers inform the existing review process with intervals.
- **Anchoring restricted** to an independent same-construct, same-population, same-term survey (issue 6).

## Consequences
- Auto-research loop 1 runs on C5 first (its frozen evaluator exists: `components/trust_audit/autoresearch/`), loop 2 on C4 (`components/diagnostics/autoresearch/`).
- The proposal leads with the teacher's Monday plan and the child, then shows how the same data, moderated, becomes block decisions.
- C12 policy must deny school-level `TrustAssessment` to every role except the moderation team (auditor) and state; tests enforce it.
