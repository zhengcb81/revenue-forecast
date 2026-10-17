import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

AUTHOR = Path(os.environ.get('DU8_REVIEW_SOURCE', 'C:/Users/郑曾波/Projects/revenue-forecast-du8-comparison'))
OWNED = Path(__file__).resolve().parent
paths = ['scripts/research/target_comparison.py', 'scripts/research/targets.py', 'scripts/revenue_report.py', 'tests/fixtures/du8_comparison/models.py', 'tests/test_du8_owner_enforcement.py']
before = {p: hashlib.sha256((AUTHOR / p).read_bytes()).hexdigest() for p in paths}
rows = []
with tempfile.TemporaryDirectory(prefix='review-', dir=OWNED) as temp:
    scratch = Path(temp)
    sentinel = scratch / 'sentinel'
    sentinel.write_bytes(b'ROOT independent reviewer sentinel')
    stamp = sentinel.stat().st_mtime_ns
    os.environ['REVENUE_PUBLICATION_REGISTRY'] = str(scratch / 'registry.jsonl')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(AUTHOR / 'scripts'), str(AUTHOR / 'tests'), str(AUTHOR / 'tests/fixtures/du8_comparison')]
    from revenue_core import run_forecast, canonical_sha256
    from revenue_report import validate_forecast_output
    from revenue_publication import _payload_sha256, _receipt_sha256
    from models import legacy_annual_model, typed_level_model, typed_quarterly_model, growth_model, constrained_model, legacy_approximately_model, legacy_cumulative_model

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

    for factory in (legacy_annual_model, typed_level_model, typed_quarterly_model, growth_model, constrained_model, legacy_approximately_model, legacy_cumulative_model):
        data = factory()
        result = run_forecast(data)
        validate_forecast_output(result, data)
        targets = result['management_target_coverage']['targets']
        row = next(iter(targets[0]['scenario_comparison'].values()))
        rows.append({'case': factory.__name__, 'clean': 'PASS', 'first_row': row})
        for field, value in [('meets_target', int(row['meets_target'])), ('meets_target', 2 if row['meets_target'] else 0), ('meets_target', 'False' if row['meets_target'] else ''), ('modeled_value', 987654321.0), ('attainment_ratio', 998.0)]:
            tamper = copy.deepcopy(result)
            next(iter(tamper['management_target_coverage']['targets'][0]['scenario_comparison'].values()))[field] = value
            tamper = reseal(tamper)
            try:
                validate_forecast_output(tamper, data)
                outcome = 'ACCEPTED'
            except Exception as exc:
                outcome = 'REJECTED: ' + type(exc).__name__ + ': ' + str(exc)
            rows.append({'case': factory.__name__, 'field': field, 'replacement': value, 'outcome': outcome})
    cleaned = sentinel.read_bytes() == b'ROOT independent reviewer sentinel' and sentinel.stat().st_mtime_ns == stamp
after = {p: hashlib.sha256((AUTHOR / p).read_bytes()).hexdigest() for p in paths}
payload = {'reviewer': '/root/du8_rf_root_review', 'reviewed_author_head': '8845bc18', 'source': str(AUTHOR), 'sha256_before': before, 'sha256_after': after, 'unchanged': before == after, 'sentinel_unchanged': cleaned, 'owned_temp_removed': not Path(temp).exists(), 'supplier_calls': 0, 'http_calls': 0, 'results': rows}
(OWNED / ('probe-results.json' if AUTHOR.name == 'revenue-forecast-du8-comparison' else 'probe-final-results.json')).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False, indent=2))
