#!/usr/bin/env bash
# Fetch ABIDES (J.P. Morgan, BSD-3) at the pinned commit into the gitignored .cache/.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache
if [ ! -d .cache/abides-jpmc-public ]; then
  git clone https://github.com/jpmorganchase/abides-jpmc-public.git .cache/abides-jpmc-public
fi
git -C .cache/abides-jpmc-public checkout -q f9cbe51342b7dedd9587e4e069040d68a5c6477f
echo "ABIDES ready at .cache/abides-jpmc-public (f9cbe51)"
