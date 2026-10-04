#!/usr/bin/env bash
# Fetch the small Open Bandit Dataset sample (10,000 rows per policy, "All" campaign) and the BTS prior
# from the official Open Bandit Pipeline repo (Apache-2.0). About 10 MB; written to the gitignored .data/.
set -euo pipefail
cd "$(dirname "$0")/.."
B=https://raw.githubusercontent.com/st-tech/zr-obp/master
mkdir -p .data/obd/random/all .data/obd/bts/all
for f in obd/random/all/all.csv obd/random/all/item_context.csv obd/bts/all/all.csv; do
  curl -sS -L --retry 3 --max-time 900 -o ".data/$f" "$B/$f"
done
curl -sS -L --retry 3 --max-time 300 -o .data/obd/prior_bts.yaml "$B/obp/policy/conf/prior_bts.yaml"
wc -l .data/obd/*/all/all.csv
