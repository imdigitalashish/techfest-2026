# Approach — AI for Technology Readiness (2nd APCTT Hackathon 2026)

_Draft v0, 2026-10-04 (project lead). Round 1 = frozen model, hidden evaluation set, max 3 submissions, deadline 15 Nov 23:59 IST. The official training guide, criteria checklist and samples arrive 10 Oct; everything below is built to be re-pointed at them within hours._

## 1. What we must be able to show
| Judged item (official statement) | Evidence we will produce |
|---|---|
| "Model Ordinal Accuracy & Precision on Hidden Evaluation Set (Primary Score)" | Held-out ordinal metrics — exact accuracy, within-1 accuracy, MAE, quadratic weighted kappa (QWK), macro precision — on a frozen public split and on the 10 Oct dev samples; decoding tuned to the official metric once it is published. |
| "Strict pass/fail compliance on output schema, execution speed, and dependency checks" | Every record validated against the official schema loaded **from file**; 100% validity on fuzzed inputs; measured docs/s and peak RAM on CPU; pinned, minimal, permissively licensed dependencies; offline run. |
| Round 2: integrate the frozen model, process live files, usability, pitch | The same frozen model plus an audit report: level, confidence (calibrated once C5 is fitted), quoted page-anchored evidence per rubric criterion (supported / contradicted / not evidenced), and the gap list for the next level. |

## 2. Pipeline (details: [architecture/components.md](../architecture/components.md), [ADR 001](../architecture/adr/001-spike.md))
`raw file → C1 parse → C2 genre router → C3 evidence extractor ★ → C4 ordinal model (P(TRL>k), k=1..8) → C5 calibrate & decode ★ → C6 rubric engine & gap analysis ★ → C7 assemble + validate against official schema → JSON`.
- **Spike reframed after review ([ADR 002](../architecture/adr/002-reframe-spike.md)):** Round 1 is scored only on hidden-set accuracy, and our genre-shift study shows shift is the dominant risk. The primary spike is therefore a **transfer-robust ordinal model chosen by a tournament on a leakage-clean, shift-aware eval suite**. The evidence-led audit (C3+C6) is the Round-2 sidecar and enters the model only if it wins on that suite.
- **Why ordinal:** the model outputs 8 cumulative decisions "is the technology beyond level k?", which respects the order of TRL, lets us pick the decision rule for the official metric, and lets the audit report the model's P(TRL ≥ level) next to each rubric criterion (model-consistent reporting; not a faithfulness claim).
- **Why evidence matters:** every rubric we opened defines a level by *what was demonstrated, where, at what scale* (EU Horizon Annex G; NASA). Hypothesis to test: such claims transfer across patents, papers and reports better than raw n-grams do (patent claims express legal scope, so this may fail for patents).
- **Self-contained:** CPU, offline, open weights only. v0 is scikit-learn; any LLM challenger must be open-weight, run offline and fit the latency budget.

## 3. Public-data plan
| Source | Status | Use |
|---|---|---|
| NASA TechPort public API (no key) | **Verified tonight**: 21,046 projects indexed; 11,427 fetched (seeded random 54% sample); 8,587 with ≥200-char description + TRL. `data/techport/fetch_techport.py`, `build_dataset.py`. | Primary labelled set (labels `trl_begin`, `trl_current`, `trl_end`). **Text only** — program/SBIR metadata is never a feature (the hidden set is raw documents). |
| EU CORDIS (Horizon topic TRL ranges) | Planned, not yet opened | Weak labels; non-US genre. |
| SBIR.gov awards (phase) | Planned, not yet opened | Weak prior only. |
| Patents / papers (USPTO, Lens, arXiv, OpenAlex) | Planned | Genre-shift test set (hand-labelled with the rubric by ≥2 annotators) and unlabelled pool for weak supervision. |
| Official dev samples (10 Oct) | Pending | Calibration and decoding thresholds; never used in a way that memorises specific documents. |
All sources must fall under the organisers' "approved public data sources" — **check on 10 Oct and drop any that don't**. Fetch scripts are committed; data stays in gitignored `.data/`.

## 4. Evaluation plan and first numbers
- **Split:** grouped 80/20 by normalised title (so SBIR Phase I/II of the same technology never straddle train/test), seed 20261004, test ids frozen in `eval/splits/`.
- **Metrics:** exact, within-1, MAE, QWK, macro precision, macro-F1; runtime (fit s, ms/doc).
- **Reproduce:** `python data/techport/fetch_techport.py && python data/techport/build_dataset.py && python eval/baseline_tfidf.py --label trl_current --label trl_begin --label trl_end` (from `apctt-trl-assessor/`).
- **Results:** `eval/results/baseline_v0_<label>.json` and `eval/results/results.tsv`; the summary table lives in [`eval/README.md`](../eval/README.md). Only numbers from committed runs are quoted.
- **Next eval layers:** (1) per-component metrics (C3 span-F1 on ~200 annotated sentences; C5 RPS/ECE); (2) genre-shift set (patents/papers); (3) the 10 Oct dev samples as the closest proxy to the hidden set; (4) a final hold-out we never tune on.

## 5. Three-submission plan
| # | Target date | What | Purpose |
|---|---|---|---|
| 1 | as early as compliant (target ≤31 Oct; earlier if feedback latency is unknown) | The **strongest** fully compliant tournament winner (not a deliberately weak baseline), schema-exact, offline. | First hidden-set score plus run/fail diagnostics, early enough to react. |
| 2 | ~8 Nov | **Exactly one orthogonal hypothesis** vs #1, with identical parser, packaging, adapter and decoder — e.g. shift-robust student (augmented/distilled) vs direct TechPort model. | A clean A/B on the hidden set: one score, one cause. |
| 3 | by 14 Nov (24 h buffer before the 15 Nov 23:59 freeze) | The diagnostic winner **exactly**, plus pass/fail fixes only; nothing output-changing appears first in the immutable entry. | Final, immutable entry. **Nothing user-dependent in 19–25 Nov** (exams); the freeze precedes them. |
Rule for every submission: a clean-machine dry run (fresh venv, network off, timer on) and schema validation of all outputs before upload.

## 6. 10-Oct adaptation checklist (target: a first adapted dry run within ~6 hours of receipt; longer if schema, formats, metric or environment differ materially)
1. Read the training guide, criteria checklist and dataset guidelines; log every rule in the thought node.
2. Output schema → save the organisers' file as a resource; write an explicit adapter `Assessment → official record`; validate with the organisers' checker if provided, else a standards-complete validator (pinned, licence-checked). Add golden fixtures and exact record-count/order checks. The internal mini-validator fails closed and is not evidence of official compliance.
3. Metric → implement it exactly in `eval/`; switch C5's decoding rule to the metric-optimal one.
4. Approved data list → prune or extend `data/` sources; re-run the builders.
5. Criteria checklist → encode as the rubric data file used by C3 and C6 (replacing EU+NASA v0 wording); map each criterion to evidence signals.
6. Dev samples → genre mix, length and label distribution vs TechPort; calibrate priors and thresholds on them (cross-validated, no memorisation).
7. Runtime limits and environment (CPU/GPU, RAM, time, Python version) → set C8 budgets; re-measure.
8. Submission format (container? script? entry point?) → build a package skeleton and dry-run it offline.
9. Re-run the full eval; update the 3-submission plan dates.
10. Raise ambiguities (e.g. what "hardcoded output schemas" exactly forbids) in the official **Doubt** section (rule 9) — the user posts them.

## 7. Rules compliance
- **Self-contained:** runs offline; no external API calls at inference; open weights only; no private API keys anywhere (repo secret-scanned before each submission).
- **No hard-coding:** no answers keyed to documents; the official output schema is loaded from the organisers' file at run time, never inlined. We read rule 6 conservatively and will confirm its meaning via the Doubt section.
- **Freeze:** after submission #3 no retraining, fine-tuning or model replacement; Round 2 integrates the frozen artefact. Integration fixes only with written authorisation (rule 3).
- **Licensing:** Stage 2 package under Apache-2.0 (rule 5). We only take dependencies whose licences are compatible (avoid AGPL/GPL parsers); the dependency licence audit runs in C8. Licence facts for each candidate library are **UNVERIFIED** until that audit runs.
- **Originality and attribution:** all code ours; third-party methods cited (Frank & Hall 2001; CORAL; CORN); data sources credited.
- **Eligibility:** team of 1–3, all ≤35 on 17 Dec 2026; registration on techfest.org by 9 Oct (user action).

## 8. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Genre shift (TechPort descriptions → patents/papers/reports) | Evidence features that are genre-neutral; genre router; calibrate on the 10 Oct samples; patent/paper test set. |
| Label semantics (begin vs current vs end TRL; "planned" vs "achieved" work) | Report all three labels; polarity in C3; pick the label definition that matches the official guide. |
| Unknown metric | C5 keeps the full distribution; switch decoding in minutes. |
| Execution limits | CPU-first design; measured latency; per-doc timeouts; fail-closed schema-valid output. |
| Only 3 submissions | Submission #1 early as an environment probe; offline dry-run harness before each upload. |
| Exams 19–25 Nov | Freeze is 15 Nov; final submission planned for 14 Nov. |
