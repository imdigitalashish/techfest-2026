# C8 Contribution accountant — component research

**Contract:** per-device intended contributions c_k (ΔW space) + applied update P → influence shares s_k = ⟨c_k,P⟩/‖P‖². **Isolated metric:** Spearman correlation between s_k and leave-one-device-out change in macro loss (ground truth; costs K extra runs).

- **Today:** computed every round inside the aggregator (`product_space_report`), layer by layer; exact schemes give Σ s_k = 1. Under FedAvg over A,B the data-rich device's share is ≈ 1.02–1.04 (> 1 because inexact aggregation adds cross terms) — measured, `eval/results/v1_*.jsonl`.
- **Literature (tonight):** data-Shapley / leave-one-out contribution in FL and incentive scoring in decentralised training networks are the right comparators; no accepted scalar "dominance index" was confirmed tonight → ours is labelled as our definition.
- **Candidates:** cap s_k online (water-filling weights so no device exceeds 1/K + ε); loss-aware weights (q-FFL); dashboard bar per round for the finals demo; Shapley approximation over the 5 devices (2^5 = 32 subsets is cheap with the anchor because aggregation is linear).
