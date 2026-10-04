# Landscape — Theme 1: Maternal & Early Childhood Nutrition

> State of the art and what is deployed today, for the gap between what Poshan Tracker / Mission Poshan 2.0 collects and what frontline systems act on. Compiled 4 Oct 2026 (IST). **Rule:** every claim is tied to a source that was opened, by the lead or by a research agent whose notes (with URLs, quotes and access dates) are in [`sources/`](sources/). Items those notes could not verify are marked **UNVERIFIED**.

## 1. The measurable gap (verified)

| Indicator (children) | NFHS-5 survey, 2019–21, under 5 | Poshan Tracker, Nov 2023 | Poshan Tracker, June 2025, 0–5 y |
|---|---|---|---|
| Stunted | **35.5%** [P1] | 37.51% (under 6) [P1] | **37.07%** [P2] |
| Underweight | **32.1%** [P1] (35.8% in NFHS-4) | 17.43% (under 6) [P1] | **15.93%** [P2] |
| Wasted | **19.3%** [P1] (21.0% in NFHS-4) | 6% (under 5) [P1] | **5.46%** [P2] |

- [P1] PIB, MWCD written reply in Rajya Sabha, 20 Dec 2023 (PRID 1988614): NFHS-5 stunting "reduced from 38.4% to 35.5%", wasting "from 21.0% to 19.3%", underweight "from 35.8% to 32.1%". Same reply: in Nov 2023 "around 7.44 crore children under 6 years were measured… 37.51% … stunted, 17.43% … underweight and 6% children under 5 years were found to be wasted. The levels of underweight and wasting are much less than that projected by NFHS 5."
- [P2] Rajya Sabha Unstarred Question 477, answered 23 Jul 2025, Annexure I: "State wise details of malnutrition indicators for children in the age group of 0 - 5 years from Poshan Tracker data for the month of June, 2025": India **37.07 / 5.46 / 15.93** (stunted / wasted / underweight %). Bihar 42.68 / 9.31 / 20.98; Uttar Pradesh 48.83 / 5.04 / 19.96. PDF on disk (`.data/raw/poshan/AU477_annex.pdf`, sha256 `f96a3377…`); 37 state rows in [`sources/L4-poshan-state.csv`](sources/L4-poshan-state.csv).

**Reading.** Height-based stunting agrees between the survey and the administrative system (35.5% vs 37.07%), while the weight-based indicators diverge 2–3.5× (wasting 19.3% vs 5.46%; underweight 32.1% vs 15.93%). Part of this may be real improvement since 2019–21, and age ranges and timing differ. But stunting moved in the *other* direction, so improvement alone can't explain it. The government's own reply names the other candidates: "administrative data have been known to suffer from data gaps due to coverage, measurement, training etc." (Rajya Sabha reply, Dec 2025, as reported by News18; [`R6`](sources/R6-social-signal.md) — secondary, **UNVERIFIED** against the primary text). Today's system **cannot tell which explanation holds, AWC by AWC**. With roughly 6.3 crore children measured a month (PIB, May 2026 [P3]), even a small under-detected share would matter, but the size of that share is **unknown**. The comparison is not age-, time- or denominator-harmonised (see [hostile-judge-01](hostile-judge-01.md)). That inability to decompose the discrepancy is the governance failure we target.

## 2. What the system already collects (Poshan Tracker)
From [`L9`](sources/L9-poshan-tracker.md) (primary: PIB Research factsheet, 8 Jul 2026 [P3]; MWCD page [P4]; Digital India page [P5]):
- Launched 1 Mar 2021 (NeGD/MeitY for MWCD); replaced 11 paper registers; 24 languages [P3, P4].
- A "Poshan Calculator" classifies height/weight/age/sex against WHO standards into stunting, underweight, wasting, SAM/MAM and overweight [P3].
- An IT-enabled home-visit scheduler with **23 structured home visits** (4 in pregnancy, 4 in the first postpartum month, 7 from 2–12 months, 5 from 1–2 y, 3 from 2–3 y) [P3].
- Scale: >8.93 crore beneficiaries registered (May 2026); growth monitoring for **>6.3 crore children aged 0–5 (~94%)** (May 2026); all AWWs have smartphones (₹2,000/yr data) and growth-monitoring devices at each AWC [P3]. Digital India page: 13,96,946 AWCs, 10.12 crore beneficiaries [P5].
- Face Recognition System (FRS) for Take-Home Ration mandatory from **1 Jul 2025**, at registration from 1 Aug 2025 ([`R6`](sources/R6-social-signal.md), news reports of the 30 May 2025 MWCD order; primary circular **UNVERIFIED**). Poshan helpline 1515 since Nov 2025 [P3].

**What's missing:** no cross-check of measurement credibility; no link to the health system's birth weight, illness or immunisation records; no forward-looking risk (classification is point-in-time); dashboards are for review, not task routing. These are derived from the feature lists above. The absence of growth-velocity alerts in the current app is our inference — **UNVERIFIED**.

## 3. Why the gap persists (cited)
1. **Silos even when data exists.** Melghat (Maharashtra): Poshan Tracker recorded 1,82,443 malnourished children statewide (Feb 2025: 30,800 SAM + 1,51,643 MAM), and Village Child Development Centres exist in every gram panchayat. Yet after 65 infant deaths (Jun–Nov 2025) the Bombay High Court called the response "extremely casual"; officials cite departments "operat[ing] in silos" and slow referral (The Hindu explainer [D4], via [`L7`](sources/L7-deployed-india.md)).
2. **Digitising the worker's task list improves process, not outcomes.** ICDS-CAS (CommCare) evaluation, MP and Bihar (Patil et al. 2022, *BMJ Global Health* [D1]): adequate home visits +8.3 pp (MP) / +7.9 pp (Bihar); counselling recall +11.5 / +8.0 pp; growth-monitoring coverage +22 pp in Bihar only; "no effects … on infant and young child feeding practices". **Lesson:** another app isn't the answer. The missing layer is linkage, verification and accountability.
3. **Frontline burden and parallel systems.** Duplicate paper + app registers, device and network failures, and FRS exclusion risk, reported across states. Tamil Nadu workers run both Poshan Tracker and a state ICDS app. Six Anganwadi unions petitioned the Bombay HC against mandatory FRS/OTP for THR (Dec 2025). Evidence strength is graded in [`R6`](sources/R6-social-signal.md); news sources, partly **UNVERIFIED**.
4. **Campaign mode, not continuous governance.** UP's Sambhav Abhiyan targets the 100 highest-stunting AWCs per district (7,500 statewide) for nodal-officer monitoring and monthly District Nutrition Committee review [D2]. Assam's Project Sampoorna (Bongaigaon) uses "buddy mothers" with Google Sheets/WhatsApp tracking; its recovery claims are secondary [D3].
5. **Data siloed across sources.** IFPRI/CGIAR (Menon et al.): of 55 key nutrition interventions only 6 have data across all major sources ([`R6`](sources/R6-social-signal.md); **UNVERIFIED** at primary).

## 4. State of the art by component (summary; details in `sources/`)
- **Growth standards.** WHO 2006 Child Growth Standards (LMS method); WHO publishes LMS and expanded z-score tables. Our engine reproduces WHO's own tables to ≤0.003 z on 87,408 points ([`eval/results/growth_standards.json`](../eval/results/growth_standards.json)). The reference implementation is WHO's `anthro` R package (GPL-3.0, last commit 30 Jan 2026, read for rules only).
- **Epidemiology for early warning** ([`L5`](sources/L5-growth-epi.md), ki consortium, *Nature* 2023; PMC full texts opened):
  - Wasting peaks at birth to 3 months.
  - South Asia: at-birth wasting **18.9%**; cumulative wasting incidence by 24 mo **52.2%**.
  - Pooled: **29.2%** by 24 mo, and 12.9% by 3 mo (47.8% of all ever-wasted).
  - Recovery: **39.0% / 64.7% / 71.1%** of episodes recover within 30/60/90 days, lower in South Asia.
  - So early detection must start in infancy, and repeated faltering is common. Exactly the window monthly growth monitoring covers.
- **Individual-level early warning** ([`L6`](sources/L6-ews-models.md)):
  - True prospective, externally validated child-level prediction is rare. The cleanest example is Ahmed et al., *eLife* 2023 (doi:10.7554/eLife.78491): a prediction rule derived in GEMS (n=7,639) and validated in MAL-ED (1,322 children). It predicts linear-growth faltering after diarrhoea; its AUC is **UNVERIFIED** in our notes.
  - NFHS/DHS cross-sectional ML classifiers are *not* early warning.
  - Population-level: since 7 Apr 2026 Kenya's NDMA integrates ML forecasts of child acute malnutrition into its drought early-warning system (ILRI/Community Jameel press release; PNAS 2025, doi:10.1073/pnas.2416161122).
  - Capacity-constrained targeting of frontline visits: ARMMAN + Google restless-bandit allocation (AAAI 2022/2023; arXiv 2604.07384). Effect sizes **UNVERIFIED**.
- **Anthropometric data quality.** WHO/UNICEF 2019 recommendations; SMART plausibility checks; digit preference; DHS assessments. The dedicated agent failed on infrastructure timeouts, so its sources are not yet opened (**UNVERIFIED**). Our engine uses only standard, transparent statistics (WHO flags, terminal-digit preference, SD of WHZ, longitudinal impossibilities, trajectory realism).
- **Record linkage and privacy** ([`L12`](sources/L12-pprl-dp-audit.md)):
  - Splink (UK MoJ; MIT; ~2.4k★, active; Fellegi–Sunter; "1M records/min", "100M+ via Spark") is the best maintained probabilistic linker.
  - Bloom-filter PPRL (anonlink/clkhash, CSIRO) works but has a small community and known pattern-mining attacks, so keys are kept inside the vault and filters hardened.
  - **No published study on matching Indic-script and transliterated names** was found, so that is open room for us.
  - DP tooling: OpenDP and Tumult Analytics are active.
  - Audit: Trillian is in maintenance mode (use Tessera); FHIR AuditEvent; Open Policy Agent (~12.3k★) for policy-as-code.
- **Law and standards** (verified by agent V1 at primary texts; [`V1-dpdp-verified.md`](sources/V1-dpdp-verified.md)):
  - DPDP Act 2023: s.2(f) "child" = under 18, so every ICDS beneficiary is covered. s.9(1)–(5): verifiable parental consent; no detrimental processing; no tracking, behavioural monitoring or targeted advertising.
  - s.7(b) is *conditional*: it needs prior consent for that benefit or a Centre-notified database. s.7(c) (State function "under any law") fits supervisory and monitoring uses better.
  - s.8(3) accuracy duty when data drive decisions or are disclosed; s.17(2)(b) research only if "not to be used to take any decision specific to a Data Principal".
  - DPDP Rules 2025 (G.S.R. 846(E), 13 Nov 2025): Rule 1 commencement, with Rules 3 and 5–16 in force 18 months after notification, i.e. 13 May 2027. Rule 10 covers verifiable parental consent. Rule 12 + Fourth Schedule: Part A(1) clinical establishments/healthcare professionals (health services to the child); Part B(1) functions "in the interests of a child, under any law"; Part B(2) State benefits to children. Rule 5 + Second Schedule set standards for State processing.
  - Whether the Act's ss.4–17 are already in force is **UNVERIFIED** (secondary trackers cite G.S.R. 843(E)).
  - The statutory ICDS anchor (National Food Security Act 2013 s.5(2), "identified through the local anganwadi") is seen only in secondary text, so it is **UNVERIFIED** at primary.
  - ABDM consent-artefact details are still **UNVERIFIED**.

## 5. What is deployed today
| System / initiative | Owner · scale | What it does | Data → action | Evidence | Where we borrow / beat |
|---|---|---|---|---|---|
| **Poshan Tracker** | MWCD/NeGD · all States/UTs, >8.9 cr beneficiaries [P3] | Registration, growth monitoring with WHO classification, THR/HCM with FRS, 23-visit scheduler | Dashboards; monthly review | Govt factsheet [P3]; admin-vs-survey divergence [P1, P2] | **Borrow:** the data and the AWW app (no new app). **Beat:** add credibility scoring, health linkage, forward risk and SLA-tracked escalation |
| **ICDS-CAS (CommCare)** | MWCD + Dimagi, 2017–21 (replaced by Poshan Tracker) | Worker task lists, home-visit scheduling | Worker-level due lists | Patil et al. 2022 [D1]: process gains, no feeding-practice effect | **Lesson:** worker-side digitisation alone doesn't change outcomes. Accountability above the worker is the missing layer |
| **UP Sambhav Abhiyan** | Govt of UP · 7,500 AWCs (100 per district) [D2] | Annual sprint on highest-stunting AWCs | Nodal officers + monthly District Nutrition Committee | News + official quotes [D2] | **Borrow:** district committee as the escalation sink. **Beat:** continuous, risk-ranked targeting |
| **Assam Project Sampoorna** | Bongaigaon district admin [D3] | Buddy-mother peer support | Google Sheets / WhatsApp | Secondary claims [D3] | **Borrow:** community action loop. **Beat:** verifiable data trail |
| **Melghat VCDCs** | Maharashtra, every GP [D4] | Facility-level SAM monitoring | Siloed departments | HC proceedings via [D4] | Shows data without cross-department escalation fails |
| **Gujarat ICDS MIS** | Govt of Gujarat [D5] | State MIS dashboard | Review | Portal [D5] | State-level analogue |
| **Wadhwani AI Shishu Maapan** | Wadhwani AI · Odisha pilot 2025 [`L6`] | Newborn anthropometry from smartphone video | Capture, not prediction | Product page | Complementary input (better birth weight/length) |
| **Kenya NDMA ML malnutrition forecasts** | NDMA + ILRI/Jameel, Apr 2026 [`L6`] | County-level forecasts of acute malnutrition | Drought EWS bulletins | Press release + PNAS 2025 | Population-level analogue; we add the child-level, capacity-aware layer |
| **ARMMAN + Google (SAHELI)** | India, maternal mHealth [`L6`] | Restless-bandit allocation of limited health-worker calls | Weekly call lists | AAAI papers; effect sizes **UNVERIFIED** | **Borrow:** budgeted allocation under capacity |

International production analogues (Peru's Padrón Nominal with results-based budgeting, Brazil SISVAN, DHIS2 Tracker nutrition modules, WHO SMART Guidelines DAKs) are **UNVERIFIED** tonight; the agent ([`L8`](sources/L8-deployed-global.md)) failed mid-run. Its partial notes are kept.

## 6. Innovation room (what nobody ships yet)
1. **Credibility-weighted surveillance.** No deployed Indian system scores each AWC's measurement credibility and uses it both to target re-measurement and to correct prevalence. This turns the 19.3% vs 5.46% question into a measurable, AWC-level quantity.
2. **Capacity-constrained, reason-coded early warning** on routine monthly growth data linked to health events. Metric: recall of future wasting at a fixed home-visit budget.
3. **Indic-name privacy-preserving linkage** between ICDS and RCH/U-WIN; no published benchmark found.
4. **Decision rights as code:** a purpose-bound access policy with legal-basis citations, a tamper-evident audit trail, and SLA clocks aligned to existing review meetings.

## Sources
- [P1] PIB (MWCD), "Steady improvement in indicators for malnutrition…", 20 Dec 2023, PRID 1988614. https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1988614 (opened by lead, 4 Oct 2026).
- [P2] Rajya Sabha, Unstarred Question No. 477, answered 23.07.2025, MWCD, Annexure I. https://www.sansad.in/getFile/annex/268/AU477_kllCxU.pdf?source=pqars (downloaded and parsed by lead, 4 Oct 2026).
- [P3] PIB Research, "Poshan Tracker: India's Real-Time Nutrition Monitoring Platform", 8 Jul 2026. https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202678915801.pdf (agent L9).
- [P4] MWCD, POSHAN Tracker page. https://www.wcd.gov.in/public/offerings/poshan-tracker (agent L9).
- [P5] Digital India, Poshan Tracker. https://www.digitalindia.gov.in/initiative/poshan-tracker/ (agent L9).
- [D1] Patil SR et al., "Can digitally enabling community health and nutrition workers improve services delivery…", *BMJ Global Health* 2022;6(Suppl 5):e007298. https://gh.bmj.com/content/6/Suppl_5/e007298 (agent L7).
- [D2] Hindustan Times (Lucknow), "Sambhav Abhiyan 5.0…", 2025. https://www.hindustantimes.com/cities/lucknow-news/sambhav-abhiyan-5-0-up-focuses-on-eliminating-malnutrition-reducing-stunting-in-kids-101752606088986.html (agent L7).
- [D3] Indian Masterminds, "Project Sampoorna…". https://indianmasterminds.com/feature-stories-on-bureaucrats-changemakers/project-sampoorna-dr-ms-lakshmi-priya-malnutrition-assam-206636/ (agent L7).
- [D4] The Hindu, "Why do infant deaths persist in … Melghat…". https://www.thehindu.com/sci-tech/health/why-do-infant-deaths-persist-in-the-tribal-dominated-region-of-melghat-in-maharashtra/article70295537.ece (agent L7).
- [D5] Gujarat WCD ICDS portal. https://wcd-icds-new.gujarat.gov.in/ (agent L7).
- ki consortium (Mertens et al., *Nature* 2023, PMC10511327/325/328), Ahmed et al. *eLife* 2023, ILRI 2026, Splink/OPA/Tessera/OpenDP repos: full citations in [`L5`](sources/L5-growth-epi.md), [`L6`](sources/L6-ews-models.md), [`L12`](sources/L12-pprl-dp-audit.md).
