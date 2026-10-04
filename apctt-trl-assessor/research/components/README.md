# Per-component research notes — v0

_2026-10-04 08:00 IST, project lead, lean mode (no per-component research agents yet; each section below seeds that agent's brief once agents are re-enabled). Facts cite sources opened in [`../landscape.md`](../landscape.md). Everything under "Innovation candidates" is a **hypothesis to test**, not a finding._

## C1 Ingest & parse
- **Baseline:** text-layer PDF extraction plus heading heuristics; plain-text/HTML/XML strip.
- **Constraint:** the Stage 2 package must be Apache-2.0, so parser licences matter. Licence facts per library are **UNVERIFIED** until the C8 audit runs; check copyleft parsers before adopting them.
- **Innovation candidates:** section-aware parsing (claims / abstract / experiments / results / conclusions), because maturity evidence concentrates in results and conclusions; OCR fallback only when there is no text layer (speed).
- **Isolated metric:** character-F1 vs gold text on ~30 mixed docs; pages/s.

## C2 Doc-type router
- **Baseline:** rules (a claims block means a patent; abstract plus references means a paper; else report/proposal).
- **Innovation candidates:** genre-conditioned priors and calibration (a granted patent and a lab paper have different TRL base rates — to be measured on the 10 Oct samples, not assumed).
- **Isolated metric:** macro-F1 on a labelled genre set.

## C3 Evidence extractor ★ (spike 1)
- **Grounding (opened):** EU H2020 Annex G and the NASA TRL page define levels by demonstration type and environment ("validated in lab", "validated/demonstrated in relevant environment", "operational environment", "qualified", "proven").
- **Baseline v0:** a cue lexicon derived *from rubric wording only* (never from test documents), with tense/modality rules for achieved vs planned vs negated.
- **Innovation candidates:** (1) a sentence-level tagger with signal × environment × scale × polarity, trained on weak labels from TechPort (sentences from high-TRL vs low-TRL projects) and refined on ~200 hand-annotated sentences; (2) an open-weight small LLM as an offline sentence tagger, used only if it fits the latency budget; (3) polarity — TechPort text is proposal-style ("we will demonstrate…"), so separating *planned* from *achieved* is the crux.
- **Isolated metric:** span-level micro-F1 (signal × polarity) on annotated sentences; achieved-vs-planned accuracy.

## C4 Ordinal TRL model (seam for spike 1)
- **Grounding (opened):** CORAL (arXiv:1901.07884) and CORN (arXiv:2111.08851) — rank-consistent ordinal heads; Frank & Hall (2001) cumulative decomposition (link UNVERIFIED; implemented).
- **Measured (eval/README.md):** hashed TF-IDF ridge QWK 0.314 / MAE 1.053 on TechPort `trl_current` (vs majority QWK 0.000 / MAE 1.112).
- **Innovation candidates:** (1) the full sklearn TF-IDF + cumulative logit (pending run); (2) add C3 evidence counts per threshold as features and keep them only if held-out QWK rises (ratchet); (3) a small sentence-embedding encoder + CORN head; (4) an open-weight LLM challenger behind the same seam (LoRA) — only if it beats the backbone within the CPU budget.
- **Isolated metric:** QWK on the frozen TechPort v0 split (MAE, exact and within-1 secondary).

## C5 Calibrate & decode ★ (spike 2)
- **Measured:** on the same predictions, mode decoding gives the best exact accuracy, expectation the best MAE and within-1, rounded regression the best QWK (eval/README.md) — decoding is a free lever.
- **Innovation candidates:** (1) choose the decoding rule per the official metric (10 Oct); (2) tune ordinal thresholds directly for QWK on cross-validated out-of-fold predictions; (3) temperature or isotonic calibration of P(TRL>k); (4) prediction sets ("TRL 4–5") with coverage guarantees for the audit report; (5) an abstain flag for low-confidence documents in Round 2.
- **Isolated metric:** ranked probability score and ECE on held-out data; official metric after decoding.

## C6 Rubric engine & gap analysis ★ (spike 1)
- **Grounding (opened):** Thales (PESARO 2026) assesses AI-system TRL with structured checklists; EU Annex G gives a domain-neutral level ladder.
- **Innovation candidates:** (1) *faithful by construction*: each threshold k's probability P(TRL>k) plus the evidence that fired becomes the "criterion met / not met" line, so the gap list is the model's own boundary; (2) the rubric as a versioned data file (EU+NASA v0, swapped for APCTT's checklist on 10 Oct); (3) suggested next actions per missing criterion, templated from the rubric's next-level text (no free-form generation needed for Round 1).
- **Isolated metric:** criterion-level Cohen κ vs an expert checklist; citation precision.

## C7 Assemble & validate
- **Baseline:** JSON Schema validation against the official schema file; fail-closed defaults.
- **Innovation candidates:** property-based fuzzing (empty, huge, non-English, scanned PDF) to guarantee 100% schema-valid output.
- **Isolated metric:** % schema-valid on 1,000 fuzzed inputs.

## C8 Runner & packaging
- **Innovation candidates:** single-process CPU path with lazy imports (tonight showed that import time can dominate on a loaded machine — 89 s for sklearn under I/O starvation); a numpy-only inference path (already exists: `eval/baseline_numpy.py`); a network-off guard; a clean-room dry run before each submission.
- **Isolated metric:** docs/s, peak RSS, cold-start s on a 100-doc batch; licence-audit pass.

## C10 Data & weak labels
- **Measured:** TechPort label consistency can be checked (trlBegin ≤ trlCurrent ≤ trlEnd), giving a cheap label-noise estimate — not yet computed.
- **Candidates (UNVERIFIED sources, not opened tonight):** CORDIS topic TRL ranges; SBIR phases; patents/papers for a genre-shift set.
