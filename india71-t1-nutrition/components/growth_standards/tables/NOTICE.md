# WHO Child Growth Standards — LMS tables (vendored for offline use)

- **What:** LMS parameters of the WHO Child Growth Standards (WHO Multicentre Growth Reference Study Group, 2006): weight-for-age (`weianthro`), length/height-for-age (`lenanthro`), weight-for-length (`wflanthro`), weight-for-height (`wfhanthro`), BMI-for-age (`bmianthro`), arm-circumference-for-age (`acanthro`).
- **Source files:** taken verbatim from `data-raw/growthstandards/` of the World Health Organization's `anthro` R package, commit `b776d8a12b1c97369c748b561159fd2ec4f4db58` (30 Jan 2026): https://github.com/WorldHealthOrganization/anthro — package licence GPL-3.0 (https://github.com/WorldHealthOrganization/anthro/blob/master/LICENSE). Only these data tables are reused; none of the package code.
- **Integrity:** SHA-256 of each file is pinned in `components/growth_standards/fetch_who.py` (same values); our engine reproduces WHO's own published expanded z-score tables to ≤0.003 z (`eval/results/growth_standards.json`).
- **Why vendored:** so the demo and tests run offline from a fresh clone (PLAYBOOK §11).
