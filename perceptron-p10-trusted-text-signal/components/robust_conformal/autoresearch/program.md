# Ratchet program — spike C10 (CR-ACI)

**Goal:** make the certified interval narrower without giving up coverage, clean or attacked.

**Metric (frozen, `eval.py` v2 from 4 Oct 13:00):** `SCORE` = mean CR-ACI width (k = 3, α = 0.1) on clean validation data, plus a penalty of 50 × shortfall if clean or pump-attacked coverage < 0.895. Lower is better. v2 splits are all inside 2014 — train Jan–Jun, calibration Jul–Sep, validation Oct–Dec — so the loop never touches the main calibration (H1-2015) or test (Jul 2015 → Mar 2016) periods (fix after the rubber-duck review: v1 validated on H1-2015, the main calibration set). Kept changes are re-checked on the test period at most once per batch, and every look is counted in `results.tsv`.

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
