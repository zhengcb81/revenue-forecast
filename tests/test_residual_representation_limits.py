"""Residual representation constraints are not research/source permissions."""
from copy import deepcopy
import json

import pytest

from filing_upstream_cause import failure_observation, parse_error_document, validated_filing_fetch_failure
from revenue_backtest import create_snapshot, evaluate_snapshot
from revenue_core import ForecastInputError, run_forecast, text_sha256
from test_backtest import actuals_document
from test_du67_typed_builder_composition import money_target_document, rebuild_target
from test_recognition_bridge import forecast_document
from test_r1_local_preparation_observation import wire, OBSERVATION


@pytest.mark.parametrize('excerpt', ['达标', 'Original business context. ' * 100], ids=['short', 'long'])
def test_target_builder_preserves_complete_nonempty_excerpt(excerpt):
    data = money_target_document(raw_value=1000, raw_currency='USD', raw_scale='million', comparison_value=1000)
    old = data['management_targets'][0]
    claim = next(c for c in data['evidence_claims'] if c['claim_id'] in old['claim_ids'])
    claim.update(excerpt=excerpt, excerpt_sha256=text_sha256(excerpt))
    # This test exercises excerpt construction, not model-target construction.
    # Preserve the existing model's scope/benchmark component references while
    # consuming the builder's actual source claims through the native validator.
    native = deepcopy(data)
    built = rebuild_target(data, treatment=old['treatment'])
    assert any(c['excerpt'] == excerpt for c in built['claims'])
    native['management_targets'][0]['claim_ids'] = built['target']['claim_ids']
    native['evidence_claims'] = [c for c in native['evidence_claims']
                                 if c['claim_id'] not in old['claim_ids']] + built['claims']
    run_forecast(native)


def test_backtest_long_excerpt_keeps_real_hash_and_currency_checks():
    snapshot = create_snapshot(forecast_document(), 'residual')
    actuals = actuals_document()
    for claim in actuals['evidence_claims']:
        claim['excerpt'] += ' Original same-basis reported context.' * 40
        claim['excerpt_sha256'] = text_sha256(claim['excerpt'])
    evaluate_snapshot(snapshot, actuals)
    bad = deepcopy(actuals)
    bad['evidence_claims'][0]['excerpt'] += 'tamper'
    with pytest.raises(ForecastInputError, match='excerpt/hash'):
        evaluate_snapshot(snapshot, bad)
    bad = deepcopy(actuals)
    bad['currency'] = 'CNY'
    with pytest.raises(ForecastInputError, match='currency/unit'):
        evaluate_snapshot(snapshot, bad)


def widen_drivers(data, count, evidence_count):
    original = data['growth_driver_tree']['drivers'][0]
    base_nodes = original['evidence_nodes']
    claims = {c['claim_id']: c for c in data['evidence_claims']}
    widened = []
    for i in range(count):
        driver = deepcopy(original)
        driver['driver_id'] = f'wide_driver_{i}'
        for entry in driver['segment_attribution']:
            entry['weight'] /= count
        driver['evidence_nodes'] = []
        for j in range(evidence_count):
            node = deepcopy(base_nodes[j % len(base_nodes)])
            node['evidence_id'] = f'wide_evidence_{i}_{j}'
            new_claims = []
            for old_id in node['claim_ids']:
                claim = deepcopy(claims[old_id])
                claim['claim_id'] = f'wide_claim_{i}_{j}_{old_id}'
                claim['target_id'] = node['evidence_id']
                data['evidence_claims'].append(claim)
                new_claims.append(claim['claim_id'])
            node['claim_ids'] = new_claims
            driver['evidence_nodes'].append(node)
        widened.append(driver)
    data['growth_driver_tree']['drivers'] = widened + data['growth_driver_tree']['drivers'][1:]
    return data


@pytest.mark.parametrize('count,evidence_count', [(11, 2), (1, 11)])
def test_complete_driver_tree_and_evidence_not_cut_to_ten(count, evidence_count):
    data = widen_drivers(forecast_document(), count, evidence_count)
    output = run_forecast(data)
    assert len(output['growth_driver_analysis']['drivers']) == len(data['growth_driver_tree']['drivers'])
    assert abs(output['growth_driver_analysis']['reconciliation']['difference']) < 1e-8
    bad = deepcopy(data)
    bad['growth_driver_tree']['drivers'][0]['segment_attribution'][0]['weight'] += .25
    with pytest.raises(ForecastInputError, match='attribution weight'):
        run_forecast(bad)


def test_local_failure_large_deep_diagnostics_are_complete_and_isolated():
    payload = wire(diagnostics=1500)
    branch = {'counter': 3}
    for _ in range(24):
        branch = {'next': branch}
    payload[OBSERVATION]['operations'].append(branch)
    result = validated_filing_fetch_failure(payload)
    assert result == payload
    result[OBSERVATION]['diagnostics'][0]['reason'] = 'changed'
    assert result != payload
    assert parse_error_document(json.dumps(payload)) == payload


def test_invalid_optional_observation_does_not_erase_primary_failure():
    payload = wire()
    payload[OBSERVATION]['diagnostics'] = [{'path': 'not_a_public_location'}]
    result = failure_observation(payload)
    assert result['upstream_cause'] == payload['filing']['upstream_cause']
    assert result['filing_fetch_result']['filing'] == payload['filing']
    assert OBSERVATION not in result['filing_fetch_result']
    assert result['downloads'] == 0


def test_availability_proof_has_no_text_length_permission():
    from contracts.source_clock import validate_availability_evidence, SourceClockError
    from test_source_clock import proof
    value = proof('a' * 64)
    value['evidence_ref'] = 'urn:owner:capture:' + 'a' * 6000
    value['locator'] = 'logical/member/' + 'b' * 6000
    assert validate_availability_evidence(value, 'a' * 64) == value
    with pytest.raises(SourceClockError, match='version_mismatch'):
        validate_availability_evidence(value, 'b' * 64)
