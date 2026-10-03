"""Export JSON Schema for every contract model into architecture/contracts/schemas/.

Run from india71-t2-learning/:  python -m architecture.contracts.export_schemas
"""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from architecture.contracts import fln_contracts as c

OUT = Path(__file__).parent / "schemas"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    n = 0
    for name in c.__all__:
        obj = getattr(c, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj.__module__ == c.__name__:
            (OUT / f"{name}.schema.json").write_text(json.dumps(obj.model_json_schema(), indent=2) + "\n")
            n += 1
    print(f"wrote {n} schemas to {OUT} (schema version {c.SCHEMA_VERSION})")


if __name__ == "__main__":
    main()
