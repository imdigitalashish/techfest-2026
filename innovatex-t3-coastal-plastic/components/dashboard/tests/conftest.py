import sys
from pathlib import Path

HERE = Path(__file__).resolve()
for p in (HERE.parents[2], HERE.parents[1]):  # .../components and .../components/dashboard
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
