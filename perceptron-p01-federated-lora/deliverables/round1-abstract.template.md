# Round 1 abstract (v2, 4 Oct 2026) — Perceptron Hackathon 2026, Problem 1

**AnchorLoRA: exact mixed-rank federated LoRA in which weak, intermittent devices still count**

*Body 600–900 words. Every number is rendered from committed results (`eval/results/v2_canonical.json`, 5 paired seeds) by `scripts/render_deliverable.py` and verified by `scripts/check_numbers.py`. Edit the template (`round1-abstract.template.md`), not this file.*

### Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 1: *Cheap Fine-Tuning Across Weak, Scattered Devices.* Trading desks across jurisdictions, hospital sites and staff phones hold text that cannot be pooled; fine-tuning one shared small model in place with LoRA is the cheapest way to specialise it. It is a systems problem disguised as an optimisation problem.

### Understanding of the challenge
The starter recipe (PEFT LoRA + Flower FedAvg) breaks in three places:
1. **LoRA updates are products.** ΔW_k = B_k·A_k, so averaging A and B separately gives mean(B)·mean(A) ≠ mean(B·A). In our pilot the starter's applied update was {{dropout.fedavg_ab_homo.agg_err_mean|pct.1f}}% off the true average of device updates.
2. **Unequal work and dropouts bias the objective.** Weak devices finish fewer steps, miss deadlines or vanish; discarding their work favours always-on, fast devices (FedNova's "objective inconsistency").
3. **Sample-weighted averaging is a micro-average.** A device with 8× the data sets the direction. Under the starter, the data-rich domain improved by {{dropout.fedavg_ab_homo.wiki.gain_mean|.2f}} nats/token while all four other domains ended *worse* than the untuned model (every 95% confidence interval below zero).

So the brief's three goals are three properties of the aggregation: exact, unbiased under partial participation, balanced.

### Proposed approach
- **Stack:** HF PEFT LoRA on SmolLM2-135M, then Qwen2.5-0.5B and SmolLM2-1.7B; Flower `ServerApp`/`ClientApp`, one process per device; PyTorch MPS plus Azure.
- **Shared anchor.** Every device regenerates the same frozen A from a public seed (never transmitted) and trains only the first r_k ∈ {2,…,16} columns of B, so its trainable parameters and uplink scale with r_k: r·d_out numbers per layer, {{const.upload_ratio_theory|.1f}}× fewer than sending A and B. Because A is shared, Σ_k w_k ΔB_k·A *is* the average of the devices' weight updates for any mix of ranks.
- **Participation corrections:**
  - partial work cut off by the round deadline is kept and step-normalised (FedNova-style);
  - an absent device's last update is reused for ≤4 rounds (MIFA-style);
  - per-device (macro) weights with median-norm clipping.

  Sharing A removes only the factorisation error; ablations test the corrections.
- **Influence audit:** each round logs every device's share of the applied update; leave-one-device-out and Sybil tests are planned.
- **Data:** the pilot uses five real-text domains, one per device; the finals use FlowerTune-Finance (FPB/FiQA/TFNS accuracy) with Dirichlet non-IID splits.

### Minimum Viable (what will exist and be demoable)
- *Simulate 3–5 nodes with different data splits and compute budgets.* **Already running:** five device profiles (workstation to Raspberry Pi) with distinct domains, 8× quantity skew, ranks and local steps 16/8/4/2/4, and seeded dropouts.
- *Show convergence despite heterogeneity:* per-domain, macro and worst-domain held-out loss against rounds.
- **Pilot result** (SmolLM2-135M, 12 rounds, dropout scenario, {{dropout.anchor_full.n|d}} paired seeds; untuned macro loss {{base.macro|.3f}}):

  | Method | Macro loss | AnchorLoRA − method (95% CI) |
  |---|---|---|
  | **AnchorLoRA** | **{{dropout.anchor_full.macro_mean|.3f}}** | — |
  | Starter | {{dropout.fedavg_ab_homo.macro_mean|.3f}} | {{dropout.spike_vs_fedavg_ab_homo.macro_mean|.3f}} ({{dropout.spike_vs_fedavg_ab_homo.macro_lo|.3f}} to {{dropout.spike_vs_fedavg_ab_homo.macro_hi|.3f}}) |
  | FFA-LoRA | {{dropout.ffa_lora.macro_mean|.3f}} | {{dropout.spike_vs_ffa_lora.macro_mean|.3f}} ({{dropout.spike_vs_ffa_lora.macro_lo|.3f}} to {{dropout.spike_vs_ffa_lora.macro_hi|.3f}}) |
  | FlexLoRA | {{dropout.flexlora.macro_mean|.3f}} | {{dropout.spike_vs_flexlora.macro_mean|.3f}} ({{dropout.spike_vs_flexlora.macro_lo|.3f}} to {{dropout.spike_vs_flexlora.macro_hi|.3f}}) |

  AnchorLoRA improved {{dropout.anchor_full.domains_ci_pos_bonf|d}} of 5 domains with Bonferroni-adjusted intervals above zero; the starter improved only the data-rich one.

### Stretch ambitions
- **Dropout mid-training.** A five-round outage of the tablet is built into the dropout scenario.
  - Under the starter, the tablet's domain loss peaked {{dropout.fedavg_ab_homo.outage_peak_rise_mean|+.2f}} above the untuned model.
  - Under AnchorLoRA it stayed below it at every evaluation checkpoint (every 3 rounds; mean peak {{dropout.anchor_full.outage_peak_rise_mean|+.3f}}).
  - Live demo: kill a Flower SuperNode mid-round.
- **Smarter vs naive aggregation:** an ablation ladder from FedAvg to AnchorLoRA, one mechanism at a time.

### Novelty / differentiation
Each half of our design exists alone:
- **Frozen A:** FFA-LoRA (ICLR 2024); CF-LoRA (2026) shares a learned frozen A.
- **Prefix-nested ranks:** PreLort (2026).

To our search, no method combines a seed-generated frozen A with nested device ranks, making mixed-rank aggregation exact at minimal upload. We contribute that combination as an evaluated system, not a new primitive, with participation corrections, a macro objective (every device's domain counts, not every sample) and an influence audit. The data-rich device's bounded norm share of each update falls from {{dropout.fedavg_ab_homo.c0_norm_mean|.2f}} under the starter to {{dropout.anchor_full.c0_norm_mean|.2f}}, against a fair share of 0.2.

### Evaluation plan
- **Metrics:**
  - macro, worst-domain and per-domain held-out loss; finance accuracy;
  - micro (sample-weighted) loss, to expose the trade-off: AnchorLoRA's is {{dropout.spike_vs_fedavg_ab_homo.micro_mean|.3f}} *worse* than the starter's, because the data-rich domain gains less;
  - influence shares, aggregation error, post-dropout spikes, upload bytes, peak memory.
- **Baselines:** starter, FFA-LoRA, FlexLoRA, HetLoRA-style padding (implemented); FedEx-LoRA, PreLort, RoLoRA, centralised and local-only bounds (next).
- **Protocol:**
  - identical seeded device schedules for every method (paired), ≥5 seeds, 95% t-intervals;
  - a Latin-square rotation of domains across device budgets, so budget, domain and data size aren't confounded; a Sybil test.

### Feasibility and risks
- **Team:**
  - [TEAM: lead — distributed systems, LLMs] owns the aggregator and Flower deployment;
  - [TEAM: member 2 — optimisation/ML] owns baselines and ablations;
  - [TEAM: member 3 — data/visualisation] owns datasets, the harness and the dashboard.
- **Milestones:**
  - Weeks 1–2: finance data, Flower multi-process. Weeks 3–4: baselines, Latin square. Week 5: 0.5–1.7B on Azure. Week 6: dashboard, kill-a-node demo.
  - 19–25 Nov exams kept free; 1 Dec midway report; physical devices and rehearsal to 15 Dec.
- **Risks and mitigations:**
  - Frozen A may cap expressiveness (RoLoRA argues for trainable A): periodic anchor refresh, larger ranks on strong devices.
  - Macro weights are Sybil-sensitive: √n weights, device registration.
  - Part of the gain may come from step-normalisation or memory replay: ablations queued.
  - Simulation isn't hardware, and the pilot's per-domain test sets are only 6,144 tokens: measure a real phone or Pi via Flower; use FlowerTune's public test sets.

---
*Notes for the team (not part of the submission):*
- Replace the [TEAM] placeholders with names and skills.
- Novelty wording follows `research/novelty.md`: never "first to freeze A" or "first nested ranks".
- Re-render after any new results: `python -m eval.summarize --tag v2 && python -m eval.dropout_analysis --tag v2 && python scripts/render_deliverable.py deliverables/round1-abstract.template.md deliverables/round1-abstract.md && python scripts/check_numbers.py deliverables/round1-abstract.md`.
