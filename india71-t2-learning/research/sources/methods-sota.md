> **DRAFT — contribution by research subagent.** This file did not exist prior to this
> contribution (checked: `india71-t2-learning/research/sources/` was empty at start).
> Content covers Methods 1–5 only, as scoped. Merge/reconcile with any parallel
> contributions before treating as final. All access dates are **2026-10-04** unless
> otherwise noted. Items I could not independently verify in-session are explicitly
> marked **UNVERIFIED**.

# Methods SOTA — Techfest 2026 India @71/100, Theme 2 (Learning)
Ordered **newest first** within each method section.

---

## Method 1 — IRT for early-grade assessment + mirt / TAM / py-irt / girth maintenance status

### Package maintenance snapshots (checked via GitHub API, 2026-10-04)

- **mirt** (R) — GitHub mirror `philchalmers/mirt`.
  - Last push: `2026-10-03T03:24:23Z`; last commit `2026-10-03T01:16:01Z`, message "missed new ref", sha `5213f2dc0e6da866fbf09da0ffe6fd021a047253`.
  - Recent tags: `v.1.47`, `v1.46.1`, `v1.45.1` (tag list truncated to top 3).
  - Source: https://github.com/philchalmers/mirt (commits/tags endpoints), accessed 2026-10-04.
  - **Actively maintained** — commit same day as access date.
  - CRAN description (https://cran.r-project.org/web/packages/mirt/index.html, accessed 2026-10-04): "Analysis of discrete response data using unidimensional and multidimensional item analysis models under the Item Response Theory paradigm (Chalmers (2012) doi:10.18637/jss.v048.i06)." Also: "latent class models such as the DINA, DINO, multidimensional latent class, mixture IRT models... are supported" — i.e., mirt overlaps into Method 2 (CDM) territory via DINA/DINO support.

- **TAM** (R, "Test Analysis Modules") — GitHub mirror `alexanderrobitzsch/TAM`.
  - Last push: `2025-08-28T23:10:49Z`; last commit `2025-08-28T23:08:19Z`, sha `8fc1c216ff8bfd8a354ae760662a4897ae46a291`.
  - Source: https://github.com/alexanderrobitzsch/TAM (commits endpoint), accessed 2026-10-04.
  - **Maintained but slower cadence** than mirt (~13 months since last commit as of access date).
  - CRAN description (https://cran.r-project.org/web/packages/TAM/index.html, accessed 2026-10-04): "Includes marginal maximum likelihood estimation and joint maximum likelihood estimation for unidimensional and multidimensional item response models. The package functionality covers the Rasch model, 2PL model, 3PL model, generalized partial credit model, multi-faceted Rasch model, nominal item response model, structured latent class model, mixture distribution IRT models, and located latent class models." Cites Adams, Wilson & Wang 1997 (doi:10.1177/0146621697211001) and Adams, Wilson & Wu 1997 (doi:10.3102/10769986022001047) — TAM is the R implementation lineage closest to the ConQuest/ACER large-scale-assessment tradition used in international surveys (PISA-style scaling), relevant to early-grade LSA linking.

- **py-irt** (Python, Bayesian IRT via Pyro) — `nd-ball/py-irt`.
  - Repo: `pushed_at: 2026-09-01T21:32:43Z`, `updated_at: 2026-09-24T09:24:14Z` (GitHub API, accessed 2026-10-04).
  - Latest default-branch commit: sha `6514928ec753771c8858bf16581e9715d6025ed9`, date `2026-06-19T12:15:00Z`.
  - `pyproject.toml` (https://raw.githubusercontent.com/nd-ball/py-irt/master/pyproject.toml, accessed 2026-10-04) shows `version = "0.7.1"`, deps `torch = "^2.2.0"`, `pyro-ppl = "^1.8.6"`, `python = ">=3.9,<3.12"` — actively updated to modern PyTorch/Python ranges.
  - README (https://github.com/nd-ball/py-irt, accessed 2026-10-04): "At present, the one parameter logistic (1PL) model, aka Rasch model, two parameter logistic model (2PL) and four parameter logistic model (4PL) have been implemented... fitting Item Response Theory (IRT) models using variational inference." Points to the **EACL 2024 IRT4NLP tutorial** (https://eacl2024irt.github.io/notebooks/2_IntroToIRT_jupyter.html) as the current usage reference — i.e., primary current documentation is a 2024 tutorial, not just the README.
  - Core citations in README: Lalor, Wu & Yu, EMNLP 2019 ("Learning Latent Parameters without Human Response Patterns: Item Response Theory with Artificial Crowds"); Rodriguez et al., ACL-IJCNLP 2021 ("Evaluation Examples Are Not Equally Informative: How Should That Change NLP Leaderboards?").
  - **Note on applicability**: py-irt's primary use-case lineage is NLP-model/leaderboard evaluation (treating test examples as "items" and models as "examinees"), not originally built for K-12 student assessment — relevant caveat for Theme 2 adoption.

- **girth** (Python, classical/Bayesian IRT) — `eribean/girth`.
  - Repo: `pushed_at: 2022-09-09T23:53:56Z` (GitHub API, accessed 2026-10-04) — **last code push over 4 years before access date; effectively stale/unmaintained** relative to mirt/py-irt/pykt-toolkit.
  - Latest GitHub Release: tag `v0.8.0`, name "Directory Refactor", `published_at: 2021-11-11T01:58:40Z` (https://github.com/eribean/girth/releases, accessed 2026-10-04). Release notes text: "No major features or bugs were fixed in this release. The dependency on Numba was removed to address some issue. This release, and others moving forward, should play nice with google colab and pyodide."
  - README (https://github.com/eribean/girth, accessed 2026-10-04) lists coverage: Rasch/1PL (JML, conditional, MML), 2PL (JML/MML/mixed EAP-MML), 3PL (MML, "No Optimization and Minimal Support"), Graded Response Model, Partial Credit Model, Graded Unfolding Model, plus synthetic data generators. Also points to a companion `girth_mcmc` package for Bayesian/variational estimation (not independently checked in this session — **UNVERIFIED** maintenance status of girth_mcmc).
  - **Maintenance verdict**: girth is feature-complete for classical dichotomous/polytomous unidimensional IRT but shows no recent commits; treat as a "frozen reference implementation" rather than an actively evolving tool for a 2026 build.

### Early-grade assessment relevance (contextual, not package-specific)
- No early-grade-specific IRT package found distinct from the general-purpose tools above; early-grade programs (e.g., ASER/Pratham-style oral tests) typically apply these general IRT tools (mirt/TAM in R) to binary/graded item data rather than using a bespoke "early-grade IRT" library. **UNVERIFIED** — did not find a maintained, early-grade-specific IRT package in this session; flagging as a possible gap rather than asserting one doesn't exist.

---

## Method 2 — Cognitive diagnosis models (CDM): G-DINA / EduCDM / pyCDM and 2024–2026 work

### Package status
- **GDINA** (R) — CRAN page (https://cran.r-project.org/web/packages/GDINA/index.html, accessed 2026-10-04): "A set of psychometric tools for cognitive diagnosis modeling based on the generalized deterministic inputs, noisy and gate (G-DINA) model by de la Torre (2011) doi:10.1007/s11336-011-9207-7 and its extensions, including the sequential G-DINA model by Ma and de la Torre (2016) doi:10.1111/bmsp.12070 for polytomous responses, and the polytomous G-DINA model by Chen and de la Torre doi:10.1177/0146621613479818 for polytomous attributes." Tutorials cited: Ma & de la Torre 2020 (doi:10.18637/jss.v093.i14), Ma & de la Torre 2019 (doi:10.1111/emip.12262).
  - GitHub mirror `Wenchao-Ma/GDINA`: `pushed_at: 2026-09-16T13:49:36Z`, last commit sha `f612d2dc9c9f9091fc699745e6ce524759c54f98` dated `2026-09-16T13:47:23Z` (GitHub API, accessed 2026-10-04) — **actively maintained**, commit ~2.5 weeks before access date.

- **EduCDM** (Python, "Model Zoo of Cognitive Diagnosis Models") — `bigdata-ustc/EduCDM`.
  - Repo: `pushed_at: 2024-10-25T06:01:41Z` (GitHub API, accessed 2026-10-04).
  - Releases (https://github.com/bigdata-ustc/EduCDM, accessed 2026-10-04): `v1.0.1` published `2024-10-25T06:01:41Z`; `v1.0.0` published `2024-10-24T02:52:04Z`; `v0.0.13` published `2022-01-30T02:47:00Z`. So the jump from v0.0.13 → v1.0.0/v1.0.1 happened within two days in Oct 2024, then **no further releases through the 2026-10-04 access date** (~2 years quiet on releases, though repo metadata shows later `updated_at` which can reflect non-code GitHub activity).
  - README (https://github.com/bigdata-ustc/EduCDM, accessed 2026-10-04): "The Model Zoo of Cognitive Diagnosis Models, including classic Item Response Ranking (IRT), Multidimensional Item Response Ranking (MIRT), Deterministic Input, Noisy 'And' model (DINA), and advanced Fuzzy Cognitive Diagnosis Framework (FuzzyCDF), Neural Cognitive Diagnosis Model (NCDM), Item Response Ranking framework (IRR), Incremental Cognitive Diagnosis (ICD) and Knowledge-association based extension of NeuralCD (KaNCD)." Underlying papers cited inline: NeuralCD = Wang et al., AAAI (Fei Wang paper PDF link on USTC staff page); KaNCD cites IEEE document (ieeexplore.ieee.org/document/9865139).

- **pyCDM**: no actively-maintained, purpose-built Python package under this exact name was found. Closest current analogues identified via search (not independently fetched/verified in-session beyond titles — **UNVERIFIED** for these three):
  - `InsCD` (`ECNU-ILOG/InsCD`) — "A Modularized, Comprehensive and User-Friendly Toolkit for Machine Learning Empowered Cognitive Diagnosis" per GitHub API description (accessed 2026-10-04). Repo `pushed_at: 2025-11-27T12:19:29Z`, last commit same timestamp, sha `ddce0f28e7b7f34589fd3d498cbcedada8bb4e33` — **actively maintained** (~10 months before access date), and the most recently-updated CDM toolkit found among the Python options.
  - `pygdina` (`jiewenTsai/pygdina`) — described as a pure-Python G-DINA implementation (title only, not fetched: "pyGDINA: Pure-Python Cognitive Diagnosis..."). **UNVERIFIED** — not fetched directly.
  - A PyPI package literally named `Pycdm` exists but search summary suggests it is unrelated to educational cognitive diagnosis (possibly a CONTENTdm metadata client) — **UNVERIFIED**, flagging as likely a false-positive name match, not a recommended tool.

### 2024–2026 research directions
- **Survey**: Liu et al. (or listed authorship per arXiv), "A Survey of Models for Cognitive Diagnosis: New Developments and Future Directions," arXiv:2407.05458 (July 2024). Fetched text (https://arxiv.org/html/2407.05458, accessed 2026-10-04), Introduction: "Cognitive diagnosis, as a representative, aims to measure the cognitive status of individuals, especially the ability levels such as knowledge structures and processing skills, so as to provide information about their cognitive strengths and weaknesses (Leighton and Gierl, 2007)." The survey frames cognitive diagnosis as inferring latent, multi-skill mastery profiles rather than a single ability score — the key practical distinction from Method 1 IRT for Theme 2 diagnostic (vs. ranking) use cases.
- **Concept-Aware Latent and Explicit Knowledge Integration for Enhanced Cognitive Diagnosis (CLEKI-CD)**, arXiv:2502.02104 (Feb 2025). Confirmed title via https://arxiv.org/abs/2502.02104 (accessed 2026-10-04); full text not rendered as markdown (PDF binary returned) — **UNVERIFIED** beyond title/date; addresses incompleteness of binary Q-matrix via an attention-based latent Q-matrix per secondary search summary (not independently confirmed from primary text in-session).
- Other 2024–2025 items surfaced only via search-engine summary, **not independently fetched from primary source — mark all as UNVERIFIED**:
  - "Q-matrix-Constrained Neural Network (QNN)" / SOM-NN unsupervised training variant, cited to a Springer/Behavior Research Methods article (doi via link.springer.com/article/10.3758/s13428-024-02404-5).
  - "GE-QCDM" (genetic-evolution Q-matrix enhancement), cited to ECAI 2025 proceedings (journals.sagepub.com/doi/pdf/10.3233/FAIA251263).

---

## Method 3 — Knowledge tracing: pyKT / simpleKT / LLM-KT 2024–2026 and sparse periodic-assessment suitability

### pyKT toolkit
- `pykt-team/pykt-toolkit` — repo `pushed_at: 2026-09-22T06:03:56Z`, latest commit same date, sha `77c3e90fdb807542194b989656ccac10e5d92e12` (GitHub API, accessed 2026-10-04) — **actively maintained**, ~2 weeks before access date.
- README (https://github.com/pykt-team/pykt-toolkit, accessed 2026-10-04): "pyKT is a python library build upon PyTorch to train deep learning based knowledge tracing models. The library consists of a standardized set of integrated data preprocessing procedures on more than 7 popular datasets across different domains, 5 detailed prediction scenarios, more than 10 frequently compared DLKT approaches for transparent and extensive experiments." Links to website https://pykt.org/ and docs at pykt-toolkit.readthedocs.io.
- Implemented model list per README includes (exact names as given): DKT, DKT+, DKT-Forget, KQN, DKVMN, ATKT, GKT, SAKT, SAINT, AKT, HawkesKT, IEKT, SKVMN, LPKT, QIKT, RKT, DIMKT (list truncated by fetch; "simpleKT" is documented separately — see below — and is part of the pyKT family per its own README pointer).

### simpleKT
- Paper: Liu, Z., Liu, Q., Chen, J., Huang, S., Luo, W. "simpleKT: A Simple But Tough-to-Beat Baseline for Knowledge Tracing." ICLR 2023. arXiv:2302.06881.
- Fetched body text (https://ar5iv.labs.arxiv.org/html/2302.06881, accessed 2026-10-04), §4.4 Experimental Results: "simpleKT almost always ranks top 3 in terms of AUC scores and achieves 55 wins, 3 ties and 18 loss in total against 12 baselines on 7 public datasets of different domains." Method basis per abstract/search summary (not independently re-quoted from a second primary passage): uses the Rasch model (an IRT formulation — direct bridge from Method 1 into KT) for question-specific variation plus a simple dot-product (not multi-layer) attention mechanism for time-aware modeling.
- Code: https://github.com/pykt-team/pykt-toolkit (same repo as above — confirms simpleKT is maintained as part of the actively-updated pyKT codebase, not a separate stale repo).
- Relevance to this Challenge: simpleKT is presented explicitly as a "baseline" intended to be hard to beat with more complex architectures — relevant for Theme 2 if the team needs a defensible, computationally cheap, strong KT baseline rather than a heavyweight transformer.

### LLM-based KT, 2024–2026
- Survey: "A Systematic Review of Knowledge Tracing and Large Language Models in Education: Opportunities, Issues, and Future Research," arXiv:2412.09248 (Dec 2024). Title confirmed via https://arxiv.org/abs/2412.09248 (accessed 2026-10-04); body text not rendered in this session (abstract page returned only the title due to arXiv's JS-gated abstract) — **mark specific claims below as UNVERIFIED beyond title/date**, sourced instead from a secondary search-engine synthesis:
  - Per search synthesis only (not independently confirmed from primary text): the review frames LLM integration into KT as addressing predictive-accuracy and interpretability limits of classical KT, particularly for "sparse and cold-start scenarios," and surveys architectures using in-context learning / agent-based reasoning / feature enrichment.
- Related 2024 paper referenced by the same search synthesis: "Difficulty-Focused Contrastive Learning for Knowledge Tracing with a Large Language Model" — ACL Anthology 2024.lrec-main.438 (https://aclanthology.org/2024.lrec-main.438/). **Not independently fetched in-session — UNVERIFIED**, but the ACL Anthology URL itself is a legitimate, citable primary-source venue if a follow-up session fetches and confirms it.
- "DDKT" (Dual-channel Difficulty-aware Knowledge Tracing), cited to a 2025 IEEE BigData proceedings page (computer.org/csdl/proceedings-article/bigdata/2025/11402203) per search synthesis — **UNVERIFIED**, not independently fetched.
- "LLM-KT: Aligning Large Language Models with Knowledge Tracing," arXiv:2502.02945 — title surfaced via search citation only; **UNVERIFIED**, not independently fetched in this session.

### Suitability for sparse / periodic assessment (Theme 2's core constraint)
- No primary source in this session directly benchmarks classic DLKT (pyKT models) vs. LLM-KT specifically under sparse/periodic (as opposed to dense/continuous) student-interaction logs with controlled, quoted numbers. The search-engine synthesis claims LLM-augmented KT "is particularly effective under sparse or periodic assessment regimes... compensating for the lack of frequent, dense student performance data" — **this entire claim is UNVERIFIED against a primary source** and should be treated as a hypothesis to test against the actual cited papers (2412.09248, the DDKT paper, 2024.lrec-main.438), not as an established fact, until a follow-up fetch confirms it from the paper text/tables.
- **Gap to flag explicitly for the main agent**: classic KT models (DKT, AKT, simpleKT, etc.) are generally benchmarked on dense interaction-log datasets (ASSISTments, EdNet, etc.) with many observations per student; none of the pyKT README's listed datasets were confirmed in this session to be low-frequency/periodic-assessment style (e.g., termly/annual test administrations typical of Theme 2's India @71 context). This is a load-bearing uncertainty for picking KT vs. CDM vs. IRT-linking as the core method.

---

## Method 4 — Computerized adaptive testing / classification testing (CAT/SPRT) and early-grade ORF/CAT

- **SPRT in testing — origin and application**: Wald's Sequential Probability Ratio Test, applied to adaptive/tailored testing and computerized classification/mastery testing. Per search synthesis (not independently fetched from primary Reckase/Eggen texts in this session — **UNVERIFIED pending primary fetch**):
  - Reckase (1983), "The Use of the Sequential Probability Ratio Test in Making Grade Classifications in Conjunction with Tailored Testing" — full report hosted at ERIC: https://files.eric.ed.gov/fulltext/ED208006.pdf.
  - Eggen, T.J.H.M. (1999), "Item selection in adaptive testing with the sequential probability ratio test," Applied Psychological Measurement, 23(3), 249–261 — indexed at https://psycnet.apa.org/record/1999-11079-007 and https://eric.ed.gov/?id=EJ596309. Search synthesis states Eggen compared Fisher-information vs. Kullback-Leibler-information item-selection criteria within SPRT-driven classification and found KLI-based selection "often performed as well or better."
  - A Cito (Dutch National Institute for Educational Measurement) technical document, "The Sequential Probability Ratio Test in Educational Testing" (https://cito.nl/media/aumjtart/the-sequential-probability-ratio-test-in-educational-testing.pdf) was located but returned only as raw PDF binary in this session — **not read; UNVERIFIED content, URL only confirmed to resolve**.
  - Mechanism as described by search synthesis (standard SPRT logic, cross-checked against general statistical knowledge of Wald's test, not specific to this source): item-by-item likelihood-ratio accumulation against preset upper/lower bounds derived from target Type I/II error rates, stopping as soon as a classification (e.g., "master"/"non-master") decision boundary is crossed, which is what gives CAT/SPRT its item-count efficiency over fixed-length tests.
- **Early-grade ORF/CAT specifically**: No primary source was located and fetched in this session that documents a specific, named computerized-adaptive oral-reading-fluency (ORF) instrument with verifiable numbers (e.g., RTI International's EGRA is the dominant early-grade reading tool globally, but this session did not confirm whether/which EGRA deployments use CAT/SPRT item-selection logic rather than fixed-form administration). **Mark as an open research gap**, not a negative finding — a follow-up session should fetch RTI International's EGRA toolkit documentation and any World Bank/USAID technical reports describing adaptive scoring/stopping rules for oral reading fluency specifically, since none of that was independently verified here.

---

## Method 5 — Linking heterogeneous assessments: UIS policy linking / GPF / AMPL / IEA Rosetta Stone / Angrist 2021 HLO / equating

### UIS Global Proficiency Framework (GPF) + Policy Linking
- Primary documents located (URLs confirmed to exist via search; **full text not independently fetched in this session** — one direct fetch attempt to the WG-GAML-5 summary PDF returned HTTP 403, so treat details below as **UNVERIFIED pending a successful fetch**):
  - "POLICY LINKING FOR MEASURING GLOBAL LEARNING OUTCOMES — UPDATES" (WG-GAML 5th meeting summary), UIS, https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/08/WG-GAML-5-summary-Policy-Linking-Summary.pdf (fetch attempted 2026-10-04, returned 403 — URL/date of document per filesystem path suggests 2025/08 vintage, **not independently confirmed**).
  - "Aligning and reporting on indicator 4.1.1: UIS annotated workflow," https://www.uis.unesco.org/sites/default/files/medias/fichiers/2025/07/4.1.1_Aligning-and-reporting_SDG-4.1.1_2023.03.28.pdf (filename embeds an internal date of 2023-03-28; hosting-folder path suggests a 2025/07 republish — **discrepancy flagged, not resolved in-session**).
  - "4.4.c About Policy Linking," UIS Learning Data Resource Center, https://learningdata.uis.unesco.org/index.php/navigator/what-are-the-options-for-reporting-on-sdg-indicator-4-1-1/4-4-what-if-a-country-uses-national-assessments/4-4-c-about-policy-linking/ — not independently fetched; **UNVERIFIED** content beyond URL.
  - "Eligibility criteria for reporting against SDG 4.1.1: A discussion paper," ACER, https://people.acer.org/en/publications/eligibility-criteria-for-reporting-against-sdg-411-a-discussion-p/ — not independently fetched; **UNVERIFIED**.
- Conceptual summary of GPF + policy linking (per search-engine synthesis only, **not confirmed against primary text in this session — treat as plausible but unverified**): GPF supplies standardized proficiency-level descriptors for reading/mathematics across grades 1–9; policy linking is the process by which a country's own national/subnational assessment is mapped onto GPF minimum-proficiency-level (MPL) cut-points via expert panel review, rather than via statistical equating — positioned as low-cost/fast relative to large-scale statistical linking, and usable even by countries that don't participate in PISA/TIMSS.

### AMPL
- Initial search for "AMPL" (expected: "Analysis of Mapping to the Proficiency Levels" or similar World Bank/UIS linking methodology acronym) did **not** return a clearly matching, independently confirmed primary source in this session. **This is an explicit gap**: I was not able to verify what "AMPL" stands for, its authors, or a specific technical reference in the time available. Flag for the main agent / a follow-up fetch — do not assume it is the same thing as "policy linking" above without checking a primary UIS/World Bank glossary.

### IEA Rosetta Stone
- Search intent executed ("IEA Rosetta Stone methodology linking TIMSS PIRLS national assessments") but the search call hit a rate limit and was not successfully re-run with enough remaining budget in this session to retrieve and fetch a primary IEA source. **UNVERIFIED / NOT RESEARCHED** — this sub-topic needs a dedicated follow-up: search for "IEA Rosetta Stone" directly against iea.nl / iea-popup or ILSA-gateway sources, since the generic query above did not surface it distinctly from the UIS/GPF results already captured.

### Angrist et al. (2021) — Harmonized Learning Outcomes (HLO)
- Citation: Angrist, N., Djankov, S., Goldberg, P.K., & Patrinos, H.A. (2021). "Measuring human capital using global learning data." *Nature*, 592, 403–408. https://doi.org/10.1038/s41586-021-03323-7 (direct fetch of nature.com returned HTTP 406 in this session — title/author/journal/volume/page/DOI triangulated via search synthesis and the World Bank Data Catalog page below, not from the Nature page itself).
- **World Bank Data Catalog entry** (fetched directly, https://datacatalog.worldbank.org/search/dataset/0038001/harmonized-learning-outcomes-hlo-database, accessed 2026-10-04) — exact quote: "The Harmonized Learning Outcomes (HLO) database bridges this gap by constructing a globally comparable database of 164 countries from 2000 to 2017. The data represent 98% of the global population and developing economies comprise two-thirds of the included countries. The data is publicly available and will be updated regularly." This is a primary-source-adjacent confirmation (World Bank's own catalog page for the dataset underlying the paper) of the key numbers: **164 countries, 2000–2017 coverage, 98% of global population**.
- Relevance to Theme 2: HLO is the canonical example of statistically linking many heterogeneous international/regional/national large-scale assessments onto one comparable scale (precursor/sibling methodology to GPF policy linking and to any India-specific learning-outcomes harmonization the team designs) — useful as the "gold standard, resource-heavy" comparison point against the lighter-weight policy-linking approach above.

### Classical test equating (background, not separately requested but relevant context for Method 5)
- Not separately researched with new primary sources in this session beyond what overlaps with mirt/TAM's documented support for "differential item, bundle, and test functioning" (mirt CRAN description, already quoted in Method 1) — mirt's DIF/DTF tooling is directly applicable to detecting non-invariant items before/while linking heterogeneous assessments. No dedicated equating-method (e.g., Stocking-Lord, mean-mean) primary source was fetched in this session — **flag as a gap** if the final document needs classical IRT-equating citations distinct from policy linking.

---

## Summary of explicit gaps / follow-up needed
1. **AMPL** acronym/source not identified — needs a dedicated follow-up search against World Bank/UIS glossaries.
2. **IEA Rosetta Stone** not researched due to a rate-limited search call that wasn't re-run — needs a dedicated follow-up.
3. LLM-KT sparse/periodic-assessment suitability claims are sourced only from a search-engine synthesis, not from primary text of arXiv:2412.09248 or the cited DDKT/LRE-C papers — needs direct fetch/confirmation.
4. Early-grade-specific CAT/SPRT for oral reading fluency (e.g., EGRA) was not confirmed from a primary source — needs direct fetch of RTI International / USAID / World Bank EGRA technical documentation.
5. UIS WG-GAML-5 Policy Linking summary PDF returned HTTP 403 on fetch — content summarized only via search synthesis, not primary text; re-attempt fetch or find an HTML mirror.
6. Nature.com returned HTTP 406 for the Angrist et al. 2021 article itself; the 164-country/2000–2017/98%-of-population figures were confirmed via the World Bank Data Catalog page (a legitimate but secondary-to-the-paper source) rather than the Nature article text directly.
7. `pyCDM` as a literal maintained package name was not found; `InsCD` and `pygdina` are the closest current Python CDM tooling, with `InsCD` independently confirmed as actively maintained (last commit 2025-11-27) and `pygdina` not independently verified.
