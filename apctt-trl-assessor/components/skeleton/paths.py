"""Resource lookup: packaged `resources/` (submission build) first, then the repo layout (development)."""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "resources"
REPO = HERE.parents[1]  # apctt-trl-assessor/ when running from the repo


def resource(packaged_name: str, repo_relative: str) -> Path:
    p = RES / packaged_name
    return p if p.exists() else REPO / repo_relative
