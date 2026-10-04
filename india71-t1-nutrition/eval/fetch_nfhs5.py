#!/usr/bin/env python3
"""
fetch_nfhs5.py — Re-download NFHS-5 (2019-21) district & state fact-sheet
compilations and rebuild tidy CSVs for the India@71 Theme-1 nutrition demo.

Sources (both CC-BY-4.0 / public re-publications of official IIPS PDF fact
sheets at https://rchiips.org/nfhs/ , archived under the new domain
https://www.nfhsiips.in/):

1. District level (707 districts, 29 states + 8 UTs, NFHS-5 vs NFHS-4):
   https://raw.githubusercontent.com/SaiSiddhardhaKalla/NFHS/main/India.csv
   Repo: https://github.com/SaiSiddhardhaKalla/NFHS (includes the source
   IIPS PDFs under /pdfs/<state>/<district> — used in this project to spot
   -verify 3 districts x 4 anthropometry indicators = 12/12 exact matches,
   see research/sources/R7b-data-sources.md).

2. State level (37 rows: India + 28 states + 8 UTs, urban/rural/total,
   131 indicators), CC-BY-4.0, citable via https://doi.org/10.7910/DVN/42WNZF
   https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-States.csv
   Repo: https://github.com/pratapvardhan/NFHS-5

Outputs (written under .data/raw/nfhs5/, which is gitignored):
   - India_raw.csv                 (raw download, district-level, cached)
   - NFHS-5-States_raw.csv         (raw download, state-level, cached)
   - nfhs5_district_tidy.csv       (tidy: state, district, indicator, ...)
   - nfhs5_state.csv               (tidy: state-level child anthropometry only)

Usage:
    .venv/bin/python eval/fetch_nfhs5.py
    .venv/bin/python eval/fetch_nfhs5.py --no-download   # rebuild from cache only
"""
import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd
import requests

DISTRICT_CSV_URL = (
    "https://raw.githubusercontent.com/SaiSiddhardhaKalla/NFHS/"
    "main/India.csv"
)
STATE_CSV_URL = (
    "https://raw.githubusercontent.com/pratapvardhan/NFHS-5/"
    "master/NFHS-5-States.csv"
)

HERE = Path(__file__).resolve().parent
RAW_DIR = (HERE / ".." / ".data" / "raw" / "nfhs5").resolve()

ANTHRO_INDICATORS_STATE = [
    # Exact strings as published in NFHS-5-States.csv (pratapvardhan compilation)
    "81. Children under 5 years who are stunted (height-for-age)18 (%)",
    "82. Children under 5 years who are wasted (weight-for-height)18 (%)",
    "83. Children under 5 years who are severely wasted (weight-for-height)19 (%)",
    "84. Children under 5 years who are underweight (weight-for-age)18 (%)",
]

# Short labels used in tidy output
ANTHRO_LABELS = {
    ANTHRO_INDICATORS_STATE[0]: "stunted_pct",
    ANTHRO_INDICATORS_STATE[1]: "wasted_pct",
    ANTHRO_INDICATORS_STATE[2]: "severely_wasted_pct",
    ANTHRO_INDICATORS_STATE[3]: "underweight_pct",
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, timeout: int = 120) -> None:
    print(f"Downloading {url}\n  -> {dest}")
    with requests.get(url, timeout=timeout, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    size = dest.stat().st_size
    print(f"  OK: {size:,} bytes  sha256={sha256_of(dest)}")


def build_district_tidy(raw_path: Path, out_path: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_path, low_memory=False)
    # Raw columns: State, ST_CEN_CD, District, DISTRICT, DT_CEN_CD, Category,
    #              Indicator, NFHS 5, NFHS 4
    df = df.rename(
        columns={
            "State": "state",
            "ST_CEN_CD": "state_census_code",
            "District": "district",
            "DISTRICT": "district_upper",
            "DT_CEN_CD": "district_census_code",
            "Category": "category",
            "Indicator": "indicator",
            "NFHS 5": "nfhs5_value",
            "NFHS 4": "nfhs4_value",
        }
    )
    df["indicator"] = df["indicator"].str.strip()
    df["state"] = df["state"].str.strip()
    df["district"] = df["district"].str.strip()
    df = df.drop(columns=["district_upper"])
    df["source"] = (
        "SaiSiddhardhaKalla/NFHS (GitHub, CSV reformatted from IIPS NFHS-5 "
        "district fact-sheet PDFs, rchiips.org/nfhs) - "
        + DISTRICT_CSV_URL
    )
    cols = [
        "state",
        "state_census_code",
        "district",
        "district_census_code",
        "category",
        "indicator",
        "nfhs5_value",
        "nfhs4_value",
        "source",
    ]
    df = df[cols].sort_values(["state", "district", "indicator"]).reset_index(drop=True)
    df.to_csv(out_path, index=False)
    return df


def build_state_anthro(raw_path: Path, out_path: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_path)
    df["indicator"] = df["indicator"].str.strip()
    sub = df[df["indicator"].isin(ANTHRO_INDICATORS_STATE)].copy()
    sub["indicator_short"] = sub["indicator"].map(ANTHRO_LABELS)
    sub["state"] = sub["state"].str.strip()
    sub["source"] = (
        "pratapvardhan/NFHS-5 (GitHub, CC-BY-4.0, CSV from IIPS NFHS-5 state "
        "fact-sheet PDFs, rchiips.org/nfhs; DOI 10.7910/DVN/42WNZF) - "
        + STATE_CSV_URL
    )
    cols = [
        "state",
        "state_code",
        "indicator",
        "indicator_short",
        "nfhs5_urban",
        "nfhs5_rural",
        "nfhs5_total",
        "nfhs4_total",
        "source",
    ]
    sub = sub[cols].sort_values(["state", "indicator_short"]).reset_index(drop=True)
    sub.to_csv(out_path, index=False)
    return sub


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--no-download",
        action="store_true",
        help="Skip re-downloading; rebuild tidy CSVs from cached raw files only.",
    )
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    district_raw = RAW_DIR / "India_raw.csv"
    state_raw = RAW_DIR / "NFHS-5-States_raw.csv"

    if not args.no_download:
        download(DISTRICT_CSV_URL, district_raw)
        download(STATE_CSV_URL, state_raw)
    else:
        if not district_raw.exists() or not state_raw.exists():
            print("ERROR: --no-download given but cached raw files are missing.", file=sys.stderr)
            return 1

    district_out = RAW_DIR / "nfhs5_district_tidy.csv"
    state_out = RAW_DIR / "nfhs5_state.csv"

    dtidy = build_district_tidy(district_raw, district_out)
    print(
        f"District tidy: {district_out}  "
        f"rows={len(dtidy):,}  districts={dtidy['district'].nunique()}  "
        f"states={dtidy['state'].nunique()}"
    )

    stidy = build_state_anthro(state_raw, state_out)
    print(
        f"State anthropometry tidy: {state_out}  "
        f"rows={len(stidy):,}  states={stidy['state'].nunique()}"
    )

    # Lightweight self-check: 4 anthropometry indicators must be present for
    # every district that has at least one row (spot check, not exhaustive).
    n_districts = dtidy["district"].nunique()
    anthro_rows = dtidy[dtidy["indicator"].str.contains(
        "stunted|wasted|underweight", case=False, regex=True
    )]
    print(
        f"Self-check: {anthro_rows['district'].nunique()} / {n_districts} "
        "districts have >=1 anthropometry row."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
