# AI for Technology Readiness · TRL assessor — Thought Node

> Journal for `apctt-trl-assessor/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
_Updated 2026-10-04 08:05 IST._
- **Phase:** 4 — eval harness with real baseline numbers (done); walking skeleton next. Morning package pushed: [landscape](research/landscape.md) · [per-component notes](research/components/README.md) · [components + contracts](architecture/components.md) · [ADR 001](architecture/adr/001-spike.md) · [approach](deliverables/approach.md) · [eval + numbers](eval/README.md) · selection memo below.
- **Plan:** evidence-first ordinal TRL assessor, CPU-only and offline, with the official schema loaded from file. Public benchmark = NASA TechPort (text only). Ratchet the spikes (C3 evidence → C4 thresholds; C5 metric-aware decoding) on the frozen split. Adapt within 6 h of the 10 Oct guide.
- **Status of the numbers:** TechPort `trl_current`, test n=1,657 — majority QWK 0.000 / MAE 1.112 → hashed TF-IDF ridge QWK **0.314** / MAE 1.053; threshold-ridge→expectation MAE **1.034**, within-1 0.754. The same pattern holds for `trl_begin` and `trl_end` (eval/README.md). These are deliberately weak v0 baselines.
- **Doing:** lead alone (lean mode until 08:30). The sklearn TF-IDF + logistic/cumulative-logit run is still stuck importing scipy on the overloaded machine.
- **Next:** (1) walking skeleton `components/pipeline/` — file → ParsedDocument → evidence (rubric lexicon) → threshold model → decision → gap analysis → `Assessment` validated against `contracts.schema.json`, with contract tests; (2) `components/ordinal/autoresearch/` (program.md, frozen eval.py, results.tsv) and the first ratchet: sklearn TF-IDF + cumulative logit, then evidence features, then QWK-tuned thresholds; (3) once ≤3 sub-agents are allowed after 08:30: an independent rubber-duck review of ADR 001 and a fact-check of the landscape citations; (4) finish the TechPort crawl (resumable); (5) open the DoD/GAO/DOE TRA guides and ISO 16290; CORDIS/SBIR weak labels; patent/paper genre-shift set.
- **Needs from user:** (a) **register by 9 Oct** (team of 1–3, all ≤35 on 17 Dec 2026); (b) forward the 10 Oct training guide, criteria checklist and samples into this Inbox; (c) after 10 Oct, post our Doubt-section questions (meaning of "hardcoded output schemas", approved data list, runtime environment) — see `deliverables/approach.md` §6.10; (d) later: two annotators for about 2 h each to label ~100 patents/papers for the genre-shift test.
- **Risks:** genre/label mismatch (TechPort proposal-style text vs hidden patents/papers/reports); metric and schema unknown until 10 Oct; only 3 submissions; ambiguous rule 6; landscape citations not yet independently fact-checked; v0 baselines are weak (QWK ≈0.3), so most of the gain must come from the ratchet.

## Key decisions
- 2026-10-04 — Primary public labelled set: **NASA TechPort** (public API, no key; `trlBegin/trlCurrent/trlEnd`). Models use **text only** — no program/SBIR metadata — because the hidden set is raw documents.
- 2026-10-04 — Spike = **evidence-first ordinal assessor** (C3 → C4 cumulative thresholds → C6 gap analysis, faithful by construction) + **metric-aware calibration/decoding** (C5). See [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — The official output schema is **loaded from the organisers' file at run time**, never inlined (conservative reading of rule 6); no outputs keyed to documents.
- 2026-10-04 — CPU-first, offline, open weights only, permissively licensed dependencies (Stage 2 must be Apache-2.0).
- 2026-10-04 — Labels: report `trl_current`, `trl_begin`, `trl_end`; primary = `trl_current` until the 10 Oct guide defines the target.
- 2026-10-04 — Submissions: #1 ~31 Oct (environment probe), #2 ~8 Nov (spike), #3 by 14 Nov (final, 24 h buffer before the 15 Nov freeze; clear of the 19–25 Nov exams).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Ingest & parse | file → ParsedDocument | pypdfium2/pdfplumber + heuristics | | contract | char-F1 vs gold text |
| C2 | Doc-type router | ParsedDocument → DocType | rules | | contract | macro-F1 |
| C3 | Evidence extractor | ParsedDocument + rubric → EvidenceItem[] | lexicon/regex from EU+NASA wording | ★ | contract | span micro-F1 (signal × polarity) |
| C4 | Ordinal TRL model | text + evidence → TRLDistribution | TF-IDF + cumulative logit | (seam for ★) | baseline running | QWK (MAE, exact, within-1) |
| C5 | Calibrate & decode | TRLDistribution → TRLDecision | temperature/isotonic; median/mode/thresholds | ★ | decodings in baseline | RPS, ECE; official metric |
| C6 | Rubric engine & gap analysis | decision + evidence + rubric → GapAnalysis | rubric table | ★ | contract | criterion κ; citation precision |
| C7 | Assemble & validate | all → Assessment / official JSON | jsonschema | | contract | % schema-valid (fuzz) |
| C8 | Runner & packaging | dir → dir | CLI + pool + timeouts | | planned | docs/s, peak RSS, licence audit |
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
- **Biggest risk:** genre/label mismatch between public training text (NASA project descriptions) and the hidden APCTT set; metric and schema unknown until 10 Oct; only 3 submissions.
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

