# Perceptron P1 · Cheap fine-tuning across weak, scattered devices — Thought Node

> Journal for `perceptron-p01-federated-lora/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** DEMO (Supervisor 19:57 IST, PLAYBOOK §11). Child session "P1 demo builder" proposes the "crazy" element; the lead approves, then it builds `demo/`. After that: lead verification from a clean checkout → gpt-6-astra demo review → "DEMO DONE". (Earlier: the 11:10 definition of done was met at 13:05.)
- **Headline** (5 paired seeds, dropout scenario, SmolLM2-135M, 12 rounds; `eval/results/v2_summary.md`):

  | Method | Macro loss | AnchorLoRA − method, 95 % CI |
  |---|---|---|
  | AnchorLoRA | 2.665 | — |
  | Starter | 2.747 | −0.081 [−0.093, −0.070] |
  | FFA-LoRA | 2.715 | −0.050 [−0.053, −0.046] |
  | FlexLoRA | 2.748 | −0.083 [−0.091, −0.074] |

  - **Per domain:** AnchorLoRA improves all 5 domains (Bonferroni); every baseline improves only the data-rich one, and its other four regress.
  - **Costs:**
    - micro loss +0.116 [+0.107, +0.124];
    - worst-domain loss +0.057 [+0.024, +0.089], because the data-rich domain is the hardest and gains less.
  - **Data-rich device's mean norm share:** 0.88 (starter) → 0.21 (AnchorLoRA).
  - **Outage device:** its domain stayed below untuned at every checkpoint in every AnchorLoRA seed; under the starter it peaked +0.28 above.
- **Deliverables:** abstract v3 (889 words, rendered); memo (rendered, synced below); diagram; `research/novelty.md`; ADR 001 with supersession table; reviews + ledger.
- **Checks:**
  - `scripts/check_numbers.py`: PASS;
  - `scripts/check_claims.py`: 12/12;
  - 19 tests;
  - committed token blocks and data manifest;
  - bit-identical reruns across code revisions.
- **Next (only when a GPU slot is granted):**
  1. Run `eval/queue_later.txt` (85 runs, about 3–4 h on a shared GPU): P1b effective-scale-4 sensitivity → P2 matched-work/attribution controls (starter + partial, leave-one-mechanism-out) → P3 clean → P4 rest. To run, copy its lines into `eval/queue.txt` and `scripts/handover_to_queue.sh 0`.
  2. The finals experiments from the astra review: matched-work attribution and weak-client removal; a resource-real Flower run with a real kill; a fresh FlowerTune-Finance holdout.
- **Needs from user:**
  - Register by 15 Oct (after the 12 Oct selection).
  - Teammates' names and skills (the abstract has [TEAM] placeholders).
  - Optional: a phone or Raspberry Pi for the resource-real weak-client run.
- **Risks:**
  1. Judges may read the work as incremental (it is a systems recipe; CF-LoRA and PreLort are close).
  2. The gain is not yet attributed: AnchorLoRA admits more work (143 vs 115 fresh client-rounds over 3 seeds).
  3. Micro and worst-domain costs.
  4. Tiny pilot: 135M, 12 rounds, 2–3-document test sets.

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
_Source of truth: [deliverables/selection-memo.md](deliverables/selection-memo.md), rendered from results._

*Rendered from committed results (`eval/results/v2_canonical.json`; AnchorLoRA/starter n = 5/5, FFA-LoRA n = 5, FlexLoRA n = 5 paired seeds) by `scripts/render_deliverable.py`. Scores 1–5, each with one line of evidence.*

| Criterion | Score | Evidence |
|---|---|---|
| **Winnability** | 4 | In our pilot the starter most teams will submit (PEFT LoRA + FedAvg) lets the 8×-data device's domain gain 0.375 nats/token while all four other domains regress below the untuned model. AnchorLoRA's macro loss is lower than the starter's by 0.081 (paired 95% CI -0.093 to -0.070, n = 5) It is also lower than FFA-LoRA's by 0.050 (-0.053 to -0.046) and FlexLoRA's by 0.083 (-0.091 to -0.074), each with n = 5. All five of AnchorLoRA's domains improve (Bonferroni); every baseline improves only the data-rich one. The evidence is deterministic, provenance-tracked and cross-model reviewed (code 13/14 and abstract 12/12 findings accepted). |
| **Innovation headroom** | 3 | An evaluated *systems recipe*: FFA-LoRA's frozen-A design extended to prefix-masked device updates, plus participation handling and update-share diagnostics. It is not a new primitive. CF-LoRA (Sep 2026) and PreLort (Jun 2026) are close (`research/novelty.md`), and the hostile judge rated novelty 3/5. Headroom for the finals: matched-work attribution, resource-real rank-r_k clients, a real Flower kill, leave-one-out influence. |
| **Feasibility** | 5 | Runs end to end today on a shared M5: 5 heterogeneous devices, seeded dropouts, 4 aggregators + ablations, 19 tests, committed data, one-command reproduction. Nothing is gated on hardware or the user; Azure covers scale-up. The 19–25 Nov exams are left free. |
| **Demo strength** | 4 | Live per-device "who got better" bars plus update-share diagnostics. The data-rich device's round-and-seed mean norm share falls from 0.88 (starter) to 0.22; this is a magnitude diagnostic, not a fairness cap. Kill a Flower node mid-round. Less visual than trading or agent demos. |
| **Fit with the user** | 5 | Distributed systems + LLM fine-tuning + Azure: core Microsoft-style systems work. |

- **Biggest risks:**
  - Judges read it as incremental (published ingredients).
  - Better-tuned baselines may close the gap. The pilot is a full-system comparison with more admitted work; effective-scale and attribution controls are queued (`eval/queue_later.txt`).
  - AnchorLoRA's micro (sample-weighted) loss is 0.116 worse than the starter's, and its worst-domain loss 0.057 higher: the data-rich domain is also the hardest and gains less. This is the price of the macro objective and must be argued, not hidden.
  - The pilot is a 135M model, 12 rounds, with 2–3-document test sets per domain.
- **One-line pitch:** "Federated LoRA in which a Raspberry Pi's data counts. Exact mixed-rank aggregation from a seed-shared frozen A, plus partial-work and per-device weighting. In our pilot it lowered every device's mean domain loss (5 of 5 Bonferroni-significant), while the standard recipe improved only the data-rich one."
- **Overall:** 4.2 / 5, the unweighted mean of the five scores (4 + 3 + 5 + 4 + 5 = 21). The hostile-judge review scored abstract v2 against the official rubric at 3.40/5; v3 applies all 12 of its fixes (not re-scored).
- **Versus the other finalists** (facts as the Supervisor relayed them; the ranking is the Supervisor's call): our spike *replicated* under paired seeds, with bit-identical reruns, and has been compared against two published aggregators. P7's detector spike failed its pre-registered replication. P9 reports 36–43% catch rate on real τ-bench errors.

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

### 2026-10-04 09:45 IST — Lead: Supervisor memory request (08:50 / 09:08) handled; seed-1 replication
- **Memory.** The session died on a model 408 right after the 08:50 request. On resume (09:12), swap stood at 31.5 / 32.8 GB. Three of my runs were alive: 62365 (dropout matrix, `fedavg_ab_het` seed 1, running since 08:42), plus 19612 (dropout `anchor_full` seed 1, ~50 min of progress) and 62358 (clean `anchor_full` seed 0, ~6 min), both of which I had paused (SIGSTOP) at 08:28.
  - **Kept 19612**: it had the most progress and is the key spike replication. Resumed it at nice 10.
  - **Stopped 62365 and 62358** (`kill`). Their in-progress rounds lived only in memory, so that partial work was lost. The 8 completed runs were already saved in `eval/results/v1_*.jsonl`.
  - 19612 then finished. All remaining runs go through one sequential queue under `nice -n 10` (`scripts/gpu_queue.sh` via `scripts/handover_to_queue.sh`; idempotent with `--skip-existing`), which started at 09:41.
  - Swap after the stop: 20.9 GB used.
- **Replication (dropout, 12 rounds).**

  | Run | Seed 0 | Seed 1 |
  |---|---|---|
  | `anchor_full` macro | 2.66508 | 2.66510 |
  | Starter `fedavg_ab_homo` macro | 2.7346 | 2.7535 |
  | `anchor_full` c0 influence share | 0.204 | 0.224 |

  Untuned model: 2.7063. All 5 domains improve over the untuned model on both seeds (`eval/results/v1_summary.md`).

  **Paired 95 % CI** vs the starter (same seed ⇒ same schedule): Δ = −0.079, CI [−0.199, +0.041] at n = 2. Both seeds favour AnchorLoRA (−0.070, −0.088), but **the CI still includes 0, so the result is not yet significant**. Seeds 2–4 are queued; `eval.summarize` now prints this table.
- **New code (13/13 tests).**
  - `Anchor` options for the ratchet: `tau_from` (actual vs planned), `memory_decay`, `segment_norm` (PreLort-style per-column owners), and √n weights. The default path stays bit-identical to the v1 runs; a test asserts it.
  - `eval.run_matrix --skip-existing`.
  - C10 Flower adapter by agent `c10-flower-adapter`: Flower 1.39 Message API with an in-process `LocalGrid` (no Ray) and `kill_node`. Its 3 CPU tests pass. The LLM parity run did not finish on the loaded GPU and is pending.
- **Research.**
  - `research/raw/companies.md`: 25 primary sources; the landscape §6 was rewritten, and 3 claims re-opened by the lead were confirmed.
  - `research/raw/fedlora_frontier.md`: prior-art verdict **NOT FOUND** for the exact combination. The closest work is CF-LoRA (frozen shared A, same rank) and PreLort (nested ranks, trained A). The 13 new arXiv IDs were verified by script; the TSV now has 57 rows.
- Supervisor: memory request done as asked (this entry).

### 2026-10-04 10:00 IST — Lead: dropout stretch evidence (from existing logs, no extra GPU)
- `python -m eval.dropout_analysis --tag v1` → `eval/results/v1_dropout_analysis.md`. Device c4 (tablet, manpages) is offline in rounds 5–9, on top of random offline rounds and deadline cut-offs.
- **Weak devices' work actually counts.** Rounds in which a device's update entered the aggregate (mean over seeds):

  | Device | Baselines | AnchorLoRA (+ memory) |
  |---|---|---|
  | c2 (phone) | 5 / 12 | 9.7 (+2.0) |
  | c4 (tablet) | 3 / 12 | 5.3 (+5.7) |

  Under the baselines, deadline cut-offs throw away the weak devices' partial work (`xxxo-----oo-`).
- **Outage stability.** Peak rise of the outage device's domain loss above the untuned model (3.233):

  | Strategy | Peak rise | n |
  |---|---|---|
  | FedAvg-homo (starter) | +0.27 | 2 |
  | FedAvg-het | +0.30 | 1 |
  | anchor_naive | +0.15 | 1 |
  | **anchor_full** | **−0.021** (never above untuned; monotone decrease) | 3 |

- The queue landed anchor_full seed 2 at **2.6646**. Three AnchorLoRA seeds so far: 2.66508 / 2.66510 / 2.6646.
- Lean Mode (Supervisor 09:40) acknowledged: no new agents; the ADR review agent launched at 09:43 is still running; compute is the single nice-10 queue.

### 2026-10-04 09:52 IST — Lead: independent ADR review; seed-2 replication; PAUSED by Supervisor
- **ADR 001 independent review** (rubber-duck, launched 09:43, before Lean Mode reached me). Verdict: "conditionally yes" as a spike. Defensible claim: *"an evaluated systems integration — not a new primitive — of frozen shared A with prefix-heterogeneous B ranks for exact mixed-rank aggregation, augmented with partial-participation handling, equal-client weighting, clipping, stale-update memory, and product-space influence instrumentation."* Findings:
  1. **Upload accounting** counted r_k columns while the full r_max-wide ΔB was passed on. → *Fixed*: the anchor payload is now sliced to r_k columns and padded on the server (bit-identical numerics; tested). Device memory still allocates r_max, so it is not a measured claim.
  2. **Planned-step rescaling** can amplify short partial updates. → The `anchor_full_tauact` and new `anchor_full_nonorm` ablations will tell.
  3. **Memory reapplies a stale direction** for up to 4 rounds. → Report credited vs actual work (already in `v1_dropout_analysis.md`).
  4. **Influence share** is unbounded near cancellation. → Bounded norm share + leave-one-out are planned (ADR synthesis #7).
  5. **Seeds 0–1 came from different commits.** The code path was identical (the only intervening change was docs), and seeds 2–4 run from a single revision.
  6. **Abstract over-claims:** five rewordings are listed in the resume point (not yet applied).
- **Replication:** seed 2 saved by the queue: AnchorLoRA 2.6646 (114 s), starter 2.7547 (319 s). Paired 95 % CI at n = 3: [−0.111, −0.054].
- **Pause (Supervisor 09:55).** Queue stopped at 09:50 right after seed 2 saved. `anchor_full` seed 3 had just started, so nothing was lost. No processes of ours are running. Code state committed with 13/13 tests. Resume point in *Now*. Idle.

### 2026-10-04 11:40 IST — Lead: resumed (Supervisor 11:10); v2 evidence pipeline
- **Synced.** The Inbox is empty. The `autostash` in the stash list belongs to the P7 worktree (shared stash list), so I left it alone.
- **Published baselines, read from the full papers.**
  - **FlexLoRA** (arXiv 2402.11505 §3): W_g = Σ n_i s B_i A_i / Σ n_i; client i gets B_i = U[:, :r_i] Σ[:r_i, :r_i] / s and A_i = V[:r_i, :]ᵀ.
    - Our choices, documented in the code: round 0 uses the standard LoRA init; late devices are dropped; the global model is evaluated at its rank-16 truncation, and the truncation error is reported.
  - **FFA-LoRA** (ICLR 2024) = `Anchor(homogeneous_rank=8)`: frozen A, FedAvg(n_k) over B.
  - Unit tests check the paper's equations; 17 tests pass.
- **Novelty.**
  - CF-LoRA's full text: frozen shared Ā gives "exactly the average of the clients' induced updates"; its A is *learned* and clustered; 0 hits for any rank-heterogeneity mechanism.
  - PreLort: prefix-nested ranks with segment-wise averaging; the LoRA parameters are trained.
  - → `research/novelty.md` (one-sentence claim, credit table, comparison table); landscape §2 gets 7 verified 2026 rows.
- **Determinism.** The v2 rerun of `anchor_full` seed 0 (code 046b2cdabf9a) reproduces v1 (commit e6b17ac) **bit for bit**: Δ = 0.0 on the macro loss and on every domain.
- **v1 at 3 seeds** (honest costs now visible):

  | Comparison (paired Δ, AnchorLoRA − starter) | Mean | 95 % CI |
  |---|---|---|
  | Macro | −0.083 | [−0.111, −0.054] |
  | Micro (sample-weighted) | **+0.112** (AnchorLoRA worse) | [+0.097, +0.127] |
  | Worst domain | +0.062 | [−0.021, +0.145] |

  Per-domain gains vs the untuned model: AnchorLoRA is CI > 0 on 5/5 domains; the starter only on wiki (+0.369), with the other four significantly negative.
- **Memory rule.** Implemented in `eval/queue_runner.py`. The level hovers at 23–36 %, so runs pause and resume often (9 pauses by 11:30).

### 2026-10-04 11:52 IST — Lead: code review acted on; GPU frozen for Namma Space; hostile-judge review started
- **GPU freeze (Supervisor request, about 11:46).** Our queue runner **PID 44556** has been stopped (SIGSTOP, state T) since about 11:41. Its last child (`fedavg_ab_homo` seed 2) finished at 11:43 and saved its result. **No P1 training process is running.**
  - On "GPU free" I will `kill 44556` (it still holds the old queue code) and restart with `scripts/handover_to_queue.sh 0`.
  - The queue file is unchanged and finished runs are skipped, so nothing is lost or duplicated.
  - CPU-only work continues.
- **Code + eval review (gpt-6-sol, max):** 3 BLOCKING / 10 MAJOR / 1 MINOR. **13 accepted, 1 partly rejected.** Dispositions are appended to `reviews/2026-10-04-code-eval-gpt-6-sol.md`; the ledger row is in `reviews/ledger.tsv`. Key changes:
  - Claims narrowed:
    - no device memory or compute claim; only trainable parameters and uplink ∝ r_k;
    - dropout stability is claimed only at evaluation checkpoints (every 3 rounds);
    - per-domain wins are reported with Bonferroni adjustment.
  - Controls queued: starter + partial work (`fedavg_ab_homo_partial`); leave-one-mechanism-out ablations; effective-scale-4 sensitivity (tag `v2a64`, = literal PEFT r=8, α=32).
  - Reproducibility:
    - the exact token blocks are committed (`eval/data/*.npz`, 1 MB, sha1 c5a6afcf6d80) and the loader prefers them;
    - `scripts/data_manifest.py` finds 0 exact train/eval or cross-domain duplicate documents;
    - but each domain's eval set is **only 2–3 documents** (6,144 tokens), now disclosed;
    - the readmes source pool changed after the `flwr` install, which is why the blocks are committed;
    - `flwr` pinned; a fresh offline venv passes all 19 tests;
    - provenance digests per run; the summarizer rejects duplicate or dirty runs.
- **Abstract v2** is rendered from the template: 865 words, number check PASS. Provisional at n = 3/2 seeds:

  | Comparison (AnchorLoRA − baseline, macro) | Δ | 95 % CI |
  |---|---|---|
  | Starter | −0.083 | [−0.111, −0.054] |
  | FFA-LoRA | −0.051 | [−0.079, −0.024] |
  | FlexLoRA | −0.080 | [−0.188, +0.028] |

  AnchorLoRA improves 4/5 domains Bonferroni-significant.
- **Started** child session "P1 review: abstract+spike (gpt-6-astra)" (max effort): rubric scores, novelty vs CF-LoRA/PreLort, over-claims. The sol session is archived.

### 2026-10-04 12:28 IST — Lead: hostile-judge review acted on; abstract v3
- **gpt-6-astra (max) review** of abstract v2 + spike: **3.40/5** on the official rubric (1 BLOCKING, 8 MAJOR, 3 MINOR). **All 12 accepted**; dispositions appended to `reviews/2026-10-04-abstract-spike-gpt-6-astra.md`, ledger updated.
  - **The BLOCKING finding was right:** exact aggregation ≠ unbiased optimisation.
    - The participation corrections are heuristics.
    - Prefix masks also omit other clients' gradients in columns that only c0 owns.
    - So "unbiased under partial participation" is gone from every deliverable.
  - **Novelty reframed** as "an evaluated systems recipe extending FFA-LoRA's frozen-A design to prefix-masked device updates".
    - Not a new primitive; no "minimal upload" claim.
    - `anchor_full_seg` ≠ PreLort, because PreLort's multi-prefix training is not reproduced.
  - **The reviewer recounted admitted work over seeds 0–2:**

    | Quantity | AnchorLoRA | Starter |
    |---|---|---|
    | Fresh client-rounds | 143 | 115 |
    | Partial client-rounds | 28 | 0 |
    | Replays | 32 | 0 |

    So the pilot is a **full-system comparison, not matched work**. The attribution controls (P2) are the decisive next experiment.
- **Abstract v3:** 889 words, all 8 sections, number check PASS, per-comparison shared n in the table, exploratory labels, an operational definition of meaningful participation.
- **Also updated:** ADR 001 (supersession table), `research/novelty.md`, landscape, diagram, memo (re-rendered and synced).
- **Provenance note (review #7):** the ten provisional v2 rows predate the per-run `data_digest`/`model_revision` fields. Continuity rests on the committed token blocks plus the bit-identical v1→v2 reruns. The original README document inventory cannot be rebuilt (source pool changed).

### 2026-10-04 13:05 IST — Lead: definition of done met; slot free
- **Queue:** runner PID 78322 finished all 20 P1 runs (5 seeds × AnchorLoRA / starter / FFA-LoRA / FlexLoRA, dropout scenario) at 12:57 under the memory guard, then exited. Post-P1 work was moved to `eval/queue_later.txt` to free the GPU.
- **Final numbers:** in *Now*. All three paired macro CIs exclude zero; FlexLoRA's comparison, provisional at n = 2, is now clear at n = 5. FlexLoRA's served-model truncation error averages 0.51 %.
- **Worst-domain cost is now significant:** +0.057 [+0.024, +0.089] vs the starter. Abstract and memo say so explicitly.
- **New `scripts/check_claims.py`** asserts the 12 qualitative claims in the deliverables against `v2_canonical.json`; all pass. Abstract v3 re-rendered (889 words); memo re-rendered and synced.
- **Supervisor messaged:** "DONE — slot free".

### 2026-10-04 19:57 IST — Lead: demo phase started
- Read PLAYBOOK §11.
  - Bar: one-command `demo/run.sh`, first visual ≤ 60 s, offline, CPU only.
  - Real first: real model, real text, committed runs; simulation second and labelled.
  - Baseline side by side; one judge knob; every number from committed results or live code.
  - Deliverables: `SCRIPT.md`, `fallback/`, `smoke.sh`, a gpt-6-astra demo review.
- CPU feasibility, measured (nice 10, 4 threads):

  | Operation | Time |
  |---|---|
  | Train step, batch 4×128 tokens | 1.32 s |
  | Train step, batch 2×64 tokens | 0.28 s |
  | Eval forward, 8×128 | 1.06 s |
  | Full-fidelity 12-round run (estimate) | ≈ 11 min |

  So any live element needs a reduced configuration, validated offline against the committed pattern.
- Spawned child session **"P1 demo builder"** (autopilot). It has full context plus the Supervisor's suggestion ("unplug the tablet"), the memory and CPU rules, and the wording constraints from both reviews. Phase 1 is a proposal; it waits for lead approval.

### 2026-10-04 20:11 IST — Lead: demo proposal approved ("Pull the plug", live)
- **Builder's proposal:**
  - Two federations (the starter and AnchorLoRA) train the real SmolLM2-135M side by side on CPU through the Flower Message API (in-process `LocalGrid`), with paired availability.
  - The judge unplugs or replugs any device at any round (`kill_node` in both grids). The page shows per-domain Δ-vs-untuned bars, a "reusing last update (age k/4)" badge, and a pre-recorded no-unplug ghost.
  - Knobs: which device and for how long, plus the seed.
  - The page opens on the REAL committed 5-seed replay; every number carries a provenance chip.
- **Live configuration:** the committed one except batch 1×64, eval on 8×64 tokens per domain every round, 6 rounds. Measured at 12.5–16.5 s/round for both federations, about 90 s per run, peak RSS 1.27 GB.
  - Pilot (seed 0, tablet out rounds 2–4), loss change vs untuned at round 5: the starter's four small domains rose +0.11 to +0.14; AnchorLoRA's all fell.
  - Validation is pre-registered: P1 (AnchorLoRA's manpages below untuned at every live eval), P2 (the starter's manpages above both untuned and AnchorLoRA at round 6), P3 (the unplug's own effect is larger for the starter). Seeds 0–4; results go to `demo/validation/`.
- **No components/ changes; no GPU.**
- **My amendments:**
  - Bonferroni intervals for per-domain bars; every number from canonical keys;
  - no claim if P3 fails;
  - explicit labels: simulated budgets, in-process grid (not an OS-process kill), reduced config, pre-recorded ghosts;
  - fresh work kept separate from memory reuse;
  - wording guardrails from the reviews;
  - headless smoke ≤ 3 min;
  - matplotlib PNG and in-page RECORDED fallback;
  - one validation batch at a time.

### 2026-10-04 20:47 IST — Lead: live-config validation passed (pre-registered)
- `demo/validation/RESULTS.md` (commit 1833303; code 5d655ba, code_sha cc9d632a1a27, clean): seeds 0–4, none picked; each run is a fresh process of the demo's live engine (Flower LocalGrid, CPU, nice 10); the tablet is unplugged in rounds 2–6.
- **All three pre-registered checks pass in all 5 seeds**, and every round-1 rerun is bit-identical:
  - **P1:** AnchorLoRA's manpages stays below untuned at every live evaluation (max −0.0067 to −0.0107).
  - **P2:** at round 6 the starter's manpages is above untuned (+0.076 to +0.140) and above AnchorLoRA's (−0.026 to −0.040).
  - **P3:** the unplug's own effect at round 6 is larger for the starter (+0.009 to +0.029 vs −0.002 to +0.008).
- **Honest read, agreed with the builder:** most of the round-6 gap is the starter's domination, visible in the no-unplug ghost. The unplug's own effect is small but points the same way in all 5 seeds. The talk track must say exactly that.

### 2026-10-04 21:10 IST — Lead: demo built; clean-checkout verification PASS; astra demo review started
- **Builder delivered** `demo/` (main through c194e83; components/ untouched; 19 tests):
  - `run.sh`: the replay works on system python3 alone; live mode needs `fetch.sh` once.
  - `server.py`, `web/` (offline vanilla JS/SVG), `live_engine.py`, `validate.py` and `validation/`, `export_replay.py`, `render_fallback.py`.
  - `fallback/`: PNG frames, a GIF and a recorded live run that replays in-page, labelled RECORDED.
  - `smoke.sh`, `SCRIPT.md`, `README.md`.
- **Lead verification from a clean clone of origin/main** (10209ca, `/tmp/p1_demo_verify`):
  - `fetch.sh` succeeded offline from local caches.
  - `smoke.sh` PASS in 67 s, including:
    - a fresh live run bit-identical to the committed ghost and unplug runs;
    - Flower path == in-process harness, max |diff| 0.0;
    - the tablet unplugged in both grids, with AnchorLoRA reusing its last update at age 1/4.
  - `run.sh` gave a first visual in 0.6 s.
  - Browser check at 1440×900: tab 1 opens on the REAL committed 5-seed per-domain bars with Bonferroni whiskers, a paired-CI ledger and file·key provenance on every number. Tab 3's live panel carries the reduced-config, in-process-kill and pre-recorded-ghost labels. Server stopped by PID afterwards.
- Started child session **"P1 review: demo (gpt-6-astra)"** (max): a hostile judge watching the demo. The builder stays idle for fixes.

### 2026-10-04 21:31 IST — Lead: astra demo review in; all 8 findings accepted; builder fixing
- **gpt-6-astra (max) demo review:** **7/10** "would this win the room"; 0 BLOCKING, 5 MAJOR, 3 MINOR.
  - Its own run of smoke passed (83 s), first paint came at 0.08 s, and a six-round live run reproduced all 60 committed validation losses exactly. It found no invented numbers.
- **The fixes, now with the builder:**
  - an event-gated stage flow, since wall-clock choreography missed the round-2 unplug;
  - honest full-system wording instead of "memory absorbs it": 93 % of the seed-0 gap exists with nobody unplugged;
  - the RECORDED handoff must stop live;
  - the stage layout must fit 1440×900;
  - smoke must assert P1–P3 are true, plus a UI self-test;
  - corrections to a reversed caption formula, the memory-banner text and the header wording.
- Dispositions appended to the review file; ledger row added; reviewer session archived.
