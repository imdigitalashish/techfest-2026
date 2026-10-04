# C11 — MRV evidence records (hash-chained, signed, reconciled)

Turns each crew clearance claim into a tamper-evident evidence record, `contracts.LedgerEntry`, and checks the claimed quantity against an independent, volume-based sensor estimate. It does not pay anyone. It makes a claim auditable and flags the ones that need a look.

**Why.** In May 2025 Mumbai's Economic Offences Wing booked 13 people, including three BMC officials, over Mithi river desilting. The wrongful loss was ₹65.54 crore. The preliminary inquiry found MoUs for silt-dumping land that were fake, and "nothing was found on the land leased … to dump silt". Staff "did not record the weight being carried by the dumpers that came to the weighbridge". An EOW officer said "there was no scientific evaluation done of how much silt was there" ([Hindustan Times, May 2025](https://www.hindustantimes.com/cities/mumbai-news/mithi-river-desilting-fraud-eow-books-13-people-including-three-bmc-officials-101746559759764.html); [The Hindu, 7 May 2025](https://www.thehindu.com/news/national/maharashtra/mithi-river-desilting-scam-sit-registers-fir-bmc-suffered-65-crore-loss/article69546177.ece); both opened 2026-10-04). Boom-clearance contracts paid per kg have the same weak point. This component is designed for it.

## What it does
| Piece | File | Notes |
|---|---|---|
| Canonical JSON + SHA-256 | `canonical.py` | RFC 8785-style: keys sorted, compact, numbers laid out like ECMAScript. Byte-identical to the browser verifier `dashboard/site/ledger_verify.js`, which the tests check through node. |
| Hash chain | `chain.py` | `hash = sha256(canonical({seq, record, reconciliation, prev_hash}))`, genesis `0×64`. `verify(entries, anchor)` catches any edit, deletion, insertion or reordering. Tail truncation and wholesale rewrite are caught only against a **published anchor** (length + head hash, e.g. committed to git or posted on the ward portal). |
| Signatures | `chain.py` | Ed25519 over each entry hash, one key per crew device, plus a key registry. This catches a consistent rewrite that re-hashes the whole chain. **Demo keys derive from public seeds (DEMO ONLY).** |
| Reconciliation | `reconcile.py` | Works on a **dry-equivalent basis**. Sensor kg = fill-fraction drop × boom capacity (m³) × wet bulk density × (1 − moisture); the claim uses the same moisture. Score `z = (claimed − sensor)/σ_honest`, where σ_honest is built from fill-sensor noise, density variation and reporting noise. Flags: `ok`, `review` (z > threshold), `reject` (z > 2.326, or claim > weighbridge slip). Also flags no detectable fill drop, missing photo hashes, and an implied wet density above 450 kg/m³ (suspected water or silt). |
| Synthetic trips | `synth.py` | Four kinds: honest; inflated (claim × U(1.2, 3)); phantom (no clearance happened); wetted (soaked or silted load with a genuine slip × U(1.3, 2)). Also `twin_clearance_events()`, which turns the twin's `cleared_kg` runs into honest trips. |

All parameters in `reconcile.Params` are **ASSUMPTIONS**: wet bulk density 150 kg/m³, moisture 0.40, fill σ 0.03, density σ 25 %, claim σ 10 %. No opened source gave measured values for Mumbai boom catch. They must be calibrated with weighed and volumed samples. The dashboard build recalibrates density per site from the twin (`stored_kg / (fill × capacity)`).

## Results (SYNTHETIC data — `python3 -m mrv_ledger.evaluate`, run at git 57938df)
The threshold is calibrated on 20 000 separate honest trips, aiming for 4.75 % flags, which is 5 % minus the one-sided 95 % sampling margin. It is then tested on 10 000 honest, 3 000 inflated, 1 000 phantom and 1 000 wetted trips.

| Method | Fraud recall | False flags (honest) | Inflated ×1.2–1.5 / 1.5–2 / 2–3 | Phantom | Wetted | Precision @5 % / 10 % prevalence | AUC |
|---|---|---|---|---|---|---|---|
| **Uncertainty-aware z (proposed)** | **71.6 %** | **4.7 %** | 24.4 / 58.0 / 88.6 % | 100 % | 50.0 % | 44.5 % / 62.9 % | 0.926 |
| Fixed ratio threshold (baseline) | 67.5 % | 4.8 % | 20.6 / 50.3 / 85.5 % | 100 % | 42.8 % | 42.6 % / 61.0 % | 0.917 |
| Status quo: claim vs weighbridge slip only | 0 % | 0 % | 0 / 0 / 0 % | 0 % | 0 % | — | — |

- **Tamper detection with a published anchor: 100 %** for edit, delete, reorder, insert, tail truncation and suffix rewrite (200 random trials each, 300-record ledger). Without the anchor, truncation and suffix rewrite go **undetected (0 %)**, which is why the anchor is required. Signatures catch the suffix rewrite (100 %). Unit tests cover every single-field edit, every deletion and every adjacent swap.
- **Honest limits.** Inflation below ×1.5 is mostly invisible (24 % recall) under 25 % density noise. At 5 % fraud prevalence, fewer than half of the flags are fraud, so a flag means *review*, not *penalise*. Density calibration dominates: if true density is 25 % above nominal, honest false flags rise from 4.7 % to **17.8 %**; at −20 %, they fall to 0.75 %. The fix is to recalibrate density per site from trips that carry a genuine weighbridge slip.
- Status quo row: when the slip itself is forged, or matches a soaked load, a slip check catches nothing in this synthetic setup.

Full numbers: `results/eval_detail.json`. Flat metrics for the dashboard: `results/metrics.json`.

## Use
```bash
cd innovatex-t3-coastal-plastic/components
python3 -m mrv_ledger.evaluate                 # metrics (≈2 min)
python3 -m pytest mrv_ledger/tests -q          # 19 tests incl. Python↔JS hash parity (needs node)
```
```python
from mrv_ledger import append, reconcile, verify, anchor
entries = []; append(entries, record, reconcile(record, boom_capacity_m3=12.0))
verify(entries, expected_anchor=published).ok
```

## Decisions and assumptions
- The contract's `LedgerEntry.hash` covers `(seq, record, reconciliation, prev_hash)`, so the flag is sealed at write time. Re-reconciling with better parameters means appending a new entry, not editing an old one.
- Ratio uses `claimed / max(sensor, 1 kg)` to stay finite. `reasons` carries `payable_dry_kg = min(claimed, sensor)` as a suggested settlement basis.
- Contract gaps for the lead to consider: signatures, anchor and key registry live outside `LedgerEntry` (in `dashboard/site/aux.json`). A `signature` field and an anchor log would make them first-class.
