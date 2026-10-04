#!/usr/bin/env bash
# Kept for compatibility: the registry-driven fetcher reads every data/sources/*.yaml entry.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 data/fetch/fetch_sources.py "$@"
