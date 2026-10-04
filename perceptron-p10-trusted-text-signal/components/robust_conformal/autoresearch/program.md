# Ratchet program — spike C10 (CR-ACI)

**Goal:** make the certified interval narrower without giving up coverage, clean or attacked.

**Metric (frozen, `eval.py`):** `SCORE` = mean CR-ACI width (k = 3, α = 0.1) on clean validation data (2015-01-02 → 2015-06-30), plus a penalty of 50 × shortfall if clean or pump-attacked coverage < 0.895. Lower is better. Train 2014-01 → 2014-09, calibration 2014-10 → 2014-12. The reported test period (2015-07 → 2016-03) is never touched by the loop; the lead re-checks kept changes there with `eval/run_baselines.py`.

**Allowed edits:** `config.json` (text feature subset, LightGBM params, ACI γ) and implementation inside `components/fusion`, `components/aggregator`, `components/robust_conformal` — contract tests must still pass and every text feature must keep an exact deletion-range rule. Never edit `eval.py`, `eval/metrics.py` or the splits.

**Keep rule:** keep a change only if the mean SCORE over 3 seeds improves by > 1% and both coverages stay ≥ 0.895; log every attempt in `results.tsv` (kept or not). (Tightened 4 Oct 08:27 after h1's −0.6% single-seed validation gain did not transfer to the test period.)

**Idea backlog (ordered):**
1. Drop the loosest-boxed feature (`sent_std`).
2. Robust-only text features (`log_n_docs`, `sent_trim`).
3. ACI step size γ ∈ {0.005, 0.02}.
4. LightGBM monotone constraints on sentiment features (fewer reachable leaves → tighter bounds).
5. Fewer trees / larger `min_child_samples` on text splits.
6. Two-tier budget: k for metadata-mimicking attackers, larger k only for low-trust accounts.
7. Attention z-score (abnormal tweet volume) as a volatility feature — needs a history-robust deletion rule.
8. FinBERT scorer once weights are on disk (re-run `eval/prepare.py`).
