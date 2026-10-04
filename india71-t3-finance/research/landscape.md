# Landscape — Financial inclusion: from holding an account to using it (India @71/100, Theme 3)

Last updated 2026-10-04 07:30 IST · Lead: india71-t3-finance session.

**How to read this file.** Every number carries a source. **[P]** = primary source opened on 2026-10-04 (local copy in the gitignored `.cache/src/` or `.data/`). **[S]** = secondary source (news) seen in search results tonight, not yet checked against the primary — treat as **UNVERIFIED** until the primary is opened. **[L]** = lead only (named programme or method we know of but did not open tonight) — **UNVERIFIED**. Overnight, most research sub-agents failed on network timeouts (see the thought node), so this version rests on fewer, harder sources; the verification backlog is at the end.

## 1. The measurable gap (scorecard vs lived reality)

The scorecard says inclusion is rising; the ledger says usage is falling.

| Indicator | Earlier | Latest | Source |
|---|---|---|---|
| PMJDY accounts | 42.20 crore (Mar 2021) | 59.09 crore (19 Aug 2026) | [P1] Annexure-II; [P4] |
| RBI Financial Inclusion Index | 43.4 (Mar 2017), 53.9 (Mar 2021) [P17]; 64.2 (Mar 2024) | 67.0 (Mar 2025) → **70.0 (Mar 2026)**, rise "mainly on account of uptick in Usage" | [P5], [P6], [P17] |
| **Inoperative PMJDY accounts** | **5.94 crore = 14.1% (Mar 2021)** | **15.09 crore = 26.4% of 57.07 crore (Lok Sabha answer, 8 Dec 2025)** | [P1] Annexure-II; [P3] |

Inoperative-account series from the Ministry of Finance's own Parliament answers ([`eval/public_data/derived/pmjdy_inoperative_trend.csv`](../eval/public_data/derived/pmjdy_inoperative_trend.csv)):

| As on | Accounts (crore) | Women's accounts (crore) | Inoperative (crore) | Inoperative share | Source |
|---|---|---|---|---|---|
| Mar 2021 | 42.20 | 23.38 | 5.94 | 14.1% | [P1] |
| Mar 2022 | 45.06 | 25.08 | 6.57 | 14.6% | [P1] |
| Mar 2023 | 48.65 | 27.05 | 9.45 | 19.4% | [P1] |
| Mar 2024 | 51.95 | 28.90 | 10.21 | 19.7% | [P1] |
| Mar 2025 | 55.18 | 30.75 | 11.94 | 21.6% | [P1] |
| 31 Jul 2025 | 56.04 | — | 13.05 | 23.3% | [P2] |
| answered 8 Dec 2025 | 57.07 | — | 15.09 | 26.4% | [P3] |

Accounts grew 35% (42.20 → 57.07 crore) while inoperative accounts grew 154% (5.94 → 15.09 crore). Over FY 2025-26 RBI reported that the FI-Index rose to 70.0 "mainly on account of uptick in Usage" [P6], while inoperative PMJDY accounts went from 11.94 crore (Mar 2025) to 15.09 crore (Dec 2025 answer) [P1, P3]. (The FI-Index covers all financial services nationally, so the two are not like-for-like — which is exactly the problem: the national usage signal cannot see Jan Dhan holders.) Note: PIB's Aug 2026 backgrounder [P4] says "67 in 2026", whereas RBI's own March 2026 value is 70.0 [P6]; we use RBI's figures. Caveat: the definition wording differs between answers — [P2] cites RBI's 2009 guideline ("no transactions in the account for over a period of two years"), [P3] says "no customer induced transactions ... over a period of two years" — and [P3] does not state the as-of date of its counts. Part of the late-2025 jump may be definitional; we present the series as reported.

**The governance half of the gap.** Asked in Parliament, the Ministry said the following are *not centrally maintained*: gender-wise inoperative accounts and range-wise inoperative data [P1, footnote to Annexure-II]; institutional credit extended to PMJDY holders [P1]; inoperative accounts closed, by women and by rural/semi-urban area, and the number of accounts holding less than ₹500 [P3]. The State cannot currently say *who* is excluded — so it cannot target them or hold anyone accountable for reaching them.

**State variation** (31 Jul 2025, [P2], parsed to [`pmjdy_inoperative_by_state_2025-07-31.csv`](../eval/public_data/derived/pmjdy_inoperative_by_state_2025-07-31.csv); totals reproduce the annexure exactly: 56,03,84,490 accounts, 13,04,52,845 inoperative). Largest counts: Uttar Pradesh 2.75 crore (27.5%), Bihar 1.39 crore (21.5%), Madhya Pradesh 1.07 crore (23.4%), West Bengal 0.88 crore (16.3%), Maharashtra 0.81 crore (22.0%). Highest shares: Goa 39.0%, Dadra & Nagar Haveli and Daman & Diu 36.1%, Telangana 32.5%, Chandigarh 32.3%, Sikkim 32.2%.

**Who.** Women hold 55.8% of PMJDY accounts (31.24 of 55.98 crore, 25 Jul 2025) [P1] and 32.92 of 59.09 crore (55.7%) on 19 Aug 2026 [P4]. Rural and semi-urban areas hold 45.95 crore of 59.09 crore accounts (77.8%; urban/metro 13.14 crore) [P4]. In March 2025, 22.86 crore women's and 20.04 crore men's PMJDY accounts were in the "below ₹2,500" balance band [P1 Annexure-I; the header reads "₹ in crore" but the bands sum to the account totals, so we read them as numbers of accounts in crore — flagged].

**Depth of use today** [P1, P4]: deposits ₹3,16,514 crore (19 Aug 2026; ≈ ₹5,356 per account, derived); 41.29 crore RuPay cards issued; overdraft availed by 35,99,662 holders (≈ 0.64% of accounts, derived) with ₹393.02 crore outstanding (Mar 2025).

**Person-level view — the two lenses disagree** [P7] (World Bank Global Findex 2025 data file; India rows in [`findex2025_india_account_inactive.csv`](../eval/public_data/derived/findex2025_india_account_inactive.csv)). Adults (15+) with an *inactive* account (no deposit or withdrawal in the past year): **27.4% in 2021 → 14.3% in 2024** (35.4% → 16.1% of account owners, derived), while account ownership rose 77.5% → 89.0%. So the *survey, person-level* lens shows inactivity halving while the *administrative, account-level* PMJDY lens shows the inoperative share rising (14.1% → 26.4%). The likely reconciliation — people using one account while older Jan Dhan accounts lapse — cannot be tested with administrative data that counts accounts, not people. **Who is left behind (2024, share of account owners with an inactive account, derived):** women 19.6% vs men 12.6%; poorest 40% 23.2% vs richest 60% 11.6%; primary education or less 19.1% vs secondary or more 10.2%; out of the labour force 20.9% vs in it 13.0%; rural 16.0% ≈ urban 16.2%. India's 14.3% of adults compares with 11.8% for South Asia and 6.1% for developing economies [P7].

## 2. Existing ecosystem and why the gap persists

What is in place (verified tonight from the Ministry's answers [P1–P3]):
- **RBI's revised instructions (in force since 1 Apr 2024)** [P8]: an account is inoperative if there are no "customer induced transactions" for over two years; banks must review at least annually accounts with no customer-induced transaction for over a year, alert holders by letter/e-mail/SMS that the account will become inoperative within the next year and that fresh KYC will then be needed, and trace holders (or nominees/legal heirs) when letters bounce; KYC for reactivation must be accepted at all branches, including non-home branches, and through V-CIP; no charges for activation and no minimum-balance penalties on inoperative accounts; transactions in reactivated accounts are monitored to reduce fraud. **Crucially, accounts opened to receive DBT or scholarships must be segregated in core banking "so that the stipulation of 'inoperative' account is not applicable to these accounts"** [P8, Annex para 3] — the official inoperative flag is blind, by design, to unused DBT accounts.
- **Rules.** An account is inoperative after two years without (customer-induced) transactions; unclaimed balances move to RBI's DEA Fund after ten years; an inoperative account can be reactivated at any time by completing KYC under the Master Direction – KYC 2016 [P3].
- **Alerts.** Banks inform holders by letter, e-mail or SMS before an account becomes inactive and contact holders of inoperative accounts quarterly [P2].
- **DBT keeps flowing.** DBT benefits are credited even to inactive accounts [P2] — so a benefit can land in an account its owner cannot or does not use.
- **Campaigns.** A Gram Panchayat-level saturation campaign ran 1 Jul – 30 Sep 2025 with re-KYC of inactive PMJDY accounts as a key focus [P1, P2]; financial literacy through 2,421 RBI Centres for Financial Literacy (31 Mar 2025), monthly rural-branch camps and Financial Literacy Week [P1].
- **Products attached to the account:** RuPay card with accident cover (₹1 lakh; ₹2 lakh for accounts opened after Aug 2018), overdraft up to ₹10,000 per household, DBT, PMJJBY, PMSBY, APY, MUDRA eligibility [P4].

**Legal ground rules (verified [P13]–[P16]; interpretation is ours, pending legal review).**
- *Statistics vs decisions.* The DPDP Act does not apply to processing "necessary for research, archiving or statistical purposes if the personal data is not to be used to take any decision specific to a Data Principal", subject to prescribed standards [P13 s.17(2)(b)]. Accountability statistics can therefore be designed to fit this exemption; **person-level targeting cannot** (it is a decision about a person) and needs its own basis — in our design it stays with the account-holding bank, the data fiduciary for its own customers.
- *State benefits.* The State may process personal data to provide a subsidy, benefit or service "as may be prescribed" where the person consented earlier or the data sits in a notified State database [P13 s.7(b)] — a possible anchor for DBT-side data, to be examined.
- *Timing.* The DPDP Rules were notified on 14 Nov 2025; the Act's substantive provisions (incl. ss. 3–17) come into force 18 months after the 13 Nov 2025 commencement notification, i.e. from about May 2027 (derived) [P14] — before any state roll-out of our design.
- *Identity.* Core biometrics may never be shared; other identity information only as the Aadhaar Act and its regulations allow, and requesting entities may not use it beyond the purposes stated in writing [P15 s.29]. UIDAI requires every requesting entity to keep Aadhaar numbers only in an Aadhaar Data Vault and to use a *Reference Key* in all business systems [P16]. **Our linkage therefore uses only reference keys, HMAC-ed per purpose — never Aadhaar numbers.**

Why the gap persists — root-cause tree (evidence status in brackets):
0. **The official flag is not a usage measure.** "Inoperative" is a fraud-control and unclaimed-deposit status; DBT/scholarship accounts are exempted from it [P8], so the very beneficiaries the theme targets can be invisible in inoperative statistics, and a DBT account that is credited and immediately emptied counts as "operative".
1. **Measurement counts accounts, not people, and enrolment, not use.** Key breakdowns are "not centrally maintained" [P1, P3]; review forums therefore see openings and totals. Usage enters the national scorecard only through the composite FI-Index [P5, P6] (Usage weight 45% per [S] ET/BusinessLine — UNVERIFIED at RBI), which is national, not district- or implementer-level [L].
2. **One-size outreach.** Alerts and campaigns go to every inoperative account [P2]. Many inoperative accounts belong to people who use another account (duplicates), have migrated, or have died — reactivating those wastes visits; meanwhile persuadable users get the same SMS as everyone else. (Mechanism plausible; share **UNVERIFIED** — no public data; our simulator makes the assumption explicit.)
3. **KYC friction, now partly addressed.** Reactivation needs KYC [P3, P8]; since 12 Jun 2025 authorised BCs may facilitate re-KYC with electronic self-declarations after biometric e-KYC [P24, P25] — but each bank must operationalise it, and the hardest-to-reach holders are the last to benefit.
4. **DBT as pass-through.** Benefits land and are withdrawn in cash, so accounts are "active" without meaningful use (no saving, insurance, digital payment) [mechanism; magnitude **UNVERIFIED** — needs bank data].
5. **Safety.** Reactivated dormant accounts can be abused as mule accounts; MHA's I4C and RBI Innovation Hub signed an MoU (May 2026) to feed I4C's Suspect Registry into "MuleHunter.ai™ implemented across banks" [P22]. A reactivation drive without a fraud gate creates risk.
6. **Data-sharing uncertainty.** Linking bank, NPCI-mapper and DBT data touches the DPDP Act 2023 and the Aadhaar Act [P13–P16]; the rules allow a workable pattern (aggregate statistics vs bank-held person decisions; reference keys only), but no actor has built it, so each keeps its silo.

## 3. What is deployed today

| Who | What | Status | Evidence |
|---|---|---|---|
| DFS, Ministry of Finance | PMJDY: BSBD accounts, RuPay, OD, DBT eligibility, Jan Suraksha linkage | Production, 59.09 crore accounts (19 Aug 2026) | [P4] |
| DFS + banks | Gram Panchayat saturation campaign incl. re-KYC of inactive PMJDY accounts, 1 Jul – 30 Sep 2025 | Ran; outcome numbers not opened tonight | [P1, P2] |
| Banks | Pre-inoperative alerts; quarterly contact of inoperative holders (letter/e-mail/SMS) | Production | [P2] |
| RBI | Inoperative-account regime: annual review, alerts, tracing, KYC at any branch or V-CIP, no activation charges, DBT/scholarship accounts exempt, reactivated-account monitoring | Production since 1 Apr 2024 | [P8] |
| RBI | DEA Fund (unclaimed deposits after 10 years); KYC-based reactivation | Production | [P3] |
| RBI | FI-Index (national composite, 0–100), first published Aug 2021 | Annual; 70.0 for March 2026 | [P5, P6] |
| RBI | 2,421 Centres for Financial Literacy | Production (31 Mar 2025) | [P1] |
| NPCI / RBI | UPI 123PAY — UPI for feature phones via app, missed call, IVR and proximity sound (launched with the DigiSaathi helpline) | Production; usage numbers not found on the opened page | [P10] |
| NPCI | AePS (Aadhaar-enabled Payment System) — cash withdrawals 92.64 million (₹22,642.99 crore) in Sept 2026, 99.99 million in Aug 2026 | Production | [P18] |
| NPCI / DBT Mission | APB system and NPCI mapper: Aadhaar-based DBT goes to the bank with the **latest seeding mandate** ("all the subsidies will be routed to that bank only"); seeding needs the customer's written, informed consent | Production (SOP v3.0.2, Feb 2021) | [P20] |
| NPCI | "Hello! UPI" conversational voice payments | Production per news (Sept 2023) | [L] UNVERIFIED — NPCI's 2026 site restructure returns 404 for the old press-release and white-paper URLs |
| MoRD / DAY-NRLM | BC Sakhi — SHG women as Business Correspondent agents (deposits, credit, remittances, pensions and scholarships, MGNREGA wages, insurance/pension enrolment) | 65,949 deployed FY 2022-23 to June 2025 | [P19] |
| India Post Payments Bank | Doorstep banking, AePS | Production | [L] UNVERIFIED (not needed for the proposal) |
| Sahamati / RBI | Account Aggregator consent framework (NBFC-AA) | 500 million+ consents fulfilled, 310 million+ accounts linked, 1,100+ regulated entities (as of Sept 2026) | [P11] |
| RBI Innovation Hub | MuleHunter.AI (AI model to detect mule accounts) | Piloted with two large public-sector banks (Dec 2024) [P12]; "implemented across banks" and fed by I4C's Suspect Registry under a May 2026 MoU [P22]; bank count UNVERIFIED (secondary sources say 26 or 31) | [P12], [P22] |
| iSPIRT (DEPA) | DEPA for Training — open-source reference implementation of Confidential Clean Rooms (needs a signed e-contract and an Azure subscription); README: "work-in-progress and should not be used in production"; 18 GitHub stars, last push 12 Aug 2026, CC0 licence | Reference implementation, not production | [P21] |

**Where our design borrows and where it goes further.** We reuse every rail above unchanged (accounts, KYC, BCs, UPI 123PAY, AePS, alerts, campaigns, SLBC/DLCC review forums). What is missing in production — based on what the Ministry says it does not maintain [P1, P3] — is (a) a person-level, gaming-resistant usage measure, (b) targeting by *expected incremental* usage instead of by dormancy, (c) causal measurement of which outreach works for whom, and (d) usage-based accountability tables down to district and implementer level released with privacy guarantees. That is the scope of Sakriya.

## 4. Method state of the art used in the design (standard techniques; library and paper citations are on the verification backlog)

- **Targeting under a budget:** uplift / heterogeneous-treatment-effect models (meta-learners such as T-, X- and DR-learners; causal forests) and policy learning with budget constraints; evaluation by policy value against an oracle on held-out units, Qini/uplift curves [L].
- **Adaptive measurement:** randomised holdouts and adaptive experiments (bandits) to keep estimating effects after launch [L].
- **Privacy:** keyed-hash (HMAC) pseudonymous tokens scoped per purpose; private set intersection; confidential-computing clean rooms; differential privacy for published aggregates with a privacy-budget ledger; small-cell suppression [L].
- **Accountability:** value-added / difference-in-differences style attribution against comparable units with confidence intervals; Goodhart-resistant metric design (multi-dimensional, customer-induced, persistence-weighted) [L].

## 5. Our own numbers so far (committed runs)

- Real data: the two CSVs above (reproduce with `python eval/public_data/parse_ls4090.py`).
- Synthetic targeting benchmark (C14 simulator → C2 → C3 → C6): [`eval/results/c6_*.json`](../eval/results/) and the ledger [`components/targeting/autoresearch/results.tsv`](../components/targeting/autoresearch/results.tsv); all account-level data there is **SYNTHETIC**, calibrated to the 23% inoperative share above.
- **C6 v0.2 pre-registered test** (SYNTHETIC; `eval/preregistration/c6_v02.md` → `c6_v02_results.md`): transparent rule 0.38, learned who-only challenger 0.46 (+0.079, 95% CI 0.058–0.100, 10/10 seeds); gate never deployed it; ADR 002 ships the rule with the model as a gated challenger.
- **C5 policy engine:** 22/22 governance scenarios, 0 false allows; audit-log tampering detected 65/65 with a published checkpoint (`eval/results/policy_engine.json`).
- **Real-RCT check of the C6 learner** [P9] (`python eval/hillstrom_eval.py --seeds 0 1 2` → [`hillstrom_uplift.json`](../eval/results/hillstrom_uplift.json); retail e-mail, not banking): incremental visits per 1,000 customers vs no e-mail, IPW on held-out halves, mean of 3 splits — at a 10% budget: random 6.4, best arm to a random subset 8.1, our learner 10.6; at 20%: 13.2 / 15.5 / 18.7; at 100%: 63.6 / 80.7 / 77.5. The learner wins when contacts are scarce (who to contact) and loses at full coverage (which message), where per-person arm choice is noisy; the 95% CIs of the paired difference include zero in 2 of 3 splits at 10–20%.
- Findex 2025 India extract: [`findex2025_india_account_inactive.csv`](../eval/public_data/derived/findex2025_india_account_inactive.csv).

## 6. Sources

- **[P1]** Rajya Sabha Unstarred Question 2636, answered 12 Aug 2025, Ministry of Finance (DFS), "Credit disbursed to PMJDY account holders", incl. Annexures I–II. https://sansad.in/getFile/annex/268/AU2636_2RfYLG.pdf?source=pqars — opened 2026-10-04.
- **[P2]** Lok Sabha Unstarred Question 4090, answered 18 Aug 2025, Ministry of Finance (DFS), "Number of Jan Dhan accounts", incl. state-wise annexure. https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU4090_LCDFLT.pdf?source=pqals — opened 2026-10-04.
- **[P3]** Lok Sabha Unstarred Question 1333, answered 8 Dec 2025, Ministry of Finance (DFS), "Inoperative Jan Dhan accounts". https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU1333_viWPuz.pdf?source=pqals — local copy retrieved overnight by our fetcher; text read 2026-10-04.
- **[P4]** Press Information Bureau backgrounder "12 Years of PM Jan Dhan Yojana: Banking for All, Empowerment for All", 27 Aug 2026 (PDF, 6 pp.). URL recovered and figures re-verified in a browser on 2026-10-04 (posted 27 Aug 2026, 2:06 PM): https://pib.gov.in/PressNoteDetails.aspx?NoteId=159721&ModuleId=3
- **[P5]** Reserve Bank of India, Press Release 2025-2026/759, "Financial Inclusion Index for March 2025", 22 Jul 2025. https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60875 — opened 2026-10-04.
- **[P6]** Reserve Bank of India, Press Release 2026-2027/686, "Financial Inclusion Index for March 2026", 16 Jul 2026. https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63164 — opened 2026-10-04.
- **[P7]** World Bank, Global Findex Database 2025 (GlobalFindexDatabase2025.csv; indicators account_t_d, inactive_t_d). https://thedocs.worldbank.org/en/doc/be6615202d1f08a25855c8ac2d615122-0050012025/related/GlobalFindexDatabase2025.csv (download page https://www.worldbank.org/en/publication/globalfindex/download-data) — downloaded and read 2026-10-04.
- **[P8]** Reserve Bank of India, circular RBI/2023-24/105 DOR.SOG (LEG).REC/64/09.08.024/2023-24, "Inoperative Accounts/Unclaimed Deposits in Banks – Revised Instructions", 1 Jan 2024, effective 1 Apr 2024. https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12589&Mode=0 — opened 2026-10-04.
- **[P9]** K. Hillstrom, MineThatData E-Mail Analytics and Data Mining Challenge dataset (64,000 customers randomised to no e-mail / men's / women's e-mail), 2008. http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv — downloaded 2026-10-04.
- **[P10]** RBI Press Release 2021-2022/1830 on the launch of UPI 123PAY and DigiSaathi. https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=53385 — opened 2026-10-04 by verification agent v1 (`research/verification-rails.md`).
- **[P11]** Sahamati, "Account Aggregator crosses 500 million consents as India marks 5th AA Foundation Day", Sept 2026. https://sahamati.org.in/media-article/account-aggregator-crosses-500-million-consents-as-india-marks-5th-aa-foundation-day/ — opened 2026-10-04 by v1.
- **[P12]** RBI Press Release 2024-2025/1648, Statement on Developmental and Regulatory Policies, 6 Dec 2024. https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=59245 — opened 2026-10-04 by v1.
- **[P13]** Digital Personal Data Protection Act, 2023 (No. 22 of 2023), ss. 7(b), 8(7), 10, 17(2)(b). https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf — opened 2026-10-04 (verification agent v2, `research/verification-law.md`).
- **[P14]** MeitY notification G.S.R. 843(E), 13 Nov 2025 (commencement of the DPDP Act: most substantive provisions incl. ss. 3–17 in force 18 months after publication); PIB backgrounder on the DPDP Rules 2025 notified 14 Nov 2025. https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf · https://pib.gov.in/PressReleasePage.aspx?PRID=2190655 — opened 2026-10-04 (v2).
- **[P15]** Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and Services) Act, 2016, s. 29 (as amended). https://backend.uidai.gov.in/get/files/media/document/2026-06/Aadhaar_Act_2016_as_amended_0.pdf — opened 2026-10-04 (v2).
- **[P16]** UIDAI Circular No. 14 of 2025 (4 Nov 2025), Aadhaar Data Vault and Reference Key. https://uidai.gov.in/images/Circular-No.14_of-2025.pdf — opened 2026-10-04 (v2).
- **[P17]** RBI Press Release 2021-2022/70, Financial Inclusion Index (17 Aug 2021): Access 35%, Usage 45%, Quality 20%; 97 indicators; 53.9 for March 2021 vs 43.4 for March 2017; no base year; annual in July. https://www.rbi.org.in/scripts/FS_PressRelease.aspx?prid=52068 — opened 2026-10-04. **Note:** PIB's Aug 2026 backgrounder [P4] says "53.9 in 2018"; RBI's release dates 53.9 to March 2021, so we use RBI's figures.
- **[P18]** NPCI, AePS Product Statistics, "AePS – Cash Withdrawal Monthly Statistics" (2026-27; data MTD as of 30 Sep 2026). https://www.npci.org.in/product/aeps/product-statistics — opened in a browser 2026-10-04.
- **[P19]** Lok Sabha Unstarred Question 1598, Ministry of Rural Development, answered 29 Jul 2025 (BC Sakhis deployed). https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU1598_DuNizn.pdf?source=pqals — opened 2026-10-04.
- **[P20]** DBT Mission / NPCI, "Aadhaar Payments Bridge (APB) System — Standard Operating Procedure", v3.0.2 (Feb 2021), §2 and note (a). https://dbtbharat.gov.in/data/dbt_payments/Standard-Operating-Procedure-of-Aadhaar-Payments-Bridge-(APB).pdf — opened 2026-10-04.
- **[P21]** iSPIRT, `depa-training` repository (README; GitHub API: 18 stars, pushed 2026-08-12, CC0-1.0). https://github.com/iSPIRT/depa-training — opened 2026-10-04.
- **[P22]** PIB (Ministry of Home Affairs), "I4C and RBIH Sign MoU to Strengthen AI-Driven Detection of Mule Accounts and Cyber Financial Frauds", 12 May 2026. https://pib.gov.in/PressReleasePage.aspx?PRID=2260277 — opened in a browser 2026-10-04.
- **[P23]** Digital Personal Data Protection Rules, 2025, G.S.R. 846(E), 13 Nov 2025 — rule 16 ("The provisions of the Act shall not apply to the processing of personal data necessary for research, archiving or statistical purposes if it is carried on in accordance with the standards specified in Second Schedule") and the Second Schedule standards (lawful processing; purpose limitation; minimisation; reasonable efforts for accuracy; retention only while required; reasonable security safeguards; for s.7(b) processing, intimation to the Data Principal). https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf (linked from PIB PRID 2190655) — opened 2026-10-04.
- **[P24]** RBI/2025-26/52, "Inoperative Accounts/Unclaimed Deposits in Banks – Revised Instructions (Amendment) 2025", 12 Jun 2025: para 6.1 substituted — KYC updation for activation at all branches, V-CIP "endeavour", and the services of an authorised Business Correspondent. https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12864&Mode=0 — opened 2026-10-04 (lead found via the gpt-6-astra review).
- **[P25]** RBI/2025-26/51, "Reserve Bank of India (Know Your Customer (KYC)) (Amendment) Directions, 2025", 12 Jun 2025: para 38(a)(iia) — self-declaration (no change / address change only) through an authorised BC, recorded electronically after biometric e-KYC; low-risk customers may keep transacting until KYC is updated within one year of falling due or by 30 Jun 2026, whichever is later. https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12866&Mode=0 — opened 2026-10-04.
- **[P26]** RBI press release, "National Strategy for Financial Inclusion (NSFI): 2025-30", 1 Dec 2025 — approved by the FSDC Sub-Committee; "improving the quality and consistency of last mile access and effective usage of financial services"; five strategic objectives (Panch-Jyoti) incl. a gender-sensitive approach and customer protection/grievance redressal; 47 action points. https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=61712 — opened 2026-10-04.
- **[P0]** Official problem statement, The India @71/100 Challenge, Techfest 2026-27 — `_briefs/india71.pdf`.
- **[S]** News coverage seen in search results 2026-10-04, not checked against primaries: The Hindu BusinessLine and Economic Times on RBI FI-Index FY25 = 67.0 (from 64.2) and weights Access 35% / Usage 45% / Quality 20%.

## 7. Verification backlog (do before any number goes into the PDF)

1. ~~Global Findex 2025 India figures~~ (done: [P7], data file).
2. ~~FI-Index values~~ (done: [P5], [P6]); still to open: the Aug 2021 methodology release (weights, 97 indicators — currently [S]).
3. NFHS-5 / NFHS-4: women having a bank or savings account they themselves use (national, state, district) — overnight download was truncated.
4. ~~RBI circular on inoperative accounts~~ (done: [P8]).
5. ~~DPDP Act ss. 7, 8, 10, 17; Rules and commencement; Aadhaar Act s. 29; UIDAI ADV~~ (done: [P13]–[P16]); NPCI mapper consent (done: [P20]); DPDP Rules' standards for s. 17(2)(b) (done: [P23], rule 16 + Second Schedule).
6. Done 4 Oct 14:30 IST: AePS [P18], NPCI mapper consent and routing [P20], BC Sakhi [P19], MuleHunter.AI deployment [P22] (bank count still UNVERIFIED), FI-Index weights [P17], DEPA [P21]. Still UNVERIFIED: Hello! UPI (NPCI URLs 404), IPPB figures.
7. DBT Bharat totals (FY 2024-25, 2025-26) — the dashboard is client-rendered; needs a browser.
8. Outcomes of the Jul–Sep 2025 saturation campaign (PIB/DFS).
9. Effect sizes from account-usage RCTs (Dupas et al. 2018; Field et al. 2021; Karlan et al. 2016; Schaner 2018; Bachas et al. 2021) to replace simulator ASSUMPTIONs.
