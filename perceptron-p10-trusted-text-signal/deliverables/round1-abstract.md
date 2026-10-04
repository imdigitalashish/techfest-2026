# Round 1 abstract — Perceptron 2026, Problem 10: Trusting a Signal Extracted from Messy, Manipulated Text

_Rendered from committed results by `deliverables/render.py` (template: `round1-abstract.template.md`); `deliverables/check_drift.py` fails if any number is stale. Results: `eval/results/`. Reviewed by gpt-6-astra and gpt-6-sol (`reviews/`)._

**Problem & theme.** Theme 6 (AI You Can Actually Trust), Problem 10. Desks and apps act on sentiment from news and social posts, and one hacked tweet once moved the Dow 140 points. We make the confidence bound, not the point forecast, the thing a user can trust when some of the text is fake.

**Understanding of the challenge.** Three difficulties interact.
1. **Text is a weak signal.** Our StockNet estimates are close, and a pre-registered test on unseen data found no incremental value (results below).
2. **Returns are not exchangeable.** Volatility clusters, so a split-conformal band that is valid on average under-covers exactly in stressed markets.
3. **Manipulation acts on the test input.** Injected posts move the features after calibration, which no standard conformal guarantee covers.

So "meaningful" must be measured: valid on held-out time and within regimes, misses not clustered, narrow, and robust to a stated attack budget.

**Proposed approach.** A ten-component pipeline with typed contracts:
1. *Ingest and align* posts to the 16:00 New York close. A timestamp-alignment check finds 0 of 119,641 tweets after the cut-off.
2. *Text scorer:* frozen MiniLM-L6 embeddings plus a sentiment head trained on labelled financial tweets (macro-F1 0.69 vs 0.49 for the VADER lexicon). The head receives no return labels; contamination of the pretrained encoder is not excluded.
3. *Trust* from each post's own account metadata.
4. *Bounded-influence aggregation:* count, mean, 20% trimmed mean, dispersion.
5. *Fusion:* LightGBM quantile regression on 12 price/volatility features plus text.
6. *Conformal layer:* MAPIE split conformal and conformalized quantile regression (CQR), plus our Adaptive Conformal Inference (ACI) loop for drift.
7. *Spike, CR-ACI:* if at most k posts of a stock-day are injected, the clean features lie in a "deletion box" whose per-feature ranges are exact in real arithmetic (computed with a derived round-off margin). We propagate the box through every tree. At a fixed conformal offset, the interval then contains the clean model's interval, so injection within budget cannot add misses. ACI separately targets long-run daily coverage; separately adapted clean and attacked runs need not be nested.

**Minimum Viable mapping.** MV1 (fusion of text sentiment and a time-series signal): the LightGBM quantile fusion model, running end to end. MV2 (off-the-shelf conformal bounds): MAPIE split conformal and CQR around it, also running.

**Stretch ambitions.** Both are already built.
- *Adversarial:* pump attacks, the worst of 53 tested variants, bursts on chosen days, and budgets beyond k.
- *Noisy labels:* flipping 20% / 40% of the scorer's training labels lowers macro-F1 to 0.66 / 0.61.
- *Calibration:* Kupiec and Christoffersen tests, day-clustered confidence intervals, coverage by volatility regime.

Next: an edit budget (attackers who alter real posts) and pre-registered FNSPID news 2018–2023.

**Novelty.**
1. We specialise robust conformal verification to *document-injection budgets*, using tractable deletion ranges. VRCP and RCP1 already certify regression under other threat models; in our searches none covers injected documents feeding a text-and-time-series regressor.
2. Admission is decided by evidence: the certified width cost of text is set against its pre-registered value on unseen data. If text fails, the channel stays off and the price-only model, a separate zero-exposure alternative, is used.

**Evaluation plan and preliminary results.** StockNet (87 US stocks; exploratory, because its test period was inspected during development): train 2014, calibrate H1-2015, test Jul-2015–Mar-2016 (16,443 stock-days). Target coverage is 90%.
- *The starter baseline is not meaningful.* Split conformal covers 81.6% overall and 76.9% in the high-volatility tercile (Kupiec p < 0.001). CQR reaches 86.6%; ACI 89.5% (day-clustered 90% CI 87.5%–91.2%).
- *Text value.* Pinball loss is 0.3508 with text vs 0.3513 without. On unseen Kaggle DJIA news (2008–2016, 505 test days) the pre-registered test found no evidence that text adds value: Winkler 3.524 → 3.520, p = 0.46. The test conditions on the official open; an exploratory pre-open variant is also null (p = 0.73). A positive control shows it detects a +11.1% gain but misses +3.9%.
- *Attacks (k = 3; symmetric CQR).* The worst tested variant per row drives plain CQR to 84.7%. The certified interval cannot fall below this test set's clean 86.7%, and covers 89.5% under the worst fixed attack (plain 85.7%). With 10 injected posts, beyond budget, it still covers 86.9% (plain 86.2%). CR-ACI covers 89.5% clean and 89.7% under a pump, for +0.4% / +1.0% width versus plain ACI.

Baselines: price-only, text-only and fusion models, each with split, CQR and ACI.

**Feasibility and risks.** Everything runs CPU-only on one laptop. The cached StockNet evaluation takes 217 s. The v1 non-timing results were independently reproduced; v2 changes are recorded. Unit tests check the certificate against brute force and ACI against its theorem. Risks:
- Text may stay weak; the pitch rests on guarantees.
- The threat model is injection-only; an edit budget is next.
- Boxes may loosen as features grow; a ratchet loop minimises certified width.

Team: Ashish (IIT Delhi; works with Microsoft), plus up to two teammates to be confirmed at registration. The MVP already runs end to end, so the plan does not depend on them.

| Dates | Milestone |
|---|---|
| by 15 Oct | Register; confirm team |
| by 30 Oct | Submit abstract (deadline 31 Oct) |
| Oct–Nov | Edit budget; FNSPID pre-registration; demo |
| 19–25 Nov | Exams (automated runs only) |
| 1 Dec · 15–18 Dec | Midway report · Finals: attack toggle, k slider |
