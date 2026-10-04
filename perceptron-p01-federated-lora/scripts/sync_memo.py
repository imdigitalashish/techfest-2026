#!/usr/bin/env python3
"""Copy the rendered deliverables/selection-memo.md into thought_node.md's '## Selection memo' section."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
memo = (ROOT / "deliverables" / "selection-memo.md").read_text().split("\n", 1)[1].strip()  # drop the H1
tn = ROOT / "thought_node.md"
t = tn.read_text()
s = t.index("## Selection memo\n")
e = t.index("\n## Log", s)
t = t[:s] + "## Selection memo\n_Source of truth: [deliverables/selection-memo.md](deliverables/selection-memo.md), rendered from results._\n\n" + memo + "\n" + t[e:]
tn.write_text(t)
print("thought node memo synced")
