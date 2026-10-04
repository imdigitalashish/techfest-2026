"""Known issue 1 (eval/taubench/README.md): impact of stripping contractions before option tokenising.

  python -m eval.taubench.known_issue_contractions   -> eval/results/taubench/known_issue_contractions.json

This measures a HYPOTHETICAL fix without applying it. `norm` is patched in-process only, and the committed guard code
and committed results are unchanged. For every config and split it counts decisions that would change, by label.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from components.checker import taubench_retail as tr
from eval.provenance import code_sha256
from eval.taubench.replay import _load_tau, load_items
from eval.taubench.run import CONFIGS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "eval" / "results" / "taubench" / "known_issue_contractions.json"
CONTR = re.compile(r"['\u2019](m|s|re|ve|ll|d|t)\b", re.I)


def main():
    products = _load_tau()[0]()["products"]
    orig = tr.norm
    fixed = lambda s: orig(CONTR.sub("", str(s)))
    res = {"hypothetical_fix": "strip 'm 's 're 've 'll 'd 't before norm() (not applied to committed code)",
           "code_sha256": code_sha256(), "by_split": {}}
    try:
        for split in ("dev", "test"):
            items = load_items(split)
            res["by_split"][split] = {}
            for g, fields in CONFIGS.items():
                tr.SUMMARY_FIELDS = fields
                ch = Counter()
                for it in items:
                    data = {"orders": it["db"]["orders"], "users": it["db"]["users"], "products": products}
                    a = []
                    for f in (orig, fixed):
                        tr.norm = f
                        a.append(tr.guard(it["tool"], it["args"], it["user_turns"], it["observations"], it["auth_user_id"], data,
                                          confirm_prompt=it.get("confirm_prompt", ""))[0].value)
                    if a[0] != a[1]:
                        ch[f"{it['kind']}: {a[0]} -> {a[1]}"] += 1
                res["by_split"][split][g] = {"n_changed": sum(ch.values()), "changes": dict(sorted(ch.items()))}
                print(split, g, res["by_split"][split][g], flush=True)
    finally:
        tr.norm = orig
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
