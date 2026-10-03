from datetime import date, datetime

import pytest
from pydantic import ValidationError

from architecture.contracts import models as m


def test_measurement_event_roundtrip():
    geo = m.GeoUnit(state_code="S1", district_code="D1", project_code="P1", sector_code="SC1", awc_code="A1")
    prov = m.Provenance(source=m.SourceSystem.SIMULATOR, source_record_id="r1", extracted_at=datetime(2026, 10, 4), synthetic=True)
    ev = m.MeasurementEvent(event_id="e1", child_key="c1", geo=geo, sex=m.Sex.FEMALE, dob=date(2025, 1, 1),
                            measured_on=date(2026, 1, 1), weight_kg=8.1, length_height_cm=72.0,
                            measure_position="recumbent", measured_by="w1", provenance=prov)
    assert m.MeasurementEvent.model_validate_json(ev.model_dump_json()) == ev


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        m.QualityFinding(code="X", severity="warn", detail="d", unexpected=1)
