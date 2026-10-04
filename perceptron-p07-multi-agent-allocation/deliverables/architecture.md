# Approach diagram (Round-1 optional 1-page architecture) — P7 shock-aware look-ahead allocator

```mermaid
flowchart TB
  subgraph WORLD["Multi-agent dispatch world (PettingZoo ParallelEnv, built)"]
    D["Demand generator<br/>Poisson per zone x diurnal cycle<br/>+ abrupt shock + gradual drift + spikes<br/>(ground-truth change labels, common random numbers)"]
    S["Simulator<br/>K resource units = agents on a zone grid<br/>travel 1 step/hop · FIFO queues · patience P · trips relocate units"]
    D --> S
  end

  subgraph AGENT["Look-ahead allocator (one decision per step)"]
    N["Nowcaster<br/>observed arrivals per zone"]
    CD["Change detector (spike)<br/>two-sided Poisson CUSUM to BOCPD<br/>alarm + onset + post-change rate<br/>tunable false-alarm rate"]
    F["Forecaster (spike)<br/>learned time-of-day profile x level<br/>slow EWMA (drift) / restart on alarm (shock)<br/>+ conformal upper band (safety stock)"]
    P["MPC planner<br/>time-expanded LP over H steps:<br/>hop flows · service flows via OD matrix · backlog<br/>max served - move cost - wait cost (HiGHS)"]
    C["Coordinator<br/>zone flows to per-unit orders<br/>(LP dual prices for a decentralised / auction variant)"]
    N --> CD --> F --> P --> C
  end

  S -- "fleet state: idle, en-route, queues" --> P
  S -- "arrivals" --> N
  C -- "move orders (one per idle agent)" --> S

  subgraph BASE["Baselines"]
    R1["Static historical shares"]
    R2["Greedy neighbour rule (decentralised)"]
    R3["Reactive proportional rebalancing (30-min window)"]
    RL["RL comparator: MAPPO/IPPO (stretch)"]
    O["Oracle MPC on true rates (regret reference)"]
  end
  BASE -. "same API, same seeds" .-> S

  subgraph EVAL["Evaluation harness"]
    M["Served fraction · demand lost in 2 h after shock · time-to-recover<br/>wait p50/p95 · empty moves · planner latency<br/>per component: detection delay at fixed ARL0, post-shock forecast error"]
    ST["Frozen test seeds ≥ 20 · paired bootstrap CIs · IQM · Wilcoxon + Holm<br/>scenarios: stationary / shock / drift / shock+drift / spikes<br/>sweep: lead time L vs patience P"]
  end
  S --> M --> ST
```

**Reading guide.**
- One step of the loop, in order: arrivals are observed; the detector updates; the forecaster restarts or smooths; the MPC solves an H-step LP using the units that will free up; only the first step of the plan is executed; then the loop repeats.
- Rule-based baselines plug into the same API, which isolates the value of each layer:
  - planner without forecast,
  - forecast without detector,
  - detector + forecast + planner,
  - oracle.
