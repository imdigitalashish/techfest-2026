# Theme 2 (Foundational Learning Outcomes) — dataset source verification notes

> Produced by a research subagent, 2026-10-04 IST. All downloads tested live with
> `curl -L -A "Mozilla/5.0" <url>`. Status/format/size are from the actual response,
> not from page text. "Failure" entries are genuine connection failures observed from
> this sandbox (see network caveat below), not assumptions.

## Network caveat (read first)
From this sandboxed environment, **all `*.nic.in` domains and a few `*.gov.in` domains
timed out or reset the connection** (`curl: (28) Connection timed out` / `curl: (35)
Recv failure: Connection reset by peer`), while sibling domains on the same
ministry/agency (e.g. `parakh.ncert.gov.in`, `udiseplus.gov.in`, `pgi.udiseplus.gov.in`,
`data.gov.in` search pages) responded normally. This looks like an IP/ASN-level
block or geo-fence on specific Indian government hosts rather than the content being
unavailable — **re-test `ncert.nic.in`, `nas.gov.in`, `lgdirectory.gov.in`, and
`censusindia.gov.in` (without `-k`) from a normal residential/India-based network or a
cloud egress IP before concluding they are down.** Do not hard-code "unavailable" into
the architecture based on this alone.

---

## 1. PARAKH Rashtriya Sarvekshan (PRS) 2024 — national diagnostic survey (Grades 3/6/9)

**Primary host:** `parakh.ncert.gov.in` (Drupal site) + `dashboard.parakh.ncert.gov.in` (Next.js dashboard app). Both resolved and loaded successfully — no block observed on these subdomains.

| URL | HTTP | Content-Type | Size | Notes |
|---|---|---|---|---|
| `https://dashboard.parakh.ncert.gov.in/en` | 200 | text/html | 22,920 B | Next.js SPA shell (`en/dashboard/` deep link); real tables render client-side via JS — curl only sees the shell, so this needs a headless browser (Playwright) to extract indicator tables, not raw curl. |
| `https://parakh.ncert.gov.in/prs-reports-2024` | 200 | text/html | 39,310 B | Listing page, Drupal. No direct report links on this exact path; actual PDFs are linked from the `/prs` page (see below). |
| `https://parakh.ncert.gov.in/prs` | 200 | text/html | 47,493 B | **Working list page** with direct PDF links under `/themes/parakh/prs-files/`. |
| `https://parakh.ncert.gov.in/prs-reports-2024-statelist` | **403** | text/html | 40,729 B | Blocked for this UA/no-referer combination — state-wise report listing page returns Forbidden. Likely needs a referer header from `/prs` or a logged-in session; retry with `-e "https://parakh.ncert.gov.in/prs"`. |
| `https://parakh.ncert.gov.in/prs-reports-2024-districtlist` | not tested (linked from dashboard, same pattern as statelist expected) | — | — | Expect same 403 pattern; retest with referer. |

**Confirmed downloadable national PRS 2024 PDFs** (all `HTTP 200`, `application/pdf`, served from `parakh.ncert.gov.in/themes/parakh/prs-files/`):

| File | URL | Size |
|---|---|---|
| Grade 3 national report | `https://parakh.ncert.gov.in/themes/parakh/prs-files/Grade3.pdf` | 815,445 B (~800 KB) |
| Grade 6 national report | `https://parakh.ncert.gov.in/themes/parakh/prs-files/Grade6.pdf` | 684,614 B (~670 KB) |
| Grade 9 national report | `https://parakh.ncert.gov.in/themes/parakh/prs-files/Grade9.pdf` | 669,648 B (~654 KB) |
| Analysis framework | `https://parakh.ncert.gov.in/themes/parakh/prs-files/Analysis_Framework_PARAKH.pdf` | 4,732,651 B (~4.5 MB) |
| Assessment framework | `https://parakh.ncert.gov.in/themes/parakh/prs-files/Assessment_Framework_PARAKH_Rashtriya_Sarvekshan_07-11-2024.pdf` | 7,791,323 B (~7.4 MB) |
| Operational guidelines 2024 | `https://parakh.ncert.gov.in/themes/parakh/prs-files/OPERATIONAL_GUIDELINES2024.pdf` | 6,556,729 B (~6.3 MB) |

- **License/terms:** No explicit license/terms-of-use statement observed on the pages crawled (Drupal site has no visible footer license text in the fetched HTML); treat as "Government of India public report, reuse with attribution" pending explicit confirmation — **check the page footer / `/faq` / `/about-parakh` manually in a browser for an explicit GODL/CC statement before citing a license.**
- **Login/captcha/API key:** None for the PDFs above (direct anonymous GET). The dashboard (`dashboard.parakh.ncert.gov.in`) and state/district list pages may be rate-limited or referer-gated (see 403 above). `board.parakh.ncert.gov.in` and `ta.parakh.ncert.gov.in` are separate login portals for boards/teachers — not needed for public data.
- **Granularity:** National Grade 3/6/9 report PDFs are **national-level** analysis (subject-wise, learning-outcome-wise proficiency bands). State/district-wise report cards exist (linked from the dashboard as `prs-reports-2024-statelist` / `-districtlist`) but those listing pages returned 403 in this test — needs retry with a referer header or a different network.
- **Years:** PRS was conducted in **2024** (survey date referenced as "07-11-2024" in the assessment framework filename, i.e. November 2024 survey window; results/reports dated into early 2026 per event-calendar postings on the Drupal site, e.g. "meeting to discuss major findings PARAKH Rashtriya Sarvekshan 2024").
- **Key fields (from framework PDFs, by title/structure):** subject-wise mean scores, proficiency levels/bands per Learning Outcome (LO), analysis framework maps items to NCF/NEP competencies — exact field names need extraction from inside the PDFs (not yet parsed in this pass; recommend a follow-up task to OCR/parse `Grade3.pdf`/`Grade6.pdf`/`Grade9.pdf` tables).
- **Gap:** Could not directly confirm existence/URL of a state-level or district-level PRS 2024 report card at public anonymous access (403 encountered). The PARAKH NAS dashboard link `http://parakh.ncert.gov.in/dashboard/NAS2021#/` is for the **2021** NAS cycle, a separate dashboard from PRS 2024.

---

## 2. ASER 2024 — national citizen-led learning assessment report

**Primary host:** `asercentre.org` (and `www.asercentre.org`, both resolve/redirect to each other). No block observed.

| URL | HTTP | Content-Type | Size |
|---|---|---|---|
| `https://www.asercentre.org/report/aser-2024/` | 200 | text/html | 249,072 B |
| `https://asercentre.org/aser-2024/` | 200 | text/html | 147,440 B |
| **`https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf`** | **200** | **application/pdf** | **10,879,964 B (~10.4 MB)** — this is the **full ASER 2024 national report**, confirmed downloadable anonymously, no login/captcha. |
| `https://asercentre.org/wp-content/uploads/2022/12/ASER-2024-National-findings.pdf` | 200 | application/pdf | 37,714 B (short national findings summary) |

Other PDFs discovered on the report page (not individually download-tested, but same host/path pattern as the two confirmed above, so expected to work the same way):
- `ASER-2024-All-India-ppt-Jan-27-11am.pdf` (slide deck)
- `ASER-2024-assessment-tasks.pdf` (the Std III reading/arithmetic test tools)
- `ASER-2024-survey-process-summary.pdf`
- `ASER_2024_Final-Report_13_2_24-1.pdf` → **this is the one containing the Std III/V/VIII state-wise reading & arithmetic tables** (standard ASER report structure: All-India + state-wise tables by grade and task level).
- State 6-pagers for several states/languages (e.g. `ASER-2024_Gujarat_6pager_Gujarati.pdf`, `ASER-2024_Karnataka_6pager_Kannada-3-8.pdf`, etc.) — state-level 6-page summaries.
- District/divisional estimate PDFs per state, e.g. `Andhra-Prades_District-Estimates.pdf`, `Andhra-Pradesh_Divisional-estimates.pdf`, `Assam_District-Estimates.pdf`, `Bihar_District-Estimates.pdf`, `Chhattisgarh_District-Estimates.pdf`, and `Annexure_1.pdf` … `Annexure_13.pdf` (methodology/sampling annexures). **District-level estimates exist as separate PDFs per state** — confirms ASER 2024 does publish sub-state granularity, contrary to assuming only state-level.
- Note the inconsistent WordPress upload path (`/wp-content/uploads/2022/12/...` even though these are 2024 files) — this is just the CMS's fixed folder, not a dating error.

- **License/terms:** ASER Centre reports are typically released for public/educational use with attribution (Pratham/ASER Centre branding); **no explicit license text parsed from the fetched HTML in this pass** — recommend checking the site's "Terms of Use"/footer directly for exact wording before citing a specific license (CC-BY vs. "all rights reserved, free to download").
- **Login/captcha/API key:** None. Fully open download.
- **Granularity:** All-India, state-wise, and (confirmed via filenames) **district/divisional estimates** for several large states.
- **Years:** Survey year **2024** (ASER resumed full "basic" survey in 2024 after 2022's partial/limited rounds).
- **Key fields:** Std III/V/VIII enrolment status, reading level (nothing/letter/word/Std-I-text/Std-II-text), arithmetic level (nothing/recognize numbers/subtraction/division), school type (government/private), out-of-school rates by age — per standard ASER tool structure (confirmed from the existence of `ASER-2024-assessment-tasks.pdf` as the test instrument).

---

## 3. UDISE+ / data.gov.in — school education indicators

| URL | HTTP | Content-Type | Size | Notes |
|---|---|---|---|---|
| `https://udiseplus.gov.in/` | 200 | text/html | 88,965 B | Angular/Vue SPA shell only (`chunk-LM7JK4TJ.js`, `styles-*.css`); **no static report links in raw HTML** — report cards and dashboards require JS execution (and in many cases state/district drill-down clicks) to reach download buttons. A headless-browser pass (Playwright) is required to enumerate actual report-card PDF/Excel URLs; curl alone cannot discover them. |
| `https://data.gov.in/search/site/udise` | 200 | text/html | 13,178 B | Search page loads; returned a mostly-empty/placeholder result set in the raw HTML (typical for JS-rendered search-results on data.gov.in — the result list itself is client-rendered). |
| `https://www.data.gov.in/search?title=UDISE` | 200 | text/html | 840,219 B | This alternate search path returned a **much larger** HTML payload (840 KB vs 13 KB), suggesting more content was server-rendered here — worth parsing directly for dataset resource IDs/links in a follow-up pass (not done in this run). |
| `https://data.gov.in/` (root) | **000 (timeout)** | — | — | Root domain timed out repeatedly in this sandbox even though `/search/...` sub-paths on the same host resolved — inconsistent connectivity, re-test from another network. |
| `https://data.gov.in/apis` | **000 (timeout)** | — | — | Could not confirm the OGD (Open Government Data) platform API/key-registration page in this pass. **data.gov.in's OGD API is documented elsewhere to require a free API key (`data.gov.in/user/me` → generate key) for `api.data.gov.in` resource endpoints** — not independently re-verified here due to timeout; treat as "API key required" pending confirmation. |

- **Login/captcha/API key:** UDISE+ public summary report cards are stated (by secondary sources) to be downloadable without login from the portal's Reports section, but the raw SPA shell gave no direct evidence either way in this pass — needs a browser-driven check. Bulk/school-level microdata export requires authorized login. data.gov.in's REST API (`api.data.gov.in`) requires a free registered API key; anonymous bulk CSV/XLSX download of individual datasets from the catalog pages does not need a key.
- **Granularity:** UDISE+ in principle publishes School → Block → District → State → National indicators (enrolment, PTR, infrastructure, dropout). Not independently confirmed at school/granular level in this pass because the SPA blocked static crawling.
- **Years:** UDISE+ report cards are published annually (recent known cycles: 2020-21, 2021-22, 2022-23); current latest cycle not confirmed in this pass — recommend a browser-driven check of `udiseplus.gov.in` reports section for the latest year available.
- **Gap/Follow-up needed:** This source needs a Playwright-driven crawl (not curl) to extract actual indicator tables/PDF links, since both the portal and PGI tool are JS SPAs.

---

## 4. NAS 2021 / PGI / PGI-D

| URL | HTTP | Notes |
|---|---|---|
| `https://nas.gov.in/result.html` | **000 (timeout, 20s)** | `nas.gov.in` resolved to `164.100.252.80` (confirmed via `curl -v`) but connection timed out — consistent with the broader pattern of certain Indian gov IP ranges being unreachable from this sandbox. |
| `https://ncert.nic.in/DRC_2021.php` | **000 (connection reset by peer, TLS handshake stage)** | `ncert.nic.in` resolved to `164.100.166.133`; TLS client-hello sent, then `Recv failure: Connection reset by peer` — looks like an active reset, not just a routing timeout. All `*.nic.in` paths tested in this session failed the same way. |
| `https://ncert.nic.in/pdf/NAS/DRC_report.pdf` | **000 (timeout)** | Same `.nic.in` block pattern. |
| `https://ncert.nic.in/pdf/NAS/NAS21_NRC.pdf` | **000 (timeout)** | Same. |
| `https://ncert.nic.in/pdf/NAS/NAS_2021_Technical-Report-2024.pdf` | not completed (killed after 30s hang) | Same domain, same expected failure. |
| `https://pgi.udiseplus.gov.in/` | **200** | `text/html`, 1,742 B — **this one worked** (different host than `ncert.nic.in`, served by Apache, `Last-Modified: Fri, 31 Jul 2026`). It's an Angular SPA shell (`#/home` route) — static HTML has no direct report links; needs a browser pass to reach PGI/PGI-D state and district report downloads. |
| `https://parakh.ncert.gov.in/nas-dashboard` | 200 | text/html, 43,224 B | **Useful discovery:** this Drupal page (on the *working* `parakh.ncert.gov.in` host, not `ncert.nic.in`) links out to the actual NAS 2021 PDF reports on `ncert.nic.in` — i.e. the source documents exist and are indexed, but are hosted on the blocked domain. Links found: `https://ncert.nic.in/pdf/NAS/DRC_report.pdf` (District Report Cards), `https://ncert.nic.in/pdf/NAS/NAS21_NRC.pdf` (National Report Card), `https://ncert.nic.in/pdf/NAS/NAS_2021_Technical-Report-2024.pdf` (technical report, re-released/updated 2024), `https://ncert.nic.in/pdf/NAS/WithReleaseDate_NPPTL.pdf`, `https://ncert.nic.in/pdf/NAS/nas_report_02_02_2024.pdf`. Also an NAS2021-specific dashboard link: `http://parakh.ncert.gov.in/dashboard/NAS2021#/` (not separately tested; likely same Next.js SPA pattern as the PRS dashboard). |

- **Conclusion:** NAS 2021 national/district report cards and PGI/PGI-D exist and are indexed (titles/URLs confirmed via the working PARAKH Drupal page), but the file-serving domain (`ncert.nic.in`) and `nas.gov.in` are **unreachable from this sandbox** — this is almost certainly a sandbox/network restriction (TLS reset + timeout pattern on `.nic.in` specifically), not evidence the files don't exist or require auth. **Re-test these exact URLs from an unrestricted network before writing them off:**
  - `https://ncert.nic.in/pdf/NAS/DRC_report.pdf` (District Report Cards, NAS 2021)
  - `https://ncert.nic.in/pdf/NAS/NAS21_NRC.pdf` (National Report Card, NAS 2021)
  - `https://ncert.nic.in/pdf/NAS/NAS_2021_Technical-Report-2024.pdf`
  - `https://pgi.udiseplus.gov.in/#/home` (PGI/PGI-D — needs Playwright, SPA)
- **Login/captcha/API key:** None apparent from URL patterns (direct PDF paths); PGI portal is a public SPA with no visible login wall on its root shell.
- **Granularity:** NAS 2021 = district report cards (hence "DRC") + national report card; PGI-D = district-level grading index; PGI = state/UT-level.
- **Years:** NAS last conducted **2021** (no NAS cycle since; PRS 2024 appears to have effectively superseded/replaced NAS as the national large-scale assessment — worth noting as a decision-relevant fact for the architecture: **the policy pipeline shifted from NAS → PRS between 2021 and 2024**, so any "decision-support system" design should treat PRS 2024 as current and NAS 2021 as historical baseline/trend data only).

---

## 5. LGD (Local Government Directory) / geography codes

| URL | HTTP | Notes |
|---|---|---|
| `https://lgdirectory.gov.in/` | **000 (timeout, 20s)** | Resolved to `164.100.128.239`, TLS client-hello sent, then timed out — same `.gov.in`-specific-host blocking pattern as `nas.gov.in`. |
| `https://lgdirectory.gov.in/downloadDirectory.do` | **000 (timeout)** | Same. |
| `https://india-lgd-index-api.vercel.app/v1/states` | **200** | `application/json`, 4,713 B. **Confirmed working, keyless, no auth.** Returned full list of States/UTs with LGD `code`, `name`, `name_local`, `census_2001_code`, `census_2011_code` fields (e.g. `{"code":"28","name":"Andhra Pradesh",...}`). This is a **third-party community mirror** of the official LGD codes, not the primary source — cite it as a fallback/mirror only, and note in the architecture that primary `lgdirectory.gov.in` should be re-verified from a normal network. |
| `https://ckandev.indiadataportal.com/dataset/a7419751-ac37-46ad-b938-638cda7b7b60/resource/cb81a7a4-a3bc-4962-a1eb-838a1db5bfdb/download/villages-lgd-codes.csv` | **200** | `text/csv`, 32,229 B. Works, anonymous, no key. Note: 32 KB is far too small to be the full all-India village-level LGD list (~650,000+ villages) — this resource is likely a **sample/truncated extract or a different aggregation level** (possibly just a metadata/column-schema file or a small subset). Needs manual inspection of the CSV content before relying on it as the full village master.|

- **License/terms:** LGD data is issued under the Government Open Data License - India (GODL) per secondary sources; not independently confirmed from the primary `lgdirectory.gov.in` site in this pass due to the block.
- **Granularity:** State → District → Sub-district (Tehsil/Taluk) → Block → Village/Town → Urban Local Body, with unique LGD codes at each level — this is the standard geography backbone needed to join UDISE+/PARAKH/ASER/Census data across sources.
- **Login/captcha/API key:** None for either the official bulk XLS download (per secondary sources) or the two working mirrors above.
- **Recommendation:** Use LGD codes as the canonical geographic join key across all four education datasets (UDISE+, PARAKH, ASER, NAS/PGI) since each publishes at different sub-national granularities; re-verify `lgdirectory.gov.in` bulk download from a non-restricted network since it's the authoritative source and the mirrors found here are not guaranteed complete or current.

---

## 6. Census 2011 PCA (Primary Census Abstract) / SHRUG

| URL | HTTP | Notes |
|---|---|---|
| `https://censusindia.gov.in/nada/index.php/home` | 000 (timeout) plain; **200 with `-k`** (`text/html`, 29,999 B) | TLS handshake fails with "SSL certificate problem: unable to get local issuer certificate" on a plain request — i.e. **the server's certificate chain is incomplete/non-standard**, not a network block (distinct failure mode from the `.nic.in` cases above). Works fine once `-k` (insecure, skip cert verification) is added. In production code, this means you may need to pin/add the correct intermediate CA or accept that this government NADA (census microdata catalog) instance has a cert misconfiguration — **do not silently use `-k`/`verify=False` in a real pipeline; instead fetch and install the correct CA chain, or proxy through a service that already trusts it.** |
| `https://censusindia.gov.in/nada/index.php/catalog/4256/download/6389` (direct PCA state/district XLSX) | **000 (timeout, even with `-k`)** | Catalog page loads but the specific resource-download endpoint did not respond within 25s even bypassing the cert issue — could be an expired/renumbered catalog+resource ID (NADA catalog IDs can change between census portal revisions) or a slow backend. **Needs re-verification with the current catalog ID** by browsing `https://censusindia.gov.in/nada/index.php/catalog` for "Primary Census Abstract" and copying the live download link rather than reusing this possibly-stale ID. |
| `https://www.devdatalab.org/shrug_download` | 200 | `text/html`, 13,032 B. SHRUG (Socioeconomic High-resolution Rural-Urban Geographic) download page loads; the actual file links are JS-templated (`href="${row['primary_download']}"`) so static curl can't enumerate individual file URLs — **confirmed, though, that SHRUG's real data host is Harvard Dataverse**, linked from this page as `https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DPESAK`. |
| `https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DPESAK` | **202** | `text/html`, 0 B body. HTTP 202 (Accepted) with empty body from a plain curl GET is typical of Dataverse's JS-rendered dataset page (it likely returns a redirect/placeholder to clients without a full browser, or is rate-limiting). Needs a browser-driven fetch or the Dataverse API (`https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/DPESAK`) to actually list/download the files anonymously. |
| `https://www.devdatalab.org/shrug` | 200 | `text/html`, 29,272 B — SHRUG landing/about page, loads fine. |
| `https://github.com/devdatalab/shrug-public` | linked, not separately curl-tested | Public GitHub mirror of SHRUG documentation/code (confirmed to exist via link on the download page) — likely the fastest path to understand SHRUG's Census-2011-linked keys (`shrid`) without fighting the Dataverse UI. |

- **License/terms:** SHRUG is explicitly licensed **CC BY-NC-SA 4.0** — confirmed directly from the page HTML: `href="http://creativecommons.org/licenses/by-nc-sa/4.0/"` on `devdatalab.org/shrug_download`. This is a **non-commercial** license — relevant for the architecture/deliverable, since a Techfest solution proposing commercial deployment would need to flag this constraint or use SHRUG only for research/analysis, not as a redistributed commercial data layer.
- **Granularity:** SHRUG provides a village/town-level (`shrid`) consistent key bridging Census 2001/2011, Economic Census, and other datasets — exactly the kind of geographic harmonization layer useful for joining UDISE+/PARAKH school locations to Census socio-economic covariates (e.g. for identifying "underserved group" per the challenge's problem statement).
- **Login/captcha/API key:** Harvard Dataverse normally allows anonymous download of public (non-restricted) files; some SHRUG components may require a quick form/email signup (a Google Form link was present on the devdatalab site: `https://docs.google.com/forms/d/e/1FAIpQLSd1zLWK-s24O7OeNh5oFdNQoBvvadP3sxw-aBxR-HjnlsRZbw/viewform`) — likely for a mailing list / "how are you using this" survey, not a hard gate; not independently confirmed as mandatory.
- **Years:** SHRUG's primary vintage is **Census 2001 and 2011** PCA/Economic Census data, consistent with the brief's ask for "Census 2011 PCA/SHRUG."
- **Gap:** Could not directly confirm download of the official Census 2011 PCA state/district Excel file from `censusindia.gov.in` due to the cert issue + stale-looking catalog ID; **SHRUG is the more reliable/already-tested path to Census 2011 PCA data for this project** given the plain `censusindia.gov.in` NADA portal's TLS and endpoint issues in this sandbox.

---

## Summary table (quick reference)

| Dataset | Primary URL | Status | Format | License | Auth needed |
|---|---|---|---|---|---|
| PARAKH PRS 2024 Grade 3/6/9 national reports | `parakh.ncert.gov.in/themes/parakh/prs-files/Grade{3,6,9}.pdf` | ✅ 200, confirmed | PDF (~700-820 KB each) | Not stated; assume GoI public report | None |
| PARAKH assessment/analysis frameworks | same host, `prs-files/*.pdf` | ✅ 200, confirmed | PDF (4.5–7.8 MB) | Not stated | None |
| PARAKH state/district PRS report lists | `parakh.ncert.gov.in/prs-reports-2024-{state,district}list` | ❌ 403 | — | — | Possibly referer/session-gated; retry with referer header |
| PARAKH dashboard (interactive) | `dashboard.parakh.ncert.gov.in/en` | ⚠️ 200 shell only | JS SPA (Next.js) | — | None visible, but needs browser automation |
| ASER 2024 full national report | `asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf` | ✅ 200, confirmed | PDF (10.4 MB) | Not explicit; public download | None |
| ASER 2024 state 6-pagers / district estimates | same host pattern | linked, not individually tested | PDF | Not explicit | None expected |
| UDISE+ portal | `udiseplus.gov.in` | ⚠️ 200 shell only | JS SPA | Unclear | None for shell; login likely for microdata export |
| data.gov.in UDISE search | `data.gov.in/search/site/udise`, `www.data.gov.in/search?title=UDISE` | ✅ 200 (second one much richer payload) | HTML (JS-rendered results) | GODL (typical for data.gov.in, not reconfirmed here) | API key needed for `api.data.gov.in` REST; browsing/download of catalog entries typically free |
| NAS 2021 reports | `ncert.nic.in/pdf/NAS/*.pdf`, `nas.gov.in/result.html` | ❌ 000 (blocked from this sandbox) | PDF (unconfirmed size) | Not confirmed | Unconfirmed; URLs discovered via working `parakh.ncert.gov.in/nas-dashboard` page |
| PGI / PGI-D | `pgi.udiseplus.gov.in` | ⚠️ 200 shell only | JS SPA | Unclear | None visible |
| LGD codes (official) | `lgdirectory.gov.in` | ❌ 000 (blocked) | XLS (unconfirmed) | GODL (per secondary sources) | None expected |
| LGD codes (community mirror) | `india-lgd-index-api.vercel.app/v1/states` | ✅ 200, confirmed | JSON | Unclear (community project) | None |
| LGD codes (India Data Portal CSV) | `ckandev.indiadataportal.com/.../villages-lgd-codes.csv` | ✅ 200, confirmed but suspiciously small (32 KB) | CSV | Unclear | None |
| Census 2011 PCA (official NADA) | `censusindia.gov.in/nada/...` | ⚠️ catalog loads only with `-k` (cert issue); specific download endpoint timed out | XLSX expected | GoI, not reconfirmed | None expected, but cert chain issue |
| SHRUG (Census 2011-linked village panel) | `devdatalab.org/shrug_download` → Harvard Dataverse | ✅ page 200; Dataverse dataset page returned 202/empty to plain curl | CSV/DTA bundles on Dataverse | **CC BY-NC-SA 4.0 (confirmed from page HTML)** | None expected; may need Dataverse API or browser for actual file list |

---

## Recommended follow-ups (not performed in this pass, flagged for the lead)
1. Re-test all `❌ 000` rows above (`ncert.nic.in`, `nas.gov.in`, `lgdirectory.gov.in`, plain `censusindia.gov.in`) from a non-sandboxed/India-region network — the failure signatures (TLS reset vs. timeout vs. cert-chain) suggest sandbox/network restriction, not genuine unavailability.
2. Use Playwright (not curl) against `udiseplus.gov.in`, `dashboard.parakh.ncert.gov.in`, and `pgi.udiseplus.gov.in` to enumerate the actual report/indicator download links behind their JS SPAs.
3. Retry `https://parakh.ncert.gov.in/prs-reports-2024-statelist` and `-districtlist` with a `Referer: https://parakh.ncert.gov.in/prs` header (or with cookies from a prior page load) to get past the 403.
4. Query the Harvard Dataverse REST API directly (`GET https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/DPESAK`) to get a JSON file manifest for SHRUG instead of the JS-rendered HTML page.
5. Manually open `https://censusindia.gov.in/nada/index.php/catalog` in a browser to find the current (non-stale) catalog/resource ID for the India state+district PCA Excel file, since the one surfaced by web search (`catalog/4256/download/6389`) may be outdated.
6. Confirm whether `api.data.gov.in` requires a registered API key for the UDISE-related resources identified via `www.data.gov.in/search?title=UDISE` (840 KB response — worth parsing for exact dataset/resource IDs in a follow-up).
