# Judging criteria → evidence map (Round 1 and finals)

Every claim points to a committed artefact; the numbers themselves live in `eval/results/` and are quoted only through rendered documents (`deliverables/render.py`, checked by `eval/check_docs.py`).

| Criterion (weight) | What the reviewer checks | Our evidence |
|---|---|---|
| Problem understanding (20%) | The real crux, and a scope realistic for the MVP | The abstract's "Understanding" section: the before/after identity; when OPE identifies the counterfactual (propensities, overlap, no unlogged confounding); the hard parts (heavy-tailed weights under greedy policies, uncertainty for a difference, untestable confounding, feedback). Backed by `research/landscape.md` §1, §4, §5. |
| Technical soundness & feasibility (25%) | Valid method, suitable tools and data, buildable by 3 people | Working code behind typed contracts (`architecture/contracts/contracts.py`) and contract tests (`tests/`). Standard estimators returning influence terms (`components/estimators/ope.py`). The 2×2 Shapley decomposer (`components/decomposer/decompose.py`). The overlap gate (`components/report/gate.py`) and verdict (`components/report/verdict.py`). MSM bounds (`components/sensitivity/msm.py`). Each result reproduces with one command on a laptop CPU. |
| Innovation / novelty (20%) | Beyond the starter baseline (IPW/DR on OBD) | (1) Attribution of a policy switch: 2×2 Shapley with the interaction, where OPE fills the cells a difference-in-differences would need from a control arm. (2) An abstention gate calibrated on simulation and checked on real truth (`eval/results/gate_obd_posthoc.md`, post hoc). (3) A protocol finding: the deployed Thompson-sampling policy drifted, while the standard obp protocol evaluates a static prior (`eval/results/obd_slice_summary.md`, Analysis 1; verified obp source in `research/landscape.md` §9). Prior-art comparison in `research/landscape.md` §2, §5, §6. |
| Clarity (10%) | Precise, concrete, picturable | The abstract is rendered from results (no hand-typed numbers), the architecture diagram (`deliverables/architecture.md`), and the waterfall and drift-sweep figures (`deliverables/figures/`). |
| Impact & rigor of evaluation (15%) | Meaningful metrics and baselines; would the comparison prove the claim? | Real truth from concurrent OBD arms, with the analysis pre-registered before results (`eval/preregistration_obd.md`). Disclosed deviation and post-hoc labels. A frozen simulator bank with exact truth, drift sweep, feedback, misspecification and confounding tests (`eval/results/decomposer_review.md`, `sim_bank_summary.md`). Metrics: RMSE, sign accuracy, coverage, abstention rate, confident-wrong count. Baselines: naive, DM, IPW, obp estimators. Cross-model reviews in `reviews/`. |
| Team fit & readiness (10%) | Skill mix; week-by-week milestones | Milestones in the abstract (exam window kept free); `thought_node.md` *Now* and *Log* show the working cadence. Teammates are TBD (a *Needs from user* item). |

## Finals (working build)
- MVP 1 (standard OPE): `eval/run_obd_slice.py`, Analysis 2.
- MVP 2 (estimate vs naive before/after): `eval/run_obd_slice.py`, Analysis 3 (real), and `eval/run_sim_bank.py` S1/S2 (simulator).
- Stretch 1 (uncertainty): intervals, Shapley coverage, the overlap gate.
- Stretch 2 (confounding): MSM bounds and the tipping point Γ\* (`components/sensitivity/msm.py`; simulator S4).
