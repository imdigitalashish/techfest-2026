#!/usr/bin/env bash
# Re-download every raw source used by data/factors/*.yaml into the gitignored .data/raw/ tree.
# Usage: bash data/fetch/fetch_sources.sh   (run from ev-c2-green-auto-lca/)
set -euo pipefail
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
get() { mkdir -p "$(dirname "$1")"; [ -s "$1" ] || curl -sL -m 300 -A "$UA" -o "$1" "$2"; echo "ok $1"; }
get .data/raw/electricity/cea_ug_v22.pdf  "https://cea.nic.in/wp-content/uploads/baseline/2026/09/User_Guide__Version_22.0.pdf"
get .data/raw/electricity/cea_db_v22.xlsx "https://cea.nic.in/wp-content/uploads/baseline/2026/09/Baseline_Carbon_Dioxide_Emission_Database_Version_22.0.xlsx"
get .data/raw/electricity/ls_au842.pdf    "https://www.sansad.in/getFile/loksabhaquestions/annex/186/AU842_VAJOF4.pdf?source=pqals"
get .data/raw/fuels/ipcc2006_v2_ch1.pdf   "https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf"
get .data/raw/fuels/unsd_conv.pdf         "https://unstats.un.org/unsd/energystats/pubs/yearbook/2020/09ii.pdf"
get .data/raw/benchmarks/icct_2w_fc_2021.pdf "https://theicct.org/wp-content/uploads/2021/12/fuel-consumption-2w-india-aug2021.pdf"
get .data/raw/benchmarks/icct_india_2021.pdf "https://theicct.org/wp-content/uploads/2021/12/lca-ghg-emissions-ice-evs-india-sept21_0.pdf"
