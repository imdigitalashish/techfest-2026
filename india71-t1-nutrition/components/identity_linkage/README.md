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

### Stress knobs (added for the demo; defaults reproduce the committed benchmark byte for byte)

- `generate_benchmark(..., shared_id_rate=0.35, extra_noise=0.0)`. `shared_id_rate` is the share of Poshan Tracker records (of children also in the health registry) that carry the RCH ID; 0.35 is a **simulation assumption**, not a measured figure. `extra_noise` adds, per name field and DOB, one extra typo / DOB entry error with that probability, on top of the base noise. It uses its own RNG with a fixed number of draws per field (common random numbers), so a field corrupted at a lower rate is corrupted identically at every higher rate.
- `identities_for_cohort(children, ...)` gives `cohort_simulator` children Poshan Tracker and health-side identity records with the same name/DOB noise helpers, so a child's measurements and health events can be joined only through linkage (used by `demo/export.py`).
- Tests: `test_linkage.py` pins the default output's SHA-256 and checks both knobs.

### Department boundary (`pprl.py`)

`link.py` takes both sides' plaintext records in one process. `pprl.py` makes the boundary explicit and testable:

- `encode_department(records_df, secret_key)` runs inside each department and emits only `source`, `record_id`, `clk` (1,000-bit Bloom filter, hex), keyed-HMAC `block_tokens` (village × birth-year band, mother-name phonetic code), keyed-HMAC `id_tokens` (shared programme IDs), a keyed-HMAC `sex_token` and `synthetic`. No name, DOB, village or sex in plaintext.
- `match_encoded(enc_a, enc_b, threshold)` accepts exactly those columns (fails closed otherwise) and reproduces `link_pprl_bloom` decision for decision: same ID step, blocking, Dice score with sex penalty, greedy assignment and thresholds. Only an ID-joined pair's `child_key` differs (derived from the ID token).
- `accept_at(decisions, t)` relabels a `clerical_low` run as if matched at threshold `t` (the assignment doesn't depend on it), for precision-matched comparisons.
- `test_pprl.py`: identical F1/precision/recall to `eval/results/identity_linkage.json`; identical decisions to `link_pprl_bloom` across knob settings; only allowed columns and no plaintext in the encoded frames; record IDs treated as opaque labels; `accept_at` equals a re-run.
- The matcher still learns which records share a token, and Bloom filters are attackable (frequency and pattern mining). The secret key must be withheld from the matcher; hardening is a pilot item.

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
