# Perceptron P1 · Cheap fine-tuning across weak, scattered devices — Thought Node

> Journal for `perceptron-p01-federated-lora/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1 — SOTA research (Phase 0 done 02:10 IST); walking skeleton started in parallel.
- **Plan (overnight, IST):** 02:00–02:30 brief + research fan-out + env → 02:30–04:00 contracts + walking skeleton + eval harness + baseline numbers → 04:00–05:00 landscape + per-component research + ADR 001 → 05:00–06:30 spike + head-to-head runs + first auto-research loop → 06:30–07:45 abstract, architecture, selection memo, fact-check → 08:00 everything pushed; Supervisor messaged.
- **Doing:** 7 background research agents: r1 LoRA aggregation · r2 weak devices/dropout/async · r3 fairness/dominance · r4 frameworks/code/models · r5 what companies ship · r6 benchmarks/datasets/social · fp-bottleneck (First Principles). Lead: venv (`.venv`, uv, Python 3.12) and skeleton.
- **Next:** contracts → skeleton → baseline numbers → landscape.md → per-component research → ADR 001 → spike runs → deliverables.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** (1) the M5 (24 GB) is shared with 19 sibling projects, so runs stay small (≤0.5B models, minutes each); (2) novelty claims must survive 2025–26 prior art (the research threads check this); (3) Flower's Ray-based simulation on macOS may be fragile, so we use an in-process simulator for research loops plus a Flower adapter for the demo.

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
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:10 IST — Lead: Phase 0 done, Phase 1 launched
- Read PLAYBOOK, this brief and the full official statement. Extracted the constraints and an evidence list (E1–E6) mapped to the judging weights (above). Key insight: the midway check penalises pivoting, so the abstract must promise only what we can build.
- Machine: Apple M5, 24 GB, macOS 26.2, 71 GB free disk. Azure: "Visual Studio Enterprise Subscription" enabled. PyPI today: flwr 1.39.0, flwr-datasets 0.6.1, peft 0.21.2, torch 2.14.1, mlx-lm 0.32.0.
- Spawned 7 background agents (r1–r6 research, fp-bottleneck). Venv install running.
