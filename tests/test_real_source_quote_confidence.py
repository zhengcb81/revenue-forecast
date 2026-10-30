"""Real historical regression; pure native compute, no raw lake or providers."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import socket
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
from revenue_core import run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402

FIXTURES = Path(__file__).parent / 'fixtures' / 'source_quote_confidence'


def _stored(label):
    return json.loads(gzip.decompress((FIXTURES / (label + '-stable-fsum-1.json.gz')).read_bytes()))


def test_historical_real_source_quote_artifacts_keep_their_original_calculation():
    before, after = (_stored(label) for label in ('baseline', 'adopted'))
    for artifact in (before, after):
        assert artifact['confidence']['calculation_version'] == 'stable-fsum/1'
        validate_published_forecast(artifact, artifact['input_document'])
    assert before['confidence']['score'] == 65.38058062293638
    assert after['confidence']['score'] == 65.39469303281442


def test_real_same_source_adoption_cannot_change_current_score_or_economics(tmp_path, monkeypatch):
    monkeypatch.setenv('REVENUE_PUBLICATION_REGISTRY', str(tmp_path / 'publications.jsonl'))
    def deny_network(*args, **kwargs):
        raise AssertionError('native regression cannot call providers or download originals')
    monkeypatch.setattr(socket.socket, 'connect', deny_network)
    outputs = []
    for label in ('baseline', 'adopted'):
        data = deepcopy(_stored(label)['input_document'])
        data['forecast_version'] = 'source-quote-confidence-regression'
        result = run_forecast(data)
        validate_published_forecast(result, data)
        outputs.append(result)
    before, after = outputs
    assert before['confidence'] == after['confidence']
    assert before['consolidated_forecast'] == after['consolidated_forecast']
    changes = []
    for old, new in zip(before['parameter_trace'], after['parameter_trace'], strict=True):
        old, new = deepcopy(old), deepcopy(new)
        old_claims, new_claims = old.pop('claim_ids'), new.pop('claim_ids')
        assert old == new
        if old_claims != new_claims:
            assert new_claims[:-1] == old_claims
            assert new_claims[-1] not in old_claims
            changes.append(old['parameter_id'])
    assert changes == ['equipment_units_base_2026']


@pytest.mark.parametrize("unknown_publication", [False, True])
def test_registered_original_rows_do_not_fabricate_missing_url_or_date(tmp_path, monkeypatch, unknown_publication):
    from fix_hashes import apply_hash_fixes
    from test_recognition_bridge import forecast_document
    from test_source_provenance import AS_OF, local_record
    from revenue_report import render_markdown

    monkeypatch.setenv('REVENUE_PUBLICATION_REGISTRY', str(tmp_path / 'publications.jsonl'))
    source = local_record(unknown=unknown_publication)
    frozen = deepcopy(source)
    def relink(value):
        if isinstance(value, dict):
            return {key: AS_OF.isoformat() if key in {'checked_date', 'verified_date'} else relink(item)
                    for key, item in value.items()}
        if isinstance(value, list):
            return [relink(item) for item in value]
        return source['source_id'] if value == 'filing' else value
    data = relink(forecast_document())
    data['as_of_date'] = AS_OF.isoformat()
    data['sources'] = [source]
    for claim in data['evidence_claims']:
        claim['content_sha256'] = source['capture']['snapshot_sha256']
        claim['capture_receipt_sha256'] = source['capture']['receipt_sha256']
    apply_hash_fixes(data)
    result = run_forecast(data)
    report = render_markdown(result)
    source_table = report.split('## 参数来源', 1)[1]
    assert '](None)' not in source_table
    assert '| ' + source['source_id'] + ' |' in source_table
    assert ('| 未知 |' in source_table) if unknown_publication else source['published_date'] in source_table
    assert source == frozen
    assert result['input_document']['sources'][0]['url'] is None
    assert result['input_document']['sources'][0]['published_date'] == source['published_date']


def test_known_source_http_link_remains_in_markdown():
    from revenue_report import render_markdown
    stored = _stored('baseline')
    source = next(source for source in stored['sources'] if source['url'] is not None)
    report = render_markdown(stored)
    assert '](' + source['url'] + ')' in report
