"""Write demo/fallback/p8_demo_offline.html: demo/web/index.html with data.js inlined (no server, no network).

Tabs 1, 3 and 4 replay committed results exactly as on the live page. Tab 2 (the live engine) says it is offline:
use the numbered screenshots in demo/fallback/ for it. No-text mode only: data.js holds derived outcomes, no Eedi text.
    .venv/bin/python -m demo.make_fallback
"""
from __future__ import annotations

from pathlib import Path

WEB = Path(__file__).resolve().parent / "web"
OUT = Path(__file__).resolve().parent / "fallback" / "p8_demo_offline.html"


def main() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    data = (WEB / "data.js").read_text(encoding="utf-8")
    tag = '<script src="data.js"></script>'
    assert html.count(tag) == 1, tag
    html = html.replace(tag, "<script>\n" + data.replace("</script", "<\\/script") + "</script>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(WEB.parents[1])} ({OUT.stat().st_size / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
