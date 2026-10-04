# V4: state-by-state wasting gap, verified at primary sources (lead, 2026-10-04 18:09 IST)

**Output:** [`state_gap_verified.csv`](state_gap_verified.csv): 36 States/UTs + India; NFHS-5 (2019–21) vs Poshan Tracker (June 2025) stunted / wasted / underweight %.

| Series | Primary source (opened and parsed by the lead) | Check |
|---|---|---|
| NFHS-5 2019–21, children under 5, by State/UT | Lok Sabha Unstarred Question No. 2668 (MWCD), answered 04.08.2023, Annexure "Prevalence of under-nutrition among women and children as per NFHS-5 (2019-21)": https://sansad.in/getFile/loksabhaquestions/annex/1712/AU2668.pdf?source=pqals (sha256 `a1033b69…10dbc7`) | All 36 States/UTs parsed; the India row reads 35.5 / 32.1 / 19.3 (stunted / underweight / wasted), matching PIB PRID 1988614. The annexure's own serial numbers skip 27 and repeat 30; all 36 rows are present. Cross-checked against the CC-BY compilation pratapvardhan/NFHS-5: wasting identical for 35/36 (Delhi unmatched only by name). |
| Poshan Tracker, June 2025, 0–5 years, by State/UT | Rajya Sabha Unstarred Question No. 477 (MWCD), answered 23.07.2025, Annexure I: https://www.sansad.in/getFile/annex/268/AU477_kllCxU.pdf?source=pqars (sha256 `f96a3377…98d4`) | All 37 rows of `L4-poshan-state.csv` match the PDF exactly ("J&K" there = "Jammu & Kashmir"). |

**Finding (REAL data):** Poshan Tracker's June 2025 wasting is lower than NFHS-5's in **36 of 36** States/UTs; nationally 5.46% vs 19.3%. Stunting is close in most states (India 37.07% vs 35.5%).

**Caveat (must accompany any display):** different periods (2019–21 vs June 2025), age bands (0–59 months vs 0–5 years), and denominators (household sample vs registered and measured children). This is an *unexplained discrepancy*, not a measured under-detection rate.

**Extra data point, same LS 2668 answer (verbatim):** "as per data recorded in Poshan Tracker … close to 7 crore children were measured in the country in the month of June 2023 as per which, 7% were wasted and 19% underweight".
