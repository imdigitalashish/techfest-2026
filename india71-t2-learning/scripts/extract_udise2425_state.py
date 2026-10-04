#!/usr/bin/env python3
"""Extract UDISE+ 2024-25 Table 2.2 state highlights."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".data" / "UDISE_2024_25_Booklet_existing.txt"
OUT = ROOT / "data" / "public" / "udise2425_state.csv"

FIELDNAMES = [
    "state",
    "schools",
    "enrolment",
    "teachers",
    "single_teacher_schools",
    "enrolment_single_teacher",
    "zero_enrolment_schools",
    "ptr",
]


def table_block(text: str) -> str:
    start = text.rindex("Table 2.2: State wise highlights of the UDISE+ 2024-25 data")
    end = text.index("Source: UDISE+ 2024-25", start)
    return text[start:end]


def parse_rows(block: str) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    pending_name = ""
    skip_diu_suffix = False
    for raw_line in block.splitlines():
        line = " ".join(raw_line.split())
        if not line or line.startswith(("Table 2.2", "Total number", "Pupil", "Teacher", "Ratio", "(1)", "India/State/UT")):
            continue
        nums = [int(x) for x in re.findall(r"\d+", line)]
        if len(nums) < 10:
            if "Dadra and Nagar Haveli and Daman and" in line:
                pending_name = line
                skip_diu_suffix = True
            elif skip_diu_suffix and line == "Diu":
                skip_diu_suffix = False
            continue
        first_num = re.search(r"\d+", line)
        assert first_num is not None
        state = line[: first_num.start()].strip()
        if not state and pending_name:
            state = f"{pending_name} Diu"
            pending_name = ""
        values = nums[-10:]
        schools, enrolment, teachers, ptr, _avg_teachers, _avg_enrolment, zero_schools, _teachers_zero, single_schools, single_enrolment = values
        rows.append(
            {
                "state": state,
                "schools": schools,
                "enrolment": enrolment,
                "teachers": teachers,
                "single_teacher_schools": single_schools,
                "enrolment_single_teacher": single_enrolment,
                "zero_enrolment_schools": zero_schools,
                "ptr": ptr,
            }
        )
    return rows


def main() -> None:
    text = RAW.read_text(encoding="utf-8", errors="replace")
    rows = parse_rows(table_block(text))
    india = next(row for row in rows if row["state"] == "India")
    expected = {
        "schools": 1_471_473,
        "single_teacher_schools": 104_125,
        "enrolment_single_teacher": 3_376_769,
    }
    for key, value in expected.items():
        if india[key] != value:
            raise RuntimeError(f"India {key} expected {value}, got {india[key]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"wrote {OUT} rows={len(rows)}; India verified schools={india['schools']} "
        f"single_teacher_schools={india['single_teacher_schools']} "
        f"enrolment_single_teacher={india['enrolment_single_teacher']}"
    )


if __name__ == "__main__":
    main()
