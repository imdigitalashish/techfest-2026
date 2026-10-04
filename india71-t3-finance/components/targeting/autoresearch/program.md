# C6 ratchet loop — program (written by the lead)

**Goal.** Raise the normalised policy value of the `uplift` policy — the share of the oracle's achievable incremental meaningful usage, above random, captured at a fixed budget — on SYNTHETIC held-out persons.

**Metric.** `python components/targeting/autoresearch/eval.py` prints `METRIC <x>` = mean over seeds 0–2 (20,000 persons each, ₹10 per eligible person). Higher is better. Baseline 0.3396 (T-learner, HistGradientBoosting, Lagrangian allocation). Reference points: best-average-arm-for-all 0.3835, oracle 1.0.

**Rules.** Edit only `components/targeting/engine.py`. `eval.py`, the simulator and `eval/targeting_eval.py` are frozen. Keep a change only if METRIC improves by more than 0.01 (≈ ¼ of the seed s.d.); log every attempt in `results.tsv` (kept or not). Every 5 kept changes the lead re-checks on fresh seeds 10–12 to catch overfitting to seeds 0–2. The women's-share floor must stay on.

**Idea backlog (ordered).**
1. Shrink per-person uplift toward each arm's pilot average (empirical-Bayes style), κ ∈ {0.25, 0.5}.
2. Hybrid: give the cheapest positive-ATE arm to everyone first, spend the remainder on expensive arms by predicted uplift.
3. S-learner / X-learner / DR-learner instead of the T-learner (pool strength across arms).
4. Allocate expensive arms by a lower confidence bound (bootstrap the pilot).
5. Policy selection: choose among {learned, best-arm, hybrid} by doubly-robust policy value on a pilot split.
6. Feature work: interactions for KYC-due × inoperative, women × BC Sakhi, phone × literacy.
