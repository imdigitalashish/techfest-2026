#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DATA_DIR="$ROOT/.data/nyc_tlc"
mkdir -p "$DATA_DIR"

curl -L --retry 5 --max-time 1800 \
  -o "$DATA_DIR/yellow_tripdata_2025-07.parquet" \
  "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-07.parquet"
curl -L --retry 5 --max-time 1800 \
  -o "$DATA_DIR/taxi_zone_lookup.csv" \
  "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
curl -L --retry 5 --max-time 1800 \
  -o "$DATA_DIR/taxi_zones.zip" \
  "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
