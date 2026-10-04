# ADR 002 — Reframe the spike: transfer-robust ordinal model first, evidence audit as a sidecar

- **Status:** accepted, 2026-10-04 09:30 IST. Amends [ADR 001](001-spike.md); evidence in the [review](001-review.md) and [eval/README.md](../../eval/README.md).
- **Deciders:** project lead, after an independent adversarial review (thesis/antithesis) and the genre-shift study (first measured evidence).

## What changed since ADR 001
1. **Antithesis (independent reviewer):** Round 1 is 100% hidden-set ordinal accuracy. ADR 001 picked its spike partly on novelty and demoability, and the "evidence-first" mechanism did not feed the model at all.
2. **Measurement (genre-shift study v0):** shift dominates. A text model trained on one TechPort writing source loses 60–75% of its QWK on the other (e.g. 0.345 → 0.126). Abstract-length inputs lose about 40%. The same 98 projects scored from their papers instead of their descriptions drop from QWK 0.414 to 0.212 (MAE +0.196, 95% CI [0.069, 0.319]).
3. **Leakage audit:** about 14% of TechPort texts state a TRL explicitly; SBIR briefing charts print "Estimated TRL at beginning and end of contract"; the title-only grouping misses content duplicates.

## Decision
- **Spike 1 (Round 1, primary) — transfer-robust ordinal TRL model (C4)**, chosen by a **model tournament** on an eval suite whose primary score is the *shifted* condition, not in-distribution TechPort:
  - **Eval suite v1 (arbiter):** leakage-clean TechPort (explicit-TRL and SBIR/phase statements redacted, content-deduplicated, snapshot-hashed), cross-source splits (SBIR ↔ NASA-internal), abstract-length inputs, paired papers (OpenAlex), TechPort briefing-chart PDFs (redacted), then NTRS/OSTI reports with proxy labels and the 10 Oct dev samples. Report each condition with bootstrap CIs. Score = the mean over shifted conditions of the official metric (QWK/MAE until 10 Oct).
  - **Tournament entrants:** (a) word + char TF-IDF linear/ordinal models (strong cheap floor); (b) small open-weight sentence encoder + ordinal head (CORN/CORAL/cumulative logit); (c) training-time augmentation for shift: length cropping (abstract-length views), redaction, pooled sources; (d) an offline open-weight LLM rater or teacher (rubric prompting; distilled into a small student if too slow); (e) ensembles. Every entrant must pass the C8 budget (CPU time, RSS, licence, offline).
- **Spike 2 — metric-aware decoding and calibration (C5):** nested out-of-fold threshold tuning for the official metric; calibration verified under shift.
- **Explicit-TRL statement detector (new, part of C3):** documents that state their TRL ("currently at TRL 4", "TRL 3 → 6") carry the strongest possible signal, but the role matters (current vs begin vs target). This is a high-precision feature for the hidden set and must be redacted in training text so the model also learns from the rest.
- **Round-2 sidecar — evidence-led audit (C3 + C6):** quoted, page-anchored evidence and rubric criteria marked supported / contradicted / not evidenced, with the model's P(TRL ≥ level) alongside. This is *model-consistent reporting*, **not** a faithfulness claim. Evidence features enter C4 only if they win on the eval suite.

## Consequences
- The next build is eval suite v1 (a redacted, deduplicated benchmark plus shift conditions), then the tournament; the auto-research ratchet optimises the shifted score.
- Submission plan (approach §5): #1 = strongest compliant tournament winner, early; #2 = exactly one orthogonal hypothesis (e.g. a shift-robust student vs a direct model); #3 = the diagnostic winner with pass/fail fixes only.
- The audit sidecar keeps the finals story honest and cheap: no claim beyond what the code does.
