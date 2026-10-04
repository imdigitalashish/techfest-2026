# C5 Update codec — component research

**Contract:** tensors → payload + bytes. **Isolated metric:** upload bytes per round at ≤ 1 % relative reconstruction error of the applied update.

- **Today:** fp32. FedAvgAB uploads A and B (r_k·(d_in+d_out) floats per layer); the anchor uploads only ΔB columns (r_k·d_out) because A is regenerated from a shared seed. Measured upload over 12 rounds (dropout scenario, same participation): fedavg_ab_het 44.2 / 16.6 / 4.6 / 4.1 / 2.8 MB (c0…c4) vs anchor_naive 17.7 / 6.6 / 1.8 / 1.7 / 1.1 MB, a 2.5× reduction (r·768 vs r·1,920 floats per q/v layer pair). The homogeneous rank-8 starter uploads 22.1 MB per always-on device in the clean scenario.
- **Candidates:** fp16/int8 quantisation of ΔB with error feedback; top-k sparsification; seed-based zeroth-order payloads for the weakest devices (FedKSeed, ICML 2024: "communication cost under 18 kilobytes" — title).
