#!/usr/bin/env bash
# One-time setup on macOS (Apple silicon): Python env, Brush (Metal 3DGS trainer), checks.
set -euo pipefail
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { echo "Install ffmpeg first: brew install ffmpeg"; exit 1; }
command -v uv >/dev/null || { echo "Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
[ -x .venv/bin/python ] || uv venv .venv --python 3.11 -q
uv pip install -q --python .venv/bin/python -r requirements.txt
BRUSH_DIR=.cache/brush
if [ ! -x "$BRUSH_DIR/brush-app-aarch64-apple-darwin/brush_app" ]; then
  mkdir -p "$BRUSH_DIR"
  curl -sSL -o "$BRUSH_DIR/brush.tar.xz" \
    https://github.com/ArthurBrussee/brush/releases/download/v0.3.0/brush-app-aarch64-apple-darwin.tar.xz
  tar -xf "$BRUSH_DIR/brush.tar.xz" -C "$BRUSH_DIR"
  xattr -dr com.apple.quarantine "$BRUSH_DIR" 2>/dev/null || true
fi
.venv/bin/python -c "import pycolmap, cv2, numpy; print('ok: pycolmap', pycolmap.__version__, '| opencv', cv2.__version__)"
"$BRUSH_DIR/brush-app-aarch64-apple-darwin/brush_app" --version
