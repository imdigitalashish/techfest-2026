"""Export every contract model to JSON Schema: `python -m architecture.contracts.export_schemas`."""

import json
from pathlib import Path

from pydantic import BaseModel

from architecture.contracts import models

OUT = Path(__file__).parent / "schemas"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    names = []
    for name in dir(models):
        obj = getattr(models, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj not in (BaseModel, models.Strict):
            (OUT / f"{name}.json").write_text(json.dumps(obj.model_json_schema(), indent=2, default=str) + "\n")
            names.append(name)
    print(f"exported {len(names)} schemas to {OUT}: {', '.join(sorted(names))}")


if __name__ == "__main__":
    main()
