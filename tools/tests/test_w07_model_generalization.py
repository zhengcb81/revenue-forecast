"""W07-RF-MODEL: model generalization matrix — centralized fast tests.

Run with:  python -B -m pytest -q tools/tests/test_w07_model_generalization.py

These tests guard the *reusable matrix tool*, not the revenue engine's economic
quality.  They cover the adversarial behaviours the handoff contract names:

1.  the oracle must not be fooled by a wrong engine result (expected is computed
    from drivers, never from output);
2.  unknown values stay null, never 0;
3.  a native exception is captured, never swallowed into a PASS;
4.  scratch/cleanup restores the baseline (absent) even on error;
5.  a contaminated input is caught by the per-case driver self-check.

Monkeypatching here exercises the wrapper; node C separately runs the real
engine end-to-end.  Nothing here asserts a buy-side conclusion.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from model_generalization_matrix import bootstrap, cases as C  # noqa: E402
from model_generalization_matrix import oracle as O  # noqa: E402
from model_generalization_matrix.native import NativeEngine  # noqa: E402
from model_generalization_matrix.runner import run_case  # noqa: E402
from model_generalization_matrix import run as run_mod  # noqa: E402


@pytest.fixture(scope="module")
def runtime():
    return bootstrap.load_runtime()


@pytest.fixture()
def engine(runtime):
    return NativeEngine(runtime)


# --- 1. oracle independent of the engine ---------------------------------

def test_oracle_not_fooled_by_wrong_result(runtime):
    """A wrong engine result must FAIL the case; the oracle reads drivers only."""
    spec = C.case_index()["M01-L"]
    # expected is computed from frozen drivers, independent of any engine call
    expected_revenue = O.unit_sales_revenue([10.0, 12.0], [5.0, 5.0], [1.0, 1.0])
    assert expected_revenue == [50.0, 60.0]

    # Now feed a deliberately wrong result through the comparison path.
    from model_generalization_matrix.runner import _assert_values
    from model_generalization_matrix.runner import CaseResult

    bad_observed = {"revenue": {"2026": 999.0, "2027": 999.0}}

    case_res = CaseResult(
        case_id=spec.case_id, cls=spec.cls, vector=spec.vector, mode="draft",
        boundary=spec.boundary, status="NOT_RUN", expected=spec.expected,
    )
    out = _assert_values(spec, case_res, bad_observed)
    assert out.status == "FAIL", "oracle was fooled by a wrong result"


def test_oracle_accepts_correct_result():
    from model_generalization_matrix.runner import CaseResult, _assert_values

    spec = C.case_index()["M01-L"]
    good = {"revenue": {"2026": 50.0, "2027": 60.0}}
    case_res = CaseResult(
        case_id=spec.case_id, cls=spec.cls, vector=spec.vector, mode="draft",
        boundary=spec.boundary, status="NOT_RUN", expected=spec.expected,
    )
    out = _assert_values(spec, case_res, good)
    assert out.status == "PASS"


# --- 2. unknown stays null ----------------------------------------------

def test_unknown_cagr_is_null_not_zero(runtime):
    """M05: CAGR from a zero base is None, never 0."""
    assert O.cagr(0.0, 480.0, 2) is None
    spec = C.case_index()["M05-L"]
    engine = NativeEngine(runtime)
    data, observe = spec.build()
    result = engine.run_forecast(copy.deepcopy(data))
    obs = observe(result)
    assert obs["cagr"] is None, "zero-base CAGR must be null, not 0"


def test_unknown_assertion_rejects_zero():
    from model_generalization_matrix.runner import CaseResult, _assert_values

    spec = C.case_index()["M05-C"]
    case_res = CaseResult(
        case_id=spec.case_id, cls=spec.cls, vector=spec.vector, mode="draft",
        boundary=spec.boundary, status="NOT_RUN", expected=spec.expected,
    )
    # observed value 0 where an unknown is expected -> must FAIL (0 is a lie).
    out = _assert_values(spec, case_res, {"cagr": 0.0})
    assert out.status == "FAIL", "a 0 was accepted where an unknown (null) is required"


# --- 3. native exception captured, never a PASS --------------------------

def test_native_exception_is_captured_not_passed(runtime):
    spec = C.case_index()["M01-L"]

    class Boom(NativeEngine):
        def run_forecast(self, data):
            raise RuntimeError("synthetic native failure")

    engine = Boom(runtime)
    res = run_case(spec, engine)
    assert res.status == "ERROR"
    assert "synthetic native failure" in res.diagnostics.get("error", "")
    # The failure is recorded in diagnostics, and the case never became PASS.
    assert res.status != "PASS"


def test_unexpected_reject_on_legal_vector_fails(runtime):
    """A legal vector that is refused is a FAIL, not silently accepted."""
    spec = C.case_index()["M01-L"]

    class Refuse(NativeEngine):
        def run_forecast(self, data):
            raise ValueError("incompatible unit conversion")

    engine = Refuse(runtime)
    res = run_case(spec, engine)
    # M01-L expects a computed result, so a reject is a mismatch/failure.
    assert res.status in {"FAIL", "REJECT_MISMATCH"}


# --- 4. scratch/cleanup restores baseline -------------------------------

def test_cleanup_restores_absent_baseline(runtime, tmp_path):
    owned = tmp_path / "owned"
    out = tmp_path / "out"
    report = run_mod.run_matrix(out, owned, e2e=False)
    scratch = Path(report["cleanup"]["scratch_path"])
    assert not scratch.exists(), "scratch must be removed after the run"
    assert report["cleanup"].get("restored_absent") is True
    # read-only trees unchanged
    assert report["cleanup"].get("readonly_unchanged") is True


def test_cleanup_restores_on_error(runtime, tmp_path, monkeypatch):
    owned = tmp_path / "owned"
    out = tmp_path / "out"

    def boom(*a, **k):
        raise RuntimeError("mid-run failure")

    monkeypatch.setattr(run_mod, "run_case", boom)
    with pytest.raises(RuntimeError):
        run_mod.run_matrix(out, owned, e2e=False)
    # Even though the run raised, no scratch should be left behind.
    leftovers = list((owned / ".tmp").glob("w07-*")) if (owned / ".tmp").exists() else []
    assert leftovers == [], f"scratch not cleaned on error: {leftovers}"


# --- 5. input contamination caught --------------------------------------

def test_contaminated_input_is_caught():
    """If a builder's drivers drift from the frozen drivers, the case errors."""
    spec = C.case_index()["M01-L"]

    def contaminated_build():
        data, observe = spec.build()
        # Mutate a driver AFTER build to simulate contamination.
        for p in data["parameters"]:
            if p["parameter_id"].endswith("units_2026_base") or p["parameter_id"] == "unit_sales_units_2026_base":
                p["value"] = 999999.0
                break
        else:
            # fall back to first units driver
            for p in data["parameters"]:
                if "units" in p["parameter_id"] and p.get("scenario") == "base":
                    p["value"] = 999999.0
                    break
        return data, observe

    import dataclasses

    bad = dataclasses.replace(spec, build=contaminated_build)
    from model_generalization_matrix.runner import run_case as rc

    class _E(NativeEngine):
        pass

    from model_generalization_matrix import bootstrap as _b

    engine = _E(_b.load_runtime())
    res = rc(bad, engine)
    assert res.status == "ERROR", "contaminated input was not caught"
    assert "contamination" in res.diagnostics.get("error", "").lower()


def test_case_inputs_are_deep_isolated(runtime):
    """Mutating one case's input must not leak into another run of the same case."""
    spec = C.case_index()["M02-L"]
    data1, _ = spec.build()
    data1["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["new_arr"] = ["hacked"]
    data2, _ = spec.build()
    assert data2["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["new_arr"] != ["hacked"]


# --- structural coverage ------------------------------------------------

def test_sixteen_cases_eight_classes():
    assert len(C.CASES) == 16
    classes = {c.cls for c in C.CASES}
    assert classes == {"M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08"}
    for cls in classes:
        vecs = [c.vector for c in C.CASES if c.cls == cls]
        assert "legal" in vecs, f"{cls} missing a legal vector"
        assert any(v in {"counter", "unknown"} for v in vecs), f"{cls} missing a counter/unknown vector"


def test_every_expected_from_drivers_not_output():
    """The oracle module must not import or call the engine under test.

    Only real dependency signals are checked (import statements and call sites),
    not prose in the module docstring that merely names the engine.
    """
    import inspect
    import re

    src = inspect.getsource(O)
    assert not re.search(r"^\s*(?:import|from)\s+revenue_core\b", src, re.M), \
        "oracle must not import the engine under test"
    assert not re.search(r"\brun_forecast\s*\(", src), \
        "oracle must not call the engine under test"
    assert not re.search(r"\bconvert_input_quantity\s*\(", src), \
        "oracle must not call the unit-conversion entry"
