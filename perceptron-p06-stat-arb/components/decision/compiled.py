"""C8 compiled decision step: LEV (a fitted sklearn HistGradientBoostingRegressor) flattened into
arrays and evaluated by Numba, so the act/skip decision never touches the Python interpreter.

    decide(raw, x_buf, xi_buf) -> (act, value_bps)
raw is a float64[13] vector of detector scalars at episode open (RAW_FIELDS). decide() builds the
LEV feature vector exactly as components/decay/survival.add_features + decision/policies.with_net
do on the batch path, predicts E[P&L bps | x, L] and acts iff value > margin and net edge > 0.
Exactness against sklearn is checked by components/decision/test_compiled.py and eval/decision_timing.py.
"""
from __future__ import annotations

import ctypes

import numpy as np
from numba import njit

from components.decision.autoresearch.rules import LEARN_X

RAW_FIELDS = ["edge0_bps", "age_sell_us", "age_buy_us", "updater_is_sell", "spread_sell_bps", "spread_buy_bps",
              "vol_1s_bps", "sell_is_perp", "buy_is_perp", "size", "pair_id", "L_ms", "fee_bps"]
EXPECTED_X = ["log_edge", "log_age_other_ms", "updater_is_sell", "spread_sum_bps", "log_vol", "sell_is_perp", "buy_is_perp",
              "edge0_bps", "net0_bps", "log_size", "pair_id", "L_ms", "fee_bps"]
assert LEARN_X == EXPECTED_X, "LEV feature order changed; update raw_to_x"


def flatten(model):
    """Concatenate every tree of a fitted HistGradientBoostingRegressor into flat arrays."""
    trees = [preds[0] for preds in model._predictors]
    n_nodes = [len(t.nodes) for t in trees]
    off = np.concatenate([[0], np.cumsum(n_nodes)[:-1]]).astype(np.int64)
    n_bits = [t.raw_left_cat_bitsets.shape[0] for t in trees]
    boff = np.concatenate([[0], np.cumsum(n_bits)[:-1]]).astype(np.int64)
    nodes = np.concatenate([t.nodes for t in trees])
    rep = np.repeat(off, n_nodes)
    bits = [t.raw_left_cat_bitsets for t in trees if t.raw_left_cat_bitsets.shape[0]]
    raw_bits = np.concatenate(bits).astype(np.uint32) if bits else np.zeros((1, 8), np.uint32)
    known_bits, fmap = model._bin_mapper.make_known_categories_bitsets()
    perm, is_cat_col, catcode = _preprocessing(model)
    return dict(perm=perm, is_cat_col=is_cat_col, catcode=catcode,
        feat=nodes["feature_idx"].astype(np.int64), thr=nodes["num_threshold"].astype(np.float64),
        left=(nodes["left"].astype(np.int64) + rep), right=(nodes["right"].astype(np.int64) + rep),
        leaf=nodes["is_leaf"].astype(np.bool_), value=nodes["value"].astype(np.float64),
        mgl=nodes["missing_go_to_left"].astype(np.bool_), iscat=nodes["is_categorical"].astype(np.bool_),
        bidx=(nodes["bitset_idx"].astype(np.int64) + np.repeat(boff, n_nodes)),
        raw_bits=raw_bits, known_bits=np.ascontiguousarray(known_bits, dtype=np.uint32), fmap=fmap.astype(np.int64),
        roots=off, base=float(np.ravel(model._baseline_prediction)[0]), n_trees=len(trees), n_nodes=int(sum(n_nodes)))


def _preprocessing(model):
    """sklearn >= 1.6 wraps HGB inputs in a ColumnTransformer: categorical columns first (ordinal-encoded,
    unknown -> NaN), then numeric columns, each group in original order. Tree feature indices refer to that
    internal order. Returns perm[j] = original column of internal column j, a categorical flag per internal
    column, and a raw-value -> code lookup table (NaN = unknown) shared by the categorical column(s)."""
    n = model.n_features_in_
    pre = getattr(model, "_preprocessor", None)
    if pre is None:
        return np.arange(n, dtype=np.int64), np.zeros(n, np.bool_), np.full(1, np.nan)
    perm, flags, table = [], [], np.full(1, np.nan)
    for name, tr, cols in pre.transformers_:
        if name == "remainder" or tr == "drop":
            continue
        idx = np.flatnonzero(cols) if np.asarray(cols).dtype == bool else np.asarray(cols)
        perm += list(idx)
        flags += [name == "encoder"] * len(idx)
        if name == "encoder":
            if len(idx) != 1:
                raise NotImplementedError("one categorical column supported")
            cats = np.asarray(tr.categories_[0], dtype=float)
            if np.any(cats < 0) or np.any(cats != np.round(cats)):
                raise NotImplementedError("categories must be non-negative integers")
            table = np.full(int(cats.max()) + 1, np.nan)
            table[cats.astype(np.int64)] = np.arange(len(cats), dtype=float)
    return np.asarray(perm, np.int64), np.asarray(flags, np.bool_), table


def build(model, margin_bps: float = 0.0):
    """Return (predict_row, decide, raw_to_x) Numba functions with the model baked in as constants."""
    a = flatten(model)
    feat, thr, left, right, leaf, value = a["feat"], a["thr"], a["left"], a["right"], a["leaf"], a["value"]
    mgl, iscat, bidx, raw_bits, known_bits, fmap = a["mgl"], a["iscat"], a["bidx"], a["raw_bits"], a["known_bits"], a["fmap"]
    roots, base, margin = a["roots"], a["base"], float(margin_bps)
    perm, is_cat_col, catcode = a["perm"], a["is_cat_col"], a["catcode"]
    n_codes = catcode.shape[0]

    @njit(fastmath=False)
    def predict_row(x, xi):
        for j in range(perm.shape[0]):
            v = x[perm[j]]
            if is_cat_col[j]:
                c = np.int64(v)
                xi[j] = catcode[c] if (v == c and 0 <= c < n_codes) else np.nan
            else:
                xi[j] = v
        out = base
        for t in range(roots.shape[0]):
            i = roots[t]
            while not leaf[i]:
                v = xi[feat[i]]
                if np.isnan(v):
                    i = left[i] if mgl[i] else right[i]
                elif iscat[i]:
                    if v < 0:
                        i = left[i] if mgl[i] else right[i]
                    else:
                        c = np.int64(v)
                        if (raw_bits[bidx[i], c >> 5] >> np.uint32(c & 31)) & np.uint32(1):
                            i = left[i]
                        elif (known_bits[fmap[feat[i]], c >> 5] >> np.uint32(c & 31)) & np.uint32(1):
                            i = right[i]
                        else:
                            i = left[i] if mgl[i] else right[i]
                else:
                    i = left[i] if v <= thr[i] else right[i]
            out += value[i]
        return out

    @njit(fastmath=False)
    def raw_to_x(r, x):
        edge, age_s, age_b, upd = r[0], r[1], r[2], r[3]
        x[0] = np.log(max(edge, 1e-6))
        x[1] = np.log1p(max((age_b if upd > 0.5 else age_s) / 1000.0, 0.0))
        x[2] = upd
        x[3] = r[4] + r[5]
        x[4] = np.log1p(max(r[6], 0.0))
        x[5] = r[7]
        x[6] = r[8]
        x[7] = edge
        x[8] = edge - 2.0 * r[12]
        x[9] = np.log(max(r[9], 1e-6))
        x[10] = r[10]
        x[11] = r[11]
        x[12] = r[12]

    @njit(fastmath=False)
    def decide(r, x, xi):
        raw_to_x(r, x)
        v = predict_row(x, xi)
        return (v > margin) and (x[8] > 0.0), v

    return predict_row, decide, raw_to_x, a


# ---------------------------------------------------------------- in-kernel timing (Apple Silicon)
_libc = ctypes.CDLL("/usr/lib/libSystem.dylib")
_mach_absolute_time = _libc.mach_absolute_time
_mach_absolute_time.restype = ctypes.c_uint64
_mach_absolute_time.argtypes = []


class _TB(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]


def ns_per_tick() -> float:
    tb = _TB()
    _libc.mach_timebase_info(ctypes.byref(tb))
    return tb.numer / tb.denom


def make_timer(decide):
    """Numba loop that times every decide() call with mach_absolute_time (ticks)."""
    clock = _mach_absolute_time

    @njit
    def timed(R, out_ticks, out_val):
        x = np.empty(13)
        xi = np.empty(13)
        acts = 0
        for k in range(R.shape[0]):
            t0 = clock()
            a, v = decide(R[k], x, xi)
            t1 = clock()
            out_ticks[k] = t1 - t0
            out_val[k] = v
            acts += a
        return acts

    return timed
