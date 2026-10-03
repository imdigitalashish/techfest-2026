from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from architecture.contracts.fln_contracts import Competency, Item, SourceSystem, Subject

FRAMEWORK_PATH = Path(__file__).with_name("framework.json")


def load_framework(path: str | Path = FRAMEWORK_PATH) -> list[Competency]:
    data = json.loads(Path(path).read_text())
    return [Competency(**row) for row in data["competencies"]]


def load_q_matrix(item_bank: pd.DataFrame) -> list[Item]:
    items = []
    for _, row in item_bank.iterrows():
        code = row.get("competency_code") or row.get("competency_codes")
        codes = code if isinstance(code, list) else [str(code)]
        items.append(Item(
            item_id=str(row["item_id"]), instrument=SourceSystem(row.get("instrument", "classroom_tool")),
            subject=Subject(row["subject"]), competency_codes=codes, max_score=float(row.get("max_score", 1.0)),
            irt_a=float(row["irt_a"]) if row.get("irt_a") is not None else None,
            irt_b=float(row["irt_b"]) if row.get("irt_b") is not None else None,
        ))
    return items
