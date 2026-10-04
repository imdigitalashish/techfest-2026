#!/usr/bin/env bash
# Download the public floating-litter datasets used by C5/C6 (no credentials needed).
#   TUD-GV subset (Jia et al. 2024, Water Research 266:122405), CC BY 4.0, doi:10.5281/zenodo.13730228
#   Groningen     (same paper),                                   CC BY 4.0, doi:10.5281/zenodo.13730384
# Output: innovatex-t3-coastal-plastic/.data/detection/raw/{tudgv,groningen}/  (gitignored)
# Zenodo drops long single connections; aria2c (brew install aria2) resumes and parallelises.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="$HERE/../../../.data/detection/raw"
mkdir -p "$RAW/tudgv" "$RAW/groningen"

fetch() {  # record_id file dest_dir
  local url="https://zenodo.org/api/records/$1/files/$2/content"
  if [ -s "$3/$2" ] && [ ! -e "$3/$2.aria2" ]; then echo "have $3/$2"; return; fi
  if command -v aria2c >/dev/null; then
    aria2c -q -x 6 -s 6 -k 20M --max-tries=50 --retry-wait=3 --timeout=30 --continue=true -d "$3" -o "$2" "$url"
  else
    curl -sSL --retry 20 --retry-delay 3 -C - -o "$3/$2" "$url"
  fi
}
for f in images.zip labels_txt.zip classes.txt; do fetch 13730228 "$f" "$RAW/tudgv"; done
for f in images.zip labels_txt.zip classes.txt; do fetch 13730384 "$f" "$RAW/groningen"; done

# Expected sizes from the Zenodo API (2026-10-04): tudgv/images.zip 840309218 B, groningen/images.zip 5376277 B
for d in tudgv groningen; do
  (cd "$RAW/$d" && rm -rf images labels && mkdir images labels &&
   unzip -q -o images.zip -d images && unzip -q -o labels_txt.zip -d labels)
done
echo "done: $(find "$RAW/tudgv/images" -type f | wc -l) TUD-GV images, $(find "$RAW/groningen/images" -type f | wc -l) Groningen images"
