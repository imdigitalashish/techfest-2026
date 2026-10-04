# Independent antithesis review of ADR 001 (rubber-duck agent, 4 Oct 2026 ~09:30 IST)

_Saved by the lead. This is the independent adversarial review that ADR 001 said was pending; the lead's response and fix status follow the review._

## Review (condensed faithfully; file:line refs are to the code at commit 06e2d81)
**1. Guarantee as implemented.** The fixed-feature, fixed-q tree certificate is mostly sound for the five current features (empty set handled; min/max across crossing quantile models handled). The end-to-end CR-ACI guarantee is not:
- **Blocking — trust is not deletion-stable.** Trust used the copy-paste cluster size, computed over the whole ticker-day (`trust_scorer/heuristic.py`). Injected copies can lower an existing clean document's trust. Deleting the injected rows does not restore it, so in a real deployment the clean features need not lie in the box. The evaluation bypassed this by appending hand-set trust values without re-running the scorer.
- **Blocking — the ACI loop did not match ACI's theorem.** α_t was clipped to [0, 1]. At α_t ≤ 0 the infinite quantile was replaced by 3 × max score, and lower/upper endpoints were reordered (turning empty intervals into non-empty ones). Negative q_t plus reordering could break containment.
- Same-q_t containment is pathwise for q_t ≥ 0, but it does not contain the counterfactual clean-history ACI interval.
- EPS = 1e-6 is empirical. Missing-value routing in the trees is ignored (fine for finite inputs; reject non-finite inputs explicitly).
- Split-CQR's nominal coverage still assumes clean, exchangeable calibration and test data.

**2. Overclaims.**
- "So coverage holds per prediction, not just on average" is false. Only *clean interval covers ⇒ certified interval covers* is per-instance.
- "88.0% at 4.5% extra width" uses the clean width. Under the pump attack the certified width is 5.088 vs CQR 4.594.
- "+0.3% width" for CR-ACI holds only on clean data; under the pump it is +0.9%.
- ACI is our own loop, not MAPIE.

**3. Evaluation flaws.**
- The 12-variant oracle is not a worst case for non-monotone trees.
- Attacking every day lets ACI adapt; sparse, burst and targeted attacks are untested.
- Pooled Kupiec/Christoffersen tests ignore same-day correlation; use date-cluster bootstrap or day-level tests.
- H1-2015 serves both as ratchet validation and as main calibration, and kept changes were re-checked on the test period, which contaminates both.
- Single seed; fixed 87-stock universe; VADER.
- State that forecasts are made after the 16:00 close (same-day features are then causal). Audit Yahoo adjusted-close back-adjustment.

**4. Strongest "not worth it" case.** Dropping text gives attack immunity for free and scores no worse:
- price-only pinball 0.3513 vs fusion 0.3518;
- IC 0.0119 vs 0.0059;
- ACI coverage 89.5% vs 89.4%.

The pump moves the forecast 0.04 pp while certification adds ~0.21 pp of width. Refuting this needs out-of-time evidence that text improves proper scores or utility, that realistic attacks cause harm, and that certification beats drop-text, robust aggregation and adversarial training.

**5. Ranked fixes.**
1. Context-free trust, or certify its recomputation.
2. Correct ACI boundary semantics, tested against the theorem.
3. Precise containment wording.
4. Untouched calibration/test sets, seeds, date-cluster inference.
5. Raw-document, mixed and sparse attacks, and a text-utility vs drop-text comparison.

## Lead response (synthesis) and status
| # | Finding | Accepted? | Status |
|---|---|---|---|
| 1 | Trust not deletion-stable | Yes | **Fixed in code:** `trust_of()` uses only the document's own metadata; `dup_cluster` kept as a detection signal, excluded from certified features. Rerun pending (baseline_v1). |
| 2 | ACI semantics | Yes | **Fixed in code:** no clipping; α_t ≤ 0 → whole line, α_t ≥ 1 → empty; no reordering; boundary diagnostics recorded. Evaluator v1 treats lo > hi as empty and reports infinite widths separately. Test against the long-run bound still to write. |
| 3 | Overclaims | Yes | **Fixed in the abstract** (containment wording; pump widths; ACI is ours). |
| 4 | Contaminated splits / inference | Yes | To do: move the ratchet to 2014-only splits; count test looks (so far 2: baseline + one h1 re-check); date-cluster bootstrap; 3 seeds. The finals' untouched holdout will be FNSPID news after 2016. |
| 5 | Drop-text argument | Partly | The strongest critique. MiniLM+LR scorer (macro-F1 0.691 vs VADER 0.489 on labelled financial tweets) is the first step. Next: text→volatility features, plus utility tests vs drop-text. If text still adds nothing out of time, the pitch becomes "certify how much an untrusted channel can hurt you", with drop-text as a legitimate k = ∞ endpoint. |
