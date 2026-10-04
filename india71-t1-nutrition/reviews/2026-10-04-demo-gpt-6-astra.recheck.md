# Demo jury recheck: gpt-6-astra

**Recorded:** 2026-10-04 21:10 IST. **Snapshot:** `306509d39b472abe1bc6420d08b857f75d1c97d9`, including `915afb2`, `d0dd7e4`, `4377d35`, `ad9f42b`. Single-context follow-up to the original review and the lead's decisions. Paths below are relative to `india71-t1-nutrition/`.

**Verdict: 10 FIXED, 2 PARTLY.** The privacy interface and projector presentation are substantially improved. The matched-precision comparison honestly shows a privacy/recovery trade-off, not a win over pooled matching. However, its new precision-search claim and false-link bar encoding have demonstrable errors; the script also retains an inactive-K cue. I would not yet mark the honesty/script bars complete.

## Execution and standards

- `demo/smoke.sh`: **PASS, 24.28 s**, CPU-only under `nice -n 10`, memory level **40**. Actual offline `file://` first visual **0.18 s**, no page errors/network. District-source re-derivation was explicitly **skipped** because raw NFHS files are absent. No full exporter run.
- Targeted `test_pprl.py`, `test_eval_v2.py`, `test_router.py`: **17 passed**, 44.01 s, memory **42**.
- Re-watched all seven screens through the unchanged loopback mirror at **1280x720 and 1440x900**, including both cohorts: 22 screen/cohort/viewport states, all 35 linkage cells, K bounds/reveal, changed AWC/K notice, phone scrolling, six requests and all five ledger variants per cohort.
- No primary verdict/caveat below the viewport; source text **13.0 / 13.9px**. Smoke's worst tile contrast is **4.62:1**. Static shell detector: `[]`, not an assurance about all dynamically rendered content.
- Six PNGs: **1,388,003 bytes**, all decode, below 2 MB. The mirror and reviewer tab were closed. No implementation changes.

## Spec: original twelve items

| Item | Verdict | Evidence |
|---|---|---|
| **B1** | **FIXED** | `pprl.py:75-110` separates department encoding from a strict encoded-column matcher and rejects raw/extra columns; an additional fresh-process probe reproduced **179 decisions** from encoded JSON without supplying raw records or the fresh encoding secret. This proves the coded interface, not deployed departmental isolation or anonymisation. |
| **B2** | **FIXED** | Both requested viewport sizes fit; sources/caveats remain visible, all 35 linkage verdicts fit at 720px, and tile contrast passes. See [linkage](2026-10-04-demo-shots-recheck/01-matched-precision-1280.png) and [worklist](2026-10-04-demo-shots-recheck/03-monthly-worklist-1280.png). |
| **M1** | **FIXED** | `eval_v2.py:55-57` gates ranking at **183 days**; smoke checks every exported ranked list, minimum shown age 6.1 months. Infant-pathway routing itself remains explicitly unimplemented in the SMS Details/README; this is an eligibility fix, not delivered infant care. |
| **M2** | **FIXED** | `router.py:124-156` blocks undelivered tasks, clears their worker clock and creates the LS capacity exception; Nandurbar's **11** blocked tasks remain blocked on day 8. [Evidence](2026-10-04-demo-shots-recheck/04-capacity-gate-1280.png). This fixes capacity overflow, not every possible resource-readiness condition. |
| **M3** | **FIXED** | `demo/export.py:518-533` checks prior true wasting and recorded MAM/SAM, not just the first qualifying episode. PT-000872's prior true WLZ minimum is **-1.5022**, PT-002229's **-1.3930**; neither has prior recorded MAM/SAM. Both were born in January 2025. [Nandurbar](2026-10-04-demo-shots-recheck/02-first-onset-1280.png), [Amravati](2026-10-04-demo-shots-recheck/05-amravati-first-onset-1440.png). |
| **M4** | **PARTLY** | At zero IDs/+40% errors, **2,250 correct/31 false** encoded versus **2,456/34** pooled, both rounding to 98.6% precision, is honest: encoded recovers **206 fewer** true links. The fixed illustration is labelled. But the new endpoint and visual-encoding defects below undermine the comparison at other settings. |
| **M5** | **PARTLY** | K5 reveal now correctly shows the same five children, and changing K/AWC produces an explicit fixed-K5 SMS notice. But `SCRIPT.md:14` ends back at **K5** while saying the screen states K1's non-significance; that message only appears after selecting **K1**. Add that click, then return to K5, or remove “the screen says so.” |
| **M6** | **FIXED** | Screen 7 visibly distinguishes recorded decisions, live hashing and simulated checkpoint custody, including the replace-both limit. Request clicks leave the recorded ledger unchanged as disclosed; all attack variants behaved correctly in both cohorts (`demo/js/break.js`). |
| **N1** | **FIXED** | Main labels now distinguish nominal conditional coverage from realised all-records coverage: **32.8%** at nominal 35%, **94.9%** at nominal 100%; error probability is a generator parameter. [Evidence](2026-10-04-demo-shots-recheck/06-unreachable-claim-1280.png). |
| **N2** | **FIXED** | `demo/js/find.js:41-49` derives the change text from the selected data instead of asserting that both methods degrade. The 100%-ID/+40% case no longer makes the old false degradation claim. |
| **N3** | **FIXED** | Repeated “slot” labels are replaced by ranks inside markers; event labels are placed without the previous collision. Both Amravati sizes inspected. [1440 evidence](2026-10-04-demo-shots-recheck/05-amravati-first-onset-1440.png). |
| **N4** | **FIXED** | CIs say **percentage points**; hashing counts actual verification calls (**60** intact versus **27** after truncation for Nandurbar); SMS caveat distinguishes exported <=80-character examples from the renderer's **160** limit. |

The first-onset claim is now honest **within the monthly simulator**: the selection rule is visible in Details, excludes earlier true/recorded wasting and explicitly selects a successfully listed example. It is not an average outcome or evidence of real-world prevention. The v2 recall denominator is also different: Nandurbar counts **11,921 rankable episodes out of 13,797**, with the window-start age rule explained in Details.

## New/residual issues

### R1 - Major: “cannot reach that precision” is false

`demo/export.py:316-340` searches observed probabilistic scores but omits the operating point that rejects every probabilistic pair while retaining deterministic ID matches. All five 100%-ID cells are exported as “target not reachable.”

**Direct counterexample:** regenerate only the **100%-ID/no-extra-error** benchmark, encode it, match at 0.86, then apply `accept_at(decisions, 1.0)`. This returns **4,531 correct, 0 false, precision/recall/F1 = 1.0**. The highest non-ID score is only **0.9600523903**. The current page instead says the best possible result has one false link: [screenshot](2026-10-04-demo-shots-recheck/06-unreachable-claim-1280.png).

**Fix:** include the upper-end/ID-only operating point, handle an empty probabilistic set, test the perfect-ID case, and regenerate the affected payload. Preserve sufficient threshold precision: even the stored rounded threshold **0.9601** already rejects that last false pair, unlike the stored one-false-link result.

### R2 - Major: false-link bars disappear at full gold-pair recovery

`demo/js/find.js:16-25` clips the red segment to `1 - true_links/gold_pairs`. At 100% IDs, `true_links == gold_pairs`, so **all 77 false links at the default threshold have zero red width**. The zero-false baselines and 77-false encoded row look equally full/clean, despite the correct text counts. The same screenshot demonstrates this.

**Fix:** use a common count axis that accommodates the largest **correct + false** total, rather than clipping at the number of gold pairs. Assert that a positive false-link count produces a nonzero visible red segment, including the 100%-ID case.

### R3 - Operating-point wording still needs qualification

`SCRIPT.md:12` and its hard-question answer say “we don't run it there” / “We operate at matched precision.” The frontier is selected using that same synthetic cell's gold labels (`demo/export.py:316-374`), while the child/cohort path still calls `match_encoded` at its default **0.91** (`demo/export.py:508`). Describe this as an **in-sample comparison and proposed operating policy**, not an implemented end-to-end or field-validated 98.6% guarantee. The 2,250/31 versus 2,456/34 comparison itself is valid.

### R4 - Minor: three “slots below” are not accessible

At 1280x720/K10, `demo/js/week.js:7-25` renders seven selected rows and says **“+ 3 more slots below”**, but the remaining rows are neither rendered below nor available in Details. The tallies are numerically correct. Add the complete roster to Details, or explicitly say “not shown” instead of offering a nonexistent below-the-fold continuation.

## PLAYBOOK section 11

| Item | Yes / No | Evidence |
|---|---|---|
| 1. One command, offline, <=60 s, CPU | **YES** | Existing launcher remains offline; actual file-page first visual 0.18 s. |
| 2. Real first, live demonstration, baseline and labels | **YES** | Real state/district opening; visible encoded-versus-pooled trade-off; synthetic/real boundaries remain explicit. |
| 3. Judge-controlled “crazy” element | **YES** | Coverage/noise/K controls and the live chain/checkpoint attack work. |
| 4. Honest numbers, no unsupported claims | **NO** | R1's false impossibility claim, R2's hidden false-link segments, and R3's operating-policy wording remain. |
| 5. Three-minute script and usable fallback | **NO** | Script/fallback assets exist; the inactive-K1 cue and operating-point wording need correction before using the talk track unchanged. |
| 6. Headless smoke asserts key outputs | **YES** | Smoke passes, including new age, capacity, boundary and projector checks; the district re-derivation skip is explicit. |
| 7. Jury review in reviews and ledger | **YES** | Original review/decisions are registered at `reviews/ledger.tsv:5`; this file records the requested follow-up. |

**Next action for the lead:** fix R1/R2, align the two script cues with what is actually selected/implemented, and add this recheck to the decision trail. No source, decisions or ledger file was edited here.
