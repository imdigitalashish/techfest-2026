# V3 — Lead-verified primary texts: NFSA 2013, ABDM, CMAM 2023 (4 Oct 2026)

Opened and text-extracted by the lead (pypdf) on 2026-10-04. Files kept in gitignored `.data/raw/`; SHA-256 below for reproducibility.

## National Food Security Act, 2013 (Act No. 20 of 2013) — statutory anchor for ICDS child-malnutrition processing
- Source: Gazette of India Extraordinary, Part II Section 1, No. 29, New Delhi, 10 Sept 2013, copy hosted on a gov.in S3WaaS site: https://cdnbbsr.s3waas.gov.in/s3194cf6c2de8e00c05fcf16c498adc7bf/uploads/2021/08/2021081491-1.pdf (sha256 `1cb641e28994a11bb619fcf06470956347ea4f202d3030e2f95148774b443073`). India Code (indiacode.nic.in) timed out / returned 403 from this network.
- **s.5(1)(a)** (verbatim): "in the case of children in the age group of six months to six years, age appropriate meal, free of charge, through the local anganwadi so as to meet the nutritional standards specified in Schedule II: Provided that for children below the age of six months, exclusive breast feeding shall be promoted;"
- **s.6** "Prevention and management of child malnutrition" (verbatim): "The State Government shall, through the local anganwadi, identify and provide meals, free of charge, to children who suffer from malnutrition, so as to meet the nutritional standards specified in Schedule II."
- **Correction:** secondary sources (web search answers) attribute this to "s.5(2)"; the primary text has it as **s.6**.
- **Use:** the statutory "function under any law" for DPDP Act s.7(c), and "in the interests of a child, under any law" for DPDP Rules 2025 Fourth Schedule Part B(1) (V1 rows 1, 13). Identifying malnourished children through the anganwadi is a *legal duty* of the State — Poshan Setu operationalises it.

## ABDM — consent and exchange
- **Guidelines for Health Information Providers, Health Repository Providers, Health Information Users and Personal Health Records Apps**, ABDM/NHA, version 24 October 2022: https://abdm.gov.in/strapicms/uploads/HIP_HIU_Guidelines_f85df336ec.pdf (sha256 `dd73f59793dac385877d2b78a31b8e39326d8e0c51a1b119248d7128e302c77f`).
  - p.19: "Consent in ABDM is based on the MeITY consent framework … A digital consent artefact defining the purpose of using the data, the duration for which data will be available and document to the HIU is created each time the health records are shared."
  - p.4: "All hospitals, diagnostic centers, clinics, public health programs, telemedicine players, etc. are encouraged to become HIP."
  - p.5: "A large hospital or a public health program like Reproductive and Child Health Programme (RCH) could hold the records of patients in long term storage on premises or in the cloud as per policies/guidelines issued by NHA."
  - p.11: "The HMIS/LMIS interacts with the ABDM ecosystem as HRP (HUI or HIP) using FHIR exchange standards … compliant with at least M2 milestone of ABDM Integration i.e. HIP. In M3 ABDM integration, the HMIS/LMIS acts as a HIU."
- **HIE-CM factsheet**, ABDM: https://abdmbeta.abdm.gov.in/strapicms/uploads/HIE_CM_58b5f555d2.pdf (sha256 `d2c9521887468880d36fa0d96e2724b2b34ca6fa81694c7f24269c88740f3647`): "HIE-CM is a gateway that performs the role of managing consents related to user's personal health data"; architecture lists "Public Health Programs" as both HIP and HIU and a "FHIR implementation guide for ABDM".
- **Not verified** (and therefore not claimed): specific purpose codes (e.g. CAREMGT/PUBHLTH), ABHA for minors, NRCeS IG version.

## CMAM Protocol 2023 — "Protocol for Management of Malnutrition in Children", MWCD + MoHFW, 10 Oct 2023
- https://wcd.gov.in/documents/uploaded/CMAM-Book-10-10-2023%20(1).pdf (24 pp; sha256 `7184077d31fee9ba46901de60e5c6463fc13042c3289268df4993af6c6c1533d`). PDF page numbers:
  - p.20 (Role of AWW): "Share the list of SAM children identified by her with ASHA and ANM within 2 days, to help in timely medical evaluation and referral by ANM."
  - p.8 (Step-3 Medical Assessment): "Every SAM child who passes the appetite test and all SUW children shall be screened for health status by ANM/Medical Officer of PHC within 3-5 days of appetite test at PHC …"
  - p.11 (Step-8): "Every SAM/SUW child shall be visited and mother/caregiver shall be counseled on weekly basis during the first month followed by fortnightly visits. For MAM/MUW children fortnightly visits shall be followed." Referral triggers: "Weight loss for two consecutive weeks", "Failure to gain weight for consecutive two weeks", "Non-recovery after three months in the care program".
  - p.22 (District Administration): "The District Administration shall review the progress every month. Weekly review on a dedicated day may be organized at village/urban ward level."
- Applied in `components/action_router/protocol.yaml` v0.2.0 (official steps cite these pages; our own rules are labelled DESIGN).
