"""Collect every component's committed metrics into eval/RESULTS.md.

Usage (from the repo root or anywhere):
    python3 innovatex-t3-coastal-plastic/eval/collect_results.py

Reads components/*/results/*.json (small files with a 'reproduce' key), which each component writes from a committed
run, and renders them with their reproduce commands. The script never computes or edits a
metric; it only copies them.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "eval" / "RESULTS.md"


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _flatten(d: dict, prefix: str = "") -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = []
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            rows.extend(_flatten(v, key + "."))
        elif isinstance(v, list) and len(v) > 8:
            rows.append((key, f"[list of {len(v)}]"))
        else:
            rows.append((key, v))
    return rows


def render() -> str:
    """The full RESULTS.md text (its 'Generated ...' line carries the time and commit)."""
    files = sorted(f for f in ROOT.glob("components/*/results/*.json")
                   if f.stat().st_size < 200_000 and '"reproduce"' in f.read_text())
    ist = dt.timezone(dt.timedelta(hours=5, minutes=30))
    lines = [
        "# Results — every number with its reproduce command",
        "",
        f"Generated {dt.datetime.now(ist):%Y-%m-%d %H:%M} IST at commit `{_git_sha()}` by "
        "`python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from "
        "each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the "
        "component's output; read them before quoting a number.",
        "",
    ]
    if not files:
        lines.append("_No component has committed metrics yet._")
    for f in files:
        comp = f"{f.parent.parent.name} — {f.name}"
        try:
            data = json.loads(f.read_text())
        except Exception as e:  # keep going; report the broken file
            lines += [f"## {comp}", "", f"Could not parse `{f.relative_to(ROOT)}`: {e}", ""]
            continue
        reproduce = data.get("reproduce", "—") if isinstance(data, dict) else "—"
        lines += [f"## {comp}", "", f"Source: [`{f.relative_to(ROOT)}`](../{f.relative_to(ROOT)})  ", f"Reproduce: `{reproduce}`", "",
                  "| Metric | Value |", "|---|---|"]
        rows = _flatten(data) if isinstance(data, dict) else [("value", data)]
        for k, v in rows:
            if k == "reproduce":
                continue
            if isinstance(v, float):
                v = f"{v:.4g}"
            lines.append(f"| {k} | {str(v).replace('|', '/')} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def body(text: str) -> str:
    """RESULTS.md without its 'Generated ...' line, for freshness comparison."""
    return "\n".join(line for line in text.splitlines() if not line.startswith("Generated "))


def main() -> None:
    text = render()
    OUT.write_text(text)
    n = sum(1 for line in text.splitlines() if line.startswith("## "))
    print(f"wrote {OUT.relative_to(ROOT)} from {n} metrics file(s)")


if __name__ == "__main__":
    main()
