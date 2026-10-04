# L12 — Record Linkage, PPRL, Disclosure Control & Tamper-Evident Audit (2026)

**Research status:** TIME-BOXED PASS 1 — ran significantly over the 25-min/14-source budget (~47 min elapsed; GitHub API metadata for 13 repos + 8 web_fetch/curl attempts + 7 web_search calls). Many conceptual claims rest on AI-search synthesis rather than independently opened primary text — these are explicitly marked **UNVERIFIED** below per the zero-hallucination rule. Do not cite UNVERIFIED items as fact without a follow-up read.
**Access date for all sources:** 2026-10-04
**Compiled for:** India @71/100 Challenge, Theme 1 — Maternal & Early Childhood Nutrition (Poshan Tracker ↔ RCH/U-WIN/ABHA linkage architecture)

---

## 1. Key Findings

### Record linkage (Fellegi–Sunter / Splink / alternatives)
- **Splink** (UK Ministry of Justice) is the clear state-of-the-art open tool: implements the **Fellegi–Sunter** probabilistic model, unsupervised (no labelled training data required), and is actively maintained — Splink 5 shipped ~2026-09-28, last repo push 2026-09-30 [verified, opened directly]. Verbatim scale claims from its own README: *"Capable of linking a million records on a laptop in around a minute"* and *"100+ million records"* via Spark backend [verified].
- MoJ's own internal document (a Fall-2023 internship posting, **not** a results report) confirms Splink has **"7 million users"** and underpins ADR UK's Data First programme, and that MoJ commissioned work specifically to study **bias/fairness of linkage outcomes across demographic groups** — but I could only find the project *proposal*, not the resulting quantified bias metrics [verified-opened for the proposal only; actual bias numbers NOT located — gap].
- `recordlinkage` (Python) and `fastLink` (R) are the next most-cited open implementations. `recordlinkage` shows **no commits since 2024-02-21** (~20 months stale) — a real maintenance concern if we depend on it. `fastLink` is more recently active (pushed 2026-02-28) [verified via GitHub API].
- OpenHIE's reference Client Registry ("OpenCR") now lives at `intrahealth/client-registry` (MIT, 27 stars, last push 2025-04-01) — small community. SanteMPI's backend (SanteDB, `santedb/santedb-server`) is committed very recently (2026-10-03) but has only single-digit stars — reads as an enterprise/support-model project rather than a broad open-source community [verified via GitHub API].

### Privacy-preserving record linkage (PPRL)
- Bloom-filter PPRL (Schnell et al. 2009) and the **Cryptographic Longterm Key (CLK)** concept are the dominant academic approach: q-grams of PII hashed into a Bloom filter; similarity (e.g., Dice coefficient) computed on filters without exposing raw identifiers [**UNVERIFIED — direct fetch of the 2009 BMC paper blocked with HTTP 406; description is AI-search synthesis of secondary sources, not independently read**].
- CSIRO Data61's `anonlink` (Apache-2.0, 75 stars, pushed 2026-05-19) and `clkhash` (Apache-2.0, 47 stars, pushed 2025-05-12) are the most visible maintained open implementations of CLK-based PPRL [verified via GitHub API] — but both have small communities (tens of stars) versus Splink/OPA/Trillian (hundreds–thousands), signalling niche/specialist adoption.
- Christen/Vidanage and collaborators published a multi-year attack line against Bloom-filter encodings — pattern-mining cryptanalysis (ICDE 2019), a graph-matching re-identification attack (CIKM 2020), a taxonomy of PPRL attacks (Journal of Privacy and Confidentiality 2022), and a "hardening" book chapter (Springer 2020) [**UNVERIFIED — none of these PDFs were successfully opened; CIKM 2020 fetch timed out. No re-identification success-rate numbers were verified.**]. **Implication:** CLK/Bloom-filter matching must not be treated as safe-by-default for ICDS/RCH/ABHA linkage without applying documented hardening (salting, balanced/XOR folding, bit permutation) — but which specific hardening is sufficient is an open question we have not verified from primary sources.

### Indian-name matching
- `AI4Bharat/IndicXlit` (transliteration, 21 Indic languages) exists under MIT licence with 142 stars, but **shows no commits since 2023-10-13** (~3 years stale as of today) [verified via GitHub API] — a maintenance red flag for a tool central to our name-matching pipeline.
- No transliteration-accuracy metric for IndicXlit was obtained (search was rate-limited and not successfully re-run) [gap].
- Search-engine synthesis (not independently opened) suggests India's **U-WIN** immunisation registry and **ABHA** do *not* mandate Aadhaar, accept alternate government IDs, and use a mix of deterministic + "probabilistic" matching (name/DoB/parent-name/address) for beneficiaries lacking a shared ID [**UNVERIFIED — uwin.mohfw.gov.in/faq and abdm.gov.in were not independently fetched this pass**].
- **No published Indian academic study quantifying record-linkage error rates specifically for transliterated/Indic-script name variants was located** — this looks like a genuine, citable research gap for our project rather than just an unopened source.

### Disclosure control
- US Census Bureau's 2020 **TopDown Algorithm** (differential privacy, applied national→...→block) is widely reported to trade block-level accuracy for formal DP guarantees, with independent (Harvard Imai Lab) claims of "systematic undercounts in racially and politically mixed precincts" [**UNVERIFIED — official Census brief PDF fetch timed out after 25s; Harvard DASeval page not opened; no epsilon value or accuracy-loss number independently confirmed**].
- **OpenDP** (`opendp/opendp`) is extremely actively maintained — pushed *today*, 2026-10-03, MIT licence, 438 stars [verified].
- **Tumult Analytics** now lives under the OpenDP GitHub org (`opendp/tumult-analytics`), Apache-2.0, only 17 stars but pushed 2026-09-30 — small community, high recent activity [verified]. Verbatim: *"Tumult Analytics is a Python library for privately computing aggregate queries on tabular data. It is built atop the Tumult Core library."*
- UK ONS has a live "Disclosure control" methodology page confirming a Government Statistical Service policy framework tied to the Code of Practice for Official Statistics exists, but the page returned only a one-line stub — **no specific numeric suppression threshold (e.g., a "fewer than N" rule) was obtained** [partially verified — page opened, content too thin to extract a number].

### Tamper-evident audit
- **Critical finding:** Google's `trillian` (Apache-2.0, 3,755 stars, pushed 2026-10-02) — the classic Merkle-tree transparency log behind Certificate Transparency — states in its own README, verbatim: *"Trillian is in maintenance mode. The next generation of transparency logs uses Tiled APIs and are better supported by Tessera. We recommend that any new log operators first try Tessera."* and *"we do not plan to add any new features to this version of Trillian."* [verified, directly opened]. **This means Trillian is the wrong foundation for a new 2026 build** — its successor `transparency-dev/tessera` (Apache-2.0, 242 stars, pushed 2026-10-01, *"Go library for building tile-based transparency logs (tlogs)"*) is the explicitly endorsed path [verified].
- HL7 **FHIR AuditEvent** (R5, current spec) [verified, directly opened], verbatim: *"A record of an event relevant for purposes such as operations, privacy, security, maintenance, and performance analysis,"* built on IHE-ATNA/RFC 3881/DICOM Part 15 Annex A5/NIST SP800-92 lineage, and critically: *"Servers that provide support for AuditEvent resources would not generally accept update or delete operations on the resources, as this would compromise the integrity of the audit record."* This gives a standards-based rationale for append-only audit storage — but FHIR itself only defines the **schema**, not cryptographic tamper-evidence; that still requires a hash-chain/Merkle backing (e.g., Tessera).
- FHIR **Consent** resource — fetch failed (DNS/transport-level error); **not verified at all this pass** [gap].
- **Open Policy Agent** (`open-policy-agent/opa`): Apache-2.0, **12,307 stars**, pushed *today* 2026-10-03 — by far the largest, most active project in this entire survey [verified via GitHub API]. No health-specific "purpose limitation" worked example was independently verified this pass — only its general-purpose popularity/activity is confirmed [gap].

---

## 2. Tools Table

| Tool | Purpose | Licence | Stars | Last commit (push) | Maturity | Usable by us? |
|---|---|---|---|---|---|---|
| **Splink** (`moj-analytical-services/splink`) | Probabilistic record linkage (Fellegi–Sunter), SQL-backend agnostic | MIT | 2,452 | 2026-09-30 | Mature, very active; v5 released 2026-09-28; "7M users" per MoJ | **YES** — primary candidate for ICDS↔RCH↔U-WIN↔ABHA linkage |
| `recordlinkage` (Python, `J535D165/recordlinkage`) | Modular comparison-vector + classifier toolkit (incl. Fellegi–Sunter ECM) | BSD-3-Clause | 1,063 | 2024-02-21 | **Stale (~20 mo, no recent commits)** | CAUTION — fine for prototyping, not for production without a maintenance plan |
| `fastLink` (R, `kosukeimai/fastLink`) | Fast EM-based Fellegi–Sunter probabilistic linkage | Not declared on repo (UNVERIFIED — CRAN page not checked) | 292 | 2026-02-28 | Actively maintained | YES, if team is R-capable — good cross-check against Splink |
| OpenCR (`intrahealth/client-registry`) | OpenHIE reference Client/Master Patient Registry | MIT | 27 | 2025-04-01 | Small community, ~18 mo stale | CAUTION — verify via OpenHIE community before relying on it as MPI backbone |
| SanteMPI backend (`santedb/santedb-server`) | Enterprise OpenHIE-aligned client registry/MPI | Apache-2.0 | 6 | 2026-10-03 | Actively committed, tiny public community (enterprise/support model) | CAUTION — evaluate via vendor channel, not GitHub signals alone |
| `anonlink` (CSIRO Data61) | PPRL via Cryptographic Longterm Keys (CLK) | Apache-2.0 | 75 | 2026-05-19 | Niche, moderately active | CONDITIONAL — only with documented hardening against known Bloom-filter attacks |
| `clkhash` (CSIRO Data61) | Encodes PII into CLK Bloom filters for anonlink | Apache-2.0 | 47 | 2025-05-12 | Niche, ~17 mo stale | CONDITIONAL — same caveats as anonlink |
| `AI4Bharat/IndicXlit` | Transliteration models, 21 Indic languages | MIT | 142 | 2023-10-13 | **Stale (~3 yr, no recent commits)** | CAUTION — validate output quality/accuracy before depending on it |
| OpenDP (`opendp/opendp`) | Core differential-privacy algorithm library | MIT | 438 | 2026-10-03 (today) | Very actively maintained | **YES** — strong candidate for the block/district DP aggregate layer |
| Tumult Analytics (`opendp/tumult-analytics`) | Python DP library for aggregate queries on tabular data | Apache-2.0 | 17 | 2026-09-30 | Actively maintained, small community, now under OpenDP org | **YES** — pairs with OpenDP for our "privacy-safe aggregates" use case |
| Trillian (`google/trillian`) | Merkle-tree transparency log | Apache-2.0 | 3,755 | 2026-10-02 | **Self-declared "maintenance mode," no new features planned** | **NO for new builds** — maintainers redirect new adopters to Tessera |
| Tessera (`transparency-dev/tessera`) | Tile-based transparency log, Trillian's successor | Apache-2.0 | 242 | 2026-10-01 | Actively developed; officially recommended successor | **YES** — preferred over Trillian for our tamper-evident audit log |
| Open Policy Agent (`open-policy-agent/opa`) | General-purpose policy-as-code engine (Rego) | Apache-2.0 | 12,307 | 2026-10-03 (today) | Extremely mature/active — largest community surveyed | **YES** — strong fit for purpose-limitation/consent rules gating record access |

---

## 3. Methods Table (metric quoted verbatim, source opened directly)

| Method / Claim | Metric (verbatim) | Source |
|---|---|---|
| Splink linkage speed | "Capable of linking a million records on a laptop in around a minute." | `moj-analytical-services/splink` GitHub README, accessed 2026-10-04 |
| Splink scale (big-data backend) | "Execute linkage in Python (using DuckDB) or big-data backends like Spark for 100+ million records." | `moj-analytical-services/splink` GitHub README, accessed 2026-10-04 |
| Splink algorithm basis | "Splink's linkage algorithm is based on Fellegi-Sunter's model of record linkage, with various customisations to improve accuracy." | `moj-analytical-services/splink` GitHub README, accessed 2026-10-04 |
| Splink user base | "empower Splink's 7 million users to gain a deeper understanding of bias within their data linkage processes" | Turing Internship Network (Fall 2023), "Ministry of Justice – Bias Analysis in Probabilistic Data Linkage" (ref. TIN-MOJ-002), PDF, accessed 2026-10-04 |
| MoJ's bias-analysis mandate | "Developing an analytical framework to assess the fairness and accuracy of the data linkage process, considering different demographic groups and any potential disparities in matching outcomes." | Same TIN-MOJ-002 PDF, accessed 2026-10-04 |
| Trillian maintenance status | "Trillian is in maintenance mode. The next generation of transparency logs uses Tiled APIs and are better supported by Tessera. We recommend that any new log operators first try Tessera." | `google/trillian` GitHub README, accessed 2026-10-04 |
| Trillian production use (caveat: self-reported, no named orgs listed) | "The Trillian codebase is stable and is used in production by multiple organizations, including many large-scale Certificate Transparency log operators." | `google/trillian` GitHub README, accessed 2026-10-04 |
| FHIR AuditEvent immutability rationale | "Servers that provide support for AuditEvent resources would not generally accept update or delete operations on the resources, as this would compromise the integrity of the audit record." | HL7 FHIR R5 spec, hl7.org/fhir/auditevent.html, accessed 2026-10-04 |
| FHIR AuditEvent scope | "A record of an event relevant for purposes such as operations, privacy, security, maintenance, and performance analysis." | HL7 FHIR R5 spec, hl7.org/fhir/auditevent.html, accessed 2026-10-04 |
| Tumult Analytics description | "Tumult Analytics is a Python library for privately computing aggregate queries on tabular data. It is built atop the Tumult Core library." | `opendp/tumult-analytics` GitHub repo description (GitHub REST API), accessed 2026-10-04 |
| anonlink description | "Python implementation of anonymous linkage using cryptographic linkage keys" | `data61/anonlink` GitHub repo description (GitHub REST API), accessed 2026-10-04 |
| clkhash description | "CLK hash: hash pii for entity matching" | `data61/clkhash` GitHub repo description (GitHub REST API), accessed 2026-10-04 |
| OpenCR description | "Open Client Registry Service" | `intrahealth/client-registry` GitHub repo description (GitHub REST API), accessed 2026-10-04 |
| Tessera description | "Go library for building tile-based transparency logs (tlogs)" | `transparency-dev/tessera` GitHub repo description (GitHub REST API), accessed 2026-10-04 |

**Note:** Pairwise precision/recall/F1 definitions, Schnell's Bloom-filter/CLK construction details, Vidanage/Christen attack success rates, and the Census TopDown epsilon/accuracy figures are all **real, well-known results in the literature** per convergent search-engine synthesis — but because I could not independently open the primary PDFs this pass (406 block, timeouts), I am deliberately **not** quoting any numeric metric for them. See §5 UNVERIFIED.

---

## 4. Innovation Room (one scalar metric per component)

1. **Linkage component** — Opportunity: hybrid Fellegi–Sunter (Splink) scoring + Indic transliteration/phonetic pre-blocking, with a human-reviewed "grey zone" queue for borderline scores.
   **Scalar metric to target:** *pairwise F1 score* on a gold-standard labelled sample of ICDS↔RCH↔U-WIN record pairs. **No existing published Indian benchmark for this was located in this pass** — this is a genuine opportunity to publish the first open Fellegi–Sunter + Indic-transliteration blocking benchmark for ICDS-type data, since IndicXlit itself is stale (no commits since 2023-10-13) and no comparable Indian linkage-accuracy study surfaced.

2. **Publication (disclosure control) component** — Opportunity: replace ad hoc small-cell suppression with a formal DP layer (OpenDP + Tumult Analytics) tuned for India's sub-district population denominators, which are typically far smaller than US Census geographies.
   **Scalar metric to target:** *epsilon (ε) privacy-loss budget per release cycle.* The US Census TopDown precedent for choosing ε exists but its specific schedule/value was **not verified** in this pass (PDF fetch timed out) — this remains an open parameter to be set via our own pilot utility-vs-privacy tradeoff analysis rather than copied from a confirmed published number.

3. **Audit component** — Opportunity: FHIR AuditEvent-schema records, backed by a Tessera tile-log (not Trillian — maintenance mode) for cryptographic tamper-evidence, gated by OPA policy-as-code for purpose limitation on every read of linked child-level data.
   **Scalar metric to target:** *Merkle-tree inclusion-proof verification latency as a function of log size.* Tessera is active (242 stars, pushed 2026-10-01) but **no benchmark numbers for Tessera's proof-generation/verification latency were independently verified this pass** — flagged as the next concrete thing to read before committing to it as the audit backbone.

---

## 5. UNVERIFIED / Open Questions

Everything below was **not** independently opened and read in full this pass (blocked, timed out, or simply not attempted due to the time budget) — treat as leads, not facts, until re-verified:

- **Schnell, Bachteler & Reiher (2009)**, "Privacy-Preserving Record Linkage Using Bloom Filters," *BMC Medical Informatics and Decision Making* — direct fetch returned **HTTP 406**; Bloom-filter/q-gram/Dice-coefficient description above is AI-search synthesis of secondary citations only.
- Schnell et al., "A Novel Error-Tolerant Anonymous Linking Code" (SSRN, 2011, the CLK follow-up) — not opened.
- "Evaluating privacy-preserving record linkage using cryptographic long-term keys and multibit trees" (PMC, 2017) — not opened.
- Vidanage, Christen et al.:
  - "Efficient Pattern Mining based Cryptanalysis for Privacy-Preserving Record Linkage" (ICDE 2019) — not opened.
  - "A Graph Matching Attack on Privacy-Preserving Record Linkage" (CIKM 2020) — **fetch timed out**, not opened; no re-identification success-rate number verified.
  - "Attacking and Hardening Bloom Filter Encoding" (Springer book chapter, 2020) — not opened.
  - "A Taxonomy of Attacks on Privacy-Preserving Record Linkage" (*Journal of Privacy and Confidentiality*, 2022) — not opened.
- US Census Bureau, "Disclosure Avoidance and the 2020 Census: How the TopDown Algorithm Works" (official brief PDF) — **curl timed out after 25s**, not opened; no epsilon value or block-level accuracy-loss number confirmed firsthand.
- Harvard Imai Lab, "Evaluating Bias and Noise Induced by the U.S. Census Bureau's Privacy Protection Methods" — not opened.
- India U-WIN FAQ (`uwin.mohfw.gov.in/faq`) and ABDM building blocks (`abdm.gov.in/abdm-components`) — not independently opened; the Aadhaar-less/"probabilistic matching" description rests entirely on AI-search synthesis, not a verbatim primary quote. **This is a priority re-verification item given it is central to our architecture.**
- AI4Bharat IndicXlit transliteration-accuracy metrics — search was rate-limited before any usable result returned; **no accuracy number found at all**, not even via synthesis.
- **No Indian-specific published study quantifying record-linkage error rates for transliterated Indic names was located** — real gap, not just an unopened source; worth a dedicated follow-up search pass.
- ONS disclosure-control numeric suppression threshold (e.g., a "fewer than 10" rule) — page opened but returned only a one-line stub; no number obtained. CDC/NCHS small-cell-suppression guidance was not attempted at all this pass.
- FHIR **Consent** resource (`hl7.org/fhir/consent.html`) — fetch failed (DNS/transport-level error); **completely unverified this pass**.
- OPA health-sector "purpose limitation" worked example — not found/verified; only OPA's generic popularity (12,307 stars) is confirmed.
- Tessera performance/benchmark numbers — not verified.
- fastLink's specific accuracy/scale claims beyond bare repo existence — not fetched.
- OpenCR/SanteMPI real-world deployment counts (e.g., number of OpenHIE country deployments) — not fetched.
- MoJ's actual Splink bias-analysis **results** (as opposed to the project proposal) — not located; only the Fall-2023 internship posting was found.

**Suggested immediate follow-ups for a Pass 2** (in priority order): (1) open `uwin.mohfw.gov.in/faq` and ABDM docs directly — this is load-bearing for our core architecture claim; (2) get the Schnell 2009 paper via an alternate route (Google Scholar cache / ResearchGate / sci-hub-free mirror) since BMC blocked direct access; (3) re-fetch the Vidanage CIKM 2020 PDF with a longer timeout or via arXiv mirror; (4) find a concrete small-cell-suppression numeric rule (CDC NCHS or India's own MoHFW data-release guidelines, if any exist); (5) search specifically for "Aadhaar-less record linkage India health study" / "ICDS data quality linkage" in PubMed/Google Scholar rather than general web search.

---

## 6. Sources

### Directly opened / verified (GitHub REST API or web_fetch returned real content)

1. GitHub REST API, `repos/open-policy-agent/opa`, 2026 (repo last pushed 2026-10-03), https://github.com/open-policy-agent/opa, accessed 2026-10-04.
2. GitHub REST API, `repos/opendp/opendp`, 2026 (repo last pushed 2026-10-03), https://github.com/opendp/opendp, accessed 2026-10-04.
3. GitHub REST API, `repos/santedb/santedb-server`, 2026 (repo last pushed 2026-10-03), https://github.com/santedb/santedb-server, accessed 2026-10-04.
4. GitHub REST API, `repos/opendp/tumult-analytics`, 2026 (repo last pushed 2026-09-30), https://github.com/opendp/tumult-analytics, accessed 2026-10-04.
5. moj-analytical-services, Splink GitHub README, 2026 (v5 released ~2026-09-28, repo pushed 2026-09-30), https://github.com/moj-analytical-services/splink, accessed 2026-10-04.
6. GitHub REST API, `repos/transparency-dev/tessera`, 2026 (repo last pushed 2026-10-01), https://github.com/transparency-dev/tessera, accessed 2026-10-04.
7. google, Trillian GitHub README, 2026 (repo last pushed 2026-10-02), https://github.com/google/trillian, accessed 2026-10-04.
8. GitHub REST API, `repos/data61/anonlink`, 2026 (repo last pushed 2026-05-19), https://github.com/data61/anonlink, accessed 2026-10-04.
9. GitHub REST API, `repos/kosukeimai/fastLink`, 2026 (repo last pushed 2026-02-28), https://github.com/kosukeimai/fastLink, accessed 2026-10-04.
10. UK Office for National Statistics, "Disclosure control" (methodology page, content thin/stub), n.d., https://www.ons.gov.uk/methodology/methodologytopicsandstatisticalconcepts/disclosurecontrol, accessed 2026-10-04.
11. GitHub REST API, `repos/intrahealth/client-registry` (OpenCR), 2025 (repo last pushed 2025-04-01), https://github.com/intrahealth/client-registry, accessed 2026-10-04.
12. GitHub REST API, `repos/data61/clkhash`, 2025 (repo last pushed 2025-05-12), https://github.com/data61/clkhash, accessed 2026-10-04.
13. The Alan Turing Institute, Turing Internship Network (Fall 2023), "Ministry of Justice – Bias Analysis in Probabilistic Data Linkage" (ref. TIN-MOJ-002, project proposal, not a results report), 2023, https://www.turing.ac.uk/sites/default/files/2023-08/tin_-_data_linking_bias_final.pdf, accessed 2026-10-04.
14. GitHub REST API, `repos/J535D165/recordlinkage`, 2024 (repo last pushed 2024-02-21), https://github.com/J535D165/recordlinkage, accessed 2026-10-04.
15. HL7 International, "AuditEvent" FHIR R5 resource specification (current published version), n.d. (live spec), https://www.hl7.org/fhir/auditevent.html, accessed 2026-10-04.
16. GitHub REST API, `repos/AI4Bharat/IndicXlit`, 2023 (repo last pushed 2023-10-13), https://github.com/AI4Bharat/IndicXlit, accessed 2026-10-04.
17. Anushka Vidanage, personal publications page (stub, links to Google Scholar only — no content extracted), n.d., https://anushkavidanage.github.io/publications.html, accessed 2026-10-04.

### Found via AI-search synthesis only — **UNVERIFIED**, not independently opened (listed for traceability per zero-hallucination rule; do not cite as confirmed fact)

18. Schnell, R., Bachteler, T., Reiher, J., "Privacy-Preserving Record Linkage Using Bloom Filters," *BMC Medical Informatics and Decision Making*, 2009 — **UNVERIFIED (HTTP 406 on direct fetch)**, https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/1472-6947-9-41, accessed 2026-10-04 (fetch attempt only).
19. Schnell, R. et al., "A Novel Error-Tolerant Anonymous Linking Code," SSRN, 2011 — **UNVERIFIED (not opened)**, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3549247, accessed 2026-10-04 (URL discovered via search only).
20. "Evaluating privacy-preserving record linkage using cryptographic long-term keys and multibit trees," PMC, 2017 — **UNVERIFIED (not opened)**, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5465525/, accessed 2026-10-04 (URL discovered via search only).
21. Vidanage, A. et al., "A Graph Matching Attack on Privacy-Preserving Record Linkage," CIKM, 2020 — **UNVERIFIED (fetch timed out)**, https://users.cecs.anu.edu.au/~Peter.Christen/publications/vidanage2020cikm.pdf, accessed 2026-10-04 (fetch attempt only).
22. Vidanage, A. et al., "Efficient Pattern Mining based Cryptanalysis for Privacy-Preserving Record Linkage," ICDE, 2019 — **UNVERIFIED (not opened)**, https://users.cecs.anu.edu.au/~Peter.Christen/publications/vidanage2019icde.pdf, accessed 2026-10-04 (URL discovered via search only).
23. Christen, P., Vidanage, A. et al., "Attacking and Hardening Bloom Filter Encoding," Springer book chapter, 2020 — **UNVERIFIED (not opened)**, https://link.springer.com/content/pdf/10.1007/978-3-030-59706-1_9, accessed 2026-10-04 (URL discovered via search only).
24. "A Taxonomy of Attacks on Privacy-Preserving Record Linkage," *Journal of Privacy and Confidentiality*, 2022 — **UNVERIFIED (not opened)**, https://journalprivacyconfidentiality.org/index.php/jpc/article/download/764/734/1826, accessed 2026-10-04 (URL discovered via search only).
25. US Census Bureau, "Disclosure Avoidance and the 2020 Census: How the TopDown Algorithm Works," census brief — **UNVERIFIED (curl timeout, not opened)**, https://www2.census.gov/library/publications/decennial/2020/census-briefs/c2020br-04.pdf, accessed 2026-10-04 (fetch attempt only).
26. Harvard Imai Lab, "Evaluating Bias and Noise Induced by the U.S. Census Bureau's Privacy Protection Methods" — **UNVERIFIED (not opened)**, https://imai.fas.harvard.edu/research/DASeval.html, accessed 2026-10-04 (URL discovered via search only).
27. Ministry of Health & Family Welfare (India), U-WIN FAQ — **UNVERIFIED (not opened)**, https://uwin.mohfw.gov.in/faq, accessed 2026-10-04 (URL discovered via search only).
28. National Health Authority (India), "ABDM Building Blocks – Components" — **UNVERIFIED (not opened)**, https://abdm.gov.in/abdm-components, accessed 2026-10-04 (URL discovered via search only).
29. HL7 International, "Consent" FHIR resource specification — **UNVERIFIED (fetch failed: DNS/transport error)**, https://www.hl7.org/fhir/consent.html, accessed 2026-10-04 (fetch attempt only, no content retrieved).
