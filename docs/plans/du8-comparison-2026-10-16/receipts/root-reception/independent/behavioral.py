import copy
from decimal import Decimal
import json
import os
from pathlib import Path
import sys
import tempfile

AUTHOR = Path(os.environ.get('DU8_REVIEW_SOURCE', 'C:/Users/郑曾波/Projects/revenue-forecast-du8-comparison'))
OWNED = Path(__file__).resolve().parent
checks = []
def check(label, condition, detail=None):
    checks.append({'case': label, 'pass': bool(condition), 'detail': detail})

with tempfile.TemporaryDirectory(prefix='behavior-', dir=OWNED) as temp:
    temp_path = Path(temp)
    sentinel = temp_path / 'sentinel'
    sentinel.write_bytes(b'unchanged source review')
    stamp = sentinel.stat().st_mtime_ns
    os.environ['REVENUE_PUBLICATION_REGISTRY'] = str(temp_path / 'registry.jsonl')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(AUTHOR / 'scripts'), str(AUTHOR / 'tests'), str(AUTHOR / 'tests/fixtures/du8_comparison')]
    from revenue_core import run_forecast, canonical_sha256
    import revenue_report
    from revenue_publication import _payload_sha256, _receipt_sha256
    from research.target_comparison import compare_target_measurement
    from models import legacy_annual_model, typed_level_model, typed_quarterly_model, growth_model, constrained_model, legacy_approximately_model, legacy_cumulative_model
    from test_management_targets import add_target
    from test_recognition_bridge import forecast_document

    def reseal(result):
        out = copy.deepcopy(result)
        receipt = out.get('publication_receipt')
        if isinstance(receipt, dict):
            receipt.pop('receipt_sha256', None)
            receipt.pop('validated_payload_sha256', None)
            receipt['validated_payload_sha256'] = _payload_sha256(out)
            receipt['receipt_sha256'] = _receipt_sha256(receipt)
        out['result_sha256'] = canonical_sha256({k:v for k,v in out.items() if k != 'result_sha256'})
        return out

    def reject(label, result, data=None):
        try:
            revenue_report.validate_forecast_output(reseal(result), data)
        except Exception as exc:
            check(label, type(exc).__name__ == 'ForecastInputError', type(exc).__name__ + ': ' + str(exc))
        else:
            check(label, False, 'ACCEPTED')

    # All anchors originate in the complete synthetic inputs and Decimal math,
    # never in the production comparison helper.
    for factory, modeled, target, ratio, meets in [
        (legacy_annual_model, Decimal('144'), Decimal('144'), Decimal(1), True),
        (legacy_approximately_model, Decimal('0.4905'), Decimal('0.5'), Decimal('0.981'), True),
        (legacy_cumulative_model, Decimal('120') + Decimal('144'), Decimal('260'), Decimal(264)/Decimal(260), True),
        (typed_level_model, Decimal(100), Decimal(1000), Decimal('0.1'), False),
        (constrained_model, Decimal(170)*Decimal(120)/Decimal(180), Decimal(144), Decimal(170)*Decimal(120)/Decimal(180)/Decimal(144), True),
    ]:
        data = factory()
        result = run_forecast(data)
        row = next(iter(result['management_target_coverage']['targets'][0]['scenario_comparison'].values()))
        check(factory.__name__ + ':independent_model_anchor', abs(float(modeled)-row['modeled_value']) < 1e-12)
        check(factory.__name__ + ':independent_target_anchor', float(target) == row['target_value'])
        check(factory.__name__ + ':independent_ratio_anchor', abs(float(ratio)-row['attainment_ratio']) < 1e-12)
        check(factory.__name__ + ':strict_bool_anchor', row['meets_target'] is meets)
        # Coherently forge a declaration and recompute all dependent rows. The
        # input target is untouched, so an input-bound validator must reject.
        forged = copy.deepcopy(result)
        candidate = forged['management_target_coverage']['targets'][0]
        candidate['comparison_tolerance'] = 0.249
        candidate['scenario_comparison'] = compare_target_measurement(candidate, forged)
        reject(factory.__name__ + ':forged_ledger_tolerance', forged, data)
    quarterly = run_forecast(typed_quarterly_model())
    qrow = quarterly['management_target_coverage']['targets'][0]['scenario_comparison']['low']
    check('quarterly_native_not_annualized', qrow['modeled_value'] == float(Decimal('105.84')*Decimal(1000)))
    check('quarterly_native_unit', qrow['unit'] == 'USD million')
    check('quarterly_range_no_invented_midpoint', qrow['target_value'] is None and qrow['attainment_ratio'] is None)
    growth_data = growth_model()
    growth_data['management_targets'][0]['comparison_basis']['base_period'] = None
    growth = run_forecast(growth_data)
    revenue_report.validate_forecast_output(growth, growth_data)
    grow_row = next(iter(growth['management_target_coverage']['targets'][0]['scenario_comparison'].values()))
    check('typed_missing_base_is_legal_null', grow_row['meets_target'] is None and grow_row['comparison_status'] == 'not_comparable', grow_row)
    for treatment in ('out_of_horizon', 'unmodeled_data_gap'):
        data = add_target(forecast_document(), period='FY2030', target_value=250, treatment=treatment)
        data['management_targets'][0].update(mapped_scenarios=[], mapped_parameter_ids=[])
        result = run_forecast(data)
        revenue_report.validate_forecast_output(result, data)
        check(treatment + ':no_comparison', result['management_target_coverage']['targets'][0]['scenario_comparison'] == {})
    # Exact old 3.1 row shape remains valid, as does 3.2; strip only the
    # historical fields the current producer adds to the declaration and rows.
    data = legacy_annual_model()
    for version in ('3.1', '3.2', '3.3'):
        old = run_forecast(data)
        old.update(schema_version=version, engine_version='3.4.0' if version == '3.3' else version+'.0')
        if version == '3.1':
            target = old['management_target_coverage']['targets'][0]
            for key in ('measurement_basis','measurement_periods','measurement_rationale'):
                target.pop(key, None)
            for row in target['scenario_comparison'].values():
                for key in ('measurement_basis','measurement_periods','modeled_period_values'):
                    row.pop(key, None)
        revenue_report.validate_forecast_output(reseal(old))
        check('legacy_version_' + version, True)
    # A report wrapper returning the stored rows cannot observe those rows.
    data = legacy_annual_model()
    result = run_forecast(data)
    original = revenue_report.compare_target_measurement
    captured = []
    def echo(target, model, parameters=None, *, periods=None):
        captured.append((target.get('scenario_comparison'), [t.get('scenario_comparison') for t in model['management_target_coverage']['targets']]))
        return target.get('scenario_comparison') or {}
    try:
        revenue_report.compare_target_measurement = echo
        reject('echo_wrapper_cannot_validate_itself', result, data)
    finally:
        revenue_report.compare_target_measurement = original
    check('echo_arguments_withhold_all_rows', bool(captured) and all(a is None and all(b is None for b in bs) for a,bs in captured), captured)
    check('sentinel_bytes_and_mtime', sentinel.read_bytes() == b'unchanged source review' and sentinel.stat().st_mtime_ns == stamp)
check('owned_temp_removed', not temp_path.exists())
payload = {'reviewer': '/root/du8_rf_root_review', 'source': str(AUTHOR), 'passed': sum(c['pass'] for c in checks), 'failed': sum(not c['pass'] for c in checks), 'supplier_calls': 0, 'http_calls': 0, 'checks': checks}
out = OWNED / ('behavioral-results.json' if AUTHOR.name == 'revenue-forecast-du8-comparison' else 'behavioral-final-results.json')
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(bool(payload['failed']))
