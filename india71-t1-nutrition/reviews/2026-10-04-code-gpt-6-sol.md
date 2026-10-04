# Review: code and reproducibility · GPT-6 Sol (reasoning: max) · 4 Oct 2026

- **Artifact:** `india71-t1-nutrition` code at commit `5c1f3a0`+ (growth_standards, credibility_engine, early_warning, cohort_simulator, policy_gate, audit_ledger, eval/run_pipeline).
- **How run:** `task` sub-agent (`code-review`, model `gpt-6-sol`, reasoning `max`), launched 10:10 IST before the Supervisor's 10:15 "sessions not sub-agents" directive, so it was allowed to finish.
- **Raw review:** reproduced verbatim at the end of this file.
- **Decisions by the lead (Claude Opus 5.5):**

| # | Issue (severity) | Decision | What changed / why |
|---|---|---|---|
| 1 | Demo routes SAM/MAM on WHZ only; misses MUAC- and oedema-defined SAM (High) | **ACCEPTED** | `eval/run_pipeline.py` now uses `who.classify(..., muac_cm, oedema, age_days)` |
| 2 | Early-warning features use future data (AWC credibility over full history) (High) | **ACCEPTED** | v1 path `features(unit_cred=False)` + `ANTHRO_V1`; unit test `test_no_lookahead.py` asserts that appending future records leaves earlier features unchanged |
| 3 | recall@K uses an oracle (truth-based exclusion) to free capacity (High) | **ACCEPTED** | New frozen evaluator `eval_v1.py`: observable candidate pool, observed-label training, unique-episode recall. v0 kept for history; its numbers are retracted ([ADR 003](../architecture/adr/003-transparent-ranking-first.md)) |
| 4 | Request-supplied geography bypasses AWC isolation; any scope level accepted (High) | **ACCEPTED** | `gate.py`: child-level data fails closed without trusted `subject_geo`; role→scope-level allow-list (`deny-scope-level-mismatch`). Red-team cases added |
| 5 | String `"false"` satisfies a boolean requirement (High) | **ACCEPTED** | Strict identity check (`actual is expected`); red-team case added |
| 6 | Fabricated consent / approval IDs grant access (High) | **ACCEPTED** | Grants are valid only if a trusted registry vouches for child, purpose and validity date (`_valid_grant`); 5 red-team cases added. Policy suite now **39/39, 0 false allows** |
| 7 | Deleting the ledger tail still verifies (High) | **ACCEPTED** | `Ledger.checkpoint()` (count, head hash) + `verify(checkpoint=...)`; truncation test added. The proposal now says the checkpoint is stored outside the ledger |
| 8 | Implausible or under-6-month MUAC triggers SAM (Medium) | **ACCEPTED** | `who.classify` applies MUAC cut-offs only at 6–59 months and when `flag_muacz` is false; record check `MUAC_IMPLAUSIBLE`; test added |
| 9 | "Gross-error recall" has no ground-truth denominator (Medium) | **ACCEPTED (partly deferred)** | The number is removed from the proposal. A v2 evaluator for spike A with injected-error labels is in the backlog; frozen v1 eval unchanged |
| 10 | Demo "incident" precision includes ongoing wasting (Medium) | **ACCEPTED** | Precision now requires truly not wasted at t; a separate field reports flags on already-wasted children measured as normal |
| 11 | One-entry JSONL can't be read back (Medium) | **ACCEPTED** | `from_jsonl` treats strings starting with `{` as text; round-trip test added |
| R1 | WHO tables can't be restored from a clean clone; fetch module missing | **ACCEPTED** | `components/growth_standards/fetch_who.py` with pinned commit/URLs and SHA-256 (all 17 files verify) |
| R2 | Environment not pinned | **ACCEPTED** | `requirements.txt` (exact versions from the venv) |
| R3 | Pipeline JSON embeds wall-clock runtime | **ACCEPTED** | Runtime now printed to stdout only; JSON is deterministic for a fixed seed |

**Rejected:** none. All findings were reproduced or plausible and cheap to fix.

---

## Raw review (verbatim)

## Issue: The demo misses MUAC- and oedema-defined SAM
**File:** `eval/run_pipeline.py:57` · **Severity:** High
**Problem:** Alerts use WHZ alone. A child with low MUAC but normal WHZ is marked normal; oedema makes WHZ null, which also falls through to normal.
**Evidence:** Two test measurements—one with MUAC 11 cm, the other with oedema—were both `sam` under `who.classify()` and both `normal` under the demo's expression.
**Suggested fix:** Route using the validated WHZ/MUAC/oedema classification, not WHZ alone.

## Issue: Early-warning scores use future measurements
**File:** `components/early_warning/model.py:24-37` · **Severity:** High
**Problem:** `engine.assess(meas)` calculates an AWC credibility score over the entire supplied history, then assigns it to earlier child-months. Both the frozen evaluator and pipeline supply measurements from after the date being scored. Separate simulator seeds do not prevent this within-seed look-ahead.
**Evidence:** In a small seeded cohort, withholding future months changed `awc_cred` for all 181 first-month events.
**Suggested fix:** Calculate each AWC feature as of the child's measurement date, using only records available by then; evaluate chronologically.

## Issue: Recall@K uses an oracle to free up capacity
**File:** `components/early_warning/eval.py:32-44` · **Severity:** High
**Problem:** The evaluator removes children who are *truly* wasted before ranking each AWC's top K. At deployment, true status is unavailable: an unrecognised wasted child can occupy a visit slot. The reported recall@5 therefore does not measure the operational candidate pool.
**Evidence:** A three-child, K=1 check gave recall 1.0 after the evaluator's truth-based exclusion, versus 0.0 when an unrecognised prevalent case remained in the ranked pool.
**Suggested fix:** Form and rank the candidate pool using observable status; use synthetic truth only to label and score outcomes.

## Issue: Request-supplied geography can bypass AWC isolation
**File:** `components/policy_gate/gate.py:35-55` · **Severity:** High
**Problem:** When trusted `subject_geo` is absent, the scope check falls back to `req.subject_scope_id`, without binding it to `subject_child_key`. It also accepts whatever scope level the request assigns to the actor.
**Evidence:** An AWW assigned AWC1 received `allow` for a child from AWC2 by claiming `subject_scope_id="AWC1"` with empty context; supplying the child's actual AWC2 geography returned `deny`. An AWW request claiming national scope `"IN"` was likewise allowed against the test child.
**Suggested fix:** Derive child geography and actor assignment from authoritative records; fail closed when required geography is missing and enforce role-appropriate scope levels.

## Issue: The string `"false"` satisfies an open-task requirement
**File:** `components/policy_gate/gate.py:59-73` · **Severity:** High
**Problem:** `bool(actual)` treats every nonempty string as true. An incorrectly typed `"false"` therefore satisfies `has_open_task: true` or `escalated: true` and reaches an allow rule.
**Evidence:** The same ASHA identified-child request returned `deny` with `has_open_task=False` and `allow` with `has_open_task="false"`.
**Suggested fix:** Require actual booleans for boolean predicates and reject incorrectly typed context.

## Issue: A made-up consent reference grants health-record access
**File:** `components/policy_gate/gate.py:62-69` · **Severity:** High
**Problem:** The consent rule checks only whether `consent_artefact_id` is nonempty. It does not establish that an artefact exists or covers this child, purpose and time. Research approval is likewise presence-only.
**Evidence:** `consent_artefact_id="nonexistent-consent"` returned `allow` for an AWW health-record request; `"nonexistent-approval"` returned `allow_transformed` for research.
**Suggested fix:** Resolve and validate authorization evidence against a trusted source before permitting access, including its subject, purpose and validity period.

## Issue: Deleting the audit trail's tail remains "verified"
**File:** `components/audit_ledger/ledger.py:46-55` · **Severity:** High
**Problem:** Verification checks links among entries still present, but has no trusted expected length or final hash. Removing the last entry silently produces another valid chain; the reported 100% mutation-detection result does not cover this case.
**Evidence:** A two-entry ledger verified as `(True, None)` both before and after `entries.pop()`.
**Suggested fix:** Verify against an independently stored, authenticated checkpoint containing at least the expected head hash and entry count.

## Issue: Implausible or underage MUAC values trigger SAM
**File:** `components/growth_standards/who.py:185-195` · **Severity:** Medium
**Problem:** Classification applies raw MUAC cutoffs without checking `flag_muacz` or whether the child is in the 6–59-month age group for those cutoffs. The record-quality check also omits `flag_muacz` (`components/credibility_engine/engine.py:70`), so it does not stop the value downstream.
**Evidence:** For a 365-day-old child with normal WHZ, MUAC 4 cm produced MUACZ −10.99 and `flag_muacz=True`, yet classified as `sam`. The same MUAC rule classified a 100-day-old infant as `sam`.
**Suggested fix:** Apply MUAC cutoffs only at eligible ages and to plausible measurements; route flagged values for remeasurement rather than treating them as diagnostic.

## Issue: "Gross-error recall" lacks a gross-error ground-truth denominator
**File:** `components/credibility_engine/eval.py:32-43` · **Severity:** Medium
**Problem:** The evaluator calls a record "gross" only when its weight exceeds four times that child's *observed median*, rather than using the simulator's injected-error truth. A tenfold error in a child's only measurement has ratio 1 and is omitted from recall, even if the checker misses it.
**Evidence:** The simulator injects tenfold weights at `components/cohort_simulator/simulate.py:193-194`, but does not pass that error label to this metric.
**Suggested fix:** Preserve an event-level label for corruption that survives the final observation process, and calculate rejection recall over those labelled events.

## Issue: Demo "incident" precision includes ongoing wasting
**File:** `eval/run_pipeline.py:125` · **Severity:** Medium
**Problem:** An observed-normal child can already be truly wasted because of measurement error or copying. This precision numerator counts that child if wasting persists in the future, although no *incident* wasting occurred. The demo applies `true_wlz >= -2` to its incident-recall calculation but not here.
**Evidence:** The precision expression checks only `flagged.fut_min < -2`; it has no current-truth eligibility check.
**Suggested fix:** Count a true positive only when the child was not wasted at the scoring date and becomes wasted within a complete future horizon.

## Issue: A one-entry ledger cannot be read back from its JSON text
**File:** `components/audit_ledger/ledger.py:64-69` · **Severity:** Medium
**Problem:** A one-line JSONL string has no newline, so `from_jsonl()` tries it as a filesystem path.
**Evidence:** `Ledger.from_jsonl(ledger.to_jsonl())` with one entry raised `OSError: [Errno 63] File name too long` on the project's macOS environment; the existing round-trip test uses 1,000 entries and does not exercise this case.
**Suggested fix:** Distinguish text from paths explicitly, or provide separate text/path constructors rather than probing arbitrary JSON as a path.

## Reproducibility gaps
- **WHO inputs cannot be restored from a clean clone:** raw LMS and expanded-SD tables are gitignored, and the fetch module named by `components/growth_standards/who.py:46` does not exist. The published-table test skips when those files are absent. Add a downloader with pinned source URLs and checksums.
- **The environment is not pinned:** this project has no tracked dependency manifest or lockfile; its ignored `.venv` points to a machine-specific Homebrew Python. Exact NumPy, pandas, scikit-learn, Pydantic, PyYAML and Excel-reader versions cannot be reconstructed.
- **Run commands are documented in module docstrings, but clean setup is not.** Even with the seeded simulator, `eval/run_pipeline.py:130` embeds wall-clock runtime in the saved result, so byte-for-byte JSON reproduction is not expected.
