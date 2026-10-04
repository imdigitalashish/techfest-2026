# FedLoRA frontier notes (accessed 2026-10-04)

## Prior-art verdict: NOT FOUND (exact AnchorLoRA combination)

I did **not** find a paper that combines all three AnchorLoRA ingredients: (1) a frozen/public/seed-generated shared LoRA `A`, (2) heterogeneous or nested client ranks where client `k` trains only a prefix/subset of `B` columns, and (3) exact mixed-rank aggregation as `sum_k w_k Delta B_k A`.

Closest hits split the idea in half:

- **CF-LoRA** is the closest on frozen/shared `A`: it “first learns a globally shared `A` factor while retaining personalized `B_i` factors” and then does “intra-cluster `B`-factor aggregation with a frozen `A` factor.” Its PDF further states that because every client uses the same frozen `A`, the expression is “exactly the average of the clients’ induced updates.” **But I found no heterogeneous/nested rank mechanism** in the arXiv abstract/PDF text; it is about statistical clustering and decoupled factor aggregation, not rank budgets.
- **PreLort** is the closest on nested heterogeneous ranks: it proposes “a nested low-rank formulation for federated LoRA that organizes adapter dimensions into a prefix hierarchy,” plus “segment-wise aggregation” over clients contributing to each rank segment. **But it explicitly says only `A` and `B` are trained**, and each client locally trains `(A_k, B_k)`; no frozen shared `A`.
- **Byun & Lee / rank heterogeneity**, **SeFoRA**, **FedPA-LoRA**, and **GLoRA** address heterogeneous ranks via padding, sketching, product-space aggregation, or server-side representations, not by a seed-fixed shared `A`.

Searches run/opened: arXiv API queries for `"frozen A factor" AND "Federated LoRA"`, `"globally shared A" AND LoRA`, `"heterogeneous client ranks" AND LoRA`, `"nested LoRA" AND federated`, `"MatryoshkaLoRA" AND federated`; web searches for “FFA-LoRA heterogeneous rank,” “frozen A heterogeneous rank federated,” “nested LoRA federated,” “Matryoshka LoRA federated,” and “zero-padding frozen A”; Semantic Scholar FFA-LoRA citation API offsets 0, 100, and 200 (250 citation records scanned). OpenReview pages for Byun & Lee and PF2LoRA were attempted but blocked by Turnstile; I used ACL/arXiv for Byun & Lee and mark OpenReview-only claims **UNVERIFIED**.

## New / newly checked papers

| Title | Venue/date | Mechanism quote | Relevance | URL |
|---|---:|---|---|---|
| **CF-LoRA: Decoupled Factor Aggregation and Adaptation-Aware Client Clustering** | arXiv 2026-09-29 | “learns a globally shared `A` factor while retaining personalized `B_i` factors”; “intra-cluster `B`-factor aggregation with a frozen `A` factor.” PDF: same frozen `A` makes it “exactly the average.” | **Closest prior art** for frozen-A exactness, but no verified heterogeneous/nested ranks. | https://arxiv.org/abs/2609.36986 |
| **PreLort: Prefix-Nested LoRA for Federated Fine-Tuning under Rank Heterogeneity** | arXiv 2026-06-14 | “adapter dimensions into a prefix hierarchy”; “segment-wise aggregation rule that averages only over clients contributing to each rank segment.” Also: “Only `A` and `B` are trained.” | Closest nested-rank prior art; not frozen/shared `A`, not exact `Delta B A`. | https://arxiv.org/abs/2606.15963 |
| **Towards Federated Low-Rank Adaptation…with Rank Heterogeneity** (Byun & Lee) | NAACL 2025 / arXiv v3 | Heterogeneous ranks cause instability; “zero-padding aggregation strategy…dilutes information”; proposes “replication-based padding.” | Rank heterogeneity baseline; approximate padding, no frozen `A`. | https://aclanthology.org/2025.naacl-short.30/ ; https://arxiv.org/abs/2406.17477 |
| **iFLoRA: Federated LoRA Fine-Tuning with Pipelined Error-Mitigated Aggregation and Matrix-Wise Freezing** | ACL Findings 2026 | Reconstructs local updates, aggregates global update, then “decomposed via singular value decomposition (SVD)”; “adaptive matrix-wise freezing” by stability. | Freezing exists, but adaptive matrix-wise and after SVD; not seed-fixed shared `A` or rank-prefix exactness. | https://aclanthology.org/2026.findings-acl.284/ |
| **FedTreeLoRA** | ICML 2026 / arXiv | ICML page: layers play different roles; method “organizes users into a tree-like structure” and decides sharing per layer. | Layer-depth personalization, not rank aggregation. | https://icml.cc/virtual/2026/poster/62499 ; https://arxiv.org/abs/2603.13282 |
| **SeFoRA** | arXiv 2026-08-10 | Clients may use “different LoRA ranks”; each sends “a linear sketch of its local updates,” enabling direct aggregation. | Heterogeneous ranks via sketching, not frozen `A`. | https://arxiv.org/abs/2608.10144 |
| **GLoRA: Gauge-Aware Low-Rank Server Representations** | arXiv 2026-05-07 | “estimates a consensus update subspace”; “rank-compatible readout”; tested with “heterogeneous client ranks, sparse participation.” | Good competitor for sparse participation and rank heterogeneity; no seed-frozen `A`. | https://arxiv.org/abs/2605.06733 |
| **FedPA-LoRA** | arXiv 2026-08-15 | “aggregates heterogeneous-rank updates in the common product space” and reconstructs a rank-constrained global adapter. | Product-space alternative to exact `B A` factor sharing. | https://arxiv.org/abs/2608.15381 |
| **FedLoDrop** | JSAC 2026 / arXiv 2025 | “applies dropout to the rows and columns of the trainable matrix in Federated LoRA.” | Dropout is adapter sparsity/regularization, **not** device dropout. | https://arxiv.org/abs/2510.12078 |
| **AlignFed** | arXiv 2026-06-06 | Addresses synchronous “straggler effect”; uses “version-aware update grouping,” calibration-set alignment, and “fairness-aware aggregation” using freshness and participation frequency. | Relevant to asynchronous/straggler partial work and fast-client dominance; not LoRA-specific in title but LLM FFT. | https://arxiv.org/abs/2606.08197 |
| **FairFedMed / FairLoRA** | arXiv 2025-07-21 | FairLoRA “customizes singular value matrices per demographic group while sharing singular vectors.” | Fairness across demographic groups; not data-rich-client influence auditing. | https://arxiv.org/abs/2508.00873 |
| **Worst-client fairness in federated PEFT** | arXiv 2026-09-20 | A data-poor client can be “poorly served”; lower perplexity backbones improve “worst-performing client.” | Directly relevant to data-poor/data-rich dominance framing. | https://arxiv.org/abs/2609.23463 |
| **TinyGuard** | arXiv 2026-02-02 | Byzantine defense via “statistical update fingerprinting”; LoRA-adapter experiments under sign-flip, scaling, noise, label poisoning. | LoRA-relevant Byzantine defense, not rank-specific. | https://arxiv.org/abs/2602.02615 |
| **Thermo-FL** | arXiv 2026-08-21 | Thermal-aware federated LoRA; TERRA combines “norm filtering, mask-aware directional validation, adaptive active-coordinate clipping, and mask-aware aggregation.” | Robust sparse LoRA aggregation with hardware instability/adversaries. | https://arxiv.org/abs/2608.21172 |
| **FedDR-LoRA** | ICML 2026 / PMLR | Reveals “robustness asymmetry”: `A` stable features, `B` noise-sensitive; aggregates `B` while preserving local `A`. | Robust/noisy federated LoRA; opposite factor choice from AnchorLoRA. | https://proceedings.mlr.press/v306/fang26v.html |

## Implications for AnchorLoRA novelty

- Claim safely as: **“To our search, no prior work combines frozen public/seeded `A` with prefix/nested heterogeneous `B` ranks for exact mixed-rank aggregation.”**
- Narrow against CF-LoRA: it has frozen/shared `A` and exact same-rank `B` aggregation, but not verified heterogeneous/nested client ranks or seed-generated `A`.
- Narrow against PreLort: it has prefix/nested heterogeneous ranks, but both LoRA factors are trained and segment aggregation is not `sum Delta B_k A` with a fixed public anchor.
- Position MIFA memory, partial-work acceptance, macro weights, clipping, and influence-share audit as system-stability/fairness additions; current LoRA literature more often uses padding/SVD/sketch/product-space fixes.
- For dropout claims, say “partial participation / stragglers / sparse participation” unless demonstrating true mid-run device dropout; I found no LoRA paper squarely matching AnchorLoRA’s partial-work acceptance.

## Source list

All sources above were opened on 2026-10-04. Additional opened search/source endpoints: Semantic Scholar FFA-LoRA citations API (`https://api.semanticscholar.org/graph/v1/paper/arXiv:2403.12313/citations?...`, offsets 0/100/200); arXiv API searches listed in the verdict; OpenReview attempted for `X79zY0EKHz`, `EjY4B-lMqwJ`, and `X7ITc8NmSv` but returned browser-verification pages, so OpenReview contents are **UNVERIFIED** here.
