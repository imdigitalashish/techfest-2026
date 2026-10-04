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


CG_TOTAL_SOURCE = "pib2086533"  # independent state annex total (271), not the sum of district labels


def cg_truth_harmonised():
    """Official district counts (20 Dec 2024) on 2021 district geometry. Rules: duplicate-name rows summed;
    Manendragarh-Chirmiri-Bharatpur -> Koriya (split from Korea on 9 Sep 2022); Sarangarh-Bilaigarh (two parents) split
    0.5/0.5 to Raigarh and Baloda Bazar; districts absent from the annex stay MISSING (not zero)."""
    cg = districts_of("Chhat")
    off = pd.read_csv(f"{R}/components/charger_ingest/data/official_pcs_chhattisgarh_districts_pib2086533.csv")
    m = {"Kabirdham (Kawardha)": "Kabeerdham", "Kanker": "Uttar Bastar Kanker", "Manendragarh Chirmiri Bharatpur": "Koriya",
         "Korea": "Koriya", "Balodabazar-Bhatapara": "Baloda Bazar", "Gariyaband": "Gariaband", "Bemetara": "Bemetra"}
    rows = []
    for d, n in off[["district", "pcs"]].values:
        if d == "Sarangarh-Bilaigarh":
            rows += [("Raigarh", n / 2), ("Baloda Bazar", n / 2)]
        else:
            rows.append((m.get(d, d), n))
    t = pd.DataFrame(rows, columns=["d", "pcs"]).groupby("d").pcs.sum()
    truth = t.reindex(sorted(cg.shapeName))  # NaN = no label
    acct = {"annex_rows": int(len(off)), "annex_total": int(off.pcs.sum()), "labelled_2021_districts": int(truth.notna().sum()),
            "unlabelled_2021_districts": sorted(truth[truth.isna()].index.tolist()), "unmapped_names": sorted(set(t.index) - set(cg.shapeName))}
    return cg, truth, acct


def cg_district_bev(year_end=None):
    """District BEV from RTO tables: 'till today' (A) or cumulative to the end of `year_end` (A minus later years)."""
    xw = pd.read_csv(f"{R}/components/admin_geo/data/rto_district_CG.csv")
    def bev(code, y):
        f = f"{RAW}/rto_CG_{code}_class_fuel_{y}.csv"
        if not os.path.exists(f):
            return 0.0
        d = pd.read_csv(f); return float(d.get("ELECTRIC(BOV)", 0).sum() + d.get("PURE EV", 0).sum())
    rows = []
    for code, dist in xw[xw.district.notna()][["rto_code", "district"]].values:
        v = bev(code, "A")
        if year_end is not None:
            v -= sum(bev(code, str(y)) for y in range(year_end + 1, 2027))
        rows.append((dist, v))
    return pd.DataFrame(rows, columns=["d", "bev"]).groupby("d").bev.sum()


def open_asof(date):
    """Approximate open-data sites known by `date`: OCM created on/before it + OSM last-edited on/before it (no Overture:
    no history). A lower bound; used only for the point-in-time variant."""
    import sys as _s
    _s.path.insert(0, f"{R}/components/census_completeness")
    import mse as M
    d = M.link(M.load_sources(ocm_max_created=date, use_ovt=False, osm_max_edit=date))
    return d.groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean"), state_key=("state_key", "first")).reset_index()


def score(pred, truth, lo=None, hi=None):
    lab = truth.notna()
    p, t = pred[lab].astype(float), truth[lab].astype(float)
    out = {"wape": round(float((p - t).abs().sum() / t.sum()), 4), "spearman": round(float(spearmanr(p.values, t.values)[0]), 4)}
    if lo is not None:
        out["pi90_coverage"] = round(float(((t >= lo[lab]) & (t <= hi[lab])).mean()), 4)
        out["pi90_inside"] = f"{int(((t >= lo[lab]) & (t <= hi[lab])).sum())}/{int(lab.sum())}"
    return out


def validate_chhattisgarh_point_in_time() -> dict:
    cg, truth, acct = cg_truth_harmonised()
    total = float(official(CG_TOTAL_SOURCE)["chhattisgarh"])
    idx = truth.index
    bev24 = cg_district_bev(2024).reindex(idx).fillna(0)
    ys = official("pib2086533"); bev_s24 = bev_cum_at(2024, 11)
    zero = pd.Series(0.0, index=idx)
    res, tables = {}, {}
    # (A) BEV-only, fully point-in-time: c = 0
    coefA, _ = fit_state_model(ys, bev_s24, pd.Series(0.0, index=ys.index), exclude="chhattisgarh")
    rng = np.random.default_rng(SEED); sims = []
    _, dfA = fit_state_model(ys, bev_s24, pd.Series(0.0, index=ys.index), exclude="chhattisgarh")
    for _ in range(1000):
        cb, _ = fit_state_model(ys, bev_s24, pd.Series(0.0, index=ys.index), "chhattisgarh", idx=rng.integers(0, len(dfA), len(dfA)))
        pp = np.asarray(allocate(total, bev24, zero, cb[1], 0.0).values, float) / total
        sims.append(rng.multinomial(int(round(total)), pp / pp.sum()))
    sims = np.array(sims); A = allocate(total, bev24, zero, coefA[1], 0.0)
    loA, hiA = pd.Series(np.percentile(sims, 5, 0), idx), pd.Series(np.percentile(sims, 95, 0), idx)
    res["A_bev_only_point_in_time"] = {**score(A, truth, loA, hiA), "b": round(float(coefA[1]), 3)}
    res["baseline_bev_share_point_in_time"] = score(total * bev24 / bev24.sum(), truth)
    # (B) BEV + approximate as-of open data (OCM created / OSM last edit <= 20 Dec 2024)
    o = open_asof("2024-12-20")
    open_s = o.groupby("state_key").size()
    g = gpd.GeoDataFrame(o[o.state_key == "chhattisgarh"], geometry=gpd.points_from_xy(o[o.state_key == "chhattisgarh"].lon, o[o.state_key == "chhattisgarh"].lat), crs="EPSG:4326")
    open_d = gpd.sjoin(g, cg[["shapeName", "geometry"]], how="left", predicate="within").groupby("shapeName").size().reindex(idx).fillna(0)
    B, loB, hiB, coefB = small_area(total, bev24, open_d, ys, bev_s24, open_s, exclude="chhattisgarh")
    res["B_bev_plus_open_asof_approx"] = {**score(B, truth, loB, hiB), "b": round(float(coefB[1]), 3), "c": round(float(coefB[2]), 3),
                                          "open_sites_cg_asof": int(open_d.sum())}
    res["baseline_open_share_asof_approx"] = score(total * open_d / max(open_d.sum(), 1), truth)
    # (C) current covariates (sanity check only; not a historical test)
    bevA = cg_district_bev(None).reindex(idx).fillna(0)
    open_now = open_sites_by_district("chhattisgarh", cg, "shapeName").reindex(idx).fillna(0)
    C, loC, hiC, coefC = small_area(total, bevA, open_now, official("pib2086533"), bev_cum_at(2024, 11), open_by_state(), exclude="chhattisgarh")
    res["C_current_covariates_sanity_check"] = {**score(C, truth, loC, hiC), "b": round(float(coefC[1]), 3), "c": round(float(coefC[2]), 3)}
    pd.DataFrame({"official_dec2024_harmonised": truth, "bev_to_dec2024": bev24, "open_asof_approx": open_d,
                  "A_bev_only": A, "A_lo": loA, "A_hi": hiA, "B_bev_open": B, "B_lo": loB, "B_hi": hiB,
                  "C_current": C, "C_lo": loC, "C_hi": hiC}).to_csv(f"{OUT}/cg_district_validation_pit.csv", index_label="district")
    return {"total_allocated": total, "total_source": CG_TOTAL_SOURCE, "accounting": acct, "results": res,
            "note": "interval recipe (coefficient bootstrap + multinomial) was revised after the first Chhattisgarh comparison; coverage here is not an independent calibration test"}


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
    pd.DataFrame({"official_dec2024": truth, "bev_till_today": bev_d, "open_sites": open_d, **cands, "sa_lo": lo, "sa_hi": hi}).to_csv(f"{OUT}/cg_district_validation.csv", index_label="district")
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
    s = {"chhattisgarh_point_in_time": validate_chhattisgarh_point_in_time(), "chhattisgarh_validation_v1_superseded": validate_chhattisgarh(),
         "state_model_aug2025": state_loo()}
    json.dump(s, open(f"{OUT}/small_area_summary.json", "w"), indent=1)
    print(json.dumps(s, indent=1))
