"""C9 adoption_forecast — the ONLY file the auto-research loop edits.
forecast(bev, allv) -> {state: BEV registrations forecast for the year after the last column}
  bev, allv: DataFrames (index = VAHAN state label, columns = calendar years as int, values = registrations); only years <= origin.
"""
import numpy as np

PARAMS = {'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def forecast(bev, allv):
    p = PARAMS
    yrs = sorted(bev.columns)
    last, prev = bev[yrs[-1]], bev[yrs[-2]]
    if p["method"] == "naive":
        f = last
    elif p["method"] == "growth":
        g = (last + 1) / (prev + 1) - 1
        f = last * (1 + p.get("phi", 1.0) * g)
    elif p["method"] == "pooled_growth":
        g_s = (last + 1) / (prev + 1) - 1
        g_n = last.sum() / prev.sum() - 1
        f = last * (1 + p.get("phi", 1.0) * (p["w"] * g_s + (1 - p["w"]) * g_n))
    elif p["method"] == "share_logit":
        k = p.get("k", 3)
        ys = yrs[-k:]
        share = (bev[ys] + 0.5) / (allv[ys] + 1)
        L = _logit(share.to_numpy())
        x = np.arange(k) - (k - 1) / 2
        slope_s = (L * x).sum(1) / (x ** 2).sum()
        nat = _logit((bev[ys].sum() + 0.5) / (allv[ys].sum() + 1)).to_numpy()
        slope_n = (nat * x).sum() / (x ** 2).sum()
        slope = p.get("phi", 1.0) * (p["w"] * slope_s + (1 - p["w"]) * slope_n)
        nxt = L[:, -1] + slope
        tot_growth = allv[yrs[-1]].sum() / allv[yrs[-2]].sum()
        f = (1 / (1 + np.exp(-nxt))) * allv[yrs[-1]].to_numpy() * tot_growth
        return {s: float(v) for s, v in zip(bev.index, f)}
    else:
        raise ValueError(p["method"])
    return {s: float(v) for s, v in f.items()}
