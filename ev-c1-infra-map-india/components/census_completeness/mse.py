"""C5 census_completeness v1 — three-source capture–recapture (log-linear multiple-systems estimation), validated
against official state totals.

Lists: OSM (Overpass, Oct 2026), Open Charge Map (export, Apr 2026), Overture places (2026-09-23.1; category
ev_charging_station OR strict EV-name rule). Records are linked across lists into *sites*: mutual nearest neighbours
within R metres for every source pair, then connected components. Each site gets a capture history (osm, ocm, ovt).
Per region: Poisson log-linear models on the 7 observed cells (Fienberg 1972), model chosen by AIC; N0 = exp(intercept)
is the estimated number of sites missed by all lists. 90% CI by nonparametric bootstrap of sites (B = 300, fixed model).
Validation: official public charging stations by state (PIB 2151390, as of 1 Aug 2025) — bias (median log ratio),
median |log ratio|, and 90% CI coverage across states with >= 100 official stations.
Reproduce: fetch_osm.py, fetch_ocm.py, fetch_overture.py, official_pcs.py, then
  .venv/bin/python -W ignore components/census_completeness/mse.py
"""
from __future__ import annotations

import itertools
import json
import os
import re
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

R_ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(R_, "eval", "results")
RADIUS_M = 150
SEED = 20261004
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))  # noqa: E731
ALIAS = {"up": "uttarpradesh", "utofdandnhanddandd": "dadraandnagarhavelianddamananddiu", "andamanandnicobar": "andamanandnicobarislands",
         "andamanandnicobarisland": "andamanandnicobarislands", "utofdnhanddd": "dadraandnagarhavelianddamananddiu"}
key = lambda s: ALIAS.get(norm(s), norm(s))  # noqa: E731


def load_sources() -> pd.DataFrame:
    adm = gpd.read_file(f"{R_}/.data/geo/ind_adm1.geojson")[["shapeName", "geometry"]]
    frames = []
    for src, path in (("osm", "osm_india.csv"), ("ocm", "ocm_india.csv"), ("ovt", "overture_india.csv")):
        d = pd.read_csv(f"{R_}/.data/chargers/{path}").dropna(subset=["lat", "lon"])
        d = d[["source_id", "lat", "lon", "name"]].assign(src=src)
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    g = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs="EPSG:4326")
    j = gpd.sjoin(g, adm, how="inner", predicate="within").drop(columns=["geometry", "index_right"])
    j["state_key"] = j.shapeName.map(key)
    return pd.DataFrame(j).reset_index(drop=True)


def hav(a, b):
    p = np.pi / 180
    x = np.sin((b[None, :, 0] - a[:, None, 0]) * p / 2) ** 2 + np.cos(a[:, None, 0] * p) * np.cos(b[None, :, 0] * p) * np.sin((b[None, :, 1] - a[:, None, 1]) * p / 2) ** 2
    return 2 * 6371000 * np.arcsin(np.sqrt(x))


def link(d: pd.DataFrame, radius=RADIUS_M) -> pd.DataFrame:
    """Mutual-nearest-neighbour edges within `radius` for each source pair, then connected components = sites."""
    rows, cols = [], []
    for s1, s2 in itertools.combinations(["osm", "ocm", "ovt"], 2):
        ia, ib = np.where(d.src == s1)[0], np.where(d.src == s2)[0]
        D = hav(d.loc[ia, ["lat", "lon"]].to_numpy(), d.loc[ib, ["lat", "lon"]].to_numpy())
        nnA, nnB = D.argmin(1), D.argmin(0)
        for i, j in enumerate(nnA):
            if nnB[j] == i and D[i, j] <= radius:
                rows.append(ia[i]); cols.append(ib[j])
    n = len(d)
    A = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    d = d.assign(site=lab)
    return d


def histories(d: pd.DataFrame) -> pd.DataFrame:
    h = d.groupby("site").agg(state_key=("state_key", "first"), osm=("src", lambda s: int("osm" in set(s))),
                               ocm=("src", lambda s: int("ocm" in set(s))), ovt=("src", lambda s: int("ovt" in set(s))))
    return h


PATTERNS = [p for p in itertools.product([0, 1], repeat=3) if any(p)]
INTER = {"OC": (0, 1), "OV": (0, 2), "CV": (1, 2)}
MODELS = [()] + [(k,) for k in INTER] + [tuple(c) for c in itertools.combinations(INTER, 2)] + [tuple(INTER)]


def design(model):
    X = []
    for p in PATTERNS:
        row = [1.0, *p] + [p[INTER[k][0]] * p[INTER[k][1]] for k in model]
        X.append(row)
    return np.array(X, float)


def fit(y: np.ndarray, model) -> tuple[float, float] | None:
    """Poisson IRLS on the 7 observed cells; returns (N0, AIC) or None if it fails / is degenerate."""
    X = design(model)
    if X.shape[1] > len(y):
        return None
    beta = np.linalg.lstsq(X, np.log(y + 0.5), rcond=None)[0]
    for _ in range(100):
        eta = np.clip(X @ beta, -30, 30); mu = np.exp(eta)
        z = eta + (y - mu) / mu
        W = mu
        try:
            new = np.linalg.solve(X.T @ (W[:, None] * X), X.T @ (W * z))
        except np.linalg.LinAlgError:
            return None
        if np.max(np.abs(new - beta)) < 1e-8:
            beta = new
            break
        beta = new
    mu = np.exp(np.clip(X @ beta, -30, 30))
    ll = float(np.sum(y * np.log(np.where(mu > 0, mu, 1e-300)) - mu))
    n0 = float(np.exp(np.clip(beta[0], -30, 30)))
    if not np.isfinite(n0) or n0 > 1e6:
        return None
    return n0, 2 * X.shape[1] - 2 * ll


def mse(cells: np.ndarray, rng: np.random.Generator, B=300):
    n_obs = int(cells.sum())
    fits = {m: fit(cells, m) for m in MODELS}
    fits = {m: f for m, f in fits.items() if f is not None}
    if not fits:
        return None
    m_best = min(fits, key=lambda m: fits[m][1])
    est = n_obs + fits[m_best][0]
    boots = []
    p = cells / n_obs
    for _ in range(B):
        yb = rng.multinomial(n_obs, p).astype(float)
        f = fit(yb, m_best)
        if f is not None:
            boots.append(n_obs + f[0])
    lo, hi = (np.percentile(boots, [5, 95]) if len(boots) >= 50 else (np.nan, np.nan))
    return {"n_obs": n_obs, "model": "+".join(m_best) or "indep", "N_hat": round(est, 1), "ci90_lo": round(float(lo), 1),
            "ci90_hi": round(float(hi), 1), "n_boot_ok": len(boots)}


def cells_of(h: pd.DataFrame) -> np.ndarray:
    c = h.groupby(["osm", "ocm", "ovt"]).size()
    return np.array([float(c.get(p, 0)) for p in PATTERNS])


def main():
    rng = np.random.default_rng(SEED)
    d = link(load_sources())
    h = histories(d)
    os.makedirs(OUT, exist_ok=True)
    d[["src", "source_id", "lat", "lon", "name", "state_key", "site"]].to_csv(f"{OUT}/c5_linked_records.csv", index=False)
    pcs = pd.read_csv(f"{R_}/components/charger_ingest/data/official_pcs_statewise.csv")
    off = {key(s): int(v) for s, v in pcs[pcs.source == "pib2151390"][["state", "pcs_total"]].values}
    rows = []
    for st, g in h.groupby("state_key"):
        c = cells_of(g)
        r = mse(c, rng) or {"n_obs": int(c.sum()), "model": "none", "N_hat": np.nan, "ci90_lo": np.nan, "ci90_hi": np.nan, "n_boot_ok": 0}
        r.update({"state_key": st, "official_pcs_aug2025": off.get(st), "in_all3": int(c[-1]),
                  **{f"cell_{''.join(map(str, p))}": int(v) for p, v in zip(PATTERNS, c)},
                  "n_osm": int(g.osm.sum()), "n_ocm": int(g.ocm.sum()), "n_ovt": int(g.ovt.sum())})
        rows.append(r)
    st = pd.DataFrame(rows)
    st["union_over_official"] = (st.n_obs / st.official_pcs_aug2025).round(3)
    st["mse_over_official"] = (st.N_hat / st.official_pcs_aug2025).round(3)
    st["official_in_ci90"] = (st.official_pcs_aug2025 >= st.ci90_lo) & (st.official_pcs_aug2025 <= st.ci90_hi)
    st.to_csv(f"{OUT}/c5_mse_by_state.csv", index=False)
    nat_c = cells_of(h)
    nat = mse(nat_c, rng)
    ev = st[(st.official_pcs_aug2025 >= 100) & st.N_hat.notna()]
    lr = np.log(ev.N_hat / ev.official_pcs_aug2025)
    lu = np.log(ev.n_obs / ev.official_pcs_aug2025)
    summary = {
        "radius_m": RADIUS_M, "records": {s: int((d.src == s).sum()) for s in ("osm", "ocm", "ovt")}, "sites_linked": int(len(h)),
        "national_cells": {"".join(map(str, p)): int(v) for p, v in zip(PATTERNS, nat_c)},
        "national_mse": nat, "official_national_aug2025": int(sum(off.values())), "ieefa_national_jul2026": 52718,
        "states_evaluated": int(len(ev)), "states_with_mse": int(st.N_hat.notna().sum()),
        "bias_median_log_ratio_mse": round(float(np.median(lr)), 3), "median_abs_log_ratio_mse": round(float(np.median(np.abs(lr))), 3),
        "bias_median_log_ratio_union": round(float(np.median(lu)), 3), "median_abs_log_ratio_union": round(float(np.median(np.abs(lu))), 3),
        "ci90_coverage_of_official": round(float(ev.official_in_ci90.mean()), 3),
        "median_mse_over_official": round(float(np.median(ev.N_hat / ev.official_pcs_aug2025)), 3),
        "median_union_over_official": round(float(np.median(ev.n_obs / ev.official_pcs_aug2025)), 3),
        "passes_state_check": bool(np.median(np.abs(lr)) < np.log(1.25) and ev.official_in_ci90.mean() >= 0.8),
        "pass_rule": "median |ln(MSE/official)| < ln 1.25 AND 90% CI covers official in >= 80% of states (states with >= 100 official PCS)",
    }
    json.dump(summary, open(f"{OUT}/c5_mse_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print(ev.sort_values("official_pcs_aug2025", ascending=False)[["state_key", "n_osm", "n_ocm", "n_ovt", "in_all3", "n_obs", "model", "N_hat", "ci90_lo", "ci90_hi", "official_pcs_aug2025", "mse_over_official"]].head(14).to_string(index=False))


if __name__ == "__main__":
    main()
