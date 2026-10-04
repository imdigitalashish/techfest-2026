# P10 code, reproducibility and evaluation review — GPT-6 Sol

2026-10-04. Reproduced and reviewed the P10 pipeline and frozen DJIA experiment at `5744e5b`. While finishing, `main` advanced to `fd89ca5`: its new `--seed` flag defaults to the same seed 0, and it fixed the DJIA drift-check omission found in the initial review. Remaining findings below were checked against the rebased tree. Findings are advisory. Paths are relative to `perceptron-p10-trusted-text-signal/`.

## Reproduction table (number · committed · reproduced · match?)

All percentages below are formatted to four decimal places; "exact" means the underlying JSON number, not just its display rounding, matched. VADER rows are the corresponding checks on `baseline_v1.json`; MiniLM rows are from `text_minilm_v1.json`.

| Number / JSON path | Committed | Reproduced | Match? |
|---|---:|---:|---|
| MiniLM `ablation.fusion.split.coverage` | 81.6335% | 81.6335% | Exact |
| MiniLM `ablation.fusion.cqr_mapie.coverage` | 86.6265% | 86.6265% | Exact |
| MiniLM `ablation.fusion.cqr_aci.coverage` | 89.4971% | 89.4971% | Exact |
| MiniLM `attack.oracle.vanilla_cqr_oracle_coverage` | 84.6926% | 84.6926% | Exact |
| MiniLM `attack.oracle.certified_guaranteed_floor` | 86.6569% | 86.6569% | Exact |
| MiniLM `spike.cr_aci.cr_aci_clean.coverage` | 89.5457% | 89.5457% | Exact |
| MiniLM `spike.cr_aci.cr_aci_pump.coverage` | 89.7282% | 89.7282% | Exact |
| VADER `ablation.fusion.split.coverage` | 81.6092% | 81.6092% | Exact |
| VADER `ablation.fusion.cqr_mapie.coverage` | 86.6691% | 86.6691% | Exact |
| VADER `ablation.fusion.cqr_aci.coverage` | 89.4302% | 89.4302% | Exact |
| VADER `attack.oracle.vanilla_cqr_oracle_coverage` | 84.1087% | 84.1087% | Exact |
| VADER `attack.oracle.certified_guaranteed_floor` | 86.5292% | 86.5292% | Exact |
| VADER `spike.cr_aci.cr_aci_clean.coverage` | 89.4788% | 89.4788% | Exact |
| VADER `spike.cr_aci.cr_aci_pump.coverage` | 89.6187% | 89.6187% | Exact |
| DJIA `primary.mean_winkler_improvement` | +0.0034307136674228793 | +0.0034307136674228793 | Exact |
| DJIA `primary.p_one_sided` | 0.4629 | 0.4629 | Exact |
| DJIA `primary.decision` | no evidence that text adds value | no evidence that text adds value | Exact |

Deep comparison of **every numeric leaf**, plus nonnumeric values and JSON structure: VADER **1,122/1,123** exact, MiniLM **1,120/1,121** exact, DJIA **48/48** exact. The *only* differences in those three files are elapsed time: `baseline_v1.json:meta.runtime_s` committed **67.4**, reproduced **63.1**; `text_minilm_v1.json:meta.runtime_s` committed **59.2**, reproduced **87.6**. No metric differs, even within a `1e-9` near-equality tolerance. Auxiliary preparation stats are **6/8** numeric leaves exact for each scorer: `prepare_stats_v1.json:scorer_seconds` **6.5 / 4.1** and `:total_seconds` **42.2 / 26.6** (committed / reproduced); `prepare_stats_minilm_v1.json:scorer_seconds` **0.9 / 1.4** and `:total_seconds` **13.0 / 21.8**. These four differences are also elapsed time, not data or model outputs.

The read-only data link and **copied**, not linked, MiniLM cache were used in this worktree. The 243 MB cache's SHA-256 matches the source byte for byte (`fb783704f7eaae009c11f83ededf764932c64f794828fe1a65805b0ebb2ae9ac`). Fresh CPU encoding of 100 randomly sampled, previously cached financial-news texts matched cached vectors (maximum absolute coordinate error **1.94e-7**, mean **3.52e-8**, all within `atol=rtol=1e-5`). All heavy runs used `nice -n 10`, CPU and offline model mode, and started only when `kern.memorystatus_level >= 30`.

## Test/drift results

- `python -m pytest -q tests`: **59 passed**; 30 existing pandas-4 deprecation warnings on positional `sum(1)` in `architecture/contracts/contracts.py:93`.
- `python deliverables/check_drift.py`: **OK — no drift**; abstract body **813 words**. Regenerating `eval/results/text_utility_djia_v1.md` also produces the committed bytes. Upstream commit `3fcc7e1` added that DJIA report to the drift check during this review; the check and all 59 tests passed again after rebase.
- The registered `eval/text_utility_djia.py` blob at `dd8bcd1` and at reviewed `HEAD` is identical (`258e71c777c8b998f4bafccb00847c086c1407f5`). Subsequent preregistration-text changes only corrected the registration timestamp and documented that correction.
- Focused adversarial checks reproduced the ACI trajectory counterexample (B1), a valid three-document injection outside the deletion box (B2), and a mis-scored empty interval (N1). No tracked result/report changed during reproduction.

## Findings ranked

### BLOCKING

**B1 — The advertised per-attack CR-ACI containment does not follow from the implementation.** `components/conformal/methods.py:68-94`, `eval/run_baselines.py:205-221`, `deliverables/round1-abstract.md:21`. Tree bounds contain clean *raw* predictions; adding the **same** correction preserves containment. Clean and attacked CR-ACI runs instead update separate `alpha_t` values and score pools from their own past outcomes, so their corrections need not match. A direct two-day call to `aci_from_bounds` with calibration scores `0.01,...,1.00`, `alpha=0.1`, `gamma=0.01`, first-day clean bounds `[0,0]`, attacked bounds `[-2,2]`, and outcomes `[1.05,0.92]` gives day-two **clean** `[-0.93,0.93]` (covers 0.92) but **attacked** `[-0.91,0.91]` (misses 0.92), although day-two raw bounds coincide. The abstract's "an attacker cannot add misses" is therefore false for separately adapted ACI trajectories. The reported **86.7% fixed-offset CQR floor** is a different, valid *conditional* claim if the box is sound. **Minimal fix:** restrict the per-row claim in the abstract to fixed-offset certified CQR and state only ACI's long-run, day-average feedback property for CR-ACI; if a per-row CR-ACI floor is essential, use/prove an attack-invariant conservative correction and regression-test distinct attack histories.

**B2 — The fixed `EPS` can exclude a clean feature vector from a valid deletion box.** `components/robust_conformal/certify.py:22,65-77`. Prefix-sum cancellation in `E[s²] - E[s]²` can exceed the fixed `1e-6` outward margin after taking a square root. With **49,997 clean posts plus three identical injected posts**, all with `s=0.9204812125498814` (a value emitted by the deployed MiniLM scorer) and `trust=0.05`, `deletion_box(D',3)` says `sent_std >= 1.590862272061134e-7`, while `features_from_docs(D).sent_std = 2.220446049250313e-16`: `features(D)` is **outside** the certified box. This disproves an unrestricted "every injection within budget" certificate even though the largest observed StockNet ticker-day has only **555** documents and the reproduced headline outputs match. **Minimal fix:** calculate variance with stable centered/compensated arithmetic and a justified outward error bound (or enforce and document a proven safe cardinality cap); add a constant-sentiment high-count injection regression test.

**B3 — The DJIA experiment's "tradeable at the open" timing claim is incompatible with its price-only features and target.** `eval/preregistration/2026-10-04-text-utility-djia.md:17-20`, `eval/text_utility_djia.py:57-60`, `eval/report_djia.py:34-38`. `gap` and `abs_gap` require **the next session's official Open**, while `y` includes the entire return from *that same Open* to the close. Before the opening print, `gap` is future information; after that print, the stated open-to-close starting price has already passed and need not be executable. The registered `p=0.4629` is reproducible and answers a comparison **conditional on seeing the open**; it does not establish the same null for a pre-open, tradeable text signal. Sharing the gap between arms does not make the pre-open question unaffected: overnight news could already be absorbed by that feature. **Minimal fix:** preserve the frozen registration/result, qualify the claim as conditional and not an executable-at-open test, and label a no-next-open-feature or executable post-open-price comparison as exploratory rather than silently replacing the registered analysis.

### NON-BLOCKING

**N1 — Empty intervals receive artificially good Winkler scores.** `eval/metrics.py:64-76`. `evaluate` correctly calls `lo > hi` an always-missed empty interval, but `hi_w = max(hi,lo)` scores it as a point interval. For `lo=1, hi=0, y=1`, the function reports **coverage 0, width 0, Winkler 0**. No committed ACI run had empty rows, so the headline scores are unaffected. **Minimal fix:** report empty-set frequency and mark its interval score undefined or impose an explicit infinite penalty; never score an empty interval as a zero-width interval containing its endpoint.

**N2 — The selectable FinBERT attack uses VADER sentiment.** `eval/run_baselines.py:57-63,233-238`. `--scorer finbert` prepares FinBERT documents but `template_sentiment("finbert")` takes the VADER fallback, so the "pump uses the deployed scorer" statement and FinBERT pump result would be wrong. Current VADER/MiniLM runs are unaffected. **Minimal fix:** score the template with `FinBertScorer` for that option, or reject unsupported attack scoring explicitly, and test the dispatch.

## Verdict

**Reproducibility: pass. Unqualified certificate and tradeability claims: not yet ready (3 BLOCKING, 2 NON-BLOCKING).** The required eight explicitly specified headline numbers (seven MiniLM coverages and DJIA p-value), all seven analogous VADER coverages, and every non-timing result in the three headline JSONs reproduced exactly. The 16:00 ET assignment, backward-looking StockNet rolling features, chronological label availability, finite-sample CQR quantile, quantile-crossing handling, MAPIE symmetric cross-check (maximum difference 0), daily ACI feedback, paired centered circular-block p-value, and day-block coverage CI showed no additional discrepancy on inspection. The fixed-CQR empirical floor is not the separately adapted CR-ACI guarantee, and the registered DJIA null is conditional on an opening price that the trading-at-open claim cannot use as described.
