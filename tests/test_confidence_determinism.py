"""Hash-seed and input-order regressions, independent of any issuer/ticker."""
from __future__ import annotations

import copy
from datetime import date
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analysis import confidence as confidence_model  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402


def synthetic_case():
    parameters, claims, sources = {}, {}, {}
    for i in range(20):
        claim_ids = []
        for j, support in enumerate(('exact_value', 'policy_support', 'rationale_support')[:1 + i % 3]):
            identity = f'p{i}-c{j}'
            claim_ids.append(identity)
            claims[identity] = {'support_type': support, 'source_id': identity}
            sources[identity] = {'published_date': ('2026-09-01', '2025-10-09', '2024-10-01')[j]}
        parameters[f'p{i}'] = {'claim_ids': claim_ids}
    inputs, outputs = [], []
    for i, amount in enumerate((1e16, .00001, 1.1, 1e6, .2)):
        refs = [f'p{n}' for n in range(i, i + 14)]
        inputs.append({'name': f's{i}', 'recognition': {}, 'scenarios': {
            'base': {'driver_parameter_ids': {'a': refs[:7], 'b': refs[7:]}}}})
        outputs.append({'name': f's{i}', 'scenarios': {'base': {
            'model': 'subscription', 'recognized_revenue': {'2027': amount}}}})
    data = {'segments': inputs, 'forecast_adjustments': [
        {'scenario_parameter_ids': {'base': ['p0', 'p3']}},
        {'scenario_parameter_ids': {'base': ['p1', 'p7']}},
    ]}
    validated = {'parameter_index': parameters, 'claim_index': claims,
                 'source_index': sources, 'as_of_date': date(2026, 10, 8),
                 'research_coverage': {'counts': {'data_gap': 0}}}
    result = {'segments': outputs, 'consolidated_forecast': {'base': {'adjustment_bridge': [
        {'annual_adjustment': {'2027': .0001}}, {'annual_adjustment': {'2027': 1.23}}]}},
        'constraint_audit': [{'parameter_ids': ['p0', 'p1'], 'changes': [
            {'adjustment': 1e15}, {'adjustment': .125}, {'adjustment': .75}]}]}
    sensitivity = [{'parameter_id': p, 'max_absolute_terminal_impact': v}
                   for p, v in (('p0', 1e16), ('p7', .1), ('p3', .5))]
    return data, validated, result, sensitivity


def test_identical_inputs_have_exact_confidence_across_process_hash_seeds():
    script = ('import json; from test_confidence_determinism import synthetic_case; '
              'from analysis.confidence import calculate_confidence; '
              'print(json.dumps(calculate_confidence(*synthetic_case()),sort_keys=True))')
    values = []
    for seed in (0, 1, 2, 17):
        environment = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONDONTWRITEBYTECODE='1',
                           PYTHONPATH=os.pathsep.join((str(ROOT / 'tests'), str(ROOT / 'scripts'))))
        completed = subprocess.run([sys.executable, '-B', '-c', script], env=environment,
                                   cwd=ROOT, capture_output=True, text=True, timeout=20, check=True)
        values.append(json.loads(completed.stdout))
    assert all(value == values[0] for value in values[1:])


def test_equivalent_aggregation_order_does_not_change_confidence():
    original = synthetic_case()
    data, validated, result, sensitivity = copy.deepcopy(original)
    data['segments'].reverse()
    result['segments'].reverse()
    data['forecast_adjustments'].reverse()
    result['consolidated_forecast']['base']['adjustment_bridge'].reverse()
    for parameter in validated['parameter_index'].values():
        parameter['claim_ids'].reverse()
    for entry in result['constraint_audit']:
        entry['changes'].reverse()
        entry['parameter_ids'].reverse()
    sensitivity.reverse()
    assert confidence_model.calculate_confidence(*original) == confidence_model.calculate_confidence(
        data, validated, result, sensitivity)


def test_shared_weight_contributions_retain_small_terms_and_stable_keys():
    data, _, result, _ = synthetic_case()
    weights = confidence_model.parameter_revenue_weights(data, result)
    assert list(weights) == sorted(weights)
    # p0 has s0, adjustment0, constraint0; this is independent of the model's reducer.
    expected = math.fsum((1e16 / 14, .0001 / 2, math.fsum((1e15, .125, .75)) / 2))
    assert weights['p0'] == expected


def test_new_confidence_contract_is_exact_and_legacy_float_noise_is_bounded():
    expected = confidence_model.calculate_confidence(*synthetic_case())
    assert expected['calculation_version'] == 'stable-fsum/1'
    confidence_model.validate_confidence_recomputation(expected, expected)
    perturbed = copy.deepcopy(expected)
    key = 'verified_claim_quality'
    perturbed['components'][key] = math.nextafter(perturbed['components'][key], math.inf)
    with pytest.raises(ForecastInputError, match='components'):
        confidence_model.validate_confidence_recomputation(expected, perturbed)
    legacy = copy.deepcopy(perturbed)
    legacy.pop('calculation_version')
    confidence_model.validate_confidence_recomputation(expected, legacy)
    legacy['components'][key] += .000001
    with pytest.raises(ForecastInputError, match='components'):
        confidence_model.validate_confidence_recomputation(expected, legacy)


@pytest.mark.parametrize('path,value', [
    ('driver_evidence_coverage', .123), ('sensitivity_concentration', .123),
    ('score', 1), ('historical_accuracy', {'wape': None, 'observations': 1}),
    ('historical_accuracy', {'wape': None, 'observations': False}),
])
def test_legacy_compatibility_cannot_hide_changed_contract_fields(path, value):
    expected = confidence_model.calculate_confidence(*synthetic_case())
    legacy = copy.deepcopy(expected)
    legacy.pop('calculation_version', None)
    legacy[path] = value
    with pytest.raises(ForecastInputError, match='recomputation mismatch'):
        confidence_model.validate_confidence_recomputation(expected, legacy)


def test_unknown_calculation_revision_does_not_fall_back_to_legacy():
    expected = confidence_model.calculate_confidence(*synthetic_case())
    altered = dict(expected, calculation_version='invented')
    with pytest.raises(ForecastInputError, match='calculation version'):
        confidence_model.validate_confidence_recomputation(expected, altered)


@pytest.mark.parametrize('steps,accepted', [(0, True), (64, True), (65, False)])
def test_legacy_roundoff_has_an_explicit_ulp_boundary(steps, accepted):
    expected = confidence_model.calculate_confidence(*synthetic_case())
    legacy = copy.deepcopy(expected)
    legacy.pop('calculation_version')
    key = 'verified_claim_quality'
    value = legacy['components'][key]
    for _ in range(steps):
        value = math.nextafter(value, math.inf)
    legacy['components'][key] = value
    if accepted:
        confidence_model.validate_confidence_recomputation(expected, legacy)
    else:
        with pytest.raises(ForecastInputError, match='components'):
            confidence_model.validate_confidence_recomputation(expected, legacy)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), True])
def test_legacy_roundoff_never_accepts_nonfinite_or_boolean_values(value):
    expected = confidence_model.calculate_confidence(*synthetic_case())
    legacy = copy.deepcopy(expected)
    legacy.pop('calculation_version')
    legacy['components']['verified_claim_quality'] = value
    with pytest.raises(ForecastInputError, match='components'):
        confidence_model.validate_confidence_recomputation(expected, legacy)


def test_formal_publication_is_strongly_valid_in_other_processes():
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0',
                       PYTHONPATH=os.pathsep.join((str(ROOT / 'tests'), str(ROOT / 'scripts'))))
    emit = ('import json; from test_recognition_bridge import forecast_document; '
            'from revenue_core import run_forecast; data=forecast_document(); '
            'print(json.dumps({"input":data,"result":run_forecast(data)}))')
    produced = subprocess.run([sys.executable, '-B', '-c', emit], env=environment,
                              cwd=ROOT, capture_output=True, text=True, timeout=20, check=True)
    payload = json.loads(produced.stdout)
    assert payload['result']['confidence']['calculation_version'] == 'stable-fsum/1'
    verify = ('import json,sys; from revenue_report import validate_published_forecast; '
              'pair=json.load(sys.stdin); validate_published_forecast(pair["result"],pair["input"])')
    for seed in (1, 2, 17):
        subprocess.run([sys.executable, '-B', '-c', verify], env=dict(environment, PYTHONHASHSEED=str(seed)),
                       cwd=ROOT, input=produced.stdout, capture_output=True, text=True, timeout=20, check=True)
