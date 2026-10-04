"""Digitize Figure 2 of the ICCT India LCA fact sheet (Sept 2021) from the PDF's vector drawing.

The chart is drawn with rectangles; their y-coordinates map linearly to g CO2e/km via the axis tick labels
(0 and 80). Prints YAML to stdout. Reproduce:
    python3 data/fetch/digitize_icct_factsheet_2021.py > data/benchmarks/icct_india_factsheet_2021_fig2.yaml
Needs: pip install pdfplumber; the PDF at .data/raw/benchmarks/icct_india_2021.pdf (see fetch_sources.sh).
"""
from collections import defaultdict
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / ".data/raw/benchmarks/icct_india_2021.pdf"
# Bar x-positions (left edge, pt) -> label; left panel = registered 2021, right panel = projected 2030.
BARS = {70.0: ("2021", "ice_small_motorcycle"), 122.6: ("2021", "ev_small_motorcycle"),
        175.2: ("2021", "ice_scooter"), 227.4: ("2021", "ev_scooter"),
        327.9: ("2030", "ice_small_motorcycle"), 380.5: ("2030", "ev_small_motorcycle"),
        433.1: ("2030", "ice_scooter"), 485.6: ("2030", "ev_scooter")}
# Stack order bottom -> top, from the legend (ICE has no battery segment).
STACK_ICE = ["vehicle_production", "maintenance", "fuel_consumption_ttw", "fuel_production_wtt"]
STACK_EV = ["vehicle_production", "battery_production", "maintenance", "electricity_production_wtt"]


def main() -> None:
    page = pdfplumber.open(PDF).pages[2]
    words = page.extract_words()
    tick = {w["text"]: (w["top"] + w["bottom"]) / 2 for w in words if w["text"] in ("0", "80") and w["x0"] < 60}
    y0, y80 = tick["0"], tick["80"]
    g_per_pt = 80.0 / (y0 - y80)
    segs = defaultdict(list)
    for r in page.rects:
        if r["width"] > 30 and 40 < r["top"] and r["bottom"] < 310:
            key = min(BARS, key=lambda x: abs(x - r["x0"]))
            if abs(key - r["x0"]) < 1.0:
                segs[key].append(r)
    print("# Digitized from ICCT fact sheet (Sept 2021) Figure 2 vector drawing; precision about +-0.3 g/km.")
    print("# Bars show the stated-policies electricity mix (the higher end of the error bars).")
    print("source_id: icct-india-lca-factsheet-2021")
    print("locator: \"Figure 2, p. 3\"")
    print("unit: g CO2e/km")
    print("results:")
    for key in sorted(segs):
        year, veh = BARS[key]
        stack = STACK_EV if veh.startswith("ev_") else STACK_ICE
        rects = sorted(segs[key], key=lambda r: -r["bottom"])
        vals = [round(r["height"] * g_per_pt, 2) for r in rects]
        parts = dict(zip(stack, vals))
        total = round(sum(vals), 2)
        body = ", ".join(f"{k}: {v}" for k, v in parts.items())
        print(f"  - {{year: '{year}', vehicle: {veh}, {body}, total: {total}}}")


if __name__ == "__main__":
    main()
