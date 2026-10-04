# Independent engine, evaluation, and claims review

- **Reviewer:** GPT-6 Sol (`gpt-6-sol`)
- **Date:** 2026-10-04 (IST)
- **Commit reviewed:** `fa316b6db17b01fa7c7c9a3e1f08dc85430cbcf3` (`origin/main` after fetch/rebase)
- **Scope:** `ev-c2-green-auto-lca/`, the official Challenge 2 brief, and the repository playbook. This is a code, reproducibility, and claims audit, not an ISO critical review or independent validation of the input studies.

**Bottom line:** The five specified numerical claims reproduce. The car's green "harmonized" badge does not: AR5 vehicle/fuel factors are combined with AR6 electricity. The default dashboard also gives a different answer in its what-if panel without moving the slider. **Findings: 1 critical, 4 major, 3 minor.**

## Numbered findings

1. **Critical - the car decision case falsely passes the gas-basis harmonization gate.** `components/lca_engine/greenauto/db.py:28-32` maps both `CO2e-AR5-GWP100` and `CO2e-AR6-GWP100` to the same `"GWP100"` family. `components/lca_engine/greenauto/engine.py:129-140,180-183` then treats that family as proof of harmonization; a stage containing AR6 GWP factors even takes their family in preference to its CO2-only generation factor. The car glider, battery and gasoline factors are AR5 (`data/factors/vehicle_car.yaml:88,108,234-253`), but the central electricity stage uses AR6 CH4/N2O GWP (`data/factors/energy_upstream.yaml:473,491`; `data/vehicles/case2_cars_sedan.yaml:119-130`). **Repro:** `python3 eval/eval.py` from this folder, then inspect `eval/results/summary.md:94-101`: `car_in2026_avg_co2e` says `_harmonized_`; the live dashboard says "Gas basis harmonized: all emission factors on GWP100." `car_in2026_cea_operating_margin` has the same false positive. **Fix:** Preserve the exact characterization method/version for each contributing factor and require consistency (including treatment of the CO2-only base and incomplete upstream boundary); call these results partial, unharmonized GHG indicators until converted to one documented method.

2. **Major - the dashboard silently substitutes CO2-only electricity into CO2e scenarios.** In `components/dashboard/build.py:76-85`, the default slider is set to `ef_gen = 0.675` kg CO2/kWh, but `whatif()` subtracts the scenario's **CO2e** electricity stage and adds `elec * ef_gen / (1-td)` as **CO2-only**. Opening the generated page with no interaction shows 2W "EV 38.9 ... 39.5% lower" beside the scenario card's 39.8 / 38.1%; selecting `car_in2026_avg_co2e` shows "EV 199.2 ... 11.9% lower" beside 203.5 / 10.0%. I reproduced both in the browser, not just by inspecting JS. Separately, the fixed warning in `build.py:59` incorrectly says the default 2W CO2e case has "no CH4/N2O or upstream", although its expression adds both combustion gases and coal-mine CH4 (`data/vehicles/case1_2w_scooters.yaml:126-137`). **Fix:** Recompute the *same* scenario's CO2e electricity formula at a new generation factor (or explicitly switch to, and label, a CO2-only sensitivity); at the reset point the what-if must equal the card. Generate warning text from the actual scenario basis/boundary rather than a single CO2-only string.

3. **Major - inherited, inactive inputs contaminate provenance and importance.** `_resolve()` updates inherited parameters without removing those no longer used by overridden stage expressions (`components/lca_engine/greenauto/engine.py:58-72`). The car BEV inherits ICCT's lifetime `grid` factor, then replaces the electricity stage with `ef_gen`/T&D (`data/vehicles/case2_cars_sedan.yaml:62-75,86-94,112-130`); the E0 scooter likewise retains the old `ttw` factor (`data/vehicles/case1_2w_scooters.yaml:109-117`). `run_scenario()` still samples all parameter IDs and gives the unused ICCT car grid factor nonzero importance (about `0.0000592` in the committed car decision run; `engine.py:147-149,180`). The dashboard's "every input used" table also lists it (`components/dashboard/build.py:71-73`); I confirmed its presence in the rendered car scenario. **Minimal repro:** `PYTHONPATH=components/lca_engine python3 -c 'from greenauto.engine import load_scenarios; p=next(p for p in load_scenarios()["car_in2026_avg_co2e"].products if p.id=="bev"); print(p.params["grid"], p.stage_params("electricity_production_wtt"))'`; the first ID is absent from the second list. **Fix:** Derive active record IDs from parsed stage expressions after overrides, reject or explicitly mark unused bindings, and feed only active IDs to sampling, sensitivity, provenance, and the dashboard.

4. **Major - "India-specific share" is not a share of the footprint.** `components/lca_engine/greenauto/engine.py:161-178` sums absolute *elasticities* of inputs whose pedigree geography score is 1, divides by the sum of all absolute elasticities, and `components/dashboard/build.py:68` presents the result as "India-specific share." In the car decision run the BEV badge reads **91%**, yet its EU-factor glider and China-factor battery stages alone contribute **37.91/203.51 = 18.63%** of the total (`data/factors/vehicle_car.yaml:77-112`; `data/vehicles/case2_cars_sedan.yaml:62-75`). Even treating every other stage as India-specific would cap an *impact* share at 81.37%. For the petrol car the badge is 92% although the EU-factor production stage is 13.91% of its total. **Repro:** Open the generated dashboard, select `car_in2026_avg_co2e`, and compare the BEV's 91% badge with its production-stage values in `eval/results/scenarios_full.json`. **Fix:** Rename the existing statistic "share of absolute input elasticity with geographical pedigree = 1"; separately calculate any claimed India-sourced impact share using an explicit stage/input provenance rule. Do not label a sensitivity statistic as a share of life-cycle emissions.

5. **Major - jury-facing drafts and the journal still present an earlier, different case.** `thought_node.md:14` and `deliverables/round1-methodology.md:3-11,59-70` headline 62.9/39.7 g/km and 36.9% lower on a CO2-only/E0 case; `eval/results/summary.md:57-62` now headlines 64.3/39.8 and 38.1% on the partial-CO2e/ICCT-blend case. The draft also gives old OM/BM percentages (14.0/55.2 versus 16.2/56.4 in `summary.md:36-48`), calls the present grid term CO2-only, and says the fact-sheet figure matches Table 1 to <=0.03 g/km (`round1-methodology.md:34`), although their **totals** differ by roughly 1 g/km because the fact-sheet bars include maintenance (`data/benchmarks/icct_india_factsheet_2021_fig2.yaml:1-11`; only overlapping stage rows approximately reconcile). The journal's "Now" component count also remains 23 records/8 sources versus 124/19 in `summary.md:4`. These are historical drafts, not evidence that the current run changed invisibly, but submitting or narrating them alongside the dashboard would be contradictory. **Repro:** `rg -n '62\.9|39\.7|36\.9|64\.3|39\.8|38\.1' thought_node.md deliverables/round1-methodology.md eval/results/summary.md`. **Fix:** Generate the submission numbers from the current committed run, distinguish any retained historical CO2-only calculation as a sensitivity, correct the fact-sheet wording, and refresh "Now" before a jury walkthrough.

6. **Minor - `range95` does not reproduce its stated 95% endpoints.** `components/lca_engine/greenauto/db.py:125-128,131-146` sets `sigma = ln(high/low)/3.92` but centers the lognormal at the published `value`, not at the geometric midpoint of `low` and `high`. For the IPCC gasoline NCV record (`data/factors/fuels.yaml:3-13`), a 500,000-draw sample with seed 77 gave **[43.15, 45.48]** as its 2.5th/97.5th percentiles, not the source's **[42.5, 44.8]**; `range95` also occurs for the IPCC gasoline CO2 factor (`fuels.yaml:32`). **Repro:** `PYTHONPATH=components/lca_engine python3 -c 'import numpy as np; from greenauto.db import FactorDB; r=FactorDB.load()["fuels.petrol.ncv.ipcc2006"]; print(np.percentile(r.sample(500000,np.random.default_rng(77)),[2.5,97.5]))'`. This affects the E0 sensitivity, not the two decision headline totals. **Fix:** Fit a distribution to both published quantiles (a split-lognormal if the published central value must remain its median), or explicitly relabel the stored interval as an approximate width rather than promising to honor both endpoints.

7. **Minor - tied/constant samples acquire fictitious rank-correlation importance.** The double-`argsort` ranks in `components/lca_engine/greenauto/engine.py:106-125` arbitrarily order equal values. **Minimal repro:** `PYTHONPATH=components/lca_engine python3 -c 'import numpy as np; from greenauto.engine import spearman; print(spearman(np.ones(8),np.arange(8)))'` prints `1.0`, whereas a constant input has no rank association. LCIA method records are deliberately fixed across draws (`components/lca_engine/greenauto/db.py:136-137`) and inherited inactive records can also enter `_importance`, so this can assign noise to the data-gap ranking. **Fix:** Give ties average ranks and return zero for a constant series; exclude inactive/fixed inputs before normalizing squared correlations.

8. **Minor - the published C7 contracts still advertise the pre-v2 names.** `architecture/contracts/contracts.py:94-112` requires `dqi`, `variance_share`, and `variance_share_of_reduction`; `components/lca_engine/greenauto/engine.py:176-179,189-205` actually emits `dq_score` and `importance`. This will break consumers built to the advertised typed interface; it also calls the statistic "share of rank-variance" despite the engine correctly documenting normalized squared Spearman as *not* a variance decomposition. **Repro:** `rg -n 'dqi|variance_share|dq_score|importance' architecture/contracts/contracts.py components/lca_engine/greenauto/engine.py`. **Fix:** Align the contract types with actual result shapes and add a round-trip/schema test for real engine output.

## Independently checked headline claims

I read the cited record values and rebuilt these formulas without importing `greenauto` or `eval`. Values below are g per vehicle-km after multiplying kg per vehicle-km by 1,000. The exact committed Monte Carlo run is `python3 eval/eval.py` (`N=10,000`, seed `20261004`); my separate 150,000-draw run used seed `771122`, sampling shared record IDs once per draw and excluding inactive parameters. Its 2W reduction interval was **[31.99, 43.11]%**, versus the committed **[32.0, 43.2]%**; its car interval was **[-10.13, 25.47]%**, versus **[-10.2, 25.6]%**. These differences are consistent with simulation noise. They are model-conditional uncertainty intervals, not calibrated empirical coverage or proof of a universal EV advantage.

| Claim | Verdict | Independent calculation and qualification |
|---|---|---|
| **(a) 2W: 64.3 vs 39.8; 38.1% lower [32.0, 43.2]%** | **CONFIRMED as model arithmetic** | ICE: `108.5*5.2/120000*1000 + 1 + 2.1/100*(0.64+2.15)*1000 = 64.2917`. EV: `96.9*5.2/120000*1000 + 2.9*68/120000*1000 + 1 + 3.915/100*0.841676*1000 = 39.7940`. Reduction `1-39.7940/64.2917 = 38.104%`. The result **is not harmonized**: 20-year-methane vehicle production, AR5 fuel/battery factors and partial AR6 grid. `data/vehicles/case1_2w_scooters.yaml:53-91,119-137`; `eval/results/summary.md:57-62`. |
| **(b) Car: 226.2 vs 203.5; 10.0% lower [-10.2, 25.6]%** | **CONFIRMED as model arithmetic** | Petrol: `998*5.2/165000*1000 + 5 + 6.8/100*(0.64+2.15)*1000 = 226.1721`. BEV: `998*4.7/165000*1000 + 23*68/165000*1000 + 4 + 19.2/100*0.841676*1000 = 203.5085`; reduction `10.021%`. The reported interval spans no saving, `P(BEV lower) = 0.806`, and the `_harmonized_` badge is wrong (finding 1). Do not present 10% as a settled finding for current Indian cars. `data/vehicles/case2_cars_sedan.yaml:7-75,112-130`; `summary.md:94-101`. |
| **(c) Verification MAPE: 0.06% 2W and about 1.0% car** | **CONFIRMED, as arithmetic verification only** | 2W inputs implied by Table 1 give **60.9017** and **37.5436** versus published 60.9/37.5: MAPE **0.05950%**. Four car totals from tabulated inputs are **226.1721, 239.4521, 224.0667, 185.1387** versus 228/245/226/185: MAPE **0.99914%**. Inputs/targets mostly come from the same ICCT papers; neither MAPE is independent predictive validation. `eval/eval.py:30-43`; `data/benchmarks/icct_2w_india_2021_table1.yaml:1-32`; `data/benchmarks/icct_global_2021_india_sedan.yaml:1-25`. |
| **(d) ICCT Table 1 / footnote documentation gap** | **CONFIRMED, without assigning blame** | Table 1 scooter WTT `12.8/(0.64*1000)*100 = 2.00` L/100 km; TTW `43.4/(2.17*1000)*100 = 2.00` L/100 km; electric WTT `31.7/767*100 = 4.133` kWh/100 km. The opened ICCT PDF Table 1/footnote 9 instead prints **2.2 L/100 km** and **3.7 kWh/100 km** for scooters. Its TTW factor is printed as `2.17 g/L`, apparently a unit typo: the physically usable conversion is **2.17 kg/L**, as the record notes. Rounding, labels, or unstated assumptions may contribute; this is not evidence that ICCT's conclusion is wrong. `data/benchmarks/icct_2w_india_2021_table1.yaml:12-32`; `data/factors/fuels.yaml:91-115`. |
| **(e) India grid 0.693 busbar / 0.842 meter** | **CONFIRMED as partial CO2e, not a full life-cycle EF** | `0.675*(1+(1*29.8+1.5*273)/(95.8*1000)) + 0.672*(2717/3755)*(1.565/1000)*0.67*29.8 = 0.693289 kg CO2e/kWh`; `0.693289/(1-0.1763) = 0.841676` at the meter. Coal-mine CH4 and coal combustion CH4/N2O are included; mining energy, fuel transport, gas supply and infrastructure are not. The 17.63% T&D figure includes commercial losses. `components/lca_engine/greenauto/grid.py:37-84`; `data/factors/energy_grid_co2e.yaml:1-90`; `data/factors/energy_upstream.yaml:1-575`. |

For an independent *re-run of the intervals* (not the engine's sampler), run this from `ev-c2-green-auto-lca/`. It reads the committed YAML and evaluates the eleven committed stage expressions with a separate resolver/sampler; the explicit central formulas above do not rely on the scenario expressions:

```bash
python3 - <<'PY'
import ast, copy, math
from pathlib import Path
import numpy as np, yaml
R = {r["id"]: r for f in Path("data/factors").glob("*.yaml") for r in yaml.safe_load(f.read_text())}
S = {s["id"]: s for f in Path("data/vehicles").glob("*.yaml")
     for s in yaml.safe_load(f.read_text())["scenarios"]}
P = {"reliability": (1,1.05,1.1,1.2,1.5), "completeness": (1,1.02,1.05,1.1,1.2),
     "temporal": (1,1.03,1.1,1.2,1.5), "geographical": (1,1.01,1.02,1.02,1.1),
     "technological": (1,1,1.2,1.5,2)}
N = 150000
def resolve(sid):
    s = S[sid]
    if "base" not in s: return copy.deepcopy(s["products"])
    ps = resolve(s["base"])
    for p in ps:
        ov = s.get("overrides", {}).get(p["id"], {})
        p["params"].update(ov.get("params", {}))
        p["stages"].update(ov.get("stages", {}))
    return ps
def draw(r, rng):
    v = float(r["value"]); u = r.get("uncertainty", {})
    lo, hi, d = u.get("low"), u.get("high"), u.get("distribution", "none")
    if r["layer"] == "method": return np.full(N, v)
    if d == "uniform" and lo is not None: return rng.uniform(lo, hi, N)
    if d == "range" and lo is not None:
        return rng.triangular(lo, v, hi, N) if lo <= v <= hi else rng.uniform(lo, hi, N)
    if d == "triangular" and lo is not None: return rng.triangular(lo, v, hi, N)
    if d == "normal" and lo is not None: return rng.normal(v, (hi-lo)/3.92, N)
    sigma = (math.log(hi/lo)/3.92 if d in ("range95", "lognormal") and lo and hi else
             math.sqrt(math.log(1.05)**2 + sum(math.log(P[k][r["pedigree"][k]-1])**2
                                               for k in P))/2)
    return v*np.exp(rng.normal(0, sigma, N))
def names(p):
    return {n.id for e in p["stages"].values() for n in ast.walk(ast.parse(e, mode="eval"))
            if isinstance(n, ast.Name)}
def total(p, vals):
    local = {k: vals[p["params"][k]] for k in names(p)}
    return 1000*sum(eval(e, {"__builtins__": {}}, local) for e in p["stages"].values())
for sid in ("in2026_avg_co2e", "car_in2026_avg_co2e"):
    ps = resolve(sid)
    used = {p["params"][k] for p in ps for k in names(p)}
    rng = np.random.default_rng(771122)
    vals = {rid: draw(R[rid], rng) for rid in sorted(used)}
    ice, bev = ps[0], next(p for p in ps if p["powertrain"] == "BEV")
    a, b = total(ice, vals), total(bev, vals)
    print(sid, np.percentile(100*(1-b/a), (5, 95)))
PY
```

## Engine and dimensional audit

All **eleven distinct** stage expressions in the two scenario YAML files have consistent *mass-per-vehicle-km* dimensions with the stated record units; `run_scenario()` converts kg to g by multiplying each stage by 1,000 (`engine.py:154-158`). That is a units check, not a finding that every stage shares one climate-characterization basis.

| Expression(s), by stage | Dimensional reduction |
|---|---|
| `mass * prod_int / life`; `glider * prod_int / life` | kg vehicle * kg CO2e/kg vehicle / km = kg/km |
| `kwh * bat_int / life` | kWh * kg CO2e/kWh / km = kg/km |
| `maint` | Recorded kg CO2e/km |
| `fuel / 100 * wtt`; `fuel / 100 * ttw` | L or kg per 100 km -> per km; times kg CO2e/L or kg CO2e/kg = kg/km |
| `fuel / 100 * ttw + slip * gwp_ch4 / 1e6` | CNG slip is mg CH4/km; GWP converts gas mass, and 1e6 converts mg to kg |
| `fuel / 100 * dens * ncv * ef / 1000` | L/km * kg/L * MJ/kg * g CO2/MJ / 1000 = kg CO2/km |
| `elec / 100 * grid` | kWh/km * kg CO2e/kWh = kg/km |
| `elec / 100 * ef_gen / (1 - td)` | kWh/km * kg CO2/kWh / dimensionless delivery fraction = kg CO2/km |
| `elec / 100 * (ef_gen*(1+(ch4c*gwp_ch4+n2oc*gwp_n2o)/(co2c*1000)) + coal_sh*hr/gcv*cmm/1000*dens*gwp_ch4) / (1-td)` | `co2c` g/MJ * 1000 = kg CO2/TJ; CH4/N2O numerator kg CO2e/TJ, so their ratio is dimensionless. `hr/gcv` is kg coal/kWh, `cmm/1000` is m3 CH4/kg coal, and density * GWP gives kg CO2e/m3. Both grid addends are kg/kWh before multiplying by kWh/km. |

`Record.sample()` matches its stated rule for in-bound `range` (triangular around published mode), `uniform`, `triangular`, and `normal`; otherwise it uses a lognormal with published value as median and either the pedigree sigma or the `range95`/`lognormal` width. GWP records (`layer: method`) stay fixed. Current metadata has 107 `none`, 10 `range`, 3 `uniform`, 2 `range95`, and 2 `normal` records; the two `normal` records are fixed method factors. Finding 6 is the exception to the claim that both `range95` endpoints are honored. A clone of the petrol scooter product sharing all record IDs produced exactly zero paired-draw differences (`n=300`, all reported difference quantiles zero): sampling once per shared ID in `engine.py:147-149` works. Scenario `base`/`overrides` produces the expected central formulas, subject to finding 3's inactive bindings. The +1% finite-difference elasticities and absolute-elasticity-weighted pedigree score match direct recomputation (car BEV `dq_score = 1.89011565`); this is a screening score, **not** a validated data-quality rating. `importance` sums to one by construction and is normalized squared Spearman, **not** a variance decomposition; see finding 7.

## Provenance spot-check

**Selection:** `random.Random(20261004).sample(sorted(record_ids), 10)` over all 124 factor records. For each, `source_id` resolves in the 19-source registry; the claimed locator matches the cited table/annex/page in the retrieved PDF; `verifier.load_text(local_copy)` plus `verifier.quote_found(quote, text)` finds literal, ordered fragments after whitespace normalization. PDF page numbers here are *physical file pages* and can differ from printed page numbers.

| Record ID | Source ID / claimed locator | PDF page(s) with first literal fragment | Quote |
|---|---|---:|---|
| `energy.electricity.in_delhi.td_loss_share.fy2023_24` | `loksabha-usq842-2025`, FY2023-24 Annexure | 3 | PASS |
| `energy.electricity.in.grid_bm.fy2025_26` | `cea-co2-baseline-v22`, Table S (printed p. 1) | 6 | PASS |
| `method.gwp100.n2o.no_ccfb.ipcc_ar5` | `ipcc-ar5-wg1-ch8`, Table 8.7 (printed p. 714) | 56 | PASS |
| `energy.electricity.in_orissa.td_loss_share.fy2023_24` | `loksabha-usq842-2025`, Annexure | 3 | PASS |
| `energy.upstream.coal_mining.ch4_density.ipcc2006` | `ipcc-2006-v2-ch4-fugitive-emissions`, printed p. 4.11 | 12, 19, 27 | PASS |
| `energy.electricity.in_meghalaya.td_loss_share.fy2023_24` | `loksabha-usq842-2025`, Annexure | 3 | PASS |
| `energy.upstream.coal_mining.underground_post_mining.ch4.ipcc2006.average` | `ipcc-2006-v2-ch4-fugitive-emissions`, Eq. 4.1.4, printed p. 4.12 | 12 | PASS |
| `energy.electricity.in_goa.td_loss_share.fy2023_24` | `loksabha-usq842-2025`, Annexure | 3 | PASS |
| `use.car.sedan.gasoline.l_per_100km.icct2021` | `icct-global-lca-2021`, Table A.8 (printed p. 70) | 76 | PASS |
| `method.gwp100.n2o.ipcc_ar6` | `ipcc-ar6-wg1-ch7`, Table 7.15 (printed p. 1016) | 95 | PASS |

All 10/10 sampled source links, locators, and PDF text matches passed. The verifier metric tests quote presence, **not** whether each value, unit, year, and table column was extracted correctly; retain human review. To reproduce the selection and matches from a fetched clean copy, run:

```bash
PYTHONPATH=components/ingestion python3 - <<'PY'
from pathlib import Path
import random, yaml
from verifier import load_text, quote_found
src = {s["id"]: s for f in Path("data/sources").glob("*.yaml")
       for s in yaml.safe_load(f.read_text())}
rec = {r["id"]: r for f in Path("data/factors").glob("*.yaml")
       for r in yaml.safe_load(f.read_text())}
for rid in random.Random(20261004).sample(sorted(rec), 10):
    r = rec[rid]; s = src[r["source_id"]]
    print(rid, r["locator"], quote_found(r["quote"], load_text(s["local_copy"])))
PY
```

## Reproducibility from a clean checkout

Commands (from the repository root, then from the indicated project directory):

```bash
git worktree add --detach /tmp/ev-c2-clean origin/main
cd /tmp/ev-c2-clean/ev-c2-green-auto-lca
python3 -m pytest components/lca_engine/tests -q
python3 eval/eval.py
python3 components/dashboard/build.py
diff -u <(git show HEAD:ev-c2-green-auto-lca/eval/results/summary.md | sed '1d') <(sed '1d' eval/results/summary.md)
python3 data/fetch/fetch_sources.py
python3 components/ingestion/autoresearch/eval.py
```

**Outcome:** 14/14 engine tests passed; evaluation printed `{"verification_mape_pct_2w": 0.06, "verification_mape_pct_car": 0.999}`; dashboard built as a self-contained 326 KB page and rendered in a browser without a JS exception (the browser requested a missing favicon, HTTP 404, with no app impact). Summary comparison after removing only the first commit-provenance line had **no diff**. The committed line names `c86cef7`, while the regenerated line names the clean checkout's `fa316b6`; `latest.json` and the dashboard footer differ only in that commit string. All 18 registered raw files downloaded; PDF quote-verifier evaluation returned **scalar 1.0**, **104/104** positive quotes found and **0/208** digit-perturbed negatives accepted (`false_accept_rate: 0.0`). This confirms reproducibility on this host with installed Python packages and `pdftotext`; it does not independently validate physical LCA accuracy or guarantee that future downloads are byte-identical. The temporary checkout was removed after this review.

## Lead decisions (4 Oct 2026, 10:40 IST)
| # | Decision | Reason / action |
|---|---|---|
| 1 | **ACCEPTED** (critical) | AR5 and AR6 are now separate gas-basis families (`GWP100-AR5`, `GWP100-AR6`). The CO2e grid adders in both case studies use AR5 GWPs (CH4-fossil 30, N2O 265; records from IPCC AR5 WG1 Ch. 8), matching ICCT's AR5 vehicle and fuel factors, so the car case is harmonized on AR5 GWP100. The 2W case stays flagged. The grid service gets a `gwp` option (AR6 default); AR5 vs AR6 changes the grid factor by < 0.01 %. Regression test added. |
| 2 | **ACCEPTED** | The what-if slider is seeded with the scenario's own effective factor (CO2e when the scenario is CO2e) and labels its gas basis, so the default view equals the card. Checked in a browser after the rebuild. |
| 3 | **ACCEPTED** | `load_scenarios` drops inherited parameters no stage uses (the car BEV no longer carries ICCT's lifetime `grid`). Test added. |
| 4 | **ACCEPTED** | Replaced by `india_footprint_share`: the share of the total from stages whose dominant emission factor is Indian (BEV sedan 0.81). The dashboard label says "India-specific emission factors: x % of footprint". Test added. |
| 5 | **ACCEPTED** | The methodology, roadmap, ADR and thought node were rewritten to the CO2e central case. Results blocks are rendered from `latest.json`, and `eval/check_docs.py` (in the test suite) fails on stale numbers or on prose that lacks the current headline. |
| 6 | **ACCEPTED** | `range95`/`lognormal` with value strictly inside the bounds now use a two-piece lognormal: median = published value, 2.5th/97.5th percentiles = stated bounds (IPCC NCV test reproduces 42.5/44.8 within 0.5 %). |
| 7 | **ACCEPTED** | Spearman uses average ranks (`scipy.stats.rankdata`); a constant input gives 0.0. Test added. |
| 8 | **ACCEPTED** | `architecture/contracts/contracts.py` updated to the v2 names (`dq_score`, `dq_dims`, `india_footprint_share`, `gas_basis_shares`, `importance`, `Comparison.vs/p_lower`, `ScenarioResult.harmonized`). |
| Claims a–e | Verdicts accepted | (a) and (b) are reported as model arithmetic, with the car interval spanning no saving stated explicitly; (c) is reported as arithmetic verification; (d) is worded without blame; (e) is labelled partial CO2e. |

Accepted 8, rejected 0.
