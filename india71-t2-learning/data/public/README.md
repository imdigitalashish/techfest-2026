# Public data extracts

## `aser2024_state_std3.csv`

- Source: ASER 2024 rural report, https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf
- Access date: 2026-10-04.
- Pages: All-India school-type tables on report p.19; state government-school tables on report pp.52-53.
- Extraction command: `python3 scripts/extract_aser2024.py`.
- Caveat: ASER is a rural household oral assessment; the state rows here are Std III government-school children for the two extracted indicators.

## `parakh2024_grade3_state.csv`

- Source: PARAKH Rashtriya Sarvekshan 2024 national report, https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf, and official state report cards under `https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_<StateName>_IND<code>.pdf`.
- Access date: 2026-10-04.
- Pages: Grade 3 “Comparison of State Average with National Average Across Subjects” page in each state PDF; `source_page` records the PDF page parsed by `pdftotext`.
- Extraction command: `python3 scripts/extract_parakh2024_state.py`.
- Caveat: PARAKH is a school-based written assessment reporting average percent correct. The script records Grade 3 Language and Mathematics state averages only; Dadra and Nagar Haveli and Daman and Diu was not included because a working official state-report URL was not found under the tested code/name patterns.

## `udise2425_state.csv`

- Source: UDISE+ 2024-25 existing-schools booklet, https://dashboard.udiseplus.gov.in/report-new-v.11-demo2025/static/media/UDISE+2024_25_Booklet_existing.118ba29d4773e6372f72.pdf
- Access date: 2026-10-04.
- Pages: Table 2.2, p.32, “State wise highlights of the UDISE+ 2024-25 data: Schools, Enrolments and Teachers”.
- Extraction command: `python3 scripts/extract_udise2425_state.py`.
- Caveat: These are all-management UDISE+ administrative aggregates. The analysis uses PTR and single-teacher-school share as state-level covariates, not as causal estimates.
