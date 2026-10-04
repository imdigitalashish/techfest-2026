"""Profile the REAL Delhi groundwater-level data (India-WRIS snapshot) for the pitch and the QC baseline.

Run:  innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/eval/realdata_profile.py
In:   eval/data/delhi_gw_levels.csv.gz, eval/data/delhi_gw_stations.csv  (fetch_delhi.py)
Out:  eval/results/realdata_profile.json (all numbers quoted anywhere come from here)
      eval/results/realdata_station_table.csv

What it computes (no simulation, no tuning):
  1. Inventory: stations by agency x acquisition mode; telemetric stations reporting in 2026.
  2. Data quality of telemetric (GPRS DWLR) series: share of readings that are exactly 0.000,
     implausible (|v| > 200 m), 6-h steps > 2 m (spikes), flatlines (>= 8 identical consecutive
     readings = 2 days), and missing 6-h slots between first and last report.
  3. Sign convention per station (WRIS mixes conventions): resolved by comparing with the same
     station's manual (positive mbgl) readings where both exist; otherwise by the median sign.
  4. Hydrology per telemetric station with clean data: 2025 monsoon rise (pre-monsoon max depth
     Apr-Jun minus post-monsoon min depth Aug-Nov), robust trend (Theil-Sen on monthly medians),
     and the 24-h harmonic amplitude of the detrended 6-hourly series (a pumping-cycle indicator).
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
RES.mkdir(parents=True, exist_ok=True)


def main() -> None:
    lv = pd.read_csv(ROOT / "eval/data/delhi_gw_levels.csv.gz", low_memory=False)
    st = pd.read_csv(ROOT / "eval/data/delhi_gw_stations.csv")
    lv["t"] = pd.to_datetime(lv["datetime_ist"])
    out: dict = {"source": "India-WRIS snapshot fetched 2026-10-04 (components/data-ingest/fetch_delhi.py)"}

    # 1. inventory
    out["stations_in_arcgis_layer"] = int(st.station_id.nunique())
    out["stations_in_arcgis_by_agency"] = st.groupby("agency_name").station_id.nunique().to_dict()
    out["stations_in_arcgis_telemetry_flag"] = st["telemetry"].value_counts().to_dict() if "telemetry" in st else {}
    out["stations_with_level_data"] = int(lv.station_id.nunique())
    out["rows_by_mode"] = lv["mode"].value_counts().to_dict()
    tel = lv[lv["mode"] == "Telemetric"].copy()
    man = lv[lv["mode"] == "Manual"].copy()
    out["telemetric_stations_by_agency"] = tel.groupby("agencyName").station_id.nunique().to_dict()
    last = tel.groupby("station_id").t.max()
    out["telemetric_stations_reporting_in_2026"] = int((last >= "2026-01-01").sum())
    out["telemetric_date_range"] = [str(tel.t.min()), str(tel.t.max())]
    out["manual_date_range"] = [str(man.t.min()), str(man.t.max())]
    out["telemetric_median_interval_h"] = float(
        tel.sort_values(["station_id", "t"]).groupby("station_id").t.diff().dt.total_seconds().median() / 3600)

    # 2. data quality on telemetric rows
    tel = tel.sort_values(["station_id", "t"])
    v = tel["value_m"]
    zero = v == 0
    implaus = v.abs() > 200
    tel["bad"] = zero | implaus
    dq = {"rows": int(len(tel)), "exact_zero_share": float(zero.mean()), "implausible_abs_gt_200m_share": float(implaus.mean())}
    good = tel[~tel.bad].copy()
    good["step"] = good.groupby("station_id").value_m.diff().abs()
    good["dt_h"] = good.groupby("station_id").t.diff().dt.total_seconds() / 3600
    dq["spike_step_gt_2m_in_6h_share"] = float(((good.step > 2) & (good.dt_h <= 6.5)).mean())
    run = good.groupby("station_id").value_m.transform(lambda s: s.groupby((s != s.shift()).cumsum()).transform("size"))
    dq["flatline_ge_8_identical_share"] = float((run >= 8).mean())
    exp, have = 0, 0
    for sid, g in tel.groupby("station_id"):
        span_h = (g.t.max() - g.t.min()).total_seconds() / 3600
        exp += int(span_h // 6) + 1
        have += int(g.t.dt.floor("6h").nunique())
    dq["missing_6h_slots_share"] = float(1 - have / exp) if exp else None
    zs = tel.groupby("station_id").apply(lambda g: (g.value_m == 0).mean(), include_groups=False)
    dq["stations_with_gt_50pct_zero"] = int((zs > 0.5).sum())
    dq["usable_share_after_zero_and_implausible_removed"] = float(1 - tel.bad.mean())
    out["telemetric_data_quality"] = dq

    # 3. sign convention per station
    man_med = man.groupby("station_id").value_m.median()
    conv = {}
    for sid, g in good.groupby("station_id"):
        med = g.value_m.median()
        if sid in man_med.index and man_med[sid] > 0:
            conv[sid] = 1.0 if abs(med - man_med[sid]) <= abs(-med - man_med[sid]) else -1.0
        else:
            conv[sid] = -1.0 if med < 0 else 1.0
    good["depth"] = good.value_m * good.station_id.map(conv)
    overlap = [s for s in conv if s in man_med.index]
    out["sign_convention"] = {"stations_resolved_by_manual_overlap": len(overlap),
                              "stations_negative_convention": int(sum(1 for c in conv.values() if c < 0)),
                              "stations_positive_convention": int(sum(1 for c in conv.values() if c > 0))}

    # 4. hydrology per station
    rows = []
    for sid, g in good.groupby("station_id"):
        g = g.set_index("t").sort_index()
        d = g.depth
        if len(d) < 400:
            continue
        pre = d["2025-04-01":"2025-06-30"]
        post = d["2025-08-01":"2025-11-30"]
        rise = float(pre.max() - post.min()) if len(pre) > 20 and len(post) > 20 else np.nan
        mon = d.resample("MS").median().dropna()
        slope = float(theilslopes(mon.values, np.arange(len(mon)))[0] * 12) if len(mon) >= 12 else np.nan
        x = d.resample("6h").mean()
        resid = (x - x.rolling(12, center=True, min_periods=8).median()).dropna()
        amp24 = np.nan
        if len(resid) > 200:
            hrs = (resid.index - resid.index[0]).total_seconds() / 3600
            w = 2 * np.pi / 24
            A = np.column_stack([np.cos(w * hrs), np.sin(w * hrs), np.ones(len(hrs))])
            coef, *_ = np.linalg.lstsq(A, resid.values, rcond=None)
            amp24 = float(np.hypot(coef[0], coef[1]))
        meta = g.iloc[0]
        rows.append({"station_id": sid, "name": meta.stationName, "agency": meta.agencyName,
                     "district": meta.district, "lat": meta.latitude, "lon": meta.longitude, "n": int(len(d)),
                     "median_depth_mbgl": float(d.median()), "monsoon2025_rise_m": rise,
                     "trend_m_per_yr_(+ = deepening)": slope, "diurnal_amp_m": amp24})
    tab = pd.DataFrame(rows)
    tab.to_csv(RES / "realdata_station_table.csv", index=False)
    plaus = tab[(tab.median_depth_mbgl > 0) & (tab.median_depth_mbgl < 80)]
    out["hydrology"] = {
        "stations_analysed": int(len(tab)),
        "stations_with_plausible_depth_0_80m": int(len(plaus)),
        "median_depth_mbgl_quantiles": plaus.median_depth_mbgl.quantile([.1, .5, .9]).round(2).to_dict(),
        "monsoon2025_rise_m_quantiles": plaus["monsoon2025_rise_m"].dropna().quantile([.1, .5, .9]).round(2).to_dict(),
        "n_with_monsoon2025_rise": int(plaus["monsoon2025_rise_m"].notna().sum()),
        "trend_m_per_yr_quantiles": plaus["trend_m_per_yr_(+ = deepening)"].dropna().quantile([.1, .5, .9]).round(2).to_dict(),
        "share_deepening": float((plaus["trend_m_per_yr_(+ = deepening)"].dropna() > 0).mean()),
        "diurnal_amp_m_quantiles": plaus.diurnal_amp_m.dropna().quantile([.1, .5, .9, .99]).round(3).to_dict(),
        "by_district_median_depth": plaus.groupby("district").median_depth_mbgl.median().round(1).to_dict(),
    }
    (RES / "realdata_profile.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=1, default=str)[:3500])


if __name__ == "__main__":
    main()
