# Component research — C11 MRV evidence records

_Sources opened 2026-10-04. Code: [`components/mrv_ledger/`](../../components/mrv_ledger/README.md)._

## Problem in Mumbai
- **Mithi river desilting case (2025).** The SIT of Mumbai's Economic Offences Wing registered an FIR on 6 May 2025 against 13 people: five contractors, three BMC officials, three middlemen and two private-company officials. The wrongful loss to BMC was ₹65.54 crore; the alleged scam is claimed at ₹1,000 crore ([The Hindu, 7 May 2025](https://www.thehindu.com/news/national/maharashtra/mithi-river-desilting-scam-sit-registers-fir-bmc-suffered-65-crore-loss/article69546177.ece)).
- **What the inquiry found** ([Hindustan Times](https://www.hindustantimes.com/cities/mumbai-news/mithi-river-desilting-fraud-eow-books-13-people-including-three-bmc-officials-101746559759764.html)):
  - fake MoUs for silt-dumping land;
  - "nothing was found on the land leased … to dump silt";
  - the per-tonne rate rose mid-contract;
  - weighbridge weights were not recorded;
  - "no scientific evaluation" of how much silt existed.
- **Lesson for boom clearance.** Quantity claims backed only by paper slips can be fabricated and cannot be checked afterwards. Two things are needed:
  - an independent physical estimate (volume removed from the boom, seen by a sensor);
  - records that cannot be quietly edited after the fact.

## Design (built)
1. **Evidence record per trip.** Each record carries the `ClearanceRecord` with hashes of its photos and GPS track, plus a `Reconciliation`, and is sealed in a SHA-256 chain. The canonical JSON follows [RFC 8785 (JCS)](https://www.rfc-editor.org/rfc/rfc8785.html): sorted keys, ECMAScript number layout, so Python and the browser compute identical bytes.
2. **Anchor.** The head hash and length are published outside the ledger (a git commit or the ward portal). Without one, truncation and full rewrite go unseen: measured at 0 % detection without an anchor and 100 % with it (see C11 README).
3. **Ed25519 signatures** per crew device. A party who re-hashes the whole chain still cannot forge the crew's signatures.
4. **Reconciliation on a volume / dry basis.** Volume comes from the fill-fraction drop at the boom, which a camera or range sensor measures. Mass on the slip can be inflated with water or silt; volume removed from a sensed boom is harder to fake. An uncertainty-aware z-score beats a fixed ratio threshold:

   | Method (SYNTHETIC, ≈4.7–4.8 % false flags) | Fraud recall | AUC |
   |---|---|---|
   | Uncertainty-aware z-score | 71.6 % | 0.926 |
   | Fixed ratio threshold | 67.5 % | 0.917 |

## Innovation candidates (not yet built)
- **Density self-calibration.** Learn each site's density from trips with genuine weighbridge slips. Sensitivity shows this matters most: a +25 % density error raises false flags from 4.7 % to 17.8 %.
- **Photo-based volume.** Use the C7 camera fill segmentation before and after a clearance as the sensor side, and bind the photo hashes into the record (the field already exists).
- **Cross-site consistency.** A crew's claims across sites are judged against the twin's expected arrival, which catches slow, steady inflation that per-trip tests miss.
- **Public transparency page.** Publish anchors daily so citizens and auditors can verify (an EPR / plastic-credit angle; standards not yet researched — UNVERIFIED).

## Assumptions and limits
- Parameter values (density 150 kg/m³, moisture 0.40, sensor and density noise) are ASSUMPTIONS. No opened source gave measured values for Mumbai boom catch.
- The hash chain proves records were not changed after writing. It does not prove the original entry was true; the sensor reconciliation addresses that, imperfectly.
