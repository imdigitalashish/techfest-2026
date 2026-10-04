# Round 1 abstract (draft v1, 4 Oct 2026) — Perceptron Hackathon 2026, Problem 1

**AnchorLoRA: federated LoRA that weak devices can join, dropouts can't derail, and no device can dominate**

*Word count (body, excluding this title and the notes at the end): see the count in the thought node. Pilot numbers are single-seed, 12-round results from our walking skeleton (`eval/results/v1_summary.md`). They motivate the plan; they are not the final evaluation.*

### Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 1: *Cheap Fine-Tuning Across Weak, Scattered Devices.* Organisations hold text they cannot pool: trading desks in different jurisdictions, hospital sites, staff laptops and phones. Fine-tuning one shared small language model *in place*, with LoRA adapters on devices of very different power, is the cheapest route to a specialised model, and it is a systems problem disguised as an optimisation problem.

### Understanding of the challenge
Three things break the obvious recipe (PEFT LoRA + Flower FedAvg):
1. **LoRA updates are products.** A device's weight change is ΔW_k = B_k·A_k. Averaging A and B separately gives mean(B)·mean(A) ≠ mean(B·A). With different ranks per device, the zero-padded averages are wrong again. In our pilot, FedAvg over A and B misallocated 9–36% of each round's update in weight space.
2. **Unequal work and dropouts bias the objective.** A phone that finishes 2 local steps (or is cut off by the round deadline, or vanishes for five rounds) counts as if its data barely existed. The model then optimises for always-on, fast devices (FedNova's "objective inconsistency").
3. **Sample-weighted averaging is a micro-average.** A device with 8× the data sets the direction. In our pilot under FedAvg, the data-rich device's influence share was ≈1.0: its own domain improved by 0.36 nats/token while **all four other domains ended worse than the untuned model**. The weak devices are not just ignored; they are harmed.

So the three goals in the brief are really three properties of the *aggregation*: exact, unbiased under partial participation, and balanced.

### Proposed approach
- **Stack:** HF PEFT LoRA on attention projections of SmolLM2-135M (pilot), then Qwen2.5-0.5B and TinyLlama-1.1B. Flower `ServerApp`/`ClientApp`, one process per device. PyTorch on Apple-silicon MPS, plus an Azure GPU.
- **AnchorLoRA aggregator (our spike):**
  - **Shared anchor.** Every device regenerates the same frozen A from a public seed (A is never transmitted) and trains only the first r_k columns of B, with r_k ∈ {2,…,16} chosen to fit its memory. Because A is shared, Σ_k w_k ΔB_k·A *is* the average of the devices' weight updates: aggregation is exact for any mix of ranks. A rank-2 device uploads 2·d_out numbers per layer.
  - **Corrections on top of exactness.** Classic federated corrections now apply exactly: FedNova-style step normalisation, so partial work from deadline cut-offs is kept rather than discarded; memory of absent devices' last update for ≤4 rounds (MIFA-style); macro (per-device) weights with median-norm clipping.
  - **Influence audit.** Every round we compute each device's share of the applied update in weight space, plus a leave-one-device-out ground truth, so "quiet domination" becomes a number on the dashboard.
- **Data:** five real-text domains, one per device (Wikipedia, Python, C headers, READMEs, man pages; pilot), then financial-sentiment classification and Dolly-15k categories split with Dirichlet α ∈ {0.1, 0.5}.

### Minimum Viable (what will exist and be demoable)
- *Simulate 3–5 nodes with different data splits and compute budgets.* Five devices (workstation, laptop, phone, Raspberry-Pi and tablet profiles): distinct domains, 8× quantity skew, ranks 16/8/4/2/4 and local steps 16/8/4/2/4. **This already runs** as a contract-tested walking skeleton.
- *Show the shared model converges despite heterogeneity.* Per-domain, macro and worst-domain held-out loss curves vs rounds, bracketed by centralised (pooled) and local-only bounds.
- *Pilot (single seed, 12 rounds, with dropouts):* AnchorLoRA reached the lowest macro loss (2.665 vs 2.735 for the starter baseline; untuned model 2.706). It **improved every domain** over the untuned model, held the data-rich device's influence share at 0.20, and the loss never rose between evaluations.

### Stretch ambitions
- **Dropout mid-training:** a seeded availability process (offline rounds, deadline cut-offs, a 5-round outage) shared by all methods. Live, we kill a Flower SuperNode process mid-round and show the loss curve staying flat.
- **Smarter aggregation vs naive averaging:** an ablation ladder from FedAvg to full AnchorLoRA, one mechanism at a time.
- Then asynchronous buffered rounds, and a physical phone or Raspberry Pi as one device.

### Novelty / differentiation
Beyond the starter baseline: (1) **exactness for any rank mix at minimal upload**, which lets established federated corrections apply *exactly* to LoRA; (2) a **macro objective**, where every participant's domain counts rather than every sample; (3) an **auditable influence metric** with Sybil and leave-one-out tests. We build openly on FFA-LoRA (frozen A, ICLR 2024), FedNova and MIFA. Our contribution is their integration for weak, intermittent devices, plus the measurement.

### Evaluation plan
- **Metrics:** macro held-out loss/perplexity (equal weight per device domain); worst-domain loss; weak-device gain over the base model; task accuracy (finance); dominance index (data-rich device's influence share and its leave-one-out effect); aggregation error; largest loss spike after dropouts; upload bytes and peak memory per device class.
- **Baselines:** FedAvg over A and B (starter), HetLoRA-style zero-padding, FFA-LoRA, exact weight-space averaging + SVD (FlexLoRA-style), FedEx-LoRA, RoLoRA; plus centralised and local-only bounds.
- **Protocol:** identical seeded dropout schedules for every method (paired); ≥5 seeds with 95% confidence intervals; a Latin-square rotation of domains across device budgets, so budget, domain and data size aren't confounded; a Sybil test (the data-rich device split into two identities).

### Feasibility and risks
- **Team:** Ashish (large-scale systems, frontier models; Microsoft) owns the aggregator and Flower deployment. Member 2 (optimisation/ML) owns baselines and ablations. Member 3 (data/visualisation) owns datasets, the harness and the dashboard.
- **Milestones:**
  - Wk 1–2: baselines on finance data, Flower multi-process run.
  - Wk 3–4: full ablations, 5 seeds.
  - Wk 5: 0.5B–1.1B runs on Azure.
  - Wk 6: dashboard and kill-a-node demo.
  - The 19–25 Nov exam week is kept free; buffer until the 1 Dec midway report.
  - Wk 7–9: physical-device stretch, hardening, rehearsal.
- **Risks and mitigations:**
  - A frozen A may limit expressiveness (RoLoRA's critique): add periodic anchor refresh and larger ranks for strong devices.
  - Per-device weights are Sybil-sensitive: √n weights and device registration.
  - Simulation is not hardware: measure memory and time on a real phone/Pi via Flower.
  - Small models may hide effects: confirm at 1.1B.

---
*Notes for the team (not part of the submission):*
- Prior art for "frozen shared A + nested ranks" was searched on 4 Oct and **no paper doing exactly this was found**, but that novelty is UNVERIFIED, so the abstract claims the integration, not the trick.
- Replace member placeholders with real names and skills before submission.
- Re-check the word count after edits; the target is 600–900.
