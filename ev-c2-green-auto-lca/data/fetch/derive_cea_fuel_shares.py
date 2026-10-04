"""Derive coal+lignite shares of Indian net generation FY2025-26 from the CEA CO2 Baseline Database v22.0 workbook.

Reproduce (from ev-c2-green-auto-lca/):  python3 data/fetch/derive_cea_fuel_shares.py
Needs .data/raw/electricity/cea_db_v22.xlsx (see fetch_sources.sh). Prints the numbers used in
data/factors/energy_grid_co2e.yaml. Unit-level rows (UNIT_NO != 0) reproduce CEA Annexure-I conventional generation.
"""
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
TOTAL_NET_GWH = 1761.28e3   # CEA User Guide v22.0, Annexure-I, FY2025-26 total net generation incl. RE, captive, imports


def main() -> None:
    ws = openpyxl.load_workbook(ROOT / ".data/raw/electricity/cea_db_v22.xlsx", read_only=True, data_only=True)["Data"]
    gen: dict[str, float] = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[2] in (0, None):
            continue
        try:
            g = float(r[51])          # column '2025-26 Net Generation GWh'
        except (TypeError, ValueError):
            continue
        fuel = str(r[9]).strip().upper()
        gen[fuel] = gen.get(fuel, 0.0) + g
    coal = gen.get("COAL", 0.0) + gen.get("LIGN", 0.0)
    fossil = coal + gen.get("GAS", 0.0) + gen.get("OIL", 0.0) + gen.get("DISL", 0.0)
    print({k: round(v) for k, v in sorted(gen.items(), key=lambda kv: -kv[1])})
    print(f"station rows total GWh: {sum(gen.values()):.0f} (Annexure-I conventional: 1,424,190)")
    print(f"coal+lignite GWh: {coal:.0f}; share of total net generation: {coal / TOTAL_NET_GWH:.4f}; "
          f"share of fossil (OM set proxy): {coal / fossil:.4f}")


if __name__ == "__main__":
    main()
