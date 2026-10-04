# Perceptron P1 · Cheap fine-tuning across weak, scattered devices — Thought Node

> Journal for `perceptron-p01-federated-lora/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 4–5. The walking skeleton and eval harness run end-to-end with real numbers on the M5; the AnchorLoRA spike pilot beats the starter baseline (1 seed); the ratchet is scaffolded. Morning package complete (08:00 IST).
- **Plan:** (1) replicate (seed 1 running, then ≥5 seeds) → (2) close the antithesis gaps (stronger baselines, de-confounded design, Sybil and leave-one-out tests) → (3) Flower adapter + kill-a-node demo → (4) standard datasets (finance sentiment, Dolly-15k) → (5) 0.5B–1.1B runs on Azure → abstract final by 31 Oct.
- **Doing (07:55 IST):**
  - Replication: 3 attached processes. (1) clean `anchor_naive`/`anchor_full` seed 0, then seed 1; (2) dropout seed 1 for all strategies; (3) dropout `anchor_full` seed 1 alone. Each run takes ≈30+ min at load average ≈ 80. Results append to `eval/results/v1_*.jsonl`; regenerate with `python -m eval.summarize --tag v1`.
  - Agents (network recovered for agents; PyPI ≈ 176 KB/s, so `flwr` 1.39.0 is now installed): `c10-flower-adapter` (builds `components/flower_adapter/`) · `r5c-companies` → `research/raw/companies.md` · `r46-frameworks-benchmarks` → `research/raw/frameworks_benchmarks.md` · `r1c-fedlora-frontier` → `research/raw/fedlora_frontier.md` (incl. the prior-art verdict on frozen A + nested ranks).
- **Next:**
  1. Re-run research threads r1–r6 + first principles when the network recovers, to fill the company section and verify every UNVERIFIED item.
  2. Install `flwr` (blocked: `grpcio` not downloadable overnight) and build C10.
  3. Ratchet iteration 1: τ_eff from actual vs planned steps.
  4. Baselines: exact ΔW + SVD (FlexLoRA-style), FedEx-LoRA, RoLoRA; centralised and local-only bounds.
  5. Latin-square rotation of domains across device budgets; Sybil split test; leave-one-device-out.
- **Needs from user:** register by 15 Oct (after the 12 Oct selection); teammates' names and skills (the abstract has placeholders); optional: a phone or Raspberry Pi for the physical-device stretch. Azure GPU quota for 0.5–1.1B runs is not yet checked (the subscription is enabled; SKU ask to follow).
- **Risks:**
  1. Ingredients are published (FFA-LoRA, FedNova, MIFA), so novelty is the integration plus measurement; the prior-art check for frozen-A + nested ranks is inconclusive (UNVERIFIED).
  2. Frozen A may cap expressiveness (RoLoRA, NeurIPS 2025).
  3. Single-seed, 12-round pilot on a local-text proxy.
  4. Overnight network outage: all 8 research sub-agents failed, and the company landscape is thin.
  5. The shared GPU makes runs slow (≈10 min for 12 rounds of a 135M model).

## Phase 0 — constraints and what we must show (from `_briefs/perceptron.txt`, read 02:05 IST)
**Hard constraints**
- Round 1 is plan-only: a 600–900-word abstract plus an optional one-page diagram, submitted **once** by the team leader on techfest.org. A second submission can mean disqualification.
- Theme 1 is Problem 1 *or* Problem 2. Overall, one problem per team. Team ≤ 3 students. Solutions must be original and "not protected by patents, copyrights, or publications", so published methods are attributed baselines and our contribution must be our own.
- The midway check (1 Dec, one page, unscored) confirms the team "has not stalled or pivoted away from its stated plan". **So the abstract locks in the plan: promise only what we can build.**
- Finals (15–18 Dec): a working build demonstrating the Minimum Viable scope plus any stretch goals attempted. 25–30 teams across all 10 problems; scores normalised; the top 3 overall win.
- Queries go only through the Techfest portal's Doubt section.

**Judging → evidence we must be able to show**
| Criterion (weight) | Evidence |
|---|---|
| Problem understanding (20%) | Name the crux precisely: (i) averaging LoRA factors A and B separately is not averaging ΔW=BA, and rank heterogeneity breaks naive averaging; (ii) unequal local work makes the averaged objective inconsistent; (iii) dropouts bias the objective toward always-on devices; (iv) n_k weighting is a micro-average, so the data-rich device dominates. Define "meaningful contribution", "stable", and "dominate" operationally. |
| Technical soundness (25%) | Named model, datasets, PEFT, Flower, aggregation maths; runs on a laptop. |
| Innovation (20%) | A spike that goes beyond PEFT + Flower FedAvg, checked against 2025–26 prior art. |
| Clarity (10%) | Precise, concrete, with a diagram. |
| Evaluation rigour (15%) | One experiment per claim, against named baselines, over several seeds with confidence intervals. |
| Team fit (10%) | Skill mix plus week-by-week milestones. |

Evidence list: **E1** convergence under heterogeneity (macro held-out metric vs rounds, against a centralized upper bound) · **E2** weak devices contribute meaningfully (leave-one-out gain on their own domain is > 0 and significant) · **E3** stability under mid-run dropout (no divergence, smaller loss spikes than naive) · **E4** no quiet domination (dominance index and worst-client metric, FedAvg vs ours) · **E5** cost per device class (bytes per round, compute, memory) · **E6** smarter aggregation vs naive averaging, head to head.

**Assumptions (overnight; the user can override in the Inbox)**
- A1: Problem 1 is judged on its own merits here; the Supervisor ranks all 10 Perceptron problems from the selection memos.
- A2: Team of 3 (Ashish + 2 TBD); the team-fit section uses role placeholders until names arrive.
- A3: Models are those already in the local HF cache (SmolLM2-135M for fast loops, Qwen2.5-0.5B for headline runs; GPT-2 for parity with the starter resources). TinyLlama-1.1B is optional on Azure.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 1 — Cheap Fine-Tuning Across Weak, Scattered Devices** (Theme 1: Efficient AI at Scale — teams choose Problem 1 or 2)
- **Context:** Organizations often want to specialize a shared model using data that lives on many different machines without moving the raw data anywhere.
- **Challenge:** Build a lightweight fine-tuning scheme where even low-power devices can meaningfully contribute updates to a shared model, training stays stable even when devices drop out mid-run, and one data-rich device can't quietly dominate the result.
- **Starter resources:** HuggingFace PEFT (LoRA) + an open federated learning framework (e.g. Flower), applied to a small open model (GPT-2 or TinyLlama scale).
- **Minimum Viable:** simulate 3–5 nodes with different data splits and compute budgets; show the shared model converges despite the heterogeneity.
- **Stretch goals:** simulate node dropout mid-training; compare a smarter aggregation strategy against naive averaging.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Frameworks: Flower (`flwr`) simulation, HF PEFT, Unsloth, MLX-LM LoRA on Apple silicon; small models (TinyLlama-1.1B, Qwen2.5-0.5B, SmolLM2).
- Federated-LLM fine-tuning work: OpenFedLLM / FedIT, HetLoRA, FlexLoRA, FedSA-LoRA, FLoRA (stacking-based aggregation), FFA-LoRA — and whatever has superseded them in 2025–2026.
- Heterogeneity, robustness and fairness: FedProx, FedNova, norm clipping, trimmed mean / Krum, contribution caps; stragglers and dropouts: buffered/async aggregation (FedBuff); non-IID splits via Dirichlet partitioning.
- What companies ship: on-device and federated learning at Apple, Google (Gboard), and enterprise federated platforms — check their recent engineering posts.

## Key decisions
- 2026-10-04 — **Spike = C6 aggregator "AnchorLoRA"**: a frozen seed-generated A shared by all devices, nested ranks, FedNova normalisation, macro weights, median-norm clip, memory of absent devices, and partial work kept. See [ADR 001](architecture/adr/001-spike.md). We claim the integration and the measurement, not the frozen-A trick.
- 2026-10-04 — Primary objective is **macro** (each device's domain weighted equally); the micro (sample-weighted) loss is reported alongside it.
- 2026-10-04 — Overnight data: 5 real-text domains already on the machine (WikiText-103 cache, Python, C headers, READMEs, man pages), because PyPI/HF downloads ran at ~0–0.6 KB/s. Standard datasets come next.
- 2026-10-04 — In-process simulator first (one shared base model, LoRA swapped per device). The Flower adapter follows once `flwr` installs.
- 2026-10-04 — Python 3.11 venv from the local uv cache (torch 2.10.0, transformers 4.57.6, peft 0.21.2), because the network blocked newer wheels.

## Components
Full contracts: [architecture/components.md](architecture/components.md). Research: [research/components/](research/components/).
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Data partitioner | corpus → per-domain token blocks | flwr-datasets Dirichlet | – | ✅ local-text | realised vs target skew |
| C2 | Device simulator | profiles, seed → allowed steps per round | Bernoulli participation | – | ✅ | realised vs target dropout rates |
| C3 | Budget planner | profile → rank, steps | one config for all | – | 🟡 static | loss drop per device-FLOP |
| C4 | Local trainer | task + view → ΔB (or A, B) | PEFT LoRA + AdamW | – | ✅ | loss drop per second, peak memory |
| C5 | Update codec | tensors → bytes | fp32 A, B | – | 🟡 fp32 | bytes at ≤1 % error |
| C6 | **Aggregator** | updates → global adapter + report | FedAvg over A, B | **spike** | ✅ 4 strategies | macro loss after 12 rounds of the dropout scenario |
| C7 | Orchestrator | config → rounds, summary | sync FedAvg, drop late devices | – | ✅ | max loss spike |
| C8 | Contribution accountant | c_k, P → influence shares | n_k as contribution | 2nd candidate | 🟡 in C6 | Spearman vs leave-one-out |
| C9 | Evaluator | snapshot → per-domain loss | pooled test loss | – | ✅ | determinism, CI width |
| C10 | Flower adapter | C6/C7 over Flower | Flower FedAvg | – | 🔴 blocked (flwr install) | parity with in-process sim |

## Selection memo
_First version 4 Oct 07:40 IST (final by 12 Oct). Scores 1–5, one line of evidence each._
- **Winnability — 4.** The starter baseline demonstrably fails the brief: under FedAvg the data-rich domain improves by 0.36 nats while all 4 other domains end worse than the untuned model (`eval/results/v1_summary.md`). We show the failure and a fix, with numbers, in a problem many teams will answer with plain PEFT + Flower.
- **Innovation headroom — 3.** The spike (exact rank-heterogeneous aggregation as the substrate for exact FedNova/memory/macro weighting, plus a dominance audit) goes beyond the baseline. But each ingredient is published, and 2026 work is active (iFLoRA ACL'26, FedRoRA Sep'26, CLAIR May'26). The headroom is in rigour and system integration, not a new theorem.
- **Feasibility — 5.** Already end-to-end on the M5: 5 heterogeneous devices, dropouts, 4 strategies, 7 passing contract tests, real numbers. Nothing is gated on hardware or the user; Azure scales it up. Exam week 19–25 Nov is kept free in the plan.
- **Demo strength — 4.** A live per-device "who got better/worse" table plus an influence-share bar each round; kill a Flower node mid-round and the curve stays flat. Federated training is less visual than some problems, but the dominance meter makes it tangible.
- **Fit with the user's strengths — 5.** Distributed systems + LLM fine-tuning + Azure: core Microsoft-style large-scale systems work.
- **Biggest risk:** judges read it as incremental (published ingredients), or frozen A underperforms trainable-A baselines (RoLoRA, FedEx-LoRA) at equal communication. Mitigation: anchor refresh and strong baselines in the ablation ladder.
- **One-line pitch:** "Federated LoRA where a Raspberry Pi's data counts as much as a workstation's: exact aggregation for any rank mix, dropout-tolerant, and a live dominance meter. In our pilot (1 seed, 4 methods) it was the only method that improved every device's domain."
- **Overall:** 4.2/5 (unweighted mean of the five scores).

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:10 IST — Lead: Phase 0 done, Phase 1 launched
- Read PLAYBOOK, this brief and the full official statement. Extracted the constraints and an evidence list (E1–E6) mapped to the judging weights (above). Key insight: the midway check penalises pivoting, so the abstract must promise only what we can build.
- Machine: Apple M5, 24 GB, macOS 26.2, 71 GB free disk. Azure: "Visual Studio Enterprise Subscription" enabled. PyPI today: flwr 1.39.0, flwr-datasets 0.6.1, peft 0.21.2, torch 2.14.1, mlx-lm 0.32.0.
- Spawned 7 background agents (r1–r6 research, fp-bottleneck). Venv install running.

### 2026-10-04 07:40 IST — Lead: morning package (Phases 1–5)
**What happened**
- **Network outage.** The shared uplink saturated (PyPI ≈ 0 B/s, HF API ≈ 0.3–0.6 KB/s). All 8 sub-agents died before their first turn with HTTP 408 / ETIMEDOUT: r1, r1b, r2, r3, r4, r5, r6, fp-bottleneck and its retry.
- **Fallbacks.** (a) A Python 3.11 venv built offline from the uv cache. (b) Five real-text domains from local files instead of downloaded benchmarks. (c) Primary-source verification by a local script: `scripts/verify_arxiv.py` → `research/sources/arxiv_verified.tsv`, 42/42 arXiv abstracts fetched, every title checked. (d) Server-side web_search/web_fetch for 2026 prior art: iFLoRA (ACL Findings 2026), CLAIR (2605.21217), FedRoRA (2609.00632).
- **Built (all contract-tested, 7/7 pass).** C1 data, C2 devices, C4 PEFT trainer, C6 aggregators (FedAvg on A,B homogeneous and heterogeneous rank; anchor_naive; anchor_full), C7 orchestrator, C9 evaluator + harness (`eval/run_matrix.py`, `eval/summarize.py`), and the ratchet scaffold (`components/aggregator/autoresearch/`).

**Results (real, seed 0, 12 rounds, SmolLM2-135M; `python -m eval.run_matrix --scenario {clean,dropout} --seeds 0 1 --tag v1`)**
- Untuned model: macro loss 2.7063; per domain: wiki 3.632 · pycode 2.403 · cheaders 1.767 · readmes 2.497 · manpages 3.233 (`eval/results/base_per_domain_smollm2-135m.json`).
- **Starter (FedAvg on A,B, r=8), dropout scenario:** macro 2.7346. Wiki improves to 3.265, but all 4 other domains get worse than the untuned model. Weak-device gain −0.132. Aggregation error 5.5 %. c0 influence share 1.02.
- **HetLoRA-style FedAvg:** macro 2.7046, aggregation error 25.4 % (36.2 % in the clean scenario).
- **anchor_naive (exact, n_k weights):** macro 2.7616. Exactness alone does not stop domination (c0 share 1.00).
- **anchor_full:** macro **2.6651**, the best. Every domain improves over the untuned model (weak gain +0.025), c0 share 0.20, aggregation error 0.000, no loss rise between evaluations.
- **Trade-off:** wiki improves less (3.515 vs 3.265), so the absolute worst-domain loss is higher (wiki is intrinsically the hardest domain).

**Antithesis.** The independent rubber-duck review raised 7 objections: confounded design; FedAvg-on-A,B as a straw man; planned-step scaling; prefix-rank ownership; stale replay; brittle clipping; an unbounded share metric. All are adopted as experiments in ADR 001's synthesis table.

**Deliverables.** `research/landscape.md`, `architecture/components.md` + `contracts/*.schema.json`, `research/components/*.md` (10), `architecture/adr/001-spike.md`, `deliverables/round1-abstract.md` (897 words), `deliverables/architecture.md` (mermaid), the selection memo above.

**Supervisor 07:22 alignment check.** Agreed (write ADR, deliverables, memo and Now/Log, pushing after each). Done, no reply needed.

### 2026-10-04 07:50 IST — Lead: independent fact-check of every number
- A `general-purpose` agent checked every quantitative claim in the abstract, selection memo, Log, ADR 001 and the component notes against `eval/results/*.jsonl`, the base-loss JSON and the source TSV.
- **Confirmed:** all loss, share, weak-gain, "all four other domains worse" and "every domain improves" claims.
- **Found and fixed:**
  - The aggregation-error range "9–36%" / "9–25%" came from the smoke test; the seed-0 range is 5.5–36.2%.
  - Upload "0.4–2.9 MB/round" and "2–8×" were wrong; the measured figure is a 2.5× reduction at equal ranks and participation.
  - The 1–5 option scores are now labelled subjective.
  - CLAIR and FedRoRA abstracts were added to the verified TSV (44/44); iFLoRA's ACL Anthology metadata is recorded in `research/sources/other_verified.md`.
- Simulator facts (8× data, ranks/steps, 5-round outage, 4-round memory) live in code (`device_simulator/profiles.py`, `aggregator/strategies.py`), not in the result rows. The checker flagged them as unsupported by results; they are config facts.
- **Replication in flight:** dropout seed 1 for `fedavg_ab_homo` (main process) and `anchor_full` (extra process `rep-anchor-s1`). At load average ≈ 80, expect results after 08:30.
- Also added: `requirements.txt` (pinned), `scripts/fetch_data.sh`, `README.md`.
