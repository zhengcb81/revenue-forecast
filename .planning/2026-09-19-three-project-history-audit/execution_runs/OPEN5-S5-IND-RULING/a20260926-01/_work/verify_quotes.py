#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回源校验：报告/裁定里引用的逐字片段必须真的出现在源文件中（转述=失败）。"""
import json
import os
import sys

PLAN = ".planning/2026-09-19-three-project-history-audit"
R = os.path.join(PLAN, "execution_runs")
HERE = os.path.join(R, "OPEN5-S5-IND-RULING", "a20260926-01")
ENV = os.path.join(R, "I11A-OPEN5-ENVOWNER", "a20260924-01", "ruling.md")
IND = os.path.join(R, "I11A-OPEN-IND", "a20260924-01", "ruling.md")
OWN = os.path.join(PLAN, "OWNER_DECISIONS.md")
ACCT_R = os.path.join(R, "OPEN5-S5-ACCT-GRADING", "a20260926-01", "s5_acct_report.md")
S4_R = os.path.join(R, "OPEN5-S4-DUAL-PATH-VERIFY", "a20260926-01", "s4_report.md")

CHECKS = [
    (ENV, "| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，**证据等级由会计面认定**"
          "（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | 行业 reviewer + 会计 reviewer | "
          "各自专业裁定权（**本载体不代行**） | 任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |"),
    (ENV, '即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**（IND 处置规则 B 部分继续有效：'
          '港股命题零产出、参数维持 `_PLACEHOLDER`）。'),
    (ENV, "复核不一致 ⇒ 该来源不可引用，维持不可读处置"),
    (ENV, "新建 attempt 重新取证"),
    (IND, "- 环境 owner 解决可读性后，若新 attempt 实测仍读不出原文 ⇒ B 部分（保持不可用）继续有效，C 表不启用；"),
    (IND, '- 若出现①类可读原文且含分部收入 ⇒ B 的"零产出"解除，港股命题可重新走正常取证（仍需会计面定证据等级）；'),
    (IND, "**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**"),
    (IND, "必须登记 URL + 取回时间 + sha256，**永不冒充本地可核**；且仍需可复核的取文路径"),
    (IND, "- 用外部抓取件静默顶替本地原件（必须按④登记为外部）；"),
    (IND, "**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`"),
    (IND, "**仅可作线索**，**不得**进参数、**不得**进命题的 `cited_values`"),
    (OWN, "- **取证（选项 3）的证据等级由会计面定，不由取证方自定**；取不到就维持 BLOCKED，**不造绿色样例**。"),
    (OWN, "**「授权」是许可不是动作**：四项均**不产生任何 ACCEPT、不解除任何 BLOCKED、不改任何 status**"),
    (ACCT_R, "请裁定 C 表是否启用"),
    (ACCT_R, "请确认 attempt04 的文件类型用途"),
    (ACCT_R, "请确认 attempt08 的语言面限制"),
    (ACCT_R, "请复核 G3 分歧登记"),
    (S4_R, "G2/G3 是 S5 引用前必须先补的 provenance 硬缺项"),
]


def main():
    fails = []
    for path, needle in CHECKS:
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        if needle not in text:
            fails.append({"file": path, "missing": needle[:80]})
    # ind_ruling.json 内的 verbatim 字段同样回源
    ruling = json.load(open(os.path.join(HERE, "ind_ruling.json"), encoding="utf-8"))
    pairs = [
        (ENV, ruling["authorization"]["S5_definition_verbatim"]["quote"]),
        (ENV, ruling["authorization"]["boundary_verbatim"]["quote"].strip()),
        (OWN, ruling["authorization"]["owner_rule_verbatim"]["quote"]),
        (IND, ruling["points"][0]["basis_verbatim"]["IND_L240"]),
        (IND, ruling["points"][0]["basis_verbatim"]["IND_L241"]),
        (IND, ruling["points"][0]["basis_verbatim"]["IND_L231"]),
        (IND, ruling["points"][3]["basis_verbatim"]["IND_L234"]),
        (IND, ruling["points"][3]["basis_verbatim"]["IND_L360"]),
        (IND, ruling["points"][3]["basis_verbatim"]["IND_L261"]),
    ]
    for path, needle in pairs:
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        if needle not in text:
            fails.append({"file": path, "missing": str(needle)[:80]})
    out = {"checks_total": len(CHECKS) + len(pairs), "fails": fails}
    # 报告侧：报告里引用的片段必须同时是源文件的子串（防转述/防错字）
    report_path = os.path.join(HERE, "s5_ind_report.md")
    with open(report_path, "r", encoding="utf-8", newline="") as f:
        report = f.read()
    src_cache = {}

    def src(path):
        if path not in src_cache:
            with open(path, "r", encoding="utf-8", newline="") as f:
                src_cache[path] = f.read()
        return src_cache[path]

    report_checks = [
        (ENV, '即使 S2 自检显示"某路径能读出锚词"，在 S3/S4/S5 走完之前**仍按不可读处置**'),
        (ENV, "复核不一致 ⇒ 该来源不可引用，维持不可读处置"),
        (IND, "C 表不启用"),
        (IND, "①类可读原文且含分部收入"),
        (IND, "永不冒充本地可核"),
        (IND, "**C. 可接受的替代来源及其证据等级（我裁，供 owner 解锁后使用）**"),
        (OWN, "**不造绿色样例**"),
    ]
    for path, frag in report_checks:
        if frag not in src(path) or frag not in report:
            fails.append({"report_or_source": path, "missing": frag[:80],
                          "in_source": frag in src(path), "in_report": frag in report})
    # 实测引文/计数：与本工位自抽文本对拍（报告里的数字与逐字片段都必须可复算）
    ex = os.path.join(HERE, "_work", "extract")
    zh = open(os.path.join(ex, "s5_ind_attempt04_fitz.txt"), encoding="utf-8").read()
    en = open(os.path.join(ex, "s5_ind_attempt08_fitz.txt"), encoding="utf-8").read()
    pos = [
        (zh, "截至2025年12月31日止年度的經審核合併業績"),
        (zh, "羅兵咸永道會計師事務所"),
        (zh, "概無任何重大分部間銷售"),
        (zh, "集團總收入為人民幣4,573億元"),
        (zh, "分部資料及收入"),
        (en, "FIVE-YEAR FINANCIAL SUMMARY"),
        (en, "What we have audited"),
        (en, "auditor’s report"),
        (en, "no separate segment assets"),
        (en, "Segment-wise"),
    ]
    for text, frag in pos:
        if frag not in text:
            fails.append({"extraction_missing": frag})
        if frag not in report:
            fails.append({"report_missing": frag})
    zero = ["核數師報告", "無保留意見", "財務摘要", "分部資產"]
    for frag in zero:
        if zh.count(frag) != 0:
            fails.append({"expected_zero_but": frag, "count": zh.count(frag)})
    counts = {"分部收入": 16, "手機×AIoT": 68, "業務分部": 22, "分部毛利率": 8, "毛利": 101, "總收入": 34, "五年": 4}
    for frag, want in counts.items():
        got = zh.count(frag)
        if got != want:
            fails.append({"count_mismatch": frag, "want": want, "got": got})
    extract_json = json.load(open(os.path.join(HERE, "_work", "s5_ind_extract.json"), encoding="utf-8"))
    if "460,387" not in report:
        fails.append({"report_missing": "attempt07 char count 460,387"})
    if extract_json["anchors"]["attempt07_proxy_zh"]["total_chars"] != 460387:
        fails.append({"extract_mismatch": "attempt07 total_chars != 460387"})
    out = {"checks_total": len(CHECKS) + len(pairs) + len(report_checks) + len(pos) + len(zero) + len(counts),
           "fails": fails}
    with open(os.path.join(HERE, "_work", "verify_quotes.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not fails else 3


if __name__ == "__main__":
    sys.exit(main())
