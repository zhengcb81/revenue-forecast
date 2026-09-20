"""W05A sample generator (attempt-local, run once, output frozen by hash).

Writes the fixed verified annual-report sample into samples/.  The bytes of
samples/annual_normalized.md are the frozen input for every case that
follows; every expectation in oracle.md is stated against THESE bytes, never
against anything a function under test produced.

Run:
  <iso-venv-python> -X utf8 -B scripts/w05a_make_sample.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"

DOC_ID = "urn:cw:doc:emerald-2025-annual"
SRC_ID = "urn:cw:source:sha256:emerald-2025-annual"
SOURCE_BYTES = "EMERALD-MINING-2025-ANNUAL-REPORT-ORIGINAL-BYTES\n"

# The verified annual text: one definition block, one main-business block and
# one management-discussion block, laid out with the "第X节 <title>" heading
# convention the sample corpus uses.  "## Page N" markers are part of the
# verified text (the PyMuPDF path writes them) and are what the page/span
# association is computed from.
BODY = """\
## Page 1

第一节 释义

在本报告中，除非文义另有所指，下列词语具有如下含义：公司、本公司指翡翠矿业股份有限公司；报告期指2025年1月1日至2025年12月31日。

第二节 公司业务概要

公司主营铜、金、锌等金属的采选与冶炼，兼营贸易业务。2025年矿产铜产量为58.2万吨，矿产金产量为72.4吨。公司坚持"铜金双轮驱动"的经营策略，海外矿山产能持续释放。

第三节 经营情况讨论与分析

2025年公司实现营业收入3,205.6亿元，同比增长12.4%；归属于母公司股东的净利润为428.7亿元，同比增长9.8%。营业成本同比上升11.2%，毛利率较上年提升0.7个百分点。公司预计2026年矿产铜产量将达到62万吨。

第四节 公司治理

公司按照相关法律法规及规范性文件的要求，不断完善公司治理结构，报告期内召开董事会会议12次。
"""


def build_normalized_md() -> str:
    """The exact normalized.md the normalizer would write for this document.

    Shape mirrors normalizer.normalize_catalog: frontmatter + "# <title>" +
    parser body.  The parser body here is the verified text verbatim (the
    PDF parse is a fixture, not a live parser run -- recorded in oracle.md).
    """
    frontmatter = (
        "---\n"
        "artifact_role: normalized\n"
        f"document_id: {DOC_ID}\n"
        f"source_id: {SRC_ID}\n"
        f"source_sha256: {hashlib.sha256(SOURCE_BYTES.encode('utf-8')).hexdigest()}\n"
        "parser_name: sample-parser\n"
        "parser_version: 1.0.0\n"
        "---\n"
    )
    return frontmatter + "# 翡翠矿业2025年年度报告\n\n" + BODY


def main() -> int:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    normalized = build_normalized_md()
    norm_path = SAMPLES / "annual_normalized.md"
    norm_path.write_text(normalized, encoding="utf-8", newline="\n")
    source_path = SAMPLES / "annual_source.txt"
    source_path.write_text(SOURCE_BYTES, encoding="utf-8", newline="\n")

    norm_bytes = norm_path.read_bytes()
    body_bytes = BODY.encode("utf-8")
    record = {
        "document_id": DOC_ID,
        "source_id": SRC_ID,
        "title": "翡翠矿业2025年年度报告",
        "document_kind": "annual_report",
        "published_date": "2026-03-28",
        "normalized_path": str(norm_path),
        "normalized_sha256": hashlib.sha256(norm_bytes).hexdigest(),
        "normalized_byte_size": len(norm_bytes),
        "normalized_char_count": len(normalized),
        "body_char_count": len(BODY),
        "body_sha256": hashlib.sha256(body_bytes).hexdigest(),
        # bytes before the body starts = frontmatter + "# title\n\n"
        "frontmatter_and_title_bytes": len(norm_bytes) - len(body_bytes),
        "expected_section_titles": [
            "公司业务概要",
            "经营情况讨论与分析",
            "公司治理",
        ],
        "expected_headings_present": [
            "第一节 释义",
            "第二节 公司业务概要",
            "第三节 经营情况讨论与分析",
            "第四节 公司治理",
        ],
        "page_markers": [1],
        "source_path": str(source_path),
        "source_sha256": hashlib.sha256(SOURCE_BYTES.encode("utf-8")).hexdigest(),
        "source_byte_size": len(SOURCE_BYTES.encode("utf-8")),
    }
    (SAMPLES / "sample.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "normalized_sha256": record["normalized_sha256"],
        "normalized_byte_size": record["normalized_byte_size"],
        "body_char_count": record["body_char_count"],
        "source_sha256": record["source_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
