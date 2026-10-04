"""Export JSON Schemas for every contract model: python architecture/contracts/export_schema.py"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from contracts import ROW_MODELS  # noqa: E402

out = HERE / "schema"
out.mkdir(exist_ok=True)
for m in ROW_MODELS:
    (out / f"{m.__name__}.schema.json").write_text(json.dumps(m.model_json_schema(), indent=2) + "\n")
print(f"wrote {len(ROW_MODELS)} schemas to {out}")
