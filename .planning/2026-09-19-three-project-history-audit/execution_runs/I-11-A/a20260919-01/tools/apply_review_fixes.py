"""I-11-A: apply the post-review corrections that are safer to do programmatically.

Rewrites (never silently drops) documented fields:
  P2-6  the copper-equivalent sensitivity wording in H-CN-ZIJIN-SEG-02:
        the delta is a TWO-POINT DIFFERENCE over a denominator change of +83,161
        tonnes, not a partial derivative.
  P1-3  the HK-XIAOMI-AR2025 unreadability reason in source_map.json, with the
        measured facts from tools/probe_xiaomi.py.

Usage: python -X utf8 -B tools/apply_review_fixes.py <attempt_root>
"""

from __future__ import annotations

import json
import os
import sys

NEW_FORMULA = (
    "隐含单位实现收入 = 分部对外收入 ÷ 铜当量销售量；FY2025 用精确有理数复算："
    "109,977,556,345 ÷ (884,943 + 83,161 × 24) = 109977556345/885141 ≈ 124,248.63 元/吨铜当量。"
    "口径暴露一：公司未披露铜当量换算系数，本式假定 1 千克金 = 24 吨铜当量（示意值，不是披露值）。"
    "敏感性表述（review 发现 P2-6 后改写）：金→铜当量系数每 +1 吨/千克 ⇒ 当量分母 +83,161 吨"
    "（885,141 → 968,302）⇒ 单位收入由 124,248.63 降到 113,577.74，即 −10,670.89 元/吨铜当量。"
    "这是**两点差分**，不是偏导数：分母单独 +1 吨的效应仅约 0.14 元/吨（−T/V²），两者不可混用。"
    "结论对该假设高度敏感，故整条式的可用性进入 STOP_DISCLOSURE_ADAPTATION，须由会计/行业 reviewer "
    "裁定系数来源后才可用于幅度校准。口径暴露二：该单位收入含金/银/锌等全部矿产品，"
    "不能当作铜价使用（原文 1 千克金 = 24 吨铜当量的系数同样无披露依据）"
)

NEW_REASON = (
    "classic page objects CAN be enumerated: tools/probe_xiaomi.py finds 415 classic /Type /Page "
    "objects (the raw byte scan reports 420 occurrences of /Type /Page, the difference being the "
    "/Pages tree node), so object enumeration is not the blocker. The first 30 pages expose 30 "
    "decodable /Contents streams (0 missing) containing 3,264 literal and 2,756 hex strings, yet "
    "Page.fragments() returns 0 characters for every sampled page; across the whole file only 1 of 5 "
    "classic font objects carries a /ToUnicode reference (the single raw-byte /ToUnicode occurrence) "
    "and 4 decoded CMap streams contain bfchar/bfrange blocks, none of which this reader can reach "
    "from the page content streams because the working fonts are embedded subsets whose glyph codes "
    "are not mapped. The independent pdftotext (P2) path exits 0 and emits Adobe-CNS1 mojibake: the "
    "archived output of pages 1-12 (evidence/I-11-A/extract/P2_xiaomi_probe.txt, 12,145 bytes) "
    "contains none of the strings 小米 / 收入 / 年度報告. The reviewer additionally ran pdftotext over "
    "the whole file and reported a 998,598-byte mojibake output; that full-file run was NOT archived "
    "here and is carried as review-reported evidence only. Per oracle O-7 the source is therefore "
    "marked not_readable_in_this_attempt and no value from it is cited."
)


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")

    h_path = os.path.join(ev, "hypotheses.json")
    hs = json.load(open(h_path, encoding="utf-8"))
    changed = []
    for h in hs:
        if h["hypothesis_id"] == "H-CN-ZIJIN-SEG-02":
            h["parameter_mapping"]["conversion_formula"] = NEW_FORMULA
            changed.append(h["hypothesis_id"] + ":conversion_formula")
    with open(h_path, "w", encoding="utf-8") as fh:
        json.dump(hs, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    sm_path = os.path.join(ev, "source_map.json")
    sm = json.load(open(sm_path, encoding="utf-8"))
    for entry in sm.get("not_readable_in_this_attempt", []):
        if entry.get("doc_id") == "HK-XIAOMI-AR2025":
            entry["reason"] = NEW_REASON
            entry["measured_facts"] = {
                "classic_page_objects_found": 415,
                "raw_occurrences_of_type_page": 420,
                "objstm_occurrences": 423,
                "classic_font_objects": 5,
                "classic_fonts_with_tounicode_reference": 1,
                "decoded_cmap_streams_with_bf_blocks": 4,
                "sampled_pages": 30,
                "contents_streams_decoded": 30,
                "contents_streams_missing": 0,
                "contents_literal_strings": 3264,
                "contents_hex_strings": 2756,
                "page_sample_characters": 0,
                "pdftotext_exit_code": 0,
                "pdftotext_output_bytes_archived_pages_1_12": 12145,
                "pdftotext_output_bytes_full_file_review_reported": 998598,
                "pdftotext_encoding_failure": "Adobe-CNS1 mojibake",
                "probe": "evidence/I-11-A/extract/P1_xiaomi_content_probe.json",
            }
            entry["correction_note"] = (
                "review finding P1-3: the first version of this reason said '423 /ObjStm, 0 classic "
                "page objects' and binding.json said '352 -> 0'; 352 is the Zijin page count. The "
                "reason was rewritten from the measurements in tools/probe_xiaomi.py; the conclusion "
                "(STOP_EVIDENCE, no cited value) is unchanged."
            )
            changed.append("source_map:HK-XIAOMI-AR2025:reason")
    sm["not_readable_measurement_probe"] = "evidence/I-11-A/extract/P1_xiaomi_content_probe.json"
    with open(sm_path, "w", encoding="utf-8") as fh:
        json.dump(sm, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print("fields rewritten:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
