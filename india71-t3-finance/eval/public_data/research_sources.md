# Public data sources — India financial inclusion (d1 fetcher notes)

Scope: verify official/primary URLs + key figures for the datasets this theme leans on. Status flags:
**VERIFIED-LIVE** = fetched directly this session and content matches claim. **VERIFIED-ARCHIVE** = confirmed via Wayback Machine snapshot (live site blocked the fetch tool, likely bot/JS protection — browser access should work fine for a human). **REPORTED** = corroborated only via secondary/news/search-engine summary, not independently fetched this session — re-verify before citing numbers in the proposal.

Caveat on all figures below: PMJDY/DBT/NPCI dashboards update continuously and some search results returned dates in 2026 that may reflect the assistant's current-date context rather than confirmed publication dates. **Pin every number actually used in the deliverable to a dated screenshot/PDF, not to this file's prose.**

---

## 1. PMJDY account & dormancy data (DFS, Ministry of Finance)

- **Primary dashboard:** https://pmjdy.gov.in/account — state/bank-wise PMJDY progress report (accounts, deposits, RuPay cards, gender split, rural/urban split). Site resolves and serves content (confirmed via Wayback snapshot `web.archive.org/web/20260131002527/https://www.pmjdy.gov.in/account`, page header: "Content... managed and owned by Mission Office, Department of Financial Services, Ministry of Finance"). **VERIFIED-ARCHIVE** — direct `web_fetch` to `pmjdy.gov.in` and `www.pmjdy.gov.in` failed with a transport-level error from this sandbox (likely TLS/geo filtering on the tool side, not the site itself); fetch again with a normal browser or `curl` from an unrestricted host.
- **Archive reports:** https://pmjdy.gov.in/ArchiveReports — historical weekly/monthly progress PDFs, useful for a time series. **REPORTED** (found via search, not fetched).
- **Headline figures (REPORTED, cross-check against the dashboard before citing):**
  - ~59 crore total accounts, ~₹3.15–3.17 lakh crore deposits (mid/late-2026 references in search results — note these are later than the brief's "56 crore" figure, so pull the as-of-date shown on the dashboard itself for the proposal).
  - Gender split cited as ~32.9 crore women-held vs ~26.1 crore men-held accounts; ~55.7% women share in another snapshot — the two shares are inconsistent across sources, reconcile against the live dashboard.
  - Zero-balance accounts: ~5.72 crore.
  - **Inoperative/dormant accounts:** multiple figures depending on date — 13.04 crore of 56.04 crore (~23%, reply to Parliament referencing July 31, 2025 data, via Economic Times/Business Standard coverage of a Ministry of Finance reply) and a later 15.09–15.36 crore of ~57 crore (~26%), per The Hindu's coverage of an RTI reply. **Do not average these** — pick the single most recent official reply and cite its date explicitly.
  - State breakdown (REPORTED, unverified primary): UP, Bihar, MP, WB, Maharashtra carry the largest absolute counts of both total and inoperative accounts — directionally consistent with population/PMJDY-penetration but needs the primary table.

- **Primary-source Parliament replies (best evidence tier for the "~1/4 dormant" claim):**
  - Lok Sabha unstarred question reply (Ministry of Finance, DFS), PDF hosted at `sansad.in`: https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU1333_viWPuz.pdf?source=pqals — **NOT FETCHED** (transport error from this sandbox; `sansad.in` likely needs a standard browser/TLS stack). This is the correct document type (official Parliament Q&A annexure) to cite for state-wise inoperative-account counts — retry the fetch outside this tool, or request a teammate to download and drop the PDF into `.data/`.
  - Rajya Sabha unstarred question reply, PDF also mirrored on PMJDY's own site: https://pmjdy.gov.in/files/rs_2022/2024/RSUQ-361-FEB-6.pdf and the sansad.in original https://www.sansad.in/getFile/annex/263/AU361.pdf?source=pqars — **REPORTED**, not fetched. Same retry note applies.
  - Secondary coverage corroborating the Parliament replies: The Hindu, "Every fourth Jan Dhan account inoperative; 5.72 crore have zero balance" (RTI-based) — https://www.thehindu.com/news/national/every-fourth-jan-dhan-account-inoperative-572-crore-have-zero-balance-rti/article71434658.ece; The Hindu BusinessLine, "Over 23% Jan Dhan accounts inoperative, FinMin data show" — https://www.thehindubusinessline.com/economy/over-23-jan-dhan-accounts-inoperative-finmin-data-show/article69947255.ece; Economic Times, "23% of total 56.04 crore PM Jan Dhan accounts inoperative" — https://economictimes.indiatimes.com/industry/banking/finance/banking/23-of-total-56-04-crore-pm-jan-dhan-accounts-inoperative/articleshow/123361368.cms; CNBC-TV18, "Over 15 crore Jan Dhan accounts inactive, says Finance Ministry in Lok Sabha" — https://www.cnbctv18.com/economy/over-15-crore-jan-dhan-pmjdy-accounts-inactive-finance-ministry-in-lok-sabha-ws-l-19784416.htm. All **REPORTED**, all pointing back to the same underlying Parliament-reply primary source above.

---

## 2. DBT Bharat — state-wise transfers

- **Primary dashboard:** https://dbtbharat.gov.in/ — **VERIFIED-LIVE** (fetched directly; returned a minimal placeholder body "Modal body text goes here", also confirmed via Wayback `web.archive.org/web/20260117180330/https://www.dbtbharat.gov.in/`). This means the dashboard is a JS-rendered single-page app — the `web_fetch` tool only sees the shell; the actual scheme/state tables are loaded client-side and need a real browser (or the underlying API endpoints) to extract data. A candidate state-level endpoint was probed — https://dbtbharat.gov.in/state-ut-wise-public — and returned **404**, so that exact path is wrong; the correct API routes need to be found via browser dev-tools network tab.
- **Legacy/alternate dashboard (older DBT data, pre-rebrand):** https://dbtdacfw.gov.in/DBTPrevious/DashboardScheme.aspx?Type=State — surfaced in search results as a state-wise scheme dashboard; **REPORTED**, not fetched — worth checking as a fallback if the new SPA can't be scraped in time.
- **Illustrative state figures (REPORTED only, source unclear/unverified, treat as placeholder):** a search-engine summary returned a beneficiaries/fund-transferred table by state (UP ~2.18 crore beneficiaries / ~₹4,357.6 crore; Maharashtra, MP, Bihar, Rajasthan, etc. following) but could not be traced to a specific scheme, date range, or page — **do not use these numbers without confirming on the live dashboard with a browser**, since the aggregation (which scheme? which year? cumulative or annual?) is unknown.
- **Recommended path to real data:** open https://dbtbharat.gov.in/ in an actual browser (Playwright), find the "State-wise" or "Mission-wise" report view, inspect the XHR/API calls it fires (likely a `.aspx` or JSON API under a `/api/` or `/Report` path), and hit that endpoint directly for CSV/JSON state totals by scheme and year.

---

## 3. RBI Financial Inclusion Index (FI-Index)

- **Home/definition page:** https://www.rbi.org.in (FI-Index is published via the Press Releases section, not a standing dashboard) — RBI's own site returned transport-level failures for several specific press-release URLs tried this session (`prid=59727` resolved to an unrelated VRR auction notice, confirming `prid` numbers must be looked up fresh each time rather than guessed/incremented).
- **Search-reported, needs primary verification:**
  - FI-Index for March 2024 = 64.2 (up from 60.1 in March 2023), attributed to a press release at `rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=57112` — **REPORTED**, fetch failed (transport error).
  - FI-Index for March 2025 = 67.0 (up from 64.2), attributed to `prid=58413` — **REPORTED**, fetch of this exact URL failed (transport error) both as `www.rbi.org.in` and bare `rbi.org.in`.
  - Methodology (consistent across secondary sources and matches the original 2021 RBI press release establishing the index): composite 0–100 score, no base year, three sub-indices — **Access 35%**, **Usage 45%**, **Quality 20%** — built from ~97 indicators across banking, investment, insurance, postal, pension data; inputs sourced from RBI, other regulators (SEBI/IRDAI/PFRDA), and NPCI. Original announcement PDF (2021), hosted by a trade body mirror: https://fidcindia.org.in/wp-content/uploads/2021/08/RBI-FINANCIAL-INCLUSION-INDEX-PRESS-RELEASE-17-08-21.pdf — **REPORTED** (secondary mirror of a primary RBI release; not fetched this session, but this is the right document to track down and cite directly, ideally from rbi.org.in itself).
  - Secondary analysis pages corroborating the FY24/FY25 trend: Drishti IAS — https://www.drishtiias.com/daily-updates/daily-news-analysis/rbi-financial-inclusion-index; Excelbanking — https://excelbanking.co.in/financial-inclusion-index-march-2024/. Both **REPORTED**, useful only as a pointer, not as citations in the final deliverable.
- **Action item:** the RBI site appears reachable (`BS_PressReleaseDisplay.aspx?prid=56364` loaded fine with real but unrelated content), so the issue is guessing wrong `prid` values, not a site-wide block. Browse RBI's Press Releases search/listing page directly and search "Financial Inclusion Index" to get the correct current `prid` for both the FY24 and FY25 releases, then re-fetch.

---

## 4. NPCI — UPI / AePS statistics

- **Attempted primary pages**, both blocked by the fetch tool with **HTTP 403** (bot-protection, not a dead link): https://www.npci.org.in/statistics/transaction-statistics and https://www.npci.org.in/what-we-do/upi/product-statistics. A Wayback lookup for an UPI-statistics path (`/statistics/upi-statistics`) returned 404 — wrong exact path, not proof the page doesn't exist elsewhere on the site.
- **Status: NOT VERIFIED THIS SESSION.** NPCI's statistics are known (from general knowledge, not fetched) to live under npci.org.in's "Statistics" or "What We Do → UPI/AePS" navigation, typically as downloadable month-wise Excel/CSV files (UPI volume & value, AePS transaction counts). Because the tool was blocked by a 403, this needs a real browser fetch (Playwright) or a direct `curl` with a standard User-Agent header from an unrestricted environment — the site is very likely just filtering the automated fetch tool's request signature.
- **No AePS-specific figures or URLs were successfully corroborated this session** — a targeted search for "NPCI AePS statistics monthly transactions page" returned no relevant results. This is a gap: find the exact AePS statistics page via manual browser navigation from npci.org.in's top nav.

---

## 5. NFHS-5 (2019–21) — bank-account use & covariates

- **Primary report (IIPS):** https://iipsindia.ac.in/sites/default/files/NFHS-5%20India%20Report%20Volume%20I.pdf — India national report, Volume I. **REPORTED** (found via search, not fetched this session — large PDF, fetch directly when extracting specific tables).
- **Fact sheets (IIPS/rchiips.org):** http://rchiips.org/nfhs/NFHS-5_FCTS/NFHS-5%20India%20and%20State%20Factsheet.pdf — national + state-level summary indicators including the key metric **"Women age 15–49 who have a bank or savings account that they themselves use (%)"**. **REPORTED**.
- **NFHS official portal:** https://www.nfhsiips.in/nfhsuser/publication.php (and https://rchiips.org/nfhs/ as the broader IIPS/MoHFW microsite) — lists all publications including state reports and district-level factsheets where applicable. **REPORTED**.
- **Where to find the indicator in the main report:** per secondary guidance, it appears in the Women's Empowerment chapter, typically a table numbered around "13.1" in the full report (table numbering should be confirmed directly in the PDF, not assumed from a search summary).
- **Microdata / unit-level data access:** NFHS-5 unit-level data (for covariate modelling, e.g. linking bank-account-use to household wealth quintile, education, caste/religion, rural-urban) requires registration via **the DHS Program** (ICF International, which fields NFHS under India's MoHFW): https://dhsprogram.com/data/dataset/India_Standard-DHS_2019.cfm — direct `web_fetch` to `dhsprogram.com` failed with a transport-level error this session (DNS/TLS); retry with a standard browser, and note DHS microdata requires a free registered-researcher account and a stated analysis purpose — it is not an instant anonymous download.
- **Secondary/derived tabulations (lower trust, convenience only):** data.gov.in's CKAN mirror — https://data.opencity.in/dataset/national-family-health-survey-nfhs-5-2019-21 and a community dataset at https://data.world/adiwakd/national-family-health-survey-nfhs-5 — **REPORTED**, use only to sanity-check numbers already sourced from IIPS/DHS, never as the primary citation in the deliverable.

---

## 6. World Bank Global Findex

- **Primary portal:** https://globalfindex.worldbank.org/ — **VERIFIED-LIVE**, but the fetch tool was redirected to https://www.worldbank.org/en/publication/globalfindex, which served a short landing-page summary rather than the interactive data tool itself (the interactive visualizations/download-data UI is JS-driven and wasn't captured by this fetch).
- **Key facts confirmed from the fetched landing page:** Global Findex is "the world's only demand-side survey on financial inclusion," running since 2011; the **2025 edition** is the latest, and newly introduces a "Digital Connectivity Tracker" measuring mobile-technology access/use alongside financial inclusion. Funding partners: Gates Foundation and Mastercard Foundation.
- **For India-specific figures (account ownership %, digital-payment usage %, gender gap, inactive-account share):** use the portal's "Download data" / country-profile section — not captured by this fetch since it's behind client-side rendering. Recommend a Playwright browser session against globalfindex.worldbank.org to pull the India row (or the bulk Excel/CSV download, which is the Global Findex's standard distribution format across past rounds — 2011/2014/2017/2021/2025).
- **Known risk:** earlier Findex rounds (2021 and before) are the ones most likely to have clean India time-series comparators; confirm the 2025 edition's India microdata/aggregate release timing (a full country-level data refresh sometimes lags the global launch) before building a before/after narrative.

---

## 7. Census of India 2011 — household banking-services access

- **Status: largely blocked this session.** https://censusindia.gov.in/census.website/data/census-tables returned an empty client-rendered search shell ("Searching, please wait... No matching results"), confirming the modern censusindia.gov.in portal is a JS SPA that the fetch tool cannot execute. A second attempt at https://censusindia.gov.in/nada/index.php/catalog/central (the NADA microdata catalog) timed out entirely.
- **Correct document family (per search, REPORTED only):** household-level banking-services access is captured in the **2011 Houselisting and Housing Census** (not the Primary Census Abstract, which covers population/literacy/work, not banking). The relevant table series is typically labelled "Household Amenities and Assets" and includes a household-level indicator for availing banking services, downloadable by state/district/village as Excel files.
- **Candidate entry points to retry with a browser:**
  - https://censusindia.gov.in/census.website/data/census-tables (general table finder — client-rendered, needs JS)
  - https://censusindia.gov.in/census.website/en/data/tables and https://censusindia.gov.in/census.website/en/node/91 — alternate listing pages surfaced by search, not independently checked.
  - https://censusindia.gov.in/nada/index.php/catalog/292 — reported as the direct Houselisting/household-amenities catalog entry; https://censusindia.gov.in/nada/index.php/catalog/6191 and `/catalog/425` reported as Primary Census Abstract (PCA) catalog entries (population-side, not the banking indicator, but useful for district-level population denominators).
- **Caveat for the proposal:** 2011 is now 15 years stale for a "lived reality" argument — treat Census 2011 banking-access data strictly as a historical baseline/denominator source (e.g., district population, rural/urban household counts to normalize PMJDY penetration), not as a current-state claim. NFHS-5 (2019–21) and PMJDY/DBT dashboards are the current-state sources; Census 2011 fills in demographic denominators Census 2021 would have updated had it been conducted on schedule.

---

## Cross-cutting notes for the lead / deliverable authors

1. **Tool-access pattern observed:** `pmjdy.gov.in`, `dbtbharat.gov.in`, `censusindia.gov.in`, `rbi.org.in` (selected `prid`s), `sansad.in`, and `dhsprogram.com` all either (a) transport-failed from this sandbox's `web_fetch`, (b) returned 403 (npci.org.in), or (c) returned an un-rendered JS shell (dbtbharat.gov.in, censusindia.gov.in). None of these look like genuinely dead/wrong URLs — they are consistent with bot-detection or SPA rendering. **Recommend a Playwright-driven browser pass** (the main agent/lead has `playwright-browser_*` tools) against each of these exact URLs to pull real numbers and underlying API/XHR endpoints, rather than relying on the search-engine paraphrases in this file.
2. **Every REPORTED figure above was cross-checked against at least one named secondary outlet** (The Hindu, Economic Times, Business Standard, CNBC-TV18, Drishti IAS, Excelbanking) but **none were independently fetched and read in full this session** — the actual article/PDF text should be opened before quoting a specific number in the Round-1 proposal, since search-engine summaries occasionally merge figures from different dates (the PMJDY dormancy range 23%→26% above is a clear example of this ambiguity).
3. **No account-level or person-level PMJDY/DBT microdata is public anywhere** — confirms the thought_node.md risk note; all public sources here are aggregate (national/state/district), reinforcing the plan to use a labelled synthetic simulator for account-level targeting.
4. Suggest filing one concrete follow-up per source with an owner: (a) PMJDY — fetch the Parliament PDF via browser, extract state table; (b) DBT Bharat — Playwright session to capture the SPA's API calls; (c) RBI FI-Index — browse the live Press Releases listing to get the correct current `prid`; (d) NPCI — Playwright or curl with a browser User-Agent to bypass the 403; (e) NFHS-5 — download the IIPS PDF directly and pull the exact table number/page for the bank-account indicator; (f) Findex — Playwright against the interactive portal for the India row/CSV; (g) Census 2011 — Playwright against the NADA catalog pages listed above.
