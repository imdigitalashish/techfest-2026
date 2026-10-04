"""Load the project contracts (architecture/contracts/contracts.py) without packaging the repo."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONTRACTS = PROJECT_ROOT / "architecture" / "contracts"
if str(_CONTRACTS) not in sys.path:
    sys.path.insert(0, str(_CONTRACTS))

from contracts import (  # noqa: E402
    ClearanceRecord, DashboardBundle, InterceptorSeries, LedgerEntry, Provenance, Reconciliation, Site,
)

__all__ = ["PROJECT_ROOT", "ClearanceRecord", "DashboardBundle", "InterceptorSeries", "LedgerEntry",
           "Provenance", "Reconciliation", "Site"]
