# Hostile Q&A prep — P7 (for the finals; answers cite committed evidence)

Questions come from three reviews: the hostile-judge review (rubber-duck), gpt-6-astra and gpt-6-sol (`reviews/`). Every number below traces to a committed file. Answer briefly, concede what is true, then point to the evidence.

**1. "Isn't this just MPC beating heuristics, which Iglesias et al. showed in 2018?"**
Planning beating rules is our baseline result, not our claim. What is new is a pre-registered map of *which* look-ahead layer helps, including the failures. Planning helps in 7/8 (L, P) cells. A *better* forecast — even the true rates — lowered service in 3 of 4 long-lead-time cells under our abandonment-aware planner. And a detector we predicted would help did not replicate. (`eval/results/phase-v2/summary.md`, `phase-v2c/summary.md`)

**2. "Your detector failed. What is left?"**
1. The robust result: pre-registered, 6/6 scenarios, 30/30 fresh seeds, Holm p = 1.1e-8 (`eval/results/mvp-v2/confirm.md`).
2. The finding that forecast value belongs to the forecast–planner pair. The same detector gains +0.45 to +2.63 pp with a queue-chasing planner and loses with an abandonment-aware one, on the same seeds.
3. A spike motivated by that finding, with a falsification test written before running it (`eval/preregistration.md`, Addendum B).

**3. "How do you know the gain isn't just more driving?"**
Pareto run: at a move cost of 0.5 the planner serves +3.77 pp more than the reactive rule while moving *less* (−0.17 empty hops per served request), on 30/30 seeds (`eval/results/pareto-v2/summary.md`). The default planner also moves less than the reactive rule (0.51 vs 0.59 hops per served request).

**4. "Is it really multi-agent?"**
Each unit is a PettingZoo agent. The evaluated allocator is centralised cooperative planning with per-agent execution, and we say so. The greedy rule baseline is decentralised. Decentralised coordination from the LP's dual prices is planned, not claimed.

**5. "Did you pick the baseline after seeing the results?"**
No. The reference rule per scenario was fixed on tuning seeds 0–19 and committed (10:15 IST, 4 Oct) before the 30 fresh test seeds ran. The git history proves the order.

**6. "With n=10, Holm-adjusted p was 0.068 earlier."**
Correct; that was the exploratory mvp-v1. The confirmatory mvp-v2 uses 30 fresh seeds and Holm over 6 pre-registered tests: p = 1.1e-8.

**7. "Synthetic demand is a toy."**
We replayed NYC TLC yellow-taxi trips (July 2025, Manhattan, 20 thinning replicates): +2.52 pp [+2.39, +2.67], 20/20. In the observed July-4 21:30–23:30 surge the planner lost 1.4 requests vs 39.6 for the best rule. The cause of the surge is unverified. (`eval/results/nyc-v2/summary.md`)

**8. "Short episodes?"**
A week with a shock every day plus drift: +6.34 pp, 10/10 seeds; the greedy rule decays from 91% to 47% served. A 30-day month: +6.37 pp, 4/4 seeds. With n=4 we cite CIs and wins, not Wilcoxon. (`long-week-v2`, `long-month-v2`)

**9. "Your 'oracle' underperforms. Is it broken?"**
It is a true-rate *forecast* fed to the same certainty-equivalent LP, not an upper bound. Its underperformance is the finding: certainty-equivalent planning can turn better information into worse decisions (cf. Smart Predict-then-Optimize, Management Science 2022; decision-focused learning, AAAI 2019).

**10. "Why does the LP let demand vanish? Does it match the simulator?"**
The LP is a fluid relaxation. Unserved demand may abandon, at rate 1/P. Known gap: at τ=0 it does not force "a unit that stays serves the local queue". Re-planning every step bounds the effect, and it applies equally to every planner arm. It is listed as a limitation with a fix planned.

**11. "Are the results solver-dependent?"**
Tied LP optima can make episodes differ between solvers. Every row records the backend. An independent reproduction (gpt-6-sol) replayed 8 episodes and matched 31/31 metrics exactly with highspy 1.15.1, and regenerated all 7 analyses identically.

**12. "What does L mean physically?"**
Repositioning set-up delay per hop. In autoscaling it is cold-start time, with P the request timeout. In dispatch it is travel time, with P customer patience. Loaded trips are not slowed. This is stated wherever L appears.

**13. "Is the trust spike just a hand-tuned scalar?"**
Today, yes: an exploratory global trust of 0.5 beats both extremes by +1.1–1.2 pp under shock+drift. A tuning-seed preview showed that local regime gating adds ≈0 over the best fixed trust. Addendum B will therefore be amended before any test run, to city-wide regime gating plus uncertainty-calibrated shrinkage, tuned on seeds 0–49 and tested on 300–329.

**14. "How fast is it?"**
About 6 ms per decision step end to end (median, Apple M5 laptop, shared machine; mvp-v2). A 1440-episode pre-registered grid takes about 15 minutes.

**15. "What would make you change your mind?"**
1. Addendum B failing: no Holm-significant gain over the better extreme in at least 21 of 28 cells.
2. RL beating the planner on frozen seeds.
3. The NYC advantage vanishing on other months.
All three are scheduled tests.
