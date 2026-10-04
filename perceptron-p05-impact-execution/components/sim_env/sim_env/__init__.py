"""ABIDES adapter: path setup, pomegranate shim, world building."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
ABIDES_DIR = os.environ.get("ABIDES_DIR", os.path.join(_ROOT, ".cache", "abides-jpmc-public"))

for p in (os.path.join(_HERE, "_shims"),
          os.path.join(ABIDES_DIR, "abides-core"),
          os.path.join(ABIDES_DIR, "abides-markets")):
    if p not in sys.path:
        sys.path.insert(0, p)
