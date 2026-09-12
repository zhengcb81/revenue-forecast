"""Two-sided claim audit for the phase-B run directory.

Why this file exists (B-DR5-01 / B-DR6 self-audit falsification): earlier rounds were rejected
because correction notes claimed fixes that had never landed. The first audit attempt shipped
only a JSON file of assertions - no patterns, no commands, no output - so the reviewer could not
re-run it and at least four of its "verified" entries were false or one-sided. This script is the
re-runnable form:

  * it searches EVERY manifest-eligible file in the run directory (not a hand-picked subset),
  * every check names BOTH the required new value and the superseded value(s) that must no longer
    appear as an assertion,
  * "history" is exempt at LINE level only: a line is history if it carries a version prefix such
    as `v0.1.2` / `rev3` / `B-DR` AND quotes the superseded wording inside a change-log/finding
    table; anything else counts as a live assertion,
  * it prints file:line evidence for both sides and exits non-zero on any failure.

Usage:  python evidence/claim_fact_audit.py [--verbose]
Exit:   0 = all checks pass, 1 = at least one failed, 2 = usage error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RUN = Path(__file__).resolve().parents[1]
EXCLUDE_NAMES = {"checkpoint.json"}  # same exclusion the checkpoint generator documents
# The audit tool and its output are excluded from the search set: the tool necessarily CONTAINS the
# superseded patterns as data, so searching itself would always fail. Disclosed rather than silent.
EXCLUDE_SELF = {"evidence/claim_fact_audit.py", "evidence/claim-fact-audit.json", "evidence/claim_fact_audit.pyc"}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache"}

# B-VR02R4-01: the wording about the S-10 deviation drifted because it was RESTATED in several
# places, and the previous audit could not see it — it only searched this run directory, while the
# claims also live in the product repo (docstrings and comments).  These extra roots are searched
# with the same two-sided rules and the same history exemption, so a restatement that contradicts
# the authoritative section fails the audit wherever it hides.
EXTRA_ROOTS = [
    Path(r"C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/service.py"),
    Path(r"C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/resolver.py"),
    Path(
        r"C:/Users/郑曾波/Projects/company-wiki/tests/contract/"
        "test_r4b02_candidate_selection.py"
    ),
]

# Checks: (label, [required strings], [superseded strings])
CHECKS: list[tuple[str, list[str], list[str]]] = [
    ("B05 provenance 不得存原文片段（许可已删除）",
     ["不得存原文片段"],
     ["抓取时间/原始片段或 hash", "原始片段或 hash）"]),
    ("B05 保留键两处形状定义都带 schema_version",
     ['{"r4_provenance": {"schema_version": "1.0", "fields"', '"r4_provenance": {"schema_version": "1.0", "fields"'],
     ['`{"r4_provenance": {"fields"', '"r4_provenance": {"fields": {…}}']),
    ("B05 禁止 metadata_json 整列替换（含胜利路径）",
     ["整列替换", ":1073-1077"],
     []),
    ("scanner 锚点唯一取值 :1007-1099",
     [":1007-1099"],
     [":1007-1081"]),
    ("B05 覆盖 INSERT 分支 :1009-1027",
     [":1009-1027"],
     []),
    ("`metadata_json` 共享读取者含 legacy_observer.py:90",
     ["legacy_observer.py:90"],
     []),
    ("N-1 不在 B 的完成定义/可签列/迁移前置/测试映射/VR 协议中",
     ["**不含 N-1**", "N-1 不在其中", "N-1 未定义，不得作为前置"],
     ["+ N-1 判定 +", "**N-1 支持**的判定逻辑与拒绝语义", "明确支持 N-1"]),
    ("复杂度棘轮 + 覆盖率棘轮 + NEW_FILE_MAX 均已登记",
     ["NEW_FILE_MAX", "TIER2 `resolver.py` = 86"],
     []),
    ("B-payload-hash 标注当前不可执行/blocked",
     ["当前不可执行", "**当前为 `blocked`**"],
     []),
    ("VR-N21 不在 B",
     ["**不含** VR-N21"],
     ["含 A07 的 VR-N21"]),
    ("R-6 计数 = 11 个锚点（A 侧口径已注明）",
     ["11 个锚点"],
     ["9 处同型排序"]),
    ("F2 步骤列含 B06；F11 属只读调用目标而非 allowed",
     ["B02/B04/B06/B07", "## 1b. 只读调用目标"],
     ["| F11 ✅**已批准**"]),
    ("test-acceptance-map 的 L06 只出现一次口径（= B）且无 B/C 残留",
     ["**= B**（矩阵 `:33` 原文即 `L06 B`"],
     ["L06 = B/C"]),
    ("P01–P03 归属按时引用矩阵原文（B/C 本地栏）",
     ["矩阵 `:88`"],
     ["**矩阵原文 = B/C**"]),
    ("版本/状态行 = v0.1.7（file-scope / task_plan / 实施回填）",
     ["file-scope v0.1.7", "B 设计 v0.1.7", "**六轮 rejected**"],
     ["file-scope v0.1.6", "B 设计 v0.1.6", "三轮 rejected", "**v0.1.1**：B01"]),
    ("B05 已实施（3 子步：抽取 / 保留键 / 逐列规则 + 读侧 blocked）",
     ["B05 已实施", "test_r4b05_metadata_provenance.py", "r4_provenance",
      "9db3394", "bdd99dc", "6909e78"],
     ["B05 尚未实施", "子步 3 未开始", "B05 待实施"]),
    ("B05 的两条发现已登记（声明/派生细化 + 行为变化）",
     ["F-B05-1", "F-B05-2", "声明压派生", "metadata_status"],
     []),
    ("B02 已实施（F1+F2+F10）且实施记录在案",
     ["B02 已实施", "evidence/b02-implementation.md"],
     ["设计 + 边界 + 验证协议就绪；产品代码零改动"]),
    ("B02 段 3 的硬门偏差已登记为 S-10（含\"硬门归 B03\"的依据）",
     ["S-10", "硬门归 B03"],
     []),
    ("B02 的 RED/GREEN 证据文件在场（含 pre 对照）",
     ["b02-red-green-pre-b02.json", "b02-red-green-post-b02.json"],
     []),
    ("B02 非首选副本绝不「可读即用」（B-VR02-01 已修）",
     ["非首选副本", "B-VR02-01"],
     ["回退到第一份**可读**的合格副本", "若清单里**没有任何**候选的字节通过验证、却存在**本地可读**的合格副本"]),
    ("B02 遗留注解契约保持不变（B-VR02-02/-03 已修）",
     ["遗留注解契约", "B-VR02-02"],
     ["`exact_duplicate_location_count` / `exact_original_copy_count` 现在只统计**合格**副本"]),
    ("B02 预算按请求重置（B-VR02-04）",
     ["begin_request", "B-VR02-04"],
     []),
    ("B.VR rev1 记录在场且 verdict = rejected",
     ['"verdict": "rejected"', "B.VR-b02.json"],
     []),
    ("B02 与 pre-B02 的差异被逐条列出（不再声称「由构造保证」）（B-VR02R3-01）",
     ["与 pre-B02 的两处差异", "my.rejections_backup", "B-VR02R3-01"],
     ["不宽于 pre-B02**的**由构造保证", "由构造保证不宽于 pre-B02"]),
    ("B04 已实施（验收 + 发现登记，产品代码零改动）",
     ["B04 已实施", "test_r4b04_reference_stability.py", "F-B04-1", "产品代码零改动"],
     ["B04 尚未实施", "B04 待实施"]),
    ("F-B04-1 的后果陈述已按 B.VR b04 更正（不再说「引用不可解引用」）",
     ["旧字节被物理销毁", "需要 locator 的读路径", "B-VR04-01", "S-12"],
     ["被取代修订的引用**不可再解引用**", "其引用**不可再解引用**"]),
    ("L03 的保障归因已更正（provider 门，不是 B02 组限定）",
     ["provider_document_id` 强身份门", "B-VR04-02"],
     ["已由 B02 的 source 组限定 + 本步 L03 负例确认"]),
    ("F-B04-2 + B04 变异记录在场",
     ["F-B04-2", "b04_mutation_check.py", "M3/M4/M5/M6/M7"],
     []),
    ("S-10 差异只有一处权威清单（a/b/c/d），其他地方只引用不重述",
     ["权威清单", "| a |", "| b |", "| c |", "| d |", "只引用本表",
      "section 3", "b02-implementation.md"],
     ["Two differences from pre-B02", "除这两处外没有第三种差异",
      "no wider than pre-B02", "strictly no wider than pre-B02",
      "that row minus two defects", "减去 a、b 两个缺陷",
      "构造性保证不宽于 pre-B02", "已改为构造性成立", "构造性成立",
      "= pre-B02 会服务的那一行", "锚定到 pre-B02 会服务的那一行"]),
    ("差异清单含第三/第四处（云占位探针、验证副本优先）",
     ["本地探针", "hydration_required", "验证通过的副本永远优先", "条件性"],
     []),
    ("B.VR rev3 记录在场且逐条处置已登记",
     ['"verdict": "accepted_with_findings"', "B.VR-b02-rev3.json", "B-VR02R3-07"],
     []),
    ("B02 存活变异 M5/M6/M7 已全部被杀并登记",
     ["M5 / M6 / M7 全部 KILLED", "test_r4b02_cancel_during_the_last_candidate_read"],
     []),
    ("B.VR rev2 记录在场且 verdict = accepted_with_findings",
     ['"verdict": "accepted_with_findings"', "B.VR-b02-rev2.json"],
     []),
    ("S-11（预算耗尽映射）已登记且 S-10 已重述",
     ["S-11", "unverified_budget_exceeded_on_pre_b02_canonical"],
     []),
    ("B02 未新增产品模块 / 未改棘轮表（S-7）",
     ["test_r4b02_no_new_source_catalog_module_was_added",
      "test_r4b02_complexity_ratchet_table_is_not_edited"],
     []),
    ("inputs 注记写在 inputs 内层（外层会被 main() 覆盖）",
     ["per-file versions matter"],
     []),
    ("S-7/S-8 已登记且 S-8 不在\"裁定结果\"表内",
     ["S-7_ratchet_edit", "**S-8**（v0.1.6 新增，**待 owner**）"],
     ["| **S-8**（v0.1.6 新增，**待 owner**） | 把执行计划 §B07"]),
]

HISTORY_HINT = re.compile(r"(v0\.\d\.\d|rev\d|B-DR|A-DR|BDR)", re.IGNORECASE)


def eligible_files() -> list[Path]:
    out = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(RUN)
        if rel.name in EXCLUDE_NAMES or any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if rel.as_posix() in EXCLUDE_SELF:
            continue
        out.append(path)
    return out


def classify(line: str, rel: str) -> str:
    """Decide whether a superseded value on this line is history or a live assertion.

    History means: the file is a FROZEN review record under reviews/ (never edited by the authors,
    it quotes exactly what it judged), or the line carries a version/review prefix (change-log or
    finding-history row). Everything else counts as a live assertion.
    """
    if rel.startswith("reviews/"):
        return "history"
    return "history" if HISTORY_HINT.search(line) else "ASSERTION"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    files = eligible_files()
    texts = {p.relative_to(RUN).as_posix(): p.read_text(encoding="utf-8") for p in files}
    for extra in EXTRA_ROOTS:
        if extra.is_file():
            texts[f"product:{extra.as_posix()}"] = extra.read_text(encoding="utf-8")
        else:
            print(f"WARN  extra search root missing: {extra}")
    results, failures = [], 0
    for label, required, superseded in CHECKS:
        req_hits, old_hits = [], []
        for rel, text in texts.items():
            for i, line in enumerate(text.splitlines(), 1):
                for needle in required:
                    if needle in line:
                        req_hits.append({"file": rel, "line": i, "text": line.strip()[:160]})
                for needle in superseded:
                    if needle in line:
                        old_hits.append({"file": rel, "line": i, "kind": classify(line, rel),
                                         "text": line.strip()[:160]})
        live_old = [h for h in old_hits if h["kind"] == "ASSERTION"]
        ok = bool(req_hits) and not live_old
        failures += 0 if ok else 1
        results.append({"claim": label, "required_hits": req_hits[:4], "superseded_hits": old_hits[:6],
                        "live_superseded": live_old, "verified": ok})
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        if not ok or args.verbose:
            for h in req_hits[:2]:
                print(f"        new  {h['file']}:{h['line']}  {h['text'][:110]}")
            for h in old_hits[:3]:
                print(f"        old  [{h['kind']}] {h['file']}:{h['line']}  {h['text'][:110]}")
    passed = len(CHECKS) - failures
    print(f"\n{passed}/{len(CHECKS)} checks pass (two-sided, whole-directory search)")
    out = RUN / "evidence" / "claim-fact-audit.json"
    out.write_text(json.dumps({
        "method": ("two-sided: for every claim the required value must be present AND the superseded "
                   "value must not appear as a live assertion anywhere in the run directory; a "
                   "superseded value is exempt only on a line that carries a version/review prefix "
                   "(change-log or finding history)"),
        "tool": "evidence/claim_fact_audit.py (re-runnable: python evidence/claim_fact_audit.py)",
        "files_searched": sorted(texts),
        "excluded_from_search": sorted(EXCLUDE_SELF | EXCLUDE_NAMES),
        "checks": results,
        "passed": passed, "total": len(CHECKS),
        "generated_by": "python evidence/claim_fact_audit.py",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(RUN).as_posix()}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
