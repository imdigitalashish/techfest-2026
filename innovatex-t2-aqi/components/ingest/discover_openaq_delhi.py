"""Discover OpenAQ location IDs for reference (CPCB/DPCC/IMD/IITM) monitors inside a Delhi bounding box.

Uses only the public, unsigned OpenAQ S3 archive (no API key): for each candidate ID, list one month,
download one day file, and read the station name + coordinates written inside the file itself.
Usage: python discover_openaq_delhi.py --ranges 1-1200 5500-8300 --year 2025 --month 11 --out stations_delhi.csv
"""
import argparse, csv, io, re, sys, zlib
from concurrent.futures import ThreadPoolExecutor
import requests

BUCKET = "https://openaq-data-archive.s3.amazonaws.com"
BBOX = dict(lat_min=28.40, lat_max=28.90, lon_min=76.83, lon_max=77.35)  # NCT of Delhi (approx.)

def probe(session, loc_id, year, month):
    prefix = f"records/csv.gz/locationid={loc_id}/year={year}/month={month:02d}/"
    try:
        r = session.get(f"{BUCKET}/?list-type=2&prefix={prefix}&max-keys=1", timeout=20)
        keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
        if not keys:
            return None
        # Range read: the first 4 KB of the gzip is enough for the header + first rows.
        f = session.get(f"{BUCKET}/{keys[0]}", headers={"Range": "bytes=0-4095"}, timeout=30)
        text = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(f.content).decode(errors="ignore")
        lines = text.splitlines()[:-1]  # drop a possibly truncated last line
        rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
        if not rows:
            return None
        row = rows[0]
        lat, lon = float(row["lat"]), float(row["lon"])
        params = sorted({x["parameter"] for x in rows})  # partial: only params in the first rows
        return dict(location_id=loc_id, location=row["location"], lat=lat, lon=lon, params="|".join(params), sample_key=keys[0])
    except Exception as e:  # network hiccups: report and move on
        print(f"warn id={loc_id}: {e}", file=sys.stderr)
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranges", nargs="+", default=["1-1200", "5500-8300"])
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--month", type=int, default=11)
    ap.add_argument("--out", default="stations_delhi.csv")
    ap.add_argument("--workers", type=int, default=48)
    a = ap.parse_args()
    ids = [i for rg in a.ranges for i in range(int(rg.split("-")[0]), int(rg.split("-")[1]) + 1)]
    s = requests.Session()
    with ThreadPoolExecutor(a.workers) as ex:
        found = [x for x in ex.map(lambda i: probe(s, i, a.year, a.month), ids) if x]
    delhi = [x for x in found if BBOX["lat_min"] <= x["lat"] <= BBOX["lat_max"] and BBOX["lon_min"] <= x["lon"] <= BBOX["lon_max"]]
    print(f"probed={len(ids)} with_data={len(found)} in_delhi_bbox={len(delhi)}", file=sys.stderr)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["location_id", "location", "lat", "lon", "params", "sample_key"])
        w.writeheader(); w.writerows(sorted(delhi, key=lambda x: x["location_id"]))

if __name__ == "__main__":
    main()
