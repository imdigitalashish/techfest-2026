"""Fetch WHO 2006 Child Growth Standards tables into .data/raw/ and verify SHA-256.

- LMS tables: WHO `anthro` R package data-raw (GPL-3.0), pinned to commit b776d8a (30 Jan 2026). Only the
  public WHO parameter tables are downloaded; no package code is used.
- Expanded z-score tables (validation reference): cdn.who.int, as linked from
  https://www.who.int/tools/child-growth-standards/standards (accessed 4 Oct 2026).
Run: .venv/bin/python -m components.growth_standards.fetch_who
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / ".data" / "raw"
SHA = "b776d8a12b1c97369c748b561159fd2ec4f4db58"
GH = f"https://raw.githubusercontent.com/WorldHealthOrganization/anthro/{SHA}/data-raw/growthstandards/"
CDN = "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/"

FILES = {
    "who_gs/acanthro.txt": (GH + "acanthro.txt", "1b588802bc66534abb42ead27fe6f8e8d62b26967d764eecf16d0f4a8660a7bd"),
    "who_gs/bmianthro.txt": (GH + "bmianthro.txt", "78a4364e99303114fb2c458d28d64c6d10ac33832a5d5b2d437bc5cea1c93a0d"),
    "who_gs/hcanthro.txt": (GH + "hcanthro.txt", "e794e46f06b91223ad2c6435148dc08794a1d75b67613a652c3151201a98bf7c"),
    "who_gs/lenanthro.txt": (GH + "lenanthro.txt", "709f7a11881451daf7820f022d363d5bdb93746b5361d6bd9218af6ff838e0c2"),
    "who_gs/ssanthro.txt": (GH + "ssanthro.txt", "3e6e1bce0cd87998b5f061a44730860f1393cf8f6b1f5545f80b372085b40ea1"),
    "who_gs/tsanthro.txt": (GH + "tsanthro.txt", "babc2a2a6252080f4ad9ca39a27e59248142820add3151e76d959dd104146a48"),
    "who_gs/weianthro.txt": (GH + "weianthro.txt", "bc15a6a623dd1d5beaeed1497666332aa54bc4ccd15ff9658c487d79694ab77b"),
    "who_gs/wfhanthro.txt": (GH + "wfhanthro.txt", "0050d31041c2f7d4f8a34f27e8066fd73a24806835b9e4a0de1a7ee46d54d582"),
    "who_gs/wflanthro.txt": (GH + "wflanthro.txt", "ad470cf41b147bd2a16026e57fd17968df7bf746b9f0bf2ff85df95239643778"),
    "who_sd/wfa-boys-zscore-expanded.xlsx": (CDN + "weight-for-age/expanded-tables/wfa-boys-zscore-expanded-tables.xlsx?sfvrsn=65cce121_10", "b5b4748c6bfa5230e2eddafa1767629c349178b08d457f400b59422b8bfef86c"),
    "who_sd/wfa-girls-zscore-expanded.xlsx": (CDN + "weight-for-age/expanded-tables/wfa-girls-zscore-expanded-tables.xlsx?sfvrsn=f01bc813_10", "ee3ae12cb96c6c5541cdf43665c03ce6c984f877859a183a5f6104eb06a49a6e"),
    "who_sd/lhfa-boys-zscore-expanded.xlsx": (CDN + "length-height-for-age/expandable-tables/lhfa-boys-zscore-expanded-tables.xlsx?sfvrsn=7b4a3428_12", "c4b1c9029ab9751a5f0888e32f35c7c0287a16d361885cf911ecf23b3f7f6b4f"),
    "who_sd/lhfa-girls-zscore-expanded.xlsx": (CDN + "length-height-for-age/expandable-tables/lhfa-girls-zscore-expanded-tables.xlsx?sfvrsn=27f1e2cb_10", "6aa2876319449a6b1f4d825848128902114ff53c67b92b86a0c5140846013059"),
    "who_sd/wfl-boys-zscore-expanded.xlsx": (CDN + "weight-for-length-height/expanded-tables/wfl-boys-zscore-expanded-table.xlsx?sfvrsn=d307434f_8", "1a6e9a002d2692d038161bc6572a10f8b9fa0657163808141d2981a2132c59cc"),
    "who_sd/wfl-girls-zscore-expanded.xlsx": (CDN + "weight-for-length-height/expanded-tables/wfl-girls-zscore-expanded-table.xlsx?sfvrsn=db7b5d6b_8", "ec116b8e618ad311d34a87231346badf16c75f5c4f82222ec846e05c582bf16a"),
    "who_sd/wfh-boys-zscore-expanded.xlsx": (CDN + "weight-for-length-height/expanded-tables/wfh-boys-zscore-expanded-tables.xlsx?sfvrsn=ac60cb13_8", "ed3b590f9c65937a138408b13618f33684bb6406a0c56d6a2ce3fd9053a3f59f"),
    "who_sd/wfh-girls-zscore-expanded.xlsx": (CDN + "weight-for-length-height/expanded-tables/wfh-girls-zscore-expanded-tables.xlsx?sfvrsn=daac732c_8", "fca340d5f04aa1556ac410b176b65b290e1b9ff467fc854a97f9b54ad94c9b8a"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    bad = 0
    for rel, (url, digest) in FILES.items():
        dest = ROOT / rel
        if not (dest.exists() and sha256(dest) == digest):
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                dest.write_bytes(r.read())
        ok = sha256(dest) == digest
        bad += not ok
        print(("ok  " if ok else "BAD ") + rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
