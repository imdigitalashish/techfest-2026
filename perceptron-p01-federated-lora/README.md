# Perceptron P1: cheap fine-tuning across weak, scattered devices (federated LoRA)

Journal and current state: [thought_node.md](thought_node.md). Architecture: [architecture/components.md](architecture/components.md) · [ADR 001](architecture/adr/001-spike.md). Novelty position: [research/novelty.md](research/novelty.md). Round-1 abstract: [deliverables/round1-abstract.md](deliverables/round1-abstract.md) (rendered from its template). Reviews: [reviews/](reviews/) and [ledger](reviews/ledger.tsv).

## Reproduce (Apple-silicon Mac, Python 3.11)
```bash
cd perceptron-p01-federated-lora
uv venv --python 3.11 .venv && source .venv/bin/activate
uv pip install -r requirements.txt            # pinned, incl. flwr 1.39.0
pytest -q                                     # 19 CPU tests (contracts, aggregators, Flower adapter), ~20 s
# data: the exact token blocks every reported run used are committed (eval/data/*.npz, sha1 c5a6afcf6d80) and
# loaded first; ./scripts/fetch_data.sh only matters for rebuilding from sources (may differ, see data_manifest)
python scripts/data_manifest.py               # leakage check + document manifest → eval/results/data_manifest.json
# experiments: one run at a time under nice 10, paused while kern.memorystatus_level < 25 %
scripts/handover_to_queue.sh 0                # works through eval/queue.txt; finished runs are skipped
python -m eval.summarize --tag v2             # → eval/results/v2_summary.md + v2_canonical.json (paired CIs)
python -m eval.dropout_analysis --tag v2      # → eval/results/v2_dropout_analysis.md (+ canonical)
python scripts/render_deliverable.py deliverables/round1-abstract.template.md deliverables/round1-abstract.md
python scripts/check_numbers.py deliverables/round1-abstract.md --tag v2   # every quoted number vs results
python scripts/check_claims.py --tag v2      # every qualitative claim (12) vs results
```
SmolLM2-135M must be in the local HF cache (`huggingface-cli download HuggingFaceTB/SmolLM2-135M`). One 12-round run takes about 2 min on the M5 GPU when it is not shared. MPS runs are deterministic here: reruns across code revisions were bit-identical (thought node, 11:45).

## Layout
- `components/`, one folder per component: `data_partitioner`, `device_simulator`, `local_trainer`, `aggregator` (+ `autoresearch/`), `orchestrator`, `flower_adapter`, plus `contracts.py`.
- `eval/`: harness, queue, summariser, dropout analysis, committed token blocks, results and per-round logs.
- `research/`: landscape, novelty, per-component notes, verified sources, raw agent notes.
- `architecture/`: components, JSON-Schema contracts, ADRs.
- `deliverables/`, `reviews/`, `scripts/`, `tests/`.
