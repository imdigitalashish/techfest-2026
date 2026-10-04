# PARAKH Rashtriya Sarvekshan 2024 — State Report Card URL Research

Primary-source research into official PDF locations for Grade 3 Language/Mathematics
average percentages, by state. All URLs below were tested live via `curl` against
`parakh.ncert.gov.in` (HTTP status recorded alongside). Host is a Drupal site; files
are served from `/sites/default/files/<upload-month>/...` with no directory listing
(`GET /sites/default/files/2025-07/` → 404) and no state picker exposed in the static
HTML of https://parakh.ncert.gov.in/prs (that page is a narrative overview; its only
PDF links are national technical/assessment-framework docs, not state report cards).

## Confirmed URL pattern

```
https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_<StateName>_IND0<NN>.pdf
```

- `<StateName>` = official state/UT name, spaces URL-encoded as `%20`, `&` encoded as
  literal `%26` (double-encoding, e.g. `%2526`, returns 404).
- `IND<NNN>` = the state/UT code used in the PARAKH filenames, prefixed `IND`
  (e.g. 009 = Uttar Pradesh, 023 = Madhya Pradesh, 027 = Maharashtra).
- National report is the `IND` (no numeric suffix) case: `REPORT_India_IND.pdf`.
- Upload folder `2025-07` (July 2025) is correct for every state/UT tested; no other
  month folder (`2025-05/06/08/09`) returned 200 for the national file, so state PDFs
  almost certainly all live under `2025-07` too (confirmed for every state below).

Discovery path: the pattern itself is not linked from `/prs` or the national PDF; it
was located via web search hits pointing at mirrored/CDN copies
(`druid.parakh.ncert.gov.in`, `lms.parakh.ncert.gov.in`) that exposed the exact
filenames, which were then re-tested directly against the canonical
`parakh.ncert.gov.in` host (Referer `https://parakh.ncert.gov.in/prs` not required —
plain GET suffices; tested with and without a custom User-Agent, no difference).

## Tested state/UT URLs and HTTP status

All fetched 2026-10-04 via `curl -L` against `https://parakh.ncert.gov.in/sites/default/files/2025-07/`.

| Status | State / UT | Code | Filename |
|---|---|---|---|
| 200 | India (national) | IND | `REPORT_India_IND.pdf` |
| 200 | Jammu & Kashmir | IND001 | `REPORT_Jammu%20%26%20Kashmir_IND001.pdf` |
| 200 | Himachal Pradesh | IND002 | `REPORT_Himachal%20Pradesh_IND002.pdf` |
| 200 | Punjab | IND003 | `REPORT_Punjab_IND003.pdf` |
| 200 | Chandigarh | IND004 | `REPORT_Chandigarh_IND004.pdf` |
| 200 | Uttarakhand | IND005 | `REPORT_Uttarakhand_IND005.pdf` |
| 200 | Haryana | IND006 | `REPORT_Haryana_IND006.pdf` |
| 200 | NCT of Delhi | IND007 | `REPORT_NCT%20of%20Delhi_IND007.pdf` (also `..._IND007_0.pdf`) |
| 200 | Rajasthan | IND008 | `REPORT_Rajasthan_IND008.pdf` |
| 200 | Uttar Pradesh | IND009 | `REPORT_Uttar%20Pradesh_IND009.pdf` |
| 200 | Bihar | IND010 | `REPORT_Bihar_IND010.pdf` |
| 200 | Sikkim | IND011 | `REPORT_Sikkim_IND011.pdf` |
| 200 | Arunachal Pradesh | IND012 | `REPORT_Arunachal%20Pradesh_IND012.pdf` |
| 200 | Nagaland | IND013 | `REPORT_Nagaland_IND013.pdf` |
| 200 | Manipur | IND014 | `REPORT_Manipur_IND014.pdf` |
| 200 | Mizoram | IND015 | `REPORT_Mizoram_IND015.pdf` |
| 200 | Tripura | IND016 | `REPORT_Tripura_IND016.pdf` |
| 200 | Meghalaya | IND017 | `REPORT_Meghalaya_IND017.pdf` |
| 200 | Assam | IND018 | `REPORT_Assam_IND018.pdf` |
| 200 | West Bengal | IND019 | `REPORT_West%20Bengal_IND019.pdf` |
| 200 | Jharkhand | IND020 | `REPORT_Jharkhand_IND020.pdf` |
| 200 | Odisha | IND021 | `REPORT_Odisha_IND021.pdf` |
| 200 | Chhattisgarh | IND022 | `REPORT_Chhattisgarh_IND022.pdf` |
| 200 | Madhya Pradesh | IND023 | `REPORT_Madhya%20Pradesh_IND023.pdf` |
| 200 | Gujarat | IND024 | `REPORT_Gujarat_IND024.pdf` |
| 404 | Daman & Diu (standalone) | IND025 | tried `Daman%20and%20Diu`, `Daman%20%26%20Diu` — both 404 |
| 404 | Dadra & Nagar Haveli (standalone) | IND026 | tried `Dadra%20and%20Nagar%20Haveli`, with `%26` — both 404; merged-UT name `Dadra%20and%20Nagar%20Haveli%20and%20Daman%20and%20Diu` also 404 at both 025 and 026 |
| 200 | Maharashtra | IND027 | `REPORT_Maharashtra_IND027.pdf` |
| 200 | Andhra Pradesh | IND028 | `REPORT_Andhra%20Pradesh_IND028.pdf` |
| 200 | Karnataka | IND029 | `REPORT_Karnataka_IND029.pdf` |
| 200 | Goa | IND030 | `REPORT_Goa_IND030.pdf` |
| 200 | Lakshadweep | IND031 | `REPORT_Lakshadweep_IND031.pdf` |
| 200 | Kerala | IND032 | `REPORT_Kerala_IND032.pdf` |
| 200 | Tamil Nadu | IND033 | `REPORT_Tamil%20Nadu_IND033.pdf` |
| 200 | Puducherry | IND034 | `REPORT_Puducherry_IND034.pdf` |
| 200 | Andaman & Nicobar Islands | IND035 | `REPORT_Andaman%20%26%20Nicobar%20Islands_IND035.pdf` |
| 200 | Telangana | IND036 | `REPORT_Telangana_IND036.pdf` |
| 200 | Ladakh | IND037 | `REPORT_Ladakh_IND037.pdf` |

**Gap:** the merged UT "Dadra & Nagar Haveli and Daman & Diu" is referenced in the
national report's text (as a state doing well on Mathematics by School Management —
see below) but no state-code/name combination tried for codes 025/026 resolved; this
UT's individual report PDF filename was not found (not essential for state-level
analysis — this is the smallest UT by population).

## Where Grade 3 Language/Mathematics averages appear in the PDFs

### National report (`REPORT_India_IND.pdf`, cached at `.data/parakh-prs-2024-india.pdf` / `.txt`)
- Section **"Assessing Foundational Stage Competencies (Grade 3)"** (report p.2–4).
- Breakdown bar charts give national Grade 3 **Language vs Mathematics** % by:
  Gender (Boys 63%/60%, Girls 65%/60%), Location (Rural 64%/60%, Urban 63%/59%),
  School Management (State Govt. 64%/61%, Govt. Aided 63%/58%, Private 64%/60%,
  Central Govt. 60%/57%), Social Category (SC 64%/60%, ST 61%/57%, OBC 63%/60%,
  Others 66%/61%) — `.data/parakh-prs-2024-india.txt:252-289`.
- Section **"Competency-wise Performance (Grade 3)"** gives per-competency % (not a
  single subject average), e.g. C-9.7 Language 67%, C-10.5 Language 60%, C-10.7
  Language 61% — `.data/parakh-prs-2024-india.txt:303-320`.
- The clean **overall national average** (not broken down by subgroup) is best read
  off any state report's comparison chart (see below): **Language 64%, Mathematics
  60%** nationally for Grade 3, consistent with the subgroup breakdowns above.

### State reports (same template for every state, e.g. `REPORT_Madhya Pradesh_IND023.pdf`)
- Page **12** of the PDF (page footer reads "GRADE 3 … State Report: <State>"),
  section header **"Comparison of State Average with National Average Across
  Subjects"**, directly under "Assessing Foundational Stage Competencies (Grade 3)".
- This is a two-bar chart per subject giving exactly the two numbers needed:
  **State Grade 3 Language %** vs **National Language %**, and **State Grade 3
  Mathematics %** vs **National Mathematics %**.
  - Verified example — Madhya Pradesh: Language MP 66% / National 64%;
    Mathematics MP 62% / National 60%
    (`/tmp/mp_report.txt:225-250`, extracted via `pdftotext -layout` from the live
    PDF fetched 2026-10-04).
- Subsequent pages in the same section break down State-vs-National further by
  Gender, Location, School Management Type (pp. 13+), mirroring the national
  report's structure, each pair of bars again giving Language/Math %.

This section is the single most reliable primary-source location to harvest
per-state Grade 3 Language and Mathematics average percentages, because: (1) it is
structurally identical across all 33+ state PDFs confirmed above, (2) it states both
the state value and the exact matching national value side by side (useful for
sanity-checking extraction), and (3) it is near the top of each report (page ~12),
so downstream parsing does not need to walk the whole document.

## Citations

- National report (PDF): https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf
- Madhya Pradesh state report (PDF, verified example): https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_Madhya%20Pradesh_IND023.pdf
- Punjab state report (PDF): https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_Punjab_IND003.pdf
- Uttar Pradesh state report (PDF): https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_Uttar%20Pradesh_IND009.pdf
- PARAKH Rashtriya Sarvekshan 2024 overview page (navigation only, no state PDF links): https://parakh.ncert.gov.in/prs
- Full state/UT table above — each row's URL tested live, 2026-10-04.

## Gaps / uncertainties

- Could not confirm a working PDF URL for "Daman & Diu" / "Dadra & Nagar Haveli"
  (merged UT since 2020) under codes IND025/IND026 — tried standalone and merged
  names, all 404. This UT may be folded into a different filename not yet guessed,
  or may not have a separately published PARAKH 2024 state report.
  Follow-up: try fetching `https://parakh.ncert.gov.in/reports-publications-scert-progress-tracker`
  or `/foundation-learning-study/reports` (linked from the `/prs` page HTML, not yet
  crawled) which may enumerate all state report links directly and resolve this gap.
- No single "headline" overall Grade 3 national Language/Math % (unsplit by
  subgroup) is printed verbatim in the national report; the 64%/60% figures above
  are inferred from (a) averaging the Boys/Girls or Rural/Urban breakdown bars and
  (b) cross-checked against the "National" bar shown on every state report's
  "Comparison of State Average with National Average" chart (independently
  consistent — e.g., Madhya Pradesh's chart shows National Language 64% /
  Mathematics 60%).
- Mirrors `druid.parakh.ncert.gov.in` and `lms.parakh.ncert.gov.in` surfaced in
  search results use identical `/sites/default/files/2025-07/REPORT_...` paths;
  these were not treated as authoritative (not officially linked/known-canonical)
  and all download links in this report point only at the canonical
  `parakh.ncert.gov.in` host, each independently re-verified with `curl`.
