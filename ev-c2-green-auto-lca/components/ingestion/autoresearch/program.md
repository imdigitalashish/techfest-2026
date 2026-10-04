# Autoresearch program — C3 quote verifier (spike A gate)

**Goal.** Maximise the share of genuinely verbatim quotes that the verifier finds in their source documents, while accepting **zero** quotes with a perturbed number. This is the fail-closed gate that every AI-extracted record must pass before it can be marked `verified`.

**Metric (frozen `eval.py`).** `scalar = found_rate` on gold positives (all `verified` records with a local PDF), forced to 0 if any digit-perturbed negative is accepted. Secondary: `false_accept_rate`, misses list.

**Editable:** `components/ingestion/verifier.py` only. **Frozen:** `eval.py`, the gold records (changes to gold data must be logged as a re-baseline row).

**Constraints.** No fuzzy matching of numbers (digits must match exactly); fragments of a quote are joined with ` ... ` (convention in `architecture/agent-brief.md`); keep it explainable to a jury.

**Idea backlog.**
1. Split quotes on ` ... ` and require every fragment, in order.
2. Table-aware matching: allow a fragment's tokens to be separated by layout noise (other columns, line breaks) within a bounded window, numbers still exact.
3. Unicode normalisation (en dash vs hyphen, curly quotes, ligatures, non-breaking spaces).
4. Number formats (thousand separators "120,000" vs "120 000") — only if negatives stay at 0.
5. Use pdfplumber words with coordinates for true table-cell matching (row/column alignment).

**Re-check.** When the gold set grows (new sources), re-run on the new records only as a held-out check before accepting new verifier versions.
