# Lead decisions on the gpt-6-astra demo review (written 2026-10-04 22:44 IST)
Raw: [2026-10-04-demo-gpt-6-astra.md](2026-10-04-demo-gpt-6-astra.md) (c9c9c76e). Overall **3.5/5**. The reviewer reproduced the demo end to end: live seed 20261004 in 4.8 s, 731/731 identical pre-trade events, smoke passed, works offline, no console errors. All 13 items are accepted. The demo builder implements 1–13 in `demo/`. The lead fixed the same wording in the abstract, memo and ADR (items 3–5).

| # | Finding | Decision | Action |
|---|---|---|---|
| 1 | "We sell 4,000 shares" doesn't follow the size knob | ACCEPTED | Bind the quantity to the selection; the holdings panel is labelled as the fixed 4,000-share E10 aggregate. |
| 2 | Slope shown without "75% of draws usable" | ACCEPTED | Qualification placed beside the interval. |
| 3 | "every agent re-keyed" / "shifts every later draw" overgeneralise | ACCEPTED | "every background agent"; "can desynchronise state-dependent draws". Also fixed in the abstract. |
| 4 | "7.7× tighter paired CIs" is really a std ratio | ACCEPTED | "paired-difference std 7.7× smaller (median of four policies)". Also fixed in the abstract, memo and ADR. |
| 5 | Mixed horizons (std at 20 min vs mean at 5 min) | ACCEPTED | Horizons stated explicitly. Also fixed in the abstract. |
| 6 | "single-seed differences are noise" | ACCEPTED | "one seed cannot establish an average advantage". |
| 7 | "instant (spread and book-walking)" mislabel | ACCEPTED | "decision-to-fill cost (delay + at-fill concession)". |
| 8 | Act 3 tick labels ±0.43 on a ±0.47 axis (bug) | ACCEPTED | Fix the ticks. |
| 9 | The twin coupling is confounded with the no-order world; "does not replicate" | ACCEPTED | "the coupling makes the paired difference measurable; the ghost attributes it"; "E10 did not confirm superiority". The old fallback wording is purged. |
| 10 | Live seed input silently clamped | ACCEPTED | Show the range 0–2147483647; reject invalid input. |
| 11 | The requested agent arrives too late | ACCEPTED (modified) | A ≤20 s cold open, "The answer first" (TWAP vs agent, E10 not confirmed); the ghost stays the star, as the Supervisor directed. |
| 12 | The size knob's headline quantity doesn't track the knob | ACCEPTED | Freeze the size challenge at 09:55; show the 30-seed aggregate T1 impact with its CI beside the knob. |
| 13 | Five acts are too many for 3 minutes | ACCEPTED | Three beats, with ≥20 s reserved for the judge's live seed. |
