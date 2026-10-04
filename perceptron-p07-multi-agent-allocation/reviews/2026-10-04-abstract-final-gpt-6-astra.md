# Final Round-1 abstract review - hostile-judge mode

- **Date:** 2026-10-04 (IST).
- **Model:** `gpt-6-astra`.
- **Reasoning effort:** `max`.
- **Reviewed commit:** `a99d42c0b1d73ed57be040bfb98f9b22787b1928`, after `git fetch origin && git rebase origin/main`. The final abstract was introduced in `d1d66fd`.
- **Main artifact:** `perceptron-p07-multi-agent-allocation/deliverables/round1-abstract.md`, FINAL v1.0.
- **Companion artifact:** `perceptron-p07-multi-agent-allocation/deliverables/architecture.md`.
- **Evidence:** official Problem 7 brief, all eight requested result summaries, `eval/preregistration.md`, committed episode CSVs, ADR 001, landscape, previous reviews and their disposition ledger; relevant implementation files were also inspected.
- **Scope:** independent review of the submission, not a new implementation or a rerun of the simulation sweeps. Only this review file is changed.

**Verdict: 71/100.** The MVP evidence is substantially stronger than the novelty pitch. All eight required sections exist, and the requested body count is **899 words**. Most headline numbers trace correctly to committed results. The principal numerical mismatch is the trust-sweep sentence: it mixes comparators and scenarios. The larger credibility risks are describing the proposed adaptive trust mechanism as if it already exists, calling its future test pre-registered, and failing to distinguish the contribution from established fleet MPC.

There are **eight actionable issues**, numbered in section 3 for ACCEPTED/REJECTED decisions. Audit identifiers A01-A52 and D01-D04 are evidence references, not additional issue counts. Existing fixes are credited: no demand to restore the retired capture ratio, no allegation that the MVP reference was selected on test seeds, no penalty for the explicitly centralised planner, and no penalty for `[TEAM-n]` placeholders.

Unless a path begins with `_briefs/` or `PLAYBOOK.md`, paths below are relative to `perceptron-p07-multi-agent-allocation/`.

## 1. Hostile-judge scorecard

| Criterion | Weight | Score / 5 | Weighted points / 100 | One-line justification |
|---|---:|---:|---:|---|
| Problem understanding and relevance | 20% | 4 | 16 | Lead time, patience, forecast failure and coordination are well identified; the categorical description of reactive policies and forecast necessity is too strong. |
| Technical soundness and feasibility | 25% | 3 | 15 | The implemented MPC and MVP are credible, but the proposed calibrated, per-zone trust mechanism is neither concretely specified nor demonstrated. |
| Innovation / novelty | 20% | 3 | 12 | The empirical ablation map and honest negative result go beyond the starter baseline; forecast-driven MPC and decision-focused tuning themselves are established. |
| Clarity and structure | 10% | 4 | 8 | All sections are concrete and within the requested count, but the built/planned boundary, trust sentence and stale diagram conflict. |
| Impact and rigour of evaluation | 15% | 4 | 12 | Fixed-reference paired MVP tests are a real strength; exploratory results, replay replicates and the unregistered next spike need clearer separation. |
| Team fit and readiness | 10% | 4 | 8 | Three complementary workstreams, an existing build and exam-aware milestones are credible; RL, decentralisation and cluster transfer must remain optional. |
| **Total** | **100%** | | **71** | **16 + 15 + 12 + 8 + 12 + 8 = 71.** |

This is a score for the current text, not a prediction of selection against an unknown field. Round 1 explicitly judges the plan, not whether every stretch implementation already exists. Lack of an RL result is therefore not a missing MVP requirement.

## 2. Numbers and claims audit

**Conventions.** VERIFIED means the stated value or appropriately bounded claim is supported. UNSUPPORTED does not mean false: a proposed mechanism, causal interpretation or future outcome may simply be untested. Measured outcomes below trace to the requested result artifacts. Non-result facts such as problem identifiers, grid dimensions, publication years and calendar plans are separately traced to the brief, implementation or contextual documentation rather than passed off as experimental results.

The header's Round 1, Perceptron 2026, Problem 7 and 4 Oct 2026 are document/competition metadata, not measured outcomes; `v1.0` is an author-assigned version. They are outside the requested body count.

### 2.1 Problem, architecture and MVP

| ID | Abstract number / claim | Status and exact evidence |
|---|---|---|
| A01 | Theme 4, Problem 7 | **VERIFIED.** `_briefs/perceptron.txt`, lines 134-151: Theme 4, "Agents That Compete, Cooperate, and Adapt"; Problem 7, resource reallocation with look-ahead, rule baseline plus an RL **or planning-based** agent. |
| A02 | `[TEAM]` works on large-scale systems; cold starts are a relevant motivation | **VERIFIED as supplied team context, not a measured result.** `thought_node.md`, selection memo, describes large-scale systems/autoscaling as the user's strength; `PLAYBOOK.md` identifies the systems background. Other members' individual skills remain author-supplied. No placeholder penalty. |
| A03 | Fleets and compute share lead time L and patience P | **VERIFIED as a modelling analogy.** `components/simulator/core.py` has `move_steps_per_hop` and deterministic `patience`; the cluster instance is only planned. This is not evidence that taxi percentages transfer to GPU serving. |
| A04 | A reactive allocator learns only once queues form; look-ahead needs a demand model | **UNSUPPORTED as a universal statement.** `ReactivePolicy.observe()` uses arrival counts, not only queues; `mpc-queue` plans on known incoming supply with a zero demand forecast. See issue 8. |
| A05 | Certainty-equivalent forecasting holds supply back; false alarms and herding are the difficulties | **VERIFIED as plausible design concerns; UNSUPPORTED as an established explanation of these results.** Forecast/queue ablations show a decision difference, not the proposed causal mechanism. `architecture/adr/001-spike.md`, Limitations, records alternative modelling explanations. See issue 5. |
| A06 | Built PettingZoo `ParallelEnv`; 40 agents; 25-zone grid | **VERIFIED.** `mvp-v2/confirm.md` and its episode rows have `K=40` / `n_agents=40`; `components/scenarios/scenarios.py` has `grid=5`, hence 25 zones; `components/simulator/pz_env.py` defines `DispatchParallelEnv(ParallelEnv)` and one `unit_i` per resource. The result directories in this table are under `eval/results/`. |
| A07 | Daily Poisson demand, shocks, drift, transient spikes, over-dispersion and change labels | **VERIFIED as implemented scenario capabilities.** `components/scenarios/scenarios.py`: `day=1440`, shock/drift/spike generators, `ChangePoint` labels, and gamma-Poisson over-dispersion. Not every scenario has every feature switched on. `mvp-v2/confirm.md` contains all six named scenario families. |
| A08 | FIFO abandonment; repositioning takes L per hop; LP abandonment rate 1/P | **VERIFIED, with an important distinction.** `core.py` expires requests at a deterministic P-step deadline; `planner/mpc.py` uses survival `1 - 1/P`, a fluid approximation. L affects **empty repositioning only**, not occupied-trip durations. See issue 5's scope fix. |
| A09 | NYC TLC yellow taxis, July 2025, Manhattan, thinned | **VERIFIED.** `eval/results/nyc-v2/summary.md`: test July 3-4 2025, training July 1-2, Manhattan-internal trips, approximately 10 requests/min, thinning probability approximately 0.20. This is not a whole-month test. |
| A10 | Time-expanded LP, OD return flows, rolling horizon and per-agent execution | **VERIFIED.** `planner/mpc.py` contains delayed hop and OD service-return flows; `MPCPolicy.act()` executes the first-step plan through `flows_to_targets`. This is centralised cooperative control, as the abstract correctly says. |
| A11 | Warm-started HiGHS "solves it in ~6 ms per step (median, laptop)" | **VERIFIED number; MISMATCH in measurement description.** Across 180 `mpc-ewma` rows of `eval/results/mvp-v2/episodes.csv`, `median(1000 * wall_s / horizon) = 5.9487171587 ms`. This is the median of **episode-average end-to-end loop times**, not the median individual LP solve. `eval/harness.py` times simulation, policy, observation and metric accumulation together. Median episode `solve_ms_mean` is 5.3786098683 ms. Warm starts are implemented; laptop context is recorded in `PLAYBOOK.md`. See issue 6. |
| A12 | Time-of-day profile times per-zone level; Poisson CUSUM input | **VERIFIED components; distinguish arms.** `forecasters.py` implements the seasonal EWMA and CUSUM forecaster; `policies.py` selects them as different arms. The headline successful arm is `mpc-ewma`, **without** the detector. See issue 1. |
| A13 | Trust is set per zone from calibrated forecast uncertainty and detector regime state, tuned for service | **UNSUPPORTED as a built capability.** `MPCPolicy` stores `self.trust = float(trust)` and passes `self.trust * fc.mean` to the LP. The sweep uses fixed global weights. `Forecast.upper` is optional, not consumed by this gate. The revised ADR describes the per-zone mechanism as the next spike, and `thought_node.md` explicitly says it is a plan. See issue 1. |
| A14 | Elmachtoub & Grigas 2022; Wilder et al. 2019 | **VERIFIED.** `research/landscape.md` section 3b records Management Science 2022, DOI `10.1287/mnsc.2020.3922`, and AAAI 2019, DOI `10.1609/aaai.v33i01.33011658`. Their primary arXiv abstracts support decision-aware versus prediction-error-only training; see section 5. This is conceptual attribution, not an implementation of SPO+ or differentiable decision-focused learning. |
| A15 | Three rule allocators: static, greedy neighbour and reactive proportional; MVP (i)/(ii) | **VERIFIED.** `mvp-v2/confirm.md` reports `static`, `greedy` and `reactive`; `policies.py` implements historical shares, local-neighbour queue rebalancing and arrival-based proportional rebalancing. The planning alternative satisfies official MVP (ii). |
| A16 | Pre-registered MVP, reference fixed on tuning seeds, 30 fresh tests | **VERIFIED.** `eval/preregistration.md`: references selected on seeds 0-19; test seeds 200-229; primary arm `mpc-ewma`; shock reference `greedy`, mixed-shift reference `reactive`. Registration commit `6e58813` precedes result commit `11ad5bf`. |
| A17 | Abrupt shock +3.7 pp, 95% CI [+3.3, +4.2] | **VERIFIED.** `eval/results/mvp-v2/confirm.md`, primary shock row: **+3.73 [+3.28, +4.20] pp** versus greedy; means 0.9430 versus 0.9057. Rounding is correct. |
| A18 | Shock-plus-drift +5.5 pp | **VERIFIED.** Same primary table: **+5.47 [+5.36, +5.59] pp** versus reactive; means 0.9321 versus 0.8774. |
| A19 | 30/30 seeds, Holm-adjusted p approximately 10^-8 | **VERIFIED for the MVP primary family.** All six primary rows say **30/30**, raw Wilcoxon **1.9e-09**, Holm **1.1e-08**. The exact all-positive 30-pair signed-rank probability is `2 / 2^30 = 1.8626451492e-09`; multiplying by six gives `1.1175870895e-08`. These are not p-values for the new trust gate. |

### 2.2 Stretch results and differentiation

| ID | Abstract number / claim | Status and exact evidence |
|---|---|---|
| A20 | Both official stretch goals run; shock + drift + spikes +6.0 pp | **VERIFIED.** `eval/results/mvp-v2/confirm.md`, mixed scenario: **+5.99 [+5.82, +6.15] pp**, 30/30, versus reactive. Week/month runs cover the long-horizon goal. |
| A21 | A simulated week with a shock every day plus drift | **VERIFIED.** `eval/results/long-week-v2/summary.md`: **7 days, 10080 steps, 7 shocks/run, 10 seeds (200-209), K=40, P=10, L=1**. Scenario code also enables drift and spikes. |
| A22 | Week +6.3 pp over best rule, CI [+6.3, +6.4] | **VERIFIED.** Same summary: `mpc-ewma - reactive` **+6.34 [+6.26, +6.43] pp**; reactive is the best reported rule by mean. Rounded interval is correct. This is a 10-seed result, not a 30-seed one. |
| A23 | Week 132 fewer requests lost per shock | **VERIFIED.** Same comparison: **-131.7**, in the **120-step post-onset window**; means 290.3 versus 422.0. It is not an unrestricted full-shock total or a counterfactual estimate of losses caused by the shock. |
| A24 | Greedy decays from 91% to 47% by day 7 | **VERIFIED as daily means.** Same summary: greedy day 1 **0.910**, day 7 **0.466**. Raw trajectory means are **0.910261** and **0.465576**. This describes this drifting synthetic workload, not universal time-dependent degradation of greedy dispatch. |
| A25 | Planner stays above 90% | **VERIFIED for the seven daily means; UNSUPPORTED as an every-run guarantee.** Summary `mpc-ewma` daily means: **0.960, 0.951, 0.941, 0.939, 0.938, 0.907, 0.912**. Raw minimum seed-day is **0.87684**. Add "Daily means"; see issue 6. |
| A26 | 30-day month, 4 seeds, +6.4 pp | **VERIFIED.** `eval/results/long-month-v2/summary.md`: **30 days / 43200 steps**, seeds **200-203**, `mpc-ewma - reactive` **+6.37 [+6.29, +6.44] pp**, **4/4**, Wilcoxon **p=0.125**. The abstract correctly discloses four seeds; this is descriptive long-horizon evidence, not a conventionally significant month-level test. |
| A27 | NYC +2.5 pp | **VERIFIED.** `eval/results/nyc-v2/summary.md`: `mpc-ewma - reactive` **+2.52 [+2.39, +2.67] pp**, **20/20 thinning replicates**; means 0.9981 versus 0.9729. These are not twenty independent cities, dates or demand shocks. |
| A28 | 38 fewer requests lost in an observed July-4 night surge | **VERIFIED.** Same summary: **-38.1 [-42.4, -33.9]**, July 4 **21:30-23:30**; event loss means **1.4 versus 39.5**. The window is the largest observed surge; its cause is **UNVERIFIED**. Credit the abstract for saying "observed" rather than claiming fireworks causation. |
| A29 | Next: MAPPO/IPPO with TorchRL, dual-price decentralisation, compute instance with L=cold start | **VERIFIED as explicitly future scope, not completed results.** `thought_node.md` lists C8 RL as planned; `Plan.zone_value` and LP dual extraction support a possible coordination interface but do not implement a decentralised policy. The compute mapping is an analogy, not evaluated transfer. |
| A30 | Knative panic at 200% of capacity | **VERIFIED as the configurable default, not a universal fixed setting.** `research/landscape.md` section 6 and `research/raw/companies-ship-today.md` give **200.0**. The primary Knative documentation opened for this review explicitly calls it the default and allows configuration. |
| A31 | AWS and Azure predictive scaling only scale out; production uses fixed shock guardrails | **VERIFIED for those predictive features; UNSUPPORTED as differentiation against fleet MPC or all production systems.** The primary AWS/Azure pages and raw company notes explicitly retain dynamic/reactive scale-in. Neither service is a matched fixed-fleet dispatch baseline. See issue 3. |
| A32 | Planning beats the best rule in 7/8 (L,P) cells; +2.3 to +9.8 pp; 20/20 seeds each | **VERIFIED, exploratory.** `eval/results/phase-v2/summary.md` and `phase-v2-merged/summary.md`: positive differences **+9.82, +6.88, +7.94, +5.41, +5.62, +4.94, +2.27 pp**, each **20/20**. The eighth cell, **(8,10)**, is **-0.38 [-0.89, +0.04] pp**, **6/20**. Addendum A explicitly labels best-rule-by-test-mean comparisons exploratory. The merged file is a same-seed follow-up, not another independent replication. |
| A33 | Forecast essential under drift and short patience | **VERIFIED as a finite-set service advantage, not universal necessity.** `mvp-v2/confirm.md`: queue-only minus EWMA under drift **-2.68 [-2.76, -2.59] pp**. `phase-v2/summary.md`, P=3 queue-only differences: **-10.05, -17.78, -14.27, -4.93 pp**. Queue-only still serves substantial demand; "helps" is more exact than "essential". |
| A34 | True rates reduce service in 3/4 long-lead cells by -1.1 to -1.5 pp | **VERIFIED for L in {4,8}.** Both phase summaries: oracle minus EWMA **(4,3): -1.09 [-1.67, -0.57]**, **(8,3): -1.49 [-1.98, -0.99]**, **(8,10): -1.10 [-1.45, -0.75] pp**. Fourth cell **(4,10): +0.19 [+0.08, +0.28]**. Rounded negative range is right; these are conditional results from the approximate LP, not a theorem about information. |
| A35 | Ignoring forecasts loses 62 fewer requests per pure shock | **VERIFIED.** `eval/results/mvp-v2/confirm.md`, S1 shock loss: queue-only minus EWMA **-62.30 [-70.47, -53.83]**, 120-step window. Comparator is EWMA, not the best rule. |
| A36 | Pre-registered detector hypothesis did not replicate | **VERIFIED.** Addendum A specifies eight detector-minus-EWMA shock-loss tests. `phase-v2/summary.md`: harm at **(1,10): +4.4 [+2.0, +6.8], Holm p=0.026** and **(8,10): +21.9 [+11.5, +31.6], p=0.011**; improvement at **(2,3): -9.3 [-17.2, -1.4]** does not survive Holm (**p=0.25**). `phase-v2-merged` preserves these primary results. |
| A37 | Half-trust beats both full trust and queue-only by +1.1-1.2 pp under shock-plus-drift | **MISMATCH: comparator/scenario conflation.** `eval/results/trust-v2/summary.md`, shock+drift: half **0.9434**, full **0.9321**, queue **0.9284**. Hence **+1.13 pp versus full**, **+1.50 versus queue**; raw CSV differences are **1.1288587459** and **1.4971817163**. The **+1.24** value belongs to **shock+drift+spikes**, versus its stronger endpoint. The claim of improvement over both is true; the stated shared range is not their pair of contrasts. See issue 4. |
| A38 | Best trust varies: 0.25 shocks, 0.75 drift | **VERIFIED among tested global constants, exploratory.** Same table: shock best **0.25**, service **0.9569**, advantage over stronger endpoint **+0.20 [+0.17,+0.23] pp**; drift best **0.75**, service **0.9962**, advantage **+0.16 [+0.13,+0.18]**. Tested weights are **0, 0.25, 0.5, 0.75, 1** at **L=1, P=10**. This does not establish online per-zone regime identification or the optimal weight over a continuum. |

### 2.3 Evaluation, readiness and risks

| ID | Abstract number / claim | Status and exact evidence |
|---|---|---|
| A39 | Served fraction is primary | **VERIFIED.** `eval/preregistration.md` primary endpoint; `eval/harness.py` computes **served / arrivals**. It measures this simulated allocator's service, not actual NYC customer fulfilment. |
| A40 | Requests lost per shock | **VERIFIED metric, incomplete unit definition in abstract.** `eval/harness.py` uses **WIN=120**, counting abandonment during the post-onset window, averaged over shocks in long runs. With one-minute steps this is two hours. See issue 6. |
| A41 | "Empty moves per request"; planner out-serves reactive while moving less | **MISMATCH in metric name/denominator; VERIFIED bounded comparison.** Reports use **empty repositioning hops / served request**, not move orders / all requests. `mvp-v2/confirm.md`, shock: EWMA **0.9430 served, 0.511 hops/served**, reactive **0.8996, 0.585**. `pareto-v2/summary.md`, `c_move=0.5`: **+3.77 [+3.55,+4.00] pp**, **-0.172 hops/served** versus reactive. Default EWMA moves more than greedy (**0.326**) and does not move less in every scenario; scope the parenthesis. |
| A42 | Component evaluation: detection delay, false alarms per zone-day, post-shock forecast error | **VERIFIED as stated evaluation targets, not numerical achievements.** No calibrated uncertainty coverage or trust-gate performance number is supplied. The abstract should not convert these planned checks into the built-calibration claim in A13. |
| A43 | Same-planner myopic, queue-only, no-detector and true-rate baselines | **VERIFIED.** `mvp-v2/confirm.md` S1-S3 and both phase summaries contain these contrasts. Myopic is **H=L+1**, not H=1; queue-only retains supply look-ahead. The true-rate planner is not an upper bound. |
| A44 | Following Agarwal et al. 2021 | **VERIFIED at the level claimed.** `research/landscape.md` section 4 identifies **2021**, arXiv **2108.13264**, and interval-based evaluation. The exact Wilcoxon/Holm family is this project's pre-registration, not a claim that every listed statistical choice was prescribed by that paper. |
| A45 | Evaluation protocol: fixed references, 30 fresh seeds, paired bootstrap, Wilcoxon/Holm, then grid/NYC/week/month | **VERIFIED for MVP; UNSUPPORTED if read as one protocol applying to all reported results.** Counts are **MVP 30**, **phase 20**, **NYC 20 thinnings**, **week 10**, **month 4**. Addendum A pre-registers detector shock-loss tests, while the other grid contrasts and trust sweep are exploratory. Some extended-run references are selected by reported means. See issue 6. |
| A46 | "Pre-registered spike test"; full trust 1 and queue-only 0 | **Endpoints VERIFIED; registration UNSUPPORTED today.** `trust-v2/summary.md` gives the 0/1 mapping. `eval/preregistration.md` ends at **Addendum A**. Revised ADR 001 calls the new test **"to be committed before running, as Addendum B"**. No completed preregistration for adaptive trust was found. See issue 2. |
| A47 | Three members with optimisation/simulation, RL/coordination, statistics/demo ownership | **VERIFIED as a concrete three-workstream plan.** It covers the major disciplines and the official maximum of three members. Names are intentionally absent; actual personal qualifications are not independently evidenced and should be filled by the user, not invented by the reviewer. |
| A48 | Built simulator, baselines, planner, harness and results | **VERIFIED as committed artifacts.** Implementations are present under `components/`, the harness under `eval/`, and the requested result files contain completed runs. This does not extend "built" to adaptive trust, decentralised coordination or the dashboard. |
| A49 | Oct spike; early Nov RL; 17 Nov dashboard; exams 19-25 Nov; 1 Dec freeze; Dec rehearsal | **VERIFIED as plans/context, not completed milestones.** `PLAYBOOK.md` section 8 confirms **19-25 Nov 2026** exams and **17 Nov** last teaching day; `thought_node.md` lists the **1 Dec** midway check and **15-18 Dec** finals. The future dates are commitments, not run-derived measurements. The sequence is credible if optional work does not block the demo. |
| A50 | First-step matching approximation; solver-specific tie-breaks; backend recorded | **VERIFIED and already disclosed.** `planner/mpc.py` optimises continuous flows then rounds; `core.py` performs mandatory FIFO matching after moves. ADR limitations and the accepted code review document the mismatch. MVP episode rows all identify **highspy**. Do not reopen these as undisclosed old bugs; issue 5 concerns the stronger new causal interpretation. |
| A51 | Mostly synthetic demand; real replay mitigates | **VERIFIED but limited.** NYC replay supplies real recorded pickup times and OD information to the same grid simulator; `nyc_tlc.py` does not reconstruct all latent unmet demand or actual trip-time dynamics. Synthetic travel, matching and patience remain. See issue 6. |
| A52 | Centralised planning; decentralised variant planned; RL may win and would be reported | **VERIFIED as honest scope/risk declarations.** No claim of decentralised performance or RL superiority is made. These are appropriate limitations, not disqualifying omissions from a brief that allows a planning agent. |

### 2.4 Companion architecture audit

| ID | Diagram claim | Finding |
|---|---|---|
| D01 | Main path is detector -> restarting forecaster -> planner | **STALE relative to final spike.** Revised ADR 001 rejects restart as the new spike and proposes detector state -> trust gating. The diagram lacks a trust node and a detector-free EWMA evidence path. See issue 7. |
| D02 | Planner horizon H=L+6 | **MISMATCH at L=1.** `policies.py` and Addendum A use **H=6 if L=1, otherwise H=L+6**; the diagram implies H=7 at L=1. Its myopic **H=L+1** label is correct. See issue 7. |
| D03 | Evaluation panel presents seeds 200-229 as a common suite | **OVERBROAD.** This is the MVP seed range; phase/NYC use **200-219**, week **200-209**, month **200-203**. Separate evidence panels or qualify the label. See issues 6-7. |
| D04 | True-rate MPC is "the most a better forecast could add" | **UNSUPPORTED bound wording.** The diagram's own node correctly says "not an upper bound", but the reading guide reintroduces the bound interpretation. For NYC, the corresponding arm is a retrospective smoother, not true latent rates. See issue 7. |

## 3. Top eight attacks, ranked by marks at stake

Estimated points at stake below are subjective, overlapping recoverable marks, not additive deductions or guaranteed gains.

### Issue 1 - The actual new algorithm is a proposal, while the text makes it sound implemented

**At stake:** approximately 5-8 points across technical soundness and novelty. **Lead decision:** PENDING.

The word "calibrated" carries a substantive promise: an uncertainty definition, calibration target, update rule and some validity check. The supplied implementation has a scalar constant trust, not a calibrated zone/time-varying gate. A sweep over five global constants cannot show that an online mechanism recognises regimes. Moreover, all headline MVP gains belong to detector-free EWMA-MPC, not the pictured detector stack.

Specify a small achievable gate, explicitly mark it planned, and require comparison with the **best development-tuned constant**, not just 0 and 1. Otherwise a universal 0.5 shrinkage factor can pass the proposed test without demonstrating any regime awareness. The detector also needs to earn its place against a detector-free gate.

**Concrete replacements:** replace the spike bullet content with:

```text
*Spike (planned):* grid-tune a per-zone trust gate using forecast residuals and CUSUM alarms, multiplying the forecast before planning. Tune served fraction, not forecast error; test against best fixed trust on untouched seeds (Elmachtoub & Grigas 2022; Wilder et al. 2019).
```

Replace MVP bullet (ii)'s introductory content with:

```text
*(ii)* EWMA-MPC (no detector or adaptive trust) beats the reference rule in a pre-registered test (reference fixed on tuning seeds; 30 fresh test seeds):
```

**Word budget:** -4 words; body becomes **895** if this issue alone is applied. The detailed gate/calibration design belongs in the next protocol, not in an unsupported present-tense adjective.

### Issue 2 - The new spike test is not yet pre-registered

**At stake:** approximately 4-6 points across evaluation credibility and clarity. **Lead decision:** PENDING.

The label at abstract line 56 is not backed by the committed registration. Addendum A is the detector replication; the ADR explicitly says Addendum B is still to be committed. This does not invalidate the genuine MVP registration, but it makes the strongest word in the evaluation pitch inaccurate for the new contribution.

Before running the new test, freeze the algorithm and development choices, an untouched seed block, scenario/cell family, endpoint, success rule, references and multiplicity correction. State whether success means an aggregate gain or a gain in every cell; do not decide after looking. Reusing the exploratory 200-229 results as confirmatory evidence for the chosen trust rule would be invalid.

**Concrete replacement** for the last evaluation bullet:

```text
*Next registration:* freeze fresh seeds and Holm-corrected grid contrasts against full/zero trust, best fixed trust and detector-free gating; report every cell.
```

**Word budget:** unchanged; **899**. This is a label/specification repair, not a request to invent a retrospective preregistration.

### Issue 3 - The novelty comparison avoids the nearest prior art

**At stake:** approximately 4-6 points, mainly innovation. **Lead decision:** PENDING.

Knative and predictive cloud scale-out are useful motivation, but a fixed-fleet dispatch LP does not experimentally improve upon them. Iglesias et al. already combine a time-expanded mobility network, demand forecasting and MPC. Decision-aware loss selection is also established. An Optiver/IITB judge can recognise both without following the landscape link.

The honest contribution is the conditional ablation map, including failures, plus a **proposed** regime-gated extension whose value still needs to be demonstrated. This is legitimate hackathon innovation in evaluation/framing; it is not a new forecasting/MPC paradigm.

**Concrete replacement** for the opening novelty paragraph, leaving its section heading and subsequent bullets intact:

```text
Forecast-driven fleet MPC is established (Iglesias et al., 2018); decision-focused tuning is also prior art. Our contribution is an empirical lead-time/patience ablation map, including failures, and a testable regime-gated-trust extension.
```

**Word budget:** -15 words; **884**. No need to assert priority over an incompletely searched literature.

### Issue 4 - The trust-sweep sentence reports the wrong pair of gains

**At stake:** approximately 2-4 points across rigour and clarity. **Lead decision:** PENDING.

Under shock+drift, half-trust gains **1.13 pp over full trust** and **1.50 pp over queue-only**. The 1.1-1.2 range actually combines the stronger-endpoint contrasts from two scenarios, one with spikes. This is not fabricated improvement, but a quant judge will ask for the denominator/comparator immediately.

Also say "among tested weights": the maximising grid constant is not a validated optimum or an online policy.

**Concrete replacement** for the sentence beginning "An exploratory sweep agrees":

```text
Exploratory half-trust improves shock-plus-drift by +1.13 pp versus full trust and +1.50 versus queue-only; across tested weights, shocks favour 0.25 and drift 0.75.
```

**Word budget:** -3 words; **896**. The separate +1.24 pp mixed-with-spikes result can remain in the supporting evidence rather than being squeezed into an ambiguous range.

### Issue 5 - A conditional LP result is being promoted into an explanatory mechanism

**At stake:** approximately 2-4 points across soundness and evaluation. **Lead decision:** PENDING.

The same-solver comparisons are real. They show what happens when the forecast input is changed in this implementation. They do not yet show that withholding supply from "demand that may never arrive" is the cause, rather than fluid abandonment, first-step matching mismatch, horizon effects or rounded degenerate solutions.

This is **not** a demand to reopen the previously accepted/deferred LP bugs before Round 1. It is a demand to qualify the new interpretation. A tiny exact/deterministic mechanism experiment and sensitivity to matching, abandonment and tie-breaking can distinguish those explanations later. The already supplied matched-alpha and fixed-H detector follow-ups should be credited, not demanded again.

**Concrete replacement** for the sentence beginning "Yet a better forecast":

```text
In our approximate LP, true-rate forecasts lowered service in three of four long-lead-time cells (-1.1 to -1.5 pp); the mechanism remains untested.
```

Replace the environment's queue/lead-time bullet content with:

```text
Same-zone FIFO matching; deterministic patience P; empty repositioning takes L per hop.
```

**Word budget:** -5 words together; **894**. This also prevents interpreting L as a uniform scaling of all city travel times.

### Issue 6 - Evidence scope and measurement units are compressed past the point of accuracy

**At stake:** approximately 2-3 points, mainly rigour and impact. **Lead decision:** PENDING.

The abstract's single "30 fresh seeds" protocol visually covers several distinct designs. NYC is twenty thinnings of two dates; the week uses ten seeds and the month four. The 91%/47%/>90% story is about **daily means**, not every trajectory. "~6 ms" is an episode-average full-loop quantity. The movement denominator is served requests, and the shock-loss window is missing.

The replay does mitigate purely synthetic arrival patterns, but not synthetic travel, patience or matching; two observed taxi days do not establish broad deployment benefit. These are scope corrections, not grounds to discard the correctly computed MVP.

**Concrete replacements:** replace the protocol block with:

```text
*Protocol* (Agarwal et al. 2021):
  - MVP: 30 fresh seeds, tuning-fixed references, paired bootstrap CIs, Wilcoxon/Holm.
  - Detector replication: pre-registered; other grid contrasts exploratory (20 seeds).
  - NYC: 20 thinnings of two days; week/month: 10/4 seeds, descriptive.
```

Replace the latency sentence with:

```text
Warm-started HiGHS loop: ~6 ms/step end-to-end (median episode-average, laptop).
```

Replace the shock-loss metric bullet content with:

```text
requests lost per shock (120-step window);
```

Replace the movement metric bullet content with:

```text
empty hops per served request (under shocks, the planner out-serves the reactive rule while moving less);
```

Replace the weekly performance sentence beginning "The greedy rule decays" with:

```text
Daily means: greedy falls from 91% to 47% by day 7; the planner stays above 90%.
```

Replace the synthetic-demand risk bullet content with:

```text
Real replay retains synthetic travel, matching and patience.
```

**Word budget:** +1 word across these six replacements; **900** if applied alone. In the combined edit pack there is ample margin.

### Issue 7 - The optional diagram describes the superseded spike and the wrong default horizon

**At stake:** approximately 1-3 points across clarity and soundness. **Lead decision:** PENDING.

The diagram still makes detector-triggered forecast restart the main algorithm, has no trust gate, and gives H=L+6 without the actual L=1 exception. Its reading guide calls true-rate MPC "the most a better forecast could add", contradicting the node's correct "not an upper bound" qualifier.

**Concrete diagram-only fix:** show the built evidence path as observed arrivals -> EWMA forecaster -> LP -> coordinator. Add a dashed **planned trust gate** between forecaster and LP, with detector/residual inputs, and keep the old restart arm only as an ablation. Use **"H=6 at L=1; otherwise H=L+6"**. Say **"effect of true expected rates in this planner; not an upper bound"**, with **"NYC: hindsight smoother"** separately. Restrict **200-229** to the MVP panel. In the reading guide, clarify that the policy uses observations available from the preceding step, not arrivals observed after that step's action.

**Word budget:** no abstract change; **899**. A rendered one-page export must still be checked for legibility; the supplied Markdown alone does not establish physical page count.

### Issue 8 - The opening explanation conflates reactive demand estimates with queues and forecasting with look-ahead

**At stake:** approximately 1-2 points, mainly problem understanding. **Lead decision:** PENDING.

Your own reactive proportional baseline observes arrivals, and your queue-only LP demonstrates useful look-ahead without a demand forecast. A surprise with no anticipatory information cannot be predicted before it occurs; useful anticipation can instead come from known returning supply and recurring structure. Do not make the baseline appear artificially blind to support the pitch.

**Concrete replacement** for the first two sentences of Understanding:

```text
Reactive demand estimates update after arrivals; supply delays then compete with patience. Look-ahead uses known returning units, demand forecasts, or both; forecast quality and use interact.
```

**Word budget:** -6 words; **893**. This is a framing repair, not another demand for ablations that already exist.

**Combined budget:** applying all the exact abstract replacements above, without modifying the title or deleting any section, produces **867 whitespace-delimited body words**. Each issue's replacement pack independently stays at or below 900. Diagram edits do not count toward the abstract.

## 4. Required sections, word count and team/milestone credibility

Counted from the first `**Problem` through EOF, exactly as requested:

```python
from pathlib import Path
s = Path("perceptron-p07-multi-agent-allocation/deliverables/round1-abstract.md").read_text()
body = s[s.index("**Problem"):]
assert len(body.split()) == 899
```

This deliberately counts whitespace-delimited Markdown list markers and standalone symbols, and excludes the title/header. Removing list/emphasis syntax yields 849 whitespace tokens. A different counter that splits hyphenated compounds will differ; do not treat one spare word as comfortable submission margin. The official brief calls 600-900 a suggested length; this review nevertheless applies the user's hard <=900 body requirement.

| Required section | Present and substantive? | Current body words | Judgement |
|---|---|---:|---|
| Problem & Theme chosen | Yes | 65 | Correct selection and a plausible systems motivation; placeholder names are acceptable. |
| Understanding of the challenge | Yes | 80 | Clearly identifies delayed actuation and impatient demand; repair the overgeneralisation in issue 8. |
| Proposed approach | Yes | 179 | Environment, LP, solver, forecasting and coordination are concrete; adaptive trust status/design needs issue 1. |
| Minimum Viable | Yes | 70 | Explicitly covers both official bullets, with genuine planning-versus-rule evidence. |
| Stretch ambitions | Yes | 111 | Both official goals have evidence; RL, decentralisation and cluster work are correctly future ambitions. |
| Novelty / differentiation | Yes | 178 | Measured map and failures are substantive; closest prior art and the new contribution's status need issues 3-5. |
| Evaluation plan | Yes | 119 | Metrics, controls and statistical design exist; distinguish completed protocols from the next one. |
| Feasibility and Risks | Yes | 97 | Owners, milestones, exam constraint and real limitations are present. |
| **Total** | **8/8** | **899** | **Pass under the requested count.** |

**Team credibility:** the optimisation/simulation, learning/coordination, and statistics/demo split is plausible for three people given the existing build. I have not deducted marks for `[TEAM-1..3]`, nor inferred nonexistent CVs. The November demo date leaves room around exams and the December freeze. For execution, make the October gate decision the critical path: if adaptive trust does not beat a well-tuned fixed trust, keep the validated MPC plus map. The RL comparator, decentralised variant and cluster instance must not all become dependencies of the finals demo. The abstract already labels them as "Next"; preserve that boundary.

**Architecture format:** an optional Mermaid artifact exists, but semantic consistency is currently weaker than the abstract. No PDF/page-sized export was supplied, so one-page fit and font legibility are unverified, not asserted to fail.

## 5. Is the novelty honest and narrow enough?

**Almost, but not yet.** Crediting decision-focused work and reporting the failed replication are the right choices. The safe contribution is an empirical map for this lead-time/patience simulator and a proposed, falsifiable adaptive-trust extension. Present wording still makes that extension sound built, and the production-heuristic comparison obscures the closest fleet-planning ancestor.

The following primary source pages were opened for this review; the corresponding repository records are in `research/landscape.md`, sections 2, 3b and 6:

| Prior art / source | What it establishes | Consequence for this abstract |
|---|---|---|
| [Iglesias et al., Data-Driven MPC of AMoD](https://arxiv.org/abs/1709.07032), associated with ICRA 2018 | A time-expanded mobility network, forecast-driven MPC rebalancing and an LSTM demand model evaluated on real DiDi data. | Forecast -> time-expanded optimiser -> fleet repositioning is established; cite it in the abstract, not only in background notes. |
| [Elmachtoub & Grigas, Smart "Predict, then Optimize"](https://arxiv.org/abs/1710.08005), Management Science 2022 | Prediction models can be trained using downstream decision error and an optimisation-aware surrogate rather than prediction error alone. | Decision-aware tuning is prior art. This project is not implementing SPO+ merely by sweeping a multiplicative trust coefficient; its demand forecast also enters LP constraints, so do not import SPO's guarantees by citation. |
| [Wilder, Dilkina & Tambe, Decision-Focused Learning](https://arxiv.org/abs/1809.05504), AAAI 2019 | Joint training through optimisation relaxations, with predictive accuracy not reliably measuring decision utility. | "A better prediction need not give a better decision" is not a new general discovery. The measured conditional fleet example and proposed regime policy are the potential contribution. |
| [Knative KPA](https://knative.dev/docs/serving/autoscaling/kpa-specific/) | Configurable panic behaviour; the documented threshold default is 200.0%. | A valid production example, but not a matched fleet-control comparator or evidence of superiority to Knative. |
| [AWS predictive scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/predictive-scaling-policy-overview.html) and [Azure predictive autoscale](https://learn.microsoft.com/en-us/azure/azure-monitor/autoscale/autoscale-predictive) | Predictive scale-out is combined with reactive/dynamic scaling, including scale-in. | Their one-sided predictive feature does not mean the overall systems cannot remove capacity, and adding/removing VMs is not the same optimisation problem as moving a fixed fleet. |

The negative oracle comparison is interesting but must not be sold as a violation of the value of information. An optimal decision-maker able to ignore extra information cannot be made worse simply by receiving it. Here a fixed, approximate certainty-equivalent LP is forced to consume a different point forecast, then its flows are rounded and executed in a simulator with different matching/abandonment semantics. There is no monotonicity guarantee for that procedure.

The phase results therefore establish a **conditional input-to-decision effect**, not its mechanism or generality. Likewise, the fixed-trust sweep demonstrates useful shrinkage at one L/P setting, not the added value of learning a regime or calibrating uncertainty. The narrowed novelty claim in issue 3 is defensible now. A stronger adaptive-policy claim needs held-out wins against the best fixed shrinkage and a detector-free alternative. The partial literature search cannot establish a "first-ever" regime-gated dispatch claim.

## 6. Three hardest finals Q&A questions and best honest answers

### Q1. "Is the perfect-forecast paradox just a bug in your optimiser, and what is new beyond Iglesias and decision-focused learning?"

**Best honest answer:** "The established pieces are forecast-driven fleet MPC and decision-aware tuning; we do not claim to have invented either. What we have measured is that replacing EWMA with true expected rates can reduce realised service in this particular approximate controller, including three of four long-lead cells. That is not evidence that information itself has negative value. Our fluid abandonment, matching approximation and rounding can interact with the input, and the proposed 'reserved supply' explanation is not yet isolated. We will test those alternatives in a small exact/deterministic example and planner sensitivities. The current contribution is the ablation map with failures. Adaptive trust is the next hypothesis, and it only earns a stronger claim if it beats a development-tuned constant and a detector-free gate on untouched tests."

Do not answer that common model errors cancel between arms: different forecast inputs can interact differently with the same approximation.

### Q2. "Which result was actually pre-registered, and why should I trust a sweep selected on the same seeds, twenty NYC replications and a four-seed month?"

**Best honest answer:** "The MVP primary family is pre-registered: EWMA-MPC against tuning-fixed rule references on 30 fresh seeds, with paired CIs and Holm across six scenarios. The shock gain is 3.73 pp, CI 3.28-4.20; the corrected p-value is about 1.1e-8. Addendum A separately registers detector shock-loss tests across eight cells; that hypothesis did not replicate. The fixed-trust sweep is explicitly exploratory, and the adaptive-trust Addendum B has not yet been committed. We will freeze it before a new untouched evaluation, including best fixed trust, detector-free gating, a defined success criterion and correction across the declared comparisons. NYC has twenty thinnings of the same two dates, not twenty independent real-world settings; the month has four trajectories and p=0.125. Those demonstrate bounded replay/long-run behaviour, not broad external validity. We would need additional held-out dates and workload families for that."

Do not pool reused seeds, seed-days or thinning replicates into a larger apparent independent sample, and do not turn exploratory intervals into simultaneous confidence claims.

### Q3. "Where are the autonomous agents, are the rules weak, and what would actually transfer to a fleet or compute cluster?"

**Best honest answer:** "Today this is a cooperative multi-unit system with central planning and per-unit actions, not decentralised negotiation or multi-agent learning. The official minimum allows a planning agent, and we state that limitation rather than use PettingZoo as proof of decentralised intelligence. We compare with three rules, fix the MVP reference on tuning seeds, and also use same-LP myopic and queue-only controls. Queue-only actually wins some shock comparisons, so we do not hide a stronger simple alternative. Service is not free: under pure shocks default EWMA uses 0.511 empty hops per served request versus greedy's 0.326, although it improves both service and movement relative to reactive in that scenario. The NYC input is recorded pickups in a toy grid, not a deployment. L as a setup delay and P as a timeout are transferable modelling ideas; the measured percentages are not. The finals-safe deliverable is the reproducible centralised allocator, controls, map and demo; RL, prices and a cluster instance remain optional extensions."

Do not promise independent-agent coordination, real-world customer impact or GPU savings until those systems and comparisons actually exist.

---

## Lead decisions (2026-10-04 11:28 IST) — abstract v1.2 (881 words) applies them

| Issue | Decision | Action |
|---|---|---|
| 1 — the new algorithm is a proposal but sounds implemented | **ACCEPTED** | Spike bullet replaced with "Spike (planned)" (the reviewer's wording). MVP (ii) now credits "EWMA-MPC (no detector or adaptive trust)". Allocator marked "(built)". |
| 2 — the spike test is not pre-registered | **ACCEPTED** (partly already fixed after the review snapshot) | Addendum B was committed at 11:05 IST. **Amendment B1** (11:25, before any test run) adds best fixed trust and a detector-free gate as co-primary comparators; success requires beating both. The abstract bullet now names these. |
| 3 — novelty avoids the nearest prior art | **ACCEPTED** | Novelty opening replaced: Iglesias et al. 2018 and decision-focused tuning acknowledged as prior art; contribution = empirical (L,P) ablation map with failures plus a testable regime-gated-trust extension. The Knative/AWS comparison was dropped from Novelty (motivation only, in `research/landscape.md`). |
| 4 — trust-sweep sentence reports the wrong pair of gains | **ACCEPTED (MISMATCH fixed)** | Now "+1.13 pp versus full trust and +1.50 versus queue-only; across tested weights, shocks favour 0.25 and drift 0.75". +1.24 (shock+drift+spikes) stays only in `trust-v2/summary.md`. |
| 5 — a conditional LP result promoted into a mechanism | **ACCEPTED** | "In our approximate LP, true-rate forecasts lowered service in three of four long-lead-time cells (−1.1 to −1.5 pp); the mechanism remains untested." Environment bullet now: "Same-zone FIFO matching; deterministic patience P; empty repositioning takes L per hop." |
| 6 — evidence scope and units compressed | **ACCEPTED** | Protocol split by suite (MVP 30 seeds; grid 20, pre-registered detector replication only; NYC 20 thinnings; week/month 10/4 seeds, descriptive). Latency = "median episode average, end to end". "requests lost per shock (120-step window)". "empty hops per served request (under shocks …)". "Daily means: greedy falls 91% → 47% …". Risk: "real replay retains synthetic travel, matching and patience". |
| 7 — diagram stale (restart spike, wrong default H, oracle wording) | **ACCEPTED** (mostly already fixed after the snapshot) | Trust gate (tested global trust vs planned gate) added 10:58/11:12. Now also "H = 6 at L=1, otherwise L+6"; true-rate MPC "effect of true rates in this planner; not an upper bound"; "NYC: retrospective hindsight smoother"; per-suite seed scopes; reading guide says policies use the previous step's arrivals. |
| 8 — opening conflates reactive estimates with queues | **ACCEPTED** | Understanding now opens with the reviewer's wording: reactive estimates update after arrivals; look-ahead can use known returning units, forecasts, or both. |
| Audit A25, A31, A41, A11, A13, A37, A46, D02, D04 | **ACCEPTED** | Covered by issues 1–8 above. |

**New evidence added after the review, not reviewed by it:** a second NYC period (July 10–11 2025): +1.52 pp [+1.43, +1.59], 20/20 (`eval/results/nyc-v2b/summary.md`). The abstract now says "+1.5 to +2.5 pp on two NYC periods". Reproduction of the other headline numbers: see `2026-10-04-headline-repro-gpt-6-sol.md`.
