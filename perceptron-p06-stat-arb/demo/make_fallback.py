"""Write demo/fallback/p6_demo_standalone.html: index.html with style.css, assets/data.js and app.js inlined.

One file you can open anywhere (no server, no network). It is the same page in OFFLINE mode; it still upgrades to
live mode if a backend is running on 127.0.0.1:8766.
    .venv/bin/python -m demo.make_fallback
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    html = open(os.path.join(HERE, "index.html")).read()
    css = open(os.path.join(HERE, "style.css")).read()
    data = open(os.path.join(HERE, "assets", "data.js")).read()
    app = open(os.path.join(HERE, "app.js")).read()
    for needle in ('<link rel="stylesheet" href="style.css">', '<script src="assets/data.js"></script>', '<script src="app.js"></script>'):
        assert needle in html, needle
    esc = lambda js: js.replace("</script", "<\\/script")  # noqa: E731
    html = html.replace('<link rel="stylesheet" href="style.css">', "<style>\n" + css + "</style>")
    html = html.replace('<script src="assets/data.js"></script>', "<script>\n" + esc(data) + "</script>")
    html = html.replace('<script src="app.js"></script>', "<script>\n" + esc(app) + "</script>")
    os.makedirs(os.path.join(HERE, "fallback"), exist_ok=True)
    out = os.path.join(HERE, "fallback", "p6_demo_standalone.html")
    open(out, "w").write(html)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
