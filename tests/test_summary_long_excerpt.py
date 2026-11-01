"""Complete, bounded source quotes survive the published-summary RF port."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
from company_wiki_narrative_contracts import SPAN_PREFIX, validate_narrative_response  # noqa: E402
from contracts.evidence import canonical_sha256, text_sha256  # noqa: E402
from fix_hashes import apply_hash_fixes  # noqa: E402
from revenue_core import validate_document  # noqa: E402
from test_company_wiki_narrative_reader import _valid, _resign  # noqa: E402
from test_narrative_summary_usage import PARAMETER, choose, consume  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def long_summary_input(length, prefix='The division provides a documented service. '):
    """Synthetic wire fixture through the real reader/consumer, not a fake proof."""
    request, body, receipt_bytes = _valid()
    bundle, receipt = json.loads(body), json.loads(receipt_bytes)
    span = bundle['evidence_spans'][0]
    suffix = ' Expansion remains a future plan.'
    text = (prefix * length)[:length - len(suffix)] + suffix
    assert len(text) == length and length > 500
    old = span['span_id']
    span['raw_text'] = text
    span['output_sha256'] = canonical_sha256({'raw_text': text, 'structured_value': span['structured_value']})
    new = SPAN_PREFIX + canonical_sha256({'source_id': span['source_id'], 'locator': span['locator'],
        'output_sha256': span['output_sha256']})
    span['span_id'] = new

    def rename(value):
        if isinstance(value, dict):
            return {key: rename(child) for key, child in value.items()}
        if isinstance(value, list):
            return [rename(child) for child in value]
        return new if value == old else value

    bundle = rename(bundle)
    summary = bundle['summary']['draft']['claims'][0]
    summary['text'] = text
    body, receipt_bytes = _resign(request, bundle, receipt)
    context = validate_narrative_response(request, body, receipt_bytes)
    value = context.to_dict()
    data = forecast_document()
    data['as_of_date'] = value['as_of_date']
    data['sources'][0]['capture']['snapshot_sha256'] = value['source_ref']['content_sha256']
    apply_hash_fixes(data)
    binding = {'span_id': new, 'claim_id': 'long_source_adoption', 'parameter_id': PARAMETER,
        'support_type': 'rationale_support'}
    updated, _ = consume(request, context, data, [choose(binding, summary)])
    claim = next(item for item in updated['evidence_claims'] if item['claim_id'] == binding['claim_id'])
    assert claim['excerpt'] == text
    return updated, claim, text


@pytest.mark.parametrize(('length', 'prefix'), [
    (501, 'The division provides a documented service. '),
    (519, 'The division provides a documented service. '),
    (1100, 'The division provides a documented service. '),
    (2048, 'The division provides a documented service. '),
    (519, '核心业务提供研发支持服务。'),
])
def test_complete_long_summary_anchor_validates_without_clipping(length, prefix):
    updated, claim, text = long_summary_input(length, prefix)
    before = deepcopy(updated)
    validate_document(updated)
    assert updated == before
    assert claim['excerpt'] == text
    assert claim['narrative_summary_use']['evidence_spans'][0]['raw_text'] == text
    assert text.endswith(' Expansion remains a future plan.')


@pytest.mark.parametrize('fault', ['no_proof', 'empty_proof', 'foreign_text', 'missing_context'])
def test_long_excerpt_cannot_bypass_complete_provenance_validation(fault):
    updated, claim, _ = long_summary_input(519)
    if fault == 'no_proof':
        claim.pop('narrative_summary_use')
    elif fault == 'empty_proof':
        claim['narrative_summary_use'] = {}
    elif fault == 'foreign_text':
        claim['excerpt'] += ' This is an unsupported additional assertion.'
        claim['excerpt_sha256'] = text_sha256(claim['excerpt'])
    else:
        claim['narrative_summary_use']['evidence_spans'] = []
    expected = {'no_proof': '10-500 characters', 'empty_proof': 'summary_provenance_schema',
        'foreign_text': 'summary_provenance_anchor', 'missing_context': 'summary_provenance_scope'}
    with pytest.raises(ValueError, match=expected[fault]):
        validate_document(updated)


def test_existing_full_proof_byte_bound_still_applies():
    updated, claim, _ = long_summary_input(519)
    from narrative_summary_provenance import MAX_BYTES
    claim['narrative_summary_use']['summary_claim']['text'] = 'x' * MAX_BYTES
    with pytest.raises(ValueError, match='summary_provenance_byte_bound'):
        validate_document(updated)


def test_long_source_anchor_does_not_replace_byte_bound_with_character_count():
    updated, claim, _ = long_summary_input(519)
    from narrative_summary_provenance import MAX_BYTES
    claim['excerpt'] = '界' * (MAX_BYTES // 3 + 1)
    claim['excerpt_sha256'] = text_sha256(claim['excerpt'])
    with pytest.raises(ValueError, match='summary_provenance_excerpt_byte_bound'):
        validate_document(updated)
