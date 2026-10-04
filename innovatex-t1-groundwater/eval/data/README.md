# eval/data — real public data snapshots (regenerable)

Regenerate everything: `innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/data-ingest/fetch_delhi.py` (fetched 2026-10-04 IST; raw responses cached in gitignored `.data/`).

| File | What | Source (attribution) |
|---|---|---|
| `delhi_gw_stations.csv` | Groundwater-level station metadata, `state_name='Delhi'` | India-WRIS / National Water Informatics Centre (NWIC), Ministry of Jal Shakti — ArcGIS REST `arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0` |
| `delhi_gw_levels.csv.gz` | Groundwater-level time series 2015-01-01 → 2026-10-03, CGWB and "Delhi SW GW" agencies, manual + telemetric (GPRS DWLR) | India-WRIS dataset API `POST https://indiawris.gov.in/Dataset/Ground%20Water%20Level` (per district × agency, 5,000 rows/page). Data originate from CGWB and the Delhi state groundwater agency. |
| `delhi_gw_levels_summary.csv` | Per-station counts, date range, median depth | derived |
| `delhi_weather_daily.csv` | Daily precipitation, FAO ET0, mean temperature, 2010-01-01 → 2026-09-30 at 28.6139 N, 77.2090 E | Open-Meteo historical archive (ERA5 reanalysis, Copernicus/ECMWF) — reanalysis, not a station record |

Conventions: India-WRIS `dataValue` is the water level in metres relative to ground (negative below ground); we store `depth_mbgl = -dataValue`. `datetime_ist` is the timestamp as published (IST wall clock). Data are used for non-commercial student research with attribution; India-WRIS boundary layers (Survey of India) are not redistributed here.
