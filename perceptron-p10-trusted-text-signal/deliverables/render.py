"""Render deliverables from committed results so numbers cannot drift from runs.

Templates (`deliverables/*.template.md`) contain placeholders:
    {{<result-stem>:<dotted.path>|<fmt>}}  e.g. {{baseline_v1:ablation.fusion.split.coverage|pct}}
    {{D:<derived-name>|<fmt>}}             derived values computed in `derived()` below
fmt: pct (one-decimal percent of a fraction) · pp1/pp2/pp3 (fixed decimals) · int · p (p-value, 2 sig. figs) · signpct (signed percent)
Result stems resolve to eval/results/<stem>.json. Usage:
    PYTHONPATH=. .venv/bin/python deliverables/render.py            # writes deliverables/<name>.md
    PYTHONPATH=. .venv/bin/python deliverables/check_drift.py       # fails if anything is stale
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PH = re.compile(r"\{\{([A-Za-z0-9_]+):([^|}]+)\|([a-z0-9]+)\}\}")


@lru_cache(maxsize=None)
def result(stem: str) -> dict:
    return json.loads((ROOT / "eval" / "results" / f"{stem}.json").read_text())


def get(stem: str, path: str):
    node = derived() if stem == "D" else result(stem)
    for part in path.split("."):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def derived() -> dict:
    b = result("baseline_v1")
    fz = b["ablation"]["fusion"]
    w0 = fz["cqr_sym"]["mean_width"]
    cr = b["spike"]["cr_aci"]
    pump = b["attack"]["pump"]
    d = {
        "cert_k3_width_pct": 100 * (b["spike"]["clean_k3"]["mean_width"] / w0 - 1),
        "cert_pump_width_pct": 100 * (pump["certified"]["mean_width"] / pump["vanilla_cqr"]["mean_width"] - 1),
        "cr_aci_clean_width_pct": 100 * (cr["cr_aci_clean"]["mean_width"] / cr["cqr_aci_clean"]["mean_width"] - 1),
        "cr_aci_pump_width_pct": 100 * (cr["cr_aci_pump"]["mean_width"] / cr["cqr_aci_pump"]["mean_width"] - 1),
        "worst_variant_vanilla_cov": b["attack"]["oracle"]["worst3"][0]["vanilla_coverage"],
        "worst_variant_cert_cov": b["attack"]["oracle"]["worst3"][0]["certified_coverage"],
    }
    try:
        t = result("text_utility_djia_v1")
        d["djia_rel_improvement_pct"] = 100 * t["primary"]["relative_improvement"]
    except FileNotFoundError:
        pass
    return d


def fmt(v, f: str) -> str:
    if f == "pct":
        return f"{100 * v:.1f}%"
    if f == "signpct":
        return f"{v:+.1f}%"
    if f.startswith("pp"):
        return f"{v:.{int(f[2:])}f}"
    if f == "int":
        return f"{int(round(v)):,}"
    if f == "p":
        return f"{v:.2g}"
    raise ValueError(f)


def render_text(tpl: str) -> str:
    return PH.sub(lambda m: fmt(get(m.group(1), m.group(2)), m.group(3)), tpl)


def targets():
    for tpl in sorted((ROOT / "deliverables").glob("*.template.md")):
        yield tpl, tpl.with_name(tpl.name.replace(".template.md", ".md"))


def main():
    for tpl, out in targets():
        out.write_text(render_text(tpl.read_text()))
        print("rendered", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
