import shutil
from pathlib import Path

import pandas as pd

from components.dashboard import build_dashboard


def test_dashboard_writes_html_and_json_without_school_labels():
    blocks = pd.DataFrame({"block_lgd": ["B01", "B02"], "raw": [0.30, 0.25], "estimate": [0.24, 0.22], "lo": [0.18, 0.16],
                           "hi": [0.30, 0.28], "n_schools": [100, 90], "n_retested_schools": [10, 9], "children": [3200, 2900]})
    out_dir = Path("deliverables/demo/test_dashboard_out")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    p = build_dashboard(blocks, {"title": "t", "indicator": "i", "footer": "f"}, out_dir)
    text = p.read_text()
    assert "SYNTHETIC DATA" in text and "Moderated estimate" in text
    assert "flag" not in text.lower() and "trust" not in text.lower()
    assert len(text.encode()) < 300_000
    assert (out_dir / "block_dashboard_outputs.json").exists()
    shutil.rmtree(out_dir)


def test_small_cells_suppressed_in_html_and_json():
    import json, tempfile
    b = pd.DataFrame({"block_lgd": ["B01", "B02"], "raw": [.5, .3], "estimate": [.5, .25], "lo": [.4, .2], "hi": [.6, .3],
                      "n_schools": [1, 50], "n_retested_schools": [1, 5], "children": [8, 1500]})
    with tempfile.TemporaryDirectory() as d:
        p = build_dashboard(b, {}, Path(d))
        j = json.loads((Path(d) / "block_dashboard_outputs.json").read_text())
        html_text = p.read_text()
    rec = {r["block_lgd"]: r for r in j["blocks"]}
    assert rec["B01"]["estimate"] is None and rec["B01"]["children"] is None and rec["B01"]["suppressed"]
    assert rec["B02"]["estimate"] == 0.25
    assert "50.0%" not in html_text and "suppressed" in html_text
