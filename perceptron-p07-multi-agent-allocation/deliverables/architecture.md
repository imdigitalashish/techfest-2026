# Approach diagram (Round-1 optional 1-page architecture) — P7 decision-aware look-ahead allocator

```mermaid
flowchart TB
  subgraph WORLD["Multi-agent dispatch world (PettingZoo ParallelEnv, built and tested)"]
    D["Demand<br/>synthetic: Poisson per zone x diurnal cycle + abrupt shocks + gradual drift + spikes<br/>(labelled change points)<br/>real: NYC TLC yellow-taxi trips, July 2025 (Manhattan, thinned)"]
    S["Simulator: K units = agents on a 5x5 zone grid<br/>same-zone FIFO matching · patience P · trips relocate units<br/>repositioning lead time L steps per hop"]
    D --> S
  end

  subgraph AGENT["Look-ahead allocator: centralised cooperative planning, per-unit execution"]
    N["Nowcaster<br/>observed arrivals per zone"]
    CD["Change detector<br/>two-sided Poisson CUSUM per zone<br/>regime state: alarm, onset, post-change rate"]
    F["Forecaster<br/>learned time-of-day profile x per-zone level (EWMA)"]
    TG["Trust gate (spike)<br/>planner sees trust x forecast<br/>tested: one global trust (exploratory sweep)<br/>planned: trust from calibrated uncertainty + regime state<br/>tuned for served fraction, not forecast error"]
    P["MPC planner<br/>time-expanded LP over H = L + 6 steps:<br/>hop flows (arrive after L) · service flows via OD matrix<br/>backlog with fluid abandonment (1/P per step)<br/>HiGHS, warm-started each step"]
    C["Coordinator<br/>zone flows to per-unit move orders"]
    N --> F --> TG --> P --> C
    N --> CD --> TG
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
- **Each step:** arrivals are observed; the forecaster and the detector update; the trust gate scales the forecast per zone; the LP plans H steps ahead using known future supply (units about to free up) and the current queues; only the first step is executed. Then the loop repeats.
- **What the ablations isolate:**
  - *myopic* — the value of the planning horizon;
  - *queue-only* (trust 0) — the value of any demand forecast;
  - *trust 1* — certainty equivalence;
  - *true-rate MPC* — what a perfect forecast does inside this planner (it can hurt).
- **The (L, P) sweep** shows where each layer pays.
