"""Download Lok Sabha USQ 4090 (18 Aug 2025) and parse the state-wise PMJDY inoperative-accounts annexure."""
import pathlib
import re
import subprocess

import pandas as pd
import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = "https://www.sansad.in/getFile/loksabhaquestions/annex/185/AU4090_LCDFLT.pdf?source=pqals"
raw = ROOT / ".cache" / "src" / "ls_au4090_2025.pdf"
raw.parent.mkdir(parents=True, exist_ok=True)
if not raw.exists():
    subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", "--max-time", "60", "-o", str(raw), URL], check=True)
with pdfplumber.open(raw) as pdf:
    text = "\n".join((p.extract_text() or "") for p in pdf.pages)
rows = []
for line in text.splitlines():
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+([\d,]+)\s+([\d,]+)\s*$", line)
    if m:
        rows.append((m.group(2).strip(), int(m.group(3).replace(",", "")), int(m.group(4).replace(",", ""))))
df = pd.DataFrame(rows, columns=["state_ut", "pmjdy_accounts", "inoperative_accounts"])
df["inoperative_share"] = (df.inoperative_accounts / df.pmjdy_accounts).round(4)
assert df.pmjdy_accounts.sum() == 560384490 and df.inoperative_accounts.sum() == 130452845, "totals do not match the annexure"
out = ROOT / "eval" / "public_data" / "derived" / "pmjdy_inoperative_by_state_2025-07-31.csv"
df.to_csv(out, index=False)
print(f"{len(df)} rows; inoperative share {df.inoperative_accounts.sum() / df.pmjdy_accounts.sum():.4f} -> {out}")
