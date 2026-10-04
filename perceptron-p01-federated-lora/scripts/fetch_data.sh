#!/usr/bin/env bash
# Fetch the only downloaded corpus (WikiText-103 raw, ~300 MB parquet) into the HF cache.
# The other four domains come from files already on disk (site-packages, /usr/share/man), so after
# `uv pip install -r requirements.txt` they are reproducible from the pinned package versions.
set -euo pipefail
python - <<'PY'
from huggingface_hub import snapshot_download
p = snapshot_download("Salesforce/wikitext", repo_type="dataset", allow_patterns=["wikitext-103-raw-v1/*"])
print("WikiText-103 raw at", p)
PY
python -m components.data_partitioner.local_domains   # tokenise + cache blocks in .data/
