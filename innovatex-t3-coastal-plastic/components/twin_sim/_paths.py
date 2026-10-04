"""Paths and the contracts import (contracts.py lives in architecture/contracts/, owned by the lead)."""
from __future__ import annotations

import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
SLUG = PKG.parents[1]                      # innovatex-t3-coastal-plastic/
RAW = SLUG / ".data" / "twin_sim" / "raw"  # gitignored raw downloads
DATA = PKG / "data"                        # small processed files (committed)
RESULTS = PKG / "results"

_c = str(SLUG / "architecture" / "contracts")
if _c not in sys.path:
    sys.path.insert(0, _c)
import contracts as C  # noqa: E402,F401
