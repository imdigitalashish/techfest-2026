#!/usr/bin/env bash
# Fetch the public evaluation scene (Deep Blending "drjohnson", 263 photos + COLMAP model, ~208 MB)
# from the Hugging Face mirror nvs-bench/deepblending into .data/deepblending/drjohnson/.
# Licence: the original Deep Blending data is for non-commercial research use (see research/datasets.md);
# it is NOT redistributed in this repo, and twins derived from it must not be hosted publicly.
set -euo pipefail
cd "$(dirname "$0")/.."
DST=.data/deepblending
mkdir -p "$DST"
curl -s "https://huggingface.co/api/datasets/nvs-bench/deepblending/tree/main?recursive=true" \
  | python3 -c "import sys,json; [print(f['path']) for f in json.load(sys.stdin) if f['type']=='file' and f['path'].startswith('drjohnson/')]" \
  > "$DST/drjohnson_files.txt"
echo "$(wc -l < "$DST/drjohnson_files.txt") files"
cd "$DST"
xargs -P 16 -I{} sh -c 'mkdir -p "$(dirname {})" && [ -s "{}" ] || curl -sSL --retry 3 -o "{}" "https://huggingface.co/datasets/nvs-bench/deepblending/resolve/main/{}"' < drjohnson_files.txt
echo "done: $(ls drjohnson/images | wc -l) images"
