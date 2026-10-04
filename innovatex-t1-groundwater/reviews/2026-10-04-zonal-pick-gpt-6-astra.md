# Cross-model review — Delhi-zonal theme pick (JalSakshi vs DustLedger)

- **Date:** 2026-10-04 · **Reviewer:** `gpt-6-astra`, reasoning effort `max` · **Commissioned by:** Supervisor
- **Brief given:** act as a hostile InnovateX Delhi-zonal judge; compare T1 JalSakshi (`innovatex-t1-groundwater/`) with T2 DustLedger (`innovatex-t2-aqi/`) on the official criteria; verify load-bearing claims at their sources; pick one.
- **Verdict:** **A — JalSakshi.** A second, independent judge (`grok-4.7`) reached the same pick: [2026-10-04-zonal-pick-grok-4.7.md](2026-10-04-zonal-pick-grok-4.7.md).
- **Lead:** mark each attack and red flag below as ACCEPTED or REJECTED with a reason, then add a line to `reviews/ledger.tsv`.

---

## 1. Scores

These scores assess the evidence and how credibly each team can deliver, not the teams' self-ratings. A and B paths below refer to their respective folders.

| Criterion | A: JalSakshi | B: DustLedger |
|---|---|---|
| Creativity & novelty | **3** — Distinct audit workflow; familiar physics. | **3** — Fence-line attribution already exists commercially. |
| Functionality & usability | **2** — Simulation only; operator dashboard unfinished. | **2** — Simulation only; control and tamper detection unbuilt. |
| Cost & market value | **3** — Partially priced BOM; payer not proven. | **2** — No complete installed-kit cost or validated buyer. |
| Technical feasibility | **3** — Hydraulic measurement gap is fixable. | **2** — Coarse dust, fog, wind and calibration problems compound. |
| Regional scalability | **3** — Needs pit-specific commissioning. | **3** — Needs local aerosol, wind and siting validation. |
| Environmental/socioeconomic impact | **3** — Maintenance-to-infiltration benefit plausible but unmeasured. | **2** — Pollution reduction and protected wages not proven. |
| Design & ergonomics | **3** — Simple node and an actionable maintenance workflow. | **3** — Clear workflow; multi-node installation untested. |
| Local-depth bonus | **4** — Original WRIS analysis plus the DJB hook. | **4** — Strong GRAP and worker context; policy evidence weaker. |

## 2. Pick: A — JalSakshi

**A is more likely to advance and then win**, provided it fixes its measurement claims.

A can demonstrate a maintenance failure and its repair with metered water before December. B needs several uncertain measurement and control subsystems, plus regulatory acceptance; AI expertise cannot fix aerosol physics. Neither entry would win the finals as it stands. A wins on a shorter route to independently checkable evidence, not on better simulation scores.

## 3. Five attacks, with fixes by 9 October

1. **The water balance is unobservable.** A stage reading alone cannot separate inflow from infiltration. Specify inlet/overflow measurement, or restrict the output to calibrated falling-head maintenance tests.
2. **The simulation confirms itself.** Recruit an embedded teammate, borrow a logger, and film blind weighed-water trials across drain restriction, overflow and bypass. Label the 3% and 100% results as simulation-only.
3. **Affordability is misleading.** A standalone LoRa build with a gauge costs **at least ₹47,389 in listed parts**, before installation. Produce installed and annual quotes, and validate the actual sensor specification.
4. **There's no committed buyer.** Get a pilot email from a campus or RWA and interview two maintenance officers. Sell failure detection, not guaranteed rebates or automatic penalties.
5. **Reliability is untested.** Fifteen-minute polling can miss short events. Demonstrate rain-triggered wake-up or continuous bench sampling, outage buffering and recovery, and measured current draw. Keep three-year battery life only as a target.

## 4. Five judge questions, with defensible answers

1. **"How does one level sensor measure recharge?"** On its own, it doesn't. We need measured inflow/overflow or a validated recession model. Infiltration from the structure still doesn't establish aquifer recharge.
2. **"Why not an ordinary logger?"** The hardware isn't the innovation; calibrated clogging detection and maintenance evidence are. The pilot must show value over manual inspection.
3. **"Can an owner cheat?"** Yes — a bypass during rain can fool it. Signatures authenticate records, not where the water went. Suspicious events trigger an inspection.
4. **"What's actually real?"** The WRIS data and the software. Pit performance is simulated. Neither the 3% error nor the ten detected fakes guarantees field performance.
5. **"How do you prove impact without monsoon rain?"** Metered fills before and after cleaning. Report drainage restoration with uncertainty, not invented city-wide recharge or health gains.

## 5. Source checks and red flags

- **A, `thought_node.md` Selection memo; `deliverables/zonal-pitch.md` slide 3:** [Hindustan Times](https://www.hindustantimes.com/cities/delhi-news/delhi-makes-rainwater-harvesting-mandatory-penalties-for-violators-101776711439024.html) confirms ₹204.46 crore and the rebates. But it describes self-certification as **planned**, and says certificates are issued **after inspection**. "Never checked" and "self-certification already in force" overclaim.
- **A, `deliverables/zonal-deck.md` slide 2:** "Delhi pumps more than it recharges" contradicts the cited 92.1% extraction ratio. Over-exploited tehsils don't establish city-wide over-extraction.
- **A, `research/landscape.md` §2:** [Acorn](https://www.acorncontrols.com/piezometer.html) confirms ₹38,000 and a two-readings-per-day product. That's one product, not a universal limitation of CGWA loggers.
- **A, `deliverables/prototype-plan.md` §1 and `research/landscape.md` §5:** they borrow 3 m full-scale accuracy for the 30-bar sensor listed in the BOM. Unsupported.
- **B, `deliverables/zonal-pitch.md` slides 1 and 6:** [The News Mill](https://thenewsmill.com/2026/09/delhi-launches-winter-action-plan-2026-27-with-50-work-from-home-and-construction-bans-to-reduce-pollution/) corroborates the ban dates, but only as secondary reporting. [CSTEP](https://cstep.in/publication/guidance-for-evaluating-the-performance-and-use-of-air-quality-sensors-for-construction-dust-pm10-monitoring/) supports qualitative sensor use, not reliable causal PM10 increments. Subtraction doesn't fix unequal coarse-dust responses.
- **B, `thought_node.md` Selection memo:** "tamper-proof" and "keeping clean sites working" remain unsupported. `deliverables/prototype-plan.md` §4 must reconcile its November construction-site trial with its own ban premise.
