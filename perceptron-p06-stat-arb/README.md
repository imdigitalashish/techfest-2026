# P6 — Cross-asset statistical arbitrage with latency budgets

Perceptron Hackathon 2026 (IIT Bombay × Optiver), Problem 6. Journal: [thought_node.md](thought_node.md). Spike decision: [ADR 001](architecture/adr/001-spike.md). Round-1 draft: [deliverables/round1-abstract.md](deliverables/round1-abstract.md).

## Reproduce (from this folder)
```bash
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r pyproject.toml
.venv/bin/python components/feed/fetch_tardis.py --dates 2026-09-01 2026-10-01      # free Tardis samples → .data/ (≈280 MB)
.venv/bin/python -m pytest -q components/test_contracts.py                           # contract + behaviour tests
.venv/bin/python -m eval.run_baseline --train 2026-09-01 --test 2026-10-01 \
  --legs binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT,okex-swap_BTC-USDT-SWAP,bybit_BTCUSDT,kraken_BTC-USD,bitstamp_BTCUSD,deribit_BTC-PERPETUAL \
  --tiers f0,f1,f2,f5 --out eval/results/baseline_0901_to_1001                       # decay report + latency frontier (~5 min on an M5)
.venv/bin/python -m eval.plots eval/results/baseline_0901_to_1001.json               # figure
.venv/bin/python -m components.decision.autoresearch.build_cells                     # ratchet data (cached in .cache/)
.venv/bin/python -m components.decision.autoresearch.ratchet                         # ratchet loop → results.tsv
.venv/bin/python components/feed/live_recorder.py --out .data/live --hours 1         # live 12-venue recorder
.venv/bin/python -m eval.live_latency                                                # feed latency from this machine
```

## Layout
- `architecture/` — components and contracts (`components.md`, `contracts/`), ADRs.
- `components/<name>/` — code per component: feed, latency, detector, decay, decision (+ `autoresearch/`), sim, costs. The book and fair-value baselines are currently inlined in `detector/cross.py` for speed.
- `eval/` — the end-to-end harness, plots, and `results/`, which holds every number quoted in the deliverables.
- `research/` — `landscape.md`, `notes/`, `components/`.
- `.data/`, `.cache/` — gitignored downloads, recordings and caches.

All P&L figures are **simulated**. Assumptions are listed in each results file: pre-positioned inventory, IOC legs at top of book, order latency = feed latency = δ in sweeps, and uniform fee levels.
