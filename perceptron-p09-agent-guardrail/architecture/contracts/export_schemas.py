"""Export JSON Schemas for every contract: python -m architecture.contracts.export_schemas"""
import json
from pathlib import Path

from architecture.contracts import models

OUT = Path(__file__).parent / "schemas"
for name in ("ToolCall", "Observation", "Context", "GuardRequest", "CheckResult", "Verdict", "SuiteItem"):
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.schema.json").write_text(json.dumps(getattr(models, name).model_json_schema(), indent=1))
    print("wrote", name)
