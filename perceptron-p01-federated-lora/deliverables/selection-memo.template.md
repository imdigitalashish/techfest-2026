# Selection memo — Perceptron P1 (federated LoRA), final version for the 12 Oct pick

*Rendered from committed results (`eval/results/v2_canonical.json`; AnchorLoRA/starter n = {{dropout.anchor_full.n|d}}/{{dropout.fedavg_ab_homo.n|d}}, FFA-LoRA n = {{dropout.ffa_lora.n|d}}, FlexLoRA n = {{dropout.flexlora.n|d}} paired seeds) by `scripts/render_deliverable.py`. Scores 1–5, each with one line of evidence.*

| Criterion | Score | Evidence |
|---|---|---|
| **Winnability** | 4 | The starter most teams will submit (PEFT LoRA + FedAvg) demonstrably fails the brief's "no quiet domination" clause. With 8× data on one device, the data-rich domain gains {{dropout.fedavg_ab_homo.wiki.gain_mean|.3f}} nats/token while all four other domains regress below the untuned model. AnchorLoRA beats it by {{dropout.spike_vs_fedavg_ab_homo.macro_mean|.3f}} macro (95% CI {{dropout.spike_vs_fedavg_ab_homo.macro_lo|.3f}} to {{dropout.spike_vs_fedavg_ab_homo.macro_hi|.3f}}) and FFA-LoRA by {{dropout.spike_vs_ffa_lora.macro_mean|.3f}} ({{dropout.spike_vs_ffa_lora.macro_lo|.3f}} to {{dropout.spike_vs_ffa_lora.macro_hi|.3f}}). The evidence is deterministic, provenance-tracked and cross-model reviewed. |
| **Innovation headroom** | 3 | The contribution is a *combination* (seed-frozen shared A + prefix-nested device ranks → exact mixed-rank aggregation) plus participation corrections and an influence audit. CF-LoRA (Sep 2026) and PreLort (Jun 2026) each cover one half (`research/novelty.md`). Headroom for the finals: true rank-r_k on-device adapters, a real Flower kill-a-node, leave-one-out influence. |
| **Feasibility** | 5 | Runs end to end today on a shared M5: 5 heterogeneous devices, seeded dropouts, 4 aggregators + ablations, 19 tests, committed data, one-command reproduction. Nothing is gated on hardware or the user; Azure covers scale-up. The 19–25 Nov exams are left free. |
| **Demo strength** | 4 | Live per-device "who got better" bars plus each device's share of the update. The data-rich device's bounded norm share falls from {{dropout.fedavg_ab_homo.c0_norm_mean|.2f}} (starter) to {{dropout.anchor_full.c0_norm_mean|.2f}} (fair share 0.2). Kill a Flower node mid-round. Less visual than trading or agent demos. |
| **Fit with the user** | 5 | Distributed systems + LLM fine-tuning + Azure: core Microsoft-style systems work. |

- **Biggest risks:**
  - Judges read it as incremental (published ingredients).
  - Better-tuned baselines may close the gap; an effective-scale sensitivity run is queued.
  - AnchorLoRA's micro (sample-weighted) loss is {{dropout.spike_vs_fedavg_ab_homo.micro_mean|.3f}} worse than the starter's: the data-rich domain gains less. This is the price of the macro objective and must be argued, not hidden.
  - The pilot is a 135M model, 12 rounds, with 2–3-document test sets per domain.
- **One-line pitch:** "Federated LoRA in which a Raspberry Pi's data counts. Exact mixed-rank aggregation from a seed-shared frozen A, plus dropout-tolerant, per-device weighting. In our tests it improved {{dropout.anchor_full.domains_ci_pos_bonf|d}} of 5 devices' domains significantly, while the standard recipe improved only the data-rich one."
- **Overall:** 4.2 / 5, the unweighted mean of the five scores (4 + 3 + 5 + 4 + 5 = 21).
- **Versus the other finalists** (facts as the Supervisor relayed them; the ranking is the Supervisor's call): our spike *replicated* under paired seeds, with bit-identical reruns, and has been compared against two published aggregators. P7's detector spike failed its pre-registered replication. P9 reports 36–43% catch rate on real τ-bench errors.
