"""Input manifest: SHA-256, size and provenance of every cached input the analyses read (review 2026-10-04, issue 5).

  python3 eval/data_manifest.py --write   # after a deliberate data refresh: record eval/data_manifest.json
  python3 eval/data_manifest.py           # verify: exit 1 if any input is missing or differs (run_all.sh does this)
Raw inputs stay out of git (PLAYBOOK §6); the manifest makes a frozen evaluation detect a silently newer scrape.
"""
import hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [".data/vahan/raw/*.csv", ".data/chargers/osm_india.csv", ".data/chargers/ocm_india.csv", ".data/chargers/overture_india.csv",
            ".data/chargers/osm_india_raw.json", ".data/geo/*.geojson", ".data/roads/mh_motorway_trunk.json", ".cache/sources/*.html"]
def files():
    out = []
    for p in PATTERNS:
        out += sorted(ROOT.glob(p))
    return [f for f in out if f.name != "mh_district_gap.geojson"]  # derived output, not an input
def digest(f):
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
if __name__ == "__main__":
    man = ROOT / "eval/data_manifest.json"
    cur = {str(f.relative_to(ROOT)): {"sha256": digest(f), "bytes": f.stat().st_size} for f in files()}
    if "--write" in sys.argv:
        prov = {"osm_overpass_base": json.loads((ROOT / ".data/chargers/osm_india_raw.json").read_text()).get("osm3s", {}).get("timestamp_osm_base"),
                "ocm_export_commit": "8e3bedca48ca94807d96b2f5e7ee02cffe63ae54 (2026-04-22)", "overture_release": "2026-09-23.1",
                "vahan": "fetched 2026-10-04 (per-table fetched_at in .data/vahan/raw/*.json)"}
        man.write_text(json.dumps({"provenance": prov, "files": cur}, indent=1)); print(f"manifest written: {len(cur)} files")
        sys.exit(0)
    ref = json.loads(man.read_text())["files"]
    bad = [k for k in ref if k not in cur or cur[k]["sha256"] != ref[k]["sha256"]]
    print(f"data manifest: {len(ref) - len(bad)}/{len(ref)} inputs match" + (f"; MISMATCH/MISSING: {bad[:5]}" if bad else ""))
    sys.exit(1 if bad else 0)
