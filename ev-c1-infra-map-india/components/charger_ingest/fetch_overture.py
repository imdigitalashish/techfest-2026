"""Overture Maps places with basic_category = 'ev_charging_station' inside India's bounding box (third source for C5).

Release 2026-09-23.1 (https://stac.overturemaps.org/catalog.json). Licences: CDLA-Permissive-2.0 / Apache-2.0 / CC0-1.0 per
source; the places theme "contains no OpenStreetMap data" (docs.overturemaps.org/guides/places, opened 2026-10-04).
Usage (from ev-c1-infra-map-india/): .venv/bin/python components/charger_ingest/fetch_overture.py
Selection = basic_category 'ev_charging_station' OR a strict EV-charging name rule (many Indian chargers are filed under
other categories, e.g. 'Bolt.Earth EV Charging Station' as corporate_or_business_office). Column `rule` records which matched.
Writes .data/chargers/overture_india.csv (one row per place; clipped to India later by point-in-polygon).
"""
import os, time
import duckdb
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, ".data", "chargers", "overture_india.csv")
RELEASE = "2026-09-23.1"
EV_NAME = (r"(\bev\b|e-vehicle|electric vehicle|\be\.v\.).{0,30}charg|charg.{0,30}(\bev\b|electric vehicle)|ez ?charge|tata power ev"
           r"|statiq|charge ?zone|jio-?bp ?pulse|zeon (ev|charg)|glida|kazam|bolt\.?earth|ather grid|electreefi|chargegrid|fortum charge")
EXCLUDE = r"biryani|fastener|battery charging works|recharge point|mobile recharge|villazeon"
con = duckdb.connect()
for s in ["INSTALL httpfs", "LOAD httpfs", "INSTALL spatial", "LOAD spatial", "SET s3_region='us-west-2'"]:
    con.execute(s)
t = time.time()
con.execute(f"""COPY (
  SELECT id AS source_id, names.primary AS name, basic_category, confidence,
         CASE WHEN basic_category = 'ev_charging_station' THEN 'category' ELSE 'name_rule' END AS rule,
         brand.names.primary AS brand, operating_status,
         list_transform(sources, s -> s.dataset) AS datasets,
         addresses[1].freeform AS address, addresses[1].locality AS locality, addresses[1].region AS region,
         websites[1] AS website, ST_X(geometry) AS lon, ST_Y(geometry) AS lat
  FROM read_parquet('s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*', hive_partitioning=1)
  WHERE bbox.xmin BETWEEN 68.0 AND 97.5 AND bbox.ymin BETWEEN 6.0 AND 37.5 AND (basic_category = 'ev_charging_station'
       OR (regexp_matches(lower(names.primary), '{EV_NAME}') AND NOT regexp_matches(lower(names.primary), '{EXCLUDE}')))
) TO '{OUT}' (HEADER, DELIMITER ',')""")
n = con.execute(f"SELECT count(*) FROM read_csv_auto('{OUT}')").fetchone()[0]
by = con.execute(f"SELECT rule, count(*) FROM read_csv_auto('{OUT}') GROUP BY 1 ORDER BY 1").fetchall()
print(f"overture EV charging rows in India bbox: {n} {by}  ({time.time() - t:.0f}s)  release={RELEASE}")
