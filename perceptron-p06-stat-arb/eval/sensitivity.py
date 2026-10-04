"""Amendment 1 of eval/PREREGISTRATION-walkforward-12d.md — sensitivity analyses S1–S4, plus EXPLORATORY comparisons.

Worlds (train on day i−1, test on day i, same 13 days / 5 legs / cells / statistics as the primary test):
  V0 frozen      — primary cells (frozen simulator); reproduces the registered result and adds extra policies
  V1 strict      — strict simulator (next-published-quote fills, 1 s staleness cap, no size-0 intents), basis mark
  V2 strict+mo1  — V1 fills, positions marked at mids 1 s after arrival (markout)
  V3 strict+mo10 — same with a 10 s markout
  V4 transfer    — policies trained on frozen labels, scored on V1 outcomes
S3: in V1–V4, selected intents that hit a (venue, side, quote) already hit by an earlier selected intent of the same
policy in the same cell are flagged; totals are also reported with flagged intents dropped.
Registered decision: "robust" iff LEV − threshold keeps both 95% lower bounds > 0 in V1 AND V2.
Exploratory (not registered): LEV − gbm_clf, LEV − LEV-without-latency-feature, LEV − ridge; leave-one-day-out.
Usage: eval/run_guarded.sh .venv/bin/python -m eval.sensitivity --days <13 days> --subset unseen7:<days>
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time

import numpy as np
import polars as pl
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from components.decision.autoresearch import rules as R
from eval.falsification import cached_cells, compare
from eval.strict_cells import strict_cells

LABELS = ["pnl_usd", "pnl_bps", "outcome"]
NO_L_X = [x for x in R.LEARN_X if x != "L_ms"]
NUM_X = [x for x in R.LEARN_X if x != "pair_id"]


def fit_ridge(train: pl.DataFrame) -> dict:
    pairs = sorted(train["pair_id"].unique().to_list())
    def design(df):
        oh = np.stack([(df["pair_id"].to_numpy() == p).astype(float) for p in pairs], axis=1)
        return np.hstack([df.select(NUM_X).to_numpy(), oh])
    X = design(train)
    sc = StandardScaler().fit(X)
    m = Ridge(alpha=1.0).fit(sc.transform(X), np.clip(train["pnl_bps"].to_numpy(), -30, 30))
    return {"m": m, "sc": sc, "design": design}


def act_ridge(m: dict, rows: pl.DataFrame) -> np.ndarray:
    return m["m"].predict(m["sc"].transform(m["design"](rows))) > 0


POLICIES = {
    "naive": (lambda tr: None, lambda m, te: np.ones(te.height, dtype=bool)),
    "threshold_pair": (lambda tr: R.fit_threshold(tr, ["pair_id", "fee_bps", "delta_ms"]), R.act_threshold),
    "ev_kmpair": (lambda tr: R.fit_ev(tr, ["pair_id"]), R.act_ev),
    "gbm_clf": (lambda tr: R.fit_gbm_clf(tr), R.act_gbm_clf),
    "lev": (lambda tr: R.fit_gbm_reg(tr), R.act_gbm_reg),
    "lev_edge_only": (lambda tr: R.fit_gbm_reg(tr, x=R.EDGE_ONLY_X), R.act_gbm_reg),
    "ridge": (fit_ridge, act_ridge),                                                   # S4
    "lev_noclip": (lambda tr: R.fit_gbm_reg(tr, clip=1000.0), R.act_gbm_reg),          # S4
    "lev_noL": (lambda tr: R.fit_gbm_reg(tr, x=NO_L_X), R.act_gbm_reg),                # exploratory
}
REGISTERED = [("lev", "threshold_pair"), ("gbm_clf", "threshold_pair"), ("ev_kmpair", "threshold_pair"), ("threshold_pair", "naive"),
              ("lev", "lev_edge_only"), ("ridge", "threshold_pair"), ("lev_noclip", "threshold_pair")]
EXPLORATORY = [("lev", "gbm_clf"), ("lev", "lev_noL"), ("lev", "ridge")]


def relabel(df: pl.DataFrame, which: str | None) -> pl.DataFrame:
    if which is None:
        return df
    return df.with_columns(pl.col(f"pnl_usd_{which}").alias("pnl_usd"), pl.col(f"pnl_bps_{which}").alias("pnl_bps"))


def collisions(ch: pl.DataFrame) -> np.ndarray:
    """Flag rows (in time order within each fee/latency cell) that reuse a (venue, side, quote) already hit."""
    flag = np.zeros(ch.height, dtype=bool)
    if ch.height == 0 or "snap_s" not in ch.columns:
        return flag
    d = ch.with_row_index("_r").sort("t_decide_us")
    for _, g in d.group_by(["fee_bps", "delta_ms"]):
        seen = set()
        for r, sv, ss, bv, sb in zip(g["_r"], g["sell_venue"], g["snap_s"], g["buy_venue"], g["snap_b"]):
            ks, kb = (sv, "bid", ss), (bv, "ask", sb)
            if (ss >= 0 and ks in seen) or (sb >= 0 and kb in seen):
                flag[r] = True
            if ss >= 0:
                seen.add(ks)
            if sb >= 0:
                seen.add(kb)
    return flag


def score(models: dict, test: pl.DataFrame) -> dict:
    feats = test.drop([c for c in LABELS if c in test.columns])
    out = {}
    for name, (m, act) in models.items():
        mask = np.asarray(act(m, feats), dtype=bool)
        ch = test.filter(pl.Series(mask))
        fl = collisions(ch)
        out[name] = {"total": float(ch["pnl_usd"].sum()) if ch.height else 0.0, "n": ch.height,
                     "flagged_share": float(fl.mean()) if ch.height else 0.0,
                     "flagged_pnl": float(ch.filter(pl.Series(fl))["pnl_usd"].sum()) if fl.any() else 0.0,
                     "total_dropped": float(ch.filter(pl.Series(~fl))["pnl_usd"].sum()) if ch.height else 0.0}
    return out


def fit_all(train: pl.DataFrame) -> dict:
    return {name: (fit(train), act) for name, (fit, act) in POLICIES.items()}


def summarise(per_day: dict[str, dict], subsets: dict, key: str = "total") -> dict:
    days = sorted(per_day)
    tab = {p: np.array([per_day[d][p][key] for d in days]) for p in POLICIES}
    res = {"days": days, "table": {p: tab[p].tolist() for p in POLICIES}, "registered": {}, "exploratory": {}, "subsets": {}, "loo": {}}
    for a, b in REGISTERED:
        res["registered"][f"{a} - {b}"] = compare(tab[a] - tab[b], tab[b])
    for a, b in EXPLORATORY:
        res["exploratory"][f"{a} - {b}"] = compare(tab[a] - tab[b], tab[b])
    for name, sub in subsets.items():
        idx = [i for i, d in enumerate(days) if d in sub]
        res["subsets"][name] = {f"{a} - {b}": compare((tab[a] - tab[b])[idx], tab[b][idx]) for a, b in [("lev", "threshold_pair"), ("lev", "gbm_clf")]}
    d = tab["lev"] - tab["threshold_pair"]
    res["loo"] = {"min_loo_mean": float(min(np.delete(d, i).mean() for i in range(d.size))),
                  "max_day_share_of_total": float(d.max() / d.sum()) if d.sum() > 0 else float("nan")}
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", nargs="+", required=True)
    ap.add_argument("--subset", action="append", default=[])
    ap.add_argument("--out", default="sensitivity_amendment1")
    a = ap.parse_args()
    t0 = time.time()
    subsets = {x.split(":", 1)[0]: x.split(":", 1)[1].split(",") for x in a.subset}
    frozen, strict, fps, excluded = {}, {}, {}, {}
    for d in a.days:
        frozen[d] = cached_cells(d)[0]
        sc, fps[d] = strict_cells(d)
        excluded[d] = int((~sc["valid"]).sum())          # erratum: marks/unwinds unavailable past the end of the data
        strict[d] = sc.filter(pl.col("valid"))
        print(f"cells {d}: frozen {frozen[d].height} strict {strict[d].height} excluded {excluded[d]} ({time.time() - t0:.0f}s)", flush=True)
    worlds = {k: {} for k in ("V0_frozen", "V1_strict", "V2_strict_mo1", "V3_strict_mo10", "V4_transfer")}
    for prev, cur in zip(a.days[:-1], a.days[1:]):
        m_frozen = fit_all(frozen[prev])
        worlds["V0_frozen"][cur] = score(m_frozen, frozen[cur])
        worlds["V4_transfer"][cur] = score(m_frozen, strict[cur])
        for w, lab in (("V1_strict", None), ("V2_strict_mo1", "mo1"), ("V3_strict_mo10", "mo10")):
            worlds[w][cur] = score(fit_all(relabel(strict[prev], lab)), relabel(strict[cur], lab))
        print("scored", cur, f"({time.time() - t0:.0f}s)", flush=True)
    res = {"worlds": {w: summarise(v, subsets) for w, v in worlds.items()},
           "collision_dropped": {w: summarise(v, subsets, "total_dropped") for w, v in worlds.items() if w != "V0_frozen"},
           "collisions": {w: {p: float(np.mean([v[d][p]["flagged_share"] for d in v])) for p in POLICIES} for w, v in worlds.items()},
           "per_day_raw": worlds, "fingerprints": fps, "excluded_rows_unavailable_marks": excluded}
    v1, v2 = res["worlds"]["V1_strict"]["registered"]["lev - threshold_pair"], res["worlds"]["V2_strict_mo1"]["registered"]["lev - threshold_pair"]
    robust = all(x["ci95"][0] > 0 and x["t_ci95"][0] > 0 for x in (v1, v2))
    res["decision"] = "robust" if robust else "dependent on the frozen simulator's optimistic fills or basis marking"
    res["runtime_s"] = time.time() - t0
    res["commit"] = (os.environ.get("P6_COMMIT") or subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip())
    res["command"] = "eval/run_guarded.sh .venv/bin/python -m eval.sensitivity " + " ".join(__import__("sys").argv[1:])
    json.dump(res, open(f"eval/results/{a.out}.json", "w"), indent=1, default=str)

    def row(k, v):
        return (f"| {k} | {v['mean_usd_per_day']:+,.1f} | [{v['t_ci95'][0]:+,.1f}, {v['t_ci95'][1]:+,.1f}] | [{v['ci95'][0]:+,.1f}, {v['ci95'][1]:+,.1f}] | "
                f"{v['days_positive']}/{v['n_days']} | {v['wilcoxon_p']:.4f} |")
    hdr = ["| comparison | mean USD/day | 95% t-CI | 95% bootstrap CI | days + | Wilcoxon p |", "|---|---|---|---|---|---|"]
    L = ["# Amendment 1 — sensitivity analyses S1–S4 (+ exploratory comparisons)", "",
         f"Registered decision rule: **{res['decision']}** (LEV − tuned threshold must keep both 95% lower bounds > 0 in V1 and V2).", "",
         "Worlds: V0 frozen simulator (reproduces the primary) · V1 strict fills, basis mark · V2 strict fills, 1 s markout · "
         "V3 strict fills, 10 s markout · V4 frozen-trained policies scored on strict outcomes. P&L = sum over 6 fee/latency scenarios, USD/day.", ""]
    for w, s in res["worlds"].items():
        L += [f"## {w}", "", "| policy | " + " | ".join(s["days"]) + " |", "|---|" + "---|" * len(s["days"])]
        for p in POLICIES:
            L.append(f"| {p} | " + " | ".join(f"{x:,.0f}" for x in s["table"][p]) + " |")
        L += ["", "Registered comparisons:", ""] + hdr + [row(k, v) for k, v in s["registered"].items()]
        L += ["", "Exploratory (not registered):", ""] + hdr + [row(k, v) for k, v in s["exploratory"].items()]
        for name, sub in s["subsets"].items():
            L += ["", f"Subset {name}:", ""] + hdr + [row(k, v) for k, v in sub.items()]
        L += ["", f"Leave-one-day-out: min mean(LEV − threshold) = {s['loo']['min_loo_mean']:+,.1f}; largest single-day share of the total uplift = "
              f"{s['loo']['max_day_share_of_total']:.1%}.", ""]
        if w in res["collision_dropped"]:
            c = res["collision_dropped"][w]["registered"]["lev - threshold_pair"]
            L += [f"S3 shared liquidity: flagged share LEV {res['collisions'][w]['lev']:.1%}, threshold {res['collisions'][w]['threshold_pair']:.1%}; "
                  f"with flagged intents dropped, LEV − threshold = {c['mean_usd_per_day']:+,.1f}/day, t-CI [{c['t_ci95'][0]:+,.1f}, {c['t_ci95'][1]:+,.1f}], "
                  f"{c['days_positive']}/{c['n_days']} days.", ""]
    L += [f"Erratum (Amendment 1): strict rows whose markout or unwind quote lies beyond the end of the data are excluded for every policy; "
          f"excluded rows per day: {json.dumps(excluded)} (total {sum(excluded.values())}).", ""]
    L += [f"Runtime {res['runtime_s']:.0f} s · commit `{res['commit']}` · `{res['command']}`", ""]
    open(f"eval/results/{a.out}.md", "w").write("\n".join(L))
    print("\n".join(L[:6]))


if __name__ == "__main__":
    main()
