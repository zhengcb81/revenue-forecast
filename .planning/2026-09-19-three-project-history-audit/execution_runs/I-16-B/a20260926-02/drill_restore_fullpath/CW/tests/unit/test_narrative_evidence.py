from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from scripts.narrative_evidence_pilot import _anchor_evidence_ids

from company_wiki.source_catalog.narrative_evidence import (
    NarrativeParseResult,
    SourceSummaryDraft,
    SummaryClaim,
    SummaryValidationError,
    classify_document_kind,
    _make_unit,
    _sentence_fragments,
    _table_scan_signal,
    parse_pdf,
    parse_transcript_text,
    select_narrative_evidence,
    validate_summary_draft,
    verify_pdf_evidence_spans,
    verify_transcript_evidence_spans,
)
from company_wiki.source_contract import EvidenceCoordinates, source_id_for_sha256


def _source(seed: str = "source") -> tuple[str, str]:
    sha = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return source_id_for_sha256(sha), sha


def _unit(
    text: str,
    *,
    source_id: str,
    coords: EvidenceCoordinates | None = None,
    kind: str = "pdf_text_block",
    role: str = "company_filing",
    metadata: dict | None = None,
):
    return _make_unit(
        source_id=source_id,
        parser_version="0.1.0",
        coordinates=coords or EvidenceCoordinates(page_number=1, paragraph_index=0),
        raw_text=text,
        unit_kind=kind,
        source_role=role,
        language="zh",
        metadata=metadata or {},
    )


def test_pilot_anchor_mapping_returns_only_supporting_span_window() -> None:
    source_id, _source_sha = _source()
    first = _unit(
        "订单交付进入新阶段，航空产业",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=1),
    ).to_evidence_span(topics=(), selection_reasons=())
    second = _unit(
        "形成的外协需求旺盛。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=2),
    ).to_evidence_span(topics=(), selection_reasons=())
    unrelated = _unit(
        "无关的表述。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=3),
    ).to_evidence_span(topics=(), selection_reasons=())

    assert _anchor_evidence_ids([first, unrelated], "订单交付") == (first.span_id,)
    assert _anchor_evidence_ids([first, second, unrelated], "航空产业形成") == (
        first.span_id,
        second.span_id,
    )
    assert _anchor_evidence_ids([unrelated], "订单交付") == ()


def test_pdf_parser_keeps_text_with_a_page_locator(tmp_path: Path) -> None:
    fitz = pytest.importorskip("fitz")
    path = tmp_path / "one-page.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Company launched a new product and expanded overseas capacity for a repeat customer order.",
    )
    document.save(path)
    document.close()

    actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    source_id = source_id_for_sha256(actual_sha)
    parsed = parse_pdf(
        path,
        source_id=source_id,
        source_sha256=actual_sha,
        language="en",
    )
    package = select_narrative_evidence(parsed, title="样本年报.pdf", existing_kind="annual_report")

    assert parsed.page_count == parsed.pages_read == 1
    assert parsed.coverage_complete
    assert any(unit.unit_kind == "pdf_text_block" for unit in parsed.units)
    assert package.evidence_spans
    span = package.evidence_spans[0]
    assert span.coordinates.page_number == 1
    assert span.coordinates.paragraph_index == 0
    assert span.source_id == source_id
    verified, failed = verify_pdf_evidence_spans(
        path,
        source_id=source_id,
        source_sha256=actual_sha,
        evidence_spans=package.evidence_spans,
    )
    assert verified == (span.span_id,)
    assert failed == ()


def test_financial_table_rows_are_dropped_but_business_rows_are_selected() -> None:
    source_id, source_sha = _source()
    financial = _unit(
        "营业收入 | 100.0亿元",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=2, table_index=0, row_index=1),
        kind="pdf_table_row",
        metadata={"row_cells": ("营业收入", "100.0亿元"), "table_headers": ("项目", "本期发生额")},
    )
    business = _unit(
        "海外市场的新产线已完成调试，预计第四季度投产并服务新增客户。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=2, table_index=1, row_index=2),
        kind="pdf_table_row",
        metadata={"row_cells": ("海外市场", "新产线已完成调试"), "table_headers": ("项目", "进展")},
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(financial, business),
        page_count=3,
        pages_read=3,
    )

    package = select_narrative_evidence(parsed, title="可转债募集说明书.pdf")

    assert package.document_kind == "convertible_bond_prospectus"
    assert package.dropped_financial_count == 1
    assert len(package.evidence_spans) == 1
    assert package.evidence_spans[0].coordinates.table_index == 1
    assert package.evidence_spans[0].coordinates.row_index == 2


def test_incomplete_scan_never_auto_skips_as_no_narrative() -> None:
    source_id, source_sha = _source()
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(),
        page_count=7,
        pages_read=7,
        opaque_pages=(4,),
    )
    package = select_narrative_evidence(parsed, title="投资者关系管理办法.pdf")
    assert package.status == "needs_review"
    assert not package.coverage_complete


def test_complete_known_notice_can_be_skipped_without_saving_evidence() -> None:
    source_id, source_sha = _source()
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(),
        page_count=3,
        pages_read=3,
    )
    package = select_narrative_evidence(
        parsed,
        title="关于召开年度业绩说明会的通知.pdf",
    )
    assert package.status == "skipped_no_narrative"
    assert package.evidence_spans == ()


def test_semiannual_title_is_not_misclassified_as_annual() -> None:
    assert classify_document_kind("中微公司：2025年半年度报告.pdf") == "semi_annual_report"


def test_transcript_parser_excludes_editorial_and_keeps_qa_question_context() -> None:
    source_id, source_sha = _source()
    text = (
        "Editorial summary: new product demand is rising.\n\n"
        "Full Conference Call Transcript\n"
        "CEO: We launched a new product and expanded overseas capacity.\n\n"
        "Questions & Answers\n"
        "Analyst: Is the new product ready for commercial launch?\n\n"
        "CEO: It is too early to speculate on commercial launch, though customer validation continues.\n"
    )
    parsed = parse_transcript_text(text, source_id=source_id, source_sha256=source_sha)
    package = select_narrative_evidence(parsed, title="MSFT_Q4_2026_earnings_call.txt")

    assert parsed.coverage_complete
    assert all("Editorial summary" not in unit.raw_text for unit in parsed.units)
    assert len(package.evidence_spans) >= 3
    roles = [span.structured_value["source_role"] for span in package.evidence_spans]
    assert "management" in roles
    assert "analyst" in roles  # context, never management attribution
    assert any("too early to speculate" in (span.raw_text or "") for span in package.evidence_spans)
    assert all(span.parser_version == "0.1.0" for span in package.evidence_spans)
    verified, failed = verify_transcript_evidence_spans(
        text,
        source_id=source_id,
        source_sha256=source_sha,
        evidence_spans=package.evidence_spans,
    )
    assert len(verified) == len(package.evidence_spans)
    assert failed == ()


def test_transcript_q_and_a_transition_and_two_question_links_are_preserved() -> None:
    source_id, source_sha = _source()
    text = (
        "Full Conference Call Transcript\n"
        "CEO: Welcome to the call.\n"
        "Operator: We will now take questions.\n"
        "CEO: We will now move over to Q&A.\n"
        "Karl Keirstead: First, how does model choice work? And second question, "
        "how should we think about the clinical trial?\n"
        "CEO: On the first question, starter doses are now shipping through the supply chain.\n"
        "CEO: On the second question, it is too early to speculate about the clinical trial results.\n"
    )

    parsed = parse_transcript_text(text, source_id=source_id, source_sha256=source_sha)
    questions = [unit for unit in parsed.units if unit.source_role == "analyst"]
    package = select_narrative_evidence(parsed, title="MSFT_Q4_2026_earnings_call.txt")
    selected_questions = [
        span for span in package.evidence_spans
        if span.structured_value["source_role"] == "analyst"
    ]

    assert len(questions) == 2
    assert questions[0].metadata["qa_group_id"] != questions[1].metadata["qa_group_id"]
    assert {span.structured_value["qa_group_id"] for span in selected_questions} == {
        questions[0].metadata["qa_group_id"], questions[1].metadata["qa_group_id"]
    }
    assert any("starter doses" in (span.raw_text or "") for span in package.evidence_spans)
    assert any("too early to speculate" in (span.raw_text or "") for span in package.evidence_spans)


def test_transcript_without_recognized_start_is_blocked_not_skipped() -> None:
    source_id, source_sha = _source()
    parsed = parse_transcript_text(
        "This editorial page discusses new products and demand.",
        source_id=source_id,
        source_sha256=source_sha,
    )
    package = select_narrative_evidence(parsed, title="unknown.txt")
    assert package.status == "blocked"
    assert parsed.errors == ("transcript_start_missing",)


def test_summary_draft_requires_real_evidence_ids_and_preserves_source_language() -> None:
    source_id, source_sha = _source()
    unit = _unit(
        "公司新产品已通过客户验证并获得重复订单。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(unit,),
        page_count=1,
        pages_read=1,
    )
    package = select_narrative_evidence(parsed, title="年报.pdf")
    span = package.evidence_spans[0]
    draft = SourceSummaryDraft(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        claims=(
            SummaryClaim(
                claim_id="claim-1",
                text="新产品通过客户验证并获得重复订单。",
                evidence_ids=(span.span_id,),
                claim_type="company_statement",
                modality="actual",
            ),
        ),
    )
    validate_summary_draft(
        draft,
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        evidence_spans=package.evidence_spans,
    )
    assert package.summary_input()["summary_scope"] == "selected_evidence_only"
    assert "full_document" not in package.summary_input()
    compact_evidence = package.summary_input()["evidence"][0]
    assert compact_evidence["evidence_id"] == span.span_id
    assert compact_evidence["raw_text"] == span.raw_text
    assert "structured_value" not in compact_evidence

    translated = SourceSummaryDraft(
        source_id=source_id,
        source_sha256=source_sha,
        language="en",
        claims=draft.claims,
    )
    with pytest.raises(SummaryValidationError, match="language"):
        validate_summary_draft(
            translated,
            source_id=source_id,
            source_sha256=source_sha,
            language="zh",
            evidence_spans=package.evidence_spans,
        )


def test_analyst_question_cannot_be_used_as_company_fact() -> None:
    source_id, source_sha = _source()
    question = _unit(
        "Did the company complete overseas customer qualification for its new product?",
        source_id=source_id,
        coords=EvidenceCoordinates(paragraph_index=15),
        kind="transcript_speaker_block",
        role="analyst",
        metadata={"qa_group_id": 1},
    )
    answer = _unit(
        "It is too early to speculate on the launch; customer validation continues.",
        source_id=source_id,
        coords=EvidenceCoordinates(paragraph_index=16),
        kind="transcript_speaker_block",
        role="management",
        metadata={"qa_group_id": 1},
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="en",
        units=(question, answer),
        line_count=18,
    )
    package = select_narrative_evidence(parsed, title="call transcript.txt")
    question_span = next(
        span for span in package.evidence_spans
        if span.structured_value["source_role"] == "analyst"
    )
    draft = SourceSummaryDraft(
        source_id=source_id,
        source_sha256=source_sha,
        language="en",
        claims=(
            SummaryClaim(
                claim_id="claim-1",
                text="The company completed qualification.",
                evidence_ids=(question_span.span_id,),
                claim_type="company_statement",
                modality="actual",
            ),
        ),
    )
    with pytest.raises(SummaryValidationError, match="non-company"):
        validate_summary_draft(
            draft,
            source_id=source_id,
            source_sha256=source_sha,
            language="en",
            evidence_spans=package.evidence_spans,
        )


def test_static_topic_mentions_are_not_selected_without_a_change_or_current_event() -> None:
    source_id, source_sha = _source()
    static = _unit(
        "公司主营业务包括高端装备研发、生产和销售，持续关注行业发展。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(static,),
        page_count=1,
        pages_read=1,
    )

    package = select_narrative_evidence(parsed, title="年报.pdf")

    assert package.evidence_spans == ()
    assert package.status == "needs_review"


def test_future_market_coverage_plan_is_selected_as_a_plan() -> None:
    source_id, source_sha = _source()
    unit = _unit(
        "预计未来五到十年，公司将通过自主研发和行业合作覆盖集成电路关键设备市场超过60%。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(unit,),
        page_count=1,
        pages_read=1,
    )

    package = select_narrative_evidence(parsed, title="半年报.pdf")

    assert len(package.evidence_spans) == 1
    assert "project_plan_or_status" in package.evidence_spans[0].structured_value["selection_reasons"]


def test_adjacent_product_context_is_retained_for_a_validation_event() -> None:
    source_id, source_sha = _source()
    subject = _unit(
        "四款MOCVD新产品包括用于功率器件、Micro-LED和红黄光LED的设备。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=3, paragraph_index=24),
    )
    event = _unit(
        "其中GaAs MOCVD设备已进入客户端验证阶段，部分获得批量订货。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=3, paragraph_index=25),
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(subject, event),
        page_count=15,
        pages_read=15,
    )

    package = select_narrative_evidence(parsed, title="一季报.pdf")

    assert {span.coordinates.paragraph_index for span in package.evidence_spans} == {24, 25}
    assert any(
        "adjacent_subject_context" in span.structured_value["selection_reasons"]
        for span in package.evidence_spans
    )


def test_pdf_block_sentences_are_split_before_topic_matching() -> None:
    fragments = _sentence_fragments(
        "与公司签订《劳动合同》的董事、监事及核心技术人员从本公司领取薪酬。"
        "公司推出新产品并获得海外客户订单。"
    )

    assert [fragment[2] for fragment in fragments] == [
        "与公司签订《劳动合同》的董事、监事及核心技术人员从本公司领取薪酬。",
        "公司推出新产品并获得海外客户订单。",
    ]


def test_order_production_definition_is_not_mistaken_for_a_recent_order() -> None:
    source_id, source_sha = _source()
    definition = _unit(
        "订单式生产是指公司在与客户签订订单后，根据订单情况安排生产。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(definition,),
        page_count=1,
        pages_read=1,
    )

    package = select_narrative_evidence(parsed, title="招股说明书.pdf")

    assert package.evidence_spans == ()


def test_specific_cooperation_event_does_not_require_a_predeclared_topic_word() -> None:
    source_id, source_sha = _source()
    event = _unit(
        "公司已与合作方签署项目合作意向书。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(event,),
        page_count=1,
        pages_read=1,
    )

    package = select_narrative_evidence(parsed, title="投资者关系活动记录.pdf")

    assert len(package.evidence_spans) == 1
    assert package.evidence_spans[0].structured_value["topics"] == ("new_business",)
    assert "specific_business_event" in package.evidence_spans[0].structured_value[
        "selection_reasons"
    ]


def test_pilot_line_milestone_is_classified_as_operational_evidence() -> None:
    source_id, source_sha = _source()
    event = _unit(
        "硫化锂中试线建设工作正在按计划推进，预计6月底完成建设并开展中试工作。",
        source_id=source_id,
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(event,),
        page_count=1,
        pages_read=1,
    )

    package = select_narrative_evidence(parsed, title="投资者关系活动记录.pdf")

    assert len(package.evidence_spans) == 1
    assert "capacity_projects" in package.evidence_spans[0].structured_value["topics"]
    assert package.status == "selected"


def test_table_scan_signal_requires_a_specific_event_or_current_industry_context() -> None:
    assert not _table_scan_signal("市场需求持续增长，公司研发项目较多。")
    assert _table_scan_signal("2025年新产线已完成客户验证并进入量产。")
    assert _table_scan_signal("本报告期行业竞争格局和政策变化明显。")
    assert _table_scan_signal("问：新产品什么时候量产？答：已通过客户验证。")


def test_pdf_investor_question_is_selected_only_as_context_for_a_selected_answer() -> None:
    source_id, source_sha = _source()
    question = _unit(
        "问：新产品什么时候通过客户验证？",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=5, table_index=0, row_index=0, column_index=1),
        kind="pdf_table_qa_fragment",
        role="investor_question",
        metadata={"qa_group_id": "p5:t0:r0:c1:q1", "qa_state": "question_paired"},
    )
    answer = _unit(
        "答：新产品已通过客户验证并取得首批订单。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=5, table_index=0, row_index=0, column_index=1),
        kind="pdf_table_qa_fragment",
        role="management",
        metadata={"qa_group_id": "p5:t0:r0:c1:q1", "qa_state": "answer_paired"},
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(question, answer),
        page_count=5,
        pages_read=5,
    )

    package = select_narrative_evidence(parsed, title="投资者关系活动记录.pdf")

    roles = [span.structured_value["source_role"] for span in package.evidence_spans]
    assert roles == ["investor_question", "management"]
    assert package.status == "selected"


def test_financing_project_heading_selects_and_groups_split_paragraph_context() -> None:
    source_id, source_sha = _source()
    heading = _unit(
        "2、项目建设的必要性",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=0),
        metadata={"pdf_block": 1, "bbox": (100.0, 70.0, 280.0, 84.0)},
    )
    first_line = _unit(
        "本项目以延伸锻件产业链、拓展航空零部件精密加工业务为目标，",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=1),
        metadata={"pdf_block": 2, "bbox": (100.0, 105.0, 480.0, 118.0)},
    )
    second_line = _unit(
        "并向下游装配延伸，逐步实现零件交付。",
        source_id=source_id,
        coords=EvidenceCoordinates(page_number=101, paragraph_index=2),
        metadata={"pdf_block": 3, "bbox": (90.0, 129.0, 480.0, 142.0)},
    )
    parsed = NarrativeParseResult(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        units=(heading, first_line, second_line),
        page_count=101,
        pages_read=101,
    )

    package = select_narrative_evidence(
        parsed,
        title="西安三角防务向特定对象发行股票募集说明书.pdf",
    )

    assert [span.raw_text for span in package.evidence_spans] == [
        first_line.raw_text,
        second_line.raw_text,
    ]
    group_ids = {
        span.structured_value["selection_group_id"] for span in package.evidence_spans
    }
    assert len(group_ids) == 1
    summary_group = package.summary_input()["evidence"][0]
    assert summary_group["context_member_count"] == 2
    assert summary_group["evidence_ids"] == [span.span_id for span in package.evidence_spans]
    assert summary_group["raw_text"] == first_line.raw_text + second_line.raw_text
    assert len(summary_group["locators"]) == 2


def test_company_statement_rejects_unknown_roles_and_unstable_locators_need_review() -> None:
    source_id, source_sha = _source()
    # Rebuild an unstable EvidenceSpan through the normal unit constructor.
    unstable_unit = _make_unit(
        source_id=source_id,
        parser_version="0.1.0",
        coordinates=EvidenceCoordinates(page_number=1, table_index=0, row_index=0, column_index=1),
        raw_text="新产品已通过客户验证并获得订单。",
        unit_kind="pdf_table_qa_fragment",
        source_role="company_filing",
        language="zh",
        metadata={"cell_fragment_sha256": "test"},
        quality_flags=("locator_unstable",),
    ).to_evidence_span(topics=("new_business",), selection_reasons=("test",))
    draft = SourceSummaryDraft(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        claims=(
            SummaryClaim(
                claim_id="claim-1",
                text="新产品已通过验证。",
                evidence_ids=(unstable_unit.span_id,),
                claim_type="company_statement",
                modality="actual",
            ),
        ),
    )

    with pytest.raises(SummaryValidationError, match="unstable evidence locators"):
        validate_summary_draft(
            draft,
            source_id=source_id,
            source_sha256=source_sha,
            language="zh",
            evidence_spans=(unstable_unit,),
        )

    unknown_unit = _make_unit(
        source_id=source_id,
        parser_version="0.1.0",
        coordinates=EvidenceCoordinates(page_number=1, paragraph_index=2),
        raw_text="新产品已通过客户验证并获得订单。",
        unit_kind="pdf_text_block",
        source_role="unknown",
        language="zh",
        metadata={},
    ).to_evidence_span(topics=("new_business",), selection_reasons=("test",))
    ordinary_draft = SourceSummaryDraft(
        source_id=source_id,
        source_sha256=source_sha,
        language="zh",
        claims=(
            SummaryClaim(
                claim_id="claim-2",
                text="新产品已通过验证。",
                evidence_ids=(unknown_unit.span_id,),
                claim_type="company_statement",
                modality="actual",
            ),
        ),
    )
    with pytest.raises(SummaryValidationError, match="non-company evidence"):
        validate_summary_draft(
            ordinary_draft,
            source_id=source_id,
            source_sha256=source_sha,
            language="zh",
            evidence_spans=(unknown_unit,),
        )
