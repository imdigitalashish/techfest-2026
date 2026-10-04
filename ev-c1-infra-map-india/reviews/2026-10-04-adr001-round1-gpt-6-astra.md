# Hostile-judge review: ADR 001 and Round-1 submission

**Reviewer:** GPT-6 Astra (`gpt-6-astra`), methodology/statistics and MHI/ICAT jury perspective. **Date:** 4 October 2026.

**Baseline:** [`46d10f7189f3f8b5213155410802c60a2c3f4df5`](https://github.com/imdigitalashish/techfest-2026/commit/46d10f7189f3f8b5213155410802c60a2c3f4df5). All line numbers refer to that snapshot, even if the lead subsequently changes the files. Paths are relative to `ev-c1-infra-map-india/` unless stated otherwise. This is a review, not an implementation change.

**Verdict: 70/100 for Round 1.** This is a credible, unusually transparent proposal, but not yet a defensible investment-allocation system. Demoting the failed completeness estimator is the right decision. The principal weakness is calling exploratory comparisons "validation" or "held out" more broadly than the experiments support. Fixing that does not require premium data or abandoning the project.

Reference shorthand: **M** = [methodology](../deliverables/round1-methodology.md); **R** = [roadmap](../deliverables/round1-roadmap.md); **ADR** = [ADR 001](../architecture/adr/001-spike.md); **FC** = [fact-check](../research/fact-check.md); **L** = [landscape](../research/landscape.md).

I read M/R, then ADR including its addendum, then FC/L, followed by the relevant implementations, result tables, experiment ledgers and thought-node log. Read-only checks reproduced the coverage fractions, principal result-table arithmetic, model-selection sensitivity and a nowcast invariant violation. `python3 -B eval/check_docs.py`, run inside the project, passed: six documents and 194 rendered keys. That checks rendering, not scientific validity. I did not run the mutating `run_all.sh`: this review was restricted to one output file, and the fresh worktree lacks the ignored raw VAHAN snapshots and project virtual environment. No full raw-data reproduction is claimed.

## A. Round-1 scoring

These are my judgments against the weights in the repository's `_briefs/ev-infra.txt`, not a prediction of other teams' scores. Round 1 asks for a methodology and roadmap; unfinished Round-2 features are not automatically defects.

| Criterion | Weight | Score / 10 | One-line justification | What would raise the score |
|---|---:|---:|---|---|
| Problem understanding and relevance | 25% | 8 | M sections 1 and 2.6 identify real planning users, segment differences and policy norms, but current rankings still substitute registration pressure for service need. | Specify one actionable MHI/SNA decision, its budget and service constraints, and the distinction between information gaps and charging gaps. |
| Feasibility and technical soundness | 25% | 6 | Executable baselines and an honest failed spike are strong; overlapping evaluation targets, unvalidated district uncertainty and the sizing formula weaken the evidential claims. | Purge temporal target overlap; freeze a genuinely future validation plan; label district intervals conditional; correct the energy units and require abstention for non-estimable MSE fits. |
| Innovation / novelty | 20% | 7 | A reproducible inventory-completeness audit is a plausible application contribution, but neither methodological priority nor better planning decisions has been established. | Keep a narrow dated novelty claim and demonstrate that uncertainty-aware recommendations improve a measurable planning decision over transparent baselines. |
| Clarity and completeness of roadmap | 20% | 7 | R maps deliverables to dated stages, exams and exit tests; it lacks named ownership, data-access deadlines and decision-grade acceptance criteria. | Add owners, effort/dependencies, a no-new-feed MVP, explicit budget/grid/queueing tests and a hard scope cut before the exam window. |
| Planned data strategy | 10% | 7 | Multiple open sources, provenance, licensing notes and source verification fit the brief; unit/vintage harmonisation, list eligibility and independent district labels remain weak. | Add a source-role/vintage matrix, verified public-access/status fields, an actionable BEE/API request and a stratified local audit with unknowns preserved as unknowns. |
| **Weighted total** | **100%** | **7.0** | **20 + 15 + 14 + 14 + 7 = 70/100.** | The largest gains are from better experimental design and narrower claims, not a more complicated model. |

Do not spend the remaining time polishing the "first" claim at the expense of the requirement module. The brief explicitly values defensibility over proprietary-data access. Conversely, lack of premium data does not justify presenting model-imputed supply as observed shortage.

## B. Statistics and methodology

### B1. Three-source capture-recapture

**Strongest objection:** the unseen population is identified by strong, untested assumptions about dependence, eligibility and time, while the reported interval conditions on one fragile model and one unverified linkage. This is not just a small-sample precision problem.

**Is "fails validation" right?** Yes as the result of the implemented engineering gate; no as proof that capture-recapture itself is invalid or that the true national total is known to contradict the estimate.

`eval/results/c5_mse_summary.json` reports median absolute log error **0.844**, against a cutoff of `ln(1.25)` (about **0.223**), and interval inclusion **8/17 = 47.1%**, against 80%. The median estimate/official ratio **0.576** is a bias summary, not the median absolute error. The absolute-log result corresponds to a median multiplicative discrepancy of about **2.33**, a much clearer description of the failure than merely saying "0.58 times official."

However, the lists are OCM April 2026, Overture September 2026 and OSM October 2026; the reference is the August 2025 official release (`mse.py:1-10`). They are not contemporaneous observations of a closed population. Public/semi-public access, installed versus operational status, and site versus equipment units are not harmonised by this comparison. The rejection is therefore an **external-reference discrepancy screen**, not measured frequentist coverage against a known 2026 population. Calling the discrepancy's causes definitively "thin overlaps and heterogeneous capture" (M:75; ADR:62) overstates what was diagnosed.

**Seven cells and model choice.** `mse.py:81-116` considers eight models with four to seven coefficients. The selected national model contains all three pairwise interactions: seven parameters for seven observed histories, hence zero residual degrees of freedom on those histories. It is saturated on the observed table; the missing cell is inferred by assuming the three-way interaction is zero. That assumption cannot be tested from these seven cells alone.

The committed histories are `001=952, 010=1720, 011=65, 100=501, 101=15, 110=76, 111=7`. Under the selected model:

`N_unseen = (7 * 501 * 1720 * 952) / (76 * 15 * 65) = 77,496.7`

Adding the observed 3,336 reproduces **80,832.7**. Independent maximisation of the same Poisson likelihood on these committed counts gives:

| Pairwise interactions included | Parameters | Estimated national sites | AIC above best |
|---|---:|---:|---:|
| OSM-OCM, OSM-Overture, OCM-Overture | 7 | 80,832.7 | 0.00 |
| OSM-OCM only | 5 | 28,471.0 | 0.86 |
| OSM-OCM and OCM-Overture | 6 | 35,132.8 | 1.77 |

An AIC difference of **0.86** is weak discrimination, yet the estimates differ by nearly a factor of three. The selected-model lower bound, **35,915**, even exceeds the point estimate of the near-tied OSM-OCM model. AIC is not inherently inappropriate here, but it does not resolve the substantive identification problem. Merely switching to AICc is not a general cure for models this close to saturation.

For reproducibility, this is a read-only sensitivity calculation from the repository root; it does not refit to official totals:

```python
import itertools, json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

s = json.loads(Path("ev-c1-infra-map-india/eval/results/c5_mse_summary.json").read_text())
patterns = np.array([p for p in itertools.product([0, 1], repeat=3) if any(p)])
y = np.array([s["national_cells"]["".join(map(str, p))] for p in patterns])
pairs = {"OC": (0, 1), "OV": (0, 2), "CV": (1, 2)}
for model in [("OC", "OV", "CV"), ("OC",), ("OC", "CV")]:
    X = np.column_stack([np.ones(7), patterns] +
                        [patterns[:, pairs[k][0]] * patterns[:, pairs[k][1]] for k in model])
    initial = np.linalg.lstsq(X, np.log(y), rcond=None)[0]
    def objective(beta):
        eta = X @ beta
        mu = np.exp(eta)
        return float((mu - y * eta).sum()), X.T @ (mu - y)
    result = minimize(objective, initial, jac=True, method="BFGS",
                      options={"gtol": 1e-6})
    print(model, y.sum() + np.exp(result.x[0]), 2 * X.shape[1] + 2 * result.fun)
```

The omitted Poisson factorial constant cancels in AIC differences.

**Dependence and heterogeneous capture.** The sentence "each source as an independent capture" (M:68) contradicts fitting interaction models. Say "three capture lists with modelled pairwise dependence and untested residual heterogeneity." Overture containing no OSM data does not establish statistical independence: the same brands, cities or upstream operator directories can affect all lists. Stratifying may reduce heterogeneity but also destroys already-thin overlaps. A denser list does not automatically solve dependence or create a representative population.

**An actual non-estimability problem is being reported as precision.** `c5_mse_by_state.csv:4` gives Assam **2.7 [2.7, 2.7]**, despite just two OCM-only sites and no recaptures. Chhattisgarh has **55.7 [55.3, 56.2]**, also with no cross-list recaptures (`:7`). These data do not support such precise estimates of unseen sites. `fit()` clips linear predictors, does not reject exhaustion of its 100 iterations, and returns some boundary/degenerate solutions (`mse.py:94-117`). At minimum, eligibility and convergence need explicit checks and a "not estimable" outcome.

The bootstrap fixes the chosen model and observed total, assigns zero probability to unobserved histories, and drops failed fits (`mse.py:120-137`). For Gujarat only **178/300** replicates survive (`c5_mse_by_state.csv:11`). Nominal 90% unconditional coverage cannot be claimed for these selectively retained, fixed-model intervals. Neither linkage error, changes in list coverage over time nor model-selection uncertainty is included.

**Is the pass rule sensible?** Reasonable as a conservative, documented operational screen, with these corrections:

- `median(abs(log(ratio))) < log(1.25)` is a multiplicative-factor criterion, not conventional symmetric plus/minus 25% error; its individual-ratio band is 0.8 to 1.25.
- There are **23** official states/UTs with at least 100 PCS, but only **17** receive an evaluated finite estimate. Five have linked records but no fit; Jammu and Kashmir has no row. Report availability **17/23** separately from conditional coverage **8/17**, and do not let dropping hard states improve the success criterion (`mse.py:168`; official and MSE state CSVs).
- An 80% coverage gate for nominal 90% intervals on 17 states is a tolerance rule, not proof of calibration. It also needs a width/usefulness criterion so arbitrarily wide intervals cannot earn a pass.
- The inspected earlier ADR gate required relative error below 25% in states with at least two sources (ADR:27), not this complete rule. The first MSE code/results occur together in commit `1860bb7`. "Pre-registered" (M:75) needs an earlier frozen protocol; absent that evidence, call it a versioned heuristic gate.

**Fatal?** Fatal to using these MSE point estimates or intervals as planning inputs today; **not fatal** to publishing a failed audit and continuing with a transparent prototype.

**Cheapest fix:** retain the demotion; rename the exercise an external-reference stress test; abstain on non-estimable fits; report model/radius sensitivity and fit availability; label any remaining intervals conditional. Hand-audit linkage/public-site eligibility before seeking a fourth list. Do not increase complexity just to force agreement with the official reference.

### B2. Small-area allocation to districts

**Strongest objection:** an across-state regression is transported to within-state allocation, and its only district benchmark was also used to choose the approach and revise its uncertainty. This is an ecological transportability assumption, not established district-level calibration.

`small_area.py:61-87` estimates elasticities across states, then applies them to district BEV and open-site counts. State size, urbanisation, operator composition and policy differences can create an across-state relationship that need not hold among districts within Maharashtra. This is not a classical district random-effects model with observed district training outcomes; it is a **model-based, state-total-constrained allocation**.

The Chhattisgarh exercise does show something useful: conditional on its supplied total, small-area WAPE **0.410** beats BEV-share **0.540** and open-share **0.995**. But its rank correlation **0.841** is slightly worse than BEV-share **0.855** (`small_area_summary.json`). Do not imply dominance on every metric.

**What was actually held out?** Other states' official counts train the coefficients; the target state's aggregate is supplied to the allocator; only the district distribution is withheld from that fit. M:140 and the official-data row at M:155, "held out from the estimators", are false as blanket descriptions. For Chhattisgarh, `total = truth.sum()` explicitly uses the evaluated district total (`small_area.py:117-119`). That is legitimate for conditional allocation, but different from independently predicting supply.

**The target needs a reconciliation note.** The official annex CSV contains **31 rows totalling 271** stations. Validation scores **270** over **28 2021-boundary units**. It drops Sarangarh-Bilaigarh, merges aliases and a split district, and converts absent annex entries to zero; Gaurella Pendra Marwahi is consequently scored as zero (`small_area.py:104-125`; `cg_district_validation.csv:13`). The geography contains 28 units, not 28 independently reported official labels. An unreported district is not automatically a verified zero.

There is also a date mismatch inside the experiment: the state regression uses BEV reconstructed to November 2024, while the district allocation uses **218,859 till-today registrations** and 2026 open listings against the December 2024 annex (`small_area.py:111-125`). Harmonising only the state regressors does not make the district test contemporaneous.

**Interval calibration:** coverage is **23/28 = 82.1%**, not evidence of a generally calibrated 90% interval. The implementation's own header says coefficient-only intervals covered just **29%** before multinomial count noise was added (`small_area.py:8-9`). That documents feedback from the only district benchmark into interval design; the resulting coverage is not an untouched validation result.

The bootstrap represents between-state coefficient variability, and the multinomial assumes independent station assignments conditional on the state total and predicted district probabilities. Neither supplies a measured distribution for district-specific misspecification, operator clustering, wrong crosswalks, missing labels or stale totals. Raking creates correlated district errors. Even pretending the 28 indicators were independent, a descriptive Wilson 95% interval around 23/28 is roughly **64%-92%**; 90% is inside it. Therefore neither "calibrated" nor "statistically proven undercoverage" follows. Transportability still has **one state-level replication**.

**Fatal?** Not fatal for an explicitly exploratory fallback. Fatal to calling the Maharashtra ranges validated 90% uncertainty or using them to certify a district's shortage.

**Cheapest fix:** publish the annex-to-boundary crosswalk and missing-label policy; score only harmonised known targets, with a sensitivity analysis for the omitted station; align BEV/list vintages where possible. Relabel the current ranges "conditional model ranges, not externally calibrated." Freeze the model and interval recipe before collecting another state or a modest, stratified independent district/site audit. If no additional official annex is available, an honestly documented public-source/field verification sample is preferable to calling repeated use of Chhattisgarh new validation.

### B3. Forecast backtest and 2026 nowcast

**Strongest objection:** the split holds out origins, not target observations, so development model selection has seen outcomes that recur in the nominal holdout.

`eval_monthly.py:26-31` has the following boundary:

| Origin | Months being predicted |
|---|---|
| Last DEV: September 2024 | October 2024-September 2025 |
| First HOLDOUT: December 2024 | January-December 2025 |
| Shared target months | **January-September 2025: nine months** |

The first three holdout origins share respectively nine, six and three target months with the development target span. Only the September 2025 origin has targets wholly beyond that span. The four holdout windows cover **21 unique calendar months**, not 48 independent months; states also share national shocks.

This is **not evidence that the forecasting function reads future predictor rows**: `score()` correctly slices history to each origin. The monthly ledger also supports selection on DEV: nine proposals were logged, and the selected configuration improved DEV WAPE from 0.1732 to 0.1470. The defect is outcome reuse in model selection/evaluation and dependence of the resulting errors, not a fabricated backtest.

The arithmetic **0.2229 to 0.1572 = 29.5% lower WAPE** is correct (`c9_summary.json`), but "29% more accurate" (M:105) is broader than that claim. It is not a significance result, does not ensure small-state accuracy, and does not validate a 2030 forecast. `forecast_12m()` predicts a next-year aggregate; multiple-year extrapolation, segment forecasts and uncertainty have not been validated by this experiment.

The evaluator fills missing state rows with zero (`eval_monthly.py:18-24`) and uses a present-day historical extract. Distinguish a zero from unavailable historical coverage, and call this a current-vintage retrospective backtest unless vintage-specific snapshots demonstrate what was observable at each origin. Also, rerunning all candidate holdout scores on every `run_all.sh` execution does not preserve a permanently unseen test (`nowcast.py:50-61`; `eval/run_all.sh`).

**Nowcast-specific findings:**

- `nowcast.py:34-43` chooses the best of three methods using 2023-2025 mean WAPE and reports error on those same years. **7.21%** is model-selection-period, full-year WAPE, not an independent test error.
- YoY beats the ensemble by only **0.09 percentage points** of mean WAPE (0.0721 versus 0.0730). Three years do not establish a robust superiority claim. The reported national **3.01%** is mean **absolute** relative error; the individual errors are +7.73%, +0.31% and -0.99% (`c9_nowcast_backtest.csv`).
- **3.56-3.60 million is a spread of closely related methods, not a prediction interval.** M:107 correctly calls these other methods, not a 90% interval; preserve that distinction prominently. The entire spread is 40,430 registrations, much narrower proportionally than the largest historical national error. Full-year errors include nine already observed months; separately assess the unobserved fourth-quarter residual.
- There is a concrete consistency failure: `c9_nowcast_2026.csv:37` gives Ladakh's selected YoY full-year forecast as **7**, below **8 already observed in January-September**. `nowcast.py:28-30` scales a previous full-year count rather than guaranteeing a non-negative remaining-year increment. Small national impact does not make the output logically valid.

**Fatal?** Not fatal to a sensible pooled baseline. Fatal to presenting the current split as independent confirmation or the method spread as calibrated uncertainty; the Ladakh invariant should be fixed before publishing fresh nowcast outputs.

**Cheapest fix:** relabel existing results retrospective; purge DEV horizons that overlap the first holdout target period and rerun a locked selection recipe. Report per-origin and small-state errors, with calendar-block rather than independent-row uncertainty. Already inspected data do not become pristine holdout through relabelling: reserve genuinely future observations for the next claim. For the nowcast, predict a non-negative October-December increment and add fixed YTD actuals; test `full_year >= observed_ytd`; report selection-period errors and scenario spread honestly. Validate multi-year horizons separately before attaching model accuracy to 2030.

### B4. BEV per station and the Maharashtra gap

**Strongest objection:** this is a registration-to-site ratio, not a measure of usable public charging capacity or unmet charging demand. At district level, its denominator is partly manufactured from its numerator.

M:39-43 already discloses registrations versus stock, the 14-month vintage gap and home/depot/swapping. Keep those disclosures, but carry them into labels and recommendations. A one-connector low-power site and a multi-port fast-charging hub count equally. Vehicle class, retirements, home access, visitor demand, highway flows, uptime, access restrictions and available kW change the planning interpretation. A resident's registration district is not necessarily where charging occurs.

For Maharashtra, the fitted elasticities are **b=0.463, c=0.313** (`mh_district_gap_summary.json`). Thus, for positive BEV counts and fixed state total:

`BEV / estimated_stations is proportional to BEV^0.537 / (open_sites + 1)^0.313`

The model structurally assigns greater registration pressure to larger BEV districts at equal open-site counts. Calling Nagpur "most underserved" (R:13) treats this assumption-driven ranking as independent evidence. Its **574 [423-774]** ratio and four observed open sites are not an observed census of 198 stations. The quoted ranges for Nagpur, Amravati and Nashik overlap, and no joint ranking uncertainty is reported. Marginal interval overlap is not itself a test of a rank difference; neither the point estimates nor these marginal ranges establish an ordering of actual need.

The **3,641** number is the sum of **positive, rounded district shortfalls**, ignoring district surpluses (`mh_district_gap.py:46-47,69`). A straight statewide comparison using the displayed Karnataka density gives `1,185,108 / 152.4 - 4,155`, about **3,621**. These answer different questions. The former needs the label "gross district benchmark additions without reallocation", not merely "stations needed for Maharashtra"; premature rounding adds further differences.

M:133 also has a dimensional omission: `public kWh per day / (kW * utilisation)` is not a charger count if utilisation is a fraction. The denominator needs operating hours per day, for example `deliverable_kW * open_hours_per_day * target_utilisation`, with consistent energy-side losses/availability assumptions. Convert charging units to physical sites separately, and test peak service/queueing rather than relying only on average energy.

**Fatal?** No for a clearly named exploratory registration-pressure indicator. Yes for translating these current rankings or 3,641 into a charger-class procurement recommendation.

**Cheapest fix:** show a vintage-aligned registration benchmark using the existing `bev_cum_at()` helper, alongside the deliberately mixed-vintage indicator; keep data thinness separate from infrastructure shortage. Label imputed denominators prominently, show ranking sensitivity to BEV-share/open-share/small-area allocation, and abstain from definite district priority where they disagree. Make segment/mode-adjusted energy and service constraints the actual Round-2 requirement calculation.

## C. Novelty: what the quick search supports

I made two small search requests, which returned these three query traces on 4 October 2026:

| Query | Result relevant to the claim |
|---|---|
| [capture-recapture charging stations electric vehicle](https://www.bing.com/search?q=capture-recapture+charging+stations+electric+vehicle) | No directly matching primary application was verified; the returned adjacent-paper lead failed the page check below. |
| [multiple systems estimation EV charging stations inventory india](https://www.bing.com/search?q=multiple+systems+estimation+EV+charging+stations+inventory+india) | No matching application surfaced in the returned results. This is a limited search miss, not a universal negative. |
| [Indian EV charging-station inventory completeness capture-recapture multi-source audit](https://www.bing.com/search?q=Indian+EV+charging-station+inventory+completeness+capture%E2%80%93recapture+multi-source+audit) | Returned adjacent inventory/reporting material and the OSM completeness repository, not a verified Indian capture-recapture audit. |

I then opened the closest checkable candidates:

- [iboates/osm-charging-station-completeness](https://github.com/iboates/osm-charging-station-completeness): its README describes periodic **tag completeness** for charging stations, defaulting to Karlsruhe, with a spatial API/UI. This is relevant prior art for charger-data quality, but the README does not establish an estimate of unseen Indian charging sites.
- [Crisafulli and Monzon, 2021, OST thesis](https://eprints.ost.ch/id/eprint/940/): the abstract describes intrinsic **machine-learning POI completeness estimation**, trained in Swiss cities, and explicitly notes the assumed completeness of validation areas. It is adjacent completeness-mapping work, not the claimed Indian charger/MSE application.
- A search-generated supposed adjacent paper at [this ScienceDirect URL](https://www.sciencedirect.com/science/article/abs/pii/S0198971521002871) returned **404**. I did not verify its title or existence and exclude it as evidence. Search summaries are not citations to established literature.

**Judgment:** "the first capture-recapture audit of an Indian charger inventory that we know of" is defensible only as a narrowly scoped, dated statement of the team's search knowledge. It is not demonstrated priority. Safer submission wording: **"We apply classical capture-recapture methods to audit a linked Indian charger inventory; our documented search found no prior Indian charger-inventory application."** Credit adjacent completeness tools and make clear that log-linear MSE, probabilistic linkage and small-area allocation are not newly invented statistics.

The useful contribution can be the reproducible audit, explicit non-estimability and decision consequences of missing data. Neither a negative search nor a failed benchmark alone establishes a planning benefit. The broader thought-node pitch, "India's first completeness-aware EV charging census" (`thought_node.md:77`), is substantially harder to defend and should be narrowed.

## D. Ten hostile finale questions and the best honest answers

These answers describe the reviewed repository, not promises that unbuilt features already work.

| # | Jury question | Best honest answer supported by the evidence |
|---:|---|---|
| 1 | **BEE already maintains the national database. Why should MHI fund another registry?** | "We should complement it, not claim to replace it: join auditable supply records to VAHAN and expose coverage/definition uncertainty in planning. We have not demonstrated bulk access to BEE. Its guidelines explicitly envisage non-confidential open APIs, so obtaining and assessing that interface is a priority." M:26; R:47,56; MoP clause 13 cited in E. |
| 2 | **Do we have 29,277 stations or 80,833, and is your map really 11.4% complete?** | "We cannot infer a single contemporaneous true total from these data. 29,277 is the historical official reference; 80,833 is a fragile conditional estimate that fails our screen and is not used for planning. 11.4% is the linked-list count divided by that older reference, not established present-day completeness." M:17-35,68-76; B1. |
| 3 | **You say official data are held out, but your district model uses them. Which is true?** | "The C5 estimator does not fit to the official count. The small-area model does train on other states' official totals and uses the target aggregate as a constraint. Chhattisgarh tests conditional allocation of that total, not independent prediction of total supply." `small_area.py:61-87,117-125`; M:140 needs correction. |
| 4 | **Why is Nagpur first? Can you show its actual shortage rather than your model's preference?** | "Not yet. It ranks first under a BEV-based allocation model with only four linked open sites. Its 113,736 registrations include 27,143 three-wheelers, which may need depot/swap rather than the assumed public-station mix. It is a verification candidate, not a proven first funding priority." M:122-128; `mh_district_demand.csv`; `mh_district_gap_summary.json`; B4. |
| 5 | **Why should I trust a 90% interval tested in one state, after changing the interval method?** | "**No good answer yet for calibrated Maharashtra coverage.** The current range is conditional on a model and known state total. Chhattisgarh coverage was 23/28 and informed development; we need a frozen independent district/site audit before making a calibrated-uncertainty claim." `small_area.py:8-9,78-87`; B2. |
| 6 | **Does the 29% forecasting gain prove your 2030 recommendation, or that 2026 will be within 3.56-3.60 million?** | "No. It is lower WAPE on an overlapping retrospective next-12-month evaluation. The 2026 interval-looking range is only method spread, and its backtest has three model-selection years. A 2030 scenario needs separate horizon tests and policy assumptions." `eval_monthly.py:26-31`; `c9_summary.json`; B3. |
| 7 | **How many AC/DC chargers, at what cost, should PM E-DRIVE actually pay for?** | "**No good answer yet.** The 3,641 is a district-density benchmark, not a costed eligible project list. Segment/mode energy, service capacity, costs and current scheme conditions must determine that list. M section 2.6 honestly marks this module designed, not built." M:128-136; R stages 2-3. |
| 8 | **Your chosen highway site has a charger dot. Is it reachable from both sides, heavy-duty compliant and connectable to the grid?** | "**No verified site-level answer yet.** Coordinates or proximity to a substation cannot establish those facts. We need directed-road access, suitable charger specifications, land availability and DISCOM connection/headroom evidence. Clause 12(7) specifies at least two 240 kW chargers for the long-range/heavy-duty provision." M:134-135; R:23; verified MoP clauses 11-12. |
| 9 | **Are the district assignments and national boundary depiction authoritative? Does exact RTO reconciliation prove them?** | "No. Reconciliation proves totals, not jurisdictional allocation. The current geometry is geoBoundaries ADM2 2021, with renamed units and Mumbai City/Suburban combined. The crosswalk needs an official check, and boundary compliance has not been established by removing the basemap." M:55,165-167; `mh_district_gap.py:10-23`; `thought_node.md:127,196`. |
| 10 | **What happens if VAHAN or an operator endpoint fails during the live demonstration?** | "The design uses cached snapshots with visible source dates; there are already static national/Maharashtra outputs. Fully offline operation, including vendored map assets, remains an explicit stage-5 exit test, not something this review verified. We should demonstrate the fixed snapshot and freshness warning rather than silently substitute invented live data." R:25,50; M:6,143; `eval/run_all.sh`. |

## E. Ministry-facing relevance and missing constraints

| Concern | Specific evidence or omission | Cheapest ministry-credible response |
|---|---|---|
| **BEE is an integration partner, not evidence of a nonexistent national system.** | M:26 acknowledges the registry but omits a particularly relevant provision: clause 13(2)(i)(b) of the [MoP 2024 guidelines](https://www.beeindia.gov.in/WriteReadData/L45218/2841453721548450.pdf), printed p.10, says BEE will provide open APIs restricted to non-confidential information. I opened and extracted this PDF. | Request endpoint/schema, permissible fields, update cadence and access terms via the appropriate channel; attach a deadline and no-access fallback. A network timeout neither disproves API availability nor proves coverage. Do not promise that BEE/UEI will be "near-complete" (R:56). |
| **Budget outlay and announced charger targets are not state allocations or sanctioned projects.** | M:50 quotes the 2024 PM E-DRIVE targets; R:58 postpones allocation what-ifs. FC P4-P5 supports those historical announcements, not current eligibility, subsidy treatment, sanctioned locations or remaining budget. | Version the applicable scheme guidance; distinguish announced, sanctioned, installed and operational assets. Add cost, land, upstream power and responsible-agency fields. Current allocation/eligibility details remain **UNVERIFIED in this review**; do not fabricate them. |
| **Public supply must mean usable, accessible capacity.** | `fetch_overture.py:15-17,25-34` admits brand-name matches outside the charging category and retains operating status; `mse.py:40-43` then uses only id, coordinates and name. These steps do not verify that a brand-labelled office is a publicly accessible operating charger. | Stratify a hand audit by source, name-rule/category, urbanity and matches; retain status, access restrictions, connector compatibility, port count and deliverable kW. Unknown status is not evidence of availability. |
| **DISCOM feasibility is not a decorative flag.** | M:135/R:23 propose a grid-readiness flag, without an evidential contract. MoP clause 11(3), printed p.8, explicitly connects planning to land, transformers and feeders. | Use `verified / unknown / infeasible` with evidence/date, not inferred readiness from an OSM substation point. Route finalists for connection assessment; mark recommendations provisional without headroom/connection-cost evidence. |
| **Norm compliance requires the right geography and equipment.** | M:47-49/134 abbreviate the norms. Verified clause 11 refers to state-notified urban areas, both road sides, and designated heavy-duty routes; clause 12(7), printed p.9, requires at least two chargers of at least 240 kW for that fast-charging provision. | Test notified urban grids and directed, reachable road segments; include both carriageways and vehicle-compatible equipment. Do not treat every charging POI as satisfying a 100 km heavy-duty gap. If the prototype covers national highways only, label that subset rather than all highways/major roads. |
| **Battery swapping, depots and private charging cannot be postponed while claiming all-segment requirements.** | M:43/55 includes these distinctions and an all-segment boundary, but R:57 puts swapping and depots under future expansion. | Separate segments and charging modes in the MVP's assumptions/output, even with broad sourced ranges. Do not transfer e-2W/3W registrations directly into e-4W public fast-charger requirements. Distinguish stock, location of use and through-traffic. |
| **There is public energy evidence beyond station counts.** | I opened the [CEA December 2025 EV PCS Monthly Power Consumption Report](https://cea.nic.in/wp-content/uploads/ev_charging_rep/2026/04/EV_Report__Dec_2025.pdf). Printed pp.4-5 separate non-heavy-duty PCS, heavy-duty PCS and other-than-PCS energy by state and DISCOM/utility. For example, Maharashtra's December total is 36.52 MU. The report explicitly says missing reports are unavailable data, not zero. M's planned-data table does not include this source. | Use this partial aggregate evidence as an independent plausibility check on segment/mode energy totals. It is **not** a station locator, a complete census, charger-level utilisation or proof of uptime. Preserve the reporting-coverage caveat. |
| **Need should not be validated merely against incumbent deployment.** | `architecture/components.md`, C8, proposes rank correlation with observed site density; C10 proposes AUC for where stations are subsequently added. Those outcomes can reflect private profitability or policy choices rather than unmet public need. | Keep them as behavioural secondary checks. Evaluate energy/service outcomes, accessibility and equity separately, using public energy aggregates or an independent audit where possible. Agree a service objective before comparing siting algorithms on the same assumed demand surface. |
| **Map and jurisdiction compliance need evidence, not a basemap switch.** | M:165-167 admits an unverified crosswalk and non-SoI-certified geometry; `thought_node.md:196` calls "no third-party basemap" boundary compliance. The geometry does not change merely because a raster layer is removed. | Track boundary provenance/vintage, coordinate system and reviewed national depiction; verify RTO jurisdiction mappings and display merged units explicitly. I have not established legal compliance or a legal requirement for a particular certificate; consult the authoritative requirements rather than treating certification wording as proof. |
| **Access and redistribution rights are separate from technical access.** | M:62/155-157 lists replayed VAHAN requests and mixed source licences. Public visibility and attribution alone do not establish all bulk-access or redistribution permissions. | Maintain source-specific access/licence obligations, freshness, caching and failure policies; quarantine records that cannot be redistributed. The current proposal should name an owner for these checks instead of assuming all future feeds are available. |

For source-verification transparency: direct reopens of PIB 2086533 and 2151390 returned 403 here, so I rely on the identified FC quotations and committed annex tables for those claims, not a fresh successful page read. The [official PM E-DRIVE landing page](https://pmedrive.heavyindustries.gov.in/) opened but served the original scheme-period description, not verified current allocation guidance. An attempted DST geospatial-guidelines page returned no usable substantive text, so no legal rule is inferred from it.

The roadmap is achievable only with scope control. R stages 3 and 4 overlap after exams while requiring land/grid data, routing, optimisation, API/scenarios and compliant mapping. Make Gaussian-process disaggregation (R:33) a stretch, not a dependency. Name owners and a public-data-only fallback; require service/cost outcomes, not just a nicer rank order or an optimiser beating random locations.

## F. Exact wording and traceability corrections

The number-rendering mechanism is valuable. It cannot detect a wrong denominator, a conditional interval presented as validated, or a source quote applied to the wrong claim. `check_docs.py:64-65` accepts a numerical token merely because it occurs in FC; that is not claim-level provenance.

| Artifact and location | Wording a reader could misread | More defensible wording or correction |
|---|---|---|
| ADR:7; M:17-26 | "Official counts disagree with each other." | "Published counts differ in date, source and potentially definition." Growth across different dates is not by itself disagreement or official error. Distinguish release date from an explicitly stated observation date. |
| M:26 | "no official series gives locations" | "The three official snapshots we ingested do not supply station coordinates." Do not universalise a limited search, especially given BEE's registry/API provision. |
| M:33-35,76,146 | "3,336 distinct sites"; "open data shows 11.4% of stations" | "3,336 candidate site clusters under the 150 m linkage rule; 11.4% of the older official reference count." Public-site eligibility and linkage accuracy are not yet established. |
| M:59; `architecture/components.md` C3/C8/C11/C12 | "We built 14 components" | "We defined 14 components and implemented the listed baselines." Normalisation is drafted, and demand, siting and API components are marked planned. |
| M:68; ADR:62 | "independent capture"; "needs lists that are independent" | Describe modelled pairwise dependence and untestable residual/three-way dependence. Separate data provenance from statistical independence. |
| M:73-75 | Median estimate 0.58 times official; "pre-registered"; "The causes are..." | Report median absolute log error 0.844 and 17/23 fit availability too; provide the prior protocol or remove "pre-registered"; call the proposed causes hypotheses, not identified explanations. |
| M:84 | "Chhattisgarh is the only state with official district counts"; "its 28 districts" | "The only district annex we have obtained; evaluated on 28 harmonised 2021-boundary units." Explain 270/271 stations and the imputed zero; no nationwide exclusivity claim has been established. |
| M:78,82,93,147; ADR:65 | "validated"; "honest intervals" | "Exploratory conditional allocation compared with one state annex; interval design informed by that comparison." Report 23/28 inclusion without implying Maharashtra calibration. |
| M:105 | "29% more accurate" | "29.5% lower state-weighted WAPE than last-12-month persistence on the stated overlapping retrospective split." Do not equate this with significance or 2030 accuracy. |
| M:107 | "3,598,002"; "other methods give 3.56-3.60 million"; national "error ... on average" | Keep the exact computational result in the evidence table, but headline approximately 3.60 million; label method spread explicitly, and say mean **absolute** national relative error on the three selection years. Fix the Ladakh inconsistency. |
| M:128; R:11 | "Maharashtra would need 3,641 more stations" | "Gross positive district benchmark additions, without relocating surplus capacity"; not a statewide net deficit, energy requirement or budget request. |
| M:133 | "public kWh per day / (kW x utilisation)" | Include hours/day and define utilisation, deliverable power and the energy measurement boundary; round physical equipment appropriately only after calculation. |
| M:140,155 | "Official counts are held out from the estimators." | State roles separately: C5 external comparator; other-state training totals and target-total constraint for small-area allocation; target district distribution benchmark. |
| M:55,119; R:13 | "current boundaries"; "Nagpur (most underserved)" | "2021 district geometry with stated aliases and a combined Mumbai unit"; "highest model-imputed registration-pressure ratio, requiring verification." |
| R:31,42,56 | "capture-recapture ... validated"; "all inputs are small"; BEE/UEI "become near-complete" | "Evaluated and failed the present screen"; laptop sufficiency demonstrated only for the present workload; future-source coverage and full nationwide routing/refresh cost remain unverified. |
| L:18,51; `thought_node.md:71,77` | "Only ~2%" visible; novelty "still to search"; "Most teams will have static or synthetic data"; broader "India's first" pitch | Scope 2% to OSM or update the three-list reference index; reconcile the completed search log; delete unsupported competitor predictions; narrow the novelty pitch as in C. |

The team-information placeholders at **M:4** are acceptable in a working draft, not a submitted document. The official brief requires Team Name, Team ID, Institution and Contact Details and restricts submission to the team leader. Filling them and registering on time is an administrative dependency, not a research result.

## Issues

Severity is contextual: **blocker** prevents an actual submission; **major** materially changes a scientific claim or planning decision; **minor** is a narrower wording/interpretation correction. No finding requires abandoning the Round-1 proposal.

1. **blocker (submission only)** -- `deliverables/round1-methodology.md:4`: required team details remain TBD. **Fix:** team leader supplies the required information after registration and before submission; do not treat the current draft as submission-ready.
2. **major** -- `components/adoption_forecast/autoresearch/eval_monthly.py:26-31`; M:95-105: DEV and HOLDOUT share target observations. **Fix:** purge overlapping development horizons, lock selection, report dependence and retrospective status, and reserve future observations for untouched evaluation; do not transfer the result to 2030.
3. **major** -- `components/access_gap/small_area.py:8-9,61-87`; M:78-93,147: one-state allocation/interval development is called validated uncertainty. **Fix:** label conditional ranges and ecological transport assumptions, freeze the recipe and obtain an independent audit before claiming transferable calibration.
4. **major** -- `components/access_gap/small_area.py:104-125`; `eval/results/cg_district_validation.csv`: district truth changes geography, drops one station, imputes an unreported zero and mixes predictor vintages. **Fix:** publish the crosswalk/270-of-271 accounting, preserve missing labels, align dates and rescore/sensitivity-test harmonised known targets.
5. **major** -- `components/census_completeness/mse.py:94-137`; `eval/results/c5_mse_by_state.csv:4,7,11`: non-estimable/degenerate fits and failed-bootstrap selection produce misleadingly precise intervals. **Fix:** explicit eligibility/convergence diagnostics and abstention, report failed draws, and prohibit these intervals from planning outputs.
6. **major** -- `components/census_completeness/mse.py:81-137`; `eval/results/c5_mse_summary.json`; M:68-75: near-tied model choices imply approximately 28,471 versus 80,833 sites, but the CI fixes one model. **Fix:** publish model/linkage sensitivity, state the zero-three-way-interaction assumption and label conditional uncertainty; retain the planning-use prohibition.
7. **major** -- M:26,33-35,75-76,146; ADR:7,62: a mixed-vintage/reference-count comparison is presented as measured completeness and a diagnosed failure mechanism. **Fix:** use a reference-coverage index, distinguish release/as-on dates and units, and present dependence/heterogeneity as hypotheses pending a matched-universe audit.
8. **major** -- `components/access_gap/mh_district_gap.py:38-58`; M:119-128; R:13: demand-imputed supply generates an assumption-driven shortage ranking. **Fix:** rename it registration pressure, distinguish data gaps from service gaps, show allocation/ranking sensitivity and use independent segment/mode/service evidence before ranking investments.
9. **major** -- M:133-136; R:23; `architecture/components.md` C8/C10/C11: requirement sizing omits hours/day and lacks decision-grade service/cost/constraint validation. **Fix:** correct units, define charger versus site capacity, service/queueing targets, budget, public-energy boundary and independent validation outcomes; implement a bounded requirement MVP before optional forecasting sophistication.
10. **major** -- M:140,155; `components/access_gap/small_area.py:61-87,117-119`: official counts are not universally held out. **Fix:** document training, target-total constraint, model-selection and evaluation roles separately for each estimator.
11. **major** -- `components/adoption_forecast/nowcast.py:28-30`; `eval/results/c9_nowcast_2026.csv:37`: Ladakh's selected annual forecast is below observed YTD. **Fix:** forecast a non-negative remaining-year increment and add actuals; add an invariant check and regenerate dependent summaries.
12. **minor** -- `components/adoption_forecast/nowcast.py:34-43`; M:107: reported nowcast errors come from the three method-selection years; the correctly described method spread should not acquire an uncertainty interpretation downstream. **Fix:** label selection-period errors, report the fourth-quarter residual and mean absolute national error, and keep scenarios separate from prediction intervals.
13. **major** -- M:47-55,134-135; R:23-24,46-58; `thought_node.md:196`: roadmap safeguards are too weak for ministry-facing grid, corridor, scheme and map claims. **Fix:** evidence-backed grid/land status, directed-road and heavy-duty-equipment checks, current scheme/version/access obligations, reviewed boundary/jurisdiction provenance, named owners and a no-new-feed fallback. Use the verified BEE API provision and partial CEA energy tables without assuming completeness.
14. **minor** -- M:75; ADR:27; `components/census_completeness/mse.py:168-183`: the gate wording obscures multiplicative error, excluded states and protocol chronology. **Fix:** print the exact rule, availability 17/23 and inclusion 8/17, add interval usefulness requirements, and remove "pre-registered" unless an earlier freeze is produced.
15. **minor** -- M:128; R:11; `components/access_gap/mh_district_gap.py:46-47,69`: 3,641 gross district additions is presented like a statewide net requirement. **Fix:** label the no-reallocation benchmark and distinguish it from the roughly 3,621 statewide comparison; avoid rounding inputs before allocation.
16. **minor** -- M:146; `research/fact-check.md` novelty log; `thought_node.md:77`: limited search evidence supports a scoped application claim, not demonstrated priority or a wholly novel census methodology. **Fix:** use the wording in C, cite adjacent work and retain the dated query/candidate log.
17. **minor** -- M:59,84,105; R:31,42,56; L:18,51; `thought_node.md:71`: blanket "built", "only", "validated", completeness and competitor assertions outrun their evidence. **Fix:** apply the sentence-level corrections in F and distinguish rendered numerical consistency from claim-level provenance.

---

## Lead triage (Claude Opus 5.5, 4 Oct 2026, 15:00 IST)
| # | Severity | Decision | What changed |
|---|---|---|---|
| 1 | blocker (admin) | **ACCEPTED — routed to the user** | Team fields stay TBD until registration; listed under *Needs from user*. Not a research fix. |
| 2 | major | **ACCEPTED** | v3 evaluator purges the overlap (DEV targets end Dec 2024; HOLDOUT from Jan 2025); the holdout is labelled retrospective; prospective test frozen. |
| 3 | major | **ACCEPTED** | District allocation is called "conditional" everywhere; one-state test and post-hoc interval revision disclosed. |
| 4 | major | **ACCEPTED** | Point-in-time rescoring with the accounting published (31 rows, 271 stations, 27 labelled 2021 units, 1 unlabelled kept missing, Sarangarh-Bilaigarh split 0.5/0.5). |
| 5 | major | **ACCEPTED** | Abstention rule; failed bootstrap draws reported; no capture–recapture number enters planning outputs. |
| 6 | major | **ACCEPTED** | Model/linkage sensitivity published; the no-three-way-interaction assumption stated; no national total quoted. |
| 7 | major | **ACCEPTED** | "Reference-coverage index"; dates and units distinguished; dependence/heterogeneity stated as hypotheses. |
| 8 | major | **ACCEPTED** | Maharashtra reframed: ranked on observed registration pressure and visible supply; modelled supply shown only as conditional; ranking sensitivity (Spearman 0.66) reported; "verify first" replaces "most underserved". |
| 9 | major | **ACCEPTED** | Sizing formula now includes 24 h and deliverable kW; the bounded requirement MVP (three MoP norms, energy cross-checked against CEA) precedes forecasting extras in the roadmap. |
| 10 | major | **ACCEPTED** | §2.7 states the role of official counts per estimator. |
| 11 | major | **ACCEPTED** | Nowcast = YTD + non-negative remainder, with an invariant check; Ladakh now equals its YTD. |
| 12 | minor | **ACCEPTED** | Errors labelled as selection-period; Oct–Dec increment error reported. |
| 13 | major | **ACCEPTED** | Roadmap §3 safeguards: owners (roles), BEE open-API request with deadline, grid status field, heavy-duty 2 × 240 kW rule, scheme versioning, boundary provenance, no-new-feed fallbacks. Clause 13(2)(i) and the CEA report were re-opened and added to the fact-check (P7–P9). |
| 14 | minor | **ACCEPTED** | "Pre-registered" removed; the rule's chronology is stated in code; availability (5/22) and inclusion (4/5) reported. |
| 15 | minor | **ACCEPTED** | Statewide net benchmark (3,621) is distinguished from gross district additions; neither is called a requirement. |
| 16 | minor | **ACCEPTED** | Novelty narrowed to a search-qualified application claim. |
| 17 | minor | **ACCEPTED** | Sentence-level corrections applied (defined vs built components, "candidate clusters", no competitor predictions, no "first" pitch). |
