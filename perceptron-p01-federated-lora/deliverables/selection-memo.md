# Selection memo — Perceptron P1 (federated LoRA), final version for the 12 Oct pick

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
