# Round 1 abstract — Perceptron 2026, Problem 10: Trusting a Signal Extracted from Messy, Manipulated Text

_Rendered from committed results by `deliverables/render.py` (template: `round1-abstract.template.md`); `deliverables/check_drift.py` fails if any number is stale. Results: `eval/results/`. The team section is to be completed by the team._

**Problem & theme.** Theme 6 (AI You Can Actually Trust), Problem 10. Desks and apps act on sentiment from news and social posts, and one hacked tweet once moved the Dow 140 points. We make the confidence bound, not the point forecast, the thing a user can trust when some of the text is fake.

**Understanding of the challenge.** Three difficulties interact.
1. **Text is a weak signal.** On two datasets we found it adds no measurable accuracy to a strong price baseline (results below).
2. **Returns are not exchangeable.** Volatility clusters, so a split-conformal band that is valid on average under-covers exactly in stressed markets.
3. **Manipulation acts on the test input.** Injected posts move the features after calibration, which no standard conformal guarantee covers.

So "meaningful" must be measured: valid on held-out time and within regimes, misses not clustered, narrow, and robust to a stated attack budget.

**Proposed approach.** A ten-component pipeline with typed contracts:
1. *Ingest and align* posts to the 16:00 New York close. Look-ahead leakage is a tested metric: {{prepare_stats_minilm_v1:leakage_docs|int}} of {{prepare_stats_minilm_v1:tweets|int}} tweets leak.
2. *Text scorer:* frozen MiniLM-L6 embeddings plus a sentiment head trained on labelled financial tweets (macro-F1 {{text_scorer_isolated_v1:minilm.macro_f1|pp2}} vs {{text_scorer_isolated_v1:vader.macro_f1|pp2}} for the VADER lexicon). It never sees returns, so unlike LLM backtests it cannot memorise outcomes.
3. *Trust* from each post's own account metadata.
4. *Bounded-influence aggregation:* count, mean, 20% trimmed mean, dispersion.
5. *Fusion:* LightGBM quantile regression on 12 price/volatility features plus text.
6. *Conformal layer:* MAPIE split conformal and conformalized quantile regression (CQR), plus Adaptive Conformal Inference (ACI) for drift.
7. *Spike, CR-ACI:* if at most k posts of a stock-day are injected, the clean features lie in a "deletion box" whose per-feature ranges we compute exactly from order statistics. We propagate the box through every tree and widen by the ACI-tuned conformal correction. For every attack within budget, the interval contains the clean model's interval, so an attacker cannot add misses.

**Minimum Viable mapping.** MV1 (fusion of text sentiment and a time-series signal): the LightGBM quantile fusion model, running end to end. MV2 (off-the-shelf conformal bounds): MAPIE split conformal and CQR around it, also running.

**Stretch ambitions.** Both are already built.
- *Adversarial:* pump attacks (k bullish posts from fresh accounts), a {{text_minilm_v1:attack.oracle.grid_size|int}}-variant oracle, and burst attacks on chosen days.
- *Noisy labels:* flipping 20% / 40% of the scorer's training labels lowers macro-F1 to {{text_scorer_isolated_v1:minilm_noise0.2.macro_f1|pp2}} / {{text_scorer_isolated_v1:minilm_noise0.4.macro_f1|pp2}}.
- *Calibration:* Kupiec and Christoffersen tests, day-clustered confidence intervals, coverage by volatility regime.

Next: an edit budget (attackers who alter real posts) and FNSPID news 2018–2023.

**Novelty.**
1. Robust conformal methods (RSCP, VRCP, ICML 2024, NeurIPS 2025) certify bounded perturbations of one input, or poisoned calibration data, mostly for classification. In our searches none certifies coverage against a budget of injected documents feeding a text-and-time-series regressor.
2. We pre-registered "does text help?" on unseen data. A price-of-robustness curve (width versus k) then decides how much text to admit; dropping text is its k = ∞ end.

**Evaluation plan and preliminary results.** StockNet ({{text_minilm_v1:meta.tickers|int}} US stocks, tweets with account metadata): train 2014, calibrate H1-2015, test Jul-2015–Mar-2016 ({{text_minilm_v1:meta.n_test|int}} stock-days, including the Aug-2015 and Jan-2016 sell-offs). Target coverage is 90%.
- *The starter baseline is not meaningful.* Split conformal covers {{text_minilm_v1:ablation.fusion.split.coverage|pct}} overall and {{text_minilm_v1:ablation.fusion.split.cov[vol=high]|pct}} in the high-volatility tercile (Kupiec {{D:kupiec_split|str}}). CQR reaches {{text_minilm_v1:ablation.fusion.cqr_mapie.coverage|pct}}; ACI {{text_minilm_v1:ablation.fusion.cqr_aci.coverage|pct}} (day-clustered 90% CI {{text_minilm_v1:ablation.fusion.cqr_aci.mean_day_coverage_ci90.0|pct}}–{{text_minilm_v1:ablation.fusion.cqr_aci.mean_day_coverage_ci90.1|pct}}).
- *Text value.* Pinball loss is {{text_minilm_v1:ablation.fusion.pinball_mean|pp4}} with text vs {{text_minilm_v1:ablation.price_only.pinball_mean|pp4}} without. Our pre-registered test on unseen Kaggle DJIA news (2008–2016, {{text_utility_djia_v1:meta.n_test|int}} test days) found {{D:djia_decision|str}}: interval score {{D:djia_rel_improvement_pct|signpct}}, p = {{text_utility_djia_v1:primary.p_one_sided|p}}.
- *Attacks (k = 3).* The oracle drives plain CQR to {{text_minilm_v1:attack.oracle.vanilla_cqr_oracle_coverage|pct}}. The certified interval is guaranteed never to fall below the clean {{text_minilm_v1:attack.oracle.certified_guaranteed_floor|pct}}. Under the worst fixed attack it covers {{D:worst_variant_cert_cov|pct}} (plain CQR {{D:worst_variant_vanilla_cov|pct}}). CR-ACI covers {{text_minilm_v1:spike.cr_aci.cr_aci_clean.coverage|pct}} clean and {{text_minilm_v1:spike.cr_aci.cr_aci_pump.coverage|pct}} under a pump, for {{D:cr_aci_clean_width_pct|signpct}} / {{D:cr_aci_pump_width_pct|signpct}} width versus plain ACI. The insurance is cheap because the exposure is small.

Baselines: price-only, text-only and fusion models, each with split, CQR and ACI.

**Feasibility and risks.** Everything runs CPU-only on one laptop; the full StockNet evaluation takes {{text_minilm_v1:meta.runtime_s|int}} s. Unit tests check the certificate against brute force and ACI against its theorem. Risks:
- Text may stay weak. The pitch rests on guarantees; FNSPID and stronger scorers will be tested, not assumed.
- The threat model is injection-only; an edit budget is next.
- Boxes may loosen as features grow; a ratchet loop minimises certified width.

Team: Ashish (ML systems; large-scale and frontier-model engineering) plus two teammates, names and skills TBD.

| Weeks | Milestone |
|---|---|
| 5–18 Oct | Edit-budget certificate; FNSPID subset |
| 19 Oct–1 Nov | Regime-conditional conformal; final abstract |
| 2–15 Nov | Ratchet loops; demo dashboard |
| 19–25 Nov | Exams (automated runs only) |
| 1 Dec | Midway report |
| 15–18 Dec | Finals: live attack toggle and k slider |
