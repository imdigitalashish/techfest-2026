"""Demo figure: one day, static model vs spike — price, alarms, mixer weights, rolling log-loss.

    cd perceptron-p04-lob-regimes && nice -n 10 python eval/plot_day.py 2024-05-01

Uses the v2 training context (2023 days only). 2024-05-01 is a dev day with an FOMC statement at
18:00 UTC (federalreserve.gov); the figure is illustrative, not a holdout claim.
Writes deliverables/figures/day_<date>.png.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from config_v2 import CFG_V2, SPLIT_V2  # noqa: E402
from run_baseline import load_events  # noqa: E402
from run_v2 import load_day  # noqa: E402

from components.adapter import POLICIES, build_context, run_episode  # noqa: E402
from components.evaluator import pointwise_logloss  # noqa: E402


def rolling_mean(x: np.ndarray, w: int) -> np.ndarray:
    m = ~np.isnan(x)
    c = np.concatenate([[0.0], np.cumsum(np.where(m, x, 0.0))])
    k = np.concatenate([[0], np.cumsum(m)])
    idx = np.arange(len(x))
    lo = np.maximum(idx + 1 - w, 0)
    return (c[idx + 1] - c[lo]) / np.maximum(k[idx + 1] - k[lo], 1)


def main(day: str) -> None:
    ctx = build_context([load_day(d) for d in SPLIT_V2["train"]], CFG_V2)
    f, l = load_day(day)
    res = {n: run_episode(n, f, l, ctx, POLICIES[n]) for n in ("static_snorm", "ks_refit", "spike")}
    hours = (f.grid_us - f.grid_us[0]) / 3.6e9 + (f.grid_us[0] % 86_400_000_000) / 3.6e9
    fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True, gridspec_kw={"height_ratios": [2, 1, 2, 2]})
    ax[0].plot(hours, f.mid, lw=0.6, color="k")
    ax[0].set_ylabel("BTCUSDT mid")
    for e_id, e_us in load_events().get(day, []):
        for a in ax:
            a.axvline((e_us % 86_400_000_000) / 3.6e9, color="tab:red", ls="--", lw=1)
        ax[0].text((e_us % 86_400_000_000) / 3.6e9, f.mid.max(), f" {e_id}", color="tab:red", va="top", fontsize=8)
    for row, (name, color) in enumerate((("ks_refit", "tab:gray"), ("spike", "tab:blue"))):
        for al in res[name].alarms:
            ax[1].plot(hours[al.step], row + (0.3 if al.detector == "harm_cusum" else 0), "|", color=color, ms=10)
    ax[1].set_yticks([0, 1, 1.3], ["textbook KS (all alarms)", "spike: calibrated KS", "spike: harm gate"])
    ax[1].set_ylim(-0.5, 1.8)
    w = res["spike"].extra["w_trace"]
    names = res["spike"].extra["head_names"]
    th = hours[::60][: w.shape[0]]
    groups = {"regime heads": [i for i, n in enumerate(names) if "regime" in n],
              "abstain (p=0.5)": [i for i, n in enumerate(names) if "coin" in n],
              "static / online / periodic": [i for i, n in enumerate(names) if "regime" not in n and "coin" not in n]}
    ax[2].stackplot(th, *[w[: len(th), idx].sum(1) for idx in groups.values()], labels=list(groups), alpha=0.8)
    ax[2].set_ylabel("spike mixer weight")
    ax[2].legend(loc="upper left", fontsize=8)
    for name, color in (("static_snorm", "tab:orange"), ("ks_refit", "tab:gray"), ("spike", "tab:blue")):
        ll = pointwise_logloss(res[name].p_up, l.y)
        ax[3].plot(hours, rolling_mean(ll, 1800), lw=0.9, color=color, label=name)
    ax[3].axhline(np.log(2), color="k", lw=0.8, ls=":", label="coin flip (ln 2)")
    ax[3].set_ylabel("30-min rolling log-loss")
    ax[3].set_xlabel("hour (UTC)")
    ax[3].legend(loc="upper left", fontsize=8)
    fig.suptitle(f"{day}: static model vs textbook KS→refit vs spike (trained on 2023 only)", fontsize=11)
    fig.tight_layout()
    out = ROOT / "deliverables" / "figures" / f"day_{day}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=110)
    print(out, {n: round(float(np.nanmean(pointwise_logloss(r.p_up, l.y))), 4) for n, r in res.items()},
          datetime.now(timezone.utc).isoformat(timespec="seconds"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2024-05-01")
