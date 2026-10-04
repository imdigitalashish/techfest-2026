# Architecture (1-page diagram for the Round-1 submission)

Decisions are made on what we have *received*; fills happen on what the exchange *actually had* when our order arrived. The gap between the two is the latency budget.

```mermaid
flowchart LR
  subgraph SRC["Market data (real)"]
    T["Tardis.dev tick quotes<br/>exchange + collector timestamps<br/>9 BTC venues, 1st of each month"]
    W["Live websocket recorder<br/>12 venues, receive timestamps<br/>+ NTP offset log"]
  end
  T --> N["C1 feed<br/>normalise → QuoteFrame"]
  W --> N
  N --> LAT["C2 latency<br/>feed-latency quantiles per venue<br/>order latency (assumed → measured)"]
  N --> BK["C3 book<br/>as-of top of book on the<br/>receive clock, quote ages"]
  BK --> FV["C4 fair value<br/>basis (USD/USDT, spot/perp)<br/>lead–lag (Hayashi–Yoshida)"]
  BK --> DET["C6 detector<br/>executable cross bid_A − ask_B<br/>− basis − fees, size-capped"]
  FV --> DET
  FEE["C5 costs<br/>fee levels 0/1/2/5 bps + official tiers"] --> DET
  DET --> DEC["C7 decay<br/>survival S(t | pair, age, edge)<br/>half-lives · MVP report"]
  DET --> POL
  DEC --> POL["C8 DECISION (spike)<br/>LEV(x, L) = E[P&L | x, latency]<br/>EV = S(L)·net − (1−S(L))·λ<br/>act now · wait Δ* · skip; rank"]
  LAT --> POL
  FEE --> POL
  POL --> SIM["C9 simulator<br/>legs fill vs exchange-time book<br/>at t_decide + L_order[v]<br/>partial fills, unwind loss"]
  N -. "exchange-time truth" .-> SIM
  LAT --> SIM
  SIM --> EV["C11 eval<br/>latency–P&L frontier · decay curves<br/>ranking quality · bootstrap CIs"]
  SIM -. "labels" .-> POL
  POL --> PT["C10 paper trader<br/>live feed → same path<br/>dashboard"]
  W --> PT
```

| Component | Isolated metric | Result (from committed results) |
|---|---|---|
| C6 detector | AUC-PR of "profitable at latency L" | {{n_episodes}} episodes ≥ 1 bp over fair basis on the held-out day 2026-10-01 |
| C7 decay | integrated Brier (log-t), C-index; median lifetime with hour-block CI | median {{median_life_ms}} ms (95% CI {{median_ci_lo}}–{{median_ci_hi}}); {{n_months}} monthly medians {{month_median_min}}–{{month_median_max}} ms |
| C8 decision (spike) | simulated P&L at (latency, fee) | pre-registered walk-forward, LEV − tuned threshold: {{wf_mean}}/day, 95% t-CI {{wf_tci}}, {{wf_pos}}/{{wf_n}} months positive — {{wf_verdict}} |
| C8 compiled step | p50/p99 per decision | {{dec_p50_us}} µs / {{dec_p99_us}} µs (Numba, exact vs scikit-learn) |
| C2 latency | pinball loss of quantiles | Tardis collector p50 {{feed_fast_ms}} ms (Binance perp) to {{feed_slow_ms}} ms; Mac in India p05 {{mac_p05_min}}–{{mac_p05_max}} ms |

Sources: `eval/results/headline.json` (rendered by `deliverables/render.py`; checked by `eval/check_docs.py`).
