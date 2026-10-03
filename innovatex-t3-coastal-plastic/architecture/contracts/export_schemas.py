"""Export JSON Schemas for every contract model: python3 architecture/contracts/export_schemas.py"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import contracts as c  # noqa: E402

out = HERE / "schemas"
out.mkdir(exist_ok=True)
models = [getattr(c, n) for n in dir(c)
          if isinstance(getattr(c, n), type) and issubclass(getattr(c, n), c.BaseModel) and n != "BaseModel"]
for m in models:
    (out / f"{m.__name__}.schema.json").write_text(json.dumps(m.model_json_schema(), indent=2) + "\n")
print(f"wrote {len(models)} schemas to {out}")
