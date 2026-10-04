#!/usr/bin/env bash
# Fetch StockNet (Xu & Cohen, ACL 2018; MIT licence) into .data/ (gitignored). ~660 MB on disk.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .data
[ -d .data/stocknet-dataset ] || git clone --depth 1 https://github.com/yumoxu/stocknet-dataset.git .data/stocknet-dataset
