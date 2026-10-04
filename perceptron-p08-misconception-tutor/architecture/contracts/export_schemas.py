"""Export JSON Schemas for every contract model to architecture/contracts/schemas/.

Run from the project folder: .venv/bin/python -m architecture.contracts.export_schemas
"""
from __future__ import annotations

import json
import pathlib

from pydantic import BaseModel

from architecture.contracts import models

OUT = pathlib.Path(__file__).parent / "schemas"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    names = []
    for name in dir(models):
        obj = getattr(models, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel and obj.__module__ == models.__name__:
            (OUT / f"{name}.schema.json").write_text(json.dumps(obj.model_json_schema(), indent=1))
            names.append(name)
    print(f"{len(names)} schemas (contract {models.CONTRACT_VERSION}): {', '.join(sorted(names))}")


if __name__ == "__main__":
    main()
