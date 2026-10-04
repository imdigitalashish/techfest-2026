# C4 Local trainer — component research

**Contract:** `ClientTask` + global view + token blocks → updated tensors + `ClientUpdate`. **Isolated metric:** local held-out loss drop per second and peak memory, per device class.

- **Today:** HF PEFT 0.21.2 LoRA (q_proj, v_proj; r_max 16, α 32) on SmolLM2-135M, AdamW lr 1e-3, grad-clip 1.0, fp32 on MPS (torch 2.10). Rank budget enforced by gradient masks; anchor mode trains B only (≈ half the trainable parameters).
- **Measured:** ~0.7 s per step at batch 8×128 on the M5 *while ~20 other projects share the GPU* (smoke test 06:20 IST) — not a clean throughput number.
- **Candidates:** bf16 autocast on MPS (≈2× faster, numerics to check); MLX-LM LoRA trainer for Apple-silicon devices (mlx-lm 0.32.0 on PyPI, UNVERIFIED API); QLoRA-style 4-bit base for phone-class memory; gradient checkpointing; FedProx proximal term for drift (FedProx, MLSys 2020).
- **Next:** profile clean throughput when the machine is idle; add peak-memory logging per device class (needed for the "weak device" claim).
