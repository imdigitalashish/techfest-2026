# Code, reproducibility and evaluation review (gpt-6-sol)

Reviewed at commit `cc9e0e5fbab26a59a79f8d559085f78192da1085` on 2026-10-04, 13:55 IST. This is an advisory review of the cached snapshot, not a claim that a later live VAHAN "Till Today" query will return the same cumulative value. I changed no source, result, or deliverable file. Unless noted, commands below run from `ev-c1-infra-map-india/`; paths in findings are relative to that directory. "Blocker" means the associated accuracy/security claim should not be used in a final submission before correction, not that the current draft is unusable.

## Reproduction log

1. Synced this worktree with `git fetch origin && git rebase origin/main` before the audit. Copied the lead's `.data/` and `.cache/` **locally** with `cp -R /Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-bookish-sniffle/ev-c1-infra-map-india/.data /Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-bookish-sniffle/ev-c1-infra-map-india/.cache ev-c1-infra-map-india/`. `cd ev-c1-infra-map-india && nice -n 10 uv venv .venv && UV_HTTP_TIMEOUT=300 nice -n 10 uv pip install --python .venv/bin/python -r pyproject.toml` succeeded; relevant uv output (verbatim):

   ```text
   Using CPython 3.12.12
   Creating virtual environment at: .venv
   Activate with: source .venv/bin/activate
   Resolved 35 packages in 176ms
   Installed 35 packages in 258ms
   ```
   No network download of a dataset was required. The review timestamp comes from `TZ=Asia/Kolkata date '+review_time=%Y-%m-%d %H:%M IST'` -> `review_time=2026-10-04 13:55 IST` (recorded during the audit).

2. `nice -n 10 sh eval/run_all.sh` ran each analysis, map builder, latest-number collector, and document renderer. The final `check_docs.py` exited **1**, as expected for the existing Round-1 drafts. Its stdout (trailing whitespace in the table header removed for Markdown):

   ```text
                count    sum
   source
   pib2086533     36  25202
   pib2118894     35  26367
   pib2151390     36  29277
   METRIC dev_median_abs_log_err=0.3489
   secondary dev_mean_abs_log_err=0.5294 n_dev=12 n_holdout=11 params={'mode': 'calib', 'radius_m': 150, 'min_matches': 3}
   HOLDOUT median_abs_log_err=0.4172 mean=0.4734
   METRIC dev_wape=0.1775
   secondary dev_median_smape=20.12 dev_national_err=[0.247, 0.005] params={'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}
   HOLDOUT 2024->2025 wape=0.1097 median_smape=17.39 national_err=+0.020
   METRIC dev_wape=0.1470
   secondary dev_national_err_mean=+0.098 dev_wape_range=[0.073,0.252] params={'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}
   HOLDOUT wape=0.1572 by_origin=[0.11, 0.127, 0.162, 0.229] national_err=[0.02, -0.103, -0.123, -0.223]
   national: 36 states (unmatched []), 3336 sites; maharashtra: 35 districts, 435 sites; sizes 0.91 / 0.25 MB
   latest.json: 194 keys
   deliverables/round1-methodology.md:20: number '10000' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:20: number '1014' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:22: number '2.05' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:22: number '31.8' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:22: number '7.8' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:26: number '1,468' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:26: number '1,469' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:26: number '10,550,090' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:26: number '2,356,971' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:26: number '8.05' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:28: number '1,085' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:28: number '1,123' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:35: number '1,185,108' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:49: number '61%' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:49: number '70%' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:66: number '62%' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-methodology.md:66: number '0.4' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-roadmap.md:19: number '1%' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-roadmap.md:47: number '2%' is neither rendered from a run nor in research/fact-check.md
   deliverables/round1-roadmap.md:55: number '1,468' is neither rendered from a run nor in research/fact-check.md
   ```

   This is a **draft-document failure**, not a numerical difference caused by rerunning the pipeline. Verification immediately afterward:

   ```sh
   git status --short && git diff --stat && git diff --exit-code && echo 'all tracked results and rendered documents byte-identical; worktree clean'
   ```
   ```text
   all tracked results and rendered documents byte-identical; worktree clean
   ```

3. An independent raw-table and parsed-PIB reconciliation (not just reading the summary JSON):

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   from pathlib import Path
   import pandas as pd
   R=Path('.data/vahan/raw'); cols=['ELECTRIC(BOV)','PURE EV']
   for y in ['A','2025']:
    d=pd.read_csv(R/f'nat_state_fuel_{y}.csv');print('national',y,'BEV',int(d[cols].to_numpy().sum()),'rows',len(d))
   d=pd.read_csv(R/'nat_state_fuel_A.csv').set_index('row_label')
   for code,state in [('MH','MAHARASHTRA'),('CG','CHHATTISGARH')]:
    paths=list(R.glob(f'rto_{code}_*_class_fuel_A.csv'))
    n=sum(int(pd.read_csv(p)[cols].to_numpy().sum()) for p in paths)
    print(code,'state_BE V'.replace(' ',''),int(d.loc[state,cols].sum()),'RTO_BE V'.replace(' ',''),n,'files',len(paths))
   p=pd.read_csv('components/charger_ingest/data/official_pcs_statewise.csv')
   print('PIB2151390',int(p.loc[p.source=='pib2151390','pcs_total'].sum()),'rows',len(p[p.source=='pib2151390']))
   PY
   ```
   ```text
   national A BEV 10550090 rows 36
   national 2025 BEV 2356971 rows 36
   MH state_BEV 1185108 RTO_BEV 1185108 files 61
   CG state_BEV 218859 RTO_BEV 218859 files 30
   PIB2151390 29277 rows 36
   ```
   The cached PIB page itself says "29,277 nos. of public EV charging stations", not just the parser's CSV; the local page-text check (run from the project root) was:

   ```sh
   python3 - <<'PY'
   from pathlib import Path
   import re, html, hashlib
   sources={'PIB2151390':('fdd0f25dfec5.html','29,277'),'PIB2086533':(hashlib.sha1(b'https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2086533').hexdigest()[:12]+'.html','25,202')}
   for name,(file,number) in sources.items():
    raw=(Path('.cache/sources')/file).read_text(errors='ignore')
    plain=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',raw)))
    i=plain.find(number)
    print(name,'text_excerpt:',plain[max(0,i-75):i+100] if i>=0 else 'NOT FOUND')
   PY
   ```
   ```text
   PIB2151390 text_excerpt: 56PM by PIB Delhi As per the inputs received from Ministry of Power (MoP), 29,277 nos. of public EV charging stations (EVCS) have been installed in the country. State-wise bre
   PIB2086533 text_excerpt: rk in the country. As per the information received from Ministry of Power, 25,202 EVPCS are installed in the country. The number of EVPCS installed State/UT wise is at ANNEXUR
   ```
   The parsed August PIB state names also join one-to-one to VAHAN. Executed:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import pandas as pd
   p=pd.read_csv('components/charger_ingest/data/official_pcs_statewise.csv'); p=p[p.source=='pib2151390']
   s=pd.read_csv('eval/results/state_gap_baseline.csv')
   print('PIB_unique_labels',p.state.nunique(),'VAHAN_joined',s.pib_state.notna().sum(),'unique_matched_PIB',s.pib_state.nunique(),'no_unmatched',s.pib_state.isna().sum()==0)
   PY
   ```
   ```text
   PIB_unique_labels 36 VAHAN_joined 36 unique_matched_PIB 36 no_unmatched True
   ```
   See `components/charger_ingest/official_pcs.py:14-42` for annexure splitting/deduplication and `eval/baseline_state_gap.py:19-45` for the fuel definition and join.

4. **One live VAHAN query only:** the command below fetched the State x Fuel CY2025 export and compared it to the copied raw CSV. This tests the current JSF ids and the cached annual BEV total; it does **not** independently live-verify the changing cumulative "Till Today" total or the fuel-filtered monthly endpoint.

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import sys
   import pandas as pd
   sys.path.insert(0, 'components/vahan_ingest')
   from vahan_client import Vahan
   bev = ['ELECTRIC(BOV)', 'PURE EV']
   live = Vahan().query('State', 'Fuel', '2025').set_index('row_label')
   cached = pd.read_csv('.data/vahan/raw/nat_state_fuel_2025.csv').set_index('row_label')
   a = live[bev].sort_index(); b = cached[bev].sort_index()
   print('live_rows=',len(live),'cached_rows=',len(cached),'same_states=',a.index.equals(b.index))
   print('live_bev=',int(a.to_numpy().sum()),'cached_bev=',int(b.to_numpy().sum()))
   print('max_state_bev_difference=',int((a-b).abs().sum(axis=1).max()))
   print('live_all=',int(live.TOTAL.sum()),'cached_all=',int(cached.TOTAL.sum()))
   PY
   ```
   ```text
   live_rows= 36 cached_rows= 36 same_states= True
   live_bev= 2356971 cached_bev= 2356971
   max_state_bev_difference= 0
   live_all= 29291488 cached_all= 29291488
   ```
   `openpyxl` also emitted its benign "Workbook contains no default style" warning on stderr.

5. Cache identity, to make the copied-input qualification checkable. Executed:

   ```sh
   shasum -a 256 .data/vahan/raw/nat_state_fuel_A.csv .data/vahan/raw/nat_state_fuel_2025.csv .cache/sources/fdd0f25dfec5.html .data/chargers/osm_india.csv .data/chargers/ocm_india.csv .data/chargers/overture_india.csv
   ```
   ```text
   78e6c07825ce4cc7d532abb211e0ad2cc074e22000cf178774030963e1de76fd  .data/vahan/raw/nat_state_fuel_A.csv
   6c2b4566fbe036a5eaa370fdf76785bbcb9441bd88b5c13e00b3b0effa095420  .data/vahan/raw/nat_state_fuel_2025.csv
   85b2c49c3fa20fdbb74ec366e36864951ef80b379c978d3bfdf842e634383e7d  .cache/sources/fdd0f25dfec5.html
   20ec695824e20416b11ec05c4ad34032ce2f562e7bbc335f63901661d859983b  .data/chargers/osm_india.csv
   e06d43bbdc70dd1c8dfb162fcbd99716bb97f4e5b6c52e216fc45402e479c2c4  .data/chargers/ocm_india.csv
   6b76d272092bbc8f3131bed27ec7b5c30d72a956ef75be4ac0c63cadb656171b  .data/chargers/overture_india.csv
   ```

## Numbered issues

1. **BLOCKER - A linked "site" can contain two records from one source, and one plausible split flips the national C5 answer.** `components/census_completeness/mse.py:58-77,83-90,120-136`. Each *pair* is mutual nearest neighbour, but unrestricted connected components can chain those pairs. The actual linked CSV contains a component with two OCM showroom POIs with different names. This does not prove which physical sites they represent; it shows that site identity is not enforced before constructing one binary capture history for the component. Evidence (read-only, no edits):

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import sys,json,pandas as pd
   sys.path.insert(0,'components/census_completeness')
   from mse import hav
   r=pd.read_csv('eval/results/c5_linked_records.csv');dup=r.groupby(['site','src']).size();d=dup[dup>1]
   print('same_source_components',d.index.get_level_values('site').nunique(),'site_161_sources',r.loc[r.site==161,'src'].tolist())
   q=r[(r.site==161)&(r.src=='ocm')]
   print('site_161_ocm_names',q.name.tolist(),'distance_m',round(float(hav(q[['lat','lon']].to_numpy(),q[['lat','lon']].to_numpy())[0,1]),1))
   s=pd.read_csv('eval/results/c5_mse_by_state.csv');j=json.load(open('eval/results/c5_mse_summary.json'))
   print('validated_states',j['states_evaluated'],'missing_estimates_ge100',int(((s.official_pcs_aug2025>=100)&s.N_hat.isna()).sum()),'median_abs_log',j['median_abs_log_ratio_mse'],'coverage',j['ci90_coverage_of_official'],'passed',j['passes_state_check'])
   PY
   ```
   ```text
   same_source_components 1 site_161_sources ['osm', 'ocm', 'ocm', 'ovt']
   site_161_ocm_names ['MG Motor B.U. Bhandari Showroom', 'Garve Hyundai'] distance_m 110.9
   validated_states 17 missing_estimates_ge100 5 median_abs_log 0.844 coverage 0.471 passed False
   ```

   The following is a **sensitivity experiment, not a corrected ground truth**: split just that ambiguous triple-list cluster into an OSM+OCM and an OCM+Overture site. Refit unchanged code:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 nice -n 10 .venv/bin/python - <<'PY'
   import sys,numpy as np
   sys.path.insert(0,'components/census_completeness')
   from mse import fit,MODELS,design
   base=np.array([952,1720,65,501,15,76,7.]);alt=base+np.array([0,0,1,0,0,1,-1.])
   print('observed_cells',len(base),'full_model_parameters',design(('OC','OV','CV')).shape[1])
   for label,c in [('original',base),('plausible_two_site_split',alt)]:
    candidates=sorted([(v[1],m,c.sum()+v[0]) for m in MODELS if (v:=fit(c,m)) is not None])
    for aic,m,n in candidates[:2] if label=='original' else candidates[:1]:
     print(label,'model','+'.join(m) or 'indep','aic',round(aic,2),'Nhat',round(n,1))
   PY
   ```
   ```text
   observed_cells 7 full_model_parameters 7
   original model OC+OV+CV aic -39539.45 Nhat 80832.7
   original model OC aic -39538.59 Nhat 28471.0
   plausible_two_site_split model OC aic -39553.49 Nhat 28482.9
   ```
   **Fix:** inspect and label this cluster; constrain linkage so a site cannot contain competing POIs from the same source without affirmative evidence (also check names/addresses/operator and component diameter). Publish linkage sensitivity rather than a single C5 national estimate until the match labels are audited.

2. **MAJOR - The C5 interval conditions on a data-selected, potentially saturated model.** `components/census_completeness/mse.py:83-137,155-182`. The full model has as many parameters as observed capture cells; the AIC runner-up in issue 1 has nearly the same AIC but a very different estimate. At `mse.py:126-135`, the bootstrap fixes `m_best` instead of rerunning linkage/model selection, and invalid bootstrap fits are discarded. The issue-1 command/output gives the model alternatives and the evaluated-state coverage; the latter was computed by the `eval/results/c5_mse_summary.json` generated by `run_all.sh`. The code's `passes_state_check = false` **is correct under its stated rule**: median absolute log error and interval coverage in issue 1 both miss the criteria at `mse.py:181-182`. The issue is treating the conditional percentile interval as a calibrated uncertainty interval despite model/linkage uncertainty and excluding states with no fit. **Fix:** include linkage uncertainty and AIC selection inside the resampling, report fit failures and model sensitivity alongside intervals, and withhold nominal coverage claims until they calibrate on time-aligned held-out sites.

3. **MAJOR - The C5 benchmark compares different vintages and populations.** `components/census_completeness/mse.py:38-44,153-169`; `components/charger_ingest/fetch_osm.py:55-69`. The location lists include explicitly non-public OSM records while the official denominator is *public* stations from an older release. These are known caveats in `components/census_completeness/autoresearch/program.md:19-22`, but they preclude calling the state check a same-date accuracy test. Evidence:

   ```sh
   python3 - <<'PY'
   import json,pandas as pd
   p=pd.read_csv('components/charger_ingest/data/official_pcs_statewise.csv')
   print('official_PIB2151390_as_on',p.loc[p.source=='pib2151390','as_on'].iloc[0])
   print('CG_PIB2086533_as_on',p.loc[p.source=='pib2086533','as_on'].iloc[0])
   print('OSM_base_as_on',json.load(open('.data/chargers/osm_india_raw.json'))['osm3s']['timestamp_osm_base'])
   print('CG_RTO_snapshot_fetched_at',json.load(open('.data/vahan/raw/rto_CG_15_class_fuel_A.json'))['fetched_at'])
   PY
   ```
   ```text
   official_PIB2151390_as_on 2025-08-01
   CG_PIB2086533_as_on 2024-12-20
   OSM_base_as_on 2026-10-04T00:26:35Z
   CG_RTO_snapshot_fetched_at 2026-10-04T13:33:36
   ```
   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import pandas as pd
   x=pd.read_csv('.data/chargers/osm_india.csv')
   print('OSM_access_private',int((x.access=='private').sum()),'access_no',int((x.access=='no').sum()))
   print('source_file_osm_licence_column','license' in x.columns)
   print('linked_file_licence_column','license' in pd.read_csv('eval/results/c5_linked_records.csv',nrows=1).columns)
   PY
   ```
   ```text
   OSM_access_private 10 access_no 3
   source_file_osm_licence_column True
   linked_file_licence_column False
   ```
   All of those explicitly non-public OSM rows survive the C5 point-in-polygon filter, not just the raw ingest:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import pandas as pd
   raw=pd.read_csv('.data/chargers/osm_india.csv')[['source_id','access']]
   linked=pd.read_csv('eval/results/c5_linked_records.csv');osm=linked[linked.src=='osm'].merge(raw,on='source_id',how='left')
   print('linked_osm_private',int((osm.access=='private').sum()),'linked_osm_no',int((osm.access=='no').sum()),'linked_osm_records',len(osm))
   PY
   ```
   ```text
   linked_osm_private 10 linked_osm_no 3 linked_osm_records 599
   ```
   This does **not** invalidate the narrower statement "fails the specified comparison"; it limits what one may infer from that failure. **Fix:** align source vintages/definitions with the official snapshot; exclude private/non-public or unverified-status records from the public-supply model (or report separate strata); reserve an independent, contemporary validation set.

4. **BLOCKER - Chhattisgarh's retrospective district validation uses future covariates and its district labels to set the allocation total.** `components/access_gap/small_area.py:97-126`; the analogous Maharashtra application at `components/access_gap/mh_district_gap.py:22-40` also mixes current RTO/open-site distributions with an older official supply total. The state-level fit **does exclude Chhattisgarh** (`small_area.py:61-66,118-119`); the leak is in validation inputs: RTO `*_A.csv` and the current linked open sites, plus `total = truth.sum()` after dropping the newly split district rather than the independent official state total. Evidence:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import sys,json,pandas as pd
   sys.path.insert(0,'components/access_gap')
   import small_area as S
   s=json.load(open('eval/results/small_area_summary.json'))['chhattisgarh_validation']
   off=S.official('pib2086533')['chhattisgarh']
   r=pd.read_csv('eval/results/cg_district_validation.csv')
   print('CG_dec2024_state_official',int(off),'CG_district_truth_used',int(r.official_dec2024.sum()))
   print('CG_2024_Nov_state_BEV',int(S.bev_cum_at(2024,11)['chhattisgarh']),'CG_RTO_A_BE V'.replace(' ',''),int(r.bev_till_today.sum()))
   print('reported_wape',s['methods']['small_area_model']['wape'],'spearman',s['methods']['small_area_model']['spearman'],'ci90_covered',int(((r.official_dec2024>=r.sa_lo.round())&(r.official_dec2024<=r.sa_hi.round())).sum()),'of',len(r))
   PY
   ```
   ```text
   CG_dec2024_state_official 271 CG_district_truth_used 270
   CG_2024_Nov_state_BEV 119268 CG_RTO_A_BEV 218859
   reported_wape 0.41 spearman 0.841 ci90_covered 23 of 28
   ```
   The WAPE formula, Spearman alignment, and coverage count are implemented as described (`small_area.py:122-126`); the test cannot support a *historical predictive* claim when features were collected later. **Fix:** obtain point-in-time district RTO and open-site snapshots for the official date and use the independently published state total; map the post-2021 district's count back to its parents with a documented rule. Until then call this a **current-covariate conditional allocation sanity check**, not an out-of-time validation or calibrated predictive interval.

5. **MAJOR - Byte-identical results require an untracked local cache and an unlocked environment.** `eval/run_all.sh:1-20`, `pyproject.toml:1-11`, `components/vahan_ingest/fetch_vahan.py:38-47`. This worktree had no cached inputs until they were copied; the script reads them directly. The dependency manifest declares lower bounds without a tracked resolution lock. Executed from the repo root:

   ```sh
   git ls-files ev-c1-infra-map-india/.data ev-c1-infra-map-india/.cache | wc -l | awk '{print "tracked_cached_inputs=" $1}'
   git ls-files ev-c1-infra-map-india | grep -E '(^|/)(uv.lock|poetry.lock|pdm.lock|requirements.lock|Pipfile.lock)$' | wc -l | awk '{print "tracked_lockfiles=" $1}'
   ```
   ```text
   tracked_cached_inputs=0
   tracked_lockfiles=0
   ```
   The local run is reproducible **with the copied inputs** (hashes above); it is not portable or independently verifiable from a fresh clone, and a new "Till Today" fetch changes the input. **Fix:** publish a versioned, licence-compatible input manifest/snapshot or an accessible archive with checksums, data-as-of and fetch provenance; add an environment lock. Make the pipeline verify expected input hashes for a frozen evaluation instead of silently accepting a newer scrape.

6. **MAJOR - VAHAN malformed/empty exports become valid cached data.** `components/vahan_ingest/vahan_client.py:155-188`; `components/vahan_ingest/fetch_vahan.py:38-47,104-119`. The parser coerces corrupt numeric cells to zero, and an empty table returns successfully; the fetcher then writes a CSV and treats any existing path as complete forever. In-memory synthetic workbook test (no source or cached file edited):

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   from io import BytesIO
   import pandas as pd
   import sys
   sys.path.insert(0,'components/vahan_ingest')
   from vahan_client import parse_export
   rows=[['VAHAN Export',None,None,None],['S No','State','Fuel','TOTAL'],[None,None,'ELECTRIC(BOV)',None],['1','TEST STATE','not-a-number','123']]
   def parse(sheet):
    buf=BytesIO();pd.DataFrame(sheet).to_excel(buf,header=False,index=False)
    return parse_export(buf.getvalue())
   r=parse(rows)
   print('garbled_number_becomes_zero',r[['row_label','ELECTRIC(BOV)','TOTAL']].to_dict('records'))
   print('empty_body_accepted_rows',len(parse(rows[:-1])))
   PY
   ```
   ```text
   garbled_number_becomes_zero [{'row_label': 'TEST STATE', 'ELECTRIC(BOV)': 0, 'TOTAL': 123}]
   empty_body_accepted_rows 0
   ```
   The cached BEV monthly/yearly totals did reconcile for the full years checked, so this is a **fail-open ingestion bug**, not an assertion that these particular outputs are corrupt. **Fix:** reject empty exports, missing fuel/month fields, nonnumeric values, inconsistent row/grand totals, and unexpected row counts; validate a cached CSV before skipping it, save via an atomic temporary write, and log/retry rejected queries. Specifically verify the fuel-filter query against an annual fuel pivot during refresh.

7. **MAJOR - "Frozen" C9 eval does not enforce origin isolation or a blind holdout.** `components/adoption_forecast/autoresearch/eval_monthly.py:15-41`, `components/adoption_forecast/autoresearch/run_variants_monthly.py:19-35`, `components/adoption_forecast/nowcast.py:51-59`. The current forecaster receives only pre-origin columns and excludes the partial October, which is correct. But unrestricted code in the editable `forecaster.py` runs in the same process and can read the complete raw series; the four holdout scores are also computed and committed for every candidate. A **hypothetical adversarial model injected in memory, not an accusation against the current code**, demonstrates the evaluator cannot detect reading future labels:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -W ignore - <<'PY'
   import sys,numpy as np,pandas as pd
   sys.path.insert(0,'components/adoption_forecast/autoresearch')
   import eval_monthly as E
   b,a=E.load_monthly('bev'),E.load_monthly('all')
   print('last_month',b.columns[-1],'oct_partial_excluded',pd.Period('2026-10','M') not in b.columns)
   print('actual_dev',round(np.mean([E.score(b,a,o)[0] for o in E.DEV]),4),'actual_hold',round(np.mean([E.score(b,a,o)[0] for o in E.HOLD]),4))
   def oracle(hist_b,hist_a,params=None):
    o=hist_b.columns[-1];return b.loc[:,o+1:o+12].sum(axis=1)
   E.forecaster.forecast_12m=oracle
   print('oracle_dev',np.mean([E.score(b,a,o)[0] for o in E.DEV]),'oracle_hold',np.mean([E.score(b,a,o)[0] for o in E.HOLD]))
   PY
   ```
   ```text
   last_month 2026-09 oct_partial_excluded True
   actual_dev 0.147 actual_hold 0.1572
   oracle_dev 0.0 oracle_hold 0.0
   ```
   **Fix:** freeze predictions before a separate trusted evaluator reveals holdout labels; retain a new unseen holdout for final claims and enforce/probe model input access. Treat the published holdout scores as already viewed, not as an indefinitely reusable blind test. The WAPE denominators and per-origin averaging themselves are correct (`eval.py:20-25`, `eval_monthly.py:28-41`).

8. **MAJOR - `check_docs.py` can pass fabricated claims even after the draft failures are cleared.** `eval/check_docs.py:20-23,32,49-62`; `eval/make_latest.py:18-21`. A heading is wholly skipped, while any number found *anywhere* in `research/fact-check.md` is accepted regardless of the claim's meaning. This read-only, in-memory test adds a made-up heading and misuses a real fact-check number in an unrelated forecast statement; the checker outputs **exactly the same errors** as before:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   from pathlib import Path
   from unittest.mock import patch
   from contextlib import redirect_stdout
   from io import StringIO
   import sys
   sys.path.insert(0,'eval')
   import check_docs
   real_read=Path.read_text
   def run():
    out=StringIO()
    with redirect_stdout(out): status=check_docs.main()
    return status,out.getvalue()
   baseline=run()
   def fake_read(self,*args,**kwargs):
    text=real_read(self,*args,**kwargs)
    if self.name=='round1-methodology.md':
     return text+'\n# National chargers are 987,654; this is a made-up heading\nThe 2027 model predicts 29,277 chargers (fabricated context).\n'
    return text
   with patch.object(Path,'read_text',fake_read): modified=run()
   print('baseline_status',baseline[0],'modified_status',modified[0])
   print('added_wrong_claims_detected',baseline[1]!=modified[1])
   print('fact_check_contains_29277', '29,277' in real_read(Path('research/fact-check.md')))
   PY
   ```
   ```text
   baseline_status 1 modified_status 1
   added_wrong_claims_detected False
   fact_check_contains_29277 True
   ```
   The separate document-check command/output in the reproduction log shows the current drafts fail for legitimate missing markers. **Fix:** check headings and all numeric claims, bind manually verified numbers to claim/context identifiers rather than substring occurrence, require explicit result markers for measured values, and require an explicit scoped exception for illustrative or genuinely unverified statements.

9. **MAJOR - Raw third-party site names can execute markup/scripts in the generated map.** `components/dashboard_map/build_map.py:15,32-40,60-65`; `components/dashboard_map/template.html:26,79-81`. The builder inserts `json.dumps` of untrusted charger names inside an inline `<script>`, without escaping `<`; a station name containing a closing script tag can terminate it. A second path feeds the name into MapLibre `setHTML` without escaping. This is a code-path vulnerability, **not evidence of a malicious name in the current cache**. Offline proof and provenance-column inspection:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   from pathlib import Path
   import csv,json
   s='</script><script>console.log(1)</script>'
   raw=json.dumps({'name':s},separators=(',',':'))
   tpl=Path('components/dashboard_map/template.html').read_text()
   print('raw_json_contains_closing_script','</script>' in raw)
   print('template_embeds_sites_inside_script', 'SITES=__SITES__' in tpl and '<script>' in tpl)
   print('untrusted_point_name_inserted_into_HTML', 'p.name' in tpl and '.setHTML(' in tpl)
   print('linked_csv_header',next(csv.reader(open('eval/results/c5_linked_records.csv'))))
   print('raw_osm_has_license', 'license' in next(csv.reader(open('.data/chargers/osm_india.csv'))))
   print('raw_ocm_has_provider', 'data_provider_id' in next(csv.reader(open('.data/chargers/ocm_india.csv'))))
   PY
   ```
   ```text
   raw_json_contains_closing_script True
   template_embeds_sites_inside_script True
   untrusted_point_name_inserted_into_HTML True
   linked_csv_header ['src', 'source_id', 'lat', 'lon', 'name', 'state_key', 'site']
   raw_osm_has_license True
   raw_ocm_has_provider True
   ```
   **Fix:** encode JSON for an inline HTML script context (at least `<` as a Unicode escape), and create map popups with DOM nodes/textContent or HTML-escape every external name and attribute. Test both generated pages with a deliberately hostile *synthetic* station name.

10. **MINOR - Tracked OSM-derived point data loses licence and record provenance.** `components/charger_ingest/fetch_osm.py:69`, `components/charger_ingest/fetch_ocm.py:21`, `components/census_completeness/mse.py:40-44,150`, `components/dashboard_map/template.html:43,56,81`. Raw OSM rows carry the ODbL notice and OCM rows carry the data-provider id, but `c5_linked_records.csv` retains neither (see issue 9's exact command/output); the popup lists only source names. The map footer does credit OSM generally, which is good, but a recipient of the CSV cannot read per-record terms or original URLs without going back to the sources. **Fix:** preserve source URL/provider/licence and relevant ODbL notices through linkage and into exported derivatives; review share-alike/attribution obligations for redistributed OSM-derived data rather than assuming a generic map footer covers every export.

11. **MINOR - Published district CSV rounds predictions before a reviewer can recalculate its summary metrics.** `components/access_gap/small_area.py:122-126`. The JSON metrics use full-precision allocations, while `cg_district_validation.csv` rounds those values; the CSV alone cannot reproduce every summary value:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
   import json
   import pandas as pd
   r=pd.read_csv('eval/results/cg_district_validation.csv');s=json.load(open('eval/results/small_area_summary.json'))['chhattisgarh_validation']
   n=int(((r.official_dec2024>=r.sa_lo.round())&(r.official_dec2024<=r.sa_hi.round())).sum())
   print('CG_interval_covered',n,'of',len(r),'csv_wape',round((r.small_area_model-r.official_dec2024).abs().sum()/r.official_dec2024.sum(),3),'summary_wape',s['methods']['small_area_model']['wape'],'reported_coverage',s['small_area_ci90_coverage'])
   print('CG_open_share_csv_wape',round((r.open_share-r.official_dec2024).abs().sum()/r.official_dec2024.sum(),3),'reported',s['methods']['open_share']['wape'])
   PY
   ```
   ```text
   CG_interval_covered 23 of 28 csv_wape 0.41 summary_wape 0.41 reported_coverage 0.821
   CG_open_share_csv_wape 0.994 reported 0.995
   ```
   **Fix:** export unrounded predictions/intervals as the evaluation artifact; round only in presentation. Retain the exact target-total and date metadata in the exported table.

## What I verified as correct

- `components/charger_ingest/official_pcs.py:14-42` splits the Chhattisgarh annex from the state annex and deduplicates repeated PIB rows; the cached national PIB text, parsed national total, state-row count, and one-to-one VAHAN join agree (reproduction log and `eval/baseline_state_gap.py:21-40`). The parser prints rather than asserts its expected source totals, so a future malformed source could pass silently; that is a hardening recommendation, **not** a claim that this cache is wrong.
- The raw BEV national sums, Maharashtra and Chhattisgarh RTO-to-state totals match exactly (reproduction log). The Maharashtra crosswalk covers its fetched RTO codes and maps Vasai to Palghar (`components/admin_geo/data/rto_district_MH.csv:58`); the one missing cached Chhattisgarh RTO file is the unassigned police-HQ code, not missing BEV registrations (`components/admin_geo/data/rto_district_CG.csv:30`). The historical Chhattisgarh names map to the available ADM2 boundaries; dropping the newly split district accounts for the one-station denominator difference in issue 4.
- C5's Poisson IRLS/AIC arithmetic reproduces its committed national estimate and the specified state-check failure; it is **the unstable model/linkage/interval interpretation** that needs work, not a discovered arithmetic sign error (issues 1-3).
- `components/adoption_forecast/autoresearch/eval.py:20-34`, `eval_monthly.py:15-41`, `forecaster.py:19-84`, and `nowcast.py:20-59` use pre-origin inputs in the present implementation; monthly October partial data are excluded and DEV/HOLDOUT WAPE are the documented sums of absolute errors divided by actual totals (issue 7's actual-model output). The copied monthly BEV totals reconcile with cached yearly State x Fuel BEV totals for the full years checked. Holdout integrity against future model edits remains a separate problem.
- The Chhattisgarh score uses conventional WAPE and aligned Spearman ranks; its reported interval coverage corresponds to the exported district truth (`small_area.py:122-126`, issue 4's command/output). That verifies **arithmetic**, not the temporal validity of the test.

Additional commands and their exact output supporting the crosswalk, Poisson and filtered-month checks above:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
from pathlib import Path
import pandas as pd
r=Path('.data/vahan/raw')
for c in ['MH','CG']:
 x=pd.read_csv(f'components/admin_geo/data/rto_district_{c}.csv'); raw=pd.read_csv(r/f'rto_list_{c}.csv')
 print(c,'xwalk',len(x),'unique',x.rto_code.nunique(),'listed',len(raw),'unmapped_codes',sorted(set(raw.rto_code)-set(x.rto_code)),'missing_raw',sorted(str(k) for k in x.rto_code if not (r/f'rto_{c}_{k}_class_fuel_A.csv').exists()))
print('MH_Palghar_RTO',pd.read_csv('components/admin_geo/data/rto_district_MH.csv').query('district=="Palghar"').rto_code.tolist())
PY
```
```text
MH xwalk 61 unique 61 listed 61 unmapped_codes [] missing_raw []
CG xwalk 31 unique 31 listed 31 unmapped_codes [] missing_raw ['3']
MH_Palghar_RTO [48]
```

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import sys,numpy as np
sys.path.insert(0,'components/census_completeness')
from mse import fit,MODELS
cells=np.array([40,30,120,20,80,60,240.])
fits={m:fit(cells,m) for m in MODELS}
best=min(fits,key=lambda m:fits[m][1])
print('synthetic_expected_unseen',10,'Poisson_IRLS_unseen',round(fits[()][0],6),'AIC_selected','+'.join(best) or 'indep')
PY
```
```text
synthetic_expected_unseen 10 Poisson_IRLS_unseen 10.0 AIC_selected indep
```

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
from pathlib import Path
import pandas as pd
R=Path('.data/vahan/raw');m='JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split();out={}
for y in range(2020,2026):
 f=pd.read_csv(R/f'nat_state_fuel_{y}.csv').set_index('row_label')
 b=pd.read_csv(R/f'nat_state_month_bev_{y}.csv').set_index('row_label')[m].sum(axis=1)
 out[y]=int((b-f[['ELECTRIC(BOV)','PURE EV']].sum(axis=1)).abs().sum())
print('monthly_vs_annual_BE V_abs_state_error'.replace(' ',''),out)
PY
```
```text
monthly_vs_annual_BEV_abs_state_error {2020: 0, 2021: 0, 2022: 0, 2023: 0, 2024: 0, 2025: 0}
```
