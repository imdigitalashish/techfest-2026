# Sakriya — counting people, not accounts: a usage-data governance, targeting and accountability layer for Jan Dhan

**India @71/100 Challenge · Theme 3: Financial Inclusion & Meaningful Banking Access · Round 1 proposal (v1.0, 4 Oct 2026)**

> Draft status: must fit ≤ 6 A4 pages (Arial ≥ 11 pt, 1-inch margins); check with `deliverables/render_html.py`. [P*] = official or primary source in *References*; SYNTHETIC = simulator output, not field results. Remaining UNVERIFIED items are listed in `research/landscape.md` §7 and must be cited or removed before submission.

**Team information.** Team name: _TBD_ · Team ID: _TBD_ · Institution(s): IIT Delhi (+ _TBD_) · Contact: _TBD_ · Members (≤ 4): _TBD_.

## 1. Problem identification

India's scorecard says inclusion is rising. PMJDY accounts grew from 42.20 crore (March 2021) to 59.09 crore (August 2026) [P1, P4], and the RBI Financial Inclusion Index reached 70.0 in March 2026, a rise RBI attributes "mainly" to an "uptick in Usage" [P6]. The administrative record says otherwise: **inoperative PMJDY accounts — no customer-induced transaction for two years — rose from 5.94 crore (14.1%, March 2021) to 15.09 crore (26.4%, Lok Sabha answer of 8 December 2025)** [P1, P3]. Accounts grew 35%; inoperative accounts grew 154%.

The World Bank's survey tells a third story: Indian adults with an *inactive* account fell from 27.4% (2021) to 14.3% (2024) [P7]. The lenses disagree because the State counts **accounts, not people** — someone may use one account while an old Jan Dhan account lapses — and no one can tell which. Both agree on **who is left behind**: in 2024, 19.6% of women account owners had an inactive account against 12.6% of men, and 23.2% of the poorest 40% against 11.6% of the richest 60% [P7, derived]. Yet the Ministry of Finance told Parliament that inoperative accounts by gender and by rural/semi-urban area, accounts holding under Rs 500, and credit to PMJDY holders are **"not centrally maintained"** [P1, P3].

**Gap.** One Jan Dhan account in four is inoperative and the share is rising; one woman account owner in five has not used her account in a year; and the data that could find, reach and count these people — bank ledgers, DBT credits, Business Correspondent (BC) networks — is not governed to do so. **Community:** women, the poorest and less-educated account holders, mostly in the rural and semi-urban areas that hold 77.8% of Jan Dhan accounts [P4, P7].

## 2. Evidence and context

| Indicator | Value | Source |
|---|---|---|
| PMJDY accounts (women) | 59.09 crore (32.92 crore), 19 Aug 2026; 45.95 crore rural/semi-urban | [P4] |
| Deposits; RuPay cards | Rs 3,16,514 crore; 41.29 crore cards (19 Aug 2026) | [P4] |
| Inoperative PMJDY accounts | 5.94 → 6.57 → 9.45 → 10.21 → 11.94 crore (Mar 2021–Mar 2025) → 13.05 (Jul 2025) → 15.09 crore (Dec 2025) | [P1–P3] |
| Inoperative share by state (31 Jul 2025) | 12.5% (Lakshadweep) to 39.0% (Goa); among the 16 states with > 1 crore accounts, 16.3% (West Bengal) to 32.5% (Telangana); Uttar Pradesh 2.75 crore (27.5%) | [P2], our parse |
| RBI FI-Index | 64.2 (Mar 2024) → 67.0 (Mar 2025) → 70.0 (Mar 2026) | [P5, P6] |
| Adults with an inactive account | 27.4% (2021) → 14.3% (2024); of owners in 2024: women 19.6%, men 12.6%, poorest 40% 23.2% | [P7] |
| Overdraft availed | 35.99 lakh holders (≈ 0.6% of accounts), Mar 2025 | [P1] |
| "Not centrally maintained" | inoperative by gender and area, balance ranges, accounts < Rs 500, credit to PMJDY holders | [P1, P3] |

The rise continued through a nationwide Gram Panchayat saturation campaign (1 July – 30 September 2025) that targeted re-KYC of inactive PMJDY accounts [P1, P2]. The two Parliament answers word the definition differently, so part of the late-2025 jump may be definitional — itself a governance problem.

## 3. Existing ecosystem and why the gap persists

**What exists.** Zero-balance accounts with RuPay card, accident cover and overdraft [P4]; DBT credited "even to the inactive accounts" [P2]; RBI's revised inoperative-account rules in force since April 2024 — annual review, alerts a year ahead, tracing of holders, KYC at any branch or by video, no activation charges, monitoring of reactivated accounts [P8]; unclaimed balances to RBI's DEA Fund after ten years [P3]; saturation campaigns and 2,421 Centres for Financial Literacy [P1]; feature-phone payments through UPI 123PAY (IVR, missed call, app, sound) [P10]; Account Aggregator consent rails with 310 million+ accounts linked [P11]; and the national FI-Index [P6]. AePS handles 92.6 million cash withdrawals a month (September 2026) [P18]; 65,949 SHG women were deployed as BC Sakhis between 2022-23 and June 2025 [P19]; and the NPCI mapper routes every Aadhaar-based DBT credit to the bank with the latest seeding mandate, seeded only with the customer's written consent [P20].

**Why the gap persists** — failures of data governance, not of rails:
1. **The official flag is not a usage measure.** "Inoperative" is a fraud-control status, and accounts opened for DBT or scholarships are deliberately exempted from it [P8] — unused DBT accounts can be invisible, and an account emptied the day DBT lands counts as "operative".
2. **Counting accounts, not people; enrolment, not use.** Forums review openings and totals; breakdowns by person, gender or area do not exist centrally [P1, P3]. The NPCI mapper sends all Aadhaar-based DBT to whichever bank seeded last [P20], so the account that receives benefits need not be the one a person uses.
3. **Blanket outreach.** Alerts and campaigns go to every dormant account [P2, P8]; visits are spent on duplicates, migrants and the deceased while persuadable holders get a generic SMS.
4. **Reactivation friction.** Fresh KYC at a branch or by video [P8] is hard for the people who stopped coming.
5. **No feedback loop.** No one measures which outreach changed behaviour for whom, so programmes cannot learn and implementers cannot be credited or held to account.
6. **No agreed sharing pattern.** Usage, DBT and identity data sit with banks, NPCI and departments under the DPDP Act 2023 and Aadhaar law [P13–P16]; a lawful pattern is possible (below) but nobody has built it, so each keeps its silo.

## 4. Proposed solution — Sakriya

Sakriya (Hindi for "active") is a **data-governance and decision layer on existing rails — no new financial product**. It (a) measures meaningful usage *per person*, (b) decides who gets which outreach to maximise *incremental* usage per rupee, (c) measures what worked, and (d) publishes usage-based accountability tables to the forums that already review inclusion, with privacy built into every flow. Fourteen components sit behind typed contracts; two are the innovation spikes.

```mermaid
flowchart TB
  A["<b>Banks</b> · C1–C2<br/>usage state per account"] --> B["<b>Regulated clean room</b><br/>C3 count people · C6 target<br/>C9 holdouts · C10 scorecard"]
  B -- "own-customer task lists" --> C["<b>Bank → BC / BC Sakhi,</b><br/><b>IVR, UPI 123PAY</b><br/>C7 fraud gate · C8 outreach"]
  C -- "outcomes" --> B
  B --> D["<b>C11 privacy publisher</b><br/>differential privacy"]
  D --> E["<b>Forums</b>: DFS · RBI · SLBC<br/>DLCC · public"]
  P{{"<b>C5 purpose policy</b><br/>+ audit log"}} -.-> B
```

**4.1 Usage state, not "operative" (C1–C2).** Each bank computes monthly, inside its own systems, a standard record per account — customer-induced transactions by channel, DBT credits and how fast they are withdrawn, balance, KYC status, insurance and pension enrolment — and a published rule set assigns one of five states (*inoperative, dormant-risk, DBT pass-through, basic, meaningful*) with a 0–100 Meaningful Usage Score. Token credits never count as use; anyone can recompute any state.

**4.2 Count people, not accounts (C3–C5).** In a regulated confidential-computing clean room, accounts are linked to *purpose-scoped pseudonyms* — keyed hashes of the Aadhaar Data Vault *Reference Key* that UIDAI already requires banks to use instead of Aadhaar numbers [P16] — tokens issued for targeting cannot be joined with tokens issued for statistics. A policy engine decides every request by role × purpose × data × granularity × legal basis and writes a hash-chained audit entry. The clean room can start from DEPA's open-source Confidential Clean Room reference implementation (iSPIRT; Azure confidential computing), which its authors say is not yet production-grade [P21]; hardening it is part of phase 1.

| Data | Bank and its BC | Clean room | DFS · RBI · SLBC · DLCC | Public |
|---|---|---|---|---|
| Ledger, KYC status | Own customers | Encrypted features | Never | Never |
| Person usage state, target list | Own customers, with reason codes | Purpose-bound, deleted after use | Never | Never |
| Usage rates, gender gaps, effects | Own units | Computed | Differentially private, with CIs | State level |

**Legal fit (our reading; legal review in phase 1).** The DPDP Act exempts statistical processing only where the data is "not to be used to take any decision specific to a Data Principal" [P13 s.17(2)(b)] — so Sakriya keeps accountability statistics strictly aggregate, under a separate token key, while person-level targeting (a decision about a person) stays with the account-holding bank as data fiduciary for its own customers. Core biometrics are never touched, and identity information is used only for stated purposes [P15 s.29]. The Act's substantive duties apply from about May 2027 [P14], before any state roll-out, so the design is compliant from the pilot onwards.

**4.3 Targeting (spike A, C6): a transparent rule by default, a learned model only behind a gate.** Arms: local-language IVR/SMS, BC or BC Sakhi visit with doorstep re-KYC, assisted UPI 123PAY onboarding, a small first-use incentive. The *default* is a rule anyone can recompute from the pilot table: the arm with the highest pilot effect per rupee goes to every eligible person, and the leftover budget upgrades persons, drawn by lottery, to the arm with the best extra effect per extra rupee. A *learned challenger* keeps the same arms but uses an uplift model to choose *whom* to upgrade, with women at least their eligible share; it replaces the lottery only where it beats the rule on held-out pilot data (the gate). Every plan keeps a 10% randomised holdout. A fraud gate (C7) adds verification before reactivating accounts at risk of mule use, alongside MuleHunter.AI, which RBI Innovation Hub has implemented across banks [P12, P22].

**4.4 Learning and accountability (spike B, C9–C11).** Holdouts give unbiased monthly effects by arm, segment and implementer. The **usage scorecard** reports for each district, bank, branch and BC: persons in meaningful use, inoperative persons, the gender gap, and the implementer's *incremental* usage with a confidence interval, plus gaming flags (token credits, reactivate-then-lapse, account churn). A differential-privacy publisher with a privacy-budget ledger feeds existing forums: DFS/RBI nationally (beside the FI-Index), SLBCs, District Consultative Committees and Lead District Managers, banks and BCs for their own units, and a public state page. "Accounts opened" targets become **"people actively banking" targets**. In a SYNTHETIC test with 200 implementer units, 20% of them gaming (token credits, duplicate accounts) and a year of data, ranking units by enrolments correlated 0.04 with their true contribution and put only gamers in the top 20; the account-level "operative" share correlated 0.16; Sakriya's holdout-based incremental usage correlated **0.90**, with gamers no more common in its top 20 than overall (`eval/scorecard_eval.py`).

**4.5 What the working skeleton shows (all SYNTHETIC).** On simulated populations calibrated to the official 23% inoperative share — ten worlds of 20,000 persons, results for held-out persons:

| Policy (same budget: Rs 10 per eligible person) | Share of achievable gain (mean ± sd) | Extra persons in meaningful use (per ~11,200 eligible) |
|---|---|---|
| Status quo: BC visits to inoperative, then dormant, then pass-through accounts | 0.03 ± 0.01 | 47 |
| Highest "risk of non-use" first (BC visit) | −0.06 ± 0.01 | 24 |
| Best average arm (usually IVR) to everyone; rest of budget unspent | 0.29 ± 0.14 | 112 |
| **Transparent rule (default):** best arm per rupee to all, leftover budget upgrades by lottery | 0.38 ± 0.19 | 136 |
| **Learned challenger:** same arms; model chooses *whom* to upgrade | 0.46 ± 0.19 | 156 |
| Oracle (true effects) | 1.00 ± 0.00 | 295 |

_Share of achievable gain = (policy − random) / (oracle − random). Pre-registered test, seeds 10–19: `eval/preregistration/c6_v02.md` → `eval/results/c6_v02_prereg.json`._ **Dormancy is not persuadability**: dormancy-first outreach captures almost none of what the budget could achieve, and ranking by risk of non-use is worse than random. In a test registered before it was run, the learned challenger beat the transparent rule in all 10 worlds, by 0.08 of the achievable gain (95% CI 0.06–0.10); spending the leftover budget beat best-arm-only by 0.09. Two cautions shape the roadmap. The gate, with about 840 validation persons per world, never deployed the challenger, so the system that would actually have run was the rule. And in 2 of 10 worlds the pilot (about 810 persons per arm) ranked the arms wrongly. Pilot size per arm is a design input. On a real 64,000-person randomised e-mail experiment [P9] (retail, not banking), the same learner beat "best message to a random subset" by 2.5–3.2 responses per 1,000 when only 10–20% could be contacted (CIs include zero in two of three splits), but lost at full coverage: target *who*, personalise *which* cautiously.

## 5. Feasibility and implementation roadmap

**Owners, within existing mandates.** DFS (PMJDY mission) sponsors; RBI sets usage-state definitions alongside its inoperative-account and KYC directions and oversees the clean room; NPCI issues identity-reference tokens and runs UPI 123PAY/AePS; banks run C1–C2 and outreach through their BCs; SLBCs and the Lead Bank Scheme review scorecards in existing meetings; the DBT Mission supplies credit metadata; DAY-NRLM provides BC Sakhis.

**Plan.** *Months 0–3:* publish the usage-state rules and contracts; run C1–C2 on one bank's history inside the bank; legal review of the governance matrix (DPDP Act, Aadhaar law). *Months 3–9:* one-district randomised pilot (two to three banks, BC Sakhi presence, high inoperative share; arms sized so pilot effects can be ranked — our simulations show about 810 persons per arm can pick the wrong arm): targeting engine vs blanket outreach in randomised blocks; primary outcome persons in meaningful use at six months; secondary cost per incremental active person, women's share, fraud incidents. *Months 9–18:* state scale-up through the SLBC; scorecards on DCC/SLBC agendas; public DP page. *Months 18–36:* national — NSFI monitoring adds person-level usage by district and gender beside the FI-Index.

**Feasibility and risks.** A district plan runs on a laptop in minutes in our skeleton; banks already hold every input; outreach uses existing BC commissions and IVR; clean rooms and differential privacy are mature techniques. Risks and mitigations: legal basis for linkage (purpose-scoped tokens, minimisation, person lists only inside the bank, legal review first); opacity (published rules, reason codes, simple-rule fallback); exclusion by targeting (women's floor, holdouts, grievance channel); gaming (customer-induced definitions, persistence, gaming flags, comparison units); fraud on reactivation (C7).

## 6. Expected impact and scalability

**Beneficiaries:** the people behind 15.09 crore inoperative accounts and the DBT pass-through users — mostly rural women and the poorest. **Outcomes:** more people (not accounts) in sustained use at lower cost per reactivated user; gender and district breakdowns that are "not centrally maintained" today become routine, privacy-preserving statistics; implementers are reviewed on usage. **KPIs:** persons in meaningful use by district and gender; inoperative persons; incremental users per Rs lakh of outreach; women's share of incremental users; DBT pass-through share; fraud per lakh reactivations; data latency ≤ 10 days after month-end. **Scale:** every component runs on systems and forums that already exist nationally, so scaling is a matter of standards and adoption, not new infrastructure. Impact will be measured from the pilot's randomised design, not the simulator.

## References

[P1] Rajya Sabha USQ 2636, Ministry of Finance (DFS), 12 Aug 2025, Annexures I–II, sansad.in · [P2] Lok Sabha USQ 4090, 18 Aug 2025, state annexure, sansad.in · [P3] Lok Sabha USQ 1333, 8 Dec 2025, sansad.in · [P4] PIB, "12 Years of PM Jan Dhan Yojana", 27 Aug 2026 · [P5] RBI Press Release 2025-2026/759, FI-Index for March 2025, 22 Jul 2025 · [P6] RBI Press Release 2026-2027/686, FI-Index for March 2026, 16 Jul 2026 · [P7] World Bank, Global Findex Database 2025, data file (account_t_d, inactive_t_d; owner shares derived) · [P8] RBI circular RBI/2023-24/105, Inoperative Accounts/Unclaimed Deposits – Revised Instructions, 1 Jan 2024 · [P9] Hillstrom, MineThatData e-mail challenge dataset, 2008 · [P10] RBI Press Release 2021-2022/1830 (UPI 123PAY launch), rbi.org.in prid=53385 · [P11] Sahamati, "Account Aggregator crosses 500 million consents", Sept 2026 · [P12] RBI Press Release 2024-2025/1648, Statement on Developmental and Regulatory Policies, 6 Dec 2024 (MuleHunter.AI) · [P13] Digital Personal Data Protection Act 2023, ss. 7(b), 17(2)(b) · [P14] MeitY G.S.R. 843(E), 13 Nov 2025 (commencement); PIB, DPDP Rules 2025 notified, 17 Nov 2025 · [P15] Aadhaar Act 2016, s. 29 (as amended) · [P16] UIDAI Circular No. 14 of 2025, Aadhaar Data Vault and Reference Key, 4 Nov 2025 · [P17] RBI Press Release 2021-2022/70, Financial Inclusion Index (weights; 53.9 for March 2021) · [P18] NPCI, AePS product statistics, Sept 2026 · [P19] Lok Sabha USQ 1598, Ministry of Rural Development, 29 Jul 2025 · [P20] DBT Mission/NPCI, Aadhaar Payments Bridge SOP v3.0.2, Feb 2021 · [P21] iSPIRT, depa-training repository (GitHub) · [P22] PIB (MHA), I4C–RBIH MoU on mule accounts, 12 May 2026 · Techfest 2026-27, India @71/100 Challenge statement.
