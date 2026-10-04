"""C5 census_completeness — the ONLY file the auto-research loop edits.

estimate(osm, ocm, ctx) -> {state_key: estimated number of public charging sites}
  osm, ocm: DataFrames with lat, lon, name, state_key (point-in-polygon state), one row per source record
  ctx: {"bev_cum": {state_key: BEV registrations till today}, "official": {state_key: official PCS} (training states only)}
"""
import numpy as np

PARAMS = {'mode': 'calib', 'radius_m': 150, 'min_matches': 3}


def _hav(lat1, lon1, lat2, lon2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371000 * np.arcsin(np.sqrt(a))


def _matches_by_state(osm, ocm, radius):
    A, B = osm[["lat", "lon"]].to_numpy(), ocm[["lat", "lon"]].to_numpy()
    D = _hav(A[:, None, 0], A[:, None, 1], B[None, :, 0], B[None, :, 1])
    nnA, nnB = D.argmin(1), D.argmin(0)
    m = {}
    for i, j in enumerate(nnA):
        if nnB[j] == i and D[i, j] <= radius:
            k = osm.iloc[i].state_key
            m[k] = m.get(k, 0) + 1
    return m


def _two_source(osm, ocm, p):
    m = _matches_by_state(osm, ocm, p["radius_m"])
    out = {}
    for k in set(osm.state_key.dropna()) | set(ocm.state_key.dropna()):
        n1, n2, mk = int((osm.state_key == k).sum()), int((ocm.state_key == k).sum()), m.get(k, 0)
        union = n1 + n2 - mk
        if p["mode"] == "union" or mk < p["min_matches"]:
            out[k] = float(union)
        else:
            out[k] = (n1 + 1) * (n2 + 1) / (mk + 1) - 1
    return out


def _calibrated(osm, ocm, ctx, p):
    """Small-area model: ln(official) = a + b ln(BEV regs) [+ c ln(observed open-data estimate)], fit on training states."""
    obs = _two_source(osm, ocm, {**p, "mode": p.get("obs", "chapman")})
    keys = sorted(set(ctx["bev_cum"]) | set(obs))
    def row(k):
        r = [1.0, np.log(ctx["bev_cum"].get(k, 0) + 1)]
        if p.get("obs"):
            r.append(np.log(obs.get(k, 0.0) + 1))
        return r
    train = [k for k in ctx["official"] if k in ctx["bev_cum"]]
    X = np.array([row(k) for k in train]); y = np.log(np.array([ctx["official"][k] for k in train], float))
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {k: float(np.exp(np.array(row(k)) @ coef)) for k in keys}


def estimate(osm, ocm, ctx):
    if PARAMS["mode"].startswith("calib"):
        return _calibrated(osm, ocm, ctx, PARAMS)
    return _two_source(osm, ocm, PARAMS)
