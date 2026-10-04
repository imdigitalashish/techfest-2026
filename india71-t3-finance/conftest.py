import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
for p in (ROOT, ROOT / "architecture" / "contracts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
