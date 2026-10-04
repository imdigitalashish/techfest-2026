# R2 — Robust Conformal Prediction & Bounded-Influence Aggregation: Prior Art Scan

Status: IN PROGRESS (incremental write; skeleton first, filled per-source)
Scope: Spike — conformal intervals for text+price fusion that stay valid under adversarial control of k of n docs, via bounded-influence aggregator (trimmed mean/median) + worst-case model-output-change inflation, possibly + ACI/PID for drift.
Accessed: 2026-10-04 (IST). Today's date for all "accessed" stamps below is 2026-10-04 unless noted.

---

## (1) TL;DR

_(to be filled last, after findings)_

---

## (2) Findings by sub-topic

### 2.1 Adversarially robust conformal prediction (RSCP, RSCP+, prob. robust CP, Verifiably Robust CP, CAS, COLEP, 2025–26 follow-ups)

**RSCP — Gendler, Weng, Daniel, Romano, "Adversarially Robust Conformal Prediction," ICLR 2022.**
OpenReview: https://openreview.net/forum?id=9L1BsI4wP1H (forum page itself returned a browser-verification challenge when fetched directly — not opened as rendered text this session; existence/ID confirmed via web_search tool result quoting its abstract and metadata). Code: https://github.com/Asafgendler/RSCP — **opened**, README confirms this is the official paper-replication repo (CIFAR10/CIFAR100/ImageNet experiment scripts, pretrained checkpoints, figure-reproduction scripts) — maturity: **paper-only / research reproduction code**, not a maintained library.
- **Guarantee (1 line, per web_search-returned abstract text, not independently re-derived):** finite-sample marginal coverage for classification prediction sets against *any* ℓ2-norm-bounded test-time adversarial perturbation, obtained by combining split conformal with randomized smoothing (Gaussian noise) to bound the Lipschitz constant of the non-conformity score.
- **Threat model:** test-time evasion only (ℓ2-bounded perturbation of a single input at inference), classification, images. Not text, not time series, not training/calibration-set poisoning.
- Caveat found via RSCP+ abstract (below): the original RSCP robustness guarantee was later shown to be **flawed in practice** by Yan et al.

**RSCP+ — Ge Yan, Yaniv Romano, Tsui-Wei Weng, "Provably Robust Conformal Prediction with Improved Efficiency," arXiv:2404.19651 (ICLR 2024 per task brief).** Opened: https://export.arxiv.org/api/query (arXiv metadata/abstract, not the PDF). Accessed 2026-10-04. Code: https://github.com/Trustworthy-ML-Lab/Provably-Robust-Conformal-Prediction (listed in abstract; not separately browsed this session — treat repo existence as stated-by-authors, maturity assessed as **paper code** pending direct open).
- **Guarantee (1 line, quoted from abstract):** "a novel framework called RSCP+ to provide provable robustness guarantee in evaluation, which fixes the issues in the original RSCP method," plus two efficiency methods (Post-Training Transformation, Robust Conformal Training) that shrink set size "up to 4.36×, 5.46×, 16.9×" on CIFAR10/CIFAR100/ImageNet resp.
- **Threat model:** same family as RSCP — ℓ2 adversarial test-time perturbation, classification, images, via randomized smoothing. Explicitly frames prior RSCP's guarantee as unsound ("flawed when used in practice") — important for us: even the foundational certified-robust-CP result needed a correction paper two years later, a sign this sub-field's guarantees are subtle to get right.
- Not text; not time series.

**Probabilistically Robust Conformal Prediction (PRCP / aPRCP) — arXiv:2307.16360, UAI 2023 (journal_ref confirms "Uncertainty in Artificial Intelligence, 2023").** Opened via arXiv API abstract. Author list truncated in the fetch (need second call to confirm "Ghosh" — not yet independently verified in this session; task brief names Ghosh et al., consistent with topic framing but I have not yet read the author field directly).
- **Guarantee (1 line, quoted from abstract):** robustness to *most* (not worst-case) perturbations around a clean input — a relaxation of adversarially-robust CP (worst-case) and standard CP (no robustness), via an adaptive "quantile-of-quantile" design (one threshold over data, one over the perturbation distribution) that provably achieves the targeted *probabilistic* (not fully adversarial) robust coverage.
- **Threat model:** random/bounded-probability perturbations (not arbitrary worst-case adversary), classification, images (CIFAR10/CIFAR100/ImageNet). Relevant conceptually to our spike: a middle ground between "assume no adversary" and "assume worst-case adversary" is exactly the risk/cost trade-off we'd face choosing k (the assumed corruption budget) in production.
- Not text; not time series; not explicitly an aggregation-based defense.

**Verifiably Robust Conformal Prediction (VRCP) — arXiv:2405.18942v3, accepted NeurIPS 2024 (per arXiv comment field).** Opened via arXiv API abstract. Author = "Jeary" per task brief, not yet independently confirmed from the author field (truncated in fetch).
- **Guarantee (1 line, quoted from abstract):** recovers CP coverage guarantees under adversarial attack by using **neural-network verification** (not randomized smoothing) — "the first to support perturbations bounded by arbitrary norms including ℓ1, ℓ2, and ℓ∞, **as well as regression tasks**."
- **Threat model:** test-time evasion, bounded-norm perturbation (generalizes beyond ℓ2), **both classification and regression** (regression tasks evaluated on deep-RL environments) — this is the first item in our topic-1 list that explicitly claims regression support, relevant since our fusion forecaster is a regression (or return-direction) task.
- Does not claim to handle text/discrete perturbations or non-norm-bounded (e.g., swap/insert/delete token) corruption, nor time-series exchangeability drift.
- Code availability: not yet checked this session (not opened) — **UNVERIFIED**, follow-up needed.

**COLEP — Mintong Kang et al., "COLEP: Certifiably Robust Learning-Reasoning Conformal Prediction via Probabilistic Circuits," arXiv:2403.11348, accepted ICLR 2024 (per arXiv comment).** Opened via arXiv API abstract.
- **Guarantee (1 line, quoted from abstract):** "end-to-end certification of prediction coverage ... in the presence of bounded adversarial perturbations," plus a version of the bound that **additionally accounts for finite calibration-set size** ("certified coverage considering the finite size of the calibration set") — i.e., two stacked finite-sample effects (calibration-set finiteness + adversarial perturbation bound) are both certified, not just one.
- **Mechanism:** multiple learned models for different semantic concepts + a reasoning layer (probabilistic circuits) encoding logical relationships between concepts; robustness is certified end-to-end through this learning+reasoning pipeline.
- **Threat model:** bounded adversarial perturbation at test time, classification (GTSRB, CIFAR10, AwA2 — images with auxiliary concept labels). Not text, not time series. Relevant design idea for us: COLEP's "multiple weak signals + reasoning layer with a joint certified bound" is structurally analogous to "multiple per-document sentiment scores + bounded-influence aggregator with a joint certified bound" — same shape of argument, different domain and different robust-aggregation primitive (logic/probabilistic-circuit reasoning vs. trimmed-mean/median).

**CAS candidate — Soroush H. Zargarbashi, Mohammad Sadegh Akhondzadeh, Aleksandar Bojchevski, "Robust Yet Efficient Conformal Prediction Sets," arXiv:2407.09165, Proceedings of the 41st ICML (2024).** Opened via arXiv API (abstract + metadata only; direct arxiv.org/abs page fetch twice timed out — transport failure, not opened as rendered page this session). **I could not independently confirm the acronym "CAS" is used inside the paper** (abstract doesn't contain it) — treating this as the likely match for the task brief's "CAS (Zargarbashi et al., ICML 2024)" based on author+venue+topic match, but flagging the acronym itself as **unconfirmed**.
- **Guarantee (1 line, quoted from abstract):** "provably robust sets by bounding the worst-case change in conformity scores," with tighter bounds than prior work → smaller/more efficient sets.
- **Threat model — the closest match to our spike's threat model found all session:** explicitly covers **both evasion (test-time) and poisoning attacks, on both features and labels**, and explicitly covers **both continuous and discrete (sparse) data**. This is structurally very close to "bound the worst-case shift in a score/signal under adversarial control of some inputs, then inflate the conformal interval by that bound" — our spike's core mechanism. Does not mention text, multi-document aggregation, or time series in the abstract.
- Same author group also has: "Conformal Inductive Graph Neural Networks," arXiv:2407.09173, ICLR 2024 (graph-specific exchangeability fix, not robustness — noted only to disambiguate from the robustness paper, not directly relevant to our spike).

**2025–2026 follow-ups found (same Zargarbashi/Bojchevski lineage), all opened via arXiv API abstracts:**
- **"Robust Conformal Prediction with a Single Binary Certificate," Soroush H. Zargarbashi, Aleksandar Bojchevski, arXiv:2503.05239, ICLR 2025.** Guarantee: robust CP via a **single binary certificate** rather than per-point smoothed-score certification, cutting required Monte-Carlo samples from ~10⁴ to ~150 on CIFAR10 while producing smaller sets; drops the earlier requirement of a bounded score function. Threat model: adversarial (randomized-smoothing-certifiable) perturbations, classification. Not text/time-series explicitly.
- **"One Sample is Enough to Make Conformal Prediction Robust," Soroush H. Zargarbashi, Mohammad Sadegh Akhondzadeh, Aleksandar Bojchevski, arXiv:2506.16553v2, NeurIPS 2025.** Guarantee: robust CP (RCP1) from a **single forward pass** on a randomly-perturbed input (vs. ~100 passes for prior smoothing-based SOTA), by certifying the conformal **procedure** itself rather than individual conformity scores; **explicitly task-agnostic — "applicable to classification and regression"** — and extended to robust conformal **risk control**. This is the most directly reusable 2025 result for a resource-constrained hackathon spike needing regression support without heavy per-document MC sampling.
- Both papers list ICLR 2025 / NeurIPS 2025 as peer-reviewed venues (per arXiv `arxiv:comment` fields) — maturity: **paper-only in the sense that I have not opened a code repository this session**; authors' pattern across their ICLR2024/ICML2024/ICLR2025/NeurIPS2025 papers strongly suggests a maintained GitHub org, but I have **not verified a code URL this session** — follow-up needed, log under Leads/UNVERIFIED if not resolved.



### 2.2 Conformal under calibration poisoning / contamination / label noise

_(pending)_

### 2.3 Certified robustness of text models to word substitution/insertion (+ combination with conformal)

**Jia, Raghunathan, Göksel, Liang, "Certified Robustness to Adversarial Word Substitutions," arXiv:1909.00986, EMNLP 2019.** Opened via arXiv API abstract.
- **Guarantee (1 line, quoted/paraphrased from abstract):** trains models provably robust to **all** word substitutions within a bounded synonym set per word, using **Interval Bound Propagation (IBP)** to minimize a certified upper bound on worst-case loss over the exponentially large combinatorial space of substitutions; reports 75% certified/adversarial accuracy on IMDB sentiment and SNLI vs. 8% (normal training) / 35% (data augmentation).
- **Threat model:** discrete word-substitution perturbations (not norm-ball continuous perturbations), text classification (sentiment, NLI). Directly relevant: sentiment classification on news/tweets is exactly our text-feature extraction step, so IBP-style certification could in principle bound how much an adversary's synonym-substitution attack can move a *single document's* sentiment score — a different (and in some ways complementary) robustness layer from robust-aggregation-across-documents.

**Ye, Gong, Liu, "SAFER: A Structure-free Approach for Certified Robustness to Adversarial Word Substitutions," arXiv:2005.14424, ACL 2020.** Opened via arXiv API abstract.
- **Guarantee (1 line, quoted from abstract):** certified robustness via **randomized smoothing over random word substitutions** (stochastic ensemble + statistical certification), applicable as a **black-box** method to any pretrained model (incl. BERT) without needing model structure access — first to achieve "practically meaningful certified accuracy" on BERT-scale models.
- **Threat model:** discrete synonym word-substitution, text classification (IMDB, Amazon). Black-box/model-agnostic is attractive for our pipeline since our fusion model's text encoder is likely a pretrained sentiment/embedding model we don't want to retrain with IBP constraints.

**"Text-CRS: A Generalized Certified Robustness Framework against Textual Adversarial Attacks," arXiv:2307.16630v2 (published 2023-07-31, updated 2024-06-11).** Opened via arXiv API abstract. Authors not yet captured in this session's truncated fetch — **UNVERIFIED author list**, title/abstract/arXiv ID confirmed.
- **Guarantee (1 line, quoted from abstract):** generalizes certified NLP robustness beyond synonym-substitution-only (prior certified schemes per this abstract "can only certify ... ℓ0 perturbations in synonym substitution attacks") to **four** word-level operations — synonym substitution, word reordering, insertion, and deletion — by representing each as a combination of permutation + embedding transformation, with novel randomized-smoothing theorems giving robustness bounds in both permutation and embedding space; claims first benchmark of certified accuracy/radius across all four operation types.
- **Threat model:** discrete text perturbations, broadest operation coverage found this session (substitution, reorder, **insert**, **delete**) — notably, insertion/deletion is exactly the shape of attack an adversary posting extra fabricated tweets/news snippets would use, i.e., closer to our actual threat model (injecting whole malicious *documents*) than pure word-substitution work.
- **Combination with conformal coverage: none found.** I did not find, in any of the three certified-text-robustness papers above, an explicit combination with conformal prediction coverage guarantees.

**Explicit search for "certified text robustness + conformal prediction" combination:** queried arXiv (`abs:"word substitution" AND abs:conformal`, `abs:"certified robustness" AND abs:conformal AND abs:text` — see §2.5 log) — **no paper found this session that combines word-level certified-robustness (IBP/randomized-smoothing-over-substitutions) with conformal coverage guarantees.** This appears to be a **genuine gap** in the literature as surveyed here, and is the closest thing to prior art absence directly supporting the "text" half of our spike's novelty.

### 2.4 Robust aggregation bounds (trimmed mean / median breakdown point, Byzantine-robust)

**Yin, Chen, Ramchandran, Bartlett, "Byzantine-Robust Distributed Learning: Towards Optimal Statistical Rates," arXiv:1803.01498v2, ICML 2018.** Opened via arXiv API abstract. **This is the primary citable source for the trimmed-mean/median adversarial-shift bound referenced in the task brief.**
- **Guarantee (1 line, quoted/paraphrased from abstract):** sharp statistical error-rate analysis of **two robust distributed gradient-descent algorithms based on coordinate-wise median and coordinate-wise trimmed mean**, under an arbitrary/adversarial (Byzantine) subset of compute nodes; proves these achieve **order-optimal statistical error rates for strongly convex losses** (and gives rates for non-strongly-convex and smooth non-convex losses too); also proposes a one-communication-round median-based variant with the same optimal rate for strongly-convex quadratic loss.
- **Threat model:** a bounded fraction of the n inputs (gradients from distributed workers, by direct analogy: documents/sentiment scores in our setting) are arbitrary/adversarial (Byzantine) — not norm-bounded perturbations of all inputs, but **full adversarial control over a subset**. This is exactly the "adversary controls up to k of n documents" threat model in our spike, just in the distributed-optimization literature rather than conformal prediction. **I have not opened the PDF (per instructions) so I cannot quote the exact closed-form breakdown-point formula (e.g., the precise constant/rate expression) from the paper text itself — only what the arXiv abstract states.** Follow-up: the precise finite-sample bound (commonly cited elsewhere in the literature as something like error ∝ (ε·σ + σ√(d/n)) for trimmed mean with corruption fraction ε, dimension d, n samples) should be pulled from the actual theorem statement before being used as a load-bearing number in our design doc — **flagging the exact constants as UNVERIFIED this session.**
- Directly reusable framing for our spike: if we treat "the n per-document sentiment scores for a ticker-day" as the n distributed values and "up to k adversarial docs" as Byzantine workers, Yin et al.'s coordinate-wise trimmed-mean/median machinery is close to a direct drop-in for the "bounded-influence aggregator with a computable worst-case shift under k corrupted docs" component of our spike — this is 1-dimensional (scalar sentiment per doc) rather than their high-dimensional gradient setting, which if anything makes the bound simpler/tighter to compute in our case.

**Other Byzantine-robust works found in passing (not deep-dived, listed for completeness):**
- "Secure Byzantine-Robust Distributed Learning via Clustering" (SHARE), arXiv:2110.02940, 2021 — combines secure aggregation (privacy) with Byzantine-robust filtering; tangential to our spike (privacy is not our concern), noted only because it surfaced in the same arXiv search and confirms Yin-et-al.-style trimmed-mean/clustering defenses remain an active 2021+ research line. Opened via arXiv API abstract only.
- "Communication-efficient Byzantine-robust distributed learning with statistical guarantee," arXiv:2103.00373, 2021 — same family, not opened beyond title/one-line abstract snippet; **UNVERIFIED in depth**.

**Breakdown point of trimmed mean/median — explicit concept search:** I did not find, in this session's searches, a crisper arXiv title specifically proving a classical "breakdown point = ⌊(n-1)/2⌋ for median, trim fraction α ⇒ breakdown (close to) α for trimmed mean"-style statistics-textbook result as its own paper (this is usually textbook/robust-statistics material, e.g. Huber/Tukey-era results, not an arXiv-era paper) — Yin et al. 2018 is the strongest **modern, ML-context, citable, arXiv-available** primary source found for the quantitative version of this bound applied to high-dimensional learning. Flag: a robust-statistics textbook reference (Huber & Ronchetti, *Robust Statistics*) would be the classical primary source for the pure breakdown-point number but was not opened this session (not an arXiv/web source) — **UNVERIFIED, textbook not opened.**

### 2.5 Explicit prior-art searches (hit / nothing-found log)
_Completed by the P10 lead, 4 Oct 2026 ~13:45 IST (gpt-6-astra review item #5). arXiv API (`export.arxiv.org/api/query`), sorted by submission date, newest first, max 6 results per query; titles and abstracts opened via `id_list` for any plausible hit. This is a bounded search, not a systematic review._

| Query (arXiv API `search_query`) | Hits | Relevant? |
|---|---|---|
| `abs:"conformal prediction" AND abs:adversarial AND abs:"time series"` | 2: arXiv:2609.38196 (CAGE, Sep 2026); arXiv:2205.09095 (Rolling Risk Control) | No. CAGE's "adversarial" is a GAN-style discriminator inside a forecast ensemble. Rolling RC's "adversarially" is about adversarial distribution shift, with a long-run (ACI-type) guarantee and no per-input certification. |
| `abs:conformal AND abs:sentiment AND abs:stock` | 0 | — |
| `abs:"robust conformal" AND abs:regression` | 2: RCP1 (arXiv:2506.16553), VRCP (arXiv:2405.18942) | Closest regression prior art (already in §2.1). Threat models are randomized/verified ℓp perturbations of a single input, not a document budget. |
| `abs:conformal AND abs:injection AND abs:documents` | 6, all off-topic ("conformance" testing, MT metrics, agent guardrails) | No. |
| `abs:conformal AND abs:multimodal AND abs:robust AND abs:adversarial` | 0 | — |

**Conclusion (hedged):** in these searches and in §2.1–2.4, no conformal method certifies coverage against a budget of *injected documents* feeding a text-and-time-series regressor. P10 therefore claims a specialisation — robust conformal verification applied to document-injection budgets through tractable deletion ranges — not a new robust-coverage principle and not first-in-literature status.

---

## (3) Implications / pitfalls for our design

_(pending)_

---

## (4) Source table

| URL | Title | Date | Maturity | Claim used |
|---|---|---|---|---|
_(pending)_

---

## (5) Leads not verified (UNVERIFIED — not opened this session)

_(pending)_
