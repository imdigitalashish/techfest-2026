# Per-component research — index (v1, lean mode)

> Lean mode (Supervisor, 05:50 IST) allowed per-component research to live as sections of [`../landscape.md`](../landscape.md) for the morning package. This index maps each component to its evidence and innovation candidates. Dedicated files per spike component follow once sub-agents are allowed again.

| Component | Landscape section | State of the art (cited there) | Innovation candidates (scored in ADR 001) | Isolated metric |
|---|---|---|---|---|
| C1 LogIngest | §9 | OBD schema (obd/README.md) | propensity sanity checks; detecting deterministic logging (no overlap) automatically | validation pass rate |
| C2 PolicyAdapter | §9, `eval/results/obd_sample_summary.md` | obp BernoulliTS Monte-Carlo action distribution | **found tonight:** the deployed BTS ≠ the static obp prior (correlation 0.074 with the logged propensities). Candidate: a time-varying or empirical evaluation policy | MC error; agreement with logged propensities |
| C3 PropensityModel | §4 | logged vs estimated propensities (Jeunen & London 2023) | calibrated propensity estimation when propensities are unlogged; feeds C8 | held-out log-loss |
| C4 RewardModel | §2 | DM/DR reward models; MRDR (1802.03493) | MRDR-style training for Δ; embeddings (2509.00648) | held-out log-loss |
| C5 ValueEstimator | §2, §6 | IPW, SNIPW, DR, Switch, DRos, MIPS/OffCEM, LS (2405.14335), LSE (2506.06873), kernel IS (2607.15067), nonparametric (2603.09436) | estimator selection (AutoOPE 2406.18022; SharpeRatio 2311.18207) | relative error, RMSE |
| C6 DeltaEstimator | §2 | Δ-OPE (2405.10024), additive control variates (2602.14914), baseline corrections (2405.05736) | ratchet (`components/delta_estimator/autoresearch/`) | nRMSE on the mini bank |
| C7 Interval ★ | §3 | Wald, bootstrap, EL (1906.03323), off-policy confidence sequences (2102.09540), anytime-valid (2210.10768), PERRY (2507.20068) | coverage-guaranteed Δ intervals under low overlap (S5: Switch-DR covers only 0.63) | coverage + width |
| C8 Sensitivity ★ | §4 | MSM (1805.08593), percentile bootstrap (1711.11286), sharp bounds (2102.04543; 2502.13022), OVB benchmarking (2112.13398) | joint Γ-bounds for Δ with a DR estimator; Γ\* benchmarked against observed covariates | validity at Γ_true + width |
| C9 Decomposer ★ | §1, §5, §8 | distribution-shift attribution (2210.10769), future OPE (2506.20417), CausalImpact (1506.00356) | DR-based mix term (density ratio) instead of DM; feedback-loop term | RMSE + sign of the policy term |
| C10 Report + overlap gate ★ | §7 | production pattern (Adyen 2501.10470; Personalizer retired); ESS diagnostics are standard practice | **built:** an abstention gate (ESS/n, effective rewards, mean-weight z) calibrated on simulation only (`eval/gate_rule.json`); post hoc on OBD, 0 confident wrong answers | confident-wrong count, abstention rate |
| C11 Simulator | §5 | obp synthetic; feedback-loop simulations (1710.11214) | knobs for feedback loops and novelty decay | truth precision |
