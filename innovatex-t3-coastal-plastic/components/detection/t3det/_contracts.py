"""Contract adapters: import the lead's pydantic models from architecture/contracts/contracts.py."""
import sys

from .paths import CONTRACTS

if str(CONTRACTS) not in sys.path:
    sys.path.insert(0, str(CONTRACTS))

from contracts import Detection, FluxEstimate, FrameDetections, Provenance  # noqa: E402

__all__ = ["Detection", "FluxEstimate", "FrameDetections", "Provenance"]
