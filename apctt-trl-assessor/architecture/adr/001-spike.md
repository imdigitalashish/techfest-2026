# ADR 001 — Spike choice: evidence-first ordinal assessor

- **Status:** accepted (v0, 2026-10-04 07:40 IST); revisit on 10 Oct when the official guide, criteria checklist and samples arrive.
- **Deciders:** project lead. In lean mode, with sub-agents disabled, the lead ran the six-hats and adversarial passes. An **independent** rubber-duck review is still pending and is the first task once agents are re-enabled.

## Context
Round 1 is scored 100% on hidden-set **ordinal accuracy & precision**, plus pass/fail on schema, speed and dependencies. Round 2 (finals) judges an end-to-end system on live documents in front of an expert panel, and the challenge question explicitly asks for **supporting evidence** and an **auditable, actionable gap analysis**. The frozen Round-1 model must also serve Round 2 (no retraining after 15 Nov). Labelled public text is scarce and genre-shifted (TechPort project descriptions vs. patents/papers/reports). The official label distribution and metric are unknown until 10 Oct.

## Candidates (scored 1–5: impact on judged criteria · novelty · feasibility by 15 Nov · measurability · demoability)

| Candidate | Impact | Novelty | Feasible | Measurable | Demo | Total |
|---|---|---|---|---|---|---|
| A. **Evidence-first ordinal assessor** — C3 extracts achieved/planned/negated demonstration evidence (type × environment × scale); C4 predicts the 8 cumulative decisions P(TRL>k) using text + evidence features; C6 reads the same cumulative decisions as rubric criteria, so the gap analysis is the model's own decision boundary, not a post-hoc story | 5 | 4 | 4 | 5 | 5 | **23** |
| B. **Metric-aware calibration and decoding** (C5) — calibrate the cumulative distribution; decode by mode/median/tuned thresholds for whichever official metric lands on 10 Oct | 4 | 2 | 5 | 5 | 2 | 18 |
| C. Fine-tune an open-weight LLM (LoRA) to output the TRL directly | 4 | 2 | 3 | 5 | 3 | 17 |
| D. Teacher-LLM labelling of unlabelled patents/papers + distillation into a small offline student | 4 | 3 | 3 | 4 | 2 | 16 |
| E. Bibliometric TRL (counts of papers/patents over time) | 1 | 1 | 3 | 3 | 2 | 10 |

## Six thinking hats (on A)
- **White (facts):** TechPort gives 8,587 text+TRL records from a 54% random sample (`data/techport/`). Ordinal decompositions (Frank & Hall 2001; CORAL arXiv:1901.07884; CORN arXiv:2111.08851) yield P(TRL>k) natively. Every rubric we opened (EU Annex G, NASA) defines levels by *what was demonstrated, where*. In the sources we opened, neither the published work (frameworks, bibliometrics) nor the vendors document a single-document TRL predictor with cited evidence (see `research/landscape.md`).
- **Red (gut / judges):** an expert panel trusts a level they can *check* — quoted sentences plus "criterion met / missing" — far more than a bare number. That is the finals demo.
- **Black (risks):** (1) the evidence extractor may add noise and *lower* accuracy compared with plain text features; (2) "planned vs achieved" is hard (proposals describe planned work), and TechPort's text is proposal-style; (3) hand-written cue lexicons look like "hard-coding" — they must be rubric-derived and data-validated, never keyed to test files; (4) genre shift to patents/papers.
- **Yellow (benefits):** one mechanism serves Round 1 (accuracy) and Round 2 (audit + gap analysis); evidence features are genre-robust in principle (the "validated in a relevant environment" kind of claim reads the same in a patent, a paper or a report); the extractor and the predictor are separate seams, so each can be auto-researched alone.
- **Green (alternatives):** use an LLM only as a *sentence-level* evidence tagger (small, fast, offline) rather than a whole-document rater; conformal prediction sets over TRL for "uncertain between 4 and 5"; genre-adversarial augmentation (rewrite TechPort descriptions as patent claims or paper abstracts, labelled synthetic).
- **Blue (process):** build B now (cheap and needed whatever happens); build A's evidence features as an *additive* feature block, so the ratchet keeps them only if held-out QWK improves; re-decide after the 10 Oct samples.

## Thesis → antithesis → synthesis
- **Thesis:** A wins both rounds: the cumulative "is it beyond level k?" structure *is* the rubric, so accuracy and auditability come from the same model.
- **Antithesis** (lead, playing adversary): on proposal-style text an n-gram model already captures most of the signal; evidence extraction is a pipeline of brittle heuristics that will lose to a fine-tuned LLM on accuracy, while explanations from a separate extractor may not match what the classifier actually used ("faithfulness gap"). Organisers may score only the TRL number in Round 1, so effort on gap analysis is wasted there.
- **Synthesis:** (1) keep the strong text model as the backbone and add evidence features only where the frozen held-out eval shows a gain (ratchet); (2) make the gap analysis *faithful by construction* — it reads the model's own P(TRL>k) per threshold plus the evidence that fired, rather than a separate generator's text; (3) treat C5 (B) as the always-on second spike because the metric is unknown; (4) keep C (LLM fine-tune) as a challenger behind the C4 seam — if it wins on held-out QWK within the latency budget, it replaces the backbone without changing the contracts.

## First-principles check
The real bottleneck is not model capacity; it is **label/genre mismatch**. We train on one genre with one labelling process and are scored on unknown genres labelled by APCTT experts. What generalises across genres is the *claim of demonstration* (type × environment × scale × achieved), which is exactly what A extracts. And the decision rule must match the unknown metric, which is B.

## Decision
**Spike 1 = A (C3 evidence extractor + C6 rubric/gap engine, coupled through C4's cumulative thresholds). Spike 2 = B (C5 calibration and metric-aware decoding).** C1, C2, C7 and C8 use best existing practice. LLM fine-tuning (C) and teacher distillation (D) stay challengers behind the C4 seam.

## Consequences
- The frozen held-out eval (`eval/`) is the arbiter: every evidence feature must earn its place on QWK/MAE.
- The rubric must be a **data file** (EU Annex G + NASA wording, versioned), so the 10 Oct assessment-criteria checklist can be swapped in within hours.
- Next: annotate ~200 sentences for C3's isolated metric; write `components/ordinal/autoresearch/{program.md, eval.py, results.tsv}`.
