"""DAG parsing against the REAL frozen registries + synthetic unit logic."""

from __future__ import annotations

from conftest import REPO_ROOT
from uc.dag import _expand_dep_cell, load_dag, next_units


def test_expand_dep_cell_forms():
    assert _expand_dep_cell("无") == []
    assert _expand_dep_cell("") == []
    assert _expand_dep_cell("ZR-001") == ["ZR-001"]
    assert _expand_dep_cell("ZR-002,ZR-003") == ["ZR-002", "ZR-003"]
    assert _expand_dep_cell("ZR-101~104") == ["ZR-101", "ZR-102", "ZR-103", "ZR-104"]
    assert _expand_dep_cell("全部mandatory ZR/CA功能单元、CA-206") == ["CA-206"]


def test_real_ca_registry_structure():
    dag = load_dag(REPO_ROOT)
    ca_units = {unit: deps for unit, deps in dag.items() if unit.startswith("CA-")}
    zr_units = {unit: deps for unit, deps in dag.items() if unit.startswith("ZR-")}
    assert len(ca_units) == 25
    assert len(zr_units) == 92
    assert ca_units["CA-001"] == []
    assert ca_units["CA-002"] == ["CA-001"]
    assert zr_units["ZR-001"] == []
    assert zr_units["ZR-105"] == ["ZR-101", "ZR-102", "ZR-103", "ZR-104"]
    assert zr_units["ZR-102"] == ["ZR-002", "ZR-003"]


def test_next_units_after_ca001():
    dag = {"CA-001": [], "CA-002": ["CA-001"], "CA-003": ["CA-002"], "ZR-001": []}
    state = {"units": {"CA-001": {"status": "accepted"}}}
    unlocked = next_units(state, dag)
    assert "CA-001" not in unlocked
    assert "CA-002" in unlocked
    assert "ZR-001" in unlocked  # dependency-free, but single-writer rule applies
    assert "CA-003" not in unlocked


def test_next_units_respects_in_progress():
    dag = {"CA-001": [], "CA-002": ["CA-001"]}
    state = {
        "units": {
            "CA-001": {"status": "accepted"},
            "CA-002": {"status": "in_progress"},
        }
    }
    assert next_units(state, dag) == []


def test_next_units_accepts_already_satisfied():
    dag = {"CA-001": [], "CA-002": ["CA-001"]}
    state = {"units": {"CA-001": {"status": "already_satisfied"}}}
    assert next_units(state, dag) == ["CA-002"]
