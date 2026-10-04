"""POST-HOC (review A7): raw user-feature labels at the start of each official OBD zip member (about 1.5 MB compressed each).

Shows whether the category behind the pre-registered TVD flag carries different raw labels in the two files.
Reproduce: .venv/bin/python eval/obd_raw_labels.py -> appends nothing; writes eval/results/obd_raw_labels.md
"""
import io
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from obd_zip_slice import central_directory, iter_member  # noqa: E402

ents = {e["name"]: e for e in central_directory()}
L = ["# POST-HOC: raw user-feature labels in the official OBD zip (review A7)", "",
     "Reproduce: `.venv/bin/python eval/obd_raw_labels.py` (reads the first ~1.5 MB compressed of each member by HTTP range request; labels read as raw strings, `keep_default_na=False`).", ""]
for feat in ("user_feature_0", "user_feature_1", "user_feature_2", "user_feature_3"):
    L += [f"## {feat}", "", "| label (first 12 chars) | Random share | BTS share |", "|---|---|---|"]
    shares = {}
    for p in ("random", "bts"):
        e = ents[f"open_bandit_dataset/{p}/all/all.csv"]
        blocks, header = [], None
        for h, b, _ in iter_member(e, 1_500_000):
            header = h
            blocks.append(b)
        d = pd.read_csv(io.BytesIO(header + b"".join(blocks)), usecols=[feat], keep_default_na=False, dtype=str)
        shares[p] = d[feat].value_counts(normalize=True)
    for lab in sorted(set(shares["random"].index) | set(shares["bts"].index), key=lambda x: -max(shares["random"].get(x, 0), shares["bts"].get(x, 0))):
        L.append(f"| {lab[:12] or '<empty>'} | {shares['random'].get(lab, 0):.3f} | {shares['bts'].get(lab, 0):.3f} |")
    L.append("")
L.append("Reading: labels present in only one file with matching shares are consistent with one category being anonymised differently in each file. The data cannot prove they are the same category, so the pre-registered balance caveat stays open (labelled UNRESOLVED), not dismissed.")
(ROOT / "eval" / "results" / "obd_raw_labels.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
