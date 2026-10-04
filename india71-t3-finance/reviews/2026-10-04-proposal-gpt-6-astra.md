# Sakriya: hostile Round-1 proposal review

**Model:** GPT-6 Astra (`gpt-6-astra`). **Effort:** max, the requested PLAYBOOK section 10 review tier.<br>
**Review timestamp:** 2026-10-04 14:25:17 IST, obtained with `TZ=Asia/Kolkata date`.<br>
**Commit reviewed:** `22b6d458b4b7357c74aedbb01245f7aa6fcd0ee0`, after fetching and rebasing onto `origin/main`.<br>
**Artefacts:** `deliverables/round1-proposal.md` and `deliverables/India71_100_[TeamID].pdf` under `india71-t3-finance/`; the specified research, architecture, ADR, preregistration and all eight result JSON files; the T1 proposal at the same commit.<br>
**Jury perspective:** RBI/DFS official, public-sector bank financial-inclusion head, data-protection lawyer and development economist. Advisory findings; the lead decides.

## Scope and first judgement

This is a technical governance architecture, not merely a financial product. It attempts all three Theme 3 sub-questions: targeting, last-mile access and policy accountability. The official brief actually requires **at least one**, not all three. Targeting and accountability are substantially developed; last-mile interoperability mostly names channels rather than specifying bank-owned completion and failure handling.

The PDF passes its existing checker: **6 A4 pages, Arial throughout, 11/12/14 pt, embedded fonts, text inside one-inch margins**. The substantive sections are present, but required team information is absent from the PDF: the renderer removes the Markdown's placeholder team paragraph along with the draft banner. There is no spare seventh page.

The most credible feature is the willingness to ship a transparent rule rather than pretend the learned challenger has passed its deployment gate. The biggest weaknesses are more fundamental than model quality: bank-local reference keys are treated as a ready cross-bank identity rail; the clean-room targeting flow has no established legal basis; and the definition of success can penalise entirely legitimate cash use.

**Length rule for every recommendation below:** replace or remove the named passage, never append a new paragraph. Each replacement must use no more words than its allocated passage; the cuts below are distinct unless explicitly described as a wording substitution. Hyperlink existing citation labels without printing long URLs. Word-neutral edits can still change pagination: the lead must re-render the chosen combination without shrinking fonts or margins.

## Official criterion scores

| Official criterion | Score / 10 | Reason |
|---|---:|---|
| Problem Identification | 7 | A real access-to-usage measurement problem and a recognisable priority community, but inactive accounts are not a count of excluded people. |
| Evidence & Context | 7 | Strong primary-source work and unusually candid synthetic evidence; the Parliament quotation overreaches, and the opening comparison mixes populations and dates. |
| Existing Ecosystem Analysis | 6 | Extensive coverage of existing rails, but misses the June 2025 BC re-KYC amendments and the current NSFI 2025-30 strategy while claiming an overly absolute gap. |
| Proposed Solution | 5 | Understandable component/data-flow architecture and sensible rule-first targeting, undermined by unresolved identity linkage, legal authority and a questionable welfare metric. |
| Feasibility & Implementation Roadmap | 4 | Named organisations are not committed partners; no funded delivery model, powered pilot or production clean-room acceptance gate supports the national timetable. |
| Impact & Scalability | 5 | Outcomes and causal intent are explicit, but benefits, worker safeguards, coverage and scale depend on assumptions not yet established. |

These are diagnostic scores, not an assertion of official criterion weights or a forecast of the shortlist.

## ISSUES

Severity: **blocking** means the proposal cannot honestly be treated as submission/deployment-ready without resolving or explicitly removing the claim; **major** materially weakens validity, safety or feasibility; **minor** is a bounded evidence/presentation defect.

### 1. blocking - A bank's vault Reference Key is not a national person identifier

**Location:** proposal section 4.2 opening; section 5 NPCI ownership; architecture F2; `components/linker/link.py`.

**Evidence:** UIDAI Circular 14/2025, paragraphs 7(a), 7(b), 7(d) and 7(k), requires entity-separated vaults and an entity's reference mapping. It does not guarantee identical references for the same person at different banks or create an NPCI cross-bank token service. HMAC of bank A's reference and HMAC of bank B's different reference remain different. The skeleton substitutes a shared `identity_ref`, thereby assuming away the hard part; missing references become singleton "persons", inflating counts. APB's latest-seeded-bank routing is not a directory of all a person's accounts. UIDAI also expressly disallows hashing Aadhaar numbers as Reference Keys.

**Net-neutral fix:** replace section 4.2's first two sentences with a bank-local first phase and an explicit, unbuilt, separately authorised cross-bank translation/linkage dependency. Require coverage/error reporting and an unlinked-account bucket, not asserted unique-person totals. Replace unqualified "count people" wording with "count resolved customers; report unresolved accounts". Do not repair this with a global Aadhaar hash.

### 2. blocking - The legal boundary is described by recipient, not by lawful processing

**Location:** section 4.2 "Legal fit", diagram and access table; companion architecture F1-F4/legal anchors.

**Evidence:** the diagram sends encrypted account features to a common clean room that links and targets people, then returns named tasks. Saying only the account-holding bank receives the final list does not make that upstream processing bank-internal or lawful. Being a data fiduciary creates responsibilities, not permission. DPDP section 7(b) is conditional State-benefit processing, not a generic bank-profiling licence. Section 17(2)(b) excludes person-specific decisions; Rule 16 and the Second Schedule add standards. Separate HMAC keys and aggregate output do not retroactively authorise collection or linkage. Aadhaar section 29 requires the relevant written-purpose restrictions; mapper seeding consent does not automatically cover this new use.

**Net-neutral fix:** replace the whole "Legal fit" paragraph with a per-flow legal go/no-go: named fiduciary/operator and processor contracts, identified current basis and notice/consent or applicable exception, permitted purpose, retention/deletion, grievance owner and audit. Cite Rule 16/Second Schedule. Reject cross-bank uploads until approved; use bank-local or non-identifying aggregates meanwhile. Keep May 2027 as future DPDP commencement, not evidence of present compliance.

### 3. major - Parliament did not say everything attributed to "not centrally maintained"

**Location:** section 1 second paragraph; section 2 final table row; section 3 item 2; section 6 outcome claim.

**Evidence:** P1's footnote says **range-wise** inoperative-account data is not centrally maintained; its body separately says institutional credit to PMJDY holders is not centrally maintained. The table does not publish a gender split for inoperative accounts, but that is not the quoted statement. P3's non-maintenance statement about women/rural/semi-urban inoperative accounts concerns accounts **closed**, matching the question asked. It does not establish that every gender/area breakdown of the outstanding inoperative stock is unavailable centrally. This distinction matters because the quotation anchors the claimed governance failure.

**Net-neutral fix:** replace the existing quotation-bearing clause and its repeated table/outcome shorthand with: "The cited replies do not publish the needed person-level breakdowns; P1 reports unavailable balance-band/credit data, and P3 unavailable gender/area closure data." Use "not published in these replies" where that is all the evidence shows. Do not spend words repeating the stronger claim elsewhere.

### 4. major - The apparent contradiction is not a demonstrated deterioration in people's banking

**Location:** section 1 opening/gap; section 2 dates; section 3 items 2, 5 and 6.

**Evidence:** PMJDY account-level, two-year administrative status; Findex adult/person-level, one-year survey inactivity; and a national all-finance composite are not equivalent estimands. DBT-purpose exemptions further change the administrative denominator. P3 has an answer date, not a stated observation date. The opening's 42.20-to-59.09 crore comparison is about **40%**, whereas **35%** refers to 42.20-to-57.07 crore. The sources do not establish that the people behind 15.09 crore accounts are predominantly excluded rural women. Nor is "nobody has built it" proved by a missing central table. RBI's current **NSFI 2025-30**, released 1 December 2025, already emphasises effective usage, gender-sensitive inclusion and customer protection.

**Net-neutral fix:** replace the opening paragraph and the absolute "no feedback loop/no agreed sharing pattern" claims with a dated, non-comparable-indicators caveat and a narrower gap: test whether bank-local usage/outreach evidence improves existing NSFI implementation. Preserve the figures in the table rather than repeat them. Map to current NSFI usage/gender/protection objectives; label duplicate accounts as a hypothesis and unmet-need prevalence as unknown.

### 5. major - The score can turn poverty and legitimate cash access into failure

**Location:** section 4.1; expected-impact definition; `components/usage_state/classify.py`, rules R1-R4 and MUS.

**Evidence:** the classifier subtracts a DBT cash-out from customer activity and rewards retained balances, channel diversity and protection products. A person who reliably collects her full benefit in cash to meet immediate needs can be classified pass-through despite receiving exactly the service she wants. A regular single-channel user without a protection product can fail "meaningful" use. Optimising this score can induce unnecessary transactions, product pushing or pressure to retain money. Separately, R1 labels all accounts at 24 months "inoperative" without a DBT-purpose exemption field, despite the proposal correctly recognising the regulatory exemption.

**Net-neutral fix:** replace section 4.1's paragraph with separate regulatory status and analytical usage measures, preserving DBT exemptions, plus holder-chosen successful/safe access and resolved failures. State that cash withdrawal, low balances, one channel and declining products are not failures. Co-design the outcome before the pilot; no benefit, account-service or credit eligibility decision may use the score.

### 6. major - A women's share floor is not protection from exclusion or coercion

**Location:** section 4.3 arms/holdouts; section 5 exclusion mitigation; section 6 beneficiaries and KPIs.

**Evidence:** maximising responsiveness per rupee can repeatedly deprioritise people with the highest barriers. A share among already eligible/reachable women does not cover women absent from the linked data, without private phone access, or unable to leave home. The shipped rule is a lottery, not a guarantee of access; the learned policy's under-budget-coverage branch also bypasses its explicit allocation-floor call. "Grievance channel" names neither an owner nor a remedy. A randomised holdout must not withhold ordinary DBT access, mandatory notices, re-KYC assistance on request or fraud redress.

**Net-neutral fix:** replace section 6's beneficiaries/outcomes/long KPI list, leaving its Scale sentence for issue 13, with a shorter rights-and-outcomes capsule: optional outreach only, standard services for all including holdouts, self-referral/assisted non-phone and non-Aadhaar routes, private channel/time choice, refusal without penalty and bank-owned correction/appeal. Retain successful access, six-month persistence, cost, fraud and subgroup reach; drop speculative national beneficiary characterisation and repeated score KPIs.

### 7. major - Individual BC accountability can become surveillance and unpaid pressure on Sakhis

**Location:** section 4.4 first scorecard sentences; section 4.2 "Bank and its BC" access column.

**Evidence:** an implementer's treatment effect depends on liquidity, network reliability, assigned population and intervention resources, not solely effort. Publishing named BC performance/gaming flags invites punitive comparisons and conversion pressure on women agents. The proposal has no prohibition on pay/disciplinary use, worker appeal, paid co-design or workload cap. The table also appears to grant a bank and its BC the same ledger/KYC access. A named BC is herself potentially a Data Principal: using her performance record for individual sanctions is not rescued by a beneficiary-statistics exemption.

**Net-neutral fix:** replace the scorecard-description sentence and the later "people actively banking" slogan with bank/district diagnostic accountability, resource constraints, capacity-capped tasks, worker correction/appeal and no automatic pay or disciplinary use. Leave the initial holdout-estimation sentence for issue 11. Relabel the existing access cells so a BC receives only assigned contact/action fields, never the bank's full ledger or cross-bank profile.

### 8. major - "Differentially private" needs a release policy, not only a ledger class

**Location:** section 4.4 publisher sentence; architecture F5 and monthly cycle; `components/dp_publisher/dp.py`; `eval/scorecard_eval.py`.

**Evidence:** the prototype rate mechanism assumes each person contributes to one unit. The proposal requests overlapping bank, branch, district, BC, gender and repeated monthly releases. The scorecard evaluation uses separate epsilon-1 ledgers for unit and district releases; that is not a composed system-wide guarantee. The private rate demonstration is not validation of privately published treatment effects and their intervals. Neither small-cell suppression nor purpose keys alone bounds longitudinal or cross-table privacy loss.

**Net-neutral fix:** replace the publisher's repeated list of forums, already shown in the diagram, with a fixed release contract: person-level contribution bounds, one cumulative budget across overlapping releases/time, coarse cells, uncertainty including privacy noise, and denial/pooling on budget exhaustion. Explicitly call the current publisher a demonstration pending disclosure-control review, not an established production privacy guarantee.

### 9. major - The KYC gap is outdated and the fraud gate lacks a service-resolution contract

**Location:** section 3 existing RBI rules and "Reactivation friction"; section 4.3 C7; last-mile path.

**Evidence:** RBI's **12 June 2025** amendments already permit authorised BC facilitation of reactivation/re-KYC. Paragraph 38(a)(iia) specifies no-change/address-only declarations, the authorised e-KYC/physical process, acknowledgement and bank responsibility. The proposal still frames branch/video as the available routes. The 2024 directions additionally require maker-checker activation, notification, processing within three working days of a complete application, and enhanced monitoring for at least six months. A mule-risk flag must not quietly become an indefinite benefit-access block. A source saying MuleHunter is deployed establishes neither this project's access nor its false-positive performance.

**Net-neutral fix:** replace the old RBI/branch-video summary and the C7 deployment-name sentence with the current BC-enabled procedure: bank-owned acknowledgement/activation and failure resolution, lawful fraud escalation with human review, permitted customer notices, applicable service clock and post-reactivation monitoring. Keep biometrics inside authorised authentication rails. Add the amendment to the existing P8 citation rather than a new explanatory paragraph.

### 10. major - "Existing commissions" is not a funded pilot or a BC incentive design

**Location:** section 5 "Owners, within existing mandates" and outreach financing claim.

**Evidence:** no bank, DFS unit, NPCI service or NRLM partner has committed. The plan assigns NPCI a new token-authority role and RBI operating oversight without an agreement. Rs 10 per eligible person is a **synthetic deployment budget**, excluding randomised pilot contacts, bank extraction/integration, travel, training, liquidity, legal review, secure hosting, follow-up and complaints. Commissions for existing transactions do not establish payment for visits to hard-to-reach people or failed contact attempts.

**Net-neutral fix:** replace the Owners paragraph with a compact proposed RACI and funding gate: one partner bank's FI head owns permissions/service/budget; bank contracts pay BC time, travel and attempts, not conversions; holders pay nothing; name the district coordinator and independent evaluator. Require priced fieldwork, integration, legal/security and support lines plus approval before recruitment. Mark DFS/RBI/NPCI/NRLM roles as requested, not committed mandates.

### 11. major - The pilot is not yet a design capable of testing its central decision

**Location:** section 5 Plan; section 4.4 "unbiased monthly effects"; C6 preregistration/results.

**Evidence:** one district and two-to-three banks are a setting, not a sample-size calculation. There is no prespecified minimum effect, baseline, cluster count, attrition allowance, treatment uptake or separately powered model gate. The simulation itself reports wrong arm ranking in 2/10 worlds and zero gate passes with roughly 840 validation people. A 10% no-contact holdout does not automatically identify every arm/segment/implementer effect under adaptive allocation. Monthly reports also cannot immediately reveal a six-month outcome. Individual account randomisation risks cross-account, household and BC spillovers.

**Net-neutral fix:** replace the calendar-only pilot/national rollout sentences with an approval-and-power gate: bank-local recruitment, person/household or BC-cluster assignment as appropriate, standard care, logged assignment probabilities, six-month intention-to-treat analysis, independent outcomes and a separate validation gate. Cut the repeated "pilot size is a design input" sentence. For scale intuition only, a 20%-to-22% outcome improvement at 80% power and two-sided 5% alpha needs about **6,510 independent people per equal-sized arm**, before clustering/attrition; choose actual assumptions with the partner, not this illustration.

### 12. major - One scorecard headline is inaccurate, and "a year" hides independent-row assumptions

**Location:** section 4.4 SYNTHETIC scorecard paragraph; `eval/results/scorecard_spikeB.json`; `eval/scorecard_eval.py:38-58`.

**Evidence:** the reported mean correlation **0.9002** is reproduced, but gamers occupy **23%** of the top 20, versus **21.4%** overall across the five four-quarter runs, not "no more common". One seed has 40% gamers in its top 20 versus 19% overall. This does not establish statistically meaningful enrichment either; it simply does not support the categorical wording. The four-quarter world generates **12,000 independent rows per unit** (`3,000 * quarters`), not repeated measurements of the same 3,000 holders. Enrolments are constructed independently of true contribution, and gaming is injected by design. Thus the ranking exercise does not establish robustness to persistent households, strategic response or field measurement errors.

**Net-neutral fix:** replace that paragraph with a shorter disclosure containing rho 0.90, the independent-row design, 23% versus 21.4%, and "stylised mechanism test, not field or adversarial robustness". In section 4.5, substitute "In these SYNTHETIC worlds" for the equally long "Dormancy is not persuadability" lead-in. Keep the C6 deployment-gate failure and retail-transfer caveats, not the impressive headline alone.

### 13. major - The production and national-scale conclusions contradict the stated maturity

**Location:** section 5 Feasibility opening; section 6 Scale; section 4.2 DEPA paragraph.

**Evidence:** P21 really does say the reference implementation "should not be used in production"; the proposal appropriately discloses this. Its conclusion that every component already runs nationally and scale is not new infrastructure nevertheless overreaches. A regulated cross-bank clean room, identity translation, bank interfaces, attestation/key operations, support contracts and longitudinal private publication are project dependencies, not installed rails. Laptop simulation speed measures none of their approval, security or service readiness. "Banks already hold every input" also ignores cross-bank coverage and the missing authorised translation.

**Net-neutral fix:** replace the Feasibility opening's laptop/maturity assurances and the Scale sentence with readiness conditions: bank-local read-only analysis first; a funded voluntary pilot after legal/data agreements; any cross-bank/state expansion only after audited linkage, hosting/security, interface and field-outcome acceptance. Keep DEPA explicitly optional and experimental. These replace the "not new infrastructure" assurance; issue 11 separately owns the calendar rewrite, so do not count that cut twice.

### 14. minor - Several headline citations cannot be independently followed from the PDF

**Location:** References P4, P18, P22; `research/landscape.md` source/backlog entries.

**Evidence:** P4's exact PIB URL was not recorded in the supporting source list, although it supports several prominent August 2026 totals. The PDF mostly prints source identifiers/domains, not clickable source links. NPCI P18 and PIB P22 returned 403 in this review; that is an access limitation, not proof the claims are false. P19 supports a cumulative deployed cohort, not a current available workforce. The current NSFI document and June 2025 KYC amendments are absent from the citations.

**Net-neutral fix:** hyperlink existing reference labels and existing text, with no visible-length increase. Recover and validate P4's exact primary URL or remove its dependent headline claims; do not replace them with invented figures. Add current amendments/NSFI by replacing superseded shorthand. Preserve P19's deployment-period qualifier and never relabel it active capacity.

### 15. blocking - The renderer omits mandatory team information

**Location:** team-information line; `deliverables/render_html.py` draft-banner `re.sub`; rendered PDF and filename.

**Evidence:** the official brief requires Team Name, Team ID, Institution and Contact Details, and a filename using the actual Team ID. The Markdown's 23-word team line contains placeholders. More seriously, the renderer's multiline draft-banner regex also consumes that following team paragraph: reproduced directly against the source, and the PDF has no team-information block. Filling the Markdown alone will therefore not fix the submission. The filename still literally contains `[TeamID]`. This is an administrative/formatting blocker, not a reason to prefer T1 on substantive merit.

**Net-neutral fix:** narrow banner removal to the blockquote, preserve/fill the team paragraph with verified registration details, and rename the final PDF. Fund the restored block by shortening section 4's 71-word pre-diagram (a)-(d) overview/component-count paragraph, whose content the diagram repeats; cap the restored details to the space saved. Deleting the draft banner cannot fund this: it is already absent from the PDF. Do not invent registration data or shrink fonts/margins.

## Evidence honesty: what should be retained

No field-result fabrication was found. C6's SYNTHETIC labels are conspicuous, its oracle-normalised denominator is defined, the rule is correctly the default, and the retail experiment is explicitly not banking. The raw preregistered outputs match rule **0.38029**, who-only challenger **0.45944**, paired difference **0.07915** with CI **[0.05829, 0.10001]**, and **0/10** deployment-gate passes. Consequently the simulated deployed result is roughly **136**, not 156, additional meaningful-use persons. These are expected simulator outcomes, not observed beneficiaries.

The registration commit `9a092e9` precedes result commit `d540b24`; the specified frozen files show no intervening diff. This supports the recorded local preregistration chronology, not proof of an external registry or the unknowability of prior experiments. Earlier development results openly show a simple baseline beating the original learner. The Hillstrom JSON matches approximately **+2.52/+3.21 responses per 1,000** at 10%/20% contact budgets, with intervals including zero in two of three splits, and a loss at full coverage. These are unusually useful negative findings; keep them.

## Primary-source spot checks

**Method:** "Opened" means readable primary text, not merely HTTP success or a search snippet. The bounded primary-source researcher opened Parliament/APB/BC-Sakhi documents using `curl` plus `pdftotext` when `web_fetch` returned binary PDFs or 403, and checked P5/P6 directly. I separately opened the legal, UIDAI, RBI amendment, NSFI and DEPA sources; MeitY/UIDAI PDFs required the same fallback. No primary-source status below is inferred from the project's previous verification notes.

| Claim | Primary source | Opened? | Matches? |
|---|---|---|---|
| March 2021: 42.20 crore accounts, 5.94 crore inoperative; March 2025: 55.18 and 11.94 | [P1: RS USQ 2636, Annexure II](https://sansad.in/getFile/annex/268/AU2636_2RfYLG.pdf?source=pqars) | Yes, PDF text | Yes. |
| Gender/area inoperative-stock data are expressly "not centrally maintained" | [P1](https://sansad.in/getFile/annex/268/AU2636_2RfYLG.pdf?source=pqars); [P3: LS USQ 1333](https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU1333_viWPuz.pdf?source=pqals) | Yes, both PDF texts | **Not as stated.** P1 concerns range-wise data/credit; P3's gender/area statement concerns closures. |
| 31 July 2025 totals: 560,384,490 accounts and 130,452,845 inoperative; DBT can credit inactive accounts | [P2: LS USQ 4090](https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU4090_LCDFLT.pdf?source=pqals) | Yes, PDF text | Yes; ratio 23.28%, rounding to 23.3%. |
| About 15.09 crore inoperative out of 57.07 crore, "December 2025" | [P3: LS USQ 1333](https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU1333_viWPuz.pdf?source=pqals) | Yes, PDF text | Numbers yes; 8 December is the answer date, not a stated observation date. |
| FI-Index 64.2 to 67.0 in March 2024/2025 | [P5: RBI release 2025-2026/759](https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60875) | Yes | Yes. |
| FI-Index 70.0 for March 2026, rise mainly from Usage | [P6: RBI release 2026-2027/686](https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63164) | Yes | Yes; does not establish a contradiction with the PMJDY series. |
| DBT/scholarship-purpose accounts are exempt from the inoperative stipulation | [P8: RBI/2023-24/105, Annex paragraph 3](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12589&Mode=0) | Yes | Yes; separation is based on account-opening purpose. Paragraph 2.5 separately makes regulatory classification account-specific. |
| Reactivation/re-KYC is essentially branch or video only | [RBI June 2025 activation amendment](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12864&Mode=0); [KYC amendment, paragraph 38(a)(iia)](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12866&Mode=0) | Yes, both | **Outdated/incomplete.** Authorised BC facilitation already exists; ultimate responsibility stays with the bank. |
| Latest-seeded bank receives Aadhaar-based DBT; customer written consent required | [P20: APB SOP v3.0.2, 17 February 2021, note (a), section 2 and Annexure II](https://dbtbharat.gov.in/data/dbt_payments/Standard-Operating-Procedure-of-Aadhaar-Payments-Bridge-(APB).pdf) | Yes, PDF text | Yes. Consent form limits purpose; no authorisation for the proposed unrelated cross-bank profiling/token service was found. This is APB, not every possible DBT payment rail. |
| Section 7(b) State-benefit processing; section 17(2)(b) statistics restriction | [P13: DPDP Act, official MeitY Gazette copy](https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf) | Yes, PDF text after `web_fetch` 403 | Statutory text yes; the proposal's targeting basis remains unestablished. |
| Most substantive DPDP provisions commence around May 2027 | [P14: G.S.R. 843(E), clause (c)](https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf) | Yes, PDF text after `web_fetch` 403 | Yes: eighteen months from Gazette publication. This is phasing, not compliance approval. |
| Statistical exemption has prescribed operational standards | [DPDP Rules 2025, Rule 16 and Second Schedule, G.S.R. 846(E)](https://egazette.gov.in/WriteReadData/2025/267650.pdf) | Yes, PDF text | Yes: lawful purpose, minimisation, accuracy, retention, security and accountability; the State-use limb has additional intimation requirements. |
| No core-biometric sharing; identity-use/disclosure restrictions | [P15: UIDAI-hosted Aadhaar Act, section 29](https://backend.uidai.gov.in/get/files/media/document/2026-06/Aadhaar_Act_2016_as_amended_0.pdf) | Yes, PDF text | Yes; avoiding raw Aadhaar does not itself establish the new linkage's permission. |
| UIDAI mandates vault Reference Keys, therefore cross-bank linking works | [P16: Circular 14/2025, paragraph 7](https://uidai.gov.in/images/Circular-No.14_of-2025.pdf) | Yes, complete PDF text after timeout/resumed download | First half yes; **cross-bank identity equivalence is not supplied**. Entity segregation and the prohibition on Aadhaar hashing are explicit. |
| 65,949 BC Sakhis deployed from FY 2022-23 to June 2025 | [P19: LS USQ 1598, MoRD](https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU1598_DuNizn.pdf?source=pqals) | Yes, PDF text | Yes, cumulative identified/trained/deployed cohort; not verified current active stock. |
| DEPA is a non-production reference implementation | [P21: iSPIRT's own README](https://raw.githubusercontent.com/iSPIRT/depa-training/main/README.md) | Yes | Yes; expressly work-in-progress and not for production. |
| Existing NSFI already covers effective usage, gender and protection | [RBI NSFI 2025-30 release](https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=61712); [official report](https://www.rbi.org.in/Scripts/PublicationReportDetails.aspx?ID=1307) | Yes, release and report opening | Yes to those objectives and 47 action points; no claim here to have audited all action-point metrics. |
| P4 August 2026 PMJDY totals | P4 PIB backgrounder; exact URL absent from the source register | No independent opening this pass | Not independently verified; recover the source URL. |
| 92.6 million AePS cash withdrawals in September 2026 | [P18: NPCI statistics](https://www.npci.org.in/product/aeps/product-statistics) | No: 403 | Not independently verified; not disproved. |
| MuleHunter.AI implemented across banks under the May 2026 MoU | [P22: PIB/MHA release](https://pib.gov.in/PressReleasePage.aspx?PRID=2260277) | No: 403 | Not independently verified this pass; no bank-count or project-access inference is warranted. |

This is a targeted spot-check, not certification of every reference; in particular, Findex's underlying microdata/indicator definitions were not independently re-audited here.

## T1 versus T3: one-theme selection

**I would rank T1, Poshan Setu, above T3 in Round 1 at this commit.** T1 connects a bounded measurement/action problem to existing malnutrition protocols, names who must act and when, separates missing resources from worker accountability, and explicitly prohibits punitive worker use. It admits the non-comparability of its headline datasets and ships a simple rule after its ML and linkage-prediction hypotheses disappointed. T3 has strong primary evidence, the more explicit preregistered allocation experiment and a potentially valuable bank-governance question, but its central cross-bank identity rail and authorisations are assumed, its success metric can misread household welfare, and its national adoption story is substantially less grounded. T1 still has linkage/privacy, sample-size and costing risks and this comparison does not certify its safety or field efficacy; it is nevertheless the more coherent current submission. Keep T1 as the default unless T3 is narrowed to a lawful, voluntary, funded bank-local pilot with a holder-centred outcome.

## Verdict

**Round 1:** do not submit unchanged: **15 issues, 3 blocking** (identity premise, legal boundary, omitted/unfilled team information).<br>
**Substance:** retain the technical-governance framing and honest rule-first evidence; resolve what "person", "meaningful" and "permitted" actually mean before scale claims.<br>
**Selection:** T1 ranks higher now; T3 is a credible reserve only after a narrower bank-local scope and explicit approval, funding and service-protection gates.
