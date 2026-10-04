# Approach diagram (Round-1 optional 1-page architecture) — P7 regime-aware look-ahead allocator

```mermaid
flowchart TB
  subgraph WORLD["Multi-agent dispatch world (PettingZoo ParallelEnv, built and tested)"]
    D["Demand<br/>synthetic: Poisson per zone x diurnal cycle + abrupt shocks + gradual drift + spikes<br/>(labelled change points)<br/>real: NYC TLC yellow-taxi trips, July 2025 (Manhattan, thinned)"]
    S["Simulator: K units = agents on a 5x5 zone grid<br/>same-zone FIFO matching · patience P · trips relocate units<br/>repositioning lead time L steps per hop"]
    D --> S
  end

  subgraph AGENT["Look-ahead allocator: centralised cooperative planning, per-unit execution"]
    N["Nowcaster<br/>observed arrivals per zone"]
    CD["Change detector (spike)<br/>two-sided Poisson CUSUM per zone<br/>alarm + onset + post-change rate"]
    F["Forecaster (spike)<br/>learned time-of-day profile x level<br/>slow EWMA (drift) / restart at running post-change mean (shock)"]
    P["MPC planner<br/>time-expanded LP over H = L + 6 steps:<br/>hop flows (arrive after L) · service flows via OD matrix<br/>backlog with fluid abandonment (1/P per step)<br/>HiGHS, warm-started each step"]
    C["Coordinator<br/>zone flows to per-unit move orders"]
    N --> CD --> F --> P --> C
  end

  S -- "fleet state: idle, en-route ETAs, queues" --> P
  S -- "arrivals" --> N
  C -- "one move order per idle agent" --> S

  subgraph BASE["Baselines and ablations (same API, same seeds)"]
    R["Rules: static shares · greedy neighbour (decentralised) · reactive proportional"]
    AB["Same-LP ablations: myopic (H = L+1) · queue-only (no demand forecast) · EWMA (no detector)"]
    O["True-rate MPC: fed the true expected rates<br/>(a perfect forecast, not an upper bound)"]
  end
  BASE -.-> S

  subgraph EVAL["Evaluation (pre-registered)"]
    M["Served fraction · requests lost per shock (2 h) · recovery (censored) · empty hops per served<br/>per component: detection delay, false alarms/zone-day, post-shock forecast error"]
    ST["Fresh test seeds 200-229 · reference rule fixed on tuning seeds · paired bootstrap CIs · Wilcoxon + Holm<br/>(L, P) phase diagram · week and month horizons (one shock per day + drift + spikes) · NYC replay"]
  end
  S --> M --> ST
```

**Reading guide.**
- **Each step:** arrivals are observed; the detector updates; the forecaster smooths (drift) or restarts (shock); the LP plans H steps ahead using known future supply (units about to free up); only the first step is executed. Then the loop repeats.
- **What the ablations isolate:**
  - *myopic* — the value of the planning horizon;
  - *queue-only* — the value of any demand forecast;
  - *EWMA* — the value of the change detector;
  - *true-rate MPC* — the most a better forecast could add.
- **The (L, P) sweep** shows where each layer pays.
