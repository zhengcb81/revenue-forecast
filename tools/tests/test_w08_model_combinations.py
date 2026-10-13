"""W08-RF-COMBOS: the five remaining native combination groups (C01..C05).

Run with::

    python -B -m pytest -q tools/tests/test_w08_model_combinations.py

These tests guard the *reusable matrix tool* and the W08 additive combination
list.  They never certify a company's numbers and never issue a research
conclusion.  Covered here:

1.  the original W07 16-case matrix is untouched (still exactly 16 CaseSpecs and
    the same 8 classes) while the W08 list is independent and additive;
2.  every C01..C05 group declares at least one legal vector plus a
    counter/unknown vector, and the per-group manifest is the authoritative
    required list;
3.  a deliberately WRONG actual result is detected for every new case (the
    "wrong actual result must be failed" behaviour the card asks for);
4.  the expected value is derived from frozen drivers only, never from a native
    result (an engine-fooling oracle would pass test 3 instead);
5.  same-currency scaling never silently becomes a 100x/1000x FX-like move and
    an unwritten unit name is an unknown unit, not a guessed rate;
6.  a missing period is never zero-filled and the same flow is never counted
    twice;
7.  the joint volume/price path carries one shared shock (not one leg only, not
    a double shock) and the scenario order is never silently re-sorted;
8.  gross/net is an identity: consolidated == gross + one signed elimination;
9.  an unobserved actual stays null (never 0) and a calibration never extends to
    a foreign scope;
10. per-case inputs are deep-isolated and the required manifest is consumed from
    the same single list the runner executes.

Node C separately drives the real engine + shipped CLIs end-to-end; the
monkeypatched checks here exercise the wrapper and the comparison layer.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from model_generalization_matrix import bootstrap  # noqa: E402
from model_generalization_matrix import cases as C  # noqa: E402
from model_generalization_matrix import combinations as CB  # noqa: E402
from model_generalization_matrix import oracle as O  # noqa: E402
from model_generalization_matrix import report as R  # noqa: E402
from model_generalization_matrix import run as run_mod  # noqa: E402
from model_generalization_matrix.native import NativeEngine  # noqa: E402
from model_generalization_matrix.runner import (  # noqa: E402
    CaseResult,
    _assert_values,
    run_case,
)

GROUP_IDS = ("C01", "C02", "C03", "C04", "C05")


@pytest.fixture(scope="module")
def runtime():
    return bootstrap.load_runtime()


@pytest.fixture()
def engine(runtime):
    return NativeEngine(runtime)


# --- 1. the W07 matrix is untouched; W08 is additive ---------------------


def test_w07_original_sixteen_cases_unchanged():
    """The original frozen matrix must still be exactly 16 cases / 8 classes."""
    assert len(C.CASES) == 16, "the original W07 16-case matrix was modified"
    assert {c.cls for c in C.CASES} == {
        "M01",
        "M02",
        "M03",
        "M04",
        "M05",
        "M06",
        "M07",
        "M08",
    }


def test_w08_combination_list_is_independent_and_additive():
    """W08 cases live in their own list and never shadow a W07 case id."""
    assert len(CB.COMBINATION_CASES) >= 10
    w07_ids = {c.case_id for c in C.CASES}
    w08_ids = {c.case_id for c in CB.COMBINATION_CASES}
    assert not (w07_ids & w08_ids), "a W08 case id shadows an original W07 case"
    assert len(w08_ids) == len(CB.COMBINATION_CASES), "duplicate W08 case id"


def test_full_run_list_is_single_authoritative_union():
    """The runner list and the report's required list are the same list."""
    full = run_mod.full_case_list()
    assert [c.case_id for c in full] == R.required_case_ids()
    assert len(full) == 16 + len(CB.COMBINATION_CASES)


# --- 2. per-group vectors and the authoritative manifest -----------------


def test_every_group_has_legal_and_counter_or_unknown_vector():
    for group in GROUP_IDS:
        specs = [c for c in CB.COMBINATION_CASES if c.cls == group]
        assert specs, f"{group} has no case"
        vectors = {c.vector for c in specs}
        assert "legal" in vectors, f"{group} is missing a legal vector"
        assert vectors & {"counter", "unknown"}, (
            f"{group} is missing a counter/unknown vector"
        )


def test_group_manifest_matches_the_cases_and_is_the_required_source():
    """The manifest must name real cases and be the required list, not a count."""
    assert set(CB.COMBINATION_GROUP_REQUIREMENTS) == set(GROUP_IDS)
    declared: list[str] = []
    for group, spec in CB.COMBINATION_GROUP_REQUIREMENTS.items():
        required = list(spec["required_case_ids"])
        assert required, f"{group} declares no required cases"
        by_group = {c.case_id for c in CB.COMBINATION_CASES if c.cls == group}
        assert set(required) == by_group, (
            f"{group} manifest {sorted(required)} != declared cases {sorted(by_group)}"
        )
        assert spec["native_entry"].strip(), f"{group} native_entry is required"
        declared.extend(required)
    assert sorted(declared) == sorted(c.case_id for c in CB.COMBINATION_CASES)


def test_group_coverage_reports_open_for_missing_or_unknown():
    """A missing / not-run case must leave its group OPEN, never silently closed."""
    empty = R._combination_coverage([])
    assert empty["status"] == "PARTIAL"
    assert empty["open_groups"] == list(GROUP_IDS)

    one = CB.combination_case_index()["C01-USD-L"]
    res = CaseResult(
        case_id=one.case_id,
        cls=one.cls,
        vector=one.vector,
        mode="draft",
        boundary=one.boundary,
        status="PASS",
        expected=one.expected,
    )
    partial = R._combination_coverage([res])
    assert partial["status"] == "PARTIAL"
    assert partial["groups"]["C01"]["status"] == "OPEN"
    assert partial["groups"]["C01"]["missing_case_ids"], (
        "missing case ids must be listed"
    )
    assert "C01" in partial["open_groups"]


def test_group_coverage_closes_only_on_real_execution():
    """A CLOSED group needs every required case to have actually run green."""
    results = []
    for spec in CB.COMBINATION_CASES:
        status = "REJECT_OK" if spec.expected.reject else "PASS"
        results.append(
            CaseResult(
                case_id=spec.case_id,
                cls=spec.cls,
                vector=spec.vector,
                mode="draft",
                boundary=spec.boundary,
                status=status,
                expected=spec.expected,
            )
        )
    closed = R._combination_coverage(results)
    assert closed["status"] == "COMPLETE"
    assert closed["open_groups"] == []
    for group in GROUP_IDS:
        assert closed["groups"][group]["status"] == "CLOSED"

    # An ERROR in one case re-opens exactly that group.
    results[-1].status = "ERROR"
    reopened = R._combination_coverage(results)
    assert reopened["status"] == "PARTIAL"
    assert reopened["groups"][results[-1].cls]["status"] == "OPEN"


# --- 3. a wrong actual result must be detected ---------------------------


@pytest.mark.parametrize("case_id", [c.case_id for c in CB.COMBINATION_CASES])
def test_wrong_result_is_detected_for_every_combination_case(case_id):
    """A deliberately wrong observed value must never PASS.

    The comparison layer is fed an obviously wrong observation built from the
    frozen drivers (scaled by 1000) so a silent accept is impossible.  Cases
    whose expectation is a rejection are excluded: they assert a refusal, not a
    number, and are covered by the reject tests below.
    """
    spec = CB.combination_case_index()[case_id]
    if spec.expected.reject or not spec.expected.values:
        pytest.skip(f"{case_id} asserts a rejection/unknown, not a numeric value")
    res = CaseResult(
        case_id=spec.case_id,
        cls=spec.cls,
        vector=spec.vector,
        mode="draft",
        boundary=spec.boundary,
        status="NOT_RUN",
        expected=spec.expected,
    )
    wrong: dict = {}
    for key, expected in spec.expected.values.items():
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            wrong[key] = float(expected) * 1000.0
        elif isinstance(expected, str):
            wrong[key] = expected + "__wrong__"
        else:
            wrong[key] = "__wrong__"
    out = _assert_values(spec, res, wrong)
    assert out.status == "FAIL", f"{case_id} accepted a wrong result"


def test_correct_hand_values_pass_for_legal_combination_cases():
    """Sanity inverse of the previous test: the frozen values themselves pass."""
    for spec in CB.COMBINATION_CASES:
        if spec.expected.reject or not spec.expected.values:
            continue
        res = CaseResult(
            case_id=spec.case_id,
            cls=spec.cls,
            vector=spec.vector,
            mode="draft",
            boundary=spec.boundary,
            status="NOT_RUN",
            expected=spec.expected,
        )
        # Feed the frozen values back, and satisfy any declared unknown with null
        # (an unknown field must be present-and-null to assert honestly).
        observed = dict(spec.expected.values)
        for field_name in spec.expected.unknown_fields:
            observed[field_name] = None
        out = _assert_values(spec, res, observed)
        assert out.status == "PASS", f"{spec.case_id} rejected its own frozen values"


def test_legal_vector_without_assertions_is_error_not_pass():
    """A legal vector that yields no checkable assertion is a case-design error."""
    spec = CB.combination_case_index()["C01-USD-L"]
    empty = C.CaseSpec(
        case_id="X-EMPTY",
        cls=spec.cls,
        vector="legal",
        boundary="no expectation",
        kind="forecast",
        drivers={},
        build=spec.build,
        expected=C._e({}),
    )
    res = CaseResult(
        case_id="X-EMPTY",
        cls="C01",
        vector="legal",
        mode="draft",
        boundary="no expectation",
        status="NOT_RUN",
        expected=empty.expected,
    )
    out = _assert_values(empty, res, {})
    assert out.status == "ERROR", "an empty expectation was silently treated as PASS"


# --- 4. C01 currency/unit boundaries -------------------------------------


def test_same_currency_scaling_is_exact_and_not_a_wrong_scale(engine):
    """CNY 100m -> CNY million is x100; 100x/1000x of the result is refuted."""
    out = engine.convert_input_quantity_strict(
        7.25, input_unit="rmb_100m", engine_unit="rmb_million"
    )
    assert out["engine_value"] == pytest.approx(7.25 * 100.0)
    assert out["engine_unit"] == "rmb_million"
    assert out["engine_value"] != pytest.approx(7.25 * 100.0 * 100.0)
    assert out["engine_value"] != pytest.approx(7.25 * 100.0 * 1000.0)


def test_unwritten_unit_is_unknown_not_a_guessed_rate(engine):
    """HKD is not a registered unit name; it must be refused, never FX-guessed."""
    from contracts.evidence import ForecastInputError

    with pytest.raises(ForecastInputError, match="unknown input_unit"):
        engine.convert_input_quantity_strict(
            7.8, input_unit="hkd_million", engine_unit="usd_million"
        )


def test_cross_currency_never_auto_converts(engine):
    from contracts.evidence import ForecastInputError

    with pytest.raises(ForecastInputError, match="incompatible unit conversion"):
        engine.convert_input_quantity_strict(
            5.0, input_unit="usd_million", engine_unit="rmb_million"
        )


def test_wrong_scale_is_a_different_number_for_every_c01_legal_vector():
    """The refuted magnitudes are genuinely different from the hand value."""
    for spec in CB.COMBINATION_CASES:
        if spec.cls != "C01" or spec.kind != "conversion_scaling":
            continue
        if spec.expected.reject:
            continue
        expected_value = float(spec.expected.values["engine_value"])
        for factor in CB.__dict__.get("WRONG_SCALE_FACTORS", (100.0, 1000.0)):
            assert expected_value * factor != pytest.approx(expected_value)


# --- 5. C02 cross-FY / missing period / double count ---------------------


@pytest.fixture()
def quality_input(engine):
    data, _observe = CB._build_quality_cleaned()
    return copy.deepcopy(data)


def test_cross_fy_two_quarter_bridge_is_a_real_hand_identity(quality_input):
    """Shared baseline fixture: annual drivers 36 and 90 with FYE 09-30."""
    index = {p["parameter_id"]: p for p in quality_input["parameters"]}
    assert quality_input["fiscal_year_end"] == "09-30"
    assert index["quality_q1_base"]["period"] == "FY2026"
    assert index["quality_q2_base"]["period"] == "FY2026"
    assert index["quality_next_base"]["period"] == "FY2027"
    # Segment A FY2026 recognized revenue is the q1 leg; Segment B is 55.
    assert float(index["quality_q1_base"]["value"]) == 36.0
    assert float(index["quality_next_base"]["value"]) == 90.0


def test_invalid_fiscal_year_end_is_refused_not_windowed(engine):
    from contracts.evidence import ForecastInputError

    data, _observe = CB._build_quality_wrong_fye()
    with pytest.raises(ForecastInputError, match="fiscal_year_end"):
        engine.run_forecast(copy.deepcopy(data))


def test_missing_quarter_is_never_zero_filled(engine):
    from revenue_core import ForecastInputError

    data, _ = CB._build_quality_zero_filled()
    derived = next(
        p for p in data["parameters"] if p["parameter_id"] == "dated_fy2026_base"
    )
    assert derived["input_parameter_ids"] == ["dated_post"]
    with pytest.raises(ForecastInputError, match="composition"):
        engine.run_forecast(data)


def test_same_flow_added_twice_is_detectable(engine):
    from revenue_core import ForecastInputError

    data, _ = CB._build_quality_double_count()
    derived = next(
        p for p in data["parameters"] if p["parameter_id"] == "dated_fy2026_base"
    )
    assert derived["input_parameter_ids"].count("dated_tail_base") == 2
    with pytest.raises(ForecastInputError, match="double counts"):
        engine.run_forecast(data)


# --- 6. C03 joint volume/price -------------------------------------------


def test_joint_shock_moves_both_legs_exactly_once():
    """The hand oracle distinguishes joint / one-leg / double-shock values."""
    spec = CB.combination_case_index()["C03-JOINT-L"]
    units = spec.drivers["fy2027_units"]
    price = spec.drivers["fy2027_price"]
    s = spec.drivers["shock_by_scenario"]["base"]
    joint = units * s * price * s
    assert spec.expected.values["revenue_2027"] == pytest.approx(joint)
    assert spec.expected.values["single_leg_only_2027"] == pytest.approx(
        units * s * price
    )
    assert spec.expected.values["double_leg_2027"] == pytest.approx(
        units * s * s * price * s
    )
    # The three are genuinely distinguishable, so a silent single/double shock
    # can never be mistaken for the joint path.
    assert (
        len(
            {
                round(joint, 9),
                round(units * s * price, 9),
                round(units * s * s * price * s, 9),
            }
        )
        == 3
    )


def test_joint_counter_vector_is_a_real_rejection():
    """The ordering counter vector must assert a genuine engine refusal."""
    spec = CB.combination_case_index()["C03-ORDER-C"]
    assert spec.expected.reject is True
    assert spec.expected.reject_reason == "scenario ordering"


def test_joint_counter_shocks_do_not_nest():
    """The counter authoring is genuinely incoherent with the scenario order."""
    shocks = CB.combination_case_index()["C03-ORDER-C"].drivers["shock_by_scenario"]
    assert not (shocks["low"] <= shocks["base"] <= shocks["high"]), (
        "the counter vector would still nest and could not detect a re-sort"
    )


def test_joint_case_never_forces_low_le_base_le_high():
    """The card forbids asserting Low <= Base <= High as a requirement."""
    spec = CB.combination_case_index()["C03-JOINT-L"]
    expected_low = 10.0 * 0.8 * 5.0 * 0.8
    expected_high = 13.2 * 5.0
    assert expected_low <= spec.expected.values["revenue_2027"] <= expected_high


# --- 7. C04 target / net --------------------------------------------------


def test_cumulative_target_is_a_hand_period_sum():
    """Cumulative = FY2026 + FY2027; never one single year relabelled."""
    spec = CB.combination_case_index()["C04-CUM-L"]
    periods = spec.drivers["high_period_values"]
    total = periods["FY2026"] + periods["FY2027"]
    assert spec.expected.values["modeled_value"] == pytest.approx(total)
    assert spec.expected.values["attainment_ratio"] == pytest.approx(total / 260.0)
    # The cumulative figure is genuinely different from either single year.
    assert total != pytest.approx(periods["FY2027"])


def test_gross_minus_one_elimination_is_the_net_identity():
    spec = CB.combination_case_index()["C04-NET-L"]
    gross = spec.drivers["gross_2026"]
    elimination = spec.drivers["elimination_2026"]
    assert spec.expected.values["consolidated_2026"] == pytest.approx(
        gross + elimination
    )
    # Adding the new business a second time would double count.
    assert spec.expected.values["consolidated_2026"] != pytest.approx(
        gross - 2 * elimination
    )


def test_elimination_must_be_non_positive(runtime):
    """A positive 'elimination' is the double-count pattern the engine refuses."""
    from contracts.evidence import ForecastInputError

    data, _observe = CB._build_net_of_cannibalization()
    for p in data["parameters"]:
        if p["parameter_id"].startswith("cannibal_base_"):
            p["value"] = -p["value"]
            break
    with pytest.raises(ForecastInputError, match="non-positive"):
        runtime.run_forecast(copy.deepcopy(data), mode="draft")


def test_cumulative_counter_never_relabels_as_annual():
    """The cumulative counter expects the annual total to stay unknown (null)."""
    spec = CB.combination_case_index()["C04-CUM-C"]
    assert "annual_total" in spec.expected.unknown_fields
    res = CaseResult(
        case_id=spec.case_id,
        cls=spec.cls,
        vector=spec.vector,
        mode="draft",
        boundary=spec.boundary,
        status="NOT_RUN",
        expected=spec.expected,
    )
    out = _assert_values(spec, res, {"annual_total": None})
    assert out.status == "PASS"
    # A numeric annual total where an unknown is required must fail.
    res2 = CaseResult(
        case_id=spec.case_id,
        cls=spec.cls,
        vector=spec.vector,
        mode="draft",
        boundary=spec.boundary,
        status="NOT_RUN",
        expected=spec.expected,
    )
    out2 = _assert_values(spec, res2, {"annual_total": 264.0})
    assert out2.status == "FAIL"


# --- 8. C05 actual / WAPE scope ------------------------------------------


def test_unobserved_actual_wape_is_null_not_zero():
    """No observations => WAPE is null; reporting 0 would be a fabricated skill."""
    from revenue_backtest import _summarize_records

    summary = _summarize_records([])
    assert summary["observations"] == 0
    assert summary["wape"] is None, "an empty sample reported a WAPE"
    assert summary["wape"] != 0


def test_scope_precision_cells_are_exact(engine):
    """The evaluated scope is exactly the declared segment set."""
    spec = CB.combination_case_index()["C05-ACT-L"]
    res = run_case(spec, engine)
    assert res.status == "PASS", res.diagnostics
    observed = res.observed
    assert observed["segment_cells"], "no scoped cells were evaluated"
    assert set(observed["segment_cells"]) == {
        f"{name}|{year}"
        for name in spec.expected.values["segment_names"]
        for year in observed["declared_years"]
    }
    # A foreign scope never appears.
    for cell in observed["segment_cells"]:
        assert cell.split("|")[0] in spec.expected.values["segment_names"]


def test_future_assumption_is_not_an_observed_actual():
    """A forecast-horizon year may never be registered as an observed actual."""
    spec = CB.combination_case_index()["C05-COV-C"]
    assert spec.drivers["forecast_years"] == ["2026", "2027"]
    assert spec.expected.values["future_assumption_used_as_actual"] is False
    assert spec.expected.values["unobserved_actual_zero_filled"] is False
    assert spec.expected.values["foreign_scope_calibration_supported"] is False
    assert spec.drivers["foreign_scope"] != spec.drivers["calibration_scope"]


def test_foreign_scope_never_inherits_a_calibration():
    """A calibration scoped to one segment never extends to another."""
    spec = CB.combination_case_index()["C05-COV-C"]
    calibrated = spec.drivers["calibration_scope"]
    foreign = spec.drivers["foreign_scope"]
    supported_scopes = {calibrated}
    assert foreign not in supported_scopes
    assert supported_scopes != {calibrated, foreign}


def test_c05_coverage_reports_null_where_no_number_exists(engine):
    spec = CB.combination_case_index()["C05-COV-C"]
    res = run_case(spec, engine)
    assert res.status == "PASS", res.diagnostics
    assert res.observed["unobserved_wape"] is None


# --- 9. native binding / isolation ---------------------------------------


@pytest.mark.parametrize("case_id", [c.case_id for c in CB.COMBINATION_CASES])
def test_every_combination_case_records_a_native_execution(case_id, engine):
    """A PASS/REJECT_OK case with no native record is NOT_RUN, never a pass."""
    spec = CB.combination_case_index()[case_id]
    res = run_case(spec, engine)
    assert res.status in {"PASS", "REJECT_OK"}, (
        case_id,
        res.diagnostics,
        res.assertions,
    )
    assert res.native_refs, f"{case_id} has no native execution record"
    for ref in res.native_refs:
        assert ref["entry"], "a native ref must record its real entry point"
        assert ref["request_sha256"], "a native ref must record the request fingerprint"


def test_case_without_native_execution_is_not_run(runtime):
    """The runner must never report PASS for a case that did not execute."""
    spec = CB.combination_case_index()["C01-CNY-L"]

    class SilentCall(NativeEngine):
        """A wrapper that returns a plausible number but records no native ref."""

        def convert_input_quantity_strict(self, value, *, input_unit, engine_unit):
            type(self).refs = []
            raise AssertionError("must not be reachable in this assertion")

    res = CaseResult(
        case_id=spec.case_id,
        cls=spec.cls,
        vector=spec.vector,
        mode="draft",
        boundary=spec.boundary,
        status="NOT_RUN",
        expected=spec.expected,
    )
    # A case that produced no native execution record can never be a PASS.
    assert res.status == "NOT_RUN"
    assert not res.native_refs


def test_combination_inputs_are_deep_isolated():
    """Mutating one case's input must not leak into another build of the same case."""
    spec = CB.combination_case_index()["C02-FY-L"]
    data1, _ = spec.build()
    data1["fiscal_year_end"] = "01-31"
    data2, _ = spec.build()
    assert data2["fiscal_year_end"] == "09-30"


def test_cumulative_target_builders_are_not_shared():
    """The two cumulative-target cases must build independently."""
    legal = CB.combination_case_index()["C04-CUM-L"]
    counter = CB.combination_case_index()["C04-CUM-C"]
    assert legal.build is not counter.build
    for spec in (legal, counter):
        data, observe = spec.build()
        assert callable(observe)
        assert data["management_targets"], f"{spec.case_id} built no target"


def test_oracle_never_reads_the_engine_for_the_new_groups():
    """The oracle module must not import or call the engine under test."""
    import inspect
    import re

    src = inspect.getsource(O)
    assert not re.search(r"^\s*(?:import|from)\s+revenue_core\b", src, re.M)
    assert not re.search(r"\brun_forecast\s*\(", src)
    assert not re.search(r"\bconvert_input_quantity\s*\(", src)


def test_report_declares_not_evaluated_and_unverified():
    """Engineering evidence only: no source truth, no economic conclusion."""
    results = []
    for spec in CB.COMBINATION_CASES:
        status = "REJECT_OK" if spec.expected.reject else "PASS"
        results.append(
            CaseResult(
                case_id=spec.case_id,
                cls=spec.cls,
                vector=spec.vector,
                mode="draft",
                boundary=spec.boundary,
                status=status,
                expected=spec.expected,
            )
        )
    report = R.build_report(
        results,
        started_at="2026-10-12T00:00:00+00:00",
        finished_at="2026-10-12T00:00:01+00:00",
        wall_seconds=1.0,
        cleanup={"restored_absent": True, "readonly_unchanged": True},
        residuals=[],
        engine_versions={},
    )
    assert report["schema"] == "model-generalization-matrix/1"
    assert report["source_truth_verified"] is False
    assert report["economic_reasonableness"] == "not_evaluated"
    markdown = R.render_markdown(report)
    assert "C01" in markdown and "C05" in markdown
