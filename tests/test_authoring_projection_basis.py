"""A precursor operating amount must not be relabelled final stressed revenue."""
from copy import deepcopy
from test_authoring_projection import neutral_document, neutral_plan
from research.authoring_projection import reconcile_authoring_explanations


def test_precursor_basis_and_actual_parameter_ref_remain_explicit():
    source, plan = neutral_document(), neutral_plan()
    basis = 'Before the separately modeled acceptance delay; no allocation of that delay to subscriptions versus services is assumed.'
    plan['scenario_bridges'][0]['basis'] = basis
    result = reconcile_authoring_explanations(source, plan)
    text = next(p for p in result['parameters'] if p['parameter_id'] == 'activity_low')['rationale']
    assert 'parent_low' in text
    assert basis in text
    assert 'recognized parent amount' not in text
    assert result['evidence_claims'] == source['evidence_claims']
    assert [p['value'] for p in result['parameters']] == [p['value'] for p in source['parameters']]


def test_absent_basis_does_not_infer_a_recognition_stage():
    source, plan = neutral_document(), neutral_plan()
    original = deepcopy(plan)
    result = reconcile_authoring_explanations(source, plan)
    for scenario in ('low', 'base', 'high'):
        text = next(p for p in result['parameters'] if p['parameter_id'] == f'activity_{scenario}')['rationale']
        assert f'parent_{scenario}' in text
        assert 'recognized parent amount' not in text
        assert 'Before the separately modeled' not in text
    assert plan == original


def test_timing_adjusted_total_does_not_invent_a_component_allocation():
    source, plan = neutral_document(), neutral_plan()
    source['parameters'].append({'parameter_id': 'timing_adjusted_total', 'scenario': 'low',
        'period': 'FY2031', 'unit': 'GBP million', 'value': 90})
    basis = 'Pre timing-stress operating path; allocation of the acceptance delay between components is unknown.'
    plan['scenario_bridges'][0]['basis'] = basis
    result = reconcile_authoring_explanations(source, plan)
    text = next(p for p in result['parameters'] if p['parameter_id'] == 'activity_low')['rationale']
    assert basis in text and 'parent_low' in text
    assert '-10.00%' in text and '-40.00%' not in text
    assert result['parameters'][-1] == source['parameters'][-1]
