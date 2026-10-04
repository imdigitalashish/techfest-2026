# Lead response — final-deck hostile review (gpt-6-astra, max), 4 Oct 2026

Review: [2026-10-04-final-deck-gpt-6-astra.md](2026-10-04-final-deck-gpt-6-astra.md).
**Verdict received:** READY WITH FIXES.

**Totals:** **28 ACCEPTED** (24 done, 4 need the user or the Round-2 build) · **0 REJECTED** · **1 already resolved** (D13).

Everything below is on main (see `thought_node.md` Log, 12:30 IST).

## C. Panel attacks

| # | Decision | What changed |
|---|---|---|
| C1 uncertainty interval / bypass | **ACCEPTED** | The product boundary is now **maintenance screening** (drain rate → clogging). Infiltrated volume is labelled a **model-based estimate**; the per-event band is **PLANNED** (deck slide 4; Q&A 1; plan §1). New **Backup 4**: one worked simulated event (estimate 9.80 m³ vs truth 10.38 m³, best case) plus an observability table (inlet bypass partly visible; outlet leak invisible; overflow volume estimated; blind zone below the tip). We don't show an interval the code doesn't produce. |
| C2 unplug the gauge / wake-up | **ACCEPTED — implemented** | `verifier.py` adds a **`deferred`** verdict (rain coverage < 90 % of the window, or a stage gap > 60 min). Contract v0.3.1 (`RechargeEventVerdict.deferred`, `RechargeEvent.detail`). `test_verifier.py`: 7 tests passing, including the reviewer's empty-rain and all-NaN cases. The demo has an **"Unplug rain gauge"** button. The rain gauge is now **mandatory** (it wakes the node). The deck states results assume 1-min sampling; the duty cycle is untested and is an acceptance test (plan §1). |
| C3 purchase order / first-site cost | **ACCEPTED (partly needs the user)** | Slide 8 and plan §11 show base ₹11,166.18 / first site ₹48,454.18 / 3-pit pilot ₹78,244.54 (parts only, exclusions listed). Labour and backhaul are stated as ASSUMPTIONS with no rupee figure. "First buyer" became "**prospective pilot customer; no contact yet**". **Needs user:** a dated quotation and one conversation with a provider, campus or DJB. |
| C4 pre-registration chronology / rain provenance | **ACCEPTED** | "Pre-registered" is removed. Git proves the v1 and v2 rules preceded their results (08:03 → 08:15; 08:26 → 09:46 IST). v3's rule shares a commit with its results; `program.md`'s wrong "10:50" label is **corrected, not backdated** (the rule was written ~10:31). Rain is relabelled "Open-Meteo archive, default model, not pinned". Pinning check: 8,818 of 11,352 hours identical to `models=era5`. The hourly input is frozen in `eval/data/` (sha256 in `eval/results/manifest.json`), and the minute pattern is disclosed as synthetic. Holdouts are now called "recorded checks". |
| C5 bucket size / alert time | **ACCEPTED** | Every mention is now "**large injected pulse** (500–2,000 L; demo 1,200 L)". A 20 L bucket is disclosed as undetected (unit test `test_small_bucket_is_below_event_threshold`). Demo tickets show **onset → close → issued**, and the deck says verdicts arrive when an event closes (hours to days). Slide 6 shows denominators and dev clogging precision 0.40 (3 clogged pits). The plan adds small/slow pours to the blind trials. |

## D. Red flags

| # | Decision | What changed |
|---|---|---|
| D1 team info | **ACCEPTED — needs user** | Placeholders stay visibly marked; listed under *Needs from user* (register by 9 Oct). |
| D2 inspection vacuum overclaimed | **ACCEPTED** | Opening, slide 2/3 notes, talk track, card and Q&A now say "checked by periodic inspection; nothing measures storm by storm; we add a layer alongside inspection". The landscape got a dated status note correcting "self-certification since Apr 2026". |
| D3 water balance stronger than observations | **ACCEPTED** | Slide 4 states the model basis and unobserved paths; slide 9 says "structure-level evidence … not aquifer recharge"; Backup 4 table; Q&A 1. |
| D4 band absent | **ACCEPTED** | Labelled PLANNED everywhere. The contract has no interval fields, consistent with that. |
| D5 missing rain doesn't defer | **ACCEPTED — implemented** | As C2. |
| D6 auto-zero described as available | **ACCEPTED** | Slide 7, Q&A 14 and plan §2/§4 say "tested in simulation, not adopted; PLANNED firmware". |
| D7 datum / material / reference | **ACCEPTED** | Tip 5–10 cm above the floor gives a 0.11–0.23 m³ blind zone (A: 2.25 m²) on slide 7, plan §2/§4 and Q&A 14. Vented probe with a desiccant vent end. Material quoted from the datasheet ("316L stainless steel"); the reviewer's 316L membrane / 304 casing reading is noted as not re-verified. The error budget is scoped to the storage term only. |
| D8 schedule evaluated ≠ advertised | **ACCEPTED** | Slide 6: "assumes 1-min stage sampling throughout; the duty-cycled schedule is untested". Plan §1 adds a duty-cycle acceptance test. |
| D9 plans read as guarantees | **ACCEPTED** | Status tags (BUILT · SIMULATED · PLANNED · DATASHEET · SAFETY) on slides 4 and 7. "We built the instrument" removed. The buffer is a planned 24 h acceptance test with capacity/overwrite rules first. The antenna sits clear of metal lids. |
| D10 parts sum vs deployment cost | **ACCEPTED** | As C3. The earlier lead-response line "The installed cost includes them" was wrong and is corrected below. |
| D11 expired target / no buyer | **ACCEPTED** | Slide 3: "target was 30 Jun 2026; we found no completion report". Customer status: prospective, no contact. |
| D12 chronology | **ACCEPTED** | As C4. |
| D13 five-rejections wording | **RESOLVED** during review | No further change. |
| D14 fake-pour scale | **ACCEPTED** | As C5. |
| D15 event label vs alert time | **ACCEPTED — implemented** | Demo tickets: "issued ‹close time›" with "Event ‹onset› → ‹close›". |
| D16 scoring unit / denominators | **ACCEPTED** | `eval.py` now reports a `counts` block (reporting only; all 6 re-runs reproduce identical metrics). Slide 6 and Q&A show 1,233 scored windows, 2/1,291 and 15/1,156 false implausibles, and clogging P/R 0.67/1.0 (holdout, 10 pits) and 0.40/0.67 (dev, 3 pits). `eval/results/manifest.json` has checksums. |
| D17 ERA5 provenance / minute rain | **ACCEPTED** | As C4. |
| D18 WRIS interpretation | **ACCEPTED** | The WRIS slide moved to Backup 0 as a "public-stream snapshot". It notes the latest reading (4 Jun 2026) and labels the 2.5 m statistic exploratory and not attributed to RWH. |
| D19 regional scalability | **ACCEPTED** | Slide 8 adaptation line (same software; per-site fill calibration and safety check; local radio; local rules; first pilot = one structure type). Q&A 23 rewritten. |
| D20 water-quality gate | **ACCEPTED** | Slide 9, plan §12 and Q&A 24: pilot only on permitted roof-runoff structures with pretreatment and a responsible operator. EC alone doesn't certify safety. |
| D21 stale documents | **ACCEPTED** | Dated "current state" notes added to the landscape, verifier README, ADR and components. History kept as history. |
| D22 footer promise / assets | **ACCEPTED** | Footer now: "Sources on slides or in notes · (A) = assumption · status labels". Map title moved left (no colour-bar overlap). Slide 5 uses an enlarged crop (pit panel + ticket). |
| D23 no reserve | **ACCEPTED** | Slide 4 (WRIS) moved to backup; timing now 9:15 with a 45 s reserve (talk track, card, deck notes). **Needs user:** a timed rehearsal on the exported PDF. |
| D24 pre-monsoon test | **ACCEPTED** | Slide 7, slide 9 and plan §2: a pre-monsoon metered fill check. Q&A 17. |

## F. Top three fixes — status
1. **Claims match the kept code: DONE.** Band and auto-zero are labelled planned; deferral is implemented and tested; drainage screening is the boundary; pulse scale and alert timing are disclosed.
2. **Evidence story: DONE.** Chronology corrected without backdating; denominators published; rain provenance relabelled and frozen; manifest added.
3. **Bounded pilot proposal: DONE except user items.** Pilot cost table with exclusions; prospective customer; datum, vent and safety boundaries; adaptation line; slide 4 moved to backup with the 9:15 route. Team details and the timed rehearsal need the user.

## Correction to `2026-10-04-lead-response.md`
That response said for O3 "The installed cost includes them." That was **wrong**: the published ₹11,166.18 is a parts subtotal that excludes the tube, cable, potting, installation and service. The current statement is in `deliverables/prototype-plan.md` §11.
