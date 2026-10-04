# Perceptron P1: cheap fine-tuning across weak, scattered devices (federated LoRA)

Journal and current state: [thought_node.md](thought_node.md). Architecture: [architecture/components.md](architecture/components.md) · [ADR 001](architecture/adr/001-spike.md). Round-1 draft: [deliverables/round1-abstract.md](deliverables/round1-abstract.md).

## Reproduce (Apple-silicon Mac, Python 3.11)
```bash
cd perceptron-p01-federated-lora
uv venv --python 3.11 .venv && source .venv/bin/activate
uv pip install -r requirements.txt            # pinned; overnight it was installed offline from the uv cache
./scripts/fetch_data.sh                       # WikiText-103 to the HF cache + tokenised blocks in .data/
pytest -q                                     # 7 contract tests, CPU, ~20 s
python -m eval.run_matrix --scenario dropout --seeds 0 1 --tag v1   # 4 strategies × 2 seeds
python -m eval.run_matrix --scenario clean   --seeds 0 1 --tag v1
python -m eval.summarize --tag v1             # → eval/results/v1_summary.md
python -m components.aggregator.autoresearch.eval --strategy anchor_full   # frozen ratchet metric
```
SmolLM2-135M must be in the local HF cache (`huggingface-cli download HuggingFaceTB/SmolLM2-135M`). One 12-round run takes ~8–15 min on an idle M5 GPU, and longer when the GPU is shared.

## Layout
`components/` (one folder per component: data_partitioner, device_simulator, local_trainer, aggregator (+ autoresearch/), orchestrator, contracts.py) · `eval/` (harness, results, per-round logs) · `research/` (landscape, per-component notes, verified sources) · `architecture/` (components, JSON-Schema contracts, ADRs) · `deliverables/` · `scripts/` · `tests/`.
