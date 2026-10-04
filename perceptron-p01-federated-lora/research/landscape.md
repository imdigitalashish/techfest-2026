# Landscape: federated LoRA fine-tuning across weak, scattered devices

> Lead-written 4 Oct 2026, 06:50–07:20 IST. **Verification status matters here.** Overnight, network uplink saturation killed all 8 research sub-agents before their first turn (HTTP 408 / ETIMEDOUT; see the thought-node Log). So every arXiv source below was re-checked by [`scripts/verify_arxiv.py`](../scripts/verify_arxiv.py), which fetched each abstract page on 2026-10-04 and wrote title, date, comments and abstract head to [`sources/arxiv_verified.tsv`](sources/arxiv_verified.tsv) (44/44 OK; CLAIR and FedRoRA were added at 07:49). Non-arXiv pages, and the ones that failed to load, are listed in [`sources/other_verified.md`](sources/other_verified.md). Claims marked **(abs)** were read in the abstract. **(title)** means only the title/venue was read. **UNVERIFIED** means recall or a secondary summary, not yet confirmed at the primary source. The company section is the thinnest, because most company pages timed out; it is re-queued for the next research pass.

## 1. The problem in one paragraph
Each device k holds data D_k and fine-tunes a LoRA adapter ΔW_k = B_k A_k on a frozen base model. The server must produce one shared adapter. Four things break naive FedAvg here: (i) averaging A and B separately gives mean(B)·mean(A) ≠ mean(B·A) ("aggregation noise"); (ii) devices of different power want different ranks r_k; (iii) devices do different numbers of local steps, and some drop out mid-round; (iv) weights ∝ n_k let a data-rich device set the direction of the shared model. The literature splits along exactly these lines.

## 2. Aggregation exactness and LoRA structure (the algorithmic core)
| Work | Venue / date | Mechanism | Relevance to us | Status |
|---|---|---|---|---|
| FedIT, *Towards Building the Federated GPT* ([2305.05644](https://arxiv.org/abs/2305.05644)) | arXiv, May 2023 | Federated instruction tuning with LoRA + FedAvg (title, project page) | The "obvious baseline" lineage | (title) |
| OpenFedLLM ([2402.06954](https://arxiv.org/abs/2402.06954)) | arXiv, Feb 2024 | FedLLM framework and benchmark suite (title, abs head) | Baseline aggregation code | (title) |
| FederatedScope-LLM ([2309.00363](https://arxiv.org/abs/2309.00363)) | arXiv, Sep 2023 | Package for federated LLM fine-tuning, with source code | Alternative stack | (title) |
| **FFA-LoRA**, *Improving LoRA in Privacy-preserving FL* ([2403.12313](https://arxiv.org/abs/2403.12313)) | **ICLR 2024** | Names the root cause: "discordance between jointly optimizing the two low-rank matrices by local clients and separately aggregating them by the central server". Fix: freeze the random non-zero A, train only the zero-initialised B, which halves communication | **Our anchor builds on this.** Frozen A makes B-averaging exact | (abs) |
| HetLoRA ([2401.06432](https://arxiv.org/abs/2401.06432)) | arXiv, Jan 2024 | Heterogeneous LoRA ranks for on-device foundation models. Zero-padding + rank self-pruning is UNVERIFIED (not in the abstract head we read) | Heterogeneous-rank baseline (our `fedavg_ab_het` is HetLoRA-style padding/truncation) | (title + abs head) |
| FlexLoRA ([2402.11505](https://arxiv.org/abs/2402.11505)) | arXiv, Feb 2024 | Aggregation for heterogeneous tasks and client resources; mitigates the FL "bucket effect". SVD redistribution of the full-size update is UNVERIFIED | Product-space + SVD alternative | (abs head) |
| FLoRA ([2409.05976](https://arxiv.org/abs/2409.05976)) | arXiv, Sep 2024 | Heterogeneous LoRA. Stacking-based exact aggregation per a secondary summary (UNVERIFIED in primary text) | Exact but adapter size grows with devices | (title) |
| FedSA-LoRA, *Selective Aggregation* ([2410.01463](https://arxiv.org/abs/2410.01463)) | **ICLR 2025** | Asymmetry: "A matrices are responsible for learning general knowledge, while B matrices focus on capturing client-specific knowledge"; aggregates selectively on that basis | Opposite design choice to FFA-LoRA (personalisation) | (abs) |
| FedEx-LoRA ([2410.09432](https://arxiv.org/abs/2410.09432)) | **ACL 2025 (oral)** | "Existing methods rely on traditional federated averaging of LoRA adapters, resulting in inexact updates"; adds a residual correction to make aggregation exact | Exactness with trainable A, at the cost of a dense residual | (abs) |
| LoRA-FAIR ([2411.14961](https://arxiv.org/abs/2411.14961)) | **ICCV 2025** | Aggregation and initialisation refinement | Exactness-oriented correction | (title + venue) |
| LoRA-SB ([2411.19557](https://arxiv.org/abs/2411.19557)) → **Fed-SB** ([2502.15436](https://arxiv.org/abs/2502.15436)) | arXiv, Nov 2024 / Feb 2025 | Fed-SB: existing fixes either cost communication "that scales linearly with the number of clients" or degrade. Training only a small r×r matrix between fixed factors is UNVERIFIED | Extreme communication efficiency; a strong 2025 baseline | (abs head) |
| RoLoRA ([2502.01755](https://arxiv.org/abs/2502.01755)) | **NeurIPS 2025** | Alternating optimisation of the up/down projections "to enhance expressiveness and robustness" | Argues *against* freezing A permanently. Our main risk, so it is a baseline | (abs) |
| *Asymmetry in Low-Rank Adapters* ([2402.16842](https://arxiv.org/abs/2402.16842)) | arXiv, Feb 2024 | "unexpected asymmetry in the importance of low-rank adapter matrices". That B matters more and a random A suffices is UNVERIFIED beyond the head | Theoretical support for a frozen anchor A | (abs head) |
| VeRA ([2310.11454](https://arxiv.org/abs/2310.11454)), LoRA-FA ([2308.03303](https://arxiv.org/abs/2308.03303)) | ICLR 2024 / arXiv 2023 | Frozen random shared matrices (VeRA); frozen A for memory (LoRA-FA) | Frozen random projections are established, so not our novelty | (title) |
| iFLoRA, *Pipelined Error-Mitigated Aggregation and Matrix-Wise Freezing* ([ACL Findings 2026](https://aclanthology.org/2026.findings-acl.284/)) | **ACL 2026 Findings** (Jul 2026) | Error-mitigated aggregation + matrix-wise freezing (title only) | Newest exactness/freezing work, to be read in full | (title, authors, venue) |
| CLAIR ([2605.21217](https://arxiv.org/abs/2605.21217)) | arXiv, May 2026 | "clients share only partial structure and a substantial subset may be contaminated": a low-rank + block-sparse decomposition recovers the shared LoRA subspace and detects contaminated clients | Robustness and "who drives the shared subspace" | (abs) |
| FedRoRA ([2609.00632](https://arxiv.org/abs/2609.00632)) | arXiv, Sep 2026 | Rank-heterogeneous *personalisation*: "shared global directions and personalized rank-wise magnitudes", with server SVD | Newest rank-heterogeneity work (personalised; we target one shared model) | (abs) |
| FedTreeLoRA (ICML 2026 poster); *Towards Federated LoRA with Rank Heterogeneity* (Byun & Lee, 2024, claims zero-padding dilutes high-rank clients) | 2026 / 2024 | — | Leads from a web-search summary | **UNVERIFIED** |

**Prior-art check for our spike** (frozen seed-generated A shared by all devices + *nested* heterogeneous ranks, i.e. device k trains the first r_k columns of B, which makes heterogeneous-rank aggregation exact). Two web searches on 2026-10-04 and the papers above surfaced no paper that states this exact combination. One search summary *asserted* that frozen A with zero-padding is "foundational", but cited no paper that does it. **Novelty is therefore UNVERIFIED, and we do not claim it.** The idea is a one-line consequence of FFA-LoRA's linearity, so we treat it as an enabling *design choice*, not as the contribution. The contribution claim rests on the full system (§6).

## 3. Weak devices, unequal work and dropouts
| Work | Venue | Mechanism (verified part) | Use |
|---|---|---|---|
| FedAvg ([1602.05629](https://arxiv.org/abs/1602.05629)) | AISTATS 2017 (title verified; venue from recall) | Weighted model averaging | Baseline |
| FedProx ([1812.06127](https://arxiv.org/abs/1812.06127)) | MLSys 2020 | Heterogeneous networks; proximal term (from recall) | Candidate local regulariser |
| **FedNova** ([2007.07481](https://arxiv.org/abs/2007.07481)) | arXiv 2020 | "heterogeneity in … computation speeds results in large variations in the number of local updates … Naive weighted aggregation … causes objective inconsistency" (abs) | **Step normalisation in our anchor** |
| SCAFFOLD ([1910.06378](https://arxiv.org/abs/1910.06378)); FedOpt ([2003.00295](https://arxiv.org/abs/2003.00295), ICLR 2021) | 2019 / 2021 | Control variates / server optimisers (from recall) | Next ratchet candidates (server momentum) |
| **MIFA** ([2106.04159](https://arxiv.org/abs/2106.04159)) | arXiv 2021 | Devices dropping out "beyond the control of the central server" severely affects FedAvg (abs). The memory of each device's latest update is from recall | **Memory of absent devices in our anchor** |
| FedAU ([2306.03401](https://arxiv.org/abs/2306.03401)) | ICLR 2024 | Unknown participation statistics in FedAvg (title) | Adaptive weights for unreliable devices |
| FedBuff ([2106.06639](https://arxiv.org/abs/2106.06639)) | AISTATS 2022 | Buffered asynchronous aggregation (title) | Async alternative for the finals demo |
| FedKSeed ([2312.06353](https://arxiv.org/abs/2312.06353)); FedRA ([2311.11227](https://arxiv.org/abs/2311.11227)) | ICML 2024 / arXiv 2023 | Full-parameter tuning "with communication cost under 18 kilobytes"; random layer allocation for heterogeneous devices (titles) | Ultra-weak-device options |
| DiLoCo ([2311.08105](https://arxiv.org/abs/2311.08105)), Streaming DiLoCo ([2501.18512](https://arxiv.org/abs/2501.18512)), Photon ([2411.02908](https://arxiv.org/abs/2411.02908)) | 2023–2025 | Low-communication training for "islands" of poorly connected devices (abs); Photon does federated LLM *pre*-training across "weakly-connected GPUs" (abs) | Outer-optimiser ideas transfer to our server step |

## 4. Dominance, fairness and robustness
| Work | Venue | Idea | Use |
|---|---|---|---|
| q-FFL, *Fair Resource Allocation in FL* ([1905.10497](https://arxiv.org/abs/1905.10497)) | ICLR 2020 | Re-weight toward high-loss devices (from recall) | Loss-aware weights (ratchet candidate) |
| AFL ([1902.00146](https://arxiv.org/abs/1902.00146)); Ditto ([2012.04221](https://arxiv.org/abs/2012.04221), ICML 2021) | 2019 / 2021 | Minimax over client mixtures; fair + robust personalisation (titles) | Fairness framing |
| Median / trimmed mean ([1803.01498](https://arxiv.org/abs/1803.01498), ICML 2018); centered clipping ([2012.10333](https://arxiv.org/abs/2012.10333), ICML 2021) | 2018 / 2021 | Byzantine-robust aggregation (titles) | Our median-norm clip is the light version |
| CLAIR ([2605.21217](https://arxiv.org/abs/2605.21217)) | 2026 | Detects contaminated clients in the LoRA subspace (abs) | Robustness extension |

No literature definition of a scalar "dominance index" was confirmed tonight. Ours (influence share in ΔW space) is labelled as our definition in `architecture/components.md`.

## 5. Benchmarks and frameworks
- **FedLLM-Bench** ([2406.04845](https://arxiv.org/abs/2406.04845)): "previous works all rely on arti[ficial]" partitions, so it offers realistic federated LLM datasets (abs). It is a target for the finals evaluation.
- **Flower** ([2007.14390](https://arxiv.org/abs/2007.14390), the framework paper; PyPI `flwr` 1.39.0 seen 2026-10-04). The FlowerTune LLM leaderboard page failed to load (transport error), so its datasets and baselines are **UNVERIFIED**.
- **FedScale** ([2105.11367](https://arxiv.org/abs/2105.11367), ICML 2022): system-performance benchmark with device behaviour (title). It is the source for realistic availability traces in the next iteration.
- PEFT 0.21.2 and torch 2.10 (MPS) run our skeleton today; PyPI also lists torch 2.14.1 and mlx-lm 0.32.0 (seen 2026-10-04).

## 6. What companies ship today
| Who | What is public (verified) | Status | Mechanism relevant to us |
|---|---|---|---|
| Google | *Towards FL at Scale: System Design* ([1902.01046](https://arxiv.org/abs/1902.01046)): "a scalable production system for Federated Learning in the domain of mobile devices, based on TensorFlow" (abs). *FL for Mobile Keyboard Prediction* ([1811.03604](https://arxiv.org/abs/1811.03604), Gboard; title) | **Production** (per the paper) | Synchronous rounds on many phones; dropout handling details to be re-read |
| Google (2025–26) | Blog posts *Toward provably private learning from federated data* and *Synthetic and federated … domain adaptation with LLMs for mobile applications*. Both pages timed out, so their claims (TEE-based FL, all Gboard LMs trained with FL+DP) are **UNVERIFIED** | — | — |
| Apple | *Federated Evaluation and Tuning for On-Device Personalization* ([2102.08503](https://arxiv.org/abs/2102.08503)): a "federated task processing system" for evaluation and tuning of on-device ML, later extended to FL of DNNs (abs) | **Production system** (per the paper) | Apple Intelligence 2025 adapters are inference-side; on-device *training* of LLM adapters is **UNVERIFIED** |
| Prime Intellect | INTELLECT-1 ([2412.01152](https://arxiv.org/abs/2412.01152)): 10B model, 1T tokens, "up to 14 concurrent nodes distributed across 3 continents" (abs) | Shipped model (open) | Training through node churn over the open internet |
| Flower Labs + Cambridge | Photon ([2411.02908](https://arxiv.org/abs/2411.02908)): federated LLM pre-training (abs). Flower framework | Research + OSS | Our C10 adapter targets Flower |
| Google DeepMind (affiliation UNVERIFIED) | DiLoCo / Streaming DiLoCo | Research | Outer-optimiser over pseudo-gradients |
| NVIDIA FLARE, Owkin, Apheris, Nous (Psyche), Pluralis, Templar, Gensyn | Not opened tonight | **UNVERIFIED**, re-queued | Contribution scoring in decentralised networks is the closest industry analogue to our dominance index |

**Where we borrow and where we differ.** We borrow production FL's synchronous rounds with a deadline, plus FFA-LoRA's frozen A, FedNova's normalisation and MIFA's memory. We differ in three ways. (1) We make heterogeneous ranks exact *and* cheap, so a phone-class device sends r_k·d_out floats per layer and nothing is lost in padding. (2) We optimise the **macro** objective (every device's domain counts equally) instead of n_k-weighted FedAvg. (3) We **audit** every round with per-device influence shares in ΔW space, so "quiet domination" becomes a number on a dashboard. Production systems (verified part) emphasise scale and privacy; none of the verified sources reports a per-device influence audit.

## 7. Implications for the design
1. Baselines must include FedAvg over A and B (homogeneous and heterogeneous rank), FFA-LoRA-style frozen A without our extras (`anchor_naive`), and, for the finals, FedEx-LoRA or FLoRA and RoLoRA (exact or alternating, trainable A).
2. Frozen A, step normalisation, memory and uniform weights are each published. The defensible contribution is the **integration + measurement**: exact heterogeneous-rank aggregation as the substrate that makes FedNova/MIFA/macro weights *exact* for LoRA, plus a dominance audit. Claim only that.
3. RoLoRA argues frozen A limits expressiveness. Test it directly: anchor vs trainable-A baselines at equal communication.
4. Use FedLLM-Bench or FlowerTune datasets for the finals once the network allows; the local-text domains are the overnight proxy.
