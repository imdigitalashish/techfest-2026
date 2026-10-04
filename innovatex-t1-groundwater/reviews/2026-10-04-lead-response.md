# Lead response to the zonal-pick reviews (4 Oct 2026)

Reviews: [gpt-6-astra (max)](2026-10-04-zonal-pick-gpt-6-astra.md) · [grok-4.7 (xhigh)](2026-10-04-zonal-pick-grok-4.7.md). Both picked **A — JalSakshi**.

On 4 Oct (10:25 IST) the lead re-opened the two load-bearing articles:
- **Hindustan Times, 21 Apr 2026:**
  - "A self-disclosure mechanism is also being planned…"
  - "Non-compliance may attract penalties, including a 1.5-times increase in water bills…"
  - "adequacy and functionality certificates are issued after inspection and require periodic renewal"
- **Indian Express (2026):**
  - RWH "mandatory … for plots measuring 100 square metres and above since 2001"
  - 7,596 of 9,148 government buildings have RWH
  - DJB will restore 1,000 non-functional systems and build 500 new ones (Phase I, target 30 Jun 2026)
  - "recharge potential … approximately 733 million litres … annually" (an estimate)
  - a DJB "online portal to track installations, monitor compliance" is being developed
  - DJB has "empanelled 59 service providers for the implementation, promotion and maintenance"

Status key: **ACCEPTED** = we change the work; **REJECTED** = we keep it, with a reason; **N/A** = the item concerns T2 DustLedger. Every fix is tracked in the thought node Log.

## gpt-6-astra

| # | Item | Decision | Reason / fix |
|---|---|---|---|
| A1 | The water balance is unobservable from stage alone | **ACCEPTED** | Two outputs are now separated. (1) **Drain rate from falling-head recessions → clogging index**: directly observed, the primary maintenance product. (2) **Infiltrated volume ± band** from the stage rise, checked against rain × catchment, with overflow capped at the spill stage and pit area and drain rate fixed by one metered hose fill. Bypasses widen the band. For pilots, an optional downpipe flow check validates inflow. We never say "aquifer recharge". |
| A2 | The simulation confirms itself | **ACCEPTED** | 3.0 % and 100 % are labelled "simulation, same drain model". The deck leads with **13 %** (stress test) and "n = 10 simulated fakes". Blind weighed-water trials are in the Round-2 plan. A hardware teammate goes under Needs from user. |
| A3 | Affordability misleading ("≥ ₹47,389 in listed parts") | **ACCEPTED in substance; figure REJECTED** | We recompute an installed node cost with the right sensor and every line priced (tube, cable, potting included or marked UNVERIFIED). We could not reproduce ₹47,389 from our BOM rows. Our single-node sum with the ₹17,500 probe, gauge and ESP32 is ₹31,229.67, and the ₹33,559 shared gateway and the ₹14,500 bench PPK2 are not per-node. We publish our own arithmetic. |
| A4 | No committed buyer | **ACCEPTED** | The buyer is DJB's Phase-I restorations of government buildings, through its 59 empanelled service providers, then campuses and RWAs. The product sells failure detection and inspection ranking, never automatic rebates or penalties. A pilot letter and two maintenance-officer interviews go under Needs from user. |
| A5 | Reliability untested (15-min polling misses events; battery) | **ACCEPTED** | Rain-gauge interrupt plus rise-triggered 1-min sampling, outage buffering and current draw become explicit bench tests in Round 2. The 3-year battery life stays a target only, and the 11 mAh/day reference is labelled as a different node. |
| Q1–Q5 | Five judge questions | **ACCEPTED** | Folded into `deliverables/qa-prep.md`. |
| R1 | Self-certification is planned and certificates come after inspection; "never checked" overclaims | **ACCEPTED** | Reworded everywhere: "self-disclosure is being planned; today certificates follow periodic inspection; the minister: 'no real checking'". Pitch line: **"the verification system doesn't exist yet; we're bidding to be it."** |
| R2 | "Delhi pumps more than it recharges" contradicts 92.1 % | **ACCEPTED** | CGWB 2025 gives recharge 0.38 bcm and extraction 0.32 bcm, so city-wide Delhi does *not* pump more than it recharges. New title: "Delhi uses 92 % of its extractable groundwater; 10 of 34 tehsils over-exploited". |
| R3 | Acorn is one product, not every CGWA logger | **ACCEPTED** | Now phrased as "e.g. one CGWA-compliant DWLR (Acorn PZM-24B): 2 readings/day, ≈ ₹38,000". |
| R4 | 3 m-FS accuracy borrowed for a 30-bar sensor | **ACCEPTED** | MS5837-30BA removed. The error budget is recomputed for the 0–5 m probe actually specified. |
| B items | DustLedger red flags | N/A | T2's lead owns them. |

## grok-4.7

| # | Item | Decision | Reason / fix |
|---|---|---|---|
| G1 | Wrong sensor; put the 0–5 m probe on the slide; drop the ₹3,089 BME280; state the real node price | **ACCEPTED** | Same fix as R4/A3. A 4–20 mA 0–5 m submersible probe is the baseline. A gauge-type (vented) probe needs no barometer, which removes the BME280. If a cheaper probe can't be verified, the ₹17,500 listing stands. |
| G2 | Self-certification is not in force | **ACCEPTED** | As R1. |
| G3 | 3 % is circular; open on the rebate; illegal borewells to backup | **ACCEPTED** | The deck opens on the rebate/verification gap. Illegal borewells move to a backup slide. Results lead with 13 %. |
| G4 | No owner buys a device that can take their rebate | **ACCEPTED** | As A4, plus "an inspector can override any verdict". ₹204.46 cr is never called our market. |
| G5 | No impact number; battery life is a wish | **ACCEPTED** | DJB's own estimate (733 M L/yr for Phase I) is presented as **the claim we will audit**, not our result. The battery line is replaced with a measurement plan plus a labelled reference. Team name/ID go under Needs from user. |
| Q1–Q5 | Five questions | **ACCEPTED** | In `qa-prep.md`. |
| O1/O2 | Self-certification and the 1.5× penalty overstated | **ACCEPTED** | "may attract" wording. The deck table now carries a Status column (in force / planned / may). |
| O3 | MS5837 as a 0–3 m sensor; tube/cable/potting excluded | **ACCEPTED** | As G1. The installed cost includes them. |
| O4 | Memo demo 5/5 without a rig; landscape says BOM unverified; ₹32,428 mis-sum; ₹204 cr via HT | **ACCEPTED** | Memo demo score drops to 3/5 (offline replay only) until a pour rig exists. Landscape BOM status updated. `bom-prices.md` corrected with a note: ₹32,428.67 summed both sensor options and was not a per-node price. ₹204.46 cr is always cited as "HT, citing DJB data". |
| B items | DustLedger | N/A | T2's lead owns them. |
