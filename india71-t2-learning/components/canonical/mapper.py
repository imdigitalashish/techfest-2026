from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Mapping

from architecture.contracts.fln_contracts import Administrator, Provenance, Response, School, SourceSystem, Student


def pseudonymise(raw_id: str, salt: str) -> str:
    return "ps_" + hashlib.sha256(f"{salt}:{raw_id}".encode("utf-8")).hexdigest()[:16]


def _prov(source: SourceSystem, record_id: str, transform: str = "components.canonical.mapper@0.1") -> Provenance:
    return Provenance(source=source, source_record_id=str(record_id), fetched_at=datetime.now(timezone.utc), transform=transform, synthetic=True)


def school_from_row(row: Mapping) -> School:
    enrol = {3: int(row.get("grade3_enrolment", row.get("enrolment_grade3", 0)))}
    return School(
        udise_code=str(row["udise_code"]), name=str(row.get("school_name", row.get("name", "Synthetic school"))),
        state_lgd=str(row.get("state_lgd", "27")), district_lgd=str(row.get("district_lgd", "2701")), block_lgd=str(row["block_lgd"]),
        cluster_id=str(row.get("cluster_id")) if row.get("cluster_id") is not None else None,
        management=row.get("management", "government"), rural=bool(row.get("rural", True)), n_teachers=int(row.get("n_teachers", 0)),
        enrolment_by_grade=enrol, single_teacher=bool(row.get("single_teacher", False)),
        share_sc=float(row["share_sc"]) if row.get("share_sc") is not None else None,
        share_st=float(row["share_st"]) if row.get("share_st") is not None else None,
        provenance=_prov(SourceSystem.UDISE_PLUS, row.get("udise_code", "unknown")),
    )


def student_from_row(row: Mapping, salt: str) -> Student:
    return Student(
        student=pseudonymise(str(row["student_raw_id"]), salt), udise_code=str(row["udise_code"]), grade=int(row.get("grade", 3)),
        gender=row.get("gender", "x"), social_category=row.get("social_category"),
        home_language_matches_medium=bool(row["home_language_matches_medium"]) if row.get("home_language_matches_medium") is not None else None,
        provenance=_prov(SourceSystem.UDISE_PLUS, row["student_raw_id"]),
    )


def response_from_row(row: Mapping, salt: str) -> Response:
    return Response(
        student=pseudonymise(str(row["student_raw_id"]), salt), udise_code=str(row["udise_code"]), grade=int(row.get("grade", 3)),
        item_id=str(row["item_id"]), score=float(row["score"]), administered_by=Administrator(row.get("administered_by", "teacher")),
        assessed_on=row["assessed_on"], provenance=_prov(SourceSystem.CLASSROOM_TOOL, f"{row['student_raw_id']}:{row['item_id']}"),
    )
