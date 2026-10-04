"""Word count of the Round-1 abstract as a reader sees it (markup and HTML comments removed, title line excluded)."""
import re
from pathlib import Path

t = (Path(__file__).resolve().parents[1] / "deliverables" / "round1-abstract.md").read_text()
body = re.sub(r"<!--.*?-->", "", t.split("\n", 2)[2], flags=re.S)
print(len(re.sub(r"[#*|`_]", " ", body).split()))
