#!/usr/bin/env bash
# Lead-side verification of the demo from a CLEAN checkout of origin/main (PLAYBOOK §11): no .data, no ignored files.
# The project venv is used via P3_PYTHON (a fresh clone would create it with uv; the demo needs numpy/pandas/matplotlib).
# Usage: bash perceptron-p03-off-policy-eval/eval/verify_demo_clean.sh
set -euo pipefail
REPO=$(git rev-parse --show-toplevel)
DEST=$(mktemp -d /tmp/p3-demo-verify.XXXXXX)
git -C "$REPO" fetch -q origin
git -C "$REPO" worktree add -q --detach "$DEST/wt" origin/main
trap 'git -C "$REPO" worktree remove --force "$DEST/wt" >/dev/null 2>&1 || true; rm -rf "$DEST"' EXIT
cd "$DEST/wt/perceptron-p03-off-policy-eval"
echo "clean checkout: $(git rev-parse --short HEAD) at $PWD"
test ! -e .data && echo "no .data present (as in a fresh clone)"
export P3_PYTHON="$REPO/perceptron-p03-off-policy-eval/.venv/bin/python"
export P3_NO_OPEN=1
start=$(python3 -c 'import time; print(time.time())')
bash demo/run.sh
end=$(python3 -c 'import time; print(time.time())')
python3 -c "print(f'run.sh wall time: {${end} - ${start}:.1f} s')"
test -s demo/index.html && echo "index.html built: $(wc -c < demo/index.html) bytes"
bash demo/smoke.sh && echo "SMOKE PASS"
