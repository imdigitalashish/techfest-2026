# P6 — Cross-asset statistical arbitrage with latency budgets

Perceptron Hackathon 2026 (IIT Bombay × Optiver), Problem 6. Journal: [thought_node.md](thought_node.md). Spike decision: [ADR 001](architecture/adr/001-spike.md). Round-1 draft: [deliverables/round1-abstract.md](deliverables/round1-abstract.md).

## Reproduce (from this folder)
Heavy steps go through `eval/run_guarded.sh`, which runs them under nice 10 and pauses them while system memory is low. Pinned environment: `requirements.lock`.
```bash
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.lock
.venv/bin/python components/feed/fetch_tardis.py --dates 2026-09-01 2026-10-01                 # 9-leg days (baseline, decay)
.venv/bin/python components/feed/fetch_tardis.py --set wf5 --dates 2025-10-01 2025-11-01 2025-12-01 2026-01-01 2026-02-01 \
    2026-03-01 2026-04-01 2026-05-01 2026-06-01 2026-07-01 2026-08-01                            # walk-forward days (md5: eval/results/data_manifest_wf12.tsv)
.venv/bin/python -m pytest -q components                                                       # contract, compiled-LEV and strict-simulator tests
eval/run_guarded.sh .venv/bin/python -m eval.run_baseline --train 2026-09-01 --test 2026-10-01 --legs <9 legs> --tiers f0,f1,f2,f5 --out eval/results/baseline_0901_to_1001
# PRE-REGISTERED primary test (eval/PREREGISTRATION-walkforward-12d.md; exact command inside)
eval/run_guarded.sh .venv/bin/python -m eval.falsification walkforward --days <13 days> --out falsification_walkforward_12d_prereg --subset unseen7:<7 days>
# Amendment 1 (strict fills, markouts, collisions, transfer, ablations)
eval/run_guarded.sh .venv/bin/python -m eval.sensitivity --days <13 days> --subset unseen7:<7 days>
eval/run_guarded.sh .venv/bin/python -m eval.decay_report --days <13 days>                     # decay: KM with CIs and publication-time bounds
eval/run_guarded.sh .venv/bin/python -m eval.decision_timing                                    # compiled decision step p50/p99 (macOS: mach_absolute_time)
.venv/bin/python -m eval.update_cadence && .venv/bin/python -m eval.latency_budget
.venv/bin/python -m eval.headline && .venv/bin/python deliverables/render.py && .venv/bin/python eval/check_docs.py   # deliverables, drift check
```

## Layout
- `architecture/` — components and contracts (`components.md`, `contracts/`), ADRs.
- `components/<name>/` — code per component: feed, latency, detector, decay, decision (+ `autoresearch/`), sim, costs. The book and fair-value baselines are currently inlined in `detector/cross.py` for speed.
- `eval/` — the end-to-end harness, plots, and `results/`, which holds every number quoted in the deliverables.
- `research/` — `landscape.md`, `notes/`, `components/`.
- `.data/`, `.cache/` — gitignored downloads, recordings and caches.

All P&L figures are **simulated** (basis-adjusted execution surplus; markouts in Amendment 1). Assumptions are listed in each results file: pre-positioned inventory, IOC legs at top of book, order latency = feed latency = δ in sweeps, and uniform fee levels.
