# ADR 001 — Spike choice: a completeness-aware charger census, feeding segment-aware gap and requirement estimates

- **Status:** accepted for the morning package (v1, 4 Oct 2026, 08:00 IST). Revisit by 12 Oct after the component research and the first backtests.
- **Deciders:** project lead (EV C1). The independent adversarial review (`rubber-duck`) and the First Principles agent could not run tonight: Lean Mode, no sub-agents, network saturation. The antithesis below is the lead's own steel-man. **Redo it with an independent agent before 12 Oct.**

## Context (evidence measured tonight)
- **Official counts disagree with each other.** BEE: 26,367 public charging stations (PCS) as on 1 Apr 2025 (PIB 2118894). MoP inputs: 29,277 PCS (PIB 2151390, 1 Aug 2025). Both are state-wise tables in press releases, not machine-readable feeds, and neither gives locations.
- **Operators count in other units.** Statiq claims "10000+ EV Chargers Installed" in "1014+ Cities"; Jio-bp claims "2,000+ mobility stations across India" (their home pages, opened 4 Oct 2026). Stations, chargers and connectors are not comparable without a canonical unit.
- **Open data is thin.** OpenStreetMap has **600** `amenity=charging_station` features in India (Overpass, OSM base 2026-10-04 00:26 UTC), **2.05%** of the official 29,277. Only 31.8% carry an `operator` tag and 7.8% any `socket:*` tag. Open Charge Map's API refuses unauthenticated calls (HTTP 403).
- **Demand data is good.** VAHAN 4 now lists all 36 states/UTs and 1,468 of 1,469 offices. We pull state × fuel × year, state × vehicle class × fuel, and RTO-level tables over plain HTTP.
- **Naive gap ratios mislead.** BEV registrations per official PCS range from 3.0 (Nagaland) to 1,966 (Chandigarh). Among large states: Bihar 1,085, Uttar Pradesh 792, Karnataka 152 ([`eval/results/state_gap_baseline.csv`](../../eval/results/state_gap_baseline.csv)). Hypothesis, not yet tested: high-ratio states are e-rickshaw-heavy (3W), and most of those vehicles do not use the public charging network that the PCS counts describe.

## Options considered (one or two spikes; everything else stays best practice)
| Option | Component(s) | Idea | Isolated metric |
|---|---|---|---|
| **A. Completeness-aware charger census** | C4 `charger_resolve` + C5 `census_completeness` | Resolve sites across sources (OSM, OCM, operator locators, UEI when available). Then estimate the sites *no* source lists with multiple-systems (capture–recapture) estimation, validated against held-out official state totals. Every map and gap figure carries a coverage factor and a CI. | Pairwise F1 (C4); relative error vs held-out official state totals (C5) |
| **B. Segment-aware demand → requirement engine** | C8 `demand_model` + C9 `adoption_forecast` + C11 `requirement_siting` | Split VAHAN stock by segment (2W/3W/4W/bus) and charging mode (home/depot/public/swap), forecast to 2030 with pooled regional diffusion models, and size chargers by class with queueing; site them with MCLP under grid constraints. | Backtest sMAPE (C9); demand covered per added charger vs baselines (C11) |
| C. ML/RL/GNN siting optimiser | C11 | Learn site value from utilisation | No utilisation ground truth in public data → not measurable |
| D. LLM planning copilot | C13 | Natural-language queries over the platform | Demo value, low analytical weight |

## Six Thinking Hats
- **White (facts):** Above. Supply data is the binding constraint: 2% open coverage, and two official totals 4 months apart that differ by 2,910 stations. Demand data (VAHAN) is rich and current.
- **Red (gut, judges):** MHI/ICAT want a *unified view* and *defensibility* ("intelligence, transparency, and defensibility … rather than access to premium or proprietary datasets"). A map that says "we see 61% of Maharashtra's stations; here is the CI and how we know" is more credible to officials than a pretty map that silently shows 2%.
- **Black (risks):** Capture–recapture assumes independent sources. OSM mappers copy operator apps, so the sources are positively dependent and estimates run low; we need log-linear models with interactions plus the official totals as a check. Few sources may be ToS-accessible: operator locators need permission. Judges may not value statistics they don't know, so the result must be shown as a coverage map, not as equations.
- **Yellow (benefits):** It answers the brief's first sentence (fragmentation). It is reusable: the same machinery can audit any future national registry, such as a UEI feed. Every downstream gap number becomes honest, because it can be coverage-adjusted. It is measurable against public ground truth tonight (36 state totals).
- **Green (alternatives):** Estimate the missing sites from operator self-reported totals (Statiq "10000+"). Use satellite or street imagery. Crowd-verify through a "report a charger" loop. Use UEI/Beckn discovery as a near-complete source when it opens.
- **Blue (process):** Spike A primary, B secondary (B is needed for the "future requirement" deliverable anyway, but uses best-practice parts first). Gate on 12 Oct: is C5's relative error vs official state totals < 25% for the states with ≥ 2 sources? If not, demote A to best practice and promote B.

## Thesis → antithesis → synthesis
- **Thesis:** The national problem is *not knowing what exists*. A census with measured completeness is the foundation every other number stands on. It is novel in this domain, as far as we have found (literature check pending: the research agent died before reporting), and measurable today against official totals.
- **Antithesis (lead's steel-man):** Judges score usability and planning value. Officials already have BEE's counts. A statistics-heavy census risks looking academic while the "how many chargers where by 2030" deliverable gets less attention. And with ~2% open coverage, capture–recapture across sources may simply not have enough overlap to be stable.
- **Synthesis:** Build A as the *trust layer*, not the headline. The headline is the planner-facing gap and requirement module (B, built from best-practice parts first). A feeds it a coverage factor and a CI per region, so recommendations say "need ~N more DC chargers in district X (supply coverage 0.6 ± 0.1)". If overlap is too thin for multi-source estimation, C5 degrades gracefully to *benchmark calibration*: observed ÷ official state total, which is already computable for all 36 states tonight.

## First principles (what is the real bottleneck?)
A planner needs: demand (how many EVs of each segment need public energy, where), supply (what usable public capacity exists, where), and the difference over time. Demand is observable (VAHAN). Supply is the unobserved quantity, so the highest-leverage innovation is on estimating supply and its uncertainty. The second-highest is on translating vehicle counts into *public* charging need by segment: a two-wheeler that charges at home and an e-bus at a depot do not need the same infrastructure as a ride-hailing car.

## Scores (1–5)
| Option | Impact on judged criteria | Novelty | Feasibility by 30 Oct / 16 Dec | Measurability | Demoability | Total |
|---|---|---|---|---|---|---|
| **A. Completeness-aware census** | 5 (data quality & integration 20% + robustness 25%) | 4 | 4 | 5 (official totals) | 4 | **22** |
| **B. Segment-aware requirement engine** | 5 (relevance & usability 20%) | 3 | 4 | 4 (backtests) | 5 | **21** |
| C. ML/RL siting | 3 | 3 | 2 | 1 | 4 | 13 |
| D. LLM copilot | 2 | 2 | 4 | 2 | 5 | 15 |

## Decision
**Spike 1 = A (C4 + C5).** **Spike 2 = B's adoption forecast + requirement sizing (C9 + C11)**, starting from best-practice baselines (CAGR / Bass; norm-based counts; PySAL spopt MCLP). Auto-research loops: C5 (metric: relative error vs held-out official state totals) and C9 (backtest sMAPE).

## Consequences
- C2 must ingest ≥ 2 independent sources with stable ids: OSM (done), Open Charge Map (needs a free API key, under *Needs from user*), and ≥ 1 operator or UEI feed where terms allow.
- Every `GapRecord` carries `coverage_adjusted_sites`; the dashboard shows coverage beside every supply figure.
- The eval harness holds out official state totals and never trains on them.
