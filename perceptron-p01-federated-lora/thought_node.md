# Perceptron P1 · Cheap fine-tuning across weak, scattered devices — Thought Node

> Journal for `perceptron-p01-federated-lora/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 5–6, ACTIVE again (Supervisor 11:10, slot freed by EV C2). The 12 Oct Perceptron pick is open between P1, P7 and P9, and the evidence decides it.
- **Definition of done (Supervisor 11:10):**
  1. ≥ 5 paired seeds: AnchorLoRA vs the starter vs ≥ 1 published aggregator, dropout scenario included; per-domain gains; data-rich influence share.
  2. Novelty positioned against CF-LoRA and PreLort.
  3. Final abstract with numbers checked against results, plus the diagram.
  4. Cross-model reviews (gpt-6-astra on abstract + spike; gpt-6-sol on code + eval).
  5. Final memo; thought node current; pushed; message "DONE — slot free".
- **Doing (11:40):**
  - **Queue** (`eval/queue_runner.py`, one run at a time, nice 10, paused below 25 % memory level, resumed above 30 %): 69 v2 runs from one code hash.
    - P1: AnchorLoRA / starter / FFA-LoRA / FlexLoRA × 5 seeds, dropout.
    - P2: ablations (nonorm, tauact, PreLort-style seg) × 5.
    - P3: clean scenario × 5. P4: ladder. P5: extras.
    - ≈ 2.5 min per run; P1 due around 12:20.
  - **Child session** "P1 review: code+eval (gpt-6-sol)" is running.
  - **Done since resume:**
    - FFA-LoRA + FlexLoRA implemented from the papers' equations;
    - bounded norm shares; sliced uploads; `env.code_sha` provenance;
    - `research/novelty.md`;
    - ADR 001 update with the 09:50 review dispositions;
    - summarizer with paired / per-domain CIs and the micro loss;
    - `scripts/render_deliverable.py` + `scripts/check_numbers.py` (abstract numbers come from results).
- **Next:**
  1. When P1 lands: abstract v2 from a template.
  2. Start the astra review (abstract + spike).
  3. Fold in the sol review.
  4. Final memo.
  5. DONE message.
- **Needs from user:**
  - Register by 15 Oct (after the 12 Oct selection).
  - Teammates' names and skills (the abstract uses [TEAM] placeholders).
  - Optional: a phone or Raspberry Pi for the physical-device stretch.
- **Risks:**
  1. Prior art is close on both halves (CF-LoRA, PreLort). We claim the combination + evaluation only.
  2. Part of the gain may come from planned-step amplification or memory replay; the ablations will tell.
  3. Micro (sample-weighted) loss is *worse* under AnchorLoRA: the data-rich domain gains less. It must be stated in the abstract.
  4. 12-round runs on a local-text proxy.

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
