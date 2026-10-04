# Round 1 abstract (v3, 4 Oct 2026) — Perceptron Hackathon 2026, Problem 1

**AnchorLoRA: federated LoRA for weak, intermittent devices — exact mixed-rank aggregation with measured participation and influence**

*Body 600–900 words. Every number is rendered from committed results (`eval/results/v2_canonical.json`) by `scripts/render_deliverable.py` and verified by `scripts/check_numbers.py`. Edit the template (`round1-abstract.template.md`), not this file. Wording follows the two cross-model reviews in `reviews/`.*

### Problem & theme chosen
Theme 1 (Efficient AI at Scale), Problem 1: *Cheap Fine-Tuning Across Weak, Scattered Devices.* Trading desks, hospital sites and staff phones hold text that cannot be pooled. We target collaborative specialisation of a small model without pooling raw text; the challenge couples device resource limits, interrupted work and conflicting local objectives.

### Understanding of the challenge
The starter recipe (PEFT LoRA + Flower FedAvg) has three failure modes:
1. **LoRA updates are products.** ΔW_k = B_k·A_k, so averaging A and B separately gives mean(B)·mean(A) ≠ mean(B·A). Zero-padding mixed ranks adds more error. In our pilot, the starter's mean relative round-update aggregation residual was 5.7%; its effect on task loss is not isolated.
2. **Unequal work and dropouts bias the objective:** discarding weak devices' late or partial work favours always-on, fast devices (FedNova's "objective inconsistency").
3. **Sample-weighted averaging is a micro-average.** Under the starter, the 8×-data device's domain improved by 0.37 nats/token while all four other domains ended *worse* than the untuned model.

Weak devices must supply useful fresh updates within limited resources, and availability bias or quantity skew must not silently decide whose text the model serves. These are systems and statistical requirements, not consequences of exact aggregation. Our primary target is equal-device held-out loss; we report the sample-weighted trade-off.

### Proposed approach
- **Pilot:** HF PEFT LoRA on SmolLM2-135M, simulated on one shared model. Clients update nested B prefixes (ranks 2–16) under a shared frozen A, regenerated from a public seed, and a common LoRA scale; their zero-padded deltas aggregate exactly in weight space, including after the corrections below.
- **Cost:** each payload holds r_k·d_out fp32 values per layer; at matched ranks the pilot's q/v adapters need 2.5× fewer uplink values than A+B. Active coefficients and logical uplink shrink with rank; measured RAM, total communication and throughput are not yet established.
- **Participation heuristics:**
  - partial work cut off by the round deadline is kept and step-normalised (FedNova-style);
  - an absent client's clipped direction is reused for up to four rounds (MIFA-style);
  - included clients are weighted equally.

  These do not guarantee unbiased optimisation; ablations test each.
- **Finals:** Flower processes with seed-only A transport and measured resources; FlowerTune-Finance accuracy with non-IID splits; 0.5–1.7B models on Azure.

### Minimum Viable (what will exist and be demoable)
- *Simulate 3–5 nodes with different data splits and compute budgets.* **Already running:** five device profiles (workstation to Raspberry Pi): distinct domains, 8× quantity skew, ranks/steps 16/8/4/2/4, seeded dropouts.
- *Show convergence despite heterogeneity:* per-domain and macro held-out loss against rounds (so far: short-horizon improvement).
- **Exploratory pilot** (SmolLM2-135M, 12 rounds, dropout scenario, fixed text; untuned 2.706; paired t intervals describe seed variability only):

  | Method | Macro loss | AnchorLoRA − method, 95% CI (shared seeds) |
  |---|---|---|
  | **AnchorLoRA** | **2.665** | — |
  | Starter | 2.748 | -0.083 (-0.111 to -0.054; n=3) |
  | FFA-LoRA | 2.716 | -0.051 (-0.079 to -0.024; n=2) |
  | FlexLoRA | 2.745 | -0.080 (-0.188 to 0.028; n=2) |

  - Paper-derived baselines, one fixed optimiser and scale; a full-system comparison under paired availability, not matched completed work.
  - All five AnchorLoRA mean domain losses decrease; 4 of five Bonferroni-adjusted intervals exclude zero.
  - The starter's only positive domain gain is the data-rich one.

### Stretch ambitions
- **Dropout mid-training.** A five-round tablet outage is built in.
  - Under AnchorLoRA, the tablet's domain loss stayed below untuned at rounds 3, 6, 9 and 12 in every seed; under the starter it peaked +0.28 above. Sampled checkpoints do not exclude intervening spikes.
  - Next: per-round recovery against paired no-outage/no-replay controls, then a real Flower process kill.
- **Smarter vs naive aggregation:** an ablation ladder from FedAvg to AnchorLoRA, one mechanism at a time.

### Novelty / differentiation
We extend FFA-LoRA's frozen-A design (ICLR 2024) to prefix-masked device updates and evaluate participation handling and update-share diagnostics for one shared model. CF-LoRA (2026) learns A before freezing it for clustered B aggregation; PreLort (2026) trains both factors with a multi-prefix objective and segment-wise aggregation. Our contribution is the tested systems recipe and its cost/utility trade-offs, not a new exactness primitive or a minimum-communication theorem. The data-rich client's round-and-seed mean norm share of the update falls from 0.88 to 0.22. This is a magnitude diagnostic, not a fairness cap or causal estimate.

### Evaluation plan
- **Metrics:**
  - equal-device (macro) and per-domain held-out loss; finance accuracy;
  - sample-weighted loss: AnchorLoRA's is 0.112 worse, and no worst-domain improvement is established;
  - aggregation residual, update shares, dropout recovery, bytes, peak memory.
- **Meaningful participation:** fresh updates within a measured device budget that improve held-out utility versus a paired run withholding that client.
- **Controls:** matched-work, rank-matched and leave-one-mechanism-out runs; FedEx-LoRA, PreLort, RoLoRA; local-only and centralised references.
- **Protocol:** freeze the primary macro comparison before a fresh holdout; size seeds for target precision; adjust the prespecified domain family; rotate domains across budgets and independently vary data quantity and outages (including the data-rich client); identity-split (Sybil) tests.

### Feasibility and risks
- **Team:**
  - [TEAM: lead — distributed systems, LLMs]: aggregator and Flower deployment.
  - [TEAM: member 2 — optimisation/ML]: baselines and controls.
  - [TEAM: member 3 — data/visualisation]: datasets, harness and dashboard.
- **Milestones:** weeks 1–2 controls and finance data; 3–4 Flower processes, resource-real weak clients; 5 larger models on Azure; 6 dashboard, kill-a-node demo; 19–25 Nov exams kept free; 1 Dec midway report.
- **Risks and mitigations:**
  - Frozen A may cap expressiveness (RoLoRA): anchor refresh, larger ranks on strong devices.
  - Equal-client and square-root weights remain identity-sensitive: authenticate participants and test data-preserving identity splits.
  - Gains may partly reflect extra admitted work or replay: controls queued.
  - The 12-round pilot's per-domain test sets are 6,144 tokens from 2–3 documents: the finals use a larger untouched holdout.

---
*Notes for the team (not part of the submission):*
- Replace the [TEAM] placeholders with names and skills.
- Novelty wording follows `research/novelty.md`.
- Re-render after any new results: `python -m eval.summarize --tag v2 && python -m eval.dropout_analysis --tag v2 && python scripts/render_deliverable.py deliverables/round1-abstract.template.md deliverables/round1-abstract.md && python scripts/check_numbers.py deliverables/round1-abstract.md`.
- Before submitting, confirm `dropout.anchor_full.outage_peak_rise_max < 0` in `eval/results/v2_dropout_canonical.json`. The "every seed stayed below" sentence depends on it.
