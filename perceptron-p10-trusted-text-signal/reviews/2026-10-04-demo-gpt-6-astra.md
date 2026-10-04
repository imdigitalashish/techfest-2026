# Demo judge review: Break the band

**Score: 78/100.** Reviewed `051094b53f714616c2e83ca15236b0ccba8ff885` against `PLAYBOOK.md` section 11, from my own worktree. Sources, all eight fallback PNGs, the requested smoke, and live browser/API interactions inspected. No exporter or raw-data retraining run. Paths below are project-relative.

| Section 11 bar | Verdict |
|---|---|
| One-command, offline, CPU; first visual within 60 s | Warm CPU/offline path works; documented cold path totals about 121 s |
| Core claim live with a baseline | Strong: actual model predictions and certificate, not prerecorded interval animation |
| Judge-controlled striking capability | Yes: one low-trust post removes a plain-CQR hit; state-changing interactions need hardening |
| Honest numbers and scope | Numerical anchors reproduce; two important footer qualifications are missing |
| Three-minute script and recorded fallback | Present; all eight screenshots show useful, coherent states |
| Headless smoke proves the outputs | Substantial engine/API checks; browser assertion can pass an entirely uninitialized page |
| Cross-model review recorded | This review; builder still owns the ledger entry and response |

## Would I lean in?

**Yes.** The tiny median movement versus a decisive interval-edge crossing is a better demonstration than a contrived forecast explosion. The deletion box is a concrete, inspectable mechanism, and the explicit selection rate earns trust. However, I would ask why we should retain an empirically unhelpful text channel rather than use price-only. This is a credible robustness demo, not yet a winning quantitative product argument.

## Honesty check

`V` denotes `eval/results/text_minilm_v2.json`; `J` denotes `eval/results/text_utility_djia_v1.json`.

The live path is genuine: `inject_seq -> features_from_docs -> QuantileFusion.predict / CertifiedCQR`, plus `trust_of` and `aci_from_bounds`. `scorer_worker.py` calls `MiniLMSentimentScorer.score` on CPU. The certificate is computed from observed documents, **not** manufactured by unioning with the known clean interval; clean values are diagnostic comparisons.

| Claim | Verdict | Evidence |
|---|---|---|
| Selected: 327/16,443, 2.0%; 207 silent | PASS for the stated finite grid | Smoke independently reproduces 327 hit-to-miss days using `oracle_grid(3)`; `bundle/showcase.json` records 207 silent and the selection rule. This is discovered vulnerability, not an exhaustive rate over arbitrary attacks. |
| Live MiniLM sentiment and metadata trust | PASS | Pump score `0.9521228402900375`, trust `0.10109589041095891`, matching `V.attack.pump`. Typed bearish text scores differently. |
| One bot post breaks D, 2016-03-28 | PASS | Live upper edge `2.043682 -> 1.906095`, realised return `2.016428`; median shift `-0.004288 pp`. Certified upper edge `2.119408` contains the clean edge. Matches the screenshot/talk-track rounding. |
| Certificate contains the clean interval, not necessarily the return | PASS, fixed offset only | Live `Q = 0.374909233934`. At six copies, `contains_clean=false` but `covers=true`, and the badge correctly becomes NO GUARANTEE. `research/components/robust_conformal.md` states the assumptions and numerical qualification. |
| Pump replay: plain 86.4%, certified 89.4%, 144 flips | PASS | Live `0.864197530864`, `0.893754181111`, matching `V.attack.pump`. There are also 105 rescued rows: **39 net additional misses**, not 144 net. |
| ACI 89.50% equals committed; attacked CR-ACI 89.7% | PASS | Live `0.894970504166` and `0.897403150277` match `V`. No separate-run per-row nesting is claimed. The theorem is not a 90% finite-horizon guarantee: its worst-case bound on deviation of mean miscoverage from alpha at 189 days is `0.48148` (48.15 pp). |
| Typical attacks barely move the forecast | PASS | Mean shift `+0.094306 pp`, p95 absolute shift `0.195635 pp`, versus clean width `4.756145 pp`; `V.attack.pump` and `V.attack.oracle`. A uniform random HON day also stayed covered in the live probe. |
| Text utility is null in the registered experiment | PASS as a scoped finding | `J`: Winkler `3.523920 -> 3.520489`, one-sided `p=0.4629`. Not proof that text can never help; the results document also qualifies the experiment as conditional on the open. |
| Injected posts, grid attacks, and fallback are labelled | PASS | Visible INJECTED / SYNTHETIC badges; grid explicitly sets scores directly. Forced offline VADER worker reports FALLBACK / not deployed, and returns `scorer="vader"`; UI has corresponding warning labels. |
| Footer: positive control +11%; worst attack 84.7% | NEEDS QUALIFICATION | +11.059% is an **exploratory synthetic, target-derived** control. 84.6926% is a **per-row hindsight oracle knowing y**; the worst fixed-grid variant gives 85.7325%. See M3. |

## Smoke result

Ran `bash perceptron-p10-trusted-text-signal/demo/smoke.sh` with the supplied existing `P10_PYTHON`, bytecode writes disabled, and OMP/OpenBLAS threads set to two. Memory admission was **35 >= 30**; CPU only, one heavy job at a time.

```text
smoke_test: 35/35 passed in 203.4 s
78,000 within-budget attacks on 26 days at k=1/3/5:
  certified violations 0; plain CQR broken 7,749 times
server ready in 9.7 s
14 endpoint/scoring/input assertions: PASS
headless Chrome stage: PASS (but its predicate is defective; M2)
SMOKE: ALL PASS
```

The comparisons are substantive: recalculated offsets, predictions, coverage, widths, oracle counts and scorer output versus committed anchors. The independent live seed-1 D red-team reproduced the fallback exactly: **1,769/2,000 plain breaks, zero certified violations**; beyond budget, **278 containment violations and 47 missed returns**. Population replay and PICO's one-post failure also reproduced. The review server, PID 92072, was stopped.

## Top issues, ranked

**BLOCKING:** none found in the reproduced fixed-offset computation. These MAJOR issues still prevent an unqualified section-11 sign-off.

1. **MAJOR M1: A result can silently belong to a different stock-day.** `demo/static/index.html:316-332, 348-356, 556-600`. I delayed the real response to `POST /api/redteam` with `{row:5099,k:3,n:2000,seed:2}`, selected PICO, then released it. The page headed **PICO / row 11531** displayed **1,751 breaks from D / row 5099**. Day changes clear the panel, but late responses repopulate it without identity checks. Flips have an unchecked await; population's `isPump(P)` reads current controls instead of the submitted scenario. **Fix:** capture immutable request context/version, reject stale responses after every await, invalidate or explicitly label old results when inputs change, and add this delayed-response regression test.

2. **MAJOR M2: The browser smoke assertion is vacuous.** `demo/smoke.sh:86`. Both searched phrases occur in the inline JavaScript source. I blocked **every `/api/*` request**: the day remained `...`, ACI remained uninitialized, and the chart had zero children, yet the exact two grep predicates still passed. **Fix:** assert rendered element text/classes and nonempty chart geometry, then exercise Score & inject and the beyond-budget badge. A blocked-API/boot-error run must fail. Keep the valuable engine tests.

3. **MAJOR M3: The honesty footer omits the controls' threat/data models.** `demo/static/index.html:308-310`; `eval/exploratory_djia_v2.py:53-57`; `eval/run_baselines.py:171-175`. A positive-control gain is not an observed useful text signal: it uses `abs(y) + noise`. The 84.7% oracle chooses a different attack per row after seeing the outcome; it is not one executable fixed attack. **Fix:** label the control **SYNTHETIC / target-derived / exploratory**, label 84.7% **hindsight per-row oracle, knows y**, and show 85.7% as the worst fixed-grid result. Mark 86.7% explicitly as this test set's retrospective containment floor.

4. **MAJOR M4: The fresh-start timing does not satisfy the literal 60-second bar.** `demo/README.md:12-15`, `demo/run.sh:7-11`, `demo/_env.sh:18-24`. The committed measurement is **106 s setup + 14.8 s to first visual**, about 121 s; the launch stopwatch starts after setup. This is disclosed, not fabricated, but separating the timer does not shorten the one-command path. My borrowed-interpreter run does not establish cold-install performance. **Fix:** implement and document a distinct setup/fetch prerequisite, then measure the entire post-setup launch through rendered readiness; alternatively show a useful lightweight visual before heavy setup. Put the memory guard ahead of every native-library load.

5. **MINOR: The spoken width price needs its denominator.** `demo/SCRIPT.md:24,30`. +4.8% is the **clean-data** premium. Under the demonstrated three-post pump, widths are `4.721 -> 5.185 pp`, **+9.8% versus attacked plain**, or +9.0% versus clean plain. The UI's clean-cost label is correct. **Fix:** say "4.8% on clean data; here is the actual attacked width cost" rather than quoting 4.8% unconditionally.

6. **MINOR: The honesty footer is not always visible.** `demo/static/index.html:112`. At 1024x768 it becomes static, roughly 3,759 px below the top in my probe. The 1440x900 screenshots are fine, but a narrower projector loses the persistent caveats. **Fix:** keep a compact persistent scope/selection strip at narrow widths, with expandable detail.

## What would make it a winning demo

Keep the one-post edge crossing, deletion-box explanation and honest beyond-budget failure. Fix M1-M4 before rehearsal. Then show a separately fitted **price-only, zero-text-exposure alternative** alongside the robustness/width trade-off; do not call deletion of all text equivalent to price-only.

Make the population reckoning unavoidable: 144 lost hits, 105 rescued hits, 39 net extra misses, and the actual width premium. Let the judge pick an unselected day before the close. If text has no demonstrated utility, frame this as a certified safety component for an optional text channel, not a reason to deploy that channel. The winning sentence is precise: **"At a shared conformal offset, injecting at most k posts cannot remove a hit the clean plain interval had."**

## Builder response
