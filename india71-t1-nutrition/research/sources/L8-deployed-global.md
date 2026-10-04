# L8 — What Companies/NGOs Ship Today + International Production Analogues

**Compiled for:** India @71/100 Challenge, Theme 1 — Maternal & Early Childhood Nutrition
**Research status:** IN PROGRESS (incremental — appended every 2–3 sources)
**Access date for all sources:** 2026-10-04

---

## 1. Key Findings (draft — will finalize at end)

- **Dimagi/CommCare** built the technical backbone of ICDS's Common Application Software (CAS), later folded into Poshan Tracker — reportedly the world's largest digitally-enabled frontline-worker deployment (600k+ AWWs). *(Source so far: AI-search synthesis citing Dimagi podcast/case studies — original Dimagi case-study page 404'd; needs a directly-opened primary confirmation — flagged UNVERIFIED pending further fetch.)*
- **Welthungerhilfe's Child Growth Monitor (CGM)** is a genuinely open-source (GPL-3.0), actively maintained (pushed 2025-05-05) smartphone-video anthropometry tool — small GitHub footprint (83 stars/18 forks on the main repo) relative to its field profile, split across multiple repos (scanner app, ML, API, tagging tool).
- **Wadhwani AI "Shishu Maapan"** (newborn 0–42 day anthropometry via smartphone video) is live in real Indian government pilots in 2026: Andhra Pradesh (Mangalagiri constituency, 1,000-newborn accuracy pilot, MoU with state Dept of Health & Family Welfare, reported June 2026) and an earlier Daman UT rollout (44→92 ASHAs from mid-2024). This is a concrete, verifiable "data at the point of measurement" pattern directly relevant to our early-warning layer.
- **OpenSRP 2** (Global Good / Ona) — FHIR-native, used in 14 country implementations (incl. 4 national systems), 150M+ patients registered as of June 2023 per its own site — a mature candidate architecture for client-registry + frontline-worker tooling.
- **DHIS2** is positioned by its maintainers as the "backbone for national nutrition information systems" with a UNICEF co-developed Nutrition toolkit covering growth monitoring, CMAM, IYCF, vitamin A campaigns — general platform claim verified directly; specific country-by-country CMAM deployment list still to confirm.

---

## 2. Deployed Table

| System | Owner | Where / Scale | What it does | Evaluation (verbatim) | Status 2026 | Source |
|---|---|---|---|---|---|---|
| Child Growth Monitor (CGM) | Welthungerhilfe (+ Microsoft/Children's Investment Fund Foundation, per prior public reporting — not yet independently re-verified this round) | Open-source; fielded in multiple countries (India pilots reported in earlier press, not re-verified this pass) | "AI-powered mobile and web solution for monitoring child growth and malnutrition. It uses image-based height and weight estimation, stores data on the device to work without internet for remote areas, and shows easy-to-understand growth charts for health workers in the field." Smartphone video scan → ML pose/depth estimation → malnutrition flag. | Repo description only this pass (no published accuracy figure re-verified in this session — prior independent reporting of ~92–97% accuracy claims is **UNVERIFIED** pending direct fetch of childgrowthmonitor.org or peer-reviewed paper) | Actively maintained: last push **2025-05-05**; GPL-3.0 licensed; 21 open issues | [1][2] |
| Shishu Maapan (newborn anthropometry) | Wadhwani AI | India: Daman (UT) — 44 ASHAs onboarded June 2024, 92 ASHAs "to date" (article undated within page, 2025-era); Andhra Pradesh — pilot launched, reported June 8 2026, Mangalagiri constituency (Indira Nagar, Koppuravu Colony, Kaja, Errabalem Urban Health Centres + Pedavadlapudi PHC) | Frontline worker records short smartphone video of newborn (0–42 days); AI model estimates weight, height, head/chest circumference, shoulder measurement — "tamper-proof, real-time" — without physical contact or scale/infantometer equipment. Alerts sent to medical officers if issues detected. | "As part of the pilot project, videos of 1,000 newborns will be recorded to assess the app's accuracy and effectiveness" (AP pilot, results pending as of article date) | AP: pilot stage, state-wide rollout contingent on pilot results, per State Health Minister Satya Kumar Yadav (quoted June 2026). Daman: operational, ASHA-count still growing as of article. | [3][4] |
| OpenSRP 2 | Global Good / Ona (nonprofit) | "14 country implementations (including 4 national systems)" | "Open-source FHIR-native platform designed to support health systems delivering services and collecting data offline in communities and facilities." Includes new Electronic Immunization Registry (EIR) product suite. | "has over 150 million patients registered as of June 2023" | OpenSRP 2 (2023 release) is current/active per own site (fetched 2026-10-04, content undated beyond "June 2023" patient count — no later figure found this pass) | [5] |
| DHIS2 (Nutrition use cases) | University of Oslo HISP / DHIS2 core team, co-developed with UNICEF | Described as "backbone for national nutrition information systems" generally — specific country list NOT yet independently verified this pass | Growth monitoring & promotion, community-based management of acute malnutrition (CMAM), maternal nutrition counseling, IYCF, vitamin A campaigns, nutrition surveillance; combines aggregate indicators + individual (Tracker) patient-level data + geospatial data in one system; integrates with food security/climate data. | No quantitative evaluation figure on this page — general platform description only | Toolkit live and promoted on dhis2.org as of fetch date | [6] |

*(Table will grow as remaining topics — ARMMAN, Khushi Baby, IFPRI POSHAN, Alive & Thrive, Piramal Swasthya, Peru Padrón Nominal, Brazil SISVAN, OpenHIE, WHO SMART DAKs — are verified and appended.)*

---

## 3. Borrow / Beat Analysis for Our Design

*(to be completed once more rows are in — placeholder notes:)*
- CGM + Shishu Maapan both validate the "phone-camera replaces scale/infantometer at the point of measurement" pattern — directly usable as an input layer for an early-warning system, but neither (so far verified) publishes an independent peer-reviewed accuracy figure we can cite with full confidence — **gap to flag**, not necessarily a reason to avoid borrowing the UX pattern.
- OpenSRP's FHIR-native, offline-first, multi-country track record is the strongest *architecture* analogue for a client/beneficiary registry layer feeding an ICDS–health interoperability design — worth examining its data model more closely in a follow-up pass.

---

## 4. UNVERIFIED / Open Questions

- Dimagi/CommCare CAS scale figures (600k AWWs, 100M+ households, Bihar RCT) — sourced only from AI-search synthesis this pass; original Dimagi case-study URL returned 404; podcast page not yet independently opened. **Needs direct re-fetch before final citation.**
- CGM published accuracy/validation numbers (commonly cited ~92–97% in older press) — not independently re-opened this session.
- NurtureNet (Wadhwani AI) paper's specific "3.9% relative error / ~114g MAE" figure — reported via AI-search synthesis attributing it to arXiv:2405.05530; arxiv.org and export.arxiv.org both returned only the title (JS-rendered abstract page), and the PDF fetch timed out — **figure is UNVERIFIED, not independently confirmed from the paper text.**
- ARMMAN mMitra/Kilkari, Khushi Baby, IFPRI POSHAN, Alive & Thrive, Piramal Swasthya, Peru Padrón Nominal, Brazil SISVAN, OpenHIE client registry/MPI, WHO SMART Guidelines DAKs — not yet researched this pass; in progress.

---

## 5. Sources

[1] "Welthungerhilfe/ChildGrowthMonitor" GitHub API (repo metadata), api.github.com, data as of fetch — stargazers_count 83, forks_count 18, license GPL-3.0, created_at 2017-12-28, pushed_at 2025-05-05T13:41:58Z, open_issues_count 21. URL: https://api.github.com/repos/Welthungerhilfe/ChildGrowthMonitor — Accessed 2026-10-04.

[2] "Welthungerhilfe/ChildGrowthMonitor" GitHub repository README. Publisher: Welthungerhilfe (GitHub org). URL: https://github.com/Welthungerhilfe/ChildGrowthMonitor — Accessed 2026-10-04.

[3] "Simplifying Newborn Anthropometry—One Smartphone Video at a Time." Publisher: Wadhwani AI (blog). Date: undated on page (context implies ~2024/2025). URL: https://www.wadhwaniai.org/simplifying-newborn-anthropometry-one-smartphone-video-at-a-time/ — Accessed 2026-10-04.

[4] "Andhra Pradesh Pilots AI-Powered App To Measure Newborn Health Parameters Using Smartphone Videos." Publisher: ETV Bharat. Date: June 8, 2026. URL: https://www.etvbharat.com/en/state/andhra-pradesh-pilots-ai-powered-app-to-measure-newborn-health-parameters-using-smartphone-videos-enn26060803286 — Accessed 2026-10-04.

[5] OpenSRP homepage (redirected from smartregister.org). Publisher: OpenSRP / Global Good. URL: https://opensrp.io/ — Accessed 2026-10-04.

[6] "Nutrition" page. Publisher: DHIS2.org. URL: https://dhis2.org/nutrition/ — Accessed 2026-10-04.
