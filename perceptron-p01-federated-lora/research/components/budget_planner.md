# C3 Budget planner — component research

**Contract:** `DeviceProfile` → `ClientTask` (rank, steps, lr, layers). **Isolated metric:** loss reduction per device-FLOP at a fixed deadline-miss rate.

- **Today:** static — rank and steps come from the profile (memory budget → rank, compute budget → steps). With the anchor, rank is free to differ per device at zero aggregation cost.
- **Candidates:** per-layer rank allocation (top layers get rank on weak devices); FedRA-style random layer allocation (2311.11227, title verified); adaptive steps from measured speed so devices finish inside the deadline instead of being cut off.
