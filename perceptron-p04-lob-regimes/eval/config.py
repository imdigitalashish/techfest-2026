"""Frozen evaluation configuration (the split never changes once results are reported).

train:   fit scalers, heads, regime edges and the KS reference — nothing else touches these days.
dev:     the auto-research ratchet may tune on these days only.
holdout: reported, never tuned on; re-checked by the lead to catch metric gaming.
"""
SPLIT = {
    "train": ["2023-02-01", "2023-08-01"],
    "dev": ["2023-09-01", "2023-11-01", "2023-12-01"],
    "holdout": ["2024-05-01", "2024-11-01", "2025-08-01"],
}

STEP_S = 1.0
H_STEPS = 10  # 10 s horizon at a 1 s decision grid

CFG = {
    "C": 1.0,
    "ewma_halflife_steps": 1800,
    "sgd_l2": 1e-3,
    "refit_lam": 50.0,
    "fs_eta": 1.0,
    "fs_alpha": 1e-3,
    "fs_alpha_boost": 0.05,
    "fs_boost_steps": 120,
    "ks_features": ["spread_ticks", "log_depth5", "rv_60s_bps", "log_msgs_10s", "ofi1_5s_n", "qi1", "ret_5s_bps"],
    "ks_subsample": 10,
    "ks": {"window": 600, "subsample": 10, "stride": 30, "alpha": 1e-3, "persist": 3, "cooldown": 1800},
    "ph": {"delta": 0.005, "threshold": 25.0, "min_n": 300},
}
