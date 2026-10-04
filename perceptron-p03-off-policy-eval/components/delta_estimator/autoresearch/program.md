# Ratchet program — C6 DeltaEstimator

**Goal.** Minimise `nRMSE`: the mean over the mini-bank scenarios of RMSE(Δ̂ − Δ_true)/|Δ_true|. Δ is the after-period policy effect, V(deployed) − V(old). The value is printed by the frozen `eval.py`.

**Constraints.**
- Edit only `components/delta_estimator/delta.py`. Keep the contract `estimate_delta(log, pi_old, q) -> DeltaEstimate`, with per-round `influence` whose mean is the estimate.
- Contract tests must pass (`.venv/bin/python -m pytest -q tests`).
- Secondary guard: `min_coverage` (95% Wald on the returned influence) must stay ≥ 0.90. Never buy RMSE with over-confident intervals.
- Keep a change only if nRMSE improves by more than the seed noise (the change must hold on a re-run with `SEEDS` doubled), *and* does not degrade `--holdout` by more than noise. The lead re-checks the holdout every 5 kept changes.
- Log every attempt in `results.tsv`: timestamp · commit · hypothesis · metric · delta · kept? · notes.

**Idea backlog** (from `research/landscape.md` §2):
1. SNDR (self-normalised DR residual).
2. Switch-DR with τ chosen by an estimated-MSE rule (Wang et al., arXiv:1612.01205).
3. DR with optimistic shrinkage, λ by estimated MSE (Su et al., arXiv:1907.09623).
4. Variance-optimal additive baseline / control variate for Δ, shared between the two policies (Δ-OPE, arXiv:2405.10024; Gupta et al., arXiv:2405.05736; Jeunen & Gupta, arXiv:2602.14914).
5. Weight clipping with a bias-correction term.
6. MRDR-style reward-model weighting (arXiv:1802.03493).
7. More cross-fitting folds or a better reward model (a C4 change, so it is scored separately).
8. Logarithmic smoothing of large weights (arXiv:2405.14335).
