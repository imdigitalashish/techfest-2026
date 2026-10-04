# What companies ship today: federated, on-device, and decentralized training

Access date for every source: 2026-10-04. Primary sources only. `UNVERIFIED` means I opened/searched, but the page failed, returned only non-claim text, or no primary source was found in the time box.

## Executive summary

- Apple ships Apple Intelligence foundation models and LoRA-style adapters, but public docs point to **offline/toolkit training and on-device inference**, not end-user-device adapter training. The adapter docs say developers “train adapters” with a Python/Jupyter toolkit and then users download adapter assets.
- Apple does publish real Private Federated Learning research/tooling: FL+DP “without revealing any data,” `pfl-research`, and population-expansion methods for small FL populations. This is closer to our weak-device/dropout problem than Apple Intelligence adapters are.
- Google is the clearest production cross-device FL example: Gboard has “more than twenty” deployed language models with DP guarantees, and newer Gboard work combines synthetic data and federated/privacy-preserving domain adaptation.
- Google Parfait exists publicly as privacy/federated tooling (`google-parfait/federated-language`), but Google’s Parfait blog page fetched only acknowledgements, so detailed Parfait claims are marked UNVERIFIED.
- NVIDIA FLARE, Flower, TensorOpera/FedML, Apheris, Owkin/Substra, Sherpa.ai, and Rhino mostly ship platforms or pilots for cross-silo FL, not consumer weak-device LLM fine-tuning; NVIDIA/Apheris/Flower explicitly cover PEFT/LoRA-style fine-tuning.
- Swift/Google Cloud/Capgemini/Rhino show a finance pilot: model copies go to banks, banks train locally, only learnings return for aggregation in TEE/secure aggregation.
- Decentralized-training companies ship research/announced networks rather than classic FL: Prime Intellect, Nous/Psyche, Gensyn, Pluralis, and Templar handle heterogeneous nodes via async/gossip/hierarchical or incentive mechanisms.
- Contribution fairness is most explicit in Templar and Prime Intellect: Templar validators score miner gradients by loss improvement; Prime Intellect validates rollout computation with TOPLOC. This directly informs our per-device influence audit.

## Table

| Company | What ships | Status | Date | Mechanism relevant to weak devices / dropout / contribution fairness | Source URL | Verified? |
|---|---|---:|---:|---|---|---|
| Apple | Third-gen AFM: on-device AFM 3 Core/Core Advanced plus PCC server models. | Announcement / beta | 2026 | On-device sparse model activates “1 to 4 billion parameters”; specialized image adapters are for downstream experiences. No public on-device adapter training claim. | https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models | VERIFIED |
| Apple | Foundation Models framework + adapter training toolkit. | Production developer tooling | 2025 | “LoRA adapter fine-tuning”; docs say toolkit has Python sample code, Jupyter notebook, exports `.fmadapter`; users download adapters as app assets, so adapters appear trained off-device and shipped for inference. | https://developer.apple.com/apple-intelligence/foundation-models-adapter/ | VERIFIED |
| Apple | Apple Intelligence 2024 foundation models. | Production | 2024 | Base model remains frozen; adapters are “dynamically loaded and swapped”; private user data is not used to train foundation models. | https://machinelearning.apple.com/research/introducing-apple-foundation-models | VERIFIED |
| Apple | Private FL research (`pfl-research`, population expansion). | Research / open source | 2024 | FL lets clients train a global model “without revealing any data”; `pfl-research` is “7-72× faster”; population expansion improves small-population FL utility “13% to 30%.” | https://machinelearning.apple.com/research/pfl-research ; https://machinelearning.apple.com/research/population-expansion | VERIFIED |
| Google | Gboard FL language models with DP. | Production | 2023+ | “More than twenty Gboard LMs” deployed with zCDP; “all future launches” require DP. Uses DP-FTRL, client participation criteria, secure aggregation for some models. | https://research.google/pubs/federated-learning-of-gboard-language-models-with-differential-privacy/ | VERIFIED |
| Google | Gboard synthetic + federated/privacy-preserving domain adaptation. | Production research | 2025 | Gboard uses small LMs and LLMs for “billions of users”; prior mobile typing FL/post-training yielded “3%–13% improvements.” | https://research.google/blog/synthetic-and-federated-privacy-preserving-domain-adaptation-with-llms-for-mobile-applications/ | VERIFIED |
| Google | Parfait / federated-language. | Open-source tooling | 2025 | GitHub says “framework for implementing federated algorithms and computations on privacy-sensitive data.” Main Parfait blog opened but returned only acknowledgements. | https://github.com/google-parfait/federated-language ; https://research.google/blog/parfait-enabling-private-ai-with-research-tools/ | PARTIAL |
| Meta + NVIDIA | FLARE + ExecuTorch mobile FL integration. | Framework / announcement | 2025 | Handles edge training where devices join/leave; hierarchical tree aggregation; ExecuTorch enables on-device training. No Meta product deployment found. Meta engineering URL searched/fetched returned 404. | https://developer.nvidia.com/blog/effortless-federated-learning-on-mobile-with-nvidia-flare-and-meta-executorch/ | VERIFIED/UNVERIFIED for Meta production |
| Microsoft | FLUTE. | Research simulator | 2022 | Simulates tens of thousands of clients; clients send pseudo-gradients; explicitly for testing “before implementing…in a production framework.” | https://www.microsoft.com/en-us/research/blog/flute-a-scalable-federated-learning-simulation-platform/ | VERIFIED |
| NVIDIA | NVIDIA FLARE LLM PEFT/SFT. | Production-grade framework | 2024 | For PEFT, foundation LLM weights are frozen and “only these parameters are tuned at local clients, and aggregated”; supports FedAvg and streaming large files. | https://developer.nvidia.com/blog/scalable-federated-learning-with-nvidia-flare-for-enhanced-llm-performance/ | VERIFIED |
| Flower Labs | LLM FlowerTune example. | Open-source examples / benchmark | 2024 | Federated instruction tuning with Llama2 + HF PEFT; 3B 4-bit model about 10.6GB VRAM; “single GPU” simulation. Photon/enterprise claims not verified. | https://flower.ai/blog/2024-03-14-llm-flowertune-federated-llm-finetuning-with-flower | VERIFIED |
| Apheris + AWS | Federated LoRA fine-tuning of ESM-2 protein LM. | Platform / consortium pilot | 2025 | Apheris Gateway fine-tunes ESM-2 with LoRA/FRA-LoRA; sites share full weights or adapters; PEFT reduces parameters to “two percent.” | https://aws.amazon.com/blogs/industries/federated-learning-based-protein-language-models-with-apheris-on-aws/ | VERIFIED |
| Owkin / MELLODDY | Pharma consortium FL for drug discovery. | Completed industrial pilot | 2022 | 10 pharma companies; data/models never leave owner custody; trained on “billions” of datapoints and 20M molecules; collaborative models improved 2–10%. | https://www.melloddy.eu/y3announcement ; https://www.owkin.com/federated-learning | VERIFIED |
| Sherpa.ai | Federated Learning platform. | Commercial platform | 2024/2026 page | Page metadata says platform “enables organizations to collaboratively train” global models; simplifier failed on body, so mechanism details unverified. | https://sherpa.ai/federated-learning/ | PARTIAL |
| TensorOpera/FedML | TensorOpera Federate. | Commercial platform | Current docs | “Zero-code…cross-platform…federated learning”; cross-device SDK for Android/iOS/embedded Linux. | https://docs.tensoropera.ai/federate/ | VERIFIED |
| Swift + Google Cloud + Capgemini + Rhino | Bank fraud FL prototype. | Pilot/prototype | 2025 | Swift model sent to banks; banks train locally; only learnings return; FL server in TEE and secure aggregation. Initial scope is “synthetic data sandbox.” | https://cloud.google.com/blog/products/identity-security/google-cloud-and-swift-pioneer-advanced-ai-and-federated-learning-tech | VERIFIED |
| Prime Intellect | INTELLECT-2/3 decentralized RL training. | Public research/model release | 2025 | INTELLECT-2: “anyone can permissionlessly contribute” heterogeneous compute; 4×RTX 3090 enough; TOPLOC validates rollout workers. INTELLECT-3 HF page says 106B MoE with prime-rl. | https://www.primeintellect.ai/blog/intellect-2 ; https://huggingface.co/PrimeIntellect/INTELLECT-3 | VERIFIED |
| Nous Research | Psyche decentralized training. | Production model / research network | 2025 | Hermes 4.3 “post-trained entirely” on Psyche; 24 nodes, 144k tokens/s; smart-contract consensus plus mesh P2P gradients; stable run. | https://nousresearch.com/introducing-hermes-4-3 ; https://nousresearch.com/the-next-phase-of-psyche | VERIFIED |
| Gensyn | RL Swarm. | Open-source research demo | 2025 | “Peer-to-peer nodes” on consumer/datacenter hardware; Hivemind gossip; permissionless. Contribution scoring not found on opened page. | https://www.gensyn.ai/news/rl-swarm-a-framework-for-collaborative-rl | VERIFIED |
| Pluralis | Node0 / Protocol Learning. | Public training run / research | 2026 | Node0 accepts 16GB GPUs; “participants can join and leave at any time”; progress logged in dashboard. | https://github.com/PluralisResearch/node0 ; https://pluralis.ai/blog | VERIFIED |
| Templar / Bittensor | Templar decentralized training; now dormant. | Completed run / dormant | 2025 | Covenant-72B complete; miners share compressed gradients; validators score contribution as loss improvement before/after and set blockchain weights. | https://github.com/one-covenant/templar | VERIFIED |

## Where we borrow / where we differ

- Borrow LoRA/PEFT from Apple/NVIDIA/Apheris/Flower, but differ by fixing a shared LoRA A and using nested ranks so weak devices can submit exact aggregatable sub-updates.
- Borrow FL normalisation ideas from Google/NVIDIA/FLUTE, but add FedNova-style normalisation so devices that train fewer local steps or drop mid-run do not distort the round.
- Borrow cross-silo macro-weighting from healthcare/finance FL, but cap data-rich clients with macro weights so one big participant cannot dominate small devices.
- Borrow dropout tolerance from NVFLARE hierarchy, Pluralis, Gensyn, and Prime Intellect async designs, but maintain memory of absent devices rather than silently reweighting only survivors.
- Borrow contribution measurement from Templar loss-improvement scoring and Prime Intellect TOPLOC-style validation, but use a per-device influence audit for federated LoRA updates rather than token rewards.

## Source list

- Apple, “Introducing the Third Generation of Apple’s Foundation Models,” https://machinelearning.apple.com/research/introducing-third-generation-of-apple-foundation-models, accessed 2026-10-04.
- Apple, “Foundation Models framework adapter,” https://developer.apple.com/apple-intelligence/foundation-models-adapter/, accessed 2026-10-04.
- Apple, “Introducing Apple’s On-Device and Server Foundation Models,” https://machinelearning.apple.com/research/introducing-apple-foundation-models, accessed 2026-10-04.
- Apple, “pfl-research,” https://machinelearning.apple.com/research/pfl-research, accessed 2026-10-04.
- Apple, “Population Expansion for Training Language Models with Private Federated Learning,” https://machinelearning.apple.com/research/population-expansion, accessed 2026-10-04.
- Google Research, Gboard FL+DP publication page, https://research.google/pubs/federated-learning-of-gboard-language-models-with-differential-privacy/, accessed 2026-10-04.
- Google Research, “Synthetic and federated…,” https://research.google/blog/synthetic-and-federated-privacy-preserving-domain-adaptation-with-llms-for-mobile-applications/, accessed 2026-10-04.
- Google Parfait GitHub, https://github.com/google-parfait/federated-language, accessed 2026-10-04.
- NVIDIA, “Effortless Federated Learning on Mobile…,” https://developer.nvidia.com/blog/effortless-federated-learning-on-mobile-with-nvidia-flare-and-meta-executorch/, accessed 2026-10-04.
- Microsoft Research, FLUTE blog, https://www.microsoft.com/en-us/research/blog/flute-a-scalable-federated-learning-simulation-platform/, accessed 2026-10-04.
- NVIDIA, “Scalable Federated Learning with NVIDIA FLARE…,” https://developer.nvidia.com/blog/scalable-federated-learning-with-nvidia-flare-for-enhanced-llm-performance/, accessed 2026-10-04.
- Flower Labs, “LLM FlowerTune…,” https://flower.ai/blog/2024-03-14-llm-flowertune-federated-llm-finetuning-with-flower, accessed 2026-10-04.
- AWS/Apheris, “Federated learning-based protein language models…,” https://aws.amazon.com/blogs/industries/federated-learning-based-protein-language-models-with-apheris-on-aws/, accessed 2026-10-04.
- MELLODDY, “Year 3 Announcement,” https://www.melloddy.eu/y3announcement, accessed 2026-10-04.
- Owkin, “Federated Learning,” https://www.owkin.com/federated-learning, accessed 2026-10-04.
- Sherpa.ai, “Federated Learning,” https://sherpa.ai/federated-learning/, accessed 2026-10-04.
- TensorOpera, “What is TensorOpera Federate?”, https://docs.tensoropera.ai/federate/, accessed 2026-10-04.
- Google Cloud, “Google Cloud and Swift…,” https://cloud.google.com/blog/products/identity-security/google-cloud-and-swift-pioneer-advanced-ai-and-federated-learning-tech, accessed 2026-10-04.
- Prime Intellect, “INTELLECT-2,” https://www.primeintellect.ai/blog/intellect-2, accessed 2026-10-04.
- Prime Intellect, “INTELLECT-3” model card, https://huggingface.co/PrimeIntellect/INTELLECT-3, accessed 2026-10-04.
- Nous Research, “Introducing Hermes 4.3,” https://nousresearch.com/introducing-hermes-4-3, accessed 2026-10-04.
- Nous Research, “The Next Phase of Psyche,” https://nousresearch.com/the-next-phase-of-psyche, accessed 2026-10-04.
- Gensyn, “RL Swarm,” https://www.gensyn.ai/news/rl-swarm-a-framework-for-collaborative-rl, accessed 2026-10-04.
- PluralisResearch/node0, https://github.com/PluralisResearch/node0, accessed 2026-10-04.
- Templar, https://github.com/one-covenant/templar, accessed 2026-10-04.
