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
