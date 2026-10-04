"""Demo engine: every number is computed by the committed P10 code paths on the committed bundle.

Committed code used here: eval.run_baselines.split/ALPHA/SEED, QuantileFusion.predict, cqr_offset, features_from_docs,
inject_seq, oracle_grid, CertifiedCQR (deletion box + tree interval propagation), trust_of, aci_from_bounds.
The only demo-specific piece is `_BoosterModel`, which loads the bundled LightGBM model text (bit-exact round trip,
verified by demo/export.py) and exposes the two attributes the committed code reads: `booster_` and `predict`.
Never import torch here (torch + LightGBM in one process segfaults on macOS); text scoring runs in scorer_worker.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from components.attack.inject import PUMP_TEMPLATE, inject_seq, oracle_grid
from components.conformal.methods import aci_from_bounds, cqr_offset
from components.fusion.lgbm_quantile import FEATURE_SETS, TEXT_COLS, QuantileFusion
from components.robust_conformal.certify import CertifiedCQR, docs_lookup, features_from_docs
from components.trust_scorer.heuristic import trust_of
from eval.run_baselines import ALPHA, SEED, split

DEMO = Path(__file__).resolve().parent
PROJECT = DEMO.parent
BUNDLE = DEMO / "bundle"
GAMMA = 0.01  # ACI step, as in eval/run_baselines.py
LEVEL_NAMES = ("q_lo", "q_med", "q_hi")
FEATURE_LABELS = {"log_n_docs": "log(1 + #posts)", "sent_mean": "mean sentiment", "sent_trim": "20% trimmed mean",
                  "sent_std": "sentiment std", "trust_mean": "mean trust"}


class _BoosterModel:
    """Duck-types the fitted LGBMRegressor attributes used by committed code (`booster_`, `predict`)."""

    def __init__(self, path: Path):
        self.booster_ = lgb.Booster(model_str=path.read_text())

    def predict(self, X):
        return self.booster_.predict(X)


def _f(x) -> float | None:
    x = float(x)
    return x if np.isfinite(x) else None


class Engine:
    def __init__(self, bundle: Path = BUNDLE):
        self.showcase = json.loads((bundle / "showcase.json").read_text())
        self.manifest = json.loads((bundle / "manifest.json").read_text())
        self.committed = json.loads((PROJECT / "eval/results/text_minilm_v2.json").read_text())
        self.djia = json.loads((PROJECT / "eval/results/text_utility_djia_v1.json").read_text())
        self.djia_x = json.loads((PROJECT / "eval/results/exploratory_djia_v2.json").read_text())
        panel = pd.read_parquet(bundle / "panel_caltest.parquet")
        docs = pd.read_parquet(bundle / "docs_caltest.parquet")
        _, cal, test = split(panel)
        self.cal, self.test = cal.reset_index(drop=True), test.reset_index(drop=True)
        fm = QuantileFusion(FEATURE_SETS["fusion"], ALPHA, SEED)
        fm.models = [_BoosterModel(bundle / f"model_{n}.txt") for n in LEVEL_NAMES]
        self.fm = fm
        self.Q = cqr_offset(fm, self.cal)
        self.ti = [fm.cols.index(c) for c in TEXT_COLS]
        self.X = self.test[fm.cols].to_numpy(float)
        self.Xc = self.cal[fm.cols].to_numpy(float)
        self.y = self.test["y"].to_numpy(float)
        self.yc = self.cal["y"].to_numpy(float)
        self.dates = self.test["trade_date"].to_numpy()
        self.udates = np.unique(self.dates)
        self.test_docs = docs_lookup(docs, self.test)
        self.cal_docs = docs_lookup(docs, self.cal)
        p, pc = fm.predict(self.test), fm.predict(self.cal)
        self.p_lo, self.p_med, self.p_hi = (p[c].to_numpy() for c in ("q_lo", "q_med", "q_hi"))
        self.c_lb, self.c_ub = pc["q_lo"].to_numpy(), pc["q_hi"].to_numpy()
        self.base_lo, self.base_hi = self.p_lo - self.Q, self.p_hi + self.Q
        self.base_cov = (self.y >= self.base_lo) & (self.y <= self.base_hi)
        self.key = {(t, str(d)[:10]): i for i, (t, d) in enumerate(zip(self.test["ticker"], self.test["trade_date"]))}
        self._cc: dict[int, CertifiedCQR] = {}
        self._cal_raw: dict[int, tuple[np.ndarray, np.ndarray]] = {}
        self._flip_cache: dict[tuple[int, int], list] = {}
        st: dict = {}
        lo, hi = aci_from_bounds(self.c_lb, self.c_ub, self.yc, self.p_lo, self.p_hi, self.y, self.dates, ALPHA, GAMMA, stats=st)
        self.aci_clean = self._aci_summary(lo, hi, st)

    # ---------- helpers ----------
    def cc(self, k: int) -> CertifiedCQR:
        if k not in self._cc:
            self._cc[k] = CertifiedCQR(self.fm, self.Q, k)
        return self._cc[k]

    def cal_raw(self, k: int):
        if k not in self._cal_raw:
            self._cal_raw[k] = self.cc(k).raw_bounds(self.Xc, self.cal_docs)
        return self._cal_raw[k]

    def _daily(self, covered: np.ndarray) -> np.ndarray:
        s = pd.Series(covered.astype(float)).groupby(self.dates).mean()
        return s.reindex(self.udates).to_numpy()

    def _aci_summary(self, lo, hi, stats=None) -> dict:
        cov = (self.y >= lo) & (self.y <= hi)
        daily = self._daily(cov)
        roll = pd.Series(daily).rolling(20, min_periods=1).mean().to_numpy()
        cum = np.cumsum(daily) / np.arange(1, len(daily) + 1)
        out = {"coverage": float(cov.mean()), "mean_day_coverage": float(daily.mean()),
               "mean_width": float(np.mean((hi - lo)[np.isfinite(hi - lo) & (lo <= hi)])),
               "dates": [str(d)[:10] for d in self.udates], "daily": daily.round(5).tolist(),
               "rolling20": roll.round(5).tolist(), "cumulative": cum.round(5).tolist()}
        if stats:
            out["alpha_range"] = [stats.get("alpha_min"), stats.get("alpha_max")]
        return out

    def row_of(self, ticker: str, date: str) -> int:
        return self.key[(ticker, date)]

    def random_row(self, seed: int | None = None) -> int:
        return int(np.random.default_rng(seed).integers(len(self.test)))

    @staticmethod
    def trust(followers, age_days, verified, n_cashtags) -> float:
        return float(trust_of(followers, age_days, verified, n_cashtags)[0])

    def _frame_rows(self, i: int, feats: np.ndarray) -> pd.DataFrame:
        df = self.test.iloc[np.repeat(i, len(feats))].reset_index(drop=True)
        Xv = np.repeat(self.X[i][None], len(feats), 0)
        Xv[:, self.ti] = feats
        df[self.fm.cols] = Xv
        return df

    def _plain_and_cert(self, i: int, docs_list: list, k: int):
        feats = np.stack([features_from_docs(s, w) for s, w in docs_list])
        df = self._frame_rows(i, feats)
        p = self.fm.predict(df)
        Xv = df[self.fm.cols].to_numpy(float)
        c_lo, c_hi = self.cc(k).intervals(Xv, docs_list)
        return feats, p, p["q_lo"].to_numpy() - self.Q, p["q_hi"].to_numpy() + self.Q, c_lo, c_hi

    # ---------- per-day ----------
    def day(self, i: int) -> dict:
        t = self.test.iloc[i]
        date = str(t["trade_date"])[:10]
        sc = next((d for d in self.showcase["days"] if d["ticker"] == t["ticker"] and d["date"] == date), None)
        s, w = self.test_docs[i]
        return {"row": i, "ticker": t["ticker"], "date": date, "n_real_posts": int(len(s)), "y": float(self.y[i]),
                "showcase": sc, "real_scores": [{"sentiment": float(a), "trust": float(b)} for a, b in zip(s, w)],
                "clean": {"lo": float(self.base_lo[i]), "hi": float(self.base_hi[i]), "med": float(self.p_med[i]),
                          "covers": bool(self.base_cov[i])}}

    def attack(self, i: int, inj_s: list[float], inj_w: list[float], k: int) -> dict:
        s0, w0 = self.test_docs[i]
        s, w = inject_seq(s0, w0, inj_s, inj_w)
        feats, p, lo, hi, c_lo, c_hi = self._plain_and_cert(i, [(s, w)], k)
        Xv = self._frame_rows(i, feats)[self.fm.cols].to_numpy(float)
        b_lo, b_hi = self.cc(k).boxes(Xv, [(s, w)])
        cc0_lo, cc0_hi = self.cc(k).intervals(self.X[i][None], [self.test_docs[i]])
        n_inj, y = len(inj_s), self.y[i]
        clean_f = self.X[i, self.ti]
        box = [{"feature": c, "label": FEATURE_LABELS[c], "lo": float(b_lo[0, j]), "hi": float(b_hi[0, j]),
                "clean": float(clean_f[n]), "attacked": float(feats[0, n]),
                "clean_inside": bool(b_lo[0, j] <= clean_f[n] <= b_hi[0, j])}
               for n, (c, j) in enumerate(zip(TEXT_COLS, self.ti))]
        return {
            "row": i, "k": k, "n_injected": n_inj, "within_budget": n_inj <= k, "y": float(y),
            "clean": {"lo": float(self.base_lo[i]), "hi": float(self.base_hi[i]), "med": float(self.p_med[i]),
                      "covers": bool(self.base_cov[i])},
            "clean_certified": {"lo": float(cc0_lo[0]), "hi": float(cc0_hi[0])},
            "plain": {"lo": float(lo[0]), "hi": float(hi[0]), "med": float(p["q_med"].iloc[0]),
                      "covers": bool(lo[0] <= y <= hi[0])},
            "certified": {"lo": float(c_lo[0]), "hi": float(c_hi[0]), "covers": bool(c_lo[0] <= y <= c_hi[0]),
                          "contains_clean": bool(c_lo[0] <= self.base_lo[i] and c_hi[0] >= self.base_hi[i])},
            "median_shift": float(p["q_med"].iloc[0] - self.p_med[i]),
            "box": box,
        }

    def flips(self, i: int, k: int) -> dict:
        """Which committed oracle_grid(k) variants, injected into this day's real posts, flip plain CQR?"""
        if (i, k) not in self._flip_cache:
            grid = oracle_grid(k) if k >= 1 else []
            out = []
            if grid:
                s0, w0 = self.test_docs[i]
                dl = [inject_seq(s0, w0, sv, tv) for sv, tv in grid]
                _, p, lo, hi, c_lo, c_hi = self._plain_and_cert(i, dl, k)
                y = self.y[i]
                for n, (sv, tv) in enumerate(grid):
                    out.append({"sents": list(sv), "trusts": list(tv), "n": len(sv),
                                "plain_covers": bool(lo[n] <= y <= hi[n]),
                                "plain_lo": float(lo[n]), "plain_hi": float(hi[n]),
                                "cert_contains_clean": bool(c_lo[n] <= self.base_lo[i] and c_hi[n] >= self.base_hi[i]),
                                "cert_covers": bool(c_lo[n] <= y <= c_hi[n])})
            self._flip_cache[(i, k)] = out
        out = self._flip_cache[(i, k)]
        flipping = [v for v in out if not v["plain_covers"]] if self.base_cov[i] else []
        return {"row": i, "k": k, "n_variants": len(out), "n_flipping": len(flipping),
                "flipping": flipping[:12], "n_flipping_cert_survives": sum(v["cert_contains_clean"] for v in flipping),
                "clean_covers": bool(self.base_cov[i])}

    def redteam(self, i: int, k: int, n: int = 2000, seed: int = 0, beyond: bool = True) -> dict:
        """Random attacks against one day: n within budget (1..k posts) and, optionally, n beyond it (k+1..k+5)."""
        rng = np.random.default_rng(seed)
        s0, w0 = self.test_docs[i]
        res = {"row": i, "k": k, "seed": seed}
        for name, (j_lo, j_hi) in (("within", (1, k)), ("beyond", (k + 1, k + 5))):
            if (name == "within" and k < 1) or (name == "beyond" and not beyond):
                continue
            js = rng.integers(j_lo, j_hi + 1, n)
            dl, specs = [], []
            for j in js:
                ext = rng.random(j) < 0.5
                sv = np.where(ext, rng.choice([-1.0, 1.0], j), rng.uniform(-1, 1, j))
                ext_t = rng.random(j) < 0.5
                tv = np.where(ext_t, rng.choice([0.05, 1.0], j), rng.uniform(0.05, 1.0, j))
                dl.append(inject_seq(s0, w0, sv, tv))
                specs.append((sv, tv))
            _, p, lo, hi, c_lo, c_hi = self._plain_and_cert(i, dl, k)
            y = self.y[i]
            plain_miss = ~((y >= lo) & (y <= hi))
            contain_fail = ~((c_lo <= self.base_lo[i]) & (c_hi >= self.base_hi[i]))
            cert_miss = ~((y >= c_lo) & (y <= c_hi))
            gap = np.maximum(lo - y, y - hi)
            wi = int(np.argmax(gap))
            res[name] = {"n": int(n), "posts_range": [int(j_lo), int(j_hi)],
                         "plain_broken": int(np.sum(plain_miss & self.base_cov[i])),
                         "cert_containment_violations": int(contain_fail.sum()),
                         "cert_missed_y_when_clean_covered": int(np.sum(cert_miss & self.base_cov[i])),
                         "median_shift_max_abs": float(np.max(np.abs(p["q_med"].to_numpy() - self.p_med[i]))),
                         "worst_for_plain": {"n_posts": int(js[wi]), "sents": np.round(specs[wi][0], 3).tolist(),
                                             "trusts": np.round(specs[wi][1], 3).tolist(),
                                             "plain_lo": float(lo[wi]), "plain_hi": float(hi[wi]),
                                             "cert_lo": float(c_lo[wi]), "cert_hi": float(c_hi[wi])}}
        return res

    # ---------- population replay ----------
    def population(self, inj_s: list[float], inj_w: list[float], k: int) -> dict:
        """Inject the same posts into every test stock-day; recompute plain/certified CQR and plain ACI / CR-ACI."""
        adocs = [inject_seq(s, w, inj_s, inj_w) for s, w in self.test_docs]
        Xa = self.X.copy()
        Xa[:, self.ti] = np.stack([features_from_docs(*d) for d in adocs])
        ta = self.test.copy()
        ta[self.fm.cols] = Xa
        p = self.fm.predict(ta)
        va_lb, va_ub = p["q_lo"].to_numpy(), p["q_hi"].to_numpy()
        lo, hi = va_lb - self.Q, va_ub + self.Q
        y = self.y
        plain_cov = (y >= lo) & (y <= hi)
        lb, ub = self.cc(k).raw_bounds(Xa, adocs)
        c_lo, c_hi = lb - self.Q, ub + self.Q
        cert_cov = (y >= c_lo) & (y <= c_hi)
        contains = (c_lo <= self.base_lo) & (c_hi >= self.base_hi)
        shift = p["q_med"].to_numpy() - self.p_med
        st_p, st_c = {}, {}
        alo, ahi = aci_from_bounds(self.c_lb, self.c_ub, self.yc, va_lb, va_ub, y, self.dates, ALPHA, GAMMA, stats=st_p)
        clb, cub = self.cal_raw(k)
        rlo, rhi = aci_from_bounds(clb, cub, self.yc, lb, ub, y, self.dates, ALPHA, GAMMA, stats=st_c)
        n_inj = len(inj_s)
        return {
            "k": k, "n_injected": n_inj, "within_budget": n_inj <= k, "n_rows": int(len(y)),
            "clean_plain_coverage": float(self.base_cov.mean()),
            "plain_coverage": float(plain_cov.mean()), "plain_width": float(np.mean(hi - lo)),
            "certified_coverage": float(cert_cov.mean()), "certified_width": float(np.mean(c_hi - c_lo)),
            "flipped_by_attack": int(np.sum(self.base_cov & ~plain_cov)),
            "rescued_by_attack": int(np.sum(~self.base_cov & plain_cov)),
            "certified_contains_clean_all_rows": bool(contains.all()),
            "certified_contains_clean_frac": float(contains.mean()),
            "certified_covers_all_clean_covered": bool(np.all(cert_cov[self.base_cov])),
            "median_shift_mean": float(shift.mean()), "median_shift_p95_abs": float(np.quantile(np.abs(shift), 0.95)),
            "aci_plain": self._aci_summary(alo, ahi, st_p), "cr_aci": self._aci_summary(rlo, rhi, st_c),
        }

    # ---------- committed anchors for the honest panel ----------
    def meta(self) -> dict:
        c = self.committed
        fus = c["ablation"]["fusion"]
        pump = c["attack"]["pump"]
        orc = c["attack"]["oracle"]
        w0 = orc["worst3"][0]
        widths = {k: c["spike"][f"clean_k{k}"]["mean_width"] for k in (1, 2, 3, 5)}
        base_w = orc["vanilla_clean_width"]
        return {
            "n_test": int(len(self.test)), "n_test_days": int(len(self.udates)),
            "test_period": [str(self.udates[0])[:10], str(self.udates[-1])[:10]], "alpha": ALPHA, "gamma": GAMMA,
            "Q": self.Q, "pump_template": PUMP_TEMPLATE.format(cashtag="$XYZ"),
            "showcase": {k: v for k, v in self.showcase.items() if k != "days"},
            "showcase_days": [{k: v for k, v in d.items() if k != "posts"} for d in self.showcase["days"]],
            "aci_clean_live": self.aci_clean,
            "committed": {
                "file": "eval/results/text_minilm_v2.json",
                "split_cov": fus["split"]["coverage"], "split_cov_highvol": fus["split"]["cov[vol=high]"],
                "cqr_cov": fus["cqr_mapie"]["coverage"], "aci_cov": fus["cqr_aci"]["coverage"],
                "aci_mean_day_cov": fus["cqr_aci"]["mean_day_coverage"], "aci_ci90": fus["cqr_aci"]["mean_day_coverage_ci90"],
                "aci_width": fus["cqr_aci"]["mean_width"],
                "pump_sentiment": pump["pump_sentiment"], "pump_trust": pump["pump_trust"],
                "pump_shift_mean": pump["median_shift_mean"], "pump_shift_p95": pump["median_shift_p95_abs"],
                "pump_plain_cov": pump["vanilla_cqr"]["coverage"], "pump_cert_cov": pump["certified"]["coverage"],
                "cr_aci_pump_cov": c["spike"]["cr_aci"]["cr_aci_pump"]["coverage"],
                "aci_pump_cov": c["spike"]["cr_aci"]["cqr_aci_pump"]["coverage"],
                "clean_sym_cqr_cov": orc["clean_cqr_coverage"], "oracle_plain_cov": orc["vanilla_cqr_oracle_coverage"],
                "grid_size": orc["grid_size"], "sym_cqr_width": base_w,
                "worst_fixed": {"sents": w0["sents"], "trusts": w0["trusts"], "plain": w0["vanilla_coverage"],
                                "cert": w0["certified_coverage"]},
                "width_cost": {str(k): v / base_w - 1 for k, v in widths.items()},
                "beyond": c["attack"]["beyond_budget"],
            },
            "djia": {"file": "eval/results/text_utility_djia_v1.json",
                     "winkler_price_only": self.djia["models"]["price_only"]["winkler"],
                     "winkler_fusion": self.djia["models"]["fusion"]["winkler"],
                     "p": self.djia["primary"]["p_one_sided"], "decision": self.djia["primary"]["decision"],
                     "control_detects": self.djia_x["C_positive_control"]["noise_1.0"]["relative_improvement"],
                     "control_p": self.djia_x["C_positive_control"]["noise_1.0"]["p_one_sided"]},
            "bundle": {"exported": self.manifest["exported"], "checks": self.manifest["checks"]},
        }
