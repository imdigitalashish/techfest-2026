# C7 Round orchestrator — component research

**Contract:** `ExperimentConfig` + `availability_schedule` → per-round log + `RunSummary`. **Isolated metric:** max round-to-round rise in macro loss (stability) and macro loss at a fixed wall-clock budget.

- **Today:** synchronous rounds with a deadline; devices cut off by the deadline either send partial work (anchor) or are discarded (baselines); offline devices skip the round. One shared base model in memory; LoRA state swapped per device.
- **SOTA:** production FL uses synchronous rounds on large device populations (Google system-design paper, 1902.01046, verified abstract); asynchronous buffered aggregation (FedBuff, AISTATS 2022) removes the round barrier; MIFA (2106.04159) shows FedAvg degrades when devices drop "beyond the control of the central server".
- **Candidates:** (1) deadline-aware partial work [built]; (2) FedBuff-style buffer of K updates with staleness discount s(τ)=(1+τ)^-½ [next]; (3) over-selection of devices per round [cheap]; (4) adaptive deadline from device speed history [stretch].
- **Risk:** async + memory can double-count a device; the accountant (C8) must see used_memory_for (already in `AggregationReport`).
