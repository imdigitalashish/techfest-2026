"""Static, CDN-free block dashboard for moderated FLN estimates (SYNTHETIC demo).

Shows only block-level numbers with 90 % intervals; no school-level trust labels or flags (ADR 001:
school-level moderation data is restricted to the moderation team). Every number is labelled as an
ASER-style proxy ("reads a Std II text"), not NIPUN attainment.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd


def _pct(x) -> str:
    try:
        return f"{100 * float(x):.1f}%"
    except Exception:
        return "—"


def _bar(value, lo, hi) -> str:
    v, l, h = (max(0.0, min(100.0, 100 * float(z))) for z in (value, lo, hi))
    return (f'<svg class="ci" viewBox="0 0 100 10" role="img" aria-label="estimate {_pct(value)}, 90% interval {_pct(lo)} to {_pct(hi)}">'
            f'<line x1="{l:.1f}" x2="{h:.1f}" y1="5" y2="5"/><circle cx="{v:.1f}" cy="5" r="3"/></svg>')


def build_dashboard(blocks: pd.DataFrame, meta: dict, out_dir: str | Path) -> Path:
    """blocks: block_lgd, raw, estimate, lo, hi, n_schools, n_retested_schools, children. meta: free-text labels."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, r in blocks.sort_values("block_lgd").iterrows():
        rows.append(f"<tr><td>{html.escape(str(r.block_lgd))}</td><td>{int(r.children):,}</td><td>{_pct(r.raw)}</td>"
                    f"<td><strong>{_pct(r.estimate)}</strong></td><td>{_pct(r.lo)} – {_pct(r.hi)}</td><td>{_bar(r.estimate, r.lo, r.hi)}</td>"
                    f"<td>{int(r.n_retested_schools)} of {int(r.n_schools)}</td></tr>")
    (out / "block_dashboard_outputs.json").write_text(json.dumps({"meta": meta, "blocks": blocks.to_dict(orient="records")}, indent=2, default=str), encoding="utf-8")
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>SYNTHETIC — moderated block estimates</title><style>
body{{margin:0;background:#fbf8ef;color:#17211b;font:15px/1.5 Arial,Helvetica,sans-serif}}main{{max-width:1080px;margin:auto;padding:28px 18px}}
.banner{{background:#17211b;color:#fff7d6;padding:8px 14px;border-radius:999px;display:inline-block;font-weight:700}}
h1{{font-size:1.9rem;margin:14px 0 4px}}p.note{{color:#4a5a50;margin:4px 0 14px}}
table{{width:100%;border-collapse:collapse;background:#fffdf7;border:1px solid #ded5c4}}th,td{{padding:9px 10px;text-align:left;border-bottom:1px solid #ded5c4}}
th{{font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;background:#f4eddc}}.ci{{width:150px;height:22px}}.ci line{{stroke:#b46a20;stroke-width:2.5}}.ci circle{{fill:#176b4d}}
footer{{color:#4a5a50;margin-top:14px;font-size:.9rem}}
</style></head><body><main><div class='banner'>SYNTHETIC DATA — simulated district, not real children</div>
<h1>{html.escape(meta.get('title', 'Moderated block estimates'))}</h1>
<p class='note'>{html.escape(meta.get('indicator', ''))}</p>
<table><thead><tr><th>Block</th><th>Grade 3 children</th><th>Teacher-reported</th><th>Moderated estimate</th><th>90% interval</th><th></th><th>Schools re-tested</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<footer>{html.escape(meta.get('footer', ''))}</footer></main></body></html>"""
    path = out / "block_dashboard.html"
    path.write_text(page, encoding="utf-8")
    return path
