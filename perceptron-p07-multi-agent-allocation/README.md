# P7 — Shock-aware look-ahead allocator (Perceptron 2026, Problem 7)

Journal and current state: [thought_node.md](thought_node.md) · approach: [deliverables/architecture.md](deliverables/architecture.md) · abstract: [deliverables/round1-abstract.md](deliverables/round1-abstract.md) · components: [architecture/components.md](architecture/components.md) · spike decision: [architecture/adr/001-spike.md](architecture/adr/001-spike.md) · research: [research/landscape.md](research/landscape.md)

## Live demo (PLAYBOOK §11)
```bash
bash demo/setup_venv.sh   # once per fresh clone (needs network once; creates .venv, warms native imports)
bash demo/run.sh          # offline; opens http://127.0.0.1:8707/ on the July 4th (real NYC trips) tab
bash demo/smoke.sh        # headless checks (47–48 asserts, ~40–60 s); --quick skips the week recompute
```
- **Opening scene:** real NYC TLC trips (July 2025, Manhattan, thinned). The best rule and the look-ahead planner run side by side on the identical request stream. Live losses in the July 4 21:30–23:30 surge window sit next to the committed 20-replicate means.
- **Then the judge's turn:** click to add a surge (live only). The synthetic stress test predicts first: the committed (L,P)-cell result appears before the click, and the live result then lands among the 20 committed per-seed results.
- **Talk track:** [`demo/SCRIPT.md`](demo/SCRIPT.md). Fallback screenshots and video: [`demo/fallback/`](demo/fallback/). Details: [`demo/README.md`](demo/README.md).
- **Lead's fresh-clone check** after the gpt-6-astra review fixes (`gh repo clone` of main at 10209ca, 2026-10-04 21:10 IST): smoke 47/47 in 36 s (the raw-TLC cross-check is skipped by design). First visual came 20 s after run.sh on a cold clone (includes macOS's first load of freshly installed native libraries) and 0.8 s on a warm rerun; the clone's git tree stays clean. The earlier check, before the review fixes (19:20 IST), gave smoke 31/31, 38 s cold, 2.4 s warm.

## Run it (from this folder)
```bash
uv venv .venv --python 3.11 --system-site-packages && uv pip install --python .venv/bin/python -r requirements.txt highspy
.venv/bin/python -m pytest -q tests                                  # contract tests (NYC tests skip without .data)
bash components/scenarios/fetch_nyc_tlc.sh                           # optional: NYC TLC July 2025 (~67 MB, gitignored)
# pre-registered confirmatory test (eval/preregistration.md), then its analysis
.venv/bin/python -m eval.harness --scenarios stationary shock drift shock+drift spikes shock+drift+spikes \
  --policies static greedy reactive mpc-myopic mpc-queue mpc-ewma mpc-cusum-v1 oracle --seeds 200-229 --horizon 1440 --out eval/results/mvp-v2
.venv/bin/python -m eval.confirm eval/results/mvp-v2                 # -> confirm.md (Holm, fixed reference rules)
bash eval/run_v2_queue.sh      # (L,P) phase-v2, NYC replay, week, Pareto, month (sequential, niced)
bash eval/run_v2_followup.sh   # matched-alpha, fixed-H, forecast-trust sweep
bash eval/run_v2_sensitivity.sh  # legacy-backlog planner on the same seeds
.venv/bin/python -m components.forecasting.autoresearch.eval         # frozen C4+C5 ratchet metric
```
Headline results: `eval/results/mvp-v2/confirm.md` (pre-registered), `eval/results/phase-v2/summary.md`, `eval/results/phase-v2c/summary.md`, `eval/results/long-week-v2/summary.md`, `eval/results/long-month-v2/summary.md`, `eval/results/nyc-v2/summary.md`, `eval/results/pareto-v2/summary.md`, `eval/results/trust-v2/summary.md`. Earlier exploratory runs (`mvp-v1`, `p3-v1`, `phase-v1`) used the legacy planner: reproduce with `--legacy`. Reviews and their ACCEPTED/REJECTED decisions: `reviews/`.

## Layout
- `architecture/contracts/contracts.py` — typed contracts (FleetState, StepInfo, DemandTrace, Forecast, Plan, Policy).
- `components/scenarios` — the demand generator (synthetic, labelled shocks/drift/spikes).
- `components/simulator` — the numpy core and PettingZoo `ParallelEnv`.
- `components/detection` — the Poisson CUSUM.
- `components/forecasting` — forecasters, plus `autoresearch/` (program.md, frozen eval.py, results.tsv).
- `components/planner` — the MPC LP.
- `components/coordinator` — flows → per-unit orders.
- `components/policies` — static / greedy / reactive / mpc-myopic / mpc-queue / mpc-ewma / mpc-cusum(-v1) / oracle, plus `name@k=v` variants (e.g. `mpc-ewma@trust=0.5`).
- `eval/` — the harness, the stats module and committed result folders.

Seeds 0–99 are for development and tuning; seeds 100+ are frozen test seeds. All demand is **synthetic** unless a folder says otherwise.
