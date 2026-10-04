"""C7 decay — opportunity lifetime (survival) models and the MVP decay report.

Baseline: Kaplan–Meier (no covariates, optionally per group).
Spike v0: Weibull AFT with covariates, S(t|x) = exp(-(t / exp(x·β))^ρ), with a numpy fast path
for the decision loop (µs per call) cross-checked against lifelines.
Durations are in milliseconds on the exchange (truth) clock; 1 µs is added so zero-length
episodes (open/close at the same timestamp) are valid for parametric fits.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl
from lifelines import KaplanMeierFitter, WeibullAFTFitter
from lifelines.utils import concordance_index

PERP_VENUES = ("binance-futures", "okex-swap", "bybit", "deribit", "hyperliquid")
FEATURES = ["log_edge", "log_age_other_ms", "updater_is_sell", "spread_sum_bps", "log_vol", "sell_is_perp", "buy_is_perp"]
T_GRID_MS = np.array([0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000], dtype=float)


def add_features(opp: pl.DataFrame) -> pl.DataFrame:
    is_perp = lambda c: pl.col(c).str.split(":").list.first().is_in(list(PERP_VENUES)).cast(pl.Float64)  # noqa: E731
    return opp.with_columns(
        pl.col("edge0_bps").clip(1e-6).log().alias("log_edge"),
        (pl.when(pl.col("updater_is_sell")).then(pl.col("age_buy_us")).otherwise(pl.col("age_sell_us")) / 1000.0)
        .clip(0).log1p().alias("log_age_other_ms"),
        pl.col("updater_is_sell").cast(pl.Float64),
        (pl.col("spread_sell_bps") + pl.col("spread_buy_bps")).alias("spread_sum_bps"),
        pl.col("vol_1s_bps").clip(0).log1p().alias("log_vol"),
        is_perp("sell_venue").alias("sell_is_perp"),
        is_perp("buy_venue").alias("buy_is_perp"),
        ((pl.col("duration_us") + 1) / 1000.0).alias("T_ms"),
        (~pl.col("censored")).cast(pl.Int8).alias("E"),
    )


def km_summary(opp: pl.DataFrame, by: list[str] | None = None) -> pl.DataFrame:
    rows = []
    groups = [((), opp)] if not by else opp.group_by(by, maintain_order=True)
    for key, g in groups:
        if g.height < 20:
            continue
        km = KaplanMeierFitter().fit(g["T_ms"].to_numpy(), g["E"].to_numpy())
        sf = km.survival_function_at_times(T_GRID_MS).to_numpy()
        q = lambda p: float(km.percentile(p))  # time at which S(t) = p  # noqa: E731
        row = {"n": g.height, "censored_frac": float(1 - g["E"].mean()), "half_life_ms": q(0.5), "t_S90_ms": q(0.9),
               "t_S10_ms": q(0.1), "mean_edge0_bps": float(g["edge0_bps"].mean())}
        row.update({f"S({t:g}ms)": float(s) for t, s in zip(T_GRID_MS, sf)})
        if by:
            row.update(dict(zip(by, key if isinstance(key, tuple) else (key,))))
        rows.append(row)
    return pl.DataFrame(rows)


@dataclass
class DecayModel:
    kind: str
    beta: np.ndarray | None = None   # AFT coefficients for lambda (incl. intercept last)
    rho: float | None = None
    mu: np.ndarray | None = None
    sd: np.ndarray | None = None
    km_t: np.ndarray | None = None
    km_s: np.ndarray | None = None

    def survival(self, t_ms: np.ndarray, X: np.ndarray | None = None) -> np.ndarray:
        t_ms = np.atleast_1d(np.asarray(t_ms, dtype=float))
        if self.kind == "km":
            idx = np.searchsorted(self.km_t, t_ms, side="right") - 1
            s = np.where(idx >= 0, self.km_s[np.clip(idx, 0, None)], 1.0)
            n = 1 if X is None else X.shape[0]
            return np.broadcast_to(s, (n, t_ms.size)).copy()
        Z = (X - self.mu) / self.sd
        lam = np.exp(Z @ self.beta[:-1] + self.beta[-1])          # scale per row
        return np.exp(-np.power(t_ms[None, :] / lam[:, None], self.rho))


def fit_km(opp: pl.DataFrame) -> DecayModel:
    km = KaplanMeierFitter().fit(opp["T_ms"].to_numpy(), opp["E"].to_numpy())
    sf = km.survival_function_
    return DecayModel("km", km_t=sf.index.to_numpy().astype(float), km_s=sf.iloc[:, 0].to_numpy())


class KMByPair:
    """Kaplan–Meier stratified by ordered venue pair (falls back to the pooled curve)."""

    kind = "km_pair"

    def __init__(self, opp: pl.DataFrame, min_n: int = 30):
        self.pooled = fit_km(opp)
        self.tab: dict[float, tuple[np.ndarray, np.ndarray]] = {}
        for (pid,), g in opp.group_by(["pair_id"]):
            if g.height >= min_n:
                sf = KaplanMeierFitter().fit(g["T_ms"].to_numpy(), g["E"].to_numpy()).survival_function_
                self.tab[float(pid)] = (sf.index.to_numpy().astype(float), sf.iloc[:, 0].to_numpy())

    def s_rowwise(self, pair_ids: np.ndarray, t_ms: np.ndarray) -> np.ndarray:
        t_ms = np.broadcast_to(np.asarray(t_ms, dtype=float), pair_ids.shape)
        out = np.empty(pair_ids.shape[0])
        for pid in np.unique(pair_ids):
            m = pair_ids == pid
            tt, ss = self.tab.get(float(pid), (self.pooled.km_t, self.pooled.km_s))
            i = np.searchsorted(tt, t_ms[m], side="right") - 1
            out[m] = np.where(i >= 0, ss[np.clip(i, 0, None)], 1.0)
        return out

    def survival(self, t_ms: np.ndarray, X: np.ndarray) -> np.ndarray:
        pid = np.asarray(X).reshape(-1)
        return np.stack([self.s_rowwise(pid, np.full(pid.shape, t)) for t in np.atleast_1d(t_ms)], axis=1)


def fit_weibull_aft(opp: pl.DataFrame, max_rows: int = 400_000, seed: int = 0) -> DecayModel:
    d = opp.select(FEATURES + ["T_ms", "E"])
    if d.height > max_rows:
        d = d.sample(max_rows, seed=seed)
    X = d.select(FEATURES).to_numpy()
    mu, sd = X.mean(0), X.std(0) + 1e-9
    pdf = d.to_pandas()
    pdf[FEATURES] = (X - mu) / sd
    aft = WeibullAFTFitter(penalizer=1e-3).fit(pdf, duration_col="T_ms", event_col="E")
    p = aft.params_
    beta = np.array([p.loc[("lambda_", f)] for f in FEATURES] + [p.loc[("lambda_", "Intercept")]])
    rho = float(np.exp(p.loc[("rho_", "Intercept")]))
    return DecayModel("weibull_aft", beta=beta, rho=rho, mu=mu, sd=sd)


def model_X(model, opp: pl.DataFrame) -> np.ndarray:
    return opp["pair_id"].to_numpy() if getattr(model, "kind", "") == "km_pair" else opp.select(FEATURES).to_numpy()


def brier_at(model, opp: pl.DataFrame, t_ms: np.ndarray) -> np.ndarray:
    """Brier score at each horizon; samples censored before a horizon are excluded (censoring is rare here)."""
    T, E = opp["T_ms"].to_numpy(), opp["E"].to_numpy().astype(bool)
    S = model.survival(t_ms, model_X(model, opp))
    out = []
    for j, t in enumerate(t_ms):
        known = (T > t) | E
        y = (T > t).astype(float)
        out.append(float(np.mean((S[known, j] - y[known]) ** 2)))
    return np.array(out)


def evaluate(model, test: pl.DataFrame) -> dict:
    grid = np.array([0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, 250, 500, 1000], dtype=float)
    b = brier_at(model, test, grid)
    ibs = float(np.trapezoid(b, np.log(grid)) / (np.log(grid[-1]) - np.log(grid[0])))
    if model.kind == "km":
        cidx = 0.5
    elif model.kind == "km_pair":
        cidx = float(concordance_index(test["T_ms"].to_numpy(), model.survival(np.array([10.0]), model_X(model, test))[:, 0],
                                       test["E"].to_numpy()))
    else:
        X = test.select(FEATURES).to_numpy()
        med = np.exp(((X - model.mu) / model.sd) @ model.beta[:-1] + model.beta[-1]) * np.log(2) ** (1 / model.rho)
        cidx = float(concordance_index(test["T_ms"].to_numpy(), med, test["E"].to_numpy()))
    return {"kind": model.kind, "ibs_logt": ibs, "c_index": cidx, "brier": dict(zip(map(float, grid), map(float, b)))}
