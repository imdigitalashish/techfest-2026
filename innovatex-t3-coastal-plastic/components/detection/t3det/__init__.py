import os
from pathlib import Path

# Private ultralytics config dir holding Arial.ttf: avoids matplotlib's system font scan (system_profiler),
# which failed under heavy machine load and aborted training ("KeyError: '_items'").
_cfg = Path(__file__).resolve().parents[3] / ".cache" / "ultralytics"
_cfg.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(_cfg))
