# C1 Data partitioner — component research

**Contract:** corpus spec → train/eval token blocks per domain (`[N,128]`). **Isolated metric:** realised skew vs target (per-device domain mix and size share).

- **Today (overnight proxy, real text, no synthetic data):** 5 domains from text already on the machine — WikiText-103 (local HF cache), Python sources, PyTorch C/C++ headers, package READMEs, macOS man pages; train/eval split by file hash (no document crosses the split); 48 × 128-token eval blocks per domain; quantity skew 2,400 vs 300 (×8) blocks. Chosen because PyPI/HF downloads ran at ~0.3–0.6 KB/s overnight.
- **SOTA / standard:** Dirichlet label partitions (flwr-datasets `DirichletPartitioner`); naturally-federated LLM datasets (FedLLM-Bench, 2406.04845: prior work "rel[ies] on artificial" partitions — verified abstract); FlowerTune finance/medical/code challenges (page not loadable tonight — UNVERIFIED).
- **Next:** (1) a FlowerTune-finance-style task (financial sentiment, Optiver-relevant) with Dirichlet α ∈ {0.1, 0.5}; (2) Dolly-15k by category; (3) keep the local-text domains as a fast regression suite.
