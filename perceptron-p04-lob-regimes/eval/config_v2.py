"""v2 configuration — frozen by eval/PREREGISTRATION.md before any v2 result is computed.

Day set: every Tardis.dev free day (the first of each month) for Binance USD-M BTCUSDT from
2023-01-01 to 2026-10-01, i.e. all free days and therefore no selection. Split by calendar year:
train 2023 · dev 2024 (tuning only) · holdout 2025-01 … 2026-10 (reported once, never tuned on).
v1 (eval/config.py) stays untouched so the overnight results remain reproducible.
"""
from copy import deepcopy

from config import CFG, H_STEPS, STEP_S  # noqa: F401  (same grid and horizon as v1)

SPLIT_V2 = {
    "train": [f"2023-{m:02d}-01" for m in range(1, 13)],
    "dev": [f"2024-{m:02d}-01" for m in range(1, 13)],
    "holdout": [f"2025-{m:02d}-01" for m in range(1, 13)] + [f"2026-{m:02d}-01" for m in range(1, 11)],
}
ALL_DAYS = SPLIT_V2["train"] + SPLIT_V2["dev"] + SPLIT_V2["holdout"]

CFG_V2 = deepcopy(CFG)
CFG_V2.update({
    # Calibrated rolling KS on features whose *levels* are comparable across months (ratchet cand_003);
    # thresholds = 0.999 quantile of the leave-one-train-day-out null (CFG["ksc"]).
    "ks_sets": {"lean": ["spread_ticks", "rv_60s_bps", "ofi1_5s_n", "qi1", "ret_5s_bps"]},
    # Harm gate defaults; threshold and boost length are chosen on dev by the pre-registered rule.
    "harm": {"k": 0.0, "threshold": 20.0, "min_n": 60, "cooldown": 600},
    "gbdt": {"stride": 4, "max_iter": 200, "learning_rate": 0.05, "max_leaf_nodes": 31, "l2": 1.0},
    "wf_stride": 10,  # = horizon, so walk-forward refits see non-overlapping labels
    "exec_delays_ms": [0, 100],
    # Binance USDⓈ-M Futures fee schedule (USDT), https://www.binance.com/en/fee/futureFee, accessed 2026-10-04.
    "fees_bps": {"regular": {"maker": 2.0, "taker": 5.0}, "vip9": {"maker": 0.0, "taker": 1.7}},
    "policies_dev": ["static_snorm", "ks_refit", "regime_gated", "fixed_share", "fs_coin", "fs_coin_harm",
                     "spike", "static_gbdt"],
    "policies_holdout": ["static_snorm", "static_wf", "ks_refit", "ksc_refit", "periodic_refit", "online_sgd",
                         "regime_gated", "fixed_share", "fs_coin", "fs_coin_harm", "spike", "spike_wf",
                         "static_gbdt", "spike_gbdt"],
})
