# Results (rendered by `eval/render_docs.py` from committed rows; do not edit by hand)

Pre-registration: [`PREREG.md`](PREREG.md). Engine parity: [`results/parity_torch.json`](results/parity_torch.json).

## Pre-registered verdicts

- **Primary** (RoD − StreamingLLM, keep 0.25, T1): pending → pending
- **S1** (RoD vs each query-agnostic baseline, keep 0.25, T1): pending
- **S2** (RoD − RoD-lexical, keep 0.25, T1 literal): pending
- **S2** (RoD − RoD-lexical, keep 0.25, T2 paraphrase): pending
- **S3** (primary replicated on T2 paraphrase): pending

## Memory accounting

Stored KV MiB = analytic bytes = layers × kv_heads × kept tokens × head_dim × 2 (K,V) × 2 B (fp16), plus quantisation scales/biases and, for RoD, the 4-bit sketch, 256 KiB of window queries and int32 token ids. The harness asserts that the full cache's measured tensor bytes equal T × 32 KiB. Answer-time MiB adds RoD's recalled blocks. CPU seconds are relative only.

