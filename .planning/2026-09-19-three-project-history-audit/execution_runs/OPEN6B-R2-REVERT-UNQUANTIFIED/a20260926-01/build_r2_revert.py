# -*- coding: utf-8 -*-
"""
OPEN6B-R2-REVERT-UNQUANTIFIED · 恢复路径 (c) 落地脚本（6b-R2）

授权：OWNER_DECISIONS.md §三十三（owner 原话「确认适用 (c) 不改规则（建议）」）
      + ruling_6b.md L97「(c) 若结构差无法解释 ⇒ 按 hypotheses.json L315 revert_rule
        退 unquantified —— 该写入属有写入面的实现者 / 编排层」

做什么：
  以封盘原件（supersedes_sha256 = f2178768…）为基线，**外科式文本编辑**只改
  数组下标 2（H-CN-ZIJIN-VOL-03）的三个字段，产出同目录 hypotheses_r2_v1.json。
  封盘原件零字节改动（写入前后各复算一次）；revert_rule 字面零改动。

不做什么（白名单之外一律不动）：revert_rule 字面 / falsifier 其余键 /
threshold_basis / threshold_review_status / decision.* / parameter_mapping.low,base,high /
其余 7 个下标 / 任何 status,decision 字段。
"""
import hashlib
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(BASE, "..", "..", "I-11-A", "a20260919-01",
                                     "evidence", "I-11-A", "hypotheses.json"))
PRE = os.path.join(BASE, "preimage", "hypotheses.json")
DST = os.path.join(BASE, "hypotheses_r2_v1.json")

EXPECTED_SHA = "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"
EXPECTED_BYTES = 51697
IDX = 2  # H-CN-ZIJIN-VOL-03


def sha_of(path):
    b = open(path, "rb").read()
    return hashlib.sha256(b).hexdigest(), len(b)


def fail(msg):
    print("BLOCKED: " + msg)
    sys.exit(4)


def main():
    # ---- 1. 前像/封盘复算（fail-closed：不符即 blocked）----
    src_sha, src_len = sha_of(SRC)
    pre_sha, pre_len = sha_of(PRE)
    print("[pre] source_sha256 = %s bytes = %d" % (src_sha, src_len))
    print("[pre] preimage_sha256 = %s bytes = %d" % (pre_sha, pre_len))
    if (src_sha, src_len) != (EXPECTED_SHA, EXPECTED_BYTES):
        fail("封盘原件 sha/bytes 与前像不符：preimage 复算不符")
    if (pre_sha, pre_len) != (EXPECTED_SHA, EXPECTED_BYTES):
        fail("preimage/hypotheses.json 复算不符")

    raw = open(SRC, "rb").read()
    if raw[:3] == b"\xef\xbb\xbf":
        fail("源文件含 BOM")
    if b"\r\n" in raw:
        fail("源文件含 CRLF")
    text = raw.decode("utf-8")
    lines = text.split("\n")

    # ---- 2. 规则分支与条目定位（fail-closed：定位不到即 blocked）----
    try:
        i_state = next(i for i, l in enumerate(lines)
                       if l.strip().startswith('"state"') and 240 <= i <= 244)
    except StopIteration:
        fail("定位不到 hypotheses[2].state（L243）")
    if lines[240] != '  "hypothesis_id": "H-CN-ZIJIN-VOL-03",':
        fail("下标 2 不是 H-CN-ZIJIN-VOL-03：%r" % lines[240])
    if lines[242] != '  "state": "pending_professional_decision",':
        fail("state 前像不符：%r" % lines[242])
    if not lines[243].startswith('  "state_reason": '):
        fail("state_reason 前像不符")
    if not lines[352].startswith('  "anchor_text": '):
        fail("element-2 末键定位不符")
    if lines[353] != " },":
        fail("element-2 结束定位不符：%r" % lines[353])
    data = json.loads(text)
    if len(data) != 8 or data[IDX]["hypothesis_id"] != "H-CN-ZIJIN-VOL-03":
        fail("数组形态不符（应为 8 元素，下标 2 = H-CN-ZIJIN-VOL-03）")
    revert_rule_before = data[IDX]["falsifier"]["revert_rule"]
    print("[locate] element-2 = H-CN-ZIJIN-VOL-03 | state line index =", i_state + 1)
    print("[locate] revert_rule L315 literal (must stay unchanged):")
    print("         " + revert_rule_before)

    # ---- 3. 三处改动（白名单）----
    new_state = "unquantified"
    new_reason = (
        "按 hypotheses.json L315 revert_rule 的「无法凑平 ⇒ 口径不一致」支退回 unquantified"
        "（owner OWNER_DECISIONS.md §三十三 当轮裁定原话「确认适用 (c) 不改规则（建议）」；"
        "ruling_6b.md L97 恢复路径 (c)）。实测依据：OPEN6B-R2-INVENTORY-BRIDGE/not_closed.json —— "
        "四条线 0 千克、C1 FAIL、B1/B2 触发、残差 154 千克、跨年结构差 FY2024 +93 / FY2025 +154 千克"
        "（金行专属、93–154 倍于 1 千克粒度）。两条字面触发如实登记为不成立"
        "（① 83,161 ≤ 84,477 未超；② 方向一致），revert_rule 字面零改动；旧快照保留"
        "（封盘原件 f2178768… 零字节改动 + preimage/ 前像）。恢复条件三条见 revert_r2.json。"
        "本退回不放行参数（low/base/high 仍 null）、不签 τ、不产生 ACCEPT、不解除 BLOCKED-6b"
        "（ruling_6b.md L110 由 owner/编排层另判）。原 state_reason："
        "存货桥是否闭合需要看存货明细（在产品/在途/寄售），本 attempt 只核到产销量表的三个数；"
        "是否可用产量作可售量上限需行业 reviewer 裁定"
    )
    provenance = {
        "provenance_schema": "hypotheses_version_provenance/1",
        "version": "hypotheses_r2_v1",
        "supersedes_sha256": EXPECTED_SHA,
        "supersedes_file": "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
        "supersedes_bytes": EXPECTED_BYTES,
        "branch_note": (
            "以封盘原件为基线的 6b-R2 恢复路径 (c) 单命题分支；只动下标 2（H-CN-ZIJIN-VOL-03），"
            "下标 0,1,3,4,5,6,7 仍是封盘原字节；不携带 hypotheses_v2/v3/v4/h4/h4_ind 的改动；"
            "封盘原件零字节改动；版本裁并归编排层。"
        ),
        "modified_indices": [IDX],
        "modified_fields": ["state", "state_reason", "provenance"],
        "unchanged_indices": [0, 1, 3, 4, 5, 6, 7],
        "revert_applied": {
            "target_field": "hypotheses[2].state",
            "from": "pending_professional_decision",
            "to": "unquantified",
            "rule_source": {
                "file": "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
                "line": 315,
                "byte_range": [19071, 19346],
                "literal_changed": False
            },
            "rule_branch": "「无法凑平 ⇒ 口径不一致」支（falsifier.threshold L310；由 OWNER_DECISIONS §三十三 当轮裁定确认适用）",
            "literal_triggers_both_false": [
                "① 销售量 83,161 ≤ 生产量 82,743 + 期初库存 1,734 = 84,477（未超）",
                "② 销量高于产量 ⇒ 库存应降，库存量同比 −264 千克（方向一致，非相反）"
            ],
            "authority": "OWNER_DECISIONS.md §三十三 owner 原话「确认适用 (c) 不改规则（建议）」；ruling_6b.md L97",
            "evidence": "execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/not_closed.json",
            "execution_record": "revert_r2.json",
            "recovery_conditions": [
                "公司披露按金属拆分的期末存货数量（千克）",
                "并购标的购买日存货的重量明细",
                "产销量表新增「在产品 / 在途 / 寄售」数量列"
            ],
            "recovery_rule": "任一出现即可按 OPEN6B-R2-INVENTORY-BRIDGE oracle §3.2 重评"
        },
        "releases_nothing": True,
        "does_not_claim_I11A_acceptance": True,
        "new_file_sha256": None,
        "new_file_sha256_note": "自指不可自证：本文件 sha256 由本工位写后外部复算，见同目录 revert_r2.json 与 handoff.json"
    }

    prov_text = json.dumps(provenance, ensure_ascii=False, indent=1)
    prov_inner = prov_text.split("\n")
    # 形态与封盘一致：元素键 2 空格、其内嵌对象键 3 空格、数组项 4 空格、元素内对象闭合 2 空格
    prov_lines = (['  "provenance": {']
                  + [("  " + l) if l else l for l in prov_inner[1:-1]]
                  + ["  }"])

    out_lines = list(lines)
    out_lines[i_state] = '  "state": %s,' % json.dumps(new_state, ensure_ascii=False)
    out_lines[i_state + 1] = '  "state_reason": %s,' % json.dumps(new_reason, ensure_ascii=False)
    out_lines[352] = lines[352] + ","
    out_lines[353:353] = prov_lines
    new_text = "\n".join(out_lines)

    # ---- 4. 断言 ----
    # 4.1 element-2 之外逐字节不变
    def span(t, i_start, i_after):
        ls = t.split("\n")
        starts, off = [], 0
        for l in ls:
            starts.append(off)
            off += len(l.encode("utf-8")) + 1
        return starts[i_start], starts[i_after]
    # 旧：element-2 = 行下标 239(' {') .. 353(' },')，其后行下标 354(' {')
    # 新：插入 N 行后，元素关闭行在 353+N，其后行在 354+N
    N = len(prov_lines)
    s0, e0 = span(text, 239, 354)
    s1, e1 = span(new_text, 239, 354 + N)
    b_old, b_new = text.encode("utf-8"), new_text.encode("utf-8")
    if b_old[:s0] != b_new[:s1]:
        fail("element-2 之前的字节被改动")
    print("[assert] bytes before element-2 identical = True (%d bytes)" % s1)
    # element-2 结束后的字节：以元素结束行 ' },' 的行尾对齐比较
    tail_old = b_old[e0:]
    tail_new = b_new[e1:]
    if tail_old != tail_new:
        fail("element-2 之后的字节被改动")
    print("[assert] bytes after element-2 identical = True (%d bytes)" % len(tail_new))

    # 4.2 JSON 重解析
    new_data = json.loads(new_text)
    if len(new_data) != 8:
        fail("新文件元素数 != 8")
    for i in range(8):
        if i == IDX:
            continue
        if new_data[i] != data[i]:
            fail("下标 %d 被意外改动" % i)
    print("[assert] unchanged_indices [0,1,3,4,5,6,7] deep-equal = True")
    diff_keys = sorted(set(data[IDX]) | set(new_data[IDX]))
    changed = [k for k in diff_keys if data[IDX].get(k) != new_data[IDX].get(k)]
    if sorted(changed) != ["provenance", "state", "state_reason"]:
        fail("改动字段超出白名单：%s" % changed)
    print("[assert] changed fields = %s (whitelist only)" % changed)
    if new_data[IDX]["state"] != "unquantified":
        fail("state 未退到 unquantified")
    if new_data[IDX]["falsifier"]["revert_rule"] != revert_rule_before:
        fail("revert_rule 字面被改动（owner 选择 #2 禁止）")
    if new_data[IDX]["falsifier"]["threshold_basis"] != data[IDX]["falsifier"]["threshold_basis"]:
        fail("threshold_basis 被改动")
    if data[IDX]["decision"] != new_data[IDX]["decision"]:
        fail("decision 字段被改动")
    if (new_data[IDX]["parameter_mapping"]["low"], new_data[IDX]["parameter_mapping"]["base"],
            new_data[IDX]["parameter_mapping"]["high"]) != (None, None, None):
        fail("参数 low/base/high 被改动（不得放行参数）")
    if "threshold_review_status" in new_data[IDX].get("falsifier", {}) and \
            new_data[IDX]["falsifier"]["threshold_review_status"] != "not_reviewed":
        fail("threshold_review_status 被改动")
    print("[assert] revert_rule literal unchanged = True")
    print("[assert] threshold_basis / decision / low,base,high unchanged = True")

    # ---- 5. 写入（UTF-8 无 BOM、LF）----
    with open(DST, "w", encoding="utf-8", newline="\n") as g:
        g.write(new_text)
    dst_sha, dst_len = sha_of(DST)
    out_raw = open(DST, "rb").read()
    if out_raw[:3] == b"\xef\xbb\xbf" or b"\r\n" in out_raw:
        fail("输出文件含 BOM 或 CRLF")
    json.loads(out_raw.decode("utf-8"))
    print("[write] %s" % DST)
    print("[write] new_file_sha256 = %s bytes = %d" % (dst_sha, dst_len))
    print("[write] json.load reparse = OK | BOM = False | CRLF = 0")

    # ---- 6. 封盘原件与前像写后复算 ----
    src_sha2, src_len2 = sha_of(SRC)
    pre_sha2, pre_len2 = sha_of(PRE)
    print("[post] source_sha256 = %s bytes = %d unchanged = %s"
          % (src_sha2, src_len2, (src_sha2, src_len2) == (src_sha, src_len)))
    print("[post] preimage_sha256 = %s bytes = %d unchanged = %s"
          % (pre_sha2, pre_len2, (pre_sha2, pre_len2) == (pre_sha, pre_len)))
    if (src_sha2, src_len2) != (EXPECTED_SHA, EXPECTED_BYTES):
        fail("封盘原件写后 sha 变化")
    if (pre_sha2, pre_len2) != (EXPECTED_SHA, EXPECTED_BYTES):
        fail("前像写后 sha 变化")

    result = {
        "supersedes_sha256": src_sha,
        "supersedes_bytes": src_len,
        "preimage_sha256": pre_sha2,
        "new_file": "hypotheses_r2_v1.json",
        "new_file_sha256": dst_sha,
        "new_file_bytes": dst_len,
        "target_field": "hypotheses[2].state",
        "state_from": "pending_professional_decision",
        "state_to": new_data[IDX]["state"],
        "modified_indices": [IDX],
        "sealed_unchanged": True,
        "revert_rule_literal_unchanged": True,
        "changed_fields": changed
    }
    print("RESULT_JSON " + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
