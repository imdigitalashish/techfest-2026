# C1 Data partitioner — component research

**Contract:** corpus spec → train/eval token blocks per domain (`[N,128]`). **Isolated metric:** realised skew vs target (per-device domain mix and size share).

- **Today (overnight proxy, real text, no synthetic data):** 5 domains from text already on the machine — WikiText-103 (local HF cache), Python sources, PyTorch C/C++ headers, package READMEs, macOS man pages; train/eval split by file hash (no document crosses the split); 48 × 128-token eval blocks per domain; quantity skew 2,400 vs 300 (×8) blocks. Chosen because PyPI/HF downloads ran at ~0.3–0.6 KB/s overnight.
- **SOTA / standard:** Dirichlet label partitions (flwr-datasets `DirichletPartitioner`); naturally-federated LLM datasets (FedLLM-Bench, 2406.04845: prior work "rel[ies] on artificial" partitions — verified abstract); FlowerTune finance/medical/code challenges (page not loadable tonight — UNVERIFIED).
- **Next:**
  1. FlowerTune Finance data (`flwrlabs/fingpt-sentiment-train`, MIT, 76,772 examples; evaluation is FPB/FiQA/TFNS accuracy), re-partitioned with `flwr_datasets.partitioner.DirichletPartitioner` at α ∈ {0.1, 0.5} plus quantity skew. FlowerTune itself is IID, so non-IID splits are our addition.
  2. Dolly-15k by category.
  3. Keep the local-text domains as a fast regression suite.
