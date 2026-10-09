"""Public rich-document wire export and transcript byte lineage are distinct."""
import json

import pytest

from company_wiki_narrative_contracts import NarrativeTransportError, validate_narrative_response
from test_company_wiki_narrative_reader import GOLDEN, _resign

PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _wire(mime):
    request = json.loads((GOLDEN / "html-read-request.json").read_bytes())
    bundle = json.loads((GOLDEN / "html-bundle.json").read_bytes())
    receipt = json.loads((GOLDEN / "html-read-receipt.json").read_bytes())
    request["narrative_ref"]["source_ref"]["mime_type"] = mime
    bundle["source_ref"]["mime_type"] = mime
    receipt["manifest"]["mime_type"] = mime
    body, raw = _resign(request, bundle, receipt)
    return request, body, raw


@pytest.mark.parametrize("mime", ["application/pdf", "text/html", "application/xhtml+xml", PPTX])
def test_supported_rich_document_public_export_does_not_need_transcript_lineage(mime):
    request, body, raw = _wire(mime)
    context = validate_narrative_response(request, body, raw).to_dict()
    assert context["source_ref"]["mime_type"] == mime
    assert context["summary"]["status"] == "completed"
    assert context["summary"]["translate"] is False


@pytest.mark.parametrize("mime", ["text/plain", "application/json"])
def test_text_or_json_transcript_cannot_lose_byte_lineage(mime):
    request, body, raw = _wire(mime)
    with pytest.raises(NarrativeTransportError, match="missing_transcript_lineage"):
        validate_narrative_response(request, body, raw)


@pytest.mark.parametrize("mime", ["image/png", "application/octet-stream"])
def test_unrecognized_container_is_not_misclassified_as_a_supported_document(mime):
    request, body, raw = _wire(mime)
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body, raw)
