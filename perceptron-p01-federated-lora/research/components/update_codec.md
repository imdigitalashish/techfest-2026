# C5 Update codec — component research

**Contract:** tensors → payload + bytes. **Isolated metric:** upload bytes per round at ≤ 1 % relative reconstruction error of the applied update.

- **Today:** fp32. FedAvgAB uploads A and B (r_k·(d_in+d_out) floats per layer); the anchor uploads only ΔB columns (r_k·d_out) because A is regenerated from a shared seed. Measured upload per run (12 rounds): 22.1 MB per device for the homogeneous-rank baseline vs 0.4–2.9 MB per round for anchor devices in the smoke test.
- **Candidates:** fp16/int8 quantisation of ΔB with error feedback; top-k sparsification; seed-based zeroth-order payloads for the weakest devices (FedKSeed, ICML 2024: "communication cost under 18 kilobytes" — title).
