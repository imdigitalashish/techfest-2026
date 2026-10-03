# Fleet Rebalancing / Order Dispatch / AMoD under Time-Varying Demand — Research Notes

Status: IN PROGRESS (being written incrementally; partial findings persisted after every 1-2 sources)
Access date for all sources below: 2026-10-04
Scope: Perceptron 2026 Problem 7 — multi-agent resource reallocation under shifting demand, look-ahead vs static baseline.

---

## TL;DR (for our design)

_(to be filled in once enough sources are gathered)_

---

## Sources table

| # | Title | Venue/Year | URL | Maturity | Key number |
|---|-------|------------|-----|----------|------------|
| 1 | Data-Driven Model Predictive Control of AMoD Systems (Iglesias, Rossi, Wang, Hallac, Leskovec, Pavone) | ICRA 2018 | https://arxiv.org/abs/1709.07032 | paper-only | MPC+LSTM forecast cuts mean wait time by **up to 89.6%**; MPC compute cost independent of #customers/#vehicles |
| 2 | Graph Neural Network RL for AMoD (Gammelli, Yang, Harrison, Rodrigues, Pereira, Pavone) | CDC 2021 | https://arxiv.org/abs/2104.11434 | paper-only | GNN-based RL policy; reports "promising zero-shot transfer" for inter-city generalization, service-area expansion (no single headline % in abstract) |
| 3 | Graph Meta-RL for Transferable AMoD (Gammelli, Yang, Harrison, Rodrigues, Pereira, Pavone) | KDD 2022 | https://arxiv.org/abs/2202.07147 | paper-only | Meta-RL (recurrent GNN actor-critic) achieves "near-optimal performance on unseen cities" from small adaptation data; explicitly targets robustness to **distribution shifts** (special events, unexpected congestion, dynamic pricing) |
| 4 | Learning to Control Autonomous Fleets from Observation via Offline RL (Schmidt, Gammelli, Pereira, Rodrigues) | arXiv 2023 (2302.14833) | https://arxiv.org/abs/2302.14833 | paper-only | Offline-RL-only control (i) on par with online RL, (ii) sample-efficient online fine-tuning, (iii) removes need for complex simulators |
| 5 | Real-time Control of E-AMoD via Graph RL (Gammelli et al.) | arXiv 2023 / journal version 2024 (2311.05780) | https://arxiv.org/abs/2311.05780 | paper-only | **Bi-level**: GNN-RL picks desired next state in space-charge-time graph → LP solves feasible flows. Real SF+NYC data: **up to 89% of theoretically-optimal profit**, **>100x speedup** vs. optimal LP; outperforms best heuristic |
| 6 | Robo-taxi Fleet Coordination at Scale via Reinforcement Learning / **RL4AMoD** benchmark (Tresca, Schmidt, Harrison, Rodrigues, Zardini, Gammelli, Pavone) | arXiv 2025 (2504.06125) | https://arxiv.org/abs/2504.06125 | **code** (https://github.com/StanfordASL/RL4AMOD) | Open-source graph-RL+OR framework; releases "benchmarks, datasets, and simulators" across "diverse simulation fidelities and scenarios" for standardized AMoD comparison |
| 7 | Reproducibility in the Control of AMoD Systems (Li, Alharbi, Gammelli, Harrison, Rodrigues, Schiffer, Pavone, Frazzoli, Zhao, Zardini) | arXiv 2025 (2506.07345) | https://arxiv.org/abs/2506.07345 | paper-only | Survey + "reproducibility checklist" across AMoD modeling/control/sim/eval; documents common sources of irreproducibility field-wide |
| 8 | Competitive Multi-Operator RL for Joint Pricing and Fleet Rebalancing in AMoD (Toft, Schmidt, Gammelli, Rodrigues) | arXiv 2026 (2603.05000) | https://arxiv.org/abs/2603.05000 | paper-only | First multi-operator competitive RL (discrete-choice passenger allocation); real multi-city data; learning agents are "robust to the additional stochasticity of competition" |
| 9 | Efficient Ridesharing Order Dispatching with Mean Field Multi-Agent RL (Li, Qin, Jiao, Yang, Wang, Wang, Wu, Ye) | WWW 2019 | https://arxiv.org/abs/1901.11454 | paper-only | MARL + mean-field approximation for order dispatch; "significant improvements... on GMV and order response rate" vs. strong baselines; explicitly "alleviate[s] the supply-demand gap during rush hours" |
| 10 | Large-Scale Order Dispatch in On-Demand Ride-Hailing Platforms: A Learning and Planning Approach (Xu, Li, Guan, Zhang, Li, Nan, Liu, Bian, Ye) | KDD 2018 | DOI 10.1145/3219819.3219824 (Semantic Scholar record; DBLP conf/kdd/XuLGZLNLBY18) | **production** | Two-stage: (1) offline spatiotemporal value table of driver state from historical demand/supply, (2) real-time planning step valuing each driver-order pair by immediate reward + future gain, dispatched via combinatorial optimization; "successfully deployed in the production system of Didi Chuxing" with online A/B tests |
| 11 | Value Function is All You Need: A Unified Learning Framework for Ride Hailing Platforms (Tang, Zhang, **Qin**, Wang, Shi, Song, Tong, Zhu, Ye) | KDD 2021 | https://arxiv.org/abs/2105.08791 | paper-only (real-world datasets, DiDi-affiliated authors) | Single globally-shared value function (V1D3) jointly drives dispatch+repositioning; continuously updated online + periodic offline ensemble; **"outperforms the first prize winners of both dispatching and repositioning tracks in the KDD Cup 2020 RL competition"** |
| 12 | Ride-Hailing Order Dispatching at DiDi via Reinforcement Learning (Qin, Tang, Jiao, Zhang, Xu, Zhu, Ye) | INFORMS J. Appl. Anal. 2020 | DOI 10.1287/INTE.2020.1047 | **production** | Documents evolution from **combinatorial optimization → semi-Markov decision process (SMDP) + deep RL** for order dispatch at "tens of millions [of matches] per day"; discusses real system-response-time/reliability/multi-objective constraints and "real-world impact to the business" |
| 13 | A Better Match for Drivers and Riders: Reinforcement Learning at Lyft (Azagirre, Balwally, Candeli, Chamandy, Han, King, Lee, Loncaric, Martin et al.) | arXiv 2023 / INFORMS J. Appl. Anal. 2024 (2310.13810) | https://arxiv.org/abs/2310.13810 | **production** | **Online RL** estimating real-time future driver earnings for matching — "first documented implementation of a ridesharing matching algorithm that can learn and improve in real time"; **>$30M/year incremental revenue**, millions of extra rides served/year; **rolled out globally in 2021** |
| 14 | Non-myopic Matching and Rebalancing in Large-Scale On-Demand Ride-Pooling Systems Using Simulation-Informed RL (2025) | arXiv 2025 (2510.25796) | https://arxiv.org/abs/2510.25796 | paper-only (evaluated on NYC taxi data) | Extends Xu et al. (2018) learning+planning to ride-**pooling** via simulation-informed n-step TD learning. Non-myopic matching: **+8.4% service rate** vs. myopic, **>25% fleet-size reduction** at equal performance. Adding rebalancing: **-27.3% wait time, -12.5% in-vehicle time, +15.1% service rate** vs. matching-only |
| 15 | Spatiotemporal Pricing and Fleet Management of AMoD Networks: A Decomposition and Dynamic Programming Approach with Bounded Optimality Gap | arXiv 2022/2023 (2206.03298) | https://arxiv.org/abs/2206.03298 | paper-only | Joint pricing+rebalancing vs. pricing-alone gives only **minor** profit gain under accurately-predicted demand, but **"substantially improved profits"** during **unanticipated demand surges**; also finds shock impacts "dissipate faster" under the joint policy. Validated on **Manhattan** data; provides a **bounded optimality gap** (theoretical upper bound) |

---

## Notes per source

### 1. Iglesias et al., "Data-Driven Model Predictive Control of Autonomous Mobility-on-Demand Systems" — ICRA 2018
- URL opened: Semantic Scholar Graph API search (arXiv ID **1709.07032**, DOI 10.1109/ICRA.2018.8460966). Accessed 2026-10-04.
- Maturity: paper-only (simulation study).
- Key facts (numbers exactly as stated in abstract):
  1. Models AMoD as a **time-expanded network**; computes optimal rebalancing (preemptive repositioning) + minimum feasible fleet size for given demand.
  2. Devises an **MPC algorithm** using short-term demand forecasts (**LSTM**) from historical data to compute rebalancing strategies.
  3. Tested end-to-end on **real customer data from DiDi Chuxing**; "scales very well for large systems (computational complexity of the MPC algorithm does not depend on the number of customers and of vehicles in the system)" and "outperforms state-of-the-art rebalancing strategies by reducing the mean customer wait time by up to **89.6%**."
- Relevance: canonical "MPC + forecast" baseline family that Gammelli/Pavone RL papers benchmark against. Good baseline citation for rule-based/MPC comparison tier.

### 2. Gammelli et al., "Graph Neural Network Reinforcement Learning for Autonomous Mobility-on-Demand Systems" — CDC 2021
- URL opened: https://export.arxiv.org/api/query?id_list=2104.11434 (arXiv abstract via API). Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts:
  1. Casts AMoD rebalancing as a **node-wise decision-making problem** on a graph (nodes = city areas, edges = connectivity).
  2. Deep RL framework controls rebalancing through **graph neural networks**; policies are "significantly more transferable, generalizable, and scalable" than non-GNN approaches.
  3. Shows **zero-shot transfer**: inter-city generalization, service-area expansion, adaptation to complex urban topologies — no single headline % number in the abstract itself (would need body/PDF for numeric transfer gap).
- Relevance: origin paper of the Stanford ASL "graph-RL for AMoD" line; establishes the GNN-policy approach later extended to bi-level RL+LP (see #5).

### 3. Gammelli et al., "Graph Meta-Reinforcement Learning for Transferable Autonomous Mobility-on-Demand" — KDD 2022
- URL opened: https://export.arxiv.org/api/query?id_list=2202.07147 (arXiv API). Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts:
  1. Formalizes **multi-city AMoD as meta-RL**; actor-critic algorithm built on **recurrent graph neural networks**.
  2. Trained so "a small amount of experience within a new city will produce good system performance" (fast adaptation / few-shot).
  3. Explicitly claims robustness **"to distribution shifts common in real-world operations, such as special events, unexpected congestion, and dynamic pricing schemes"** — directly relevant to our non-stationary-demand angle; achieves "near-optimal performance on unseen cities" (no single numeric % gap given in abstract).
- Relevance: closest prior work to our MVP ask ("beats baseline when demand suddenly shifts") — meta-RL explicitly framed around adapting to shocks/regime change, though their "shift" is cross-city/context not necessarily within-episode abrupt shock.

### 4. Schmidt, Gammelli, Pereira, Rodrigues, "Learning to Control Autonomous Fleets from Observation via Offline Reinforcement Learning" — arXiv 2302.14833 (2023)
- URL opened: https://export.arxiv.org/api/query?id_list=2302.14833 (arXiv API, via search au:Gammelli AND abs:mobility). Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts:
  1. Formalizes AMoD control as **offline RL** — learns solely from logged historical data (no online interaction cost).
  2. Claims offline-only policies (i) **on par with online RL** performance, (ii) enable **sample-efficient online fine-tuning**, (iii) **eliminate need for complex simulation environments**.
  3. Positions offline RL as viable for "economically-critical systems" like mobility.
- Relevance: alternative training paradigm if we lack a fast simulator or want to bootstrap from historical dispatch logs instead of pure online RL.

### 5. Gammelli et al., "Real-time Control of Electric Autonomous Mobility-on-Demand Systems via Graph Reinforcement Learning" — arXiv 2311.05780 (ECC/journal ~2024)
- URL opened: https://export.arxiv.org/api/query?id_list=... via au:Gammelli search (arXiv API). Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts (numbers exactly as stated):
  1. **Bi-level formulation** explicitly stated: "(1) leverage a graph network-based RL agent to specify a desired next state in the space-charge graph, and (2) solve more tractable linear programs to best achieve the desired state while ensuring feasibility." — this is the precise "RL picks desired distribution, LP computes flows" design referenced in our brief.
  2. Real-world data from **San Francisco and New York City**: achieves "**up to 89% of the profits of the theoretically-optimal solution** while achieving **more than a 100x speedup** in computational time" vs. solving the full LP optimally.
  3. "Outperforms the best domain-specific heuristics" (comparable/better quality, much faster than exact optimization).
- Relevance: **this is the key mechanism match** for our MVP design — bi-level RL(desired state)+LP(flow realization), and it reports the exact kind of %-of-optimal and speedup metrics we should emulate when comparing our RL/planning agent vs. rule-based baseline and vs. an oracle/perfect-foresight LP.

### 6. Tresca, Schmidt, Harrison, Rodrigues, Zardini, Gammelli, Pavone, "Robo-taxi Fleet Coordination at Scale via Reinforcement Learning" (RL4AMoD) — arXiv 2504.06125 (2025)
- URL opened: arXiv API search au:Gammelli AND abs:mobility (fragment captured; title confirmed cross-referenced from the same date/author set as the earlier truncated entry). Accessed 2026-10-04.
- Maturity: **code** — open-source at https://github.com/StanfordASL/RL4AMOD (not yet cloned/inspected this session; URL unopened beyond the paper abstract, so treat repo contents as UNVERIFIED).
- Key facts:
  1. Unifies graph representation learning + RL + classical OR (LP) tools into one coordination framework ("exploits main strengths of graph representation learning, reinforcement learning, and classical operations research tools").
  2. "Extensive evaluations across diverse simulation fidelities and scenarios" — claims superior performance, computational efficiency, and generalizability vs. prior methods (no single headline % captured from this fragment).
  3. Explicitly released to **standardize benchmarking**: "publicly available benchmarks, datasets, and simulators for network-level coordination alongside an open-source codebase... to establish a standardized validation process for comparing methodologies."
- Relevance: likely the single most useful artifact for our hackathon — a maintained open-source AMoD RL+OR benchmark/codebase we could fork or imitate for our simulator + baseline + RL-agent harness. **Follow-up action (not yet done): open github.com/StanfordASL/RL4AMOD directly to check license, env API, and whether it already includes demand-shock scenarios.**

### 7. Li, Alharbi, Gammelli, Harrison, Rodrigues, Schiffer, Pavone, Frazzoli, Zhao, Zardini, "Reproducibility in the Control of Autonomous Mobility-on-Demand Systems" — arXiv 2506.07345 (2025)
- URL opened: arXiv API search au:Gammelli AND abs:mobility. Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts:
  1. "Systematic study of reproducibility in AMoD research" spanning **system modeling, control problems, simulation design, algorithm specification, and evaluation**.
  2. Surveys prevalent practices, identifies gaps, proposes a **structured framework + "reproducibility checklist"** to assess/improve reproducibility.
  3. Positions AMoD findings as generalizing "to a broader class of cyber-physical systems that rely on networked autonomy and data-driven control."
- Relevance: directly useful as a checklist for how to document our own eval protocol (baselines, metrics, simulator fidelity disclosures) so judges can trust our reported numbers — good meta-reference to cite in our writeup's methodology section.

### 8. Toft, Schmidt, Gammelli, Rodrigues, "Competitive Multi-Operator Reinforcement Learning for Joint Pricing and Fleet Rebalancing in AMoD Systems" — arXiv 2603.05000 (2026)
- URL opened: arXiv API search au:Gammelli AND abs:mobility. Accessed 2026-10-04.
- Maturity: paper-only.
- Key facts:
  1. **Two operators simultaneously learn pricing + fleet rebalancing policies**; uses **discrete choice theory** so passenger allocation/demand competition emerges endogenously from utility-maximizing choices.
  2. "Experiments using real-world data from multiple cities demonstrate that competition fundamentally alters learned behaviors, leading to lower prices and distinct fleet positioning patterns compared to monopolistic settings."
  3. Learning agents shown "robust to the additional stochasticity of competition," converging to effective policies despite "partially unobserved competitor strategies."
- Relevance: newest (2026) Gammelli-lineage follow-up found this session; shows the line of work is still active and moving toward multi-agent/competitive extensions — useful to namecheck as "most current" related work, though its non-stationarity is competitor-induced, not demand-shock-induced.

### 9. Li, Qin, Jiao, Yang, Wang, Wang, Wu, Ye, "Efficient Ridesharing Order Dispatching with Mean Field Multi-Agent Reinforcement Learning" — WWW 2019
- URL opened: https://export.arxiv.org/api/query (arXiv ID **1901.11454**, via search ti:"mean field" AND abs:"order dispatch"). Accessed 2026-10-04.
- Maturity: paper-only (uses "simulated experiments with real data").
- Key facts (as stated in abstract):
  1. Poses order dispatch as **multi-agent RL (MARL)**, distributed/decentralized by nature, vs. prior centralized single-agent RL which "can hardly model the complex interactions between drivers and orders."
  2. Uses **mean-field approximation**: simplifies local interactions by taking an "average action among neighborhoods," letting the method "globally captur[e] dynamic demand-supply variations by propagating many local interactions."
  3. "Extensive experiments have shown significant improvements of MARL order dispatching algorithms over several strong baselines on **gross merchandise volume (GMV)** and **order response rate** measures"; simulated real-data experiments show the approach can **"alleviate the supply-demand gap during the rush hours"** — i.e., explicitly targets a recurring demand surge/non-stationarity case.
- Relevance: exactly matches priority #4 (mean-field MARL dispatch). The "average neighborhood action" trick is a cheap way to make multi-agent dispatch tractable at fleet scale — relevant if our "robot swarm/fleet" MVP needs more than 1-2 agents coordinating. Rush-hour framing is the closest explicit "demand shock" handling among the classic (pre-2020) papers found.

### 10. Xu, Li, Guan, Zhang, Li, Nan, Liu, Bian, Ye, "Large-Scale Order Dispatch in On-Demand Ride-Hailing Platforms: A Learning and Planning Approach" — KDD 2018
- URL opened: https://api.semanticscholar.org/graph/v1/paper/search?query=large-scale+order+dispatch+ride-hailing+learning+planning+Xu (Semantic Scholar Graph API). DOI 10.1145/3219819.3219824, DBLP conf/kdd/XuLGZLNLBY18. Accessed 2026-10-04.
- Maturity: **production** (explicitly deployed).
- Key facts (as stated in abstract):
  1. Order dispatch modeled as a **large-scale sequential decision-making problem**; a **centralized algorithm** assigns orders to drivers "in a coordinated way," explicitly aiming for "a more efficient way to optimize resource utilization... in a global and more farsighted view" (i.e., look-ahead vs. myopic/greedy matching).
  2. Two-stage **"learning and planning"** design: (1) offline — summarize historical demand/supply into a **spatiotemporal quantization** = expected value of a driver being in a given state (akin to a learned value function / "distribution" signal); (2) online — a **real-time planning step** values each driver-order pair using both immediate reward and future gains, then solves dispatch via a **combinatorial optimization algorithm**.
  3. "Through extensive offline experiments and online AB tests, the proposed approach delivers remarkable improvement on the platform's efficiency and **has been successfully deployed in the production system of Didi Chuxing**" (no specific % lift captured in this abstract — would need the full paper/INFORMS write-up for the number).
- Relevance: matches priority #3 (DiDi Xu et al. KDD 2018). Structurally this is the ride-hailing analogue of the Gammelli "RL/value signal + LP/combinatorial-optimization" bi-level pattern — strong independent validation (at production scale) that splitting "value estimation" from "feasible assignment solving" is the dominant real-world architecture, not just an academic simplification.

### 11. Tang, Zhang, Qin, Wang, Shi, Song, Tong, Zhu, Ye, "Value Function is All You Need: A Unified Learning Framework for Ride Hailing Platforms" — KDD 2021
- URL opened: https://api.semanticscholar.org/graph/v1/paper/search?query=ride-hailing+order+dispatching+DiDi+Qin+2020+applied+analytics (Semantic Scholar Graph API). arXiv **2105.08791**, DOI 10.1145/3447548.3467096, DBLP conf/kdd/TangZQWSSTZY21. Accessed 2026-10-04.
- Maturity: paper-only write-up, but DiDi-affiliated authors using real platform data (adjacent to production).
- Key facts (as stated in abstract):
  1. Unifies **order dispatching and vehicle repositioning** under one **globally shared value function**, updated continuously from **online** real-time platform transactions, addressing "real-time fluctuations between supply and demand" and "necessary coordinations due to the large-scale nature of the problem" that prior simplified/separate-task formulations missed.
  2. Adds a **"periodic ensemble method"** combining fast online learning with large-scale **offline training** on historical driver trajectories — explicitly to "adapt quickly to the highly dynamic environment" and "generalize robustly to recurrent patterns."
  3. Benchmarked against a real competition: **"V1D3 outperforms the first prize winners of both dispatching and repositioning tracks in the KDD Cup 2020 RL competition,"** achieving state-of-the-art on both total driver income and user-experience metrics.
- Relevance: I searched specifically for Qin et al.'s 2020 INFORMS Journal on Applied Analytics piece ("Ride-Hailing Order Dispatching at DiDi via Reinforcement Learning") per the main agent's brief but Semantic Scholar did not surface that exact venue/title (searches for it were rate-limited, see UNVERIFIED leads); this KDD 2021 paper by an overlapping DiDi author team (Qin, Ye) is the closest verified substitute and is directly useful: it names the **KDD Cup 2020 RL competition for dispatch+repositioning** as a citable public benchmark, and its "online + offline ensemble for fast adaptation" design is a concrete pattern for handling live demand drift.

### 12. Qin, Tang, Jiao, Zhang, Xu, Zhu, Ye, "Ride-Hailing Order Dispatching at DiDi via Reinforcement Learning" — INFORMS Journal on Applied Analytics, 2020
- URL opened: https://api.semanticscholar.org/graph/v1/paper/DOI:10.1287/inte.2020.1047 (Semantic Scholar Graph API, direct DOI lookup — retried after an initial 429 and succeeded). DOI **10.1287/INTE.2020.1047**, DBLP journals/interfaces/QinTJZXZY20. Accessed 2026-10-04. (Note: this corrects/confirms the exact priority-#3 paper named in the brief, found on retry after the WWW/KDD2021 substitute above.)
- Maturity: **production** ("real-world impact to the business" discussed directly).
- Key facts (as stated in abstract):
  1. Order dispatching matches "passenger trip requests to drivers at a scale of **tens of millions per day**" on the DiDi platform.
  2. Documents the platform's methodological evolution: **"from a combinatorial optimization approach to one that encompasses a semi-Markov decision-process (SMDP) model and deep reinforcement learning."**
  3. Explicitly frames the core difficulty as the **"dynamic and stochastic nature of supply and demand"**, plus practical constraints of system response time, reliability, and multiple objectives — i.e., this is the applied/operations-research framing of exactly our non-stationary-demand problem, with a documented production-stage solution path (optimization → SMDP/RL).
- Relevance: the authoritative DiDi production case study for priority #3; good citation for "non-stationary demand handled via SMDP + deep RL at production scale," and for justifying a staged MVP (start with combinatorial/rule-based optimization, evolve to RL) as an industry-validated path rather than an arbitrary choice.

### 13. Azagirre, Balwally, Candeli, Chamandy, Han, King, Lee, Loncaric, Martin, et al., "A Better Match for Drivers and Riders: Reinforcement Learning at Lyft" — arXiv 2310.13810 (2023), INFORMS J. Appl. Anal. 2024
- URL opened: https://export.arxiv.org/api/query?id_list=2310.13810 (arXiv API; ID found via web_search, abstract verified directly on arXiv this session). Accessed 2026-10-04.
- Maturity: **production** (global rollout confirmed).
- Key facts (numbers exactly as stated in abstract):
  1. Revised Lyft's **core matching algorithm** using a "novel **online reinforcement learning** approach that estimates the **future earnings of drivers in real time**" to find more efficient matches — "the first documented implementation of a ridesharing matching algorithm that can learn and improve in real time" (in production).
  2. Evaluated via **"weeks of switchback experimentation in most Lyft markets."**
  3. Impact: enabled drivers "to serve **millions of additional riders** each year, leading to **more than $30 million per year in incremental revenue**." **Lyft rolled out the algorithm globally in 2021.**
- Relevance: matches priority #3 (Lyft) exactly, and is the strongest "look-ahead value estimate beats static/greedy matching, measured in real $ terms" production proof point we found — good headline number for our pitch deck ("industry's own RL-for-dispatch deployments report $30M/yr from exactly this kind of change").

### 14. "Non-myopic Matching and Rebalancing in Large-Scale On-Demand Ride-Pooling Systems Using Simulation-Informed Reinforcement Learning" — arXiv 2510.25796 (2025)
- URL opened: https://export.arxiv.org/api/query?id_list=2510.25796 (arXiv API; first surfaced as a related result inside the Semantic Scholar search for Xu et al. KDD 2018). Accessed 2026-10-04.
- Maturity: paper-only (evaluated on NYC taxi request data).
- Key facts (numbers exactly as stated in abstract):
  1. **Explicitly extends "the learning and planning framework of Xu et al. (2018) from ride-hailing to ride-pooling"** by embedding a ride-pooling simulator inside the learning loop (simulation-informed RL) for non-myopic decisions, plus a **complementary rebalancing policy** for idle vehicles; uses **n-step temporal-difference learning on simulated experience** to derive spatiotemporal state values.
  2. **Non-myopic matching vs. myopic baseline**: service rate **+up to 8.4%**, plus reduced in-vehicle and wait times; non-myopic policy can **cut fleet size by over 25%** vs. myopic while holding performance constant.
  3. **Adding rebalancing** on top of non-myopic matching (vs. matching-only): wait time **−up to 27.3%**, in-vehicle time **−12.5%**, service rate **+15.1%** (at the cost of more vehicle-minutes traveled per passenger).
- Relevance: **best direct evidence for our core MVP claim** ("look-ahead planning/RL beats a static/myopic policy") with concrete, recent (2025), reproducible-style % numbers and a named myopic baseline — also demonstrates that pairing a dispatch/matching policy with a *separate* rebalancing policy (our bi-level idea) adds further measurable gains on top of smarter matching alone. Directly actionable template for how we should report our own baseline-vs-agent deltas.

---

## Implications (borrow / beat / non-stationarity gaps)

_(pending)_

---

## UNVERIFIED leads

_(pending — papers mentioned in instructions not yet opened)_
