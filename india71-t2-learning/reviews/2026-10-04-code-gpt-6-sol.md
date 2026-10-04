# India@71 Theme 2: code + evaluation review (GPT-6 Sol)

Scope: the synthetic district at source revision `c2caae7`, the method frozen with the
pre-registration at `f6601b9`, and the held-out results committed at `d02cef6`.
This is a review, not a change to the registered method or its results.
All commands below run from `india71-t2-learning/` unless a `git` command is
shown; the latter runs from the repository root.

## Reproduction

- `nice -n 10 python3 eval/coverage_test.py --seeds 101-130 --out /tmp/cov.json`
  returned **174/180 = 0.9666667** coverage for `fh` (Wilson 95%:
  0.92919-0.98464), moderated MAE **2.15676 pp** versus raw **4.30996 pp**,
  mean interval half-width **5.97439 pp**, and mean signed error **+0.53281 pp**.
  The default allocation difference was +0.2333 below-goal children per world
  (95% CI -5.6464 to +6.1131): **no demonstrated allocation gain**.
  A JSON comparison excluding the elapsed-time and command fields printed
  `coverage result fields identical excluding runtime/command: True []`;
  `/tmp/cov.blocks.csv` was **byte-identical** to the committed block CSV.
- To avoid rewriting any project file, I ran the exact
  `nice -n 10 python3 eval/run_eval.py` command inside a temporary
  `git archive HEAD india71-t2-learning` copy. Its
  `eval/results/headline.json`, `eval/results/summary.md`, dashboard HTML/JSON,
  and all four teacher-plan files were **byte-identical** to the committed
  outputs (eight comparisons printed `byte-identical: True`). This reruns
  dashboard, C4, C7, C12 and held-out detection AUC, but *loads* the committed
  five coverage-result JSONs; the default language coverage run above was
  independently rerun, not all secondary coverage runs.
- `python3 -m pytest -q eval/sim components` returned `57 passed in 2.10s`.
  Memory status was 41 before coverage and 40 before the headline run;
  both substantive evaluations used `nice -n 10`.
- `git log f6601b9..HEAD -- components/trust_audit/assurance.py
  eval/coverage_test.py` (with the project prefix from the repository root)
  and the corresponding `git diff --exit-code` returned **no changes**.
  Held-out results were committed after pre-registration. Git cannot prove that
  nobody privately executed those seeds before registration, but there is no
  committed post-result method tuning.
- The `separation_exploratory` code produces **99/180 = 0.55 flagged** and
  **99/99 correctly sided among flagged**, as recorded in `headline.json`;
  this is **not** 99% or 100% classification accuracy on all 180 blocks.
  Issue 11 explains which "district average" it actually uses.

## Correctness and governance issues

1. **[BLOCKING] Caller-provided text can authorize nonselected raw responses.**
   `components/governance/policy.py:17-18,25-27` accepts *any substring*
   `selected_for_audit` in `target_scope` as proof of selection, and returns
   `transform="none"`. Evidence:
   ```bash
   python3 - <<'PY'
   from architecture.contracts.fln_contracts import AccessRequest, AreaLevel, Role
   from components.governance.policy import decide
   d = decide(AccessRequest(role=Role.AUDITOR, actor_scope="AUD",
       resource="raw_responses", target_scope="S1|selected_for_audit=false",
       target_level=AreaLevel.SCHOOL, purpose="audit"))
   print(d.allowed, d.transform)
   PY
   # True none
   ```
   Neither a selection registry nor the target's actual status is checked.
   **Fix:** resolve audit-selection status from a trusted server-side record,
   separate it from the user-supplied scope string, and deny unknown/false
   status; test `false`, fabricated, and unselected targets before any real
   child data is connected.

2. **[MAJOR] The dashboard bypasses small-cell disclosure control.**
   `components/dashboard/core.py:29-37,49-50` emits every input block into
   both HTML and JSON without calling C12; `policy.py:23-24,43-44` requires
   suppression when `n < 10`. Evidence, with all writes confined to a
   disposable temporary directory:
   ```bash
   python3 - <<'PY'
   import json, tempfile
   from pathlib import Path
   import pandas as pd
   from components.dashboard import build_dashboard
   b = pd.DataFrame({"block_lgd":["B01"],"raw":[.5],"estimate":[.5],
       "lo":[.4],"hi":[.6],"n_schools":[1],"n_retested_schools":[1],
       "children":[8]})
   with tempfile.TemporaryDirectory() as d:
       p = build_dashboard(b, {}, Path(d))
       j = json.loads((Path(d)/"block_dashboard_outputs.json").read_text())
       print("B01" in p.read_text(), j["blocks"][0]["children"],
             j["blocks"][0]["estimate"])
   PY
   # True 8 0.5
   ```
   The shipped demo's cells are larger, so this does not alter its current
   numbers; the reusable renderer is nevertheless unsafe for small inputs.
   **Fix:** apply verified C12 authorization/suppression before serializing
   either output, including the JSON companion, and add an `n=8` integration
   test. A policy table passing 36/36 cases is not an integration guarantee.

3. **[MAJOR] C4 held-out classification is given thresholds from its own
   hidden truth.** `eval/sim/world.py:82-87,174-177,244` chooses each world's
   cutpoints from that world's latent `theta_*` quantile; `World.public_view`
   retains them in `cfg` (`world.py:59-74`). The C4 evaluator passes
   `w.cfg[thr_key]` into **both** `bayes_irt` and `adaptive_test`
   (`components/diagnostics/evaluate.py:49,60-61`). Evidence:
   ```bash
   python3 - <<'PY'
   import numpy as np
   from components.diagnostics.engine import _posterior, _level_probs
   from eval.sim.world import make_world
   cfg = {"n_schools":40,"n_clusters":8}
   dev, held = make_world(1,cfg), make_world(101,cfg)
   grid = np.linspace(-4,4,321); changed = 0; delta = []
   for _, child in held.children.sample(n=30,random_state=3).iterrows():
       resp = held.item_responses[(held.item_responses.student_raw_id==child.student_raw_id)
                                  & (held.item_responses.subject=="language")]
       post = _posterior(resp,held.item_bank[held.item_bank.subject=="language"],grid)
       actual = _level_probs(post,grid,held.cfg["read_thresholds"])
       fixed = _level_probs(post,grid,dev.cfg["read_thresholds"])
       changed += int(actual.argmax()!=fixed.argmax())
       delta.append(abs(actual[4]-fixed[4]))
   print(np.round(dev.cfg["read_thresholds"],3),np.round(held.cfg["read_thresholds"],3))
   print(held.public_view().cfg["read_thresholds"]==held.cfg["read_thresholds"])
   print(changed,round(float(np.mean(delta)),4),round(float(np.max(delta)),4))
   PY
   ```
   Output excerpt:
   ```
   [-0.379  0.221  0.771  0.971] [-0.48  0.12  0.67  0.87]
   True
   6 0.0387 0.0938
   ```
   Separately, C4's `WORLD_CFG` omits `ASER2024_GOVT_STD3`
   (`diagnostics/evaluate.py:20`): `make_world(101, WORLD_CFG)` printed
   `C4 world reading/math true shares: 0.25 0.2999`, rather than the
   0.234/0.276 headline calibration. This does **not** leak into the frozen
   trust-assurance coverage test, but does compromise interpretation of the
   C4 headline. **Fix:** learn/freeze cutpoints on development worlds or use
   externally specified assessment cutpoints, never held-out latent ability;
   keep truth-derived thresholds out of `public_view().cfg`, and evaluate
   C4 on the declared calibration (with a fresh independent holdout).

4. **[MAJOR] A missing audit still produces publication-shaped intervals.**
   `components/trust_audit/assurance.py:203-213,226-255,272-279`
   fits using only returned audit rows (even zero), but bootstraps using the
   full *planned* `Design.budget`; missing re-tests are silently treated as
   if the design succeeded. Evidence from a 40-school, two-block synthetic
   world with four selected schools and an empty returned re-test frame:
   ```bash
   python3 - <<'PY'
   from components.trust_audit.assurance import Design, run_assurance
   from components.trust_audit.core import forensic_flags, retest, select_audit
   from eval.sim.world import make_world
   w = make_world(2, {"n_schools":40,"n_clusters":8,"n_blocks":2}); p = w.public_view()
   r = forensic_flags(p.teacher_reports,p.schools,p.item_responses,p.item_bank)
   s = select_audit(p.schools,r,4,seed=19)
   a = retest(w,s,12,seed=33).iloc[:0]
   _,fit,iv = run_assurance(p,r,s,a,Design(budget=4),R=25,seed=55,bias_model="mean")
   print(int(s.selected_for_audit.sum()),fit.n_audited,len(iv),
         iv[["estimate","lo","hi"]].head(1).round(4).to_dict("records"))
   PY
   # 4 0 4 [{'estimate': 0.306, 'lo': 0.1543, 'hi': 0.4908}]
   ```
   `observed_inputs` also fills a missing selected-school inclusion
   probability with 1 (`assurance.py:206-210`). **Fix:** validate exact
   selected/re-tested school IDs, positive sample counts, and a usable
   double-assessed sample; fail explicitly or mark intervals unavailable when
   an audit does not materialize. A deliberately partial design needs its
   *actual* response mechanism in both fitting and bootstrap.

5. **[MAJOR] Recorded risk-PPS "inclusion probabilities" are not the
   sampler's inclusion probabilities.** `components/trust_audit/core.py:120-133`
   computes clipped `prob` and samples a fixed `b` with NumPy's *successively
   renormalized* weighted sampling without replacement. These are different
   probability laws, yet `assurance.py:141,243` uses `1/prob` as an
   Horvitz-Thompson factor. Evidence: `python3 - <<'PY'` constructing 100
   schools (five with risk 1.0, 95 with risk 0.02), calling
   `select_audit(..., 10)`, and repeating the same
   `rng.choice(100, size=10, replace=False, p=prob/prob.sum())` 5,000 times:
   ```bash
   python3 - <<'PY'
   import numpy as np, pandas as pd
   from components.trust_audit.core import select_audit
   schools = pd.DataFrame({"udise_code":[f"{i:011d}" for i in range(100)]})
   risk = schools.copy(); risk["risk_score"] = [1.]*5 + [.02]*95
   selected = select_audit(schools,risk,10,seed=118)
   pi = selected.audit_inclusion_prob.to_numpy(float)
   rng = np.random.default_rng(2); count = np.zeros(100)
   for _ in range(5000):
       count[rng.choice(100,size=10,replace=False,p=pi/pi.sum())] += 1
   print(round(pi.sum(),3),round(pi[:5].mean(),3),round((count[:5]/5000).mean(),3),
         round(pi[5:].mean(),3),round((count[5:]/5000).mean(),3))
   PY
   # 8.428 1.0 0.831 0.036 0.062
   ```
   A separate probe on the *default* seed-101, 600-school risk distribution
   using the same `select_audit`/`rng.choice` calls over 2,000 draws was
   closer: low-risk
   decile 0.0495 recorded / 0.0511 empirical, high-risk decile
   0.1675 / 0.1623. Thus this is a real design/HT bug, not evidence that
   the reported default MAE is fabricated. **Fix:** use a fixed-size PPS
   design that realizes known first-order inclusion probabilities (handling
   certainty units and recalibrating the remaining budget), or use actual
   inclusion probabilities for the implemented sampler; test empirical
   frequencies under skew as well as the current synthetic distribution.
   Any changed method needs its own honest evaluation, not a retroactive
   reinterpretation of the frozen holdout.

6. **[MAJOR] Finite-population correction removes assessor-error variance
   in completely re-tested tiny schools.**
   `components/trust_audit/assurance.py:135-140` multiplies *all* of
   `meas_var` by `(N-m)/(N-1)`. For `m=N`,
   sampling variance is zero but independent recording errors remain.
   Evidence: `python3 -c 'e=.03; print(e*(1-e)/(5*(1-2*e)**2),
   e*(1-e)/(12*(1-2*e)**2))'` printed
   `0.006586690810321413 0.0027444545043005886`
   (corrected-share assessor-only SEs 8.12 and 5.24 pp), whereas
   `fpc=0` forces the implementation's measurement component to **0** in
   both schools. Such schools occur because enrolment is drawn from 5-60
   (`world.py:123`). The misallocated noise also affects fitted school
   residual variance and the bootstrap's pseudo-truth. **Fix:** decompose
   corrected-share variance into a finite-population-adjusted true-status
   sampling term **plus** `eps*(1-eps)/(m*(1-2*eps)^2)` for independent
   assessor flips; test `N=m` and `eps=0` explicitly.

7. **[MAJOR] `truth_block` stores a school-mean, not the stated share of
   children.** `eval/sim/world.py:241-243` takes the simple mean of school
   goal rates while recording a sum of children next to it. Evidence:
   ```bash
   python3 - <<'PY'
   from eval.sim.world import make_world
   w = make_world(18,{"n_schools":80,"n_clusters":8,"n_blocks":2})
   for b in w.truth_block.itertuples():
       school_ids = w.schools[w.schools.block_lgd==b.block_lgd].udise_code
       children = w.children[w.children.udise_code.isin(school_ids)]
       print(b.block_lgd,round(b.true_read_goal_rate,4),
             round(float(children.read_goal.mean()),4))
   PY
   ```
   Output excerpt:
   ```
   B01 0.2661 0.2421
   B02 0.2887 0.257
   ```
   This **predates** vectorization and does **not** contaminate the reported
   coverage/MAE: `eval/coverage_test.py:58-61` correctly reconstructs child
   totals instead. It can mislead another evaluator by 2-3 pp. **Fix:**
   aggregate each school's successes (or enrolment times school rate) and
   divide by total children, for both reading and numeracy; add an
   unequal-enrolment test.

8. **[MINOR] The `risk_score` contract says "probability" but the output is
   only a rank blend.** `architecture/contracts/fln_contracts.py:216`
   specifies `P(reported figure inflated beyond tolerance)`, whereas
   `components/trust_audit/core.py:69-88` combines uncalibrated percentile
   ranks. Evidence:
   ```bash
   python3 - <<'PY'
   from components.trust_audit.core import forensic_flags
   from eval.sim.world import make_world
   w = make_world(18,{"n_schools":80,"n_clusters":8,"n_blocks":2}); p = w.public_view()
   risk = forensic_flags(p.teacher_reports,p.schools,p.item_responses,p.item_bank)
   print(round(float(risk.risk_score.mean()),3),
         round(float(w.truth_school.inflating_school.mean()),3))
   PY
   # 0.503 0.275
   ```
   AUC evaluates ranking, not probabilistic calibration. **Fix:** either
   calibrate on separate labelled data and check reliability, or rename the
   contract to a relative/unit-interval risk *score* and avoid probability
   language.

9. **[MINOR] The production allocation API both accepts hidden truth and
   silently substitutes raw targeting for a requested oracle.**
   `components/allocation/core.py:15-22` puts `assessments is None` ahead of
   `strategy == "oracle"`: the caller may provide `truth_school`, yet that
   call uses raw reports; providing an empty assessment list instead selects
   by hidden truth. Evidence:
   ```bash
   python3 - <<'PY'
   from components.allocation.core import allocate_camps
   from eval.sim.world import make_world
   w = make_world(18,{"n_schools":80,"n_clusters":8,"n_blocks":2}); p = w.public_view()
   for assessments in (None,[]):
       a = allocate_camps(p,assessments,2,strategy="oracle",truth_school=w.truth_school)
       print([d.area_code for d in a])
   PY
   # ['27010000034', '27010000003']
   # ['27010000034', '27010000005']
   ```
   The registered held-out allocation evaluator does **not** use this
   helper: it explicitly builds the oracle from child truth in
   `eval/coverage_test.py:69-75`, so its reported gain is unaffected.
   **Fix:** move the oracle baseline into evaluation-only code, dispatch
   `strategy` before checking assessments, and reject an unavailable
   strategy/required input rather than returning a misleadingly labelled
   fallback.

## Standards

No hard violation of an explicit coding standard was found in the
`f6601b9...c2caae7` diff; the already-registered timestamp discrepancy is
issue 12. Three nonblocking Fowler-style *judgment calls*:
`eval/run_eval.py:40-150` is a broad orchestrator (possible Divergent Change,
but its single-headline responsibility explains the grouping);
`components/teacher_view/planner.py:45-55` repeats an activity-ID lookup
(possible Duplicated Code; a shared lookup would remove it);
`components/dashboard/core.py:29-53` mixes transformation and serialization
(weak Feature Envy / Shotgun Surgery, but deliberately dashboard-specific).
The dashboard concern in issue 2 is a **functional** integration failure,
not merely a style complaint.

## Spec and reporting issues

The pre-registered primary test and MAE gate pass, and no frozen method or
seed/threshold changes appear after `f6601b9`. Extra held-out detection AUC
and C4/C7/C12 numbers added to `headline.json` after registration are
*additional* analyses, not preregistered successes. Allocation gain is
correctly reported as **not shown** for both default and need-correlated
scenarios. These distinctions should remain explicit wherever the headline
is presented.

10. **[MINOR] "20% double-assessed" describes the configured fraction, not
   the realized sample.** `components/trust_audit/core.py:157` rounds
   `0.2*12` separately for each school to **2**, or 16.7%, and
   `assurance.py:247-248` matches this in the bootstrap. Evidence: the
   preregistered seed-101 audit/re-test command:
   ```bash
   python3 - <<'PY'
   from components.trust_audit.core import forensic_flags, retest, select_audit
   from eval.sim.calibration import ASER2024_GOVT_STD3
   from eval.sim.world import make_world
   w = make_world(101,ASER2024_GOVT_STD3); p = w.public_view()
   r = forensic_flags(p.teacher_reports,p.schools,p.item_responses,p.item_bank)
   s = select_audit(p.schools,r,60,seed=118)
   a = retest(w,s,12,seed=132,double_check_frac=.2)
   print(int(a.n_double.sum()),int(a.n_audited_children.sum()),
         round(a.n_double.sum()/a.n_audited_children.sum(),4),
         int((a.n_audited_children==12).sum()))
   PY
   # 116 686 0.1691 52
   ```
   In particular, the run
   `double-check children / retested children: 116 / 686 = 0.1691`;
   52 schools had 12 re-tested children and only 2 checks each.
   The holdout validates the *actual* protocol, not an exactly 20% one.
   **Fix:** append a dated clarification to the protocol/results rather
   than rewriting the registration; for any future 20% protocol, draw
   checks across all audited children (or randomly round school quotas)
   and update its bootstrap before new held-out evaluation.

11. **[MINOR] Exploratory "district average" is an equal-block average,
    not the district child share.** `eval/run_eval.py:52-66` uses each
    seed's arithmetic means of six block estimates and six true rates
    for the flag/correct-side tests; `headline.json:136-139` does not
    qualify "district average". The block CSV contains no enrolments.
    Evidence: this lightweight command reconstructs each seed's block
    enrolment from `world.py:117-126` (the first RNG draws), combines it
    with `coverage_heldout.blocks.csv` and repeats the predicates:
    ```bash
    python3 - <<'PY'
    import numpy as np, pandas as pd
    data = pd.read_csv("eval/results/coverage_heldout.blocks.csv")
    data = data[data.method=="fh"]
    blocks = np.array([f"B{b:02d}" for b in range(1,7)])
    clusters = np.array([f"C{i+1:03d}" for i in range(40)])
    c_to_b = dict(zip(clusters,blocks[np.arange(40)%6]))
    u_flags,u_good,w_flags,w_good,shifts = [],[],[],[],[]
    for seed in range(101,131):
        rng = np.random.default_rng(seed)
        school_cluster = rng.choice(clusters,size=600,replace=True)
        n = rng.integers(5,61,size=600)
        by_block = pd.Series(n).groupby([c_to_b[c] for c in school_cluster]).sum()
        b = data[data.seed==seed].copy()
        b["n"] = b.block_lgd.map(by_block)
        eu,tu = b.estimate.mean(),b["true"].mean()
        ew,tw = np.average(b.estimate,weights=b.n),np.average(b["true"],weights=b.n)
        below_u,above_u = b.hi<eu,b.lo>eu
        below_w,above_w = b.hi<ew,b.lo>ew
        u_flags.extend((below_u|above_u).tolist())
        u_good.extend(((below_u&(b["true"]<tu))|(above_u&(b["true"]>tu))).tolist())
        w_flags.extend((below_w|above_w).tolist())
        w_good.extend(((below_w&(b["true"]<tw))|(above_w&(b["true"]>tw))).tolist())
        shifts.append(abs(eu-ew))
    print(sum(u_flags),sum(u_good),sum(w_flags),sum(w_good),
          sum(x!=y for x,y in zip(u_flags,w_flags)),round(max(shifts)*100,3))
    PY
    # 99 99 97 97 6 1.237
    ```
    Output excerpt:
    ```
    99 99 97 97 6 1.237
    ```
    The stored 0.55/1.00 numbers **are computed as coded**, not as the
    conventional child-weighted district share, and 81 blocks have no
    side flag. **Fix:** explicitly call the comparator "mean block share",
    or store block enrolments and recompute against a child-weighted
    district average; retain the exploratory/post-hoc label and report
    the flagged denominator.

12. **[MINOR] The registered minute and commit minute differ.**
    `eval/preregistration/2026-10-04-coverage.md:3` says 15:44 IST and
    cites its commit time as evidence; `PLAYBOOK.md:117` requires that
    stated time to match the Git commit time. Evidence:
    `git show -s --format='%aI %cI' f6601b9` printed
    `2026-10-04T15:44:58+05:30 2026-10-04T15:45:07+05:30`.
    The author minute agrees, the committer minute does not. Results
    were committed at 15:48 and the method remained unchanged, so this
    is **not evidence of held-out tuning**. **Fix:** append a dated,
    transparent correction identifying both timestamps; do not rewrite
    the pre-registration.

## Interval-construction judgment and simulator comparison

The algebra of the assessor correction is right under its stated symmetric,
independent two-assessor model: `d=2*eps*(1-eps)`,
`eps=(1-sqrt(1-2*d))/2`, and
`a_hat=(observed_share-eps)/(1-2*eps)` (`assurance.py:83-87,132-139`).
Children-weighting via `enrolment/pi` and the stratum *ratio* of weighted
totals are appropriate **if `pi` is the real inclusion probability**
(issue 5). The basic-bootstrap orientation is also correct:
`assurance.py:253-265` records `estimate_star - pseudo_truth` and
subtracts its 95th/5th percentiles from the observed estimate. This is a
**model-conditional prediction interval**, not distribution-free
90%-coverage for real districts.

Limitations: the bootstrap conditions on the observed census reports,
forensic scores and risk strata rather than generating new reports; it
draws Gaussian/clipped pseudo-school rates from fitted residual variances
and uses only 200 replicates (roughly ten draws in either 5% tail).
`world.py:227-233` injects 5% survey level-recording noise, whereas
`assurance.py:249-251` re-samples anchor children without that recording
step. Each synthetic world's proficiency threshold is set from its own
latent ability quantile, enforcing the ASER-like marginal; inflation,
assessor independence and same-construct anchor are assumptions, not
real-world validation. The 180 block-coverage indicators share 30 worlds;
a quick world-resampling check gave 95% coverage interval
0.9333-0.9889 versus the reported block-i.i.d. Wilson
0.9292-0.9846. Neither reverses the preregistered 0.85 gate.

`git diff 2cdbe40~1 2cdbe40 -- india71-t2-learning/eval/sim/world.py`
shows the vectorized child's categorical draws, ability formula, teacher
inflation/noise, item Bernoulli responses and survey flips preserve the
loop version's conditional distributions while changing draw order and
row order. I found no changed distribution from the vectorization itself;
issue 7 is an unchanged aggregation error. The assurance estimator sees
`public_view()` (no hidden `children` goal/ability columns or nonempty
truth tables), observed teacher/risk/survey data and the re-test output;
there is no direct hidden-truth lookup in its fit/bootstrap. `retest`
legitimately reads hidden child goal status; evaluator-only
`detection_auc`/`evaluate_area` also read truth. The allocation API's
truth-dependent oracle exception is issue 9. The **separate C4 evaluator
leak** is issue 3.

**Review axes:** Standards: 0 new documented violations in the post-registration
diff, 3 optional smells
(worst heuristic: broad `run_eval` responsibility). Spec/reporting:
3 minor discrepancies above (most consequential: realized double-check
rate); correctness/governance: 1 blocking, 6 major, 2 minor (worst:
unsuppressed raw-response access). Total numbered findings:
**1 blocking, 6 major, 5 minor**. The synthetic default coverage and
MAE reproduce; these findings limit other claims and safe deployment.
