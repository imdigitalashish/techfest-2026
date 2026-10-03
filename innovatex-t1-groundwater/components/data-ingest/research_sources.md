# Data-ingest research sources — Delhi groundwater digital twin

> Verified read-only against primary sources on 2026-10-04 (IST). All endpoints below were
> live-tested with `curl`/`web_fetch` from this sandbox unless marked otherwise. Treat anything
> marked **unverified** as needing a re-check closer to build time (government endpoints move).

---

## 1. India-WRIS groundwater-level station metadata + time series (ArcGIS REST)

**Entry point bug to know about:** `https://indiawris.gov.in/arcgis/rest/services` and
`https://indiawris.gov.in/wrisarcgis/rest/services` both issue an HTTP 301 that *prepends* another
`wris` segment each hop (`.../wrisarcgis` → `.../wriswrisarcgis` → `.../wriswriswrisarcgis` …),
i.e. a broken redirect loop — `web_fetch` exhausted its redirect budget on this host. **Do not use
these paths.** The real, working ArcGIS Server for India-WRIS/NWIC is a separate subdomain:

- **Working catalog root:** `https://arc.indiawris.gov.in/server/rest/services?f=json`
  → returns folders: `Admin, Common, DataDownload, del, eSwis, FeatureService, Hosted,
  HydrologicalData, NWIC, SubInfoSysLCC, Utilities, Vassar` (verified 2026-10-04, HTTP 200, no
  auth required, ArcGIS Server 10.91, `copyrightText: "NWIC"`).
- **Groundwater station layer (metadata, point geometry):**
  `https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer?f=json`
  — 5 sub-layers: `0 Ground Water Level` (points), `1 State Boundary`, `2 District Boundary`
  (`copyrightText: "Survey of India (SOI)"`), `3 Basin`, `4 Sub Basin`. Spatial reference is a
  custom WGS84 Lambert Conformal Conic (central meridian 80°E) — reproject to EPSG:4326 using the
  `lat`/`long` attribute fields rather than the geometry, which is simpler and avoids a CRS
  transform.
- **Layer 0 fields (station metadata):** `station_id, station_code, station_name, station_type,
  lat, long, telemetry (smallint: 1 = telemetric/DWLR, 2 = manual — inferred from values seen),
  agency_name, agency_id, state_name, state_code, district_name, district_code, block_name,
  block_code, basin_name, basin_code, sub_basin_name, sub_basin_code, created_date, remarks*,
  station_data_type_new, class, year, param`.
- **Verified query — Delhi station count:**
  `GET https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0/query?where=state_name%3D%27Delhi%27&returnCountOnly=true&f=json`
  → `{"count":382}` (382 groundwater stations tagged `state_name = 'Delhi'`, live 2026-10-04).
- **Verified sample records (first 5 of the Delhi set):**
  `.../MapServer/0/query?where=state_name%3D%27Delhi%27&outFields=station_code,station_name,agency_name,telemetry,lat,long,district_name,station_type&resultRecordCount=5&returnGeometry=false&f=json`
  returned, e.g.:
  - `station_code=PIZ10181, "Nilothi STP/Lake", agency_name="Delhi SW GW", telemetry=1, lat=28.3924, long=77.0251, district_name="West"`
  - `station_code=282432077112201, "Jheel Khoh", agency_name="CGWB", telemetry=2, lat=28.40889, long=77.18944, district_name="South"`
  - `station_code=CGWBDL28, "Delhi South East KALKAJI Asola Pz", agency_name="CGWB", telemetry=1, lat=28.4125, long=77.2667, district_name="South East Delhi"`
  - Two agencies feed Delhi stations: **CGWB** (Central Ground Water Board) and **Delhi SW GW**
    (Delhi Jal Board / state groundwater department, via the state's own telemetric network).
  - Note the query hit `"exceededTransferLimit":true` at the default page size — page with
    `resultOffset`/`resultRecordCount` (ArcGIS default max is typically 1000–2000 records/request;
    not yet confirmed for this server — test before relying on a single page).
- **Dedicated telemetry stations layer (likely the DWLR/high-frequency subset):**
  `https://arc.indiawris.gov.in/server/rest/services/DataDownload/Telemetry_Stations_Data/MapServer/0?f=json`
  → layer name `TelemetrySites`, same point geometry/CRS pattern. Not yet queried for Delhi-only
  counts — follow-up task.
- **Other discovered folders relevant to this project:**
  `NWIC/Groundwater_Stations` (MapServer), `NWIC/Ground_Water_Level` (a `GPServer` — ArcGIS
  Geoprocessing service, likely the backend the india-wris.gov.in/wris SPA calls for on-demand
  reports/time-series; not yet probed — GPServer calls use a different submit/job-poll pattern
  than FeatureServer queries), `NWIC/GroundwaterLevel_Stations`, `NWIC/GWLMap` (also GPServer),
  `NWIC/Ground_Water_Resources_SOD_DistrictLevel` / `_BlockLevel` (CGWB dynamic/static Stage-of-
  Development resource-estimation layers, annual), `NWIC/GWR2011_CGWB` … `NWIC/GWR2025_CGWB`
  (one MapServer per CGWB groundwater-resource-assessment year — useful for Delhi's annual
  extractable-resource / stage-of-extraction numbers as context for the twin, separate from
  the raw water-level time series).
- **Underlying time-series JSON API (not ArcGIS, used by the india-wris.gov.in SPA):** confirmed
  via the open-source `india-water-data` client
  (`https://github.com/DrJagadeeshG/india-water-data`, AGPL-3.0-or-later, README fetched
  2026-10-04) that the WRIS backend exposes a dataset path
  `/Dataset/Ground Water Level` (and 26 sibling paths — rainfall, river discharge, evapo-
  transpiration, soil moisture, etc.) taking `stateName`/`districtName` (or `basin`/`tributary`)
  and a date range, with `CGWB` as the default agency for groundwater. The client's own README
  states **WRIS does not currently require an API key/auth** (it has a forward-looking
  `WRIS_API_KEY` header for "the day WRIS adds auth"). I could not pull the exact request/response
  JSON schema or full base hostname for this path directly (GitHub's file browser returned a
  generic "can't perform that action" error for the `src/` tree in this session, and
  `raw.githubusercontent.com` access was flaky) — **follow-up:** `pip install` the client (or
  clone it) and run `iwd test-endpoints` to capture a live request/response pair for Delhi before
  committing to this as the time-series source; fall back to the ArcGIS `GroundwaterLevel_Stations`
  layer's attribute table (it appears to carry at least some per-record `date`/`data_value`-style
  fields per the data.gov.in mirror's schema in §2) if the JSON API proves unstable.
- **Terms of use / licence:** India-WRIS (`indiawris.gov.in`) is built, hosted and maintained by
  the National Water Informatics Centre (NWIC) under the Ministry of Jal Shakli / National
  Informatics Centre. Per NIC's standard terms of use (which indiawris.gov.in inherits as an NIC-
  hosted property) material may be reproduced free of charge for non-commercial/research use
  provided it is reproduced accurately, not in a misleading context, and the source is
  acknowledged; **material attributed to a third-party copyright holder (e.g. "Survey of India"
  boundary layers, explicitly labelled in the District Boundary layer's `copyrightText` above)
  needs separate clearance from that holder** — do not redistribute the SOI-sourced boundary
  polygons; use them for internal reference/visual QA only, and get the actual Delhi boundary
  from an openly licensed alternative (§4). I could not locate a single dedicated
  "Terms & Conditions" page at a stable URL on indiawris.gov.in within this session (the
  `/wris/` SPA root loads but its footer links are client-rendered); **follow-up:** open
  `https://indiawris.gov.in/wris/` in a real browser and capture the footer Terms/Disclaimer
  link text verbatim before the prototype ships any India-WRIS-derived figure.

---

## 2. data.gov.in — CGWB groundwater-level API/downloads + GODL terms

- **Catalog/dataset page (mirror, content verified):**
  `https://ckandev.indiadataportal.com/dataset/cgwb-changes-in-depth-to-water-level/resource/b3bfe2fa-cb02-4774-9377-d3db1e1928a5`
  — titled "Groundwater Level", sourced from the Ministry of Jal Shakti, and its published data
  dictionary (fetched 2026-10-04) is exactly the schema we need for the ingest pipeline:
  `station_name, station_code, station_type, station_status, data_acquisition_mode, agency_name,
  agency_id, well_type, well_aquifer_type, latitude, longitude, date_of_establishment,
  data_available_from, discharge_data_available, discharge (m, "mslmeter" per their typo),
  well_depth (m), date, time, data_type_code, data_type_description, data_value (m)`.
  The page explicitly describes the dataset as covering **"manually collected data from
  monitoring wells, high-frequency telemetric readings, and long-term records ... dating back to
  1969"** — i.e. this is the right place to get both the DWLR high-frequency stream and the
  historic manual dip-meter series for the same stations referenced in §1.
- **Likely data.gov.in identifiers (from the mirror, not yet independently confirmed against the
  live data.gov.in CKAN API in this session — see caveat below):**
  resource id `b3bfe2fa-cb02-4774-9377-d3db1e1928a5`, catalog/package id
  `8ff1419c-89d0-4be0-bf2a-25d2822b8006`. **Treat these as unverified** until re-checked against
  the live portal.
- **API shape (OGD Platform India convention, documented pattern, not independently re-derived
  this session):** `GET https://api.data.gov.in/resource/{resource_id}?api-key={KEY}&format=json`
  (also supports `format=xml`, `offset`, `limit`, and `filters[<field>]=<value>` query params).
  Requires a free data.gov.in account + self-service API key from the account's "My Account" page.
- **Connectivity caveat (important):** both `https://data.gov.in` (bare apex) and
  `https://api.data.gov.in` **timed out** from this sandbox on repeated attempts (connect timeout,
  no TLS handshake completed). `https://www.data.gov.in` (the `www` host) *did* respond — a plain
  `GET /` returned HTTP 200, but `/catalog/...` and `/resource/...` paths 302-redirected (likely
  to a bot-check/login-less browse page) and a direct hit on the GODL page returned HTTP 403.
  This looks like edge/WAF geofencing or bot-mitigation rather than the dataset being gone — from
  a normal browser or India-based network this is very likely to work. **Do not assume the API is
  reachable from an arbitrary cloud sandbox IP; build a manual-fallback path (CSV export / cached
  snapshot) into the ingest component.**
- **Licence — Government Open Data Licence – India (GODL-India):** confirmed via search-aggregated
  excerpt of the official gazette notification (`Gazette_Notification_OGDL.pdf`, referenced from
  `data.gov.in/government-open-data-license-india` and state mirrors e.g. `punjab.data.gov.in/Godl`).
  Key clauses: data may be used for **any lawful purpose, commercial or non-commercial**, subject
  to (a) attribution — credit the source, link the licence, note if you changed the data;
  (b) attribute each source separately if combining multiple datasets; (c) must not imply
  government endorsement of your use; (d) **no warranty — data provided "as is," no guarantee of
  continuity**; (e) personal information and RTI-Act-exempt data are outside the licence's scope.
  This traces back to the National Data Sharing and Accessibility Policy (NDSAP), Gazette of
  India, 17 March 2012. **Follow-up:** fetch the actual gazette PDF
  (`https://www.data.gov.in/sites/default/files/Gazette_Notification_OGDL.pdf`) directly once
  network access to that host is available, to quote the clauses verbatim rather than via a
  secondary aggregation — this session could not retrieve it directly (same connectivity issue
  as above).

---

## 3. Open-Meteo Historical Weather API — daily precip/ET0/temp, hourly surface pressure, licence

- **Base endpoint (confirmed live, no key required):**
  `GET https://archive-api.open-meteo.com/v1/archive`
- **Verified request (Delhi, 3-day window, exactly the variable set requested):**
  ```
  https://archive-api.open-meteo.com/v1/archive?latitude=28.65&longitude=77.23&start_date=2024-01-01&end_date=2024-01-03&daily=precipitation_sum,et0_fao_evapotranspiration,temperature_2m_max,temperature_2m_min&hourly=surface_pressure&timezone=Asia%2FKolkata
  ```
  Result (HTTP 200, fetched 2026-10-04): the API snapped the coordinate to its nearest ERA5-Land
  grid cell at `latitude=28.646748, longitude=77.2748, elevation=227.0m`, returned
  `utc_offset_seconds=19800` (IST applied correctly), `daily_units: {precipitation_sum: "mm",
  et0_fao_evapotranspiration: "mm", temperature_2m_max/min: "°C"}`, `hourly_units:
  {surface_pressure: "hPa"}`, with real values e.g. `precipitation_sum=[0.00,0.00,0.00]`,
  `et0_fao_evapotranspiration=[1.69,1.60,1.51]`, `temperature_2m_max=[16.5,15.2,15.9]`,
  `temperature_2m_min=[5.8,4.4,4.4]`, and 72 hourly `surface_pressure` readings in the 989–994 hPa
  range — all physically plausible for Delhi in early January.
- **Exact variable names to use in the ingest config:** `precipitation_sum`,
  `et0_fao_evapotranspiration`, `temperature_2m_max`, `temperature_2m_min` (daily block);
  `surface_pressure` (hourly block). All four daily variables and the hourly pressure variable
  are supported directly by this single endpoint — no separate call needed per variable.
- **Underlying data sources (from the API docs page, fetched 2026-10-04):** ERA5 and ERA5-Land
  reanalysis from ECMWF (Hersbach et al. 2023; Muñoz Sabater 2019) plus CERRA for parts of Europe
  (irrelevant for India) — i.e. this is reanalysis-model output, **not a ground station
  measurement**, which matters for how much we trust absolute precipitation values vs. using them
  as a consistent forcing series for the twin's recharge model.
- **Citation requirement:** cite Zippenfenig, P. (2023), *Open-Meteo.com Weather API*, Zenodo,
  DOI `10.5281/ZENODO.7970649`, plus the ERA5/ERA5-Land DOIs above.
- **Licence (confirmed, `https://open-meteo.com/en/licence`, fetched 2026-10-04):** API data are
  **CC BY 4.0** — free to share and adapt with attribution (credit + licence link + note changes);
  source code is AGPLv3 on GitHub (`open-meteo/open-meteo`), separate from the data licence.
- **Free-tier terms (`https://open-meteo.com/en/terms`, fetched 2026-10-04):** free API is for
  **non-commercial use only**, capped at **10,000 calls/day, 5,000/hour, 600/minute**; a
  hackathon/student prototype plainly qualifies as non-commercial ("public research conducted at
  public institutions," "educational content" are explicitly listed as allowed examples) — keep
  the request cadence well under those caps (batch by date range rather than polling live).

---

## 4. Delhi district boundary — source and licence

Two candidate primary sources, with a clear trade-off:

1. **Survey of India (via the India-WRIS ArcGIS layer), not freely redistributable.**
   `https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/2?f=json`
   (layer id 2, "District Boundary") returns `"copyrightText":"Survey of India (SOI)"` explicitly
   in its metadata (confirmed 2026-10-04). SOI is India's official mapping agency and its
   boundary products are **not openly licensed** — government portals typically only grant
   display/analysis rights within the hosting application, not redistribution. **Do not ship this
   layer's geometry in the prototype's repo or public demo without separate written SOI
   clearance.** Fine for internal cross-checking of the WRIS station attribution only.
2. **DataMeet community maps — open and redistributable, recommended for the actual digital
   twin basemap.** Repository `https://github.com/datameet/maps`, directory
   `Districts/` (Shapefile + GeoJSON of Indian district boundaries), project page
   `https://projects.datameet.org/maps/districts/`. Licensed **CC BY 2.5 India**
   (`https://creativecommons.org/licenses/by/2.5/in/`) — share and adapt with attribution, e.g.
   "Maps provided by DataMeet Community Maps Project. Available under CC BY 2.5 India." Caveat
   (carried over from search-aggregated summaries, **not yet independently re-verified against
   the live GitHub repo in this session** — follow-up: `git`-less fetch of
   `github.com/datameet/maps/tree/master/Districts` to confirm the Delhi district file names and
   last-updated date): boundaries may reflect an older delimitation and should be diffed against
   the current NCT-of-Delhi district list (Delhi was reorganised from 9 to 11, and administratively
   discussed as more, districts in recent years) before use — check the attribute table's district
   count against the current GNCTD list rather than assuming it is current.

**Recommendation for the prototype:** use DataMeet's CC BY 2.5 IN district polygons for the
public-facing basemap/demo, and treat the SOI-sourced WRIS layer only as an internal consistency
check (e.g., does a station's `district_name` attribute match which DataMeet polygon it falls
inside).

---

## 5. High-frequency groundwater pumping / extraction records — USGS IV, Pastas/BRO, and the
real India-relevant alternative

- **USGS Instantaneous Values (IV) service — confirmed US-only, not applicable to Delhi.**
  Base endpoint: `https://waterservices.usgs.gov/nwis/iv/` (e.g.
  `?format=json&sites=<siteno>&parameterCd=72019&startDT=...&endDT=...`, where parameter code
  `72019` is "Depth to water level, below land surface, ft" — this is the standard USGS code for
  high-frequency groundwater-level loggers). I did not find any USGS site-coverage for India; the
  USGS Water Services API's documented scope is U.S. monitoring networks (its "International
  Water Activities" program is a separate, non-API, project-based effort in countries like
  Afghanistan/Cape Verde, not India). **USGS IV cannot supply real Delhi pumping/level data** —
  it is only useful as a reference for API *design* (parameter-code convention, IV cadence) when
  building the ingest schema, not as a live data source for this project.
- **Pastas (time-series analysis library) + BRO (Dutch national subsurface register) — same
  conclusion: useful as methodology reference, not as Indian data.**
  - Pastas itself: `https://github.com/pastas/pastas`, MIT licence — a Python library for
    transfer-function/impulse-response modelling of groundwater head time series; directly
    reusable for the digital twin's analytics layer regardless of data source.
  - Dutch BRO groundwater-level data (`Grondwaterstandonderzoek`/GLD) is exposed as an open REST/
    OGC API, e.g. `https://api.pdok.nl/tno/bro-grondwatermonitoring-in-samenhang-karakteristieken/ogc/v1?f=html`,
    under **CC0** (no restrictions) per the BRO documentation
    (`basisregistratieondergrond.nl/documentatie/catalogus-rest-api`) — **not yet independently
    re-verified by a live request in this session** (out of scope for a Delhi project, but noted
    because it is a genuinely good worked example of a government groundwater REST API with
    public-good licensing to copy conventions from).
  - A `pastas-data` example-datasets repo exists (`github.com/pastas/pastas-data`) under
    GPL-3.0 — again Dutch/European example data, not India.
- **The real India-relevant high-frequency source is what's already in §1/§2:** the
  `telemetry` field (`DataDownload/Telemetry_Stations_Data` MapServer /
  `GroundwaterLevel_Stations` layer's `telemetry=1` stations) plus data.gov.in's explicit mention
  of **"high-frequency telemetric readings"** from CGWB's Digital Water Level Recorder (DWLR)
  network, which does cover Delhi (per the 382-station query in §1, several `agency_name="Delhi SW
  GW"`/`"CGWB"` stations are telemetric). This is DWLR *water-level* telemetry, not direct
  *pumping/extraction-volume* telemetry — India has no public high-frequency tubewell
  abstraction-metering API analogous to USGS IV that I could locate in this session. **Gap:** if
  the project specifically needs pumping *volumes* (not just levels), the only plausible public
  lead is CGWA's No-Objection-Certificate (NOC) extraction-permit database (mentioned in the
  project's own brief) — not investigated in this pass; flag as a follow-up search
  ("CGWA NOC portal API" / "ejalshakti groundwater extraction data").

---

## 6. iAWE dataset — availability and licence

- **What it is:** "Indian dataset for Ambient, Water and Electricity sensing" — 73 days (May–Aug
  2013) of 1-second-resolution water and electricity submetering data from a single home in Delhi,
  collected by IIIT-Delhi (Batra, Gulati, Singh, Srivastava). Confirmed via the dataset's NILMTK
  metadata file, fetched directly (2026-10-04):
  `https://raw.githubusercontent.com/nilmtk/nilmtk/master/nilmtk/dataset_converters/iawe/metadata/dataset.yaml`
  — `geo_location: {locality: Delhi, country: IN, latitude: 28.64, longitude: 77.11}`,
  `timezone: Asia/Kolkata`, `number_of_buildings: 1`, `contact: nipunb@iiitd.ac.in`.
- **Project homepage:** `https://iawe.github.io/` (fetched 2026-10-04) — this is a documentation/
  support site (install instructions, DB schemas, appliance metadata, starter IPython notebooks
  at `nbviewer.ipython.org/github/nipunreddevil/Home_Deployment/tree/master/notebooks/`), **not** a
  direct data-download link. The underlying raw-data hosting (originally Dropbox-style links
  referenced in older NILMTK docs) appears to have **rotted** — this session could not locate a
  currently-live direct download URL for the raw `iawe.h5`/CSV files; the NILMTK converter
  (`nilmtk.dataset_converters.convert_iawe`) expects the files locally and does not itself fetch
  them from the internet. **Treat iAWE as not reliably obtainable without contacting the authors**
  (`nipunb@iiitd.ac.in`) for a current link, or searching Academic Torrents
  (`https://academictorrents.com/`) for a community-seeded copy — neither was verified in this
  session.
- **Licence/terms:** no separate LICENSE file was found; usage terms are stated informally in the
  associated paper and NILMTK ecosystem conventions as **free for personal/classroom/research use
  without a fee, not for commercial distribution, conditioned on citing the original paper**:
  > Batra, N., Gulati, M., Singh, A., Srivastava, M. B. (2013). *It's Different: Insights into
  > Home Energy Consumption in India.* Proceedings of the 5th ACM Workshop on Embedded Systems
  > For Energy-Efficient Buildings (BuildSys '13), Rome. ACM. ISBN 978-1-4503-1169-4.
  Redistribution or commercial use would need explicit permission from the authors — this was
  **not independently confirmed from a primary licence document** (no LICENSE/TERMS file located
  in `nilmtk/nilmtk` or at `iawe.github.io`); it is reported here as the convention stated across
  secondary sources discussing the dataset, so **verify directly with the authors before relying
  on it** for anything beyond internal prototyping.
- **Relevance check for this project:** iAWE is single-home appliance/water *consumption*
  submetering, not groundwater-aquifer data — it is only tangentially useful here (e.g., as a
  demand-side signal or UI/dashboard inspiration for a household water-use layer), not as a
  groundwater-level or pumping data source. Flag to the lead whether it's actually in scope for
  the "digital twin" or was a lead worth dropping.

---

## Open follow-ups (do before relying on any of the above in the prototype)

1. Probe the `NWIC/Ground_Water_Level` and `NWIC/GWLMap` **GPServer** endpoints under
   `arc.indiawris.gov.in` — geoprocessing services use an async submit-job/poll-result pattern,
   different from the FeatureServer `query` calls tested here; this may be the real source of
   per-station historical time series rather than just point metadata.
2. Install/run `DrJagadeeshG/india-water-data`'s `iwd test-endpoints` to get one real captured
   request/response for the `/Dataset/Ground Water Level` JSON API and record the exact hostname,
   headers, and JSON shape.
3. Re-attempt `data.gov.in`/`api.data.gov.in` from a non-sandboxed/India-region network to get a
   real API key and confirm the resource/catalog IDs in §2 are still correct; grab the GODL gazette
   PDF text verbatim.
4. Confirm DataMeet's Delhi district file is current against GNCTD's official district list
   (district count/names) before using it as the twin's authoritative boundary.
5. Search CGWA's NOC/extraction-permit portal for an API (true pumping-volume data; distinct from
   DWLR water-level telemetry) to close the gap noted in §5.
6. Try to get a live iAWE download link from the authors or Academic Torrents before committing to
   using it in the prototype.
