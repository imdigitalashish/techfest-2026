# Perceptron P2 — Recall-on-Demand (KV-cache compression)

Techfest 2026 (IIT Bombay) · Perceptron Hackathon (IITB × Optiver) · Theme 1, Problem 2: *Squeezing Long-Context Inference into Less Memory*.

**Idea.** Treat the KV cache as a cache, not a store. After prefill, keep:
- a small resident cache (StreamingLLM sinks plus recent tokens);
- a 4-bit key index of one layer (0.88% of the cache);
- the token ids.

When a question arrives, its own attention queries pick which evicted 64-token blocks to recompute at their original positions.

**Headline** (rendered from committed results by `eval/render_docs.py`):
<!-- p2:headline:begin -->
On 12 held-out ~4k-token contexts (48 questions; Llama-3.2-1B-Instruct) the full cache recalls 83%. At 25% of the KV memory, ten query-agnostic baselines recall 0%–35% and RoD 58%: +0.40 over StreamingLLM (95% CI +0.25 to +0.54; pre-registered), yet 0.25 below the full cache. At 10% memory RoD recalls 85% (baselines ≤6%); on fresh paraphrased contexts it recalls 69% vs the full cache's 46% (+0.23, 95% CI +0.10 to +0.38), but 12 of the full cache's 26 misses are answers cut off by our 10-token limit (with 32 tokens and first-number scoring: full 67%, RoD 75%; exploratory).
<!-- p2:headline:end -->

| What | Where |
|---|---|
| Round-1 abstract (≤ 900 words) and diagram | [deliverables/round1-abstract.md](deliverables/round1-abstract.md) · [deliverables/architecture.md](deliverables/architecture.md) |
| Selection memo (scores by pre-fixed rules) | [deliverables/selection-memo.md](deliverables/selection-memo.md) |
| All results, verdicts, diagnostics | [eval/RESULTS.md](eval/RESULTS.md) |
| Pre-registration and amendments | [eval/PREREG.md](eval/PREREG.md) |
| Harness (every number) · parity · identity checks | [eval/kvbench_torch.py](eval/kvbench_torch.py) · [eval/results/parity_torch.json](eval/results/parity_torch.json) · [eval/results/identity_check_dev100.json](eval/results/identity_check_dev100.json) |
| Spike decision (ADR 001, v1 → v3) · components and contracts | [architecture/adr/001-spike.md](architecture/adr/001-spike.md) · [architecture/components.md](architecture/components.md) |
| State of the art, what companies ship, prior art | [research/landscape.md](research/landscape.md) · [research/components/](research/components/) |
| Cross-model reviews and triage | [reviews/](reviews/) · [reviews/ledger.tsv](reviews/ledger.tsv) |
| Demo (replay by default, `--live` opt-in) | [demo/](demo/) |
| Journal | [thought_node.md](thought_node.md) |

**Reproduce** (Azure CPU VM; see `eval/azure/`):
1. `run_on_azure.sh create`
2. `setup` (runs `setup_torch.sh`, then `setup_kvp.sh`)
3. The `T1`/`T2`/`S4`/`T3` commands in [eval/PREREG.md](eval/PREREG.md)
4. `python3 eval/render_docs.py && python3 eval/check_docs.py`
