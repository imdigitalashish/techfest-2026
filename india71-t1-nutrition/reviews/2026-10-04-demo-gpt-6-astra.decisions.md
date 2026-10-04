# Decisions on the demo review by gpt-6-astra (max), 4 Oct 2026

- Raw review: [`2026-10-04-demo-gpt-6-astra.md`](2026-10-04-demo-gpt-6-astra.md), with screenshots in `2026-10-04-demo-shots/`. It reviews demo snapshot `74e8dce`.
- Run as a child session (PLAYBOOK §10/§11).
- Decided by the lead (Claude Opus 5.5).
- Fix owners: **L** = lead (pushed in `915afb2`); **B** = demo builder session (in progress).

| # | Issue (severity) | Decision | Disposition |
|---|---|---|---|
| B1 | "Names never leave each department" is asserted, not demonstrated: `link.py` reads both raw tables and blocks on plaintext (blocking) | **ACCEPTED, with the stronger fix** | **B:** new `identity_linkage/pprl.py`. `encode_department` runs on each side and emits CLK bits plus keyed-HMAC blocking keys only. `match_encoded` sees no plaintext, and a test asserts the input columns. F1 must equal the committed cell. Copy narrowed until then. |
| B2 | Six of seven screens overflow 1280×720; source text 11 px; tile contrast below 4.5:1 (blocking) | **ACCEPTED** | **B:** a 1280×720 presentation layout. Primary comparison, verdict and caveat stay above the fold; details sit behind a toggle; source text ≥13 px; contrast ≥4.5:1. Also fixes the lead-observed overlaps (screen 1 labels, screen 7 ledger header) and N3. |
| M1 | Under-6-month infants still compete for the capped slots, contradicting the proposal (major) | **ACCEPTED** | **L:** frozen `eval_v2.py` with an infant gate. The rule scores 0.473 vs programme rule 0.413 vs ML 0.430; 14.8% of episodes go to the infant pathway. Promoted to the headline (proposal, ADR 003 addendum, check_docs 20/20). v1 kept as history. **B:** screens 4–5 and district cohorts re-run on v2. |
| M2 | Undelivered overflow tasks become the worker's overdue tasks; no readiness/worker-clock separation (major) | **ACCEPTED** | **L:** Task contract v0.3.0 (`blocked` status, `child_clock_started_on`, `worker_clock_started_on`, `blocked_reason`). `router.mark_undelivered` gives off-list tasks blocked/capacity status with no worker clock and raises one capacity exception per AWC to the LS; `escalate` skips blocked tasks; tested. **B:** screen 6 shows "retained, not delivered → capacity exception". Resource gating (scale/rations) stays design-only and is labelled so. |
| M3 | Featured episode follows earlier SAM but is narrated as first-ever wasting (major) | **ACCEPTED** | **B:** feature a first-ever-onset child with the selection rule stated, or relabel "next qualifying episode" and acknowledge the earlier SAM. |
| M4 | F1 headline hides false links: 366 vs 34 at maximum stress (major) | **ACCEPTED** | **B:** show correct and false accepted links side by side, say the trade-off aloud, add a precision-matched Bloom comparison computed by committed code, and label the bit-string pair as a fixed illustration. |
| M5 | Scripted K8 reveal quotes K5/K3 numbers; SMS screen ignores the chosen AWC/K (major) | **ACCEPTED** | **B:** SCRIPT reveals at K=5. Screen 6 either follows the chosen AWC-month/K or shows a "featured pipeline, K=5" banner. |
| M6 | Request picker replays recorded decisions but implies live appends (major) | **ACCEPTED (label, not re-implement)** | **B:** label it "recorded policy decisions (gate.py at export); live hash verification; simulated external checkpoint", and state the replace-both-ledger-and-checkpoint limit. A JS re-implementation of the gate would not be the committed component, so labelling is the honest fix. |
| N1 | Coverage knob is a conditional probability, not the all-records share; "+40%" is a generator parameter | **ACCEPTED** | **B:** precise labels; show the realised all-records share. |
| N2 | "Both degrade" is false at 100% IDs | **ACCEPTED** | **B:** derive the sentence from the selected cell. |
| N3 | Amravati timeline label collisions | **ACCEPTED** | **B:** part of B2. |
| N4 | % vs pp; "hashes checked" mislabelled; ≤80 vs ≤160 chars | **ACCEPTED** | **B:** use pp, "entries checked", and "these exported messages ≤80 characters". |
| §11-7 | Review must be recorded in `ledger.tsv` | **ACCEPTED** | **L:** done (this file + ledger line). |

**Rejected:** none.

**Verdict to re-check after the builder's fix round:** §11 items 4 (honesty) and 5 (script) were "No" in this snapshot. The lead re-verifies from a clean clone before sending DEMO DONE.

## Re-check (gpt-6-astra, max; acc3292, snapshot 306509d): decisions
Raw: [`2026-10-04-demo-gpt-6-astra.recheck.md`](2026-10-04-demo-gpt-6-astra.recheck.md). Result: 10 FIXED, 2 PARTLY (M4, M5), plus 4 residual issues. §11: yes on 1, 2, 3, 6, 7; no on 4 and 5.

| # | Issue | Decision | Disposition |
|---|---|---|---|
| R1 | "Cannot reach that precision" is false at 100% IDs: the threshold-1.0, ID-only operating point is missing from the search (major) | **ACCEPTED** | **B:** add the endpoint, handle the empty probabilistic set, test the perfect-ID case, re-export the affected cells |
| R2 | False-link bars vanish when true links equal gold pairs (major) | **ACCEPTED** | **B:** common count axis sized to max(correct + false); visible-red check |
| R3 | "We operate at matched precision" overstates an in-sample, proposed policy; the child path uses 0.91 | **ACCEPTED** | **B:** SCRIPT and screen wording say "in-sample comparison; proposed operating policy"; the child-path threshold is aligned or disclosed |
| R4 | K10 promises "+3 more slots below" that aren't accessible (minor) | **ACCEPTED** | **B:** full roster in Details, or "not shown" |
| M5 (residual) | SCRIPT claims the K1 non-significance message without selecting K1 | **ACCEPTED** | **B:** add the K1 click and return to K5, or drop the claim |

**Lead verification of the final round** (builder 5d37434; fresh clone ff786b9, 2026-10-04 21:45 IST):
- Smoke PASS in 25 s, including the district re-derivation after the documented `eval/fetch_nfhs5.py` and the default linkage cell re-run through the encoded boundary, equal to `identity_linkage.json`.
- pytest passes; check_docs 22/22; `demo/run.sh` OK.
- R1/R2 verified by eye at 1280×720 (100% IDs, +40%): no "unreachable" text; "IDs only" endpoint shown; 48 false links visible as red on a single count axis.
- §11 items 4 and 5 now judged **yes** by the lead (R1–R4 and M5 resolved). No further reviewer pass requested.
