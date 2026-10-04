"""Digitize Figure 1 of the ICCT India LCA fact sheet (Sept 2021): life-cycle GHG of average new SEDAN segment cars
registered in India in 2021 (gasoline, diesel, CNG, BEV, FCEV), from the PDF's vector drawing.

Calibration uses the chart's horizontal gridlines (0, 50, ..., 300 g CO2e/km), least-squares fit. Stack order from the
legend (bottom -> top). Prints YAML. Reproduce (from ev-c2-green-auto-lca/):
    python3 data/fetch/digitize_icct_factsheet_2021_fig1.py > data/benchmarks/icct_india_factsheet_2021_fig1_sedan.yaml
"""
from pathlib import Path

import numpy as np
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / ".data/raw/benchmarks/icct_india_2021.pdf"
BARS = [  # (x0 of bar in pt, vehicle id, stack bottom -> top)
    (77.8, "gasoline", ["vehicle_production", "maintenance", "fuel_consumption_ttw", "fuel_production_wtt"]),
    (139.3, "diesel", ["vehicle_production", "maintenance", "fuel_consumption_ttw", "fuel_production_wtt"]),
    (200.9, "cng", ["vehicle_production", "maintenance", "fuel_consumption_ttw", "fuel_production_wtt", "methane_20yr_gwp_extra"]),
    (262.4, "bev_grid_steps", ["vehicle_production", "battery_production", "maintenance", "electricity_production_wtt"]),
    (324.0, "bev_renewable", ["vehicle_production", "battery_production", "maintenance", "electricity_production_wtt"]),
    (385.6, "fcev_natural_gas_h2", ["vehicle_production", "hydrogen_system", "maintenance", "fuel_production_wtt", "methane_20yr_gwp_extra"]),
    (447.1, "fcev_renewable_h2", ["vehicle_production", "hydrogen_system", "maintenance", "fuel_production_wtt"]),
]


def main() -> None:
    page = pdfplumber.open(PDF).pages[1]
    # y-axis tick labels (0..300) give each gridline its value; gridlines start at the plot's left edge
    ticks = {float(w["text"]): (w["top"] + w["bottom"]) / 2 for w in page.extract_words()
             if w["text"] in ("0", "50", "100", "150", "200", "250", "300") and w["x0"] < 60 and 400 < w["top"] < 660}
    grid = sorted({round(ln["top"], 2) for ln in page.lines
                   if abs(ln["top"] - ln["bottom"]) < 0.01 and abs(ln["x0"] - 63.4) < 1 and ln["x1"] - ln["x0"] > 300})
    vals = [min(ticks, key=lambda v: abs(ticks[v] - y)) for y in grid]
    slope, icpt = np.polyfit(np.array(grid), np.array(vals), 1)   # value = slope*y + icpt (slope < 0)
    print("# Digitized from ICCT fact sheet (Sept 2021) Figure 1 vector drawing (gridline-calibrated, about +-0.5 g/km).")
    print("# BEV bars use the IEA STEPS-based lifetime electricity mix (upper end of the error bar).")
    print("# The 'methane_20yr_gwp_extra' segment is the extra impact when methane is counted at 20-year GWP; totals exclude it.")
    print("source_id: icct-india-lca-factsheet-2021")
    print('locator: "Figure 1, p. 2"')
    print("unit: g CO2e/km")
    print(f"calibration: {{gridlines: {len(grid)}, g_per_pt: {round(-slope, 4)}}}")
    print("results:")
    for x0, vid, stack in BARS:
        rects = [r for r in page.rects if abs(r["x0"] - x0) < 0.3 and r["width"] > 20]
        seen, segs = set(), []
        for r in sorted(rects, key=lambda r: -r["bottom"]):
            key = (round(r["top"], 1), round(r["bottom"], 1))
            if key in seen:            # pattern fills are drawn twice (colour + hatch)
                continue
            seen.add(key)
            segs.append(round(r["height"] * -slope, 2))
        parts = dict(zip(stack, segs))
        total = round(sum(v for k, v in parts.items() if k != "methane_20yr_gwp_extra"), 2)
        body = ", ".join(f"{k}: {v}" for k, v in parts.items())
        print(f"  - {{vehicle: {vid}, {body}, total_gwp100: {total}}}")


if __name__ == "__main__":
    main()
