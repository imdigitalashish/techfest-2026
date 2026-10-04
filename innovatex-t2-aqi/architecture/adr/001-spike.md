# ADR 001 — Spike: wind-resolved site attribution with self-calibrating fence-line rings

- **Status:** accepted (v1, 4 Oct 2026 07:40 IST). To be re-tested by an independent adversarial review (`rubber-duck`) once lean mode lifts. The antithesis below was written by the lead, not by an independent agent, so treat it as a first pass.
- **Context:** [landscape](../../research/landscape.md) · [components](../components.md)

## Context
Delhi controls construction dust with blanket restrictions: Nov 1–Jan 31 restrictions on dust-generating works and a total ban Dec 10–Jan 20 (Winter Action Plan 2026-27), plus GRAP stops (16 days of GRAP-3 in 2025). Delhi's construction welfare board has 1.38 M workers on its rolls (89,518 active members). Compliance is measured by equipment counts, CCTV and self-audits, and the reference-monitor norm is one station per 25–50 km². **Nobody measures what a given site adds.** The judges reward novelty, robustness in "high-dust atmospheres", calibration/maintenance realism, cost, scalability and quantified impact.

## Candidates (scored 1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasible by 1 Dec | Scalar metric | Demo | Total |
|---|---|---|---|---|---|---|
| **S1 Attribution (C6) + inter-node self-calibration (C5)**: ring differential, wind-conditioned, abstains in calm or variable wind, outputs P(site is cause) | 5 — enables targeted enforcement instead of bans | 4 — fence-line practice exists in mining/refineries (Envirosuite, EPA rings); not found at Indian construction-site cost points | 4 — software on replayed real data now; hardware ring by Nov | 5 — increment MAE vs known truth in replay | 5 — "watch the site light up only when the wind blows from it" | **23** |
| S2 Closed-loop misting (C8) | 4 — water + PM | 3 — sensor-triggered misting exists generically; no attributed trigger found | 4 | 4 — µg·h avoided per kL (simulated) | 5 — physical spray on demand | 20 |
| S3 Background forecasting (C7) | 2 — IITM's state system already does this | 2 | 5 — baseline done | 5 | 3 | 17 |
| S4 Tamper detection (spray-on-sensor signatures) | 4 — answers the Jahangirpuri sprinkler scandal | 4 | 3 — needs field signatures | 3 — F1 on staged events | 4 | 18 |
| S5 Dust-specific humidity/size calibration | 3 | 3 — κ-Köhler exists | 3 — needs a reference co-location | 5 | 2 | 16 |

**Decision:** S1 is the spike. S2 is a second, lighter spike, ratcheted in simulation after S1. S4 is folded into S1 as a feature (one node disagreeing with the ring, with an RH jump, means suspected spraying). S3 and S5 stay best-practice: GBM forecast baseline; linear + RH calibration with weekly re-fit.

## Six Thinking Hats (on S1)
- **White (facts):** Delhi winter PM10 averages ~314 µg/m³ (TERI). A site's increment at its fence must be read on top of that, so absolute sensor accuracy matters less than *consistency between identical sensors*. CSTEP (2025) says low-cost sensors are qualitative-grade for construction PM10. EPA fence lines use perimeter rings. Our forecast baseline is in `eval/results/forecast_baseline.json`.
- **Red (gut / judges):** "A ₹-thousands kit that tells the regulator *which* site is dusty, so the clean ones can keep working" is a story a Delhi panel feels: workers' wages, fairness, and the sprinkler scandal.
- **Black (risks):** calm winter nights (low wind) break upwind/downwind logic; neighbouring sites and roads confound; sensors under-read coarse dust; contractors may game the nodes; the regulator may not accept startup data; the health case for dust is weaker than for combustion.
- **Yellow (benefits):** turns flat fines and blanket bans into measured, per-site accountability; cuts water use (spray only when needed); creates an evidence trail for disputes; the hardware cost is small next to a ₹5 lakh fine.
- **Green (alternatives / wild):** drones for weekly plume mapping as a verifier; a CCTV-based dust-plume detector fused with the ring (sites already need 100 % CCTV); an "earned-permission" tier where verified-clean sites keep working through Stage 3; insurance-style pricing of fines by measured increment.
- **Blue (process):** build the replay harness first (real background and wind, simulated plumes and sensor faults, all labelled), measure baseline single-pair subtraction, then ratchet S1 against frozen `eval.py`; hardware ring field test in Nov.

## Thesis → antithesis → synthesis
| Thesis | Antithesis (strongest objection) | Synthesis (what we build / claim) |
|---|---|---|
| Measure each site's own dust; enforce on it | "We cannot remain too fixated on curbing dust": combustion PM2.5 dominates health harm (Lancet 10-city study lead author) | We don't claim the biggest health lever. Our claim is **fairness and economics**: replacing blanket bans with measured accountability, plus real PM10 cuts at the fence line where workers and neighbours breathe. The same ring detects combustion signatures on site (diesel generators, waste burning) later |
| Low-cost sensors are good enough | CSTEP 2025: low-cost sensors are *qualitative* for construction PM10 | Use them for **differences** between identical, co-calibrated units, not absolute compliance values. Output increments with 90 % intervals and P(cause). A reference-grade spot check remains the legal basis for penalties: we triage, DPCC verifies |
| Upwind–downwind isolates the site | Calm or meandering winter winds; neighbours upwind | Ring of 3–4 nodes + wind. Attribute only in well-defined wind sectors, **abstain** otherwise, and report the abstention rate as a metric. An upwind neighbour raises the background, not the increment |
| Data can drive exemptions | Contractors will spray or relocate nodes; regulators won't trust it | Signed records, a hash-chained ledger, flow-metered misting, tamper flags (one node disagreeing with the ring + RH jump), enclosure seals, and a CCTV cross-check |
| Inter-unit drift ruins differences | Optical sensors drift apart over weeks | **Self-calibration:** when the site is idle (nights, holidays) or the wind runs along the ring, all nodes breathe the same air, so the offsets and slopes between nodes can be re-estimated continuously |

## First principles
The bottleneck isn't city-level measurement (47 reference stations, going to 60) or forecasting (IITM). It's **attribution at the scale of the actor who can change behaviour**. The background is common to all nodes, so a ring measures the site's increment as a difference. Its error is dominated by *between-node* bias, not absolute bias, and between-node bias can be estimated from the site's own idle periods. That gives a cheap, self-maintaining measurement with no reference monitor on every site.

## Consequences
- Build `components/attribution/` with a frozen replay evaluator. Background = real CPCB 15-min PM10 (OpenAQ archive); wind = ERA5 / station wind; plumes = Gaussian model with known emission schedules; sensor errors = slope, offset, RH growth, noise, drift. All labelled SIMULATED.
- **Primary metric:** increment MAE (µg/m³) on held-out days. **Secondary:** CSI for "site increment > threshold" events, and abstention rate. Baseline to beat: single-pair subtraction without self-calibration.
- If S1 fails the replay (e.g. MAE no better than baseline in calm conditions), fall back to S2 + S4 as the pitch spike. Record that in ADR 002.

## First result (4 Oct 08:03 IST, replay evaluator v1, 5 seeds)
Real background (monitor 6929) + real ERA5 wind; SIMULATED site, plumes and sensors. Held-out Jan–Sep 2026, MAE over all hours (abstentions scored as 0), mean ± sd over 5 seeds: fixed pair **97.8 ± 15.6** → wind-resolved ring **58.0 ± 16.0** → ring + idle-hour self-calibration **33.8 ± 2.6 µg/m³** (coverage 0.95; CSI for > 50 µg/m³: 0.34 → 0.58 → 0.76). Dev agrees (115.1 → 58.0 → 30.9). Self-calibration also removes most of the seed-to-seed variance (sd 2.6 vs 16). Not field data. (The single-seed v0 run at 07:57 used unbounded sensor drift and is superseded.) Ledger: `components/attribution/autoresearch/results.tsv`.
