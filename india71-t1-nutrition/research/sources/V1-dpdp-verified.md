# V1 — DPDP Act 2023 / DPDP Rules 2025 citation verification (Poshan Setu)

**Scope:** Verify legal citations in `components/policy_gate/policy.yaml` and `deliverables/round1-proposal.md` against primary statutory text. Zero-hallucination protocol: every quote below was opened from the cited URL on the stated access date. Items I could not open a primary text for are marked UNVERIFIED — do not cite them as settled law.

**Access date for all sources in this file: 2026-10-04** (unless noted otherwise).

**Status legend:** verified = primary statutory/gazette text opened and quoted verbatim; partly = primary text opened but it only partially supports our citation, or commencement/applicability caveats apply; no = primary text contradicts or does not support citation; UNVERIFIED = could not open a primary source (government sites returned HTTP 403/404 to the fetch tool in this session).

---

## (a) Citation verification table

_(table under construction — rows appended as each item is verified; see progress log at bottom)_

| # | Our citation (as used in policy.yaml / proposal) | Verified? | Exact section/rule | Verbatim text (primary source) | Correction / suggested wording |
|---|---|---|---|---|---|

---
## Working notes / progress log (will be cleaned up into sections b–d below as research proceeds)

### Source 1 — DPDP Act 2023, Section 7 (verbatim, via IndiaKanoon mirror of the Act)
- URL: https://indiankanoon.org/doc/62814281/
- Access date: 2026-10-04
- Note: meity.gov.in, egazette.gov.in and indiacode.nic.in all returned HTTP 403 to the automated fetch tool in this session (bot-blocked); indiankanoon.org (a long-established, widely cited free Indian statute/case-law mirror) served the Act's Akoma Ntoso (akn-*) marked-up text, which was fetchable. Treating as a reliable secondary mirror of the enacted text pending direct confirmation; flagged accordingly below.
- VERBATIM (Section 7, "Certain legitimate uses"):

> "(a) for the specified purpose for which the Data Principal has voluntarily provided her personal data to the Data Fiduciary, and in respect of which she has not indicated to the Data Fiduciary that she does not consent to the use of her personal data.
>
> Illustrations. (I) X, an individual, makes a purchase at Y, a pharmacy. She voluntarily provides Y her personal data and requests Y to acknowledge receipt of the payment made for the purchase by sending a message to her mobile phone. Y may process the personal data of X for the purpose of sending the receipt. (II) X, an individual, electronically messages Y, a real estate broker, requesting Y to help identify a suitable rented accommodation for her and shares her personal data for this purpose. Y may process her personal data to identify and intimate to her the details of accommodation available on rent. Subsequently, X informs Y that X no longer needs help from Y. Y shall cease to process the personal data of X;
>
> (b) for the State and any of its instrumentalities to provide or issue to the Data Principal such subsidy, benefit, service, certificate, licence or permit as may be prescribed, where––
> (i) she has previously consented to the processing of her personal data by the State or any of its instrumentalities for any subsidy, benefit, service, certificate, licence or permit; or
> (ii) such personal data is available in digital form in, or in non-digital form and digitised subsequently from, any database, register, book or other document which is maintained by the State or any of its instrumentalities and is notified by the Central Government, subject to standards followed for processing being in accordance with the policy issued by the Central Government or any law for the time being in force for governance of personal data.
>
> Illustration. X, a pregnant woman, enrols herself on an app or website to avail of government's maternity benefits programme, while consenting to provide her personal data for the purpose of availing of such benefits. Government may process the personal data of X processing to determine her eligibility to receive any other prescribed benefit from the government;
>
> (c) for the performance by the State or any of its instrumentalities of any function under any law for the time being in force in India or in the interest of sovereignty and integrity of India or security of the State;
>
> (d) for fulfilling any obligation under any law for the time being in force in India on any person to disclose any information to the State or any of its instrumentalities, subject to such processing being in accordance with the provisions regarding disclosure of such information in any other law for the time being in force;
>
> (e) for compliance with any judgment or decree or order issued under any law for the time being in force in India, or any judgment or order relating to claims of a contractual or civil nature under any law for the time being in force outside India;
>
> (f) for responding to a medical emergency involving a threat to the life or immediate threat to the health of the Data Principal or any other individual;
>
> (g) for taking measures to provide medical treatment or health services to any individual during an epidemic, outbreak of disease, or any other threat to public health; ..." [continues to (h), (i) — not yet fetched]

**Key implication:** s.7(b) is NOT a generic "State benefit/service" catch-all. It requires EITHER (i) prior specific consent by the data principal for that subsidy/benefit/service, OR (ii) the data to already sit in a database "maintained by the State ... and notified by the Central Government" with Central-Government-prescribed processing standards. Our policy.yaml cites "s.7(b) — State benefit/service" for AWW/LS/CDPO/district/state routine access — but ICDS growth/Poshan Tracker records are not self-evidently a "notified database" under 7(b)(ii) absent a specific Central Government notification, and most Anganwadi enrolment does involve a consent step (closer to 7(b)(i)) — needs the actual notification check. **s.7(c)** ("performance ... of any function under any law for the time being in force", e.g. National Food Security Act 2013 ss.4–6 ICDS nutrition mandate) may be the better-fitting legitimate use for routine AWW/ASHA/supervisor programme operation, separate from 7(b) which is narrower. CORRECTION flagged in table below.

