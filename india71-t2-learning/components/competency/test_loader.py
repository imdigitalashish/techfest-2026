from eval.sim.world import make_world
from components.competency import load_framework, load_q_matrix
from architecture.contracts.fln_contracts import Competency, Item


def test_framework_contracts_and_prereqs():
    comps = load_framework()
    assert len(comps) == 8
    assert all(isinstance(c, Competency) for c in comps)
    assert next(c for c in comps if c.code == "L.STORY").prerequisites == ["L.PARA"]


def test_q_matrix_items_validate():
    w = make_world(3, {"n_schools": 3, "n_clusters": 1})
    items = load_q_matrix(w.item_bank)
    assert len(items) >= 32
    assert all(isinstance(i, Item) for i in items)
