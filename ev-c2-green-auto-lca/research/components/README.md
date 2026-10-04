# Per-component research — innovation candidates (lean-mode v0, 4 Oct 2026)

_One section per component instead of one file each (Supervisor lean-mode allowance). Evidence: `research/landscape.md` (opened sources) and committed runs in `eval/results/` and `components/ingestion/autoresearch/results.tsv`. Deeper per-component scans (with research sub-agents) are queued for when lean mode lifts._

## C1 Source registry + fetchers
- **Best practice:** a registry with URL, publisher, year, licence, access date; scripted re-download (`data/fetch/fetch_sources.sh`).
- **Innovation room:** content hashes of every raw file (detect silent revisions — e.g. CEA re-issues a version); link-rot monitoring; archive copies.
- **Metric:** % sources re-fetchable and hash-stable.

## C2 Factor store + validator
- **Best practice:** ILCD/openLCA-style process and flow records; ecoinvent pedigree matrix.
- **What we do differently:** record = one number + locator + verbatim quote + status; fail-closed loader. Tonight the verifier found my own weakness (OM/BM quotes lacked their numbers) — evidence that machine-checked provenance pays off.
- **Innovation room:** automatic unit normalisation (pint), gas-basis harmonisation (CO2 vs CO2e, AR4/AR5/AR6), conflict detection when two sources disagree for the same quantity.
- **Metric:** quote-verification rate (16/16 today).

## C3 Ingestion / extraction — ★ spike A
- **Best practice:** manual transcription by LCA analysts; generic PDF table extraction.
- **Candidates:** (a) rule/regex extractors per known document family (CEA user guide, Lok Sabha answers, BRSR Principle 6 tables); (b) LLM extraction constrained to output page + verbatim quote, followed by the fail-closed verifier; (c) layout-aware table parsing (pdfplumber word coordinates).
- **Stress test (black hat):** LLMs invent or mis-unit numbers → verifier with digit-perturbation negatives (ratchet 1: found-rate 1.0 at 0/32 false accepts).
- **Metric:** field-level F1 vs gold set; quote-found rate; false-accept rate = 0.

## C4 Grid-factor service — ★ spike B
- **Best practice:** one national average factor (most studies); ICCT used IEA STEPS life-cycle mix averaged over the vehicle lifetime (767 g CO2e/kWh incl. T&D).
- **India-specific room:** CEA station workbook has STATE for every unit (FY2017-18..2025-26) → state generation-based factors once state RE generation is added; CEA OM/BM/CM margins for marginal/new-build views; lifetime-average and prospective factors (premise-style) from CEA's own trajectory; state-wise T&D losses (Lok Sabha USQ 842 annex, on disk).
- **Metric:** reconstruction error vs CEA national values; year-ahead back-test error.

## C5 Product-system & scenario builder
- **Best practice:** carculator / carculator_two_wheeler parameterised vehicle models (European defaults).
- **Room:** Indian vehicle templates (2W, 3W, car, bus) with bill of materials linked to Indian material routes (BF-BOF vs DRI-EAF steel, coal-power aluminium), Indian Driving Cycle consumption.
- **Metric:** % parameters resolved to records (100 % today); BOM mass closure.

## C6 Calculation engine
- **Best practice:** matrix LCI (Brightway bw2calc, openLCA).
- **Room:** keep the parameterised stage model for transparency; add matrix LCI for supply chains; dimensional analysis.
- **Metric:** replication MAPE vs published studies (0.06 % on ICCT 2021).

## C7 Uncertainty, sensitivity, DQI, data gaps
- **Best practice:** pedigree → lognormal (ecoinvent/Brightway), Monte Carlo, contribution analysis.
- **What we added:** paired sampling for comparisons; elasticity-weighted DQI; India-specific share; variance-share data-gap ranking (today: consumption data = 65 % of the saving's variance).
- **Room:** calibrate pedigree factors against independent Indian benchmarks; separate scenario (method) uncertainty from parameter uncertainty in one view.
- **Metric:** interval coverage on independent benchmarks (needs ≥ 5).

## C8 Benchmark & validation harness
- **Room:** transcribe every open Indian vehicle LCA (2021–2026) into benchmark YAML with stated inputs; automatic "can the paper be reproduced from its own inputs?" report — the ICCT check generalised.
- **Metric:** # benchmarks reproduced within ±2 %.

## C9 Dashboard / API
- **Best practice:** static charts in PDF reports; carculator web app.
- **Room:** click-through provenance for every number (built), what-if grid slider with break-even (built), India state map, "add a dataset" flow.
- **Metric:** share of displayed numbers with provenance (100 % of parameters today).

## C10 Exporters
- **Room:** openLCA JSON-LD / ILCD export so ICAT and industry can reuse records in existing tools.
- **Metric:** round-trip import success.
