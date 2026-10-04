# C10 robust_conformal (spike) — research note and proofs

_Lead, 4 Oct 2026. Prior-art details and URLs: [`../notes/R2-robust-conformal-and-aggregation.md`](../notes/R2-robust-conformal-and-aggregation.md) and [`../landscape.md`](../landscape.md) §2._

## Positioning against prior art
| Work | Threat model | Task | What we take or differ on |
|---|---|---|---|
| RSCP → RSCP+ (ICLR 2022 → 2024) | ℓ2 test-time noise, randomized smoothing | classification | RSCP's guarantee was later shown to be flawed in practice — so we unit-test our certificate (`tests/`) |
| VRCP (NeurIPS 2024) | ℓ1/ℓ2/ℓ∞ via NN verification | classification + regression | closest regression precedent; we verify tree ensembles over a *data-derived* box instead of a norm ball |
| Zargarbashi et al. (ICML 2024) | evasion + poisoning, continuous and discrete | classification | same idea of bounding the worst-case conformity score; we derive the bound from a document budget |
| RCP1 (NeurIPS 2025) | randomized single-sample robustness | classification + regression | probabilistic; ours is deterministic and exact for the stated budget |
| Yin et al. (ICML 2018) | Byzantine fraction of inputs | distributed GD | trimmed mean / median as the bounded-influence primitive |
| **CR-ACI (ours)** | ≤ k injected documents per ticker-day; prices clean | regression on text + time series | deletion box → tree interval propagation → conformal offset tuned by ACI |

Novelty claim, worded carefully: *in our searches* (R2 note, §2.5) we found no conformal method certified against a budget of injected documents feeding a text + time-series regressor. An independent novelty check is pending (ADR 001).

## Why the deletion box is exact per feature
Let the observed sentiments be sorted, s₁ ≤ … ≤ s_n, and let m = n − j be the number of documents kept (j ≤ k removed).
1. **Mean and 20 % trimmed mean.** Both are non-decreasing in every order statistic. Any m-subset has i-th order statistic ≥ s_i (the i-th smallest overall) and ≤ s_{j+i}. So the minimum is attained by the m smallest values and the maximum by the m largest.
2. **Count features** (`log_n_docs`) depend only on m.
3. **Trust mean.** The same argument applied to the sorted trust weights; the box is per-feature, so it need not be the same subset as for sentiment (a sound relaxation).
4. **Standard deviation (population, ddof = 0).**
   - *Minimum:* a minimum-variance m-subset is contiguous in sorted order. Exchange argument: if a kept y₁ < z < y₂ with z removed, swapping z for whichever of y₁, y₂ is farther from the subset mean does not increase variance.
   - *Maximum:* a maximum-variance m-subset is a prefix plus a suffix. Exchange argument: for a kept y with removed z₁ < y < z₂, the variance change from replacing y by z is Δ = ((z − y)/m)·[(z − μ) + (y − μ) − (z − y)/m] (the 1/m factor was missing in v1; noted by gpt-6-astra — the sign argument is unchanged). If y ≥ μ, replacing y by z₂ gives Δ > 0. If y < μ, replacing y by z₁ gives Δ > 0. So no kept element can have removed elements on both sides, and the removed set is one contiguous block.
5. **Empty set.** When every document may be removed (m = 0), the aggregator's no-document values (all zeros) are included.

The joint feasible set is a subset of the product of these ranges, so the box is sound (possibly loose jointly). **Numerics (v2, after gpt-6-sol review B2):** v1 widened the box by a fixed ε = 1e-6, and the reviewer built a valid 50,003-post constant-sentiment day whose clean std fell outside it. v2 instead takes sums after centring at the median, and widens every bound by a round-off budget derived from the recursive-summation error bound: |δ var| ≤ (12 n²/m + 8) u X², and the same factor times (1 + max|s|) for mean-like features, plus 1e-12 for the aggregator's own rounding. It is valid for n ≤ 10⁶ posts per stock-day (enforced). Tests: brute-force exactness on 40 random small cases, the reviewer's case, and five random 5,000–60,000-post days.

## Why the tree bound is sound
For an axis-aligned box, each tree's reachable leaves are found by descending both children whenever the box straddles the split threshold. Then:

min over box of Σ_trees f_t(x) ≥ Σ_trees min over box of f_t(x)

and similarly for the maximum. LightGBM folds the initial score into the first tree; a degenerate box reproduces `predict` exactly (error 0 on the test set; also tested on synthetic data).

## Guarantee
Let D be the clean documents and D′ ⊇ D the observed ones, with |D′ \ D| ≤ k. Then features(D) ∈ B_k(D′). So, **for the same offset q**, [LB − q, UB + q] ⊇ [q̂_lo(x) − q, q̂_hi(x) + q].
- **Fixed-offset certified CQR (q = split-CQR offset from clean calibration data):** every row that the clean interval covers is covered under any attack within budget. Coverage is ≥ 1 − α under exchangeability of clean calibration and test data. The measured "floor" (e.g. 86.7%) is this test set's clean coverage, a retrospective number rather than a future probability.
- **CR-ACI (q_t adapted online):** per-row containment holds only against an ACI run that uses the *same* q_t sequence. The defender's run adapts to observed, possibly attacked, outcomes, so the clean and attacked runs are **not nested** (counterexample from gpt-6-sol, kept as `tests/test_review_fixes.py::test_separately_adapted_aci_runs_are_not_nested`). What CR-ACI keeps is ACI's arbitrary-sequence guarantee on long-run *mean daily* miscoverage, with worst-case bound (max(α, 1−α) + γ)/(γT). That bound is weak at our horizon (≈ 0.48 at T = 189, γ = 0.01).
- **Not a recovery of price-only:** deleting all documents under the fixed fusion model gives the fusion model's no-text input, not a separately trained price-only model. Large k gives an envelope, and price-only is a separate zero-exposure alternative (gpt-6-astra #7).

**Not covered:** edits of real documents (planned: replace ≤ k documents by any value in [−1, 1]), attacks on prices, true-but-misleading news, poisoned calibration data, and cross-day attacks on history features (excluded by design: no attention-history feature in the certified model).

## Measured (`eval/results/baseline_v0.md`)
- Certified CQR width costs +2.9% / +3.9% / +4.5% / +5.1% for k = 1 / 2 / 3 / 5 on clean data.
- Oracle attack at k = 3: 88.0% coverage certified vs 84.4% for plain CQR.
- CR-ACI: 89.5% clean / 89.7% under the pump attack, at +0.3% width vs plain ACI.

## Innovation backlog (ratchet `autoresearch/program.md`)
Tighter boxes (drop loose features — h1 kept), monotone constraints, a two-tier budget by trust, an edit budget, regime-conditional offsets (MAPIE `ConditionalSplitConformalRegressor`), and certifying the decision ("interval excludes 0") rather than the interval.
