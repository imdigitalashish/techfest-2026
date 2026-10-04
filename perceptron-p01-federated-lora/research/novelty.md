# Novelty position: AnchorLoRA vs the closest prior art

> Lead-written 4 Oct 2026, 11:30 IST. Every paper below was opened at arXiv (abstract page; for FlexLoRA, CF-LoRA and PreLort also the full-text HTML) on 2026-10-04, and its title and date are recorded in [`sources/arxiv_verified.tsv`](sources/arxiv_verified.tsv). Quotes are verbatim from the opened pages. Raw search notes from the research agent: [`raw/fedlora_frontier.md`](raw/fedlora_frontier.md).

## The claim we make (revised 12:25 after the gpt-6-astra review)
> We extend FFA-LoRA's frozen-A design to prefix-masked device updates and evaluate participation handling and update-share diagnostics for one shared model. CF-LoRA learns A before freezing it for clustered B aggregation; PreLort trains both factors with a multi-prefix objective and segment-wise aggregation. Our contribution is the evaluated systems recipe and its cost/utility trade-offs, not a new exactness primitive or a minimum-communication theorem.

The bounded prior-art statement is: *to our search (listed below), no paper describes this exact frozen-seed-A + B-prefix recipe.* That is not a universal absence claim. A skeptical reader can fairly call it an immediate composition of known ideas (FFA-LoRA's identity + prefix masks). The value we claim is the evaluated system, not the algebra.

## What is NOT ours (and is credited)
| Ingredient | Prior art (opened) | What it does, in its own words |
|---|---|---|
| Freezing A so that B-averaging is exact | **FFA-LoRA**, ICLR 2024 ([2403.12313](https://arxiv.org/abs/2403.12313)) | "The core idea of FFA-LoRA is to fix the randomly initialized non-zero matrices and only fine-tune the zero-initialized matrices", which also helps "further halve the communication cost" |
| A shared frozen A giving the *exact* average of client updates | **CF-LoRA**, arXiv 29 Sep 2026 ([2609.36986](https://arxiv.org/abs/2609.36986)) | "first learns a globally shared A factor while retaining personalized B_i factors … performs intra-cluster B-factor aggregation with a frozen A factor". Full text: "Because every client uses the same frozen Ā, this expression is exactly the average of the clients' induced updates." |
| Prefix-nested heterogeneous ranks; per-segment averaging | **PreLort**, arXiv 14 Jun 2026 ([2606.15963](https://arxiv.org/abs/2606.15963)) | "a nested low-rank formulation for federated LoRA that organizes adapter dimensions into a prefix hierarchy … a segment-wise aggregation rule that averages only over clients contributing to each rank segment" |
| Exact product-space aggregation for mixed ranks | **FlexLoRA** ([2402.11505](https://arxiv.org/abs/2402.11505)); FedEx-LoRA, ACL 2025 ([2410.09432](https://arxiv.org/abs/2410.09432)); FedPA-LoRA ([2608.15381](https://arxiv.org/abs/2608.15381)) | FlexLoRA: "synthesizing a full-size LoRA weight from individual client contributions and employing Singular Value Decomposition (SVD) for weight redistribution" |
| Zero-padding / truncation for mixed ranks | HetLoRA ([2401.06432](https://arxiv.org/abs/2401.06432)); Byun & Lee, NAACL 2025 ([2406.17477](https://arxiv.org/abs/2406.17477)) | described by FlexLoRA's related work as "zero-padding local LoRA weights for aggregation and truncating global weights to match the local rank" |
| Step normalisation for unequal local work | FedNova ([2007.07481](https://arxiv.org/abs/2007.07481)) | "Naive weighted aggregation … causes objective inconsistency" |
| Memory of absent devices | MIFA ([2106.04159](https://arxiv.org/abs/2106.04159)) | devices dropping out "beyond the control of the central server" severely affect FedAvg |
| Fair / per-client objectives | q-FFL, ICLR 2020 ([1905.10497](https://arxiv.org/abs/1905.10497)); AFL ([1902.00146](https://arxiv.org/abs/1902.00146)) | (titles verified; mechanisms from recall, so not quoted) |

## Exactly how we differ from the two closest papers
| | CF-LoRA (2609.36986) | PreLort (2606.15963) | **AnchorLoRA (ours)** |
|---|---|---|---|
| A matrix | *learned* globally shared, then frozen | trained: its local objective optimises θ, where "θ includes the shared frozen backbone and LoRA parameters"; a full-text search for "frozen" or "freez" finds only the backbone | *never trained*: regenerated from a public seed, 0 bytes |
| Device ranks | no rank-heterogeneity mechanism found in the full text (searched "heterogeneous rank", "different ranks", "rank heterogeneity", "varying rank": 0 hits) | prefix-nested, heterogeneous | prefix-nested, heterogeneous, sized to the device budget |
| Aggregation | exact within a cluster (shared Ā) | segment-wise averaging of factors (A and B both averaged) | exact for any rank mix: Σ w_k ΔB_k·A |
| Goal | personalised: clustered adapters | one global adapter | one global adapter, **macro** objective (every device's domain counts equally) |
| Dropout / stragglers | not addressed in the abstract | samples clients per round (§5.1, per astra review); no deadline/outage handling found | partial work accepted, FedNova-style normalisation, memory of absent devices; evaluated under seeded dropouts and outages |
| Dominance measurement | — | — | per-device influence share in ΔW space each round (projection + bounded norm share) |

**Consequences for wording.**
- Never say "first to freeze A" (FFA-LoRA, CF-LoRA) or "first nested ranks" (PreLort, HetLoRA).
- Never say "exact aggregation" without "for mixed ranks at r_k·d_out upload" (FlexLoRA and FedEx-LoRA are exact too, at higher cost).
- Normalisation, memory and weights reduce bias from partial participation and quantity skew. Sharing A removes only the *factorisation* error; it does not make those mechanisms "exact".
- PreLort's per-segment *averaging* rule is testable inside our exact space (`anchor_full_seg`). Its multi-prefix *training* objective is not reproduced, so `anchor_full_seg` is not PreLort.
- Do not say "neither paper considers participation": PreLort samples clients each round (its §5.1, per the astra review). Our distinction is device-dependent availability, deadline truncation and outage handling.
- Do not say "minimal upload": r_k·d_out is this parameterisation's uncompressed payload, not a lower bound. In the pilot, homogeneous FFA-LoRA sent less logical uplink per device than AnchorLoRA (its rank and work differ).

## Searches behind "to our search"
- **Lead, 4 Oct:** two web searches (frozen-A + heterogeneous/nested ranks), recorded in `landscape.md` §2.
- **Research agent `r1c-fedlora-frontier`, 4 Oct** (`raw/fedlora_frontier.md`):
  - arXiv API queries: "frozen A factor" AND "Federated LoRA"; "globally shared A" AND LoRA; "heterogeneous client ranks" AND LoRA; "nested LoRA" AND federated; "MatryoshkaLoRA" AND federated.
  - Web searches, plus a Semantic Scholar scan of 250 papers citing FFA-LoRA.
  - OpenReview pages were blocked by a browser check, so OpenReview-only work is **UNVERIFIED**.
- The verdict is therefore "not found", not "does not exist".
