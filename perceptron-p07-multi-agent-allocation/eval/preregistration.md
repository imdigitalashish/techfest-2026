# Pre-registration — confirmatory evaluation `mvp-v2` (written 2026-10-04 10:15 IST, before any run on seeds 200–229)

**Why.** The hostile-judge review (reviews/2026-10-04-abstract-v0.2-rubber-duck.md) showed two problems with mvp-v1: the "best rule" reference was chosen on the same test seeds, and only uncorrected p-values were headlined. This file fixes the protocol *before* the confirmatory data exist. It is committed (git timestamp) before `eval/results/mvp-v2` is created.

## Fixed design
- **Test seeds:** 200–229 (30 seeds, never used before). Tuning and ratchet seeds: 0–99. Earlier test seeds: 100–119.
- **Scenarios** (1440 steps = 1 simulated day, K=40 units, P=10, L=1): stationary, shock, drift, shock+drift, spikes, shock+drift+spikes.
- **Planner (all MPC variants):** abandonment-aware LP backlog (ρ = 1 − 1/P), HiGHS warm-start backend; H=6 unless stated. Code at the commit containing this file.
- **Common random numbers:** every policy replays the identical pre-sampled request stream per (scenario, seed).

## Reference rule per scenario (chosen on tuning seeds 0–19 — `eval/results/tuning-rules`)
| scenario | reference rule | its tuning-seed served fraction |
|---|---|---|
| stationary | greedy | 0.9771 |
| shock | greedy | 0.9156 |
| drift | reactive | 0.9351 |
| shock+drift | reactive | 0.8736 |
| spikes | greedy | 0.9726 |
| shock+drift+spikes | reactive | 0.8615 |

## Primary hypothesis (one family, Holm-corrected over the 6 scenarios)
- **H-primary:** `mpc-ewma` (look-ahead MPC with a deseasonalised EWMA forecast) has a higher served fraction than the scenario's reference rule.
- **Test:** paired by seed; mean difference with a 95% paired-bootstrap CI (10 000 resamples); two-sided Wilcoxon signed-rank; Holm across the 6 scenarios.
- **Pre-specified claim scope:** the MVP claim ("beats the rule baseline when demand suddenly shifts") rests on the **shock**, **shock+drift** and **shock+drift+spikes** rows.

## Secondary comparisons (reported with CIs; Holm within each family; exploratory, not used for the MVP claim)
- **S1, look-ahead ablations** (same LP and solver):
  - `mpc-myopic` (H = L+1) vs `mpc-ewma`: value of horizon.
  - `mpc-queue` (no demand forecast, queue only) vs `mpc-ewma`: value of the demand forecast.
- **S2, spike:** `mpc-cusum-v1` vs `mpc-ewma`. Served fraction overall, and requests lost in the 120 steps after each shock onset.
- **S3, forecast-value bound:** `oracle` (MPC fed the true expected rates — a perfect *forecast*, not a hindsight optimum or upper bound) vs `mpc-ewma`.
- **S4, cost of movement:** empty hops per served request for every policy. A separate Pareto run (`mpc-ewma@c_move ∈ {0.05, 0.2, 0.5, 1.0}`, shock scenario) traces service vs movement.

## Reporting rules
- Report every comparison above, whichever way it comes out. No seed is dropped.
- Recovery time is right-censored at 120 steps. Report the fraction of shocks recovered within 120 steps alongside the censored mean.
- Effect sizes in percentage points of served fraction; win counts over 30 seeds.
- Anything outside this list is labelled *exploratory*.

---

# Addendum A — pre-registration of the H1 replication `phase-v2` (written 2026-10-04 10:27 IST, before phase-v2 starts)

**Why.** The gpt-6-astra review (reviews/2026-10-04-spike-phase-gpt-6-astra.md) noted that phase-v1 was exploratory (legacy planner, seeds 100–109), and that the main pre-registration above fixes L=1, P=10, so it does not confirm the H1 cells.

- **Design:** (L, P) ∈ {1, 2, 4, 8} × {3, 10}; fresh seeds 200–219; 720 steps; scenario `shock`; abandonment-aware LP; highspy backend; H = 6 if L = 1 else L + 6 (same for every arm in a cell). Command: `eval/run_v2_queue.sh` step 1.
- **Primary H1 family (Holm over the 8 cells):** endpoint = requests lost in the 120 steps after shock onset; contrast = `mpc-cusum-v1` − `mpc-ewma`; paired by seed; two-sided Wilcoxon; 95% paired-bootstrap CI.
- **Predictions written now:**
  - **Fewer losses** (negative difference) at (2,3), (4,3), (8,3) and (8,10).
  - **No benefit** at (1,3), (1,10), (2,10), (4,10). Phase-v1 showed *harm* at (1,10): +8.7 lost per shock, 10/10 seeds. We predict the harm may recur; it is a known failure case to report.
- **Secondary (Holm within family, exploratory interpretation):**
  - served-fraction versions of the same contrast;
  - `oracle` − `mpc-ewma` (perfect-forecast reference);
  - `mpc-queue` − `mpc-ewma`;
  - `mpc-myopic` − `mpc-ewma`;
  - `mpc-ewma` − best rule (best rule chosen per cell by mean, labelled exploratory).
- **Follow-up sensitivity (exploratory; run after phase-v2 on the same seeds):**
  - matched-α EWMA (`mpc-ewma@alpha=0.01`, the detector arm's slow α without the detector) — separates "detector" from "slower smoothing";
  - fixed horizon H = 14 for both arms in every cell (`@horizon=14`) — removes the horizon-grows-with-L confound across cells.
- **"Null" wording:** without an equivalence margin we will say "no evidence of benefit", never "no effect".

---

# Addendum B — pre-registration of the spike falsification test (design frozen 2026-10-04 11:05 IST; to run in October)

**Spike A″ (decision-aware, regime-gated forecast trust).** The planner plans on trust_z(t) × forecast_z(t), where:
- trust_z(t) = τ_shock if zone z (or a grid neighbour) raised a Poisson-CUSUM alarm within the last W steps; otherwise τ_quiet;
- an optional variant shrinks by calibrated uncertainty: τ_quiet scaled by the conformal-PID coverage state.

(τ_shock, τ_quiet, W) are chosen by grid search on **tuning seeds 0–49 only**, maximising mean served fraction across the scenario suite and the (L, P) grid. They are then frozen and committed before any test run.

**Test seeds:** 300–329 (never used). **Cells:**
- the 6 scenarios at L=1, P=10;
- the 8 (L, P) cells of the shock scenario;
- each under both planner variants (abandonment-aware and legacy backlog): 28 cells.

**Primary family (Holm over 28 cells).** Endpoint: served fraction. Contrast: gated trust − max(trust = 0, trust = 1), where the better extreme is chosen per cell **on tuning seeds**. Paired by seed; two-sided Wilcoxon; 95% paired bootstrap CI.

**Success criterion, written now:**
- a positive, Holm-significant gain in ≥ 21 of 28 cells; and
- no cell with a Holm-significant loss larger than 0.5 pp.

Otherwise the spike is reported as failed and the deliverable rests on the planning result plus the measured map.

**Secondary:**
- gated trust − best *fixed* trust (tuned on seeds 0–49), which isolates the value of gating by regime;
- requests lost per shock;
- empty moves per served request.

**Amendments:** any change to this design must be committed (dated, with a reason) before the first test-seed run.

## Amendment B1 (2026-10-04 11:25 IST; before any test-seed run)

**Reasons.**
- The tuning-seed preview (`eval/results/gated-tuning-preview`) showed that local regime gating adds ≈0 over the best fixed trust.
- The gpt-6-astra review (`reviews/2026-10-04-abstract-final-gpt-6-astra.md`, issues 1–2) noted that a universal constant (e.g. 0.5) could pass a test against only trust ∈ {0, 1}.

**Changes to Addendum B.**
1. **Co-primary comparators.** Gated trust is tested against each of the following, with Holm over cells × comparators:
   - (a) max(trust 0, trust 1);
   - (b) the **best fixed trust**, tuned on seeds 0–49;
   - (c) a **detector-free gate** using forecast-residual uncertainty only, also tuned on seeds 0–49.
   The spike counts as **successful only if it beats (b) and (c)**. Beating (a) alone is reported as "shrinkage helps", not as regime awareness.
2. **Gate design space** (all tuned on seeds 0–49, then frozen and committed before testing):
   - a city-wide regime signal: trust ↓ while any CUSUM alarm is active city-wide;
   - per-zone uncertainty shrinkage from rolling forecast residuals;
   - the original per-zone/neighbour alarm gate.
3. **Unchanged:** seeds 300–329, cells, endpoint, two-sided Wilcoxon, paired bootstrap CIs, reporting of every cell. The success criterion of Addendum B applies to comparators (b) and (c).

---

## Correction — stated times vs commit times (appended 2026-10-04 17:28 IST; registered text above left unedited)

The times written in the headers above were estimated, not read from the clock. Each is 2–11 minutes later than its git commit, and **the commit is the evidence** (PLAYBOOK §6). Actual times, from `git log --date=format-local` (IST), with run start = config.json mtime − wall_s:

| Section | Stated time | Commit (IST) | First run it governs (IST) | Order OK? |
|---|---|---|---|---|
| Main pre-registration (mvp-v2) | 10:15 | **10:10:38** (6e58813) | mvp-v2 started 10:11:01 | yes — registered 23 s before the run |
| Addendum A (phase-v2) | 10:27 | **10:25:33** (a5eb3f0) | phase-v2 started 10:32:25 | yes |
| Addendum B (trust spike) | 11:05 | **10:59:23** (9390333) | not yet run (seeds 300–329 unused; max seed in any result = 229) | yes |
| Amendment B1 | 11:25 | **11:14:31** (72426fc) | not yet run | yes |

No registered content changes. Future registrations take their time from `TZ=Asia/Kolkata date`.
