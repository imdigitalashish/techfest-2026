# P7 landscape — state of the art and what companies ship today

> Perceptron 2026 · Problem 7 "Splitting a shared resource when demand keeps changing". Written 2026-10-04 06:40 IST by the project lead.
> **Provenance rule:** every source below was opened on 2026-10-04 by a research worker, who recorded the URL and the facts in `research/raw/*.md`. Numbers are quoted as the source states them. Anything not opened is under *Coverage gaps / UNVERIFIED*. The night's network was saturated (most worker requests failed with HTTP 408), so coverage is **partial**. The gaps are listed explicitly rather than filled from memory.

Raw notes: [papers-fleet-dispatch.md](raw/papers-fleet-dispatch.md) (15 sources) · [papers-nonstationarity.md](raw/papers-nonstationarity.md) (6) · [companies-ship-today.md](raw/companies-ship-today.md) (9) · [evaluation-and-envs.md](raw/evaluation-and-envs.md) (3 papers + 8 repos).

## 1. The crux (our framing)

Moving a resource takes time: a vehicle has to drive, a GPU replica has to load a model, a robot has to cross a warehouse. Demand, meanwhile, waits only so long before it abandons. A purely reactive allocator always arrives one lead time too late. Look-ahead fixes that, but only if its demand model is right, and a sudden shift is exactly the moment the model breaks. The core difficulty is therefore a three-way coupling:
1. **Detect quickly, but not jumpily.** Detect a regime change fast without chasing Poisson noise (the stability–plasticity trade-off; CUSUM's detection delay vs false-alarm run length).
2. **Plan over the lead time.** Plan moves over a horizon at least as long as the reallocation lead time, using known future supply (units about to free up) and the trip flows that relocate units.
3. **Coordinate the agents.** Coordinate many units so they don't all chase the same hotspot (herding) and so the cost of moving (empty travel) is weighed against expected service.

## 2. Fleet rebalancing and dispatch: research state of the art

| # | Work | Venue | Mechanism | Key reported number | Maturity |
|---|---|---|---|---|---|
| 1 | Iglesias, Rossi, Wang, Hallac, Leskovec, Pavone — Data-driven MPC for AMoD ([arXiv 1709.07032](https://arxiv.org/abs/1709.07032)) | ICRA 2018 | LSTM demand forecast feeding a rebalancing MPC | mean wait time cut "by up to 89.6%"; MPC cost independent of #customers/#vehicles | paper |
| 2 | Gammelli et al. — Graph-NN RL for AMoD ([2104.11434](https://arxiv.org/abs/2104.11434)) | CDC 2021 | GNN policy outputs a desired vehicle distribution; an LP turns it into flows | "promising zero-shot transfer" (no headline % in abstract) | paper |
| 3 | Gammelli et al. — Graph meta-RL for transferable AMoD ([2202.07147](https://arxiv.org/abs/2202.07147)) | KDD 2022 | Recurrent GNN actor-critic meta-RL | "near-optimal performance on unseen cities"; explicitly targets **distribution shifts** (special events, unexpected congestion, dynamic pricing) | paper |
| 4 | Schmidt, Gammelli, Pereira, Rodrigues — Offline RL for fleets ([2302.14833](https://arxiv.org/abs/2302.14833)) | arXiv 2023 | Offline RL from logged data | on par with online RL; sample-efficient fine-tuning | paper |
| 5 | Gammelli et al. — Real-time control of E-AMoD via graph RL ([2311.05780](https://arxiv.org/abs/2311.05780)) | 2023/2024 | **Bi-level**: RL picks the desired next state, an LP solves feasible flows | "up to 89% of theoretically-optimal profit", ">100x speedup" vs optimal LP (SF + NYC data) | paper |
| 6 | Tresca, …, Gammelli, Pavone — **RL4AMoD** benchmark ([2504.06125](https://arxiv.org/abs/2504.06125), [code](https://github.com/StanfordASL/RL4AMOD)) | arXiv 2025 | Open graph-RL + OR framework: benchmarks, datasets, simulators at several fidelities | — | code |
| 7 | Li, …, Pavone, Frazzoli, Zardini — Reproducibility in AMoD control ([2506.07345](https://arxiv.org/abs/2506.07345)) | arXiv 2025 | Survey + reproducibility checklist | documents field-wide irreproducibility sources | paper |
| 8 | Toft, Schmidt, Gammelli, Rodrigues — Competitive multi-operator RL, pricing + rebalancing ([2603.05000](https://arxiv.org/abs/2603.05000)) | arXiv 2026 | Multi-operator competitive RL | agents "robust to the additional stochasticity of competition" | paper |
| 9 | Li et al. (DiDi) — Mean-field MARL order dispatch ([1901.11454](https://arxiv.org/abs/1901.11454)) | WWW 2019 | Mean-field MARL | "significant improvements… on GMV and order response rate"; targets rush-hour supply–demand gap | paper |
| 10 | Xu et al. (DiDi) — Learning and planning for large-scale order dispatch (DOI 10.1145/3219819.3219824) | KDD 2018 | Offline spatio-temporal value table + real-time planning (matching) | deployed | production |
| 11 | Tang et al. (DiDi) — "Value function is all you need" ([2105.08791](https://arxiv.org/abs/2105.08791)) | KDD 2021 | One shared value function drives dispatch + repositioning; online updates + offline ensemble | — | paper (DiDi data) |
| 12 | Qin et al. — RL order dispatch at DiDi (DOI 10.1287/INTE.2020.1047) | INFORMS J. Appl. Anal. 2020 | Combinatorial optimisation → SMDP + deep RL at "tens of millions [of matches] per day" | — | production |
| 13 | Azagirre et al. — RL at Lyft ([2310.13810](https://arxiv.org/abs/2310.13810)) | INFORMS J. Appl. Anal. 2024 | Online RL estimating drivers' future earnings inside matching | "first documented implementation of a ridesharing matching algorithm that can learn and improve in real time" | production |
| 14 | Non-myopic ride-pooling via simulation-informed RL ([2510.25796](https://arxiv.org/abs/2510.25796)) | arXiv 2025 | Extends Xu 2018 to pooling (n-step TD) | "+8.4% service rate" vs myopic (NYC taxi data) | paper |
| 15 | Spatio-temporal pricing + fleet management with a bounded optimality gap ([2206.03298](https://arxiv.org/abs/2206.03298)) | arXiv 2022/23 | Decomposition + DP | joint pricing + rebalancing adds only a minor gain under *accurately predicted* demand, but "substantially improved profits" under *unanticipated* demand | paper |

**Reading.**
- The research frontier is **hybrid learning + optimisation** (rows 2, 5, 10): a learned component decides where supply should be, and an LP/MIP makes it feasible. RL4AMoD (row 6) is the open reference stack.
- Non-stationarity is acknowledged (rows 3, 15) but handled implicitly, through meta-learning or re-solving. None of the works opened here couples an explicit **change detector** to the planner or reports a **post-shock recovery metric**. *(Partial survey; see §7.)*
- Row 15 is the closest evidence that *unanticipated* demand is where active control pays off most. That supports making the shock window our primary evaluation slice.

## 3. Non-stationarity: detect → calibrate → decide

| # | Work | Venue | What it gives us | Source wording (abstract) |
|---|---|---|---|---|
| 1 | Adams & MacKay — Bayesian Online Changepoint Detection ([0710.3742](https://arxiv.org/abs/0710.3742)) | arXiv 2007 | Run-length posterior; exact online inference for exponential-family streams (Poisson fits) | — |
| 2 | Altamirano, Briol, Knoblauch — Robust & scalable BOCPD ([2302.04759](https://arxiv.org/abs/2302.04759)) | ICML 2023 | BOCPD that is robust to outliers (relevant to transient spikes) | — |
| 3 | Gibbs & Candès — Adaptive Conformal Inference ([2106.00170](https://arxiv.org/abs/2106.00170)) | NeurIPS 2021 | Online update of the miscoverage level | "provably achieves the desired coverage frequency over long-time intervals irrespective of the true data generating process" |
| 4 | Gibbs & Candès — DtACI ([2208.08401](https://arxiv.org/abs/2208.08401)) | arXiv 2022 | Removes ACI's fixed step size (adapts it online) | — |
| 5 | Angelopoulos, Candès, Tibshirani — Conformal PID control ([2307.16895](https://arxiv.org/abs/2307.16895)) | NeurIPS 2023 | P/I/D feedback on the conformal score; tested on **count data** (COVID-19 death counts) | "improvement in coverage over the ensemble forecaster used in official CDC communications" |
| 6 | Lekeufack, Angelopoulos, Bajcsy, … — Conformal Decision Theory ([2310.05921](https://arxiv.org/abs/2310.05921)) | ICRA 2024 | Calibrates *decisions* (risk), not just intervals | decisions have "provable statistical guarantees of having low risk without any assumptions on the world model… observations need not be I.I.D." |

**Reading.** The pieces exist separately: change detection (rows 1–2), distribution-free online calibration (rows 3–5) and risk-calibrated decisions (row 6). In this partial scan we found **no work that couples a change detector's state with conformal-calibrated safety buffers inside a rolling-horizon resource allocator.** That is a candidate innovation, labelled *not found in a partial search*, not "novel".

## 3b. Predict-then-optimise: why a better forecast can hurt (added 2026-10-04 10:50 IST)

| Work | Venue (verified via Crossref) | What it says (arXiv abstract, opened 2026-10-04) | Relevance |
|---|---|---|---|
| Elmachtoub & Grigas — Smart "Predict, then Optimize" ([arXiv 1710.08005](https://arxiv.org/abs/1710.08005)) | Management Science 2022, DOI 10.1287/mnsc.2020.3922 | ML tools "minimize prediction error and do not account for how the predictions will be used in the downstream optimization problem"; proposes SPO, which "directly leverages the optimization problem structure" | Our phase-v2 finding: with an abandonment-aware LP, a *more accurate* (true-rate) forecast lowers served fraction by 1.1–1.5 pp at long lead times. |
| Wilder, Dilkina & Tambe — Decision-focused learning for combinatorial optimisation ([arXiv 1809.05504](https://arxiv.org/abs/1809.05504)) | AAAI 2019, DOI 10.1609/aaai.v33i01.33011658 | the training loss "may easily be misaligned with the end goal, which is to make the best decisions possible" | Motivates tuning forecast *trust* for served fraction, not forecast error (spike A′). |
| Page — Continuous inspection schemes (CUSUM) | Biometrika 41(1–2):100–115, 1954, DOI 10.1093/biomet/41.1-2.100 (bibliographic record verified via Crossref; full text paywalled, not opened) | — | Origin of the CUSUM used in C4. |

## 4. Evaluation methodology (what a quant judge will look for)
- **Agarwal et al. 2021** ([2108.13264](https://arxiv.org/abs/2108.13264), NeurIPS Outstanding Paper): report interval estimates, not point estimates; use performance profiles and the interquartile mean (IQM). Rankings change once uncertainty is accounted for. Library: rliable.
- **Gorsane et al. 2022** ([2209.10485](https://arxiv.org/abs/2209.10485)): a meta-analysis of 75 cooperative-MARL papers (2016–2022) finds "worrying trends" in evaluation and proposes a standard protocol. *Protocol details not opened — UNVERIFIED.*
- **van den Burg & Williams** ([2003.06222](https://arxiv.org/abs/2003.06222)): TCPD, 37 real series × 5 annotators, 14 change-point algorithms benchmarked. Use it to score our detector (F1 with margin) — *formula not yet opened*.
- **Our protocol** (implemented in `eval/`):
  - common random numbers: every policy sees the identical request stream per seed;
  - tuning seeds (0–99) are separate from frozen test seeds (100+);
  - paired per-seed differences against the best rule-based baseline, with bootstrap 95% CIs, the Wilcoxon signed-rank test and Holm correction;
  - shock-window metrics: requests lost in the 120 steps after onset (the resilience-triangle area) and time-to-recover.

## 5. Environments and code (GitHub API, 2026-10-04)

| Repo | Stars | Last push | Licence | Fit |
|---|---|---|---|---|
| Farama-Foundation/PettingZoo | 3524 | 2026-10-03 | MIT | **Our API** (ParallelEnv); we pin 1.27.0 |
| pytorch/rl (TorchRL) | 3589 | 2026-10-03 | MIT | MAPPO/IPPO for the RL comparator |
| facebookresearch/BenchMARL | 668 | 2026-02-07 | MIT | Reference for seed-sweep harness design |
| proroklab/VectorizedMultiAgentSimulator (VMAS) | 617 | 2026-05-19 | GPL-3.0 | Physics sim, poor fit for zone/queue dispatch |
| StanfordASL/RL4AMOD | (not queried) | — | — | Graph-RL + LP reference for AMoD; candidate real-city backend |

**Decision (ADR-level):** we build our own lightweight PettingZoo ParallelEnv. It is fast enough for long horizons × many seeds in numpy, lets us inject shocks and drifts with ground-truth labels, and avoids GPL coupling. RL4AMoD stays the path to real-city data in the finals.

## 6. What companies ship today

| Company | Domain | What ships | Look-ahead? | How shocks are handled | Key fact (as stated) | Source |
|---|---|---|---|---|---|---|
| Kubernetes | Compute | HorizontalPodAutoscaler control loop | **No** (reactive) | Downscale stabilisation window (default 5 min) | — | [raw notes](raw/companies-ship-today.md) |
| Knative | Serverless compute | KPA with stable + **panic** windows | No (fast secondary window) | Panic mode when traffic exceeds 200% of capacity within the panic window; scales up aggressively, never down | stable window 60 s; panic window 6 s | [docs](https://knative.dev/docs/serving/autoscaling/kpa-specific/) |
| AWS EC2 Auto Scaling | VM fleets | Predictive scaling on top of reactive policies | **Yes** | Forecasts only ever scale **out**; spikes are left to reactive policies | hourly forecast for the next 48 h, refreshed every 6 h, needs ≥24 h of history | [docs](https://docs.aws.amazon.com/autoscaling/ec2/userguide/predictive-scaling-policy-overview.html) |
| Microsoft Azure VMSS | VM fleets | Predictive autoscale on top of mandatory reactive rules | **Yes** | "Predictive autoscale supports scale-out only" | ≥7 days of history; pre-launch 5–60 min ahead; CPU metric only | [docs](https://learn.microsoft.com/en-us/azure/azure-monitor/autoscale/autoscale-predictive) |
| NVIDIA Dynamo Planner | LLM serving GPUs | Rebalances prefill/decode GPU pools | No (heuristic thresholds) | Acts when KV-block utilisation or prefill queue depth crosses manual thresholds | — | [blog](https://developer.nvidia.com/blog/nvidia-dynamo-adds-gpu-autoscaling-kubernetes-automation-and-networking-optimizations/) |
| AIBrix (ByteDance / vLLM) | LLM serving | PodAutoscaler (HPA/KPA/APA) + opt-in predictive projector | Partial | `final = max(reactive, projected)`; prediction can only raise | horizon 120 s; docs say the predictive block is currently "accepted and validated only" | [docs](https://aibrix.readthedocs.io/latest/features/autoscaling/predictive-autoscaling.html) |
| Uber | Ride-hailing | Driver guidance heatmap from a deep probabilistic model | **Yes** (next hour) | Continuous re-forecasting every 10 min | XGBoost → Gaussian NLL → Gaussian mixture model for earnings per hour | [blog](https://www.uber.com/us/en/blog/enhancing-ubers-guidance-heatmap-with-deep-probabilistic-models/) |
| Lyft | Ride-hailing | Online-RL matching (future driver earnings) | **Yes** (value look-ahead) | Online learning; no explicit shock mechanism in the abstract | "first documented… learn and improve in real time" | [arXiv 2310.13810](https://arxiv.org/abs/2310.13810) |
| DoorDash | Food delivery | DeepRed: ML outcome predictions → MIP assignment, plus a simulation platform | Partial | Names rain/traffic as supply shocks, handled through optimisation trade-offs | ML models feed the optimisation layer (quoted in raw notes) | [blog (archive)](https://careersatdoordash.com/blog/using-ml-and-optimization-to-solve-doordashs-dispatch-problem/) |

**The production pattern.** Every production system above is **forecast + optimiser + reactive guardrail**:
- AWS and Azure forecast but only scale out, and keep reactive rules mandatory.
- Knative adds a "panic" window for bursts.
- AIBrix takes `max(reactive, predicted)`.
- Ride-hailing and delivery firms put learned value or forecast models in front of an optimiser (DoorDash MIP, DiDi planning) or inside an online-RL matcher (Lyft).

Pure end-to-end RL allocation is not what ships. Learning appears as a value or forecast input to optimisation.

**Where we borrow, and where we try to beat it.**
- We **borrow** the production structure: forecaster → optimiser → reactive guardrail. Our MPC re-plans every step on the observed queue, so the queue acts as the reactive guardrail inside the planner.
- We **beat the guardrail heuristics**. The production shock responses are fixed-threshold heuristics: Knative's 200% panic threshold, Dynamo's manual thresholds, AWS/Azure "scale-out only". We replace them with an explicit statistical change detector (Poisson CUSUM, later BOCPD) whose false-alarm rate is a *tunable, measured* quantity. We also plan symmetric moves (supply can be pulled out of a cooling zone, not only added).
- We **add what none of them report**: requests lost per shock with confidence intervals over many pre-registered seeds, plus same-planner ablations against a true-rate-forecast reference (a perfect forecast, not an upper bound).

## 7. Coverage gaps / UNVERIFIED (be honest)
- **Compute-cluster papers thread failed** (worker died on network errors). These are *not opened tonight, so not cited*: Llumnix, ServerlessLLM, DistServe, Splitwise (and its Azure LLM inference traces), Google Autopilot, Resource Central, "Serverless in the Wild" (Azure Functions trace), DeepRM, Decima, Gavel, Pollux, square-root staffing. Re-run when the network recovers.
- **Social signal (X/HN/Reddit) and competitions** (KDD Cup 2020 DiDi dispatch track, Flatland, League of Robot Runners): worker failed; **nothing cited**.
- **Not opened this session:** India-specific delivery (Swiggy, Zomato), Amazon Robotics DeepFleet, Gorsane protocol internals, TCPD metric formulas.
- Fleet-papers TL;DR rows come from abstracts and metadata. Full-text details (baselines, horizons, how shocks are evaluated) are **UNVERIFIED** beyond what the abstracts say.
