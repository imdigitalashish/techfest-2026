# Autoresearch program — C4 ordinal TRL model (spike 1, ADR 002)

**Goal.** Maximise `shifted_mean_qwk`: the mean quadratic weighted kappa over four *shifted* conditions of eval suite v1 (SBIR→internal, internal→SBIR, abstract-length crop, DOI-linked papers). Rationale: the hidden APCTT set is patents/papers/reports, and our genre-shift study showed shift costs 50–75% of QWK. In-distribution accuracy is a guard-rail, not the target.

**Loop (karpathy/autoresearch-style).** Edit `components/ordinal/model.py` only → `python components/ordinal/autoresearch/eval.py --hypothesis "<one line>"` → the evaluator prints the scalar and a verdict (KEEP/discard) and appends a row to `results.tsv` → commit model.py if KEEP, otherwise `git checkout components/ordinal/model.py`. Never edit `eval.py`, the suite builder or the split.

**Keep rule (frozen in eval.py).** Paired bootstrap of Δ vs the current best (1,000 resamples per condition, item-level): keep iff mean Δ ≥ +0.005, P(Δ>0) ≥ 0.90, and in-dist QWK drops by < 0.02.

**Constraints.** Inference must stay CPU-only, offline, ≤50 ms/doc on the M5, with a permissive licence for everything it needs (Stage 2 is Apache-2.0). No metadata features (text only). No downloads >200 MB while lean mode is on. Heavy runs one at a time under `nice -n 10`.

**Anti-gaming.** Item-level bootstrap only covers test-sample noise, not overfitting to the 4 conditions through many iterations. The lead re-checks kept models on fresh holdouts (TechPort briefing-chart PDFs, NTRS/OSTI reports, then the 10 Oct dev samples) and reports both.

**Idea backlog (ordered).**
1. sklearn word 1–2-gram TF-IDF + ridge (in-dist v0 best QWK).
2. + char_wb 3–5-gram TF-IDF (robust to vocabulary shift).
3. + length-crop augmentation (train on random 40–150-word windows as well as full text) — targets crop60/papers.
4. Ordinal heads on the best features: cumulative logit (Frank & Hall), threshold-ridge, CORN-style conditional binaries; median decoding.
5. Cut-point tuning on out-of-fold regression scores for QWK (C5 territory; inside fit via CV).
6. Domain-general vocabulary: drop NASA-specific tokens (min_df across sources; keep features frequent in both SBIR and internal).
7. Small open-weight sentence encoder (licence-checked, <200 MB) + ordinal head; ensemble with TF-IDF.
8. Evidence features from C3 (signal × polarity counts) — only if they win here.
