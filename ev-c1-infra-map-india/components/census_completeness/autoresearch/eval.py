"""FROZEN evaluator for C5 census_completeness (spike 1). The loop never edits this file.

Target: official state-wise public charging stations (PIB 2151390, 1 Aug 2025) — the best public proxy for the true
number of public charging sites (unit mismatch documented in program.md). States with official >= 100 are split
deterministically (alphabetical, alternating) into DEV and HOLDOUT. DEV is scored leave-one-state-out: the estimator
never sees the official total of the state it is predicting. HOLDOUT is only printed with --holdout (lead's check).
Metric (lower is better): median over DEV states of |ln(estimate / official)|.
Usage: .venv/bin/python -W ignore components/census_completeness/autoresearch/eval.py [--holdout]
"""
import argparse, os, re, sys, unicodedata
import numpy as np, pandas as pd, geopandas as gpd
HERE = os.path.dirname(os.path.abspath(__file__)); COMP = os.path.dirname(HERE); R = os.path.abspath(os.path.join(COMP, "..", ".."))
sys.path.insert(0, COMP)
import estimator  # noqa: E402
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))
ALIAS = {"up": "uttarpradesh", "utofdandnhanddandd": "dadraandnagarhavelianddamananddiu", "andamanandnicobar": "andamanandnicobarislands",
         "utofdnhanddd": "dadraandnagarhavelianddamananddiu", "andamanandnicobarisland": "andamanandnicobarislands"}
key = lambda s: ALIAS.get(norm(s), norm(s))
def load():
    adm = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson")[["shapeName", "geometry"]]
    def assign(df):
        g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
        j = pd.DataFrame(gpd.sjoin(g, adm, how="left", predicate="within").drop(columns=["geometry", "index_right"]))
        j["state_key"] = j.shapeName.map(lambda s: key(s) if isinstance(s, str) else None)
        return j.reset_index(drop=True)
    osm = assign(pd.read_csv(f"{R}/.data/chargers/osm_india.csv").dropna(subset=["lat", "lon"]))
    ocm = assign(pd.read_csv(f"{R}/.data/chargers/ocm_india.csv").dropna(subset=["lat", "lon"]))
    pcs = pd.read_csv(f"{R}/components/charger_ingest/data/official_pcs_statewise.csv")
    off = {key(s): int(v) for s, v in pcs[pcs.source == "pib2151390"][["state", "pcs_total"]].values}
    bev = pd.read_csv(f"{R}/eval/results/state_gap_baseline.csv")
    bev_cum = {key(s): int(v) for s, v in bev[["vahan_state", "bev_cum"]].values}
    return osm, ocm, off, bev_cum
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--holdout", action="store_true"); a = ap.parse_args()
    osm, ocm, off, bev_cum = load()
    elig = sorted(k for k, v in off.items() if v >= 100)
    dev, hold = elig[0::2], elig[1::2]
    def score(states, train_pool):
        errs = []
        for s in states:
            train = {k: off[k] for k in train_pool if k != s}
            est = estimator.estimate(osm, ocm, {"bev_cum": bev_cum, "official": train}).get(s, 0.0)
            errs.append(abs(np.log(max(est, 1.0) / off[s])))
        return float(np.median(errs)), float(np.mean(errs)), errs
    med, mean, _ = score(dev, dev)
    print(f"METRIC dev_median_abs_log_err={med:.4f}")
    print(f"secondary dev_mean_abs_log_err={mean:.4f} n_dev={len(dev)} n_holdout={len(hold)} params={estimator.PARAMS}")
    if a.holdout:
        hmed, hmean, _ = score(hold, dev)
        print(f"HOLDOUT median_abs_log_err={hmed:.4f} mean={hmean:.4f}")
if __name__ == "__main__":
    main()
