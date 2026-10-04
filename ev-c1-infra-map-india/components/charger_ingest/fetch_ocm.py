"""Open Charge Map India subset from the public per-POI export (no API key needed).

Fetch (sparse clone, ~7 MB):
  cd .data && git clone --depth 1 --filter=blob:none --sparse https://github.com/openchargemap/ocm-export.git \
     && cd ocm-export && git sparse-checkout set data/IN
Then: .venv/bin/python components/charger_ingest/fetch_ocm.py  -> .data/chargers/ocm_india.csv
Licence: per OCM data provider (OCM-contributed POIs under OCM's data licence; see the export README).
Status/usage/connection type ids are kept raw; their labels come from OCM reference data (mapping UNVERIFIED here).
"""
import glob, json, os, subprocess
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, ".data", "ocm-export")
rows = []
for f in glob.glob(os.path.join(SRC, "data", "IN", "*.json")):
    d = json.load(open(f)); a = d.get("AddressInfo") or {}
    conns = [{"type_id": c.get("ConnectionTypeID"), "power_kw": c.get("PowerKW"), "count": c.get("Quantity")} for c in (d.get("Connections") or [])]
    rows.append({"source": "ocm", "source_id": f"OCM-{d.get('ID')}", "lat": a.get("Latitude"), "lon": a.get("Longitude"),
                 "name": a.get("Title"), "operator_id": d.get("OperatorID"), "state_text": a.get("StateOrProvince"), "town": a.get("Town"),
                 "address": a.get("AddressLine1"), "usage_type_id": d.get("UsageTypeID"), "status_type_id": d.get("StatusTypeID"),
                 "data_provider_id": d.get("DataProviderID"), "n_points": d.get("NumberOfPoints"), "connectors": json.dumps(conns),
                 "date_created": d.get("DateCreated"), "date_last_verified": d.get("DateLastVerified")})
df = pd.DataFrame(rows)
os.makedirs(os.path.join(ROOT, ".data", "chargers"), exist_ok=True)
df.to_csv(os.path.join(ROOT, ".data", "chargers", "ocm_india.csv"), index=False)
commit = subprocess.run(["git", "-C", SRC, "log", "-1", "--format=%H %cI"], capture_output=True, text=True).stdout.strip()
print(f"ocm POIs: {len(df)}  export commit: {commit}")
print("status_type_id:", df.status_type_id.value_counts(dropna=False).to_dict())
print("usage_type_id:", df.usage_type_id.value_counts(dropna=False).head(8).to_dict())
print("data_provider_id:", df.data_provider_id.value_counts(dropna=False).head(6).to_dict())
