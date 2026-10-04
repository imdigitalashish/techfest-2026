# AI for Technology Readiness · TRL assessor — Thought Node

> Journal for `apctt-trl-assessor/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
_Updated 2026-10-04 09:35 IST._
- **Phase:** 4→5. Morning package delivered (08:03/08:22). Since then: submission dry run, genre-shift study, independent adversarial review → **[ADR 002](architecture/adr/002-reframe-spike.md): the spike is reframed** (Round 1 = transfer-robust ordinal model tournament on a shift-aware eval; the evidence audit becomes a Round-2 sidecar).
- **Numbers (all committed, [eval/README.md](eval/README.md)):** TechPort `trl_current` frozen split — sklearn TF-IDF cumulative logit QWK **0.343**, MAE **0.961** (best MAE), ridge QWK **0.350**, logreg exact **0.346**; majority QWK 0 / MAE 1.112. Shift: cross-source QWK 0.34 → **0.13**; abstract-length 0.31 → 0.19; same projects via their papers 0.41 → **0.21** (MAE +0.20, CI [0.07, 0.32]). These in-distribution numbers are optimistic (about 14% of texts state a TRL; see the leakage audit).
- **Submission dry run ([report](deliverables/dry_run_report.md)):** clean venv, pinned deps (numpy, pypdf; BSD), `--offline` tripwire; 106/106 outputs schema-valid against the *internal* contract; 70 MB RSS; 161 kB zip. Not yet: official adapter/validator, bundled wheels, OS-level offline test.
- **Doing:** lead. Sub-agents: none running (≤2 allowed).
- **Next:** (1) **eval suite v1** — snapshot hash, explicit-TRL and SBIR/phase redaction, content-dedup grouping, slices; briefing-chart PDF set (`/api/file/{fileId}`, verified), redacted; (2) **tournament round 1**: word+char TF-IDF, length-crop augmentation, a small open-weight encoder + ordinal head (licence-checked), scored on the shifted mean; (3) C5: out-of-fold QWK thresholds + calibration; (4) explicit-TRL statement detector (role-aware); (5) `components/ordinal/autoresearch/` ratchet on the shifted score; (6) bundled-wheel offline install + `sandbox-exec` deny-network dry run; (7) NTRS/OSTI proxy-labelled reports.
- **Needs from user:** (a) **register by 9 Oct** (team of 1–3, all ≤35 on 17 Dec 2026); (b) forward the 10 Oct guide, criteria checklist and samples into this Inbox; (c) after 10 Oct, post our Doubt-section questions (meaning of "hardcoded output schemas", approved data list, runtime environment, feedback latency for submissions #1/#2); (d) later: two annotators for ~2 h each to label ~100–300 patents/papers/reports.
- **Risks:** **genre shift (now measured — the main risk)**; TechPort label semantics and leakage; metric and schema unknown until 10 Oct; only 3 submissions; ambiguous rule 6; licences of any open-weight model we add.

## Key decisions
- 2026-10-04 — Primary public labelled set: **NASA TechPort** (public API, no key; `trlBegin/trlCurrent/trlEnd`). Models use **text only** — no program/SBIR metadata — because the hidden set is raw documents.
- 2026-10-04 — Spike = **evidence-first ordinal assessor** (C3 → C4 cumulative thresholds → C6 gap analysis, faithful by construction) + **metric-aware calibration/decoding** (C5). See [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — The official output schema is **loaded from the organisers' file at run time**, never inlined (conservative reading of rule 6); no outputs keyed to documents.
- 2026-10-04 — CPU-first, offline, open weights only, permissively licensed dependencies (Stage 2 must be Apache-2.0).
- 2026-10-04 — Labels: report `trl_current`, `trl_begin`, `trl_end`; primary = `trl_current` until the 10 Oct guide defines the target.
- 2026-10-04 — Submissions: #1 ~31 Oct (environment probe), #2 ~8 Nov (spike), #3 by 14 Nov (final, 24 h buffer before the 15 Nov freeze; clear of the 19–25 Nov exams).

- 2026-10-04 09:30 — **[ADR 002](architecture/adr/002-reframe-spike.md) amends ADR 001**: Round-1 spike = transfer-robust ordinal model (C4) chosen by a tournament on a leakage-clean, shift-aware eval suite (score = mean over shifted conditions); spike 2 = C5 metric-aware decoding/calibration; C3+C6 = Round-2 evidence-led audit sidecar (model-consistent reporting, no faithfulness claim); new explicit-TRL statement detector. Basis: independent review ([001-review.md](architecture/adr/001-review.md)) + genre-shift study.
- 2026-10-04 09:30 — Submissions: #1 = strongest compliant candidate, early; #2 = exactly one orthogonal hypothesis; #3 = the diagnostic winner with pass/fail fixes only.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Ingest & parse | file → ParsedDocument | pypdfium2/pdfplumber + heuristics | | contract | char-F1 vs gold text |
| C2 | Doc-type router | ParsedDocument → DocType | rules | | contract | macro-F1 |
| C3 | Evidence extractor (+ explicit-TRL detector) | ParsedDocument + rubric → EvidenceItem[] | lexicon/regex from EU+NASA wording | sidecar | skeleton v0.1 | span micro-F1 (signal × polarity) |
| C4 | Ordinal TRL model | text (+ evidence if it wins) → TRLDistribution | TF-IDF + cumulative logit (QWK 0.343) | ★ spike 1 (ADR 002) | baselines + skeleton v0 | shifted-mean QWK/MAE on eval suite v1 |
| C5 | Calibrate & decode | TRLDistribution → TRLDecision | temperature/isotonic; median/mode/thresholds | ★ | decodings in baseline | RPS, ECE; official metric |
| C6 | Rubric engine & gap analysis | decision + evidence + rubric → GapAnalysis | rubric table | sidecar | skeleton v0.1 (evidence-led) | criterion κ; citation precision |
| C7 | Assemble & validate | all → Assessment / official JSON | jsonschema | | contract | % schema-valid (fuzz) |
| C8 | Runner & packaging | dir → dir | CLI + isolation + timeouts | | dry run passes (internal contract) | docs/s, peak RSS, licence audit |
| C9 | Eval harness | preds + gold → metrics | `eval/baseline_*.py` | | v0 | — |
| C10 | Data & weak labels | sources → jsonl | TechPort fetch/build | | v0 (11,427 fetched) | label-noise rate |
| C11 | Audit UI (Round 2) | Assessment → report | static HTML | | planned | time-to-verify |

## Selection memo
_v1, 2026-10-04 07:50 IST (first version for portfolio prioritisation; final by 12 Oct). Scores 1–5._
- **Winnability: 4** — objective ordinal scoring; in what we could open, no prior document-level TRL predictor or public benchmark (research/landscape.md §2, §5); we already have an 8,587-record public labelled set and a running harness. Field: Indian teams plus the Philippines and South Korea.
- **Innovation headroom: 4** — the evidence-first ordinal assessor makes the gap analysis the model's own threshold decisions (faithful by construction) rather than post-hoc text, plus metric-aware decoding; both are measurable on a frozen eval (ADR 001).
- **Feasibility by the deadline: 5** — CPU-scale models; the skeleton and data pipeline were built in one night despite the outage; the freeze (15 Nov) precedes the 19–25 Nov exams; Azure is optional (teacher labelling only).
- **Demo strength: 4** — live documents → level + calibrated confidence + quoted evidence per criterion + next-level gaps; judges can check every claim.
- **Fit with the user's strengths: 4** — large-scale data pipelines, evaluation rigour, frontier/open-weight models as challengers and teachers.
- **Biggest risk:** genre shift, **now measured** — the same model loses about half its QWK going from project descriptions to the projects' own papers (0.41 → 0.21) and 60–75% across writing sources. Plus: metric and schema unknown until 10 Oct; only 3 submissions.
- **One-line pitch:** An offline, open-weight assessor that reads a patent, paper or R&D report, predicts its TRL (1–9) with calibrated confidence, and shows — with quoted evidence — which readiness criteria are met and what is missing for the next level.

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05 IST — Phase 0 started (lead)
Read PLAYBOOK, brief and official statement. Probed NASA TechPort: the public API works without a key (`/api/projects?updatedSince=…` lists 21,046 projects; `/api/projects/{id}` has trlBegin/trlCurrent/trlEnd + description/benefits). Wrote a resumable, polite fetcher (shuffled with a fixed seed, so any partial crawl is a random sample) and started it (~0.6 req/s from the API).

### 2026-10-04 02:30–07:10 IST — Session lost to model 408s
The overnight network saturation killed the session; the fetcher kept running and pulled 11,427 records. Nothing had been committed. The Supervisor switched all leads to lean mode (no sub-agents, small requests).

### 2026-10-04 07:10–07:50 IST — Morning package in lean mode
- Stopped the fetcher at 11,427 records (54% random sample) to free the network; committed the fetcher and dataset builder: 8,587 usable rows (description ≥200 chars + TRL). Label counts (trl_current): 1:157 2:716 3:2136 4:2301 5:1148 6:1068 7:334 8:107 9:42.
- `research/landscape.md` v0: opened and cited NASA SCaN TRL page, EU H2020 Annex G (definitions verified verbatim), ISO 16290 catalogue page, arXiv 2101.03989 (MLTRL), PESARO 2026 Thales paper, CORAL/CORN arXiv pages, the TechPort API and vendor pages (Patsnap, Mergeflow, ITONICS, Cypris). Marked UNVERIFIED: DoD/GAO/DOE guide contents (404/403), the bibliometric TRL papers, and vendors' TRL features (no static-HTML mention).
- `architecture/components.md` (C1–C11, contracts, isolated metrics, mermaid) + `architecture/contracts/contracts.schema.json` (11 `$defs`, parses).
- `architecture/adr/001-spike.md`: spike = evidence-first ordinal assessor + metric-aware decoding (six hats, thesis/antithesis/synthesis, first principles; independent adversarial review still pending).
- `deliverables/approach.md` v0: pipeline, public-data plan, eval plan, 3-submission plan, 10-Oct checklist, compliance, risks.
- Baselines: the machine is overloaded (load ≈65–80, swap ≈49.5/50 GB). The sklearn run spent >10 min importing scipy, so I wrote a numpy-only fallback (`eval/baseline_numpy.py`, same frozen split and metrics) and am running both.
- 07:53 — **Baseline v0 numbers committed** (`eval/baseline_numpy.py`, frozen grouped split, `trl_current`, train 6,352 / test 1,657): majority exact 0.291 · within-1 0.701 · MAE 1.112 · QWK 0.000; ridge exact 0.297 · within-1 0.745 · MAE 1.053 · QWK 0.314; threshold-ridge→median exact 0.312 · MAE 1.042 · QWK 0.302; →expectation within-1 0.754 · MAE 1.034. Learned: (1) text-only proposal descriptions carry a real but weak ordinal signal; (2) within-1 is uninformative on this label distribution (majority already 0.70), so QWK and MAE drive the ratchet; (3) decodings trade metrics against each other, which confirms C5 (metric-aware decoding) as a spike. Timings are pessimistic (machine overloaded).
- 08:00 — `trl_begin` / `trl_end` baselines committed (same pattern; QWK 0.263 / 0.319 for ridge). Per-component research notes v0 pushed (`research/components/README.md`). Morning package items 1–7 pushed except the end-to-end walking skeleton (next); item 8 (auto-research loop) not started.
- 08:22 — **Walking skeleton pushed** (`components/skeleton/`, C1–C8, numpy + stdlib; rubric `architecture/contracts/rubric_eu_nasa_v0.json`; 6/6 contract tests pass). End-to-end at 26 docs/s on CPU. On 3 held-out docs: gold 3→3, 5→5, 6→3. The rubric lexicon finds only 0–1 evidence sentences per TechPort description, so C3 recall is the first ratchet target. The sklearn run had hung for 49 min (killed); restarting under `nice`.
- 08:25 — Supervisor (08:22): package accepted; lean mode lifts at 08:30 with ≤2 concurrent sub-agents and `nice -n 10` for heavy jobs. Next asks: a **genre-shift robustness study** (NASA-style text vs patents/papers) and a **submission-package dry run** (schema-exact, offline, timed, clean deps). Both are now at the top of *Next*.
- 08:43 — **Submission dry run** (`submission/dry_run.sh`): build → clean uv venv with pinned numpy/pypdf → `--offline` batch of 106 files (100 held-out TechPort + 6 synthetic edge cases incl. a real and a corrupt PDF) → 106/106 schema-valid (internal contract), 70 MB peak RSS, 1.33 s CPU (wall 29 s on the loaded machine), 161 kB zip. Report: `deliverables/dry_run_report.md`.
- 09:07 — **Genre-shift study v0** (`eval/genre_shift.py`): cross-source shift collapses QWK (SBIR→internal 0.126 vs 0.345 in-source; internal→SBIR 0.092 vs 0.195); abstract-length input 0.314 → 0.192; paired papers (204 OpenAlex abstracts for 98 projects): QWK 0.414 → 0.212, MAE +0.196 [0.069, 0.319]. The sklearn TF-IDF baselines finished: cumulative logit QWK 0.343 / MAE 0.961; ridge QWK 0.350; logreg exact 0.346.
- 09:00 — **Independent adversarial review** (rubber-duck) of ADR 001, code and docs: 5 critical/high issues (wrong objective for Round 1; TechPort leakage — 14% explicit TRL mentions and cross-split duplicates; official-schema path; "faithful by construction" overclaimed and gap.py contradictions; non-standard macro precision and unimplemented `thresholds`). Disposition in `architecture/adr/001-review.md`. Fixed in code: evidence-led gap statuses, a fail-closed validator, decode errors on unknown rules, quote offsets, prior fallback, per-doc isolation and timeout, DOCX, page numbers; 11 tests pass.
- 09:10 — **Genre-shift sources** (research agent, `research/components/genre_shift_sources.md`): TechPort PDFs download from `/api/file/{fileId}` (I verified it: 134,826-byte PDF for fileId 367952), giving 3,066 TRL-labelled projects with briefing charts. The charts print "Estimated TRL at beginning and end of contract", so they **must be redacted**. NTRS and OSTI have keyless APIs and state TRL in prose (proxy labels). Verified negatives: NASA T2 patents carry no TRL field; UKRI none; HF none. The agent found no published document-level TRL predictor.
- 09:30 — **ADR 002** (spike reframed) + docs de-overclaimed + 3-submission plan revised; pushed.

