"""Export JSON Schemas for every contract model in gwcontracts.py into schemas/.

Run: innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/architecture/contracts/export_schemas.py
"""
from __future__ import annotations

import inspect
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gwcontracts as c  # noqa: E402
from pydantic import BaseModel  # noqa: E402

OUT = HERE / "schemas"
OUT.mkdir(exist_ok=True)
n = 0
for name, obj in vars(c).items():
    if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj.__module__ == c.__name__ and not name.startswith("_"):
        (OUT / f"{name}.schema.json").write_text(json.dumps(obj.model_json_schema(), indent=2) + "\n")
        n += 1
print(f"wrote {n} schemas to {OUT} (contracts v{c.CONTRACTS_VERSION})")
