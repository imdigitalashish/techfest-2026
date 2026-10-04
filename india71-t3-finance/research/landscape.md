# Landscape — Financial inclusion: from holding an account to using it (India @71/100, Theme 3)

Last updated 2026-10-04 07:30 IST · Lead: india71-t3-finance session.

**How to read this file.** Every number carries a source. **[P]** = primary source opened on 2026-10-04 (local copy in the gitignored `.cache/src/` or `.data/`). **[S]** = secondary source (news) seen in search results tonight, not yet checked against the primary — treat as **UNVERIFIED** until the primary is opened. **[L]** = lead only (named programme or method we know of but did not open tonight) — **UNVERIFIED**. Overnight, most research sub-agents failed on network timeouts (see the thought node), so this version rests on fewer, harder sources; the verification backlog is at the end.

## 1. The measurable gap (scorecard vs lived reality)

The scorecard says inclusion is rising; the ledger says usage is falling.

| Indicator | Earlier | Latest | Source |
|---|---|---|---|
| PMJDY accounts | 42.20 crore (Mar 2021) | 59.09 crore (19 Aug 2026) | [P1] Annexure-II; [P4] |
| RBI Financial Inclusion Index | 53.9 (2018) [P4]; 64.2 (Mar 2024) | 67.0 (Mar 2025) → **70.0 (Mar 2026)**, rise "mainly on account of uptick in Usage" | [P5], [P6] |
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

Why the gap persists — root-cause tree (evidence status in brackets):
0. **The official flag is not a usage measure.** "Inoperative" is a fraud-control and unclaimed-deposit status; DBT/scholarship accounts are exempted from it [P8], so the very beneficiaries the theme targets can be invisible in inoperative statistics, and a DBT account that is credited and immediately emptied counts as "operative".
1. **Measurement counts accounts, not people, and enrolment, not use.** Key breakdowns are "not centrally maintained" [P1, P3]; review forums therefore see openings and totals. Usage enters the national scorecard only through the composite FI-Index [P5, P6] (Usage weight 45% per [S] ET/BusinessLine — UNVERIFIED at RBI), which is national, not district- or implementer-level [L].
2. **One-size outreach.** Alerts and campaigns go to every inoperative account [P2]. Many inoperative accounts belong to people who use another account (duplicates), have migrated, or have died — reactivating those wastes visits; meanwhile persuadable users get the same SMS as everyone else. (Mechanism plausible; share **UNVERIFIED** — no public data; our simulator makes the assumption explicit.)
3. **KYC friction.** Reactivation needs fresh KYC [P3, P8]; RBI allows any branch or V-CIP [P8], but for a rural, low-literacy holder that still means a trip or a smartphone — the same friction that caused disuse. [L: BC-based re-KYC — UNVERIFIED.]
4. **DBT as pass-through.** Benefits land and are withdrawn in cash, so accounts are "active" without meaningful use (no saving, insurance, digital payment) [mechanism; magnitude **UNVERIFIED** — needs bank data].
5. **Safety.** Reactivated dormant accounts can be abused as mule accounts [L: RBIH MuleHunter.AI, I4C — UNVERIFIED tonight]; a reactivation drive without a fraud gate creates risk.
6. **Data-sharing uncertainty.** Linking bank, NPCI-mapper and DBT data touches the DPDP Act 2023 and the Aadhaar Act (s. 29) [L — section-level claims UNVERIFIED tonight]; without a clear legal pattern, each actor keeps its silo.

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
| NPCI | AePS, APBS/NPCI mapper for Aadhaar-based DBT, "Hello! UPI" voice payments | Production | [L] UNVERIFIED (npci.org.in blocked our fetchers) |
| MoRD / DAY-NRLM | BC Sakhi (women SHG members as Business Correspondents) | Production | [L] UNVERIFIED tonight |
| India Post Payments Bank | Doorstep banking, AePS | Production | [L] UNVERIFIED tonight |
| Sahamati / RBI | Account Aggregator consent framework (NBFC-AA) | 500 million+ consents fulfilled, 310 million+ accounts linked, 1,100+ regulated entities (as of Sept 2026) | [P11] |
| RBI Innovation Hub | MuleHunter.AI (AI model to detect mule accounts) | Piloted with two large public-sector banks (Dec 2024); current bank count UNVERIFIED | [P12] |
| iSPIRT / cloud providers | DEPA Training confidential clean rooms; cloud confidential clean rooms | Open source / cloud services | [L] UNVERIFIED tonight |

**Where our design borrows and where it goes further.** We reuse every rail above unchanged (accounts, KYC, BCs, UPI 123PAY, AePS, alerts, campaigns, SLBC/DLCC review forums). What is missing in production — based on what the Ministry says it does not maintain [P1, P3] — is (a) a person-level, gaming-resistant usage measure, (b) targeting by *expected incremental* usage instead of by dormancy, (c) causal measurement of which outreach works for whom, and (d) usage-based accountability tables down to district and implementer level released with privacy guarantees. That is the scope of Sakriya.

## 4. Method state of the art used in the design (standard techniques; library and paper citations are on the verification backlog)

- **Targeting under a budget:** uplift / heterogeneous-treatment-effect models (meta-learners such as T-, X- and DR-learners; causal forests) and policy learning with budget constraints; evaluation by policy value against an oracle on held-out units, Qini/uplift curves [L].
- **Adaptive measurement:** randomised holdouts and adaptive experiments (bandits) to keep estimating effects after launch [L].
- **Privacy:** keyed-hash (HMAC) pseudonymous tokens scoped per purpose; private set intersection; confidential-computing clean rooms; differential privacy for published aggregates with a privacy-budget ledger; small-cell suppression [L].
- **Accountability:** value-added / difference-in-differences style attribution against comparable units with confidence intervals; Goodhart-resistant metric design (multi-dimensional, customer-induced, persistence-weighted) [L].

## 5. Our own numbers so far (committed runs)

- Real data: the two CSVs above (reproduce with `python eval/public_data/parse_ls4090.py`).
- Synthetic targeting benchmark (C14 simulator → C2 → C3 → C6): [`eval/results/c6_*.json`](../eval/results/) and the ledger [`components/targeting/autoresearch/results.tsv`](../components/targeting/autoresearch/results.tsv); all account-level data there is **SYNTHETIC**, calibrated to the 23% inoperative share above.
- **Real-RCT check of the C6 learner** [P9] (`python eval/hillstrom_eval.py --seeds 0 1 2` → [`hillstrom_uplift.json`](../eval/results/hillstrom_uplift.json); retail e-mail, not banking): incremental visits per 1,000 customers vs no e-mail, IPW on held-out halves, mean of 3 splits — at a 10% budget: random 6.4, best arm to a random subset 8.1, our learner 10.6; at 20%: 13.2 / 15.5 / 18.7; at 100%: 63.6 / 80.7 / 77.5. The learner wins when contacts are scarce (who to contact) and loses at full coverage (which message), where per-person arm choice is noisy; the 95% CIs of the paired difference include zero in 2 of 3 splits at 10–20%.
- Findex 2025 India extract: [`findex2025_india_account_inactive.csv`](../eval/public_data/derived/findex2025_india_account_inactive.csv).

## 6. Sources

- **[P1]** Rajya Sabha Unstarred Question 2636, answered 12 Aug 2025, Ministry of Finance (DFS), "Credit disbursed to PMJDY account holders", incl. Annexures I–II. https://sansad.in/getFile/annex/268/AU2636_2RfYLG.pdf?source=pqars — opened 2026-10-04.
- **[P2]** Lok Sabha Unstarred Question 4090, answered 18 Aug 2025, Ministry of Finance (DFS), "Number of Jan Dhan accounts", incl. state-wise annexure. https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU4090_LCDFLT.pdf?source=pqals — opened 2026-10-04.
- **[P3]** Lok Sabha Unstarred Question 1333, answered 8 Dec 2025, Ministry of Finance (DFS), "Inoperative Jan Dhan accounts". https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU1333_viWPuz.pdf?source=pqals — local copy retrieved overnight by our fetcher; text read 2026-10-04.
- **[P4]** Press Information Bureau backgrounder "12 Years of PM Jan Dhan Yojana: Banking for All, Empowerment for All", 27 Aug 2026 (PDF, 6 pp.). Local copy retrieved overnight by our fetcher and read 2026-10-04; **its URL was not recorded — to re-record** (pib.gov.in).
- **[P5]** Reserve Bank of India, Press Release 2025-2026/759, "Financial Inclusion Index for March 2025", 22 Jul 2025. https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60875 — opened 2026-10-04.
- **[P6]** Reserve Bank of India, Press Release 2026-2027/686, "Financial Inclusion Index for March 2026", 16 Jul 2026. https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63164 — opened 2026-10-04.
- **[P7]** World Bank, Global Findex Database 2025 (GlobalFindexDatabase2025.csv; indicators account_t_d, inactive_t_d). https://thedocs.worldbank.org/en/doc/be6615202d1f08a25855c8ac2d615122-0050012025/related/GlobalFindexDatabase2025.csv (download page https://www.worldbank.org/en/publication/globalfindex/download-data) — downloaded and read 2026-10-04.
- **[P8]** Reserve Bank of India, circular RBI/2023-24/105 DOR.SOG (LEG).REC/64/09.08.024/2023-24, "Inoperative Accounts/Unclaimed Deposits in Banks – Revised Instructions", 1 Jan 2024, effective 1 Apr 2024. https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12589&Mode=0 — opened 2026-10-04.
- **[P9]** K. Hillstrom, MineThatData E-Mail Analytics and Data Mining Challenge dataset (64,000 customers randomised to no e-mail / men's / women's e-mail), 2008. http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv — downloaded 2026-10-04.
- **[P10]** RBI Press Release 2021-2022/1830 on the launch of UPI 123PAY and DigiSaathi. https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=53385 — opened 2026-10-04 by verification agent v1 (`research/verification-rails.md`).
- **[P11]** Sahamati, "Account Aggregator crosses 500 million consents as India marks 5th AA Foundation Day", Sept 2026. https://sahamati.org.in/media-article/account-aggregator-crosses-500-million-consents-as-india-marks-5th-aa-foundation-day/ — opened 2026-10-04 by v1.
- **[P12]** RBI Press Release 2024-2025/1648, Statement on Developmental and Regulatory Policies, 6 Dec 2024. https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=59245 — opened 2026-10-04 by v1.
- **[P0]** Official problem statement, The India @71/100 Challenge, Techfest 2026-27 — `_briefs/india71.pdf`.
- **[S]** News coverage seen in search results 2026-10-04, not checked against primaries: The Hindu BusinessLine and Economic Times on RBI FI-Index FY25 = 67.0 (from 64.2) and weights Access 35% / Usage 45% / Quality 20%.

## 7. Verification backlog (do before any number goes into the PDF)

1. ~~Global Findex 2025 India figures~~ (done: [P7], data file).
2. ~~FI-Index values~~ (done: [P5], [P6]); still to open: the Aug 2021 methodology release (weights, 97 indicators — currently [S]).
3. NFHS-5 / NFHS-4: women having a bank or savings account they themselves use (national, state, district) — overnight download was truncated.
4. ~~RBI circular on inoperative accounts~~ (done: [P8]).
5. DPDP Act 2023 sections 7, 8, 10, 17 and the DPDP Rules commencement; Aadhaar Act s. 29; NPCI mapper consent rules.
6. Partly done ([P10]–[P12]): still UNVERIFIED — AePS volumes, NPCI mapper, Hello! UPI, BC Sakhi numbers (npci.org.in and pib.gov.in block automated fetches; use a browser), current MuleHunter.AI bank count, DEPA clean-room repos.
7. DBT Bharat totals (FY 2024-25, 2025-26) — the dashboard is client-rendered; needs a browser.
8. Outcomes of the Jul–Sep 2025 saturation campaign (PIB/DFS).
9. Effect sizes from account-usage RCTs (Dupas et al. 2018; Field et al. 2021; Karlan et al. 2016; Schaner 2018; Bachas et al. 2021) to replace simulator ASSUMPTIONs.
