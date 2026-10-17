import json
import os
from pathlib import Path
import sys
import tempfile

source = Path(os.environ['DU8_REVIEW_SOURCE'])
owned = Path(__file__).resolve().parent
checks = []
with tempfile.TemporaryDirectory(prefix='binding-', dir=owned) as directory:
    scratch = Path(directory)
    os.environ['REVENUE_PUBLICATION_REGISTRY'] = str(scratch / 'registry.jsonl')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(source/'scripts'),str(source/'tests'),str(source/'tests/fixtures/du8_comparison')]
    from revenue_core import run_forecast, ForecastInputError
    import revenue_report
    from models import legacy_annual_model, typed_level_model
    for factory in (legacy_annual_model,typed_level_model):
        data = factory()
        result = run_forecast(data)
        original = revenue_report.compare_target_measurement
        calls = []
        def flip(target, model, parameters=None, *, periods=None):
            rows = original(target, model, parameters, periods=periods)
            calls.append(True)
            for row in rows.values():
                row['meets_target'] = not row['meets_target']
            return rows
        revenue_report.compare_target_measurement = flip
        try:
            try:
                revenue_report.validate_forecast_output(result, data)
            except ForecastInputError:
                checks.append({'case':factory.__name__+':owner_flipped_verdict_is_consumed','pass':bool(calls)})
            else:
                checks.append({'case':factory.__name__+':owner_flipped_verdict_is_consumed','pass':False})
        finally:
            revenue_report.compare_target_measurement = original
        observed = []
        def echo(target, model, parameters=None, *, periods=None):
            withheld = target.get('scenario_comparison') is None and all(t.get('scenario_comparison') is None for t in model['management_target_coverage']['targets'])
            observed.append(withheld)
            return target.get('scenario_comparison') or {}
        revenue_report.compare_target_measurement = echo
        try:
            try:
                revenue_report.validate_forecast_output(result, data)
            except ForecastInputError:
                checks.append({'case':factory.__name__+':echo_cannot_self_validate','pass':bool(observed) and all(observed)})
            else:
                checks.append({'case':factory.__name__+':echo_cannot_self_validate','pass':False})
        finally:
            revenue_report.compare_target_measurement = original
payload={'reviewer':'/root/du8_rf_root_review','source':str(source),'passed':sum(row['pass'] for row in checks),'failed':sum(not row['pass'] for row in checks),'checks':checks,'temporary_directory_removed':not scratch.exists(),'http_calls':0,'supplier_calls':0}
(owned/'owner-binding-results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False,indent=2))
raise SystemExit(bool(payload['failed']))
