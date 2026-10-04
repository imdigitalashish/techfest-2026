"""Shared paths for the C5/C6 detection component."""
from pathlib import Path

COMP = Path(__file__).resolve().parents[1]          # components/detection
PROJECT = COMP.parents[1]                            # innovatex-t3-coastal-plastic
DATA = PROJECT / ".data" / "detection"               # gitignored
RAW = DATA / "raw"
YOLO = DATA / "yolo"
RUNS = DATA / "runs"
SPLITS = COMP / "data" / "splits"                    # committed file lists
RESULTS = COMP / "results"
CONTRACTS = PROJECT / "architecture" / "contracts"

SEED = 42
CLASSES = ["litter"]
