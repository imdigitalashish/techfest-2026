# Identity linkage component

## Responsibility

This component builds a synthetic dual-registry benchmark and links Poshan Tracker records with RCH/U-WIN records inside the state identity vault. It emits only `LinkDecision.child_key`, a vault-keyed HMAC pseudonym, for analytics.

## Contracts

Inputs and outputs use `architecture/contracts/models.py` without modification:

- input rows: `IdentityRecord`-compatible Poshan and health-system DataFrames
- output rows: `LinkDecision` objects with `synthetic=True` for simulator-derived data

## How it works

1. `synth_registries.py` creates synthetic Indian child records across villages with transliteration, missingness, DOB heaping/errors, “Baby of <mother>” birth records, partial shared IDs, and one-sided records.
2. `link.py` first applies deterministic shared-ID joins, then one-to-one Fellegi–Sunter-style probabilistic linkage with blocking by village/birth-year and mother-name phonetic key.
3. `link.py` also provides a PPRL path using keyed HMAC-SHA256 Bloom-filter CLKs over quasi-identifiers and Dice similarity, so parties can link without exchanging plaintext names.
4. `eval_linkage.py` reports pairwise precision, recall, F1, clerical-review share, and runtime for ID-only, plaintext, and PPRL methods.

## Run

From the project root:

```bash
.venv/bin/python -m components.identity_linkage.eval_linkage
.venv/bin/python -m pytest components/identity_linkage
```

## Metric

The isolated component metric is pairwise F1 on the synthetic benchmark for:

- plaintext probabilistic linkage
- PPRL Bloom-filter linkage

## Privacy notes

The analytics plane receives only `child_key`. Plaintext linkage is intended to run inside the state identity vault. Bloom-filter CLKs reduce plaintext exchange but are still vulnerable to frequency and pattern attacks; mitigations include keyed HMAC, salting with a per-record attribute, balanced/XOR-folded filters, and keeping linkage inside the vault. See `research/components/identity_linkage.md` for references.

## Assumptions

- Synthetic names are hand-typed examples, not external data.
- Village codes and facility/AWC codes are synthetic.
- Default keys are demo constants; production keys must come from state key management.
- Clerical-review links are reported but not counted as accepted matches in F1.
