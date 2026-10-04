# Landscape — automated TRL assessment from technical documents

_v0, 2026-10-04 07:30 IST, project lead (lean mode: written without sub-agents after the overnight network outage). Access date for every source below: 2026-10-04. Rule: a source is cited only if it was opened in this session; anything else is marked **UNVERIFIED** and is a lead, not evidence._

## 1. What "TRL" means — the rubrics the judges will likely use

| Source (opened) | What it says (checked against the source) | Use for us |
|---|---|---|
| NASA SCaN, *Technology Readiness Levels* — <https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/> | 9 levels. TRL 1 "scientific research is beginning"; TRL 2 "very speculative… little to no experimental proof of concept"; TRL 3 "analytical and laboratory studies… a proof-of-concept model is constructed"; TRL 4 "multiple component pieces are tested with one another"; TRL 5 "breadboard… more rigorous testing… environments as close to realistic as possible"; TRL 6 "fully functional prototype or representational model"; TRL 7 prototype "demonstrated in a space environment"; TRL 8 "flight qualified"; TRL 9 "flight proven during a successful mission". | Level descriptors for the evidence taxonomy; note the space-specific wording at 7–9. |
| European Commission, *Horizon 2020 WP 2014–2015, General Annex G: Technology readiness levels* — <https://ec.europa.eu/research/participants/data/ref/h2020/wp/2014_2015/annexes/h2020-wp1415-annex-g-trl_en.pdf> | TRL 1 basic principles observed · 2 technology concept formulated · 3 experimental proof of concept · 4 technology validated in lab · 5 technology validated in relevant environment (industrially relevant for KETs) · 6 technology demonstrated in relevant environment · 7 system prototype demonstration in operational environment · 8 system complete and qualified · 9 actual system proven in operational environment (competitive manufacturing for KETs; or in space). | Domain-neutral wording — the best default for a UN ESCAP / developing-economies evaluation set that is not space-specific. Our gap analysis cites these criteria. |
| ISO, *ISO 16290:2013 Space systems — Definition of the Technology Readiness Levels (TRLs) and their criteria of assessment* — <https://www.iso.org/standard/56064.html> | Catalogue page title confirmed. The standard's text is paywalled — its criteria are **UNVERIFIED** here. | Cite as the formal standard; do not quote its criteria until read. |
| US DOE, *Technology Readiness Assessment Guide* (DOE G 413.3-4A) — directives page <https://www.directives.doe.gov/directives-documents/400-series/0413.3-EGuide-04a> | Page opened (title "Directives, Guidance, and Delegations"); the guide's contents were not read — **UNVERIFIED**. | Lead: DOE adapts TRL to non-space (energy/process) technologies — relevant to APCTT's sectors. |
| US DoD *TRA Guidebook* (2023) and GAO *Technology Readiness Assessment Guide* (GAO-20-48G) | Guessed DoD URL returned 404; gao.gov returned 403 to our client. **UNVERIFIED** — re-open in a browser. | Leads for "critical technology element" decomposition and evidence standards. |
| AFRL TRL Calculator; NASA TRL "Calculator"-style checklists | Not opened — **UNVERIFIED** leads. | A checklist-of-questions format is the natural shape for an auditable gap analysis. |

**Takeaway.** The rubrics agree on a structure our system can exploit: each level is defined by *what has been demonstrated* (principle → concept → proof of concept → lab validation → relevant-environment validation → relevant-environment demonstration → operational prototype → qualified system → proven system) and *where* (paper → lab → relevant environment → operational environment). Those two axes — **demonstration type × environment fidelity** (plus integration scale: component → subsystem → system) — are the evidence features a document actually contains, and the "next level's missing criterion" is the gap.

## 2. Published work on automated TRL estimation

| Work | Status of our check | Relevance |
|---|---|---|
| Lavin, Gilligan-Lee et al., *Technology Readiness Levels for Machine Learning Systems*, arXiv:2101.03989 (2021) — <https://arxiv.org/abs/2101.03989> | Title/ID/date opened. | A TRL framework for ML systems (MLTRL); relevant when the document under assessment is itself an AI system. Not an estimator. |
| Gourdin, Richard, Mattioli (Thales), *How to Assess the Technology Readiness Levels of an AI-based System?*, PESARO 2026 — <https://www.thinkmind.org/articles/pesaro_2026_1_10_68001.pdf> | PDF opened; abstract read: TRL needs "a more nuanced assessment" for AI systems because of reliance on dataset/knowledge-base quality, model adaptability and dynamic performance. | Industry (Thales) practice is **checklist-based, expert-in-the-loop** assessment — confirms our "rubric checklist + evidence" output shape. |
| "A Bibliometric Approach to Characterizing TRLs Using Machine Learning" (AIAA 2023-2686, Georgia Tech/Mavris group per search snippet) | **UNVERIFIED** — surfaced by search; not opened. | Lead: bibliometric (publication/patent/award counts) TRL regression. Different input (metadata, not one document). |
| Fraunhofer ISI, "Predicting Tech Readiness through Bibliometric Analysis using Unsupervised ML" (ISPIM 2025) | **UNVERIFIED** — the link returned an HTML stub, not the paper; the "84.9%" figure in the search snippet is not verified. | Lead, same family as above. |
| Springer 2025, "Developing an Approach for Automated Data Collection and Mining Using…" (doi 10.3103/S0005105525700670) | **UNVERIFIED** — not opened. | Lead: LLM + scraping to extract maturity statements. |

**Gap we observed (from what we could open):** published automated-TRL work is either a *framework* (MLTRL, Thales) or *bibliometric* (counts of papers/patents/awards over time). We found **no opened source** that predicts TRL from the *text of a single document* with an ordinal model, evidence spans and a gap analysis, and no public benchmark for it. That is exactly the APCTT task — the field is open, and a reproducible public benchmark (below) is itself a contribution.

## 3. Labelled public data

| Source | Verified facts | Label quality / caveats |
|---|---|---|
| **NASA TechPort** public API — <https://techport.nasa.gov/api/projects?updatedSince=1990-01-01> and `/api/projects/{id}` | Opened 2026-10-04: no API key needed; the index lists **21,046** projects; each record carries `trlBegin`, `trlCurrent`, `trlEnd`, `description`, `benefits`, `title`, `status`, program, taxonomy, organisations and library items. Latency ≈6 s/request, so a full crawl takes hours. Our resumable fetcher pulled a **seeded random 11,427-record sample** (54%); **8,587** have a ≥200-char description and a TRL (see `data/techport/`). | Labels are NASA-assigned TRLs at project start, now and target. Text is a project description (proposal-style), not a patent or paper, so expect a genre shift vs the hidden set. The SBIR/STTR share is large (program metadata exists but we deliberately **do not** use it as a feature). |
| EU CORDIS (Horizon projects; topic texts state expected TRLs) | **UNVERIFIED** — not opened tonight. | Weak labels (call-level expected TRL ranges), multilingual partner text — candidate for domain robustness. |
| SBIR.gov awards (phase I/II/III) | **UNVERIFIED** — not opened tonight. | Phase is a weak proxy for TRL; useful only as a noisy prior. |
| Patents (USPTO/Google Patents/Lens), papers (arXiv/OpenAlex) | Not opened tonight. | No TRL labels — candidates for *teacher-labelled* (LLM + rubric) or rule-labelled weak supervision; must respect "approved public data" once the 10 Oct guide defines it. |

## 4. Methods (ordinal prediction, evidence, calibration)

- **Ordinal regression.** CORAL — Cao, Mirjalili, Raschka, *Rank consistent ordinal regression for neural networks…*, arXiv:1901.07884 (2019, opened). CORN — Shi, Cao, Raschka, *Deep Neural Networks for Rank-Consistent Ordinal Regression Based On Conditional Probabilities*, arXiv:2111.08851 (2021, opened). Classical cumulative decomposition: Frank & Hall, *A Simple Approach to Ordinal Classification*, ECML 2001, doi:10.1007/3-540-44795-4_13 (DOI page blocked by a bot challenge — **link UNVERIFIED**; the method is implemented in our baseline `eval/baseline_tfidf.py`). All three turn K-class ordinal prediction into K−1 "is TRL > k?" decisions, which makes the output a *cumulative distribution* — exactly what an auditable "criteria for level k+1 met / not met" gap analysis needs.
- **Metric-aware decoding.** From a predictive distribution over 1–9 you can choose the decision that is optimal for the scoring rule: mode for exact accuracy, median for MAE, threshold-tuned for QWK. Our baseline reports all three decodings (§6) because the official "ordinal accuracy & precision" metric is not yet published.
- **Open-weight LLMs offline** (Qwen3, Phi-4, Gemma 3, Llama) — **not benchmarked tonight**; size and CPU-latency claims are UNVERIFIED until we measure them on the M5 (Phase 4b).

## 5. What companies ship today

| Company / product (page opened) | What the opened page shows | TRL-specific capability |
|---|---|---|
| Patsnap AI — <https://www.patsnap.com/ai> ("AI IP and R&D Agent") | AI agent over patents and R&D literature (title-level). | **UNVERIFIED** — no static-HTML mention of TRL or maturity. |
| Patsnap Eureka Engineering — <https://eureka.patsnap.com/rd-landing> ("AI-Powered R&D Solution Finder & Tech Intelligence") | R&D solution finder / tech intelligence. | **UNVERIFIED** (same check). |
| Mergeflow Spark — <https://www.mergeflow.com/> ("AI, purpose-built for Engineering Research and Technology Intelligence") | Technology-intelligence AI. | **UNVERIFIED** (same check). |
| ITONICS — <https://www.itonics-innovation.com/> ("The Platform for Enterprise R&D and Innovation") | Innovation/R&D portfolio platform. | **UNVERIFIED** (same check). |
| Cypris — comparison article <https://cypris.ai/insights/patsnap-alternatives-in-2026-7-r-d-intelligence-platforms-for-enterprise-teams-that-need-more-than-patent-search> | Vendor-authored comparison of R&D-intelligence platforms (opened; marketing content). | **UNVERIFIED**. |
| Thales (internal practice, via the PESARO 2026 paper above) | Checklist-based TRL assessment for AI-based systems. | Verified from the paper's abstract: framework/checklist, not an automated text classifier. |

**Reading.** The tech-scouting/IP-analytics market ships *search, landscaping and LLM agents over patents and papers*. In the static pages we opened, none publicly documents a calibrated, evidence-cited TRL 1–9 predictor with a gap analysis. A vendor-neutral, offline, open-weight, auditable TRL assessor fits APCTT's mandate (technology transfer in developing economies, where proprietary SaaS is a barrier), and that is where we position the system. We borrow the vendors' *evidence-linked answers* pattern and beat them on **transparency** (every level decision traces to quoted spans and a named rubric criterion), **cost/offline use** and **reproducibility** (public benchmark + frozen eval).

## 6. Our first public benchmark (real numbers)

See [`../eval/README.md`](../eval/README.md): TechPort v0 frozen grouped split, text-only baselines on CPU. On `trl_current` (n_test=1,657), hashed TF-IDF ridge reaches QWK 0.314 / MAE 1.053, against QWK 0.000 / MAE 1.112 for the majority class.

## 7. Open research threads (next, once lean mode lifts)
1. Re-open DoD/GAO/DOE TRA guides in a browser; extract each level's *evidence standard* into `architecture/contracts/rubric_eu_nasa.json` (v0 already uses EU + NASA wording).
2. Read ISO 16290 (library access) — confirm criteria wording.
3. Verify the bibliometric TRL papers (AIAA 2023-2686, ISPIM 2025) and look for any document-level TRL classifier we may have missed (ACL Anthology, Semantic Scholar).
4. CORDIS topic-TRL and SBIR-phase weak labels; patents/papers for genre-shift evaluation.
5. Benchmark small open-weight LLMs offline (latency/accuracy) as evidence extractors and as a zero-shot TRL rater.
