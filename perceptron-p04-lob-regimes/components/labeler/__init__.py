"""C3 Labeler: FeatureFrame -> Labels (direction of mid over h steps, with availability time).

y[t] = 1 if mid[t+h] > mid[t], 0 if mid[t+h] < mid[t], NaN on ties or past the end of the day.
The label for step t is only *known* at step t+h (avail_step), which the adapter enforces:
online updates never consume a label before it would have been observed live.
No smoothing over future windows (the FI-2010-style smoothed label mixes future prices
into the target definition; we keep the raw point-to-point label).
"""
from __future__ import annotations

import numpy as np

from components.contracts import FeatureFrame, Labels


def make_labels(frame: FeatureFrame, h_steps: int) -> Labels:
    T = frame.mid.shape[0]
    mid = frame.mid
    fut = np.full(T, np.nan)
    fut[:-h_steps] = mid[h_steps:]
    move = (fut - mid) / mid * 1e4
    y = np.where(move > 0, 1.0, np.where(move < 0, 0.0, np.nan))
    y[np.isnan(fut)] = np.nan
    avail = np.arange(T, dtype=np.int64) + h_steps
    return Labels(h_steps=h_steps, y=y, avail_step=avail, move_bps=move)
