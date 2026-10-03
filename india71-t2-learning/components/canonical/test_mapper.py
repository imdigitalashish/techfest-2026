from eval.sim.world import make_world
from components.canonical import pseudonymise, response_from_row, school_from_row, student_from_row
from architecture.contracts.fln_contracts import Response, School, Student


def test_pseudonymise_format_and_salt():
    assert pseudonymise("a", "s").startswith("ps_")
    assert len(pseudonymise("a", "s")) == 19
    assert pseudonymise("a", "s") != pseudonymise("a", "t")


def test_world_rows_validate_contracts():
    w = make_world(2, {"n_schools": 5, "n_clusters": 2})
    assert isinstance(school_from_row(w.schools.iloc[0]), School)
    assert isinstance(student_from_row(w.children.iloc[0], "salt"), Student)
    assert isinstance(response_from_row(w.item_responses.iloc[0], "salt"), Response)
