# Contracts

`contracts.schema.json` holds the internal seams between components (JSON Schema 2020-12, `$defs`): `ParsedDocument` (C1→C2/C3/C4), `DocType` (C2→C4/C5), `EvidenceItem` (C3→C4/C6), `TRLDistribution` (C4→C5), `TRLDecision` (C5→C6/C7), `GapAnalysis` (C6→C7), `Assessment` (C7, internal record).

The **official** output schema is not defined here: it will be released on 10 Oct and C7 will load it from a file at run time and map `Assessment` onto it, validating every record before writing. See [../components.md](../components.md).
