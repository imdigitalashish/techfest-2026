"""The 4 twin sites. Coordinates are the downstream (mouth) node of the named OSM waterway way
(OSM waterways are drawn in flow direction), found with the Overpass query in fetch_forcing.py,
accessed 2026-10-04. Everything that is not a coordinate is an ASSUMPTION (see twin.md table)."""
from __future__ import annotations

from ._paths import C

ACCESSED = "2026-10-04"
OVERPASS = ("https://overpass-api.de/api/interpreter  query: way[waterway][name~Mithi|Dahisar|Oshiwara|...]"
            "(18.88,72.75,19.32,73.05); out geom  -> downstream end node of the named way")

# site_id, name, lat, lon, osm ref, waterbody, outfall_type, width_m, boom_len_m, boom_cap_m3, area_km2, wards
_SITES = [
    ("mithi_mahim", "Mithi River mouth at Mahim Creek", 19.048725, 72.836919,
     "https://www.openstreetmap.org/way/420108354", "Mithi River -> Mahim Creek -> Mahim Bay",
     "river_mouth", 70.0, 90.0, 60.0, 73.0, ["G/N", "H/E", "K/E", "L", "S"]),
    ("oshiwara_malad", "Oshiwara River outfall into Malad Creek (Lokhandwala)", 19.165591, 72.819865,
     "https://www.openstreetmap.org/way/257443428", "Oshiwara River -> Malad Creek -> Arabian Sea",
     "creek", 40.0, 55.0, 35.0, 20.0, ["K/W", "P/S"]),
    ("dahisar_mouth", "Dahisar River mouth (Manori-Gorai creek system)", 19.268562, 72.84743,
     "https://www.openstreetmap.org/way/420108348", "Dahisar River -> Manori Creek",
     "river_mouth", 35.0, 45.0, 30.0, 35.0, ["R/N", "R/C"]),
    ("trombay_mahul", "Nullah outfall to Thane Creek near Trombay Koliwada (approx.)", 19.03365, 72.95036,
     "https://www.openstreetmap.org/node/1366794662", "Trombay nullah -> Thane Creek",
     "nullah_outfall", 15.0, 20.0, 12.0, 8.0, ["M/E"]),
]

# ASSUMPTION: population density ~20,000 per km2 for all catchments (order of magnitude for
# Greater Mumbai; not verified against Census tables in this run -> UNVERIFIED).
POP_DENSITY_PER_KM2 = 20_000


def _prov(kind, source, notes=""):
    return C.Provenance(kind=kind, source=source, notes=notes)


def get_sites() -> list:
    out = []
    for sid, name, lat, lon, osm, wb, typ, width, blen, bcap, area, wards in _SITES:
        a = _prov("assumption", "research/components/twin.md#parameters",
                  "ASSUMPTION; drawn over a range in the Monte Carlo")
        cat = C.CatchmentDescriptor(
            area_km2=area, population=int(area * POP_DENSITY_PER_KM2),
            informal_settlement_fraction=0.4, waste_collection_coverage=0.9,
            runoff_coefficient=0.7, wards=wards,
            provenance={
                "area_km2": _prov("assumption", "research/components/twin.md#parameters",
                                  "ASSUMPTION; Mithi 73 and Dahisar 35 match commonly quoted 7,295 ha / "
                                  "3,488 ha figures seen only in search snippets (UNVERIFIED)"),
                "population": _prov("assumption", "research/components/twin.md#parameters",
                                    "ASSUMPTION area x 20,000 per km2 (UNVERIFIED density)"),
                "informal_settlement_fraction": a, "waste_collection_coverage": a,
                "runoff_coefficient": a,
            })
        out.append(C.Site(
            site_id=sid, name=name, lat=lat, lon=lon, waterbody=wb, outfall_type=typ, tidal=True,
            channel_width_m=width, boom_length_m=blen, boom_capacity_m3=bcap, catchment=cat,
            provenance={
                "lat": _prov("observed", osm, f"OSM downstream node via Overpass, accessed {ACCESSED}"
                             + (" ; bus-station node used as approximate anchor for the creek-shore outfall"
                                if sid == "trombay_mahul" else "")),
                "lon": _prov("observed", osm, f"accessed {ACCESSED}"),
                "channel_width_m": a, "boom_length_m": a, "boom_capacity_m3": a,
            }))
    return out


SITE_IDS = [s[0] for s in _SITES]
