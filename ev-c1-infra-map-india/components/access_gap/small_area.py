"""C10 small-area supply model: district public charging stations from state totals, validated on Chhattisgarh.

Why: open-data sites cover ~10% of official stations and the three-source capture–recapture estimate failed the
state-level validation (eval/results/c5_mse_summary.json), so district supply is estimated by ALLOCATING the official
state total with weights from a model fitted across states:
    ln(official_s) = a + b·ln(BEV_s) + c·ln(open_s + 1)      (OLS over states, the target state excluded)
    est_d = Total_state · w_d / Σ w,   w_d = BEV_d^b · (open_d + 1)^c        (raking; the intercept cancels)
Interval (predictive): bootstrap over states (B = 1000) for the coefficients, then a multinomial draw of the state total
across districts → 5th–95th percentile of est_d. (Coefficient-only intervals covered just 29% of Chhattisgarh districts.)
Baselines: open-share, BEV-share, 50:50 blend.
Validation: Chhattisgarh official district counts (PIB 2086533, 20 Dec 2024; mapped to the 2021 districts of
geoBoundaries ADM2: 'Kabeerdham'+'Kabirdham (Kawardha)' → Kabeerdham, 'Kanker'+'Uttar Bastar Kanker' → Uttar Bastar
Kanker, 'Manendragarh Chirmiri Bharatpur' → Koriya (split from Korea on 9 Sep 2022, Wikipedia), 'Sarangarh-Bilaigarh'
dropped (two parents)). State model for the validation fitted on the Dec-2024 snapshot without Chhattisgarh.
Usage: .venv/bin/python -W ignore components/access_gap/small_area.py
"""
from __future__ import annotations

import json
import os
import re
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); OUT = f"{R}/eval/results"; RAW = f"{R}/.data/vahan/raw"
SEED = 20261004
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))  # noqa: E731
ALIAS = {"up": "uttarpradesh", "utofdandnhanddandd": "dadraandnagarhavelianddamananddiu", "andamanandnicobar": "andamanandnicobarislands",
         "andamanandnicobarisland": "andamanandnicobarislands", "utofdnhanddd": "dadraandnagarhavelianddamananddiu"}
key = lambda s: ALIAS.get(norm(s), norm(s))  # noqa: E731
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def bev_cum_at(year: int, month: int) -> pd.Series:
    """State BEV registrations cumulative to the end of (year, month) = till-today minus later months."""
    till = pd.read_csv(f"{RAW}/nat_state_fuel_A.csv"); till = (till["ELECTRIC(BOV)"] + till["PURE EV"]).set_axis(till.row_label.map(key))
    later = pd.Series(0.0, index=till.index)
    for y in range(year, 2027):
        d = pd.read_csv(f"{RAW}/nat_state_month_bev_{y}.csv").set_index("row_label"); d.index = d.index.map(key)
        for i, m in enumerate(MONTHS):
            if (y, i + 1) > (year, month) and m in d.columns:
                later = later.add(d[m], fill_value=0)
    return (till - later.reindex(till.index).fillna(0)).clip(lower=0)


def open_by_state() -> pd.Series:
    rec = pd.read_csv(f"{OUT}/c5_linked_records.csv")
    return rec.groupby("state_key").site.nunique()


def official(source: str) -> pd.Series:
    pcs = pd.read_csv(f"{R}/components/charger_ingest/data/official_pcs_statewise.csv")
    p = pcs[pcs.source == source]
    return pd.Series(p.pcs_total.values, index=p.state.map(key)).groupby(level=0).sum()


def fit_state_model(y: pd.Series, bev: pd.Series, opn: pd.Series, exclude: str | None = None, idx=None):
    df = pd.DataFrame({"y": y, "bev": bev, "open": opn.reindex(y.index).fillna(0)}).dropna()
    df = df[(df.y > 0) & (df.bev > 0)]
    if exclude:
        df = df.drop(index=exclude, errors="ignore")
    if idx is not None:
        df = df.iloc[idx]
    X = np.column_stack([np.ones(len(df)), np.log(df.bev), np.log(df.open + 1)])
    coef, *_ = np.linalg.lstsq(X, np.log(df.y), rcond=None)
    return coef, df


def allocate(total: float, bev_d: pd.Series, open_d: pd.Series, b: float, c: float) -> pd.Series:
    w = np.power(bev_d.astype(float).clip(lower=1), b) * np.power(open_d.astype(float) + 1, c)
    return total * w / w.sum()


def small_area(total, bev_d, open_d, y, bev_s, open_s, exclude=None, B=1000):
    coef, df = fit_state_model(y, bev_s, open_s, exclude)
    point = allocate(total, bev_d, open_d, coef[1], coef[2])
    rng = np.random.default_rng(SEED); sims = []
    for _ in range(B):
        cb, _ = fit_state_model(y, bev_s, open_s, exclude, idx=rng.integers(0, len(df), len(df)))
        p = np.asarray(allocate(total, bev_d, open_d, cb[1], cb[2]).values, float) / total
        sims.append(rng.multinomial(int(round(total)), p / p.sum()))  # predictive: coefficient + count noise
    sims = np.array(sims)
    return point, pd.Series(np.percentile(sims, 5, axis=0), index=bev_d.index), pd.Series(np.percentile(sims, 95, axis=0), index=bev_d.index), coef


def districts_of(state_prefix: str) -> gpd.GeoDataFrame:
    a1 = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson"); poly = a1[a1.shapeName.str.startswith(state_prefix)].geometry.iloc[0]
    a2 = gpd.read_file(f"{R}/.data/geo/ind_adm2.geojson")
    return a2[a2.representative_point().within(poly)].copy()


def open_sites_by_district(state_key: str, dist: gpd.GeoDataFrame, col: str) -> pd.Series:
    rec = pd.read_csv(f"{OUT}/c5_linked_records.csv")
    s = rec[rec.state_key == state_key].groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean")).reset_index()
    g = gpd.GeoDataFrame(s, geometry=gpd.points_from_xy(s.lon, s.lat), crs="EPSG:4326")
    j = gpd.sjoin(g, dist[[col, "geometry"]], how="left", predicate="within")
    return j.groupby(col).size()


def validate_chhattisgarh() -> dict:
    cg = districts_of("Chhat")
    off = pd.read_csv(f"{R}/components/charger_ingest/data/official_pcs_chhattisgarh_districts_pib2086533.csv")
    m = {"Kabirdham (Kawardha)": "Kabeerdham", "Kanker": "Uttar Bastar Kanker", "Manendragarh Chirmiri Bharatpur": "Koriya",
         "Korea": "Koriya", "Balodabazar-Bhatapara": "Baloda Bazar", "Gariyaband": "Gariaband", "Bemetara": "Bemetra"}
    off = off[off.district != "Sarangarh-Bilaigarh"].assign(d2021=lambda x: x.district.replace(m)).groupby("d2021").pcs.sum()
    truth = off.reindex(sorted(cg.shapeName)).fillna(0)
    xw = pd.read_csv(f"{R}/components/admin_geo/data/rto_district_CG.csv")
    rto = pd.concat([pd.read_csv(f"{RAW}/rto_CG_{c}_class_fuel_A.csv").assign(rto_code=c) for c in xw.rto_code
                     if os.path.exists(f"{RAW}/rto_CG_{c}_class_fuel_A.csv")])
    rto["bev"] = rto.get("ELECTRIC(BOV)", 0) + rto.get("PURE EV", 0)
    bev_d = rto.merge(xw, on="rto_code").groupby("district").bev.sum().reindex(truth.index).fillna(0)
    open_d = open_sites_by_district("chhattisgarh", cg, "shapeName").reindex(truth.index).fillna(0)
    total = float(truth.sum())
    y = official("pib2086533"); bev_s = bev_cum_at(2024, 11); open_s = open_by_state()
    sa, lo, hi, coef = small_area(total, bev_d, open_d, y, bev_s, open_s, exclude="chhattisgarh")
    cands = {"open_share": total * open_d / open_d.sum(), "bev_share": total * bev_d / bev_d.sum(),
             "blend_50_50": 0.5 * total * open_d / open_d.sum() + 0.5 * total * bev_d / bev_d.sum(), "small_area_model": sa}
    res = {k: {"wape": round(float((v - truth).abs().sum() / truth.sum()), 3), "spearman": round(float(spearmanr(np.asarray(v.reindex(truth.index), float), np.asarray(truth, float))[0]), 3)}
           for k, v in cands.items()}
    cover = float(((truth >= lo.round(0)) & (truth <= hi.round(0))).mean())
    pd.DataFrame({"official_dec2024": truth, "bev_till_today": bev_d, "open_sites": open_d, **{k: v.round(1) for k, v in cands.items()},
                  "sa_lo": lo.round(1), "sa_hi": hi.round(1)}).to_csv(f"{OUT}/cg_district_validation.csv", index_label="district")
    return {"districts": int(len(truth)), "official_total_evaluated": int(total), "bev_mapped": int(bev_d.sum()),
            "open_sites": int(open_d.sum()), "state_model_coef_dec2024_excl_cg": [round(float(x), 3) for x in coef],
            "methods": res, "small_area_ci90_coverage": round(cover, 3)}


def state_loo(source="pib2151390", ym=(2025, 7)) -> dict:
    """Leave-one-state-out error of the state model itself (how well BEV + open data predict official totals)."""
    y = official(source); bev_s = bev_cum_at(*ym); open_s = open_by_state()
    coef, df = fit_state_model(y, bev_s, open_s)
    loo = []
    for s in df.index:
        cf, _ = fit_state_model(y, bev_s, open_s, exclude=s)
        pred = np.exp(cf[0] + cf[1] * np.log(df.loc[s, "bev"]) + cf[2] * np.log(df.loc[s, "open"] + 1))
        loo.append(abs(np.log(pred / df.loc[s, "y"])))
    return {"coef_all_states": [round(float(x), 3) for x in coef], "states_in_fit": int(len(df)),
            "loo_median_abs_log_err": round(float(np.median(loo)), 3)}


if __name__ == "__main__":
    s = {"chhattisgarh_validation": validate_chhattisgarh(), "state_model_aug2025": state_loo()}
    json.dump(s, open(f"{OUT}/small_area_summary.json", "w"), indent=1)
    print(json.dumps(s, indent=1))
