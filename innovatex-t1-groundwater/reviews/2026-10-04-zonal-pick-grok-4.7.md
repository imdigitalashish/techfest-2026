# Cross-model review — Delhi-zonal theme pick (JalSakshi vs DustLedger)

- **Date:** 2026-10-04 · **Reviewer:** `grok-4.7`, reasoning effort `xhigh` · **Commissioned by:** Supervisor
- **Brief given:** act as a hostile InnovateX Delhi-zonal judge; compare T1 JalSakshi (`innovatex-t1-groundwater/`) with T2 DustLedger (`innovatex-t2-aqi/`) on the official criteria; verify load-bearing claims at their sources; pick one.
- **Verdict:** **A — JalSakshi.** It agrees with the independent `gpt-6-astra` judge: [2026-10-04-zonal-pick-gpt-6-astra.md](2026-10-04-zonal-pick-gpt-6-astra.md).
- **Lead:** mark each attack and red flag below as ACCEPTED or REJECTED with a reason, then add a line to `reviews/ledger.tsv`.

---

**Pick JalSakshi (A).** Delhi advances five teams in total, not five per theme, and AQI will draw a pile of entries.

DustLedger's honest answers won't survive a hostile 10 minutes: no price, no city AQI reduction, silent in calm wind, and exemptions that are only a wish. JalSakshi can be stated in the minister's own words and has a cost number. Its 1 Dec prototype is one node and a drum. A four-node dust ring plus a partner site is how a systems-heavy team misses the prototype bar, then loses at the national finals to other cities' AQI teams.

I opened the load-bearing pages:
- Hindustan Times (21 Apr 2026) reports ₹204.46 crore (2017–24) and "Till now, there was a rule but no real checking." It also says self-disclosure "is also being planned", and that non-compliance "may" draw a 1.5× bill.
- Indian Express confirms the Delhi Jal Board (DJB) will restore 1,000 non-functional government systems and build 500 new ones (claimed 733 million litres a year).
- Acorn's page lists about ₹38,000 and twice-daily logging.
- The News Mill confirms the Winter Action Plan dates and 334 teams.
- Down To Earth matches the worker figures.
- Hindustan Times confirms 47 Delhi stations, going to 60.
- CSTEP's page says low-cost sensors can "qualitatively assess" construction-dust controls.
- Both eval ledgers match the slides.

I did not re-download the CGWB PDF.

### Scores

| Criterion | A | B | Why |
|---|---|---|---|
| Creativity & novelty | 4 | 3 | A turns a rebate rule into a per-storm verdict. B is a cheaper fence-line ring; its self-calibration gain fell to 17% on their own stress test. |
| Functionality & usability | 3 | 2 | A's 3.0% is same-model; the harsh test gives 13%, and there's no physical pit. B: 57 µg/m³ MAE and CSI 0.61 on simulated plumes, and it abstains when Delhi's air is calm. |
| Cost & market value | 3 | 2 | A has a sourced BOM and a real comparator, but the part that can do the job isn't in the ₹10,100. B's pitch is still unpriced; the wind head alone costs ₹14.8–21.8k. |
| Technical feasibility | 3 | 2 | A's metered fill test is the right experiment, but the named sensor is 30 bar. B has no power budget, no coarse-dust result and no site. |
| Regional scalability | 3 | 3 | A's twin runs on India-WRIS, but the rebate doesn't travel. B needs no city model; its payer is Delhi's construction ban. |
| Impact | 3 | 3 | Neither has an outcome number. A can audit cubic metres. B's worker story is real, but the PM reduction is blank, and they quote the "don't fixate on dust" objection. |
| Design & ergonomics | 3 | 3 | A's four verdicts match what an inspector needs. B's Hindi supervisor view targets the right user. Neither UI exists yet. |
| Local-depth bonus | 4 | 4 | Both are far above a generic kit. Each loses a point for a rule they overstated. |

### Attacks a Delhi panel will make, and the 9 Oct fix

1. **Wrong sensor.** `prototype-plan.md` §1 calls the MS5837-30BA a 0–3 m sensor, but `bom-prices.md` row 1 lists it as "30 bar" / "Sealed Gauge" (about 300 m). Remove that line. Put the ₹17,500 0–5 m probe on the slide, recompute the mm and m³ error, drop the ₹3,089 SparkFun BME280, and state the real node price.
2. **Self-certification is not in force.** The deck table ("Verification from 2026") and pitch slide 3 overread the Hindustan Times report. Quote the plan, then say the verification system doesn't exist yet and you're bidding to be it.
3. **The 3% is circular, and slide 2 is a problem you don't solve.** Lead with 13% and "n=10 simulated fakes". Move illegal borewells to a backup slide and open on the rebate.
4. **No owner will buy a device that can take their rebate away.** The buyer is DJB's 1,000 government-building restorations (Indian Express; Phase I targeted 30 Jun 2026). Add one line: an inspector can override the verdict. Don't call the ₹204 crore your market.
5. **There's no impact number, and "≥3 years" battery life is a wish.** Use 733 million litres a year as the claim you will audit, not as your result. Replace the battery line with the labelled upper bound of 11 mAh/day. Fill in the team name and ID.

### Five questions

1. **"A level isn't recharge."** Inflow comes from the rise, checked against rain × catchment; overflow is capped at the spill level; area and drain rate come from one metered hose fill. The output is infiltrated volume with a confidence band, and an unseen bypass widens the band. Never say "aquifer recharge".
2. **"Your 3% grades your own simulator."** Yes. With the same linear drain we get 3.0% on the holdout; with a mismatched drain, 13.1%. We refused the fit that helped the stress test because it broke the first evaluator. The December evidence will be a blind test with a metered drum.
3. **"₹10,100 and a dive sensor won't pass."** That listing is off the slide. The build uses a 0–5 m probe and still costs less than Acorn's ₹38,000 logger, which logs only twice a day and so misses a two-hour storm. I opened that page.
4. **"Who pays if the owner loses money?"** Not households at first. First the government buildings DJB is already restoring, then campuses that can pass. The verdict ranks inspections; it doesn't automatically cut a bill.
5. **"This isn't underground, and you can't see illegal borewells."** The brief allows aquifer-recharge analysis. The radio sits in the lid because below-grade antennas fail. Six-hourly piezometer readings miss pump cycles. We won't accuse a well.

### Overclaimed or wrong

- **A, `zonal-deck.md` slide "The lever…" and `zonal-pitch.md` slide 3:** self-certification is stated as the 2026 rule; Hindustan Times says it's planned. The same slip is in the selection memo.
- **A, deck table and pitch slide 3:** the 1.5× penalty is stated as the rule; Hindustan Times says non-compliance "may attract" it.
- **A, `prototype-plan.md` §1:** the MS5837-30BA is presented as a 0–3 m pit sensor, but the team's own BOM says 30 bar. Tube, cable and potting are excluded from the ₹10,100.67.
- **A, selection memo:** demo strength 5/5, but no pour rig exists. `landscape.md` still says the BOM is unverified, while `bom-prices.md` later verifies prices and then wrongly sums them to a ₹32,428 "per-node" total. The ₹204.46 crore comes from Hindustan Times citing DJB, not a ledger the team saw.
- **B, `zonal-pitch.md` slide 1 notes:** "restrict all of them… whether clean or dirty". The News Mill says 1 Nov–31 Jan prohibits dust-generating demolition and outdoor civil works; the total ban runs only 10 Dec–20 Jan.
- **B, `landscape.md` §2 and pitch slide 3:** a ₹5 lakh "CAQM schedule". The Hindustan Times piece describes ₹5 lakh as Delhi's existing fine, and the new schedule as ₹1–2 lakh, doubled under GRAP.
- **B, selection-memo one-liner:** "tamper-proof" and "clean sites can keep working". The pitch Q&A correctly walks both back; saying the one-liner aloud would be false.
- **B:** construction's share of PM is still unverified, and the pitch has no kit price even though `hardware-bom.md` already has listings. That's an omission, not a fake number. Don't revive the −42% from the easy simulator.
