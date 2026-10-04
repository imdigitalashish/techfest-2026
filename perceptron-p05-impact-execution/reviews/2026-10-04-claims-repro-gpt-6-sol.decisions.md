# Lead decisions on the gpt-6-sol claims/E10 reproduction review (written 2026-10-04 13:57 IST)
Raw: [2026-10-04-claims-repro-gpt-6-sol.md](2026-10-04-claims-repro-gpt-6-sol.md) (e996762). E10 H2, the E6∪E10 pool, and 2 rerun seeds (10/10 rows) were reproduced.

| # | Sev. | Finding | Decision | Action |
|---|---|---|---|---|
| 1 | blocker | Doc gate failed (astra_final not wired); render could partially write | ACCEPTED | Ledger rows added (`astra_final` parsed from `reviews/ledger.tsv`). `render_docs.py` renders everything before writing anything. |
| 2 | major | Abstract paired different policies and seed sets | ACCEPTED | Same-arm E12 accounting (same as astra final #2). |
| 3 | major | Cached JSON could drift from the raw CSVs | ACCEPTED | Claims now recompute E8/E10 attribution and E11 statistics from the committed CSVs; E7's point estimate is cross-checked against its CSVs. Calibration and NSR JSONs come from gitignored per-seed paths, so they are regenerable by script but can't be checked against committed raw data (disclosed). |
| 4 | major | Three H2 bootstrap procedures | ACCEPTED | Claims and `h1_verdict.py` both use the registered procedure: 10k draws, RandomState(0), seed-sorted. Verdict files regenerated. |
| 5 | minor | Bare integer counts bypassed the gate | ACCEPTED | `check_docs.py` now flags count-like integers ("N seeds/runs/worlds/draws"). E8's hard-coded sample size is now a placeholder. |
| 6 | minor | "Books match" overstated | ACCEPTED | "Top-of-book event logs" (same as astra final #4). |
