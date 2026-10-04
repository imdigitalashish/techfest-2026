# L9 — Poshan Tracker: Platform Facts (launch, modules, scale, FRS, integrations) + ICDS-CAS history

**Research status:** IN PROGRESS — incremental draft, appended every 2–3 sources.
**Access date for all sources (unless noted otherwise):** 2026-10-04
**Compiled for:** India @71/100 Challenge, Theme 1 — Maternal & Early Childhood Nutrition (data-governance / early-warning layer plugging into Poshan Tracker)
**Zero-hallucination rule applied:** every claim below was read directly from the cited URL in this session (PDF text extracted via `pdftotext -layout` where the fetch tool returned raw bytes). Anything not independently opened is marked **UNVERIFIED**.

---

## 1. Key Findings

1. **Poshan Tracker launched 1 March 2021** (some official text says "March 2021" without the day), developed/deployed via the **National e-Governance Division (NeGD)** under **MeitY**, rolled out by the **Ministry of Women and Child Development (MWCD/MoWCD)** under **Saksham Anganwadi and Mission Poshan 2.0**. [1][3]
2. It replaced the manual **11 paper registers** AWWs previously maintained — a PIB framing explicitly contrasting "before Poshan Tracker" (11 registers, inconsistent home visits, no authentication, no scheme integration) with the app's "advanced features." [1]
3. Core growth-monitoring logic is a **"Poshan Calculator"**: enters height, weight, age, gender → classifies against **WHO Child Growth Standards** into stunting, underweight, wasting, **SAM/MAM**, and overweight/obesity. [1]
4. **Home-visit scheduling is a defined, numbered module**: "IT-Enabled Home Visit Scheduler" supports **23 structured home visits** with auto-scheduling + age-appropriate counselling prompts: 4 visits during pregnancy, 4 in the first postpartum month, 7 from 2 months–1 year, 5 from 1–2 years, 3 from 2–3 years. [1]
5. **Facial Recognition System (FRS)** is integrated into the platform for "last-mile tracking and service delivery authenticity" (PIB's own framing, July 2026 factsheet) — on top of Aadhaar-based verification "to prevent leakages, eliminate ghost entries." [1] Separately verified elsewhere (R6 file, this repo) that FRS became mandatory for Take-Home Ration (THR) distribution from **1 July 2025** and for new registrations from **1 Aug 2025**, per MWCD circular dated 30 May 2025.
6. **Devices**: "All AWWs equipped with smartphones; internet connectivity charges at ₹2,000 per annum per AWW. Growth Monitoring Devices (GMDs) provided at each AWC." PIB's July 2026 text does not break GMDs down into infantometer/stadiometer/weighing-scale unit counts — **UNVERIFIED at this granularity**, needs a procurement-specific source. [1]
7. **Scale (as of the PIB factsheet, dated 08 July 2026, using May/July 2026 figures)**: nationwide coverage across **all 28 States + 8 UTs**; **>8.93 crore beneficiaries** registered (May 2026); SNP received ≥15 days: **5.5 crore**; SNP received ≥21 days: **5.17 crore**; live monthly DB tracking nutrition indicators for **>7.7 crore children** via Aadhaar-authenticated data (July 2026); growth monitoring done for **>6.3 crore children aged 0–5**, ~94% of registered beneficiaries (May 2026). [1] *Note: this 8.93 crore (May 2026) is LOWER than the 10.12 crore figure reported for Feb 2025 on digitalindia.gov.in — likely reflects de-duplication/re-verification after Aadhaar/FRS e-KYC cleanup, not growth. Flagging as a fact to reconcile, not an error.*
8. Separately, **digitalindia.gov.in** (undated, appears to be a Feb/Mar 2025 snapshot) states **13,96,946 Anganwadi Centres with 10.12 cr beneficiaries registered**. [3]
9. **ECCE content delivery module** (for ages 3–6, under the "Aadharshila" national ECCE curriculum launched March 2024): 249 videos, 190 voice notes, 159 ECCE activity PDFs delivered via the app. [1]
10. **Poshan Helpline**: toll-free **1515**, operating "since November 2025," for grievance registration — reachable via/linked to Poshan Tracker. [1]
11. International recognition claimed by PIB: WHO "cited it as an exemplary nutrition data ecosystem"; UNICEF "appreciated its simplicity and beneficiary tracking features"; showcased at the 2023 G20 Ministerial Conference on Women Empowerment (Chair's Statement recognition); MWCD received the 2024 Prime Minister's Award for Excellence in Public Administration. [1] These attributions are PIB's own claims in a backgrounder — **not independently cross-checked against a WHO/UNICEF primary statement in this session — mark UNVERIFIED pending a WHO/UNICEF-sourced citation.**
12. **wcd.gov.in official page** confirms: rolled out in 2021 to monitor Mission Poshan 2.0 "in near real-time basis"; available in **24 languages** including Hindi and English; digitizes/automates AWW physical registers. [2]

---

## 2. Facts Table

| Fact | Value | Date | Source [n] | Verbatim quote |
|---|---|---|---|---|
| Launch date | 1 March 2021 ("1st March 2021") | reported undated (snapshot ~Feb/Mar 2025) | [3] | "The 'Poshan Tracker' is a mobile-based application rolled out by the Ministry of Women and Child Development, Government of India on 1st March 2021 through the National e-Governance Division (NeGD)" |
| Launch date (alt. phrasing, month-only) | "launched in March 2021" | published 08 Jul 2026 | [1] | "It was launched in March 2021 through the MoWCD and the National e-Governance Division (NeGD), under Saksham Anganwadi and Poshan 2.0." |
| Developer | National e-Governance Division (NeGD) | as above | [1][3] | "...through the National e-Governance Division (NeGD)..." |
| Implementing ministry | Ministry of Women and Child Development (MWCD/MoWCD) | as above | [1][2][3] | "rolled out by the Ministry of Women and Child Development, Government of India" |
| Parent scheme | Saksham Anganwadi and Mission Poshan 2.0 (consolidation of Poshan Abhiyan + Anganwadi Services + Scheme for Adolescent Girls) | "under Budget 2021–22" | [1] | "under Budget 2021–22, three nutrition related schemes - Poshan Abhiyan, Anganwadi Services and Scheme for Adolescent Girls were consolidated under Mission Poshan 2.0 (Mission Saksham Anganwadi and Poshan 2.0)" |
| POSHAN Abhiyaan (parent mission) launch | 8 March 2018 | — | [1] | "Launched on March 8, 2018, it is the Government of India's flagship multi-ministerial mission..." |
| Pre-digitization baseline | 11 manual registers kept by AWWs | — | [1] | "Before Poshan Tracker, Anganwadi Workers had to maintain 11 manual registers. This delayed decision-making and created service gaps." |
| Growth-monitoring classification engine | "Poshan Calculator" — WHO Child Growth Standards; inputs height/weight/age/gender; outputs stunting, underweight, wasting, SAM/MAM, overweight/obesity | — | [1] | "Poshan Calculator: Uses WHO Child Growth Standards to assess height, weight, age and gender, classifying children across stunting, underweight, wasting, SAM/MAM and overweight/obesity for standardised, accurate growth monitoring." |
| Home-visit module | IT-Enabled Home Visit Scheduler, 23 structured visits total, auto-scheduled, age-appropriate counselling prompts | — | [1] | "IT-Enabled Home Visit Scheduler: Supports 23 structured home visits with auto-scheduling and age-appropriate counselling prompts. These include 4 visits during pregnancy, 4 in the first postpartum month, 7 from 2 months to 1 year, 5 from 1–2 years, and 3 from 2–3 years." |
| Beneficiary authentication | Aadhaar-based verification + Facial Recognition System (FRS) | — | [1] | "Aadhaar-Based Verification: Prevents leakages, eliminates ghost entries and ensures benefit delivery only to registered beneficiaries." / "Facial Recognition System (FRS): Integrated for last-mile tracking and service delivery authenticity." |
| ECCE content module | 249 videos, 190 voice notes, 159 ECCE activity PDFs, based on "Aadharshila" curriculum, ages 3–6 | — | [1] | "ECCE Content Delivery: Provides 249 videos, 190 voice notes, and 159 ECCE activity PDFs based on Aadharshila for children aged 3–6 years." |
| Aadharshila curriculum launch | March 2024 | — | [1] | "Aadharshila, launched in March 2024, is the National Curriculum for Early Childhood Care and Education (ECCE) for children aged 3–6 years." |
| Helpline | Toll-free 1515, since November 2025, for grievance registration | since Nov 2025 | [1] | "Poshan Helpline: Toll-free number 1515 (since November 2025) for grievance registration." |
| Devices — smartphones | All AWWs equipped with smartphones; connectivity cost ₹2,000/year/AWW | — | [1] | "Smartphone and Connectivity: All AWWs equipped with smartphones; internet connectivity charges at ₹2,000 per annum per AWW. Growth Monitoring Devices (GMDs) provided at each AWC." |
| Devices — growth monitoring | "Growth Monitoring Devices (GMDs)" provided at each AWC — no unit-type breakdown given in this source | — | [1] | (as above) — **GMD = umbrella term here; infantometer/stadiometer/weighing-scale unit counts NOT given in this source — UNVERIFIED at granular level** |
| Scale — geographic coverage | All 28 States + 8 UTs | as of May 2026 | [1] | "As of May 2026, the Government of India has achieved nationwide coverage of Poshan Tracker across all 28 States and 8 Union Territories." |
| Scale — beneficiaries registered | >8.93 crore | as of May 2026 | [1] | "As of May 2026, the Poshan Tracker registered over 8.93 crore beneficiaries. The platform covers six beneficiary categories across the life cycle..." |
| Scale — SNP ≥15 days | >5.5 crore beneficiaries | May 2026 data | [1] | "over 5.5 crore beneficiaries received SNP for at least 15 days, while 5.17 crore beneficiaries received SNP for at least 21 days" |
| Scale — SNP ≥21 days | 5.17 crore beneficiaries | May 2026 data | [1] | (as above) |
| Scale — children with live nutrition-indicator tracking | >7.7 crore children, Aadhaar-authenticated | as of July 2026 | [1] | "As of July 2026, Poshan Tracker maintained a live monthly database tracking nutrition indicator for over 7.7 crore children using verified Aadhaar-authenticated data." |
| Scale — children growth-monitored (0–5y) | >6.3 crore children, ~94% of registered beneficiaries | as of May 2026 | [1] | "The tracker also enabled growth monitoring for over 6.3 crore children aged 0–5 years, covering nearly 94% of registered beneficiaries as of May 2026." |
| Scale — AWCs + beneficiaries (earlier snapshot) | 13,96,946 Anganwadi Centres; 10.12 cr beneficiaries registered | undated page, consistent with ~Feb/Mar 2025 per cross-source note in R6 (PIB PRID=2117763, 28 Feb 2025) | [3] | "13,96,946 anganwadi Centres with 10.12 cr beneficiaries registered" |
| Languages supported | 24 languages including Hindi and English | — | [2] | "Poshan Tracker is available in 24 languages including Hindi and English." |
| Pre-school module (3–6y) | Brings children together for physical/cognitive/social/emotional/creative development activities in remote/backward areas | — | [4] | "Poshan Tracker helps in effective management of pre-school education activities. In remote and socio-economically backward areas, it brings young children aged 3-6 years together at the Anganwadi Centre, where different activities relating to physical, cognitive, social, emotional, creative development of children" |
| International recognition (PIB claim) | WHO cited as exemplary nutrition data ecosystem; UNICEF praised simplicity/tracking; showcased G20 2023 Ministerial Conference on Women Empowerment; MWCD won 2024 PM's Award for Excellence in Public Administration | 2023 / 2024 | [1] | "The World Health Organization (WHO) cited it as an exemplary nutrition data ecosystem. The United Nations Children's Fund (UNICEF) appreciated its simplicity and beneficiary tracking features for AWWs. In 2023, Poshan Tracker was showcased at the G20 Ministerial Conference on Women Empowerment... In 2024, the Ministry of Women and Child Development received the Prime Minister's Award for Excellence in Public Administration." — **UNVERIFIED against a WHO/UNICEF primary statement; this is PIB's own characterization** |

---

## 3. Data Fields We Can Rely On

| Field | Evidence |
|---|---|
| Height, weight, age, gender (inputs to classification) | [1] "Poshan Calculator: Uses WHO Child Growth Standards to assess height, weight, age and gender..." |
| Output classes: stunting, underweight, wasting, SAM/MAM, overweight/obesity | [1] same line; confirmed independently by AI-search synthesis of wcd.gov.in + PIB July-2026 doc (not yet an independently-opened MUAC cutoff source — MUAC cm thresholds 11.5/12.5 reported only via search-engine synthesis, **UNVERIFIED primary-source-direct**, need user-manual PDF to confirm cutoffs verbatim) |
| Beneficiary categories | [1] "six beneficiary categories across the life cycle, from early childhood and adolescence to pregnancy and motherhood" — exact 6 category labels not enumerated in this source; **UNVERIFIED exact list**, likely = pregnant women, lactating mothers, children 0–3y, children 3–6y, adolescent girls (SAG districts), + one more (out-of-school 11–14y girls under SNP per [1]'s "Did You Know" box on SNP) |
| Home-visit counts by life-stage | [1] 4 (pregnancy) + 4 (first postpartum month) + 7 (2mo–1y) + 5 (1–2y) + 3 (2–3y) = 23 total, explicitly itemized |
| SNP duration tracking | [1] ≥15-day and ≥21-day SNP receipt counts are explicitly tracked/reported fields |
| Aadhaar authentication status per child record | [1] "live monthly database tracking nutrition indicator for over 7.7 crore children using verified Aadhaar-authenticated data" — implies Aadhaar-auth flag is itself a trackable field |
| AWC infrastructure data | [1] "Poshan Tracker captures data on Anganwadi infrastructure, service delivery, beneficiary coverage, and growth monitoring." — infrastructure is a named data category but field-level schema not given in this source |
| Language/localization field | [2] 24 languages supported — implies locale field exists per user/AWC |

---

## 4. Integration Points for Our Layer

*(Section in progress — RCH/U-WIN/ABHA/PMMVY/Mera Ration/DigiLocker integrations not yet confirmed from a primary source opened in this session. Will append after next research pass.)*

- Aadhaar (UIDAI) e-KYC + FRS: **confirmed** — core to beneficiary registration/authentication. [1]
- No RCH, U-WIN, ABHA, PMMVY, Mera Ration, or DigiLocker integration has been confirmed via a directly-opened primary source yet. These remain **UNVERIFIED / NOT YET FOUND** — flagging as the single biggest gap against the brief's integration question. Next step: search wcd.gov.in circulars, PIB press releases in the reference list above (e.g. PRID=2266600, 2251769, 2241721), and PMMVY/ABHA portals for cross-linkage announcements.

---

## 5. UNVERIFIED / Open Questions

- Exact MUAC cutoffs (11.5 cm / 12.5 cm) used by Poshan Tracker's classification — seen only via AI-search synthesis citing wcd.gov.in + a PIB PDF, not yet confirmed by directly reading a user manual or the Poshan Calculator spec itself.
- Breakdown of "Growth Monitoring Devices (GMDs)" into infantometer / stadiometer / weighing-scale unit counts and procurement numbers — not in the PIB July 2026 factsheet; needs a procurement order / tender / Lok Sabha Q&A.
- RCH, U-WIN, ABHA, PMMVY, Mera Ration, DigiLocker integrations — **not yet found in any primary source opened this session.**
- Reconciliation of 8.93 crore (May 2026, PIB) vs 10.12 crore (undated ~Feb 2025, digitalindia.gov.in) beneficiary counts — likely due to e-KYC/FRS de-duplication cleanup, but not explicitly stated as such in any source opened yet.
- The "six beneficiary categories" named in [1] are not individually enumerated in that source.
- WHO/UNICEF/G20 recognition claims — sourced only to PIB's own backgrounder; not cross-checked against a WHO/UNICEF primary statement.
- Public dashboard exact contents (what a citizen sees at poshantracker.in without login) — not yet directly opened in this session (next: fetch poshantracker.in/statistics).
- ICDS-CAS (2017–2021) section — not yet researched in this file (next sources: World Bank PDF, IJCMPH article).
- 2025–2026 "AI features" specifically — not yet found; PIB factsheet describes FRS/Aadhaar/Poshan Calculator as the advanced features but does not use the term "AI" or describe any new ML-based alerting beyond the existing SAM/MAM/stunting classifier.

---

## 6. Sources (newest first)

1. **"Poshan Tracker: India's Real-Time Nutrition Monitoring Platform"** — PIB Research (backgrounder/factsheet hosted on static.pib.gov.in), 08 July 2026. URL: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202678915801.pdf — Accessed 2026-10-04 (fetched as PDF; text extracted locally via `pdftotext -layout` after the web_fetch tool returned raw PDF bytes).
2. **"POSHAN Tracker"** — Ministry of Women and Child Development, official offerings page. URL: https://www.wcd.gov.in/public/offerings/poshan-tracker — Accessed 2026-10-04.
3. **"Poshan Tracker"** — Digital India (MeitY), initiative page. URL: https://www.digitalindia.gov.in/initiative/poshan-tracker/ — Accessed 2026-10-04.
4. **"Poshan Tracker"** — Digital India Corporation. URL: https://dic.gov.in/poshan-tracker/ — Accessed 2026-10-04. (Note: companion page https://dic.gov.in/poshan-tracker-2/ failed to load — transport-level/DNS error — not used.)

