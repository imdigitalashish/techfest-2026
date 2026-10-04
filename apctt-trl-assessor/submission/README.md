# Submission package (Round 1) — build and dry run

Goal: submission attempt #1 can go out within hours of the 10 Oct guide, and every attempt is checked the same way first.

```
bash submission/dry_run.sh        # build -> clean venv (pinned deps) -> offline, timed batch -> report
```
- `build.py` assembles `.data/dist/trl_assessor_<v>/` (+ zip): `trl_assessor/` (pipeline code from `components/skeleton/`, no tests), `trl_assessor/resources/{model.npz, rubric.json, contracts.schema.json}`, `run.py`, `requirements.txt` (pinned from the build environment), `MANIFEST.json` (sha256 per file).
- `make_dryrun_inputs.py` writes 100 held-out TechPort docs (seeded sample of the frozen test split; gold kept outside the input folder) plus synthetic edge cases (empty, non-English, 1 MB text, HTML, corrupt PDF, real PDF via macOS `cupsfilter`).
- `run.py --in DIR --out DIR --offline` processes every file; `--offline` makes any socket connect/DNS lookup raise, so a completed run proves no network use.
- `report.py` writes [`../deliverables/dry_run_report.md`](../deliverables/dry_run_report.md): outputs written, schema validity, wall and CPU time, peak RSS, package size and sha256, sanity accuracy on the gold docs, installed packages with their declared licences.

## When the official guide lands (10 Oct)
1. Save the official output schema as `trl_assessor/resources/official_schema.json`; add a mapping `Assessment → official record` in `emit.py`; validate against the official schema (loaded from file, never inlined) as well as our contract.
2. Match the required entry point and I/O layout (CLI args, file naming, single JSON vs one per document, container or not) in `run.py`.
3. Match the runtime (Python version, CPU/GPU, RAM, time limit): pin in `requirements.txt`, re-run `dry_run.sh`, and compare the measured time and RSS to the limits.
4. Add the Apache-2.0 `LICENSE` and a `NOTICE` (third-party attributions) — required for the Stage 2 package anyway.
