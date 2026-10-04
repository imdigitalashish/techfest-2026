# Auto-research program — credibility_engine (spike A)

**Goal:** rank Anganwadi centres by how much their growth-monitoring data can be trusted, from routine data alone.
**Primary metric (maximise):** `auroc_fabricating` printed by the FROZEN evaluator `components/credibility_engine/eval.py` (SYNTHETIC; seeds 11–13). It is the AUROC of (1 − credibility) for AWCs whose worker copies measurements forward vs all others.
**Guard metrics (must not regress):** `auroc_nongood` ≥ 0.99 · `gross_error_recall` ≥ 0.99 · `reject_rate` ≤ 0.06.
**Keep rule:** keep a change only if the primary improves by more than 2 × `auroc_fabricating_sd`/√3 (≈ noise across seeds) and no guard regresses. Otherwise revert.
**Anti-gaming:** every 5 kept changes the lead re-runs on fresh seeds (101–103) and on a simulator variant with a different fabrication pattern (e.g. real measurement every 2nd month, increments 0.1–0.4 kg). If the gain does not survive, revert to the last surviving commit.

## What may change
Only `components/credibility_engine/engine.py` (indices, weights, aggregation). Never `eval.py`, never the simulator, never the contracts. `pytest components/credibility_engine` must pass.

## Idea backlog (lead-curated, highest expected value first)
1. Variance of within-child monthly weight increments (copy-forward → narrow, all-positive increments).
2. Share of length increments in a narrow positive band (copy-forward 0.3–1.0 cm) vs real data with measurement-error dips.
3. Separate a *fabrication* signature from a *noise* signature (two scores; credibility = min). Today noisy AWCs outrank fabricating ones.
4. Rank-based (percentile) standardisation within district instead of median/MAD.
5. Lag-1 autocorrelation of WHZ residuals within child (copied data drifts smoothly).
6. Re-weight `p_nonneg_dweight` / `p_nonneg_dlength` up and digit-preference down.

## Ledger
`results.tsv`: timestamp · commit · hypothesis · metric · delta · kept? · notes.
