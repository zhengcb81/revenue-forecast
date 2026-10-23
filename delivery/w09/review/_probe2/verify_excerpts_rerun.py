"""Verify and normalise the proposed claim excerpts against the verified page text.

The preparation package proposed 47 excerpts. This module re-reads every
proposal from the *page inventory bytes*, recomputes the offset/hash, and splits
the one proposal that exceeds the native 500-character claim limit into two
contiguous source-owned spans. Nothing is trusted from the proposal's own
PASS flags.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
PAGES = RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json"
ADDENDUM = (RUN / "execution_replays/r1-remediation-02/phase_b/research"
            / "source-page-addendum-20261023.json")
BINDINGS = (RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation"
            / "claim-scope-bindings.json")
OUT = Path(r"C:\\Users\\郑曾波\\Projects\\revenue-forecast-r1-research\\delivery\\w09\\review\\_probe2\\excerpts_rerun.json")

H1 = "urn:company-wiki:source:sha256:d0dba19ede6e35ae3e127a1da91a42f04262e90d14efeb847bdfbff9b6354a5f"
ANNUAL = "urn:company-wiki:source:sha256:7f1431d66eae399d4b35639bb650e23287c7f52dacbb47b4b4a197fb5026d6a2"

# Explicit split for the one over-length proposal: the chemistry operating span
# is cut at the D&M ii. paragraph boundary so each part stays a contiguous
# source-owned range with its own business context.
CHEM_SPLIT_AT = "i.\n小分子CDMO 管线持续扩张。"


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def raw_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    pages = json.loads(PAGES.read_text(encoding="utf-8"))
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    proposals = json.loads(BINDINGS.read_text(encoding="utf-8"))["excerpts"]
    index = {}
    for source in list(pages["sources"]) + list(addendum["sources"]):
        for page in source["pages"]:
            index[(source["source_ref"]["source_id"], page["pdf_page"])] = page

    rows = {}
    for excerpt_id, proposal in proposals.items():
        source_id = proposal["source_id"]
        page = index[(source_id, proposal["pdf_page"])]
        text = page["text"]
        start, end = proposal["start_char_inclusive"], proposal["end_char_exclusive"]
        span = text[start:end]
        assert span == proposal["excerpt"], f"offset mismatch for {excerpt_id}"
        # The proposal records the raw contiguous-range hash; the native claim
        # field hashes the stripped text. Verify both identities explicitly.
        assert raw_sha256(span) == proposal["excerpt_sha256"], f"raw hash mismatch {excerpt_id}"
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == proposal["page_text_sha256"], \
            f"page text hash mismatch {excerpt_id}"
        rows[excerpt_id] = {
            "excerpt_id": excerpt_id,
            "source_id": source_id,
            "pdf_page": proposal["pdf_page"],
            "page_text_sha256": proposal["page_text_sha256"],
            "start_char_inclusive": start,
            "end_char_exclusive": end,
            "offset_basis": "Python Unicode code points on the verified page text",
            "excerpt": span,
            "contiguous_range_sha256": raw_sha256(span),
            "excerpt_sha256": text_sha256(span),
            "period": proposal.get("period"),
            "semantic_scope": proposal.get("semantic_scope"),
            "contiguous": True,
        }

    # Split the over-length chemistry span into two contiguous native-legal parts.
    # The boundary falls at the end of the D&M intro sentence (…业务保持\n强劲增长。),
    # so part 1 carries the Chemistry overview (total, capacity, R conversion, D&M
    # intro) and part 2 the small-molecule D&M pipeline detail and +72.7% actual.
    chem = rows["chemistry_non_tides_operating"]
    body = chem["excerpt"]
    marker_at = body.index(CHEM_SPLIT_AT)
    first = body[:marker_at]
    second = body[marker_at:]
    base_start = chem["start_char_inclusive"]
    # Parent-level keys only; each part recomputes its OWN contiguous-range hash
    # (a span's contiguous hash must be the hash of THAT span's raw bytes, not of
    # the parent it was split from — a defect found in round-1 review).
    parent_keys = {k: v for k, v in chem.items()
                   if k not in {"excerpt", "excerpt_sha256", "contiguous_range_sha256",
                                "start_char_inclusive", "end_char_exclusive",
                                "contiguous", "period", "semantic_scope"}}
    rows["chemistry_dm_operating"] = {
        **parent_keys,
        "excerpt_id": "chemistry_dm_operating",
        "start_char_inclusive": base_start,
        "end_char_exclusive": base_start + marker_at,
        "excerpt": first,
        "contiguous_range_sha256": raw_sha256(first),
        "excerpt_sha256": text_sha256(first),
        "period": "H1 FY2026",
        "semantic_scope": ("Chemistry operating overview: Chemistry revenue +53.3% with pipeline "
                           "progression and capacity ramp, R-to-D conversion of 155 molecules, and "
                           "the small-molecule D&M 'keeps growing strongly' intro. Own-scope support "
                           "for the non-TIDES aggregate's activity mechanism; no measured future "
                           "workload or price."),
        "contiguous": True,
    }
    rows["chemistry_r_operating"] = {
        **parent_keys,
        "excerpt_id": "chemistry_r_operating",
        "start_char_inclusive": base_start + marker_at,
        "end_char_exclusive": base_start + len(body),
        "excerpt": second,
        "contiguous_range_sha256": raw_sha256(second),
        "excerpt_sha256": text_sha256(second),
        "period": "H1 FY2026",
        "semantic_scope": ("Small-molecule D&M mechanism detail: pipeline +699 molecules, 3,731 total "
                           "with stage stock, and reported D&M revenue 149.9亿元 +72.7% (an H1 actual, "
                           "not a future rate). Own-scope support for the non-TIDES aggregate; no "
                           "future magnitude is established."),
        "contiguous": True,
    }
    rows["chemistry_non_tides_operating"]["split_into"] = ["chemistry_dm_operating", "chemistry_r_operating"]
    rows["chemistry_non_tides_operating"]["note"] = (
        "593 characters exceed the native 500-character claim limit; the two derived spans above are "
        "contiguous, source-owned and together cover the identical bytes. The boundary falls at the "
        "end of the D&M intro sentence, so part 1 is the Chemistry overview and part 2 the D&M "
        "pipeline detail; both are inside the same Chemistry operating section.")
    del rows["chemistry_non_tides_operating"]["excerpt"]
    del rows["chemistry_non_tides_operating"]["excerpt_sha256"]

    # Self-check: every recorded contiguous-range hash must equal the hash of that
    # span's raw slice re-read from the page (round-1 review found the two split
    # spans initially inherited the parent's hash; this guard makes that class of
    # defect fail loudly instead of silently).
    for excerpt_id, row in rows.items():
        if "excerpt" not in row or "contiguous_range_sha256" not in row:
            continue
        page_text = index[(row["source_id"], row["pdf_page"])]["text"]
        raw_slice = page_text[row["start_char_inclusive"]:row["end_char_exclusive"]]
        assert raw_sha256(raw_slice) == row["contiguous_range_sha256"], \
            f"contiguous_range_sha256 mismatch for {excerpt_id}"
        assert raw_slice == row["excerpt"], f"span/excerpt mismatch for {excerpt_id}"
        assert 10 <= len(row["excerpt"].strip()) <= 500, f"length out of range for {excerpt_id}"

    # Testing business's own section on H1 p12 sits between the TIDES/Testing
    # boundary and the Biology heading. The sealed input cited the page-top
    # slice (which starts with TIDES) for Testing claims; this is the same
    # wrong-scope defect class, so the own-scope range is recorded here too.
    h1_p12 = index[(H1, 12)]["text"]
    testing_start = h1_p12.index("（2）")
    testing_end = h1_p12.index("（3）")
    testing_span = h1_p12[testing_start:testing_end]
    assert 10 <= len(testing_span.strip()) <= 500, len(testing_span)
    rows["testing_h1_own"] = {
        "excerpt_id": "testing_h1_own",
        "source_id": H1,
        "pdf_page": 12,
        "page_text_sha256": index[(H1, 12)]["text_sha256"],
        "start_char_inclusive": testing_start,
        "end_char_exclusive": testing_end,
        "offset_basis": "Python Unicode code points on the verified page text",
        "excerpt": testing_span,
        "contiguous_range_sha256": raw_sha256(testing_span),
        "excerpt_sha256": text_sha256(testing_span),
        "period": "H1 FY2026",
        "semantic_scope": ("Testing business's own operating section: revenue +31.5%, safety-assessment +42.8%, "
                           "new-modality share >35%, DMPK automation, site inspections. Direction and "
                           "activity drivers only; no future revenue or price magnitude."),
        "contiguous": True,
    }

    over = {k: len(v["excerpt"]) for k, v in rows.items() if "excerpt" in v and len(v["excerpt"]) > 500}
    short = {k: len(v["excerpt"]) for k, v in rows.items() if "excerpt" in v and len(v["excerpt"].strip()) < 10}
    record = {
        "schema_version": "w09-verified-excerpts/1",
        "purpose": ("Independently re-read every proposed excerpt from the verified page bytes, recompute "
                    "the contiguous offset and the native excerpt hash, and record the one split needed to "
                    "stay inside the native 500-character limit. NOTE on counts: the count_* fields below "
                    "count UNIQUE EXCERPT TEMPLATES (contiguous source ranges), NOT claims (49 in the "
                    "review union) and NOT per-claim excerpt proposals (47 in the preparation package); "
                    "several distinct claims legitimately share one excerpt template, and one template was "
                    "split into two."),
        "source_pages_sha256": hashlib.sha256(PAGES.read_bytes()).hexdigest(),
        "proposal_sha256": hashlib.sha256(BINDINGS.read_bytes()).hexdigest(),
        "count_excerpt_templates_proposals": len(proposals),
        "count_excerpt_templates_verified": len([r for r in rows.values() if "excerpt" in r]),
        "count_proposals": len(proposals),
        "count_verified": len([r for r in rows.values() if "excerpt" in r]),
        "count_claims_in_review_union": 49,
        "count_preparation_excerpt_proposals": 47,
        "over_500": over,
        "under_10": short,
        "excerpts": rows,
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"verified": record["count_verified"], "over_500": over, "under_10": short},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
