"""Per-node power budget and solar check. Datasheet values were opened by the lead on 4 Oct 2026 (quotes below);
values tagged ASSUMPTION are engineering assumptions to be replaced by bench measurements.
Run: python power_budget.py → power_budget.json"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = {
 "sps30": ("Sensirion SPS30 datasheet v0.9 D1 (Nov 2018), Table 2: 'Average supply current Measurement-Mode 60 mA'",
           "https://media.digikey.com/pdf/Data%20Sheets/Sensirion%20PDFs/Sensirion_SPS30_Particulate_Matter_Sensor_v0.9_D1.pdf"),
 "esp32": ("Espressif ESP32-S3 datasheet v2.1, Table 5-9 Modem-sleep, 40 MHz, 'WAITI (Dual core in idle state) 13.2' mA (Typ1)",
           "https://documentation.espressif.com/esp32-s3_datasheet_en.pdf"),
 "ghi": ("NASA POWER climatology API v2.10.0 (SYN1DEG, 2001–2020), ALLSKY_SFC_SW_DWN at 28.61N 77.21E, kWh/m²/day",
         "https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=77.21&latitude=28.61&format=JSON"),
}
GHI = {"JAN": 3.0898, "FEB": 4.3471, "MAR": 5.6489, "APR": 6.5806, "MAY": 6.7116, "JUN": 6.0862, "JUL": 5.0071,
       "AUG": 4.8852, "SEP": 5.0578, "OCT": 4.6646, "NOV": 3.5796, "DEC": 3.029}
loads_w = {"SPS30, continuous measurement (5 V × 60 mA)": 5.0 * 0.060,
           "ESP32-S3, modem-sleep 40 MHz idle (3.3 V × 13.2 mA)": 3.3 * 0.0132,
           "LoRa radio + SHT30 + misc (ASSUMPTION: 3.3 V × 5 mA average)": 3.3 * 0.005}
EFF = 0.85      # ASSUMPTION: DC-DC conversion efficiency
DERATE = 0.70   # ASSUMPTION: panel soiling (construction dust), temperature, charger losses
DOD = 0.80      # ASSUMPTION: usable battery fraction
PANEL_W, BATT_WH = 10.0, 12.8 * 12.0
load_wh_day = sum(loads_w.values()) * 24 / EFF
worst = min(GHI, key=GHI.get)
gen = {m: round(PANEL_W * g * DERATE, 1) for m, g in GHI.items()}
out = {"sources": SRC, "loads_w": {k: round(v, 4) for k, v in loads_w.items()}, "assumptions": {"dc_dc_eff": EFF, "solar_derate": DERATE, "battery_dod": DOD},
       "load_wh_per_day": round(load_wh_day, 1), "panel_w": PANEL_W, "battery_wh_nominal": BATT_WH,
       "solar_wh_per_day_by_month": gen, "worst_month": worst, "worst_month_margin": round(gen[worst] / load_wh_day, 2),
       "autonomy_days_no_sun": round(BATT_WH * DOD / load_wh_day, 1),
       "caveat": "NASA POWER is a 20-year all-sky climatology; smog/fog weeks are darker than the monthly mean. Bench-measure the real draw."}
json.dump(out, open(os.path.join(HERE, "power_budget.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("load_wh_per_day", "worst_month", "worst_month_margin", "autonomy_days_no_sun")}))
