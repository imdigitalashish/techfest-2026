# Lead decisions on the gpt-6-astra hostile review (written 2026-10-04 13:13 IST)

Raw review: [2026-10-04-abstract-h1-gpt-6-astra.md](2026-10-04-abstract-h1-gpt-6-astra.md), commit a6abc05. It scored the 31-Oct draft at 2.80/5 (56/100). Decisions apply to the final abstract and the repository.

| # | Sev. | Finding (short) | Decision | Action |
|---|---|---|---|---|
| 1 | blocker | The E6 arm is "QP + legacy front-loading, market orders", not a braking controller; E8 doesn't replicate | **ACCEPTED** | The arm is renamed everywhere. E6, E8 and E10 are reported together. No braking mechanism is claimed. |
| 2 | blocker | "Ghost book" unsupported (negative OOS R²); SELL sign wrong; a mid isn't a book | **ACCEPTED** | Renamed "counterfactual-mid estimator (prototype, not yet validated)". Sign fixed (SELL: ghost mid = observed mid + Î). E9 failures reported. No "certified" or "live" wording. |
| 3 | major | RNG sync is a coupling choice; preservation of market laws is unproven | **ACCEPTED** | Wording changed to "counterfactual conditional on the simulator and its random-number coupling" and "observed paired-dispersion reduction". A native-vs-synced null-world comparison is planned/run as E11 (see preregistration). |
| 4 | major | The "bit-identical" check tolerates ≈ 1¢ | **ACCEPTED** | Wording changed to "pre-trade mids equal at 1-s sampling (≈ 1¢ tolerance)". An exact event-level check is added for future runs. |
| 5 | major | IS terms are accounting components, not causal mechanisms; drift exposure depends on the policy | **ACCEPTED** | Renamed "decision-time accounting components". Fill-time/delay diagnostics added to the plan (and to TCA after E10). The ADR's "only the last two are controllable" claim is withdrawn. |
| 6 | major | Disclose the selection history; E6 is a narrow confirmation | **ACCEPTED** | E3/E5 are exploratory and E6 is the first frozen confirmation (registered after launch, before inspection; see the timestamp correction). E8 is non-replicating validation evidence; E10 is the strict replication. The pool is descriptive (amendment A1). |
| 7 | minor | The tail fraction isn't a p-value | **ACCEPTED** | Fixed in `eval/h1_verdict.py` and in the docs. |
| 8 | major | Economic importance and baseline strength | **ACCEPTED** | Effects are reported in ¢/share, ticks and $ per parent. No win vs VWAP is claimed. A matched front-loaded TWAP (TWAP_legacy_fb) is already an E8/E10 arm. AC/OW schedules stay "planned". |
| 9 | major | E7 positivity-conditioned bootstrap; no monotonicity check; CI overlap ≠ equivalence | **ACCEPTED** | Deliverables say "formally unresolved; point estimate near-linear". A monotonicity flag is added (labelled as an amendment). Future realism tests will use an equivalence criterion. |
| 10 | major | Attribution rule treats non-significance as absence | **ACCEPTED** | Amendment A1 (committed 13:13:18, before E10 results): signed effects, ±0.02 bps equivalence margin, interaction rule. |
| 11 | major | E9 split was lexicographic | **ACCEPTED** | Fixed; E9 recomputed on the registered split (same as gpt-6-sol #1). |
| 12 | major | Novelty overstated; prior work mischaracterised | **ACCEPTED** | Reframed as an ABIDES-specific engineering/evaluation contribution. CRN/stream synchronisation, MarS, ABIDES-MARL and Olby et al. are credited. "Prior work reports beats TWAP" is fixed (Karpe et al. report convergence toward TWAP). Absence-of-prior-work claims are marked UNVERIFIED. |
| 13 | major | Inventory differences aren't a feedback mechanism | **ACCEPTED** | Presented as "end-of-session inventory redistribution by agent type (descriptive)". Feedback mechanisms are hypotheses; timestamped response paths are planned. |
| 14 | major | "Keep only significant gains" isn't a valid adaptive-search guarantee | **ACCEPTED** | The ratchet is described as development-time search, with paired candidate-vs-incumbent comparison and untouched confirmation seeds. PPO is marked deferred. |
| 15 | minor | Scale wording (1,116 agents; 35-min session, not a day; throughput) | **ACCEPTED** | Fixed. Throughput comes from the committed wall times. Every claim is marked implemented / evaluated / unresolved / planned. |
| 16 | minor | Team placeholders | **ACCEPTED (blocked)** | Needs the user's teammates. Roles stay explicit placeholders, listed under *Needs from user*. |
