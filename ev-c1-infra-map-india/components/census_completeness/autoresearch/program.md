# Auto-research program — C5 `census_completeness` (Spike 1)

## Goal
Estimate the true number of public EV charging sites per region from incomplete, overlapping source lists (OSM, Open Charge Map, later operator feeds and UEI), so that every supply figure on the platform carries a coverage factor. The state level is where official totals exist to validate against. The end use is *districts*, where none exist (small-area estimation).

## Metric (frozen in `eval.py`, lower is better)
`dev_median_abs_log_err` = median over DEV states of |ln(estimate / official)|. The official figure is state-wise public charging stations from PIB 2151390 (1 Aug 2025).
- States with official ≥ 100 are split alphabetically and alternately into DEV (12) and HOLDOUT (11).
- DEV is scored leave-one-state-out, so the estimator never sees the target state's official total.
- HOLDOUT is only checked by the lead (`--holdout`) to catch metric gaming.
- Keep a change only if it beats the best DEV metric by > 0.02 (noise margin; only 12 states).

## Rules
- Edit **only** `../estimator.py` (function `estimate(osm, ocm, ctx)`; return a positive estimate for every state).
- Never read official totals except via `ctx["official"]` (training states only). Never hard-code state numbers.
- Every run appends a row to `results.tsv` (timestamp · commit · hypothesis · metric · delta · kept · notes).
- Runtime ≤ 60 s per eval on the M5 Mac.

## Known caveats
- **Unit mismatch.** Official counts are "public charging stations". OSM features and OCM POIs are sites or sometimes single sockets, and OCM includes some non-public usage types. The target is a proxy, not the truth.
- **Different dates.** Official totals are as of 1 Aug 2025; OSM is from Oct 2026; the OCM export is from Apr 2026.
- **Source dependence.** Two-source Chapman assumes independent lists. OSM and OCM both over-capture "easy" sites (brands, highways, malls), which biases the estimate low.

## Idea backlog (ranked)
1. Stratify capture–recapture by site type (power class, brand vs independent, urban vs highway) to reduce heterogeneity bias.
2. Better matching: name/operator similarity + distance (Fellegi–Sunter weights) instead of pure distance; tune on a hand-labelled pair set (C4).
3. Calibration / small-area model: ln(official) ~ ln(BEV registrations) + ln(observed) + urbanisation; try a hierarchical (partial-pooling) version.
4. Add a third list: split OSM by `source=*` tags or edit vintage, or add one operator list → log-linear multiple-systems estimation with an interaction term.
5. Use the BEE tier-1/2/3 split (PIB 2118894) as auxiliary information for urban/rural strata.
6. Bootstrap CIs; report coverage of the CI on HOLDOUT (target: nominal 90% → observed ≥ 80%).
