"""OPEN5-S4 · write handoff.json (sha256+bytes of every file this station wrote)."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ME = os.path.dirname(HERE)
OUT = os.path.join(ME, "handoff.json")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    dpv = json.load(open(os.path.join(ME, "dual_path_verify.json"), encoding="utf-8"))
    raw = json.load(open(os.path.join(HERE, "raw_measurements.json"), encoding="utf-8"))

    files = []
    total = 0
    for base, dirs, names in os.walk(ME):
        dirs.sort()
        for n in sorted(names):
            p = os.path.join(base, n)
            rel = p.replace(os.sep, "/")
            if rel.endswith("/handoff.json"):
                continue
            b = os.path.getsize(p)
            total += b
            relpath = os.path.relpath(p, ME).replace(os.sep, "/")
            files.append({
                "path": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                        "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/" + relpath,
                "bytes": b,
                "sha256": sha256_file(p),
            })
    files.sort(key=lambda x: x["path"])

    doc = {
        "card": "OPEN-5",
        "step": "S4",
        "attempt": "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01",
        "role": "implementer_s4",
        "generated_utc": utc_now(),
        "authorized_by": {
            "dispatch": "编排层派单（ruling.md L165 受理人 = 实现者 + 独立 reviewer；"
                        "授权 = S1/S3）",
            "S4_definition_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L165",
                "quote": "| **S4** | **双路径复核 + provenance**：两条独立取文路径互证（承 P1/P2 精神），"
                         "登记文件 sha256、页码/锚文本、取回 UTC；外部件按 IND C 表 **④** 标 "
                         "`external_retrieval_not_local`、**永不冒充本地** | 实现者 + 独立 reviewer | "
                         "S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |",
            },
            "dispatch_paraphrase_delta": "派单转述失败分支为「该来源不可用」；ruling.md L165 原文为"
                                         "「该来源不可引用，维持不可读处置」。以文件原文为准，按原文执行。",
            "S5_definition_not_exercised": {
                "source": "同文件 L166",
                "quote": "| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，"
                         "**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | "
                         "行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | "
                         "任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |",
            },
            "boundary_verbatim": {
                "source": "同文件 L174-L179",
                "quote": "即使 S2 自检显示\"某路径能读出锚词\"，在 S3/S4/S5 走完之前仍按不可读处置"
                         "（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。",
            },
            "owner_authorization": {
                "source": ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md "
                          "§二十六 #1/#2",
                "quote": "#1 PEND-5a owner 原话「授权」；#2 PEND-5b owner 原话「要」→ "
                         "澄清答「两项都要（PEND-5b 装 + E1 交会计面）」",
            },
            "IND_C_table_4": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN-IND/a20260924-01/ruling.md L234",
                "quote": "| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | "
                         "`external_retrieval_not_local` | 必须登记 URL + 取回时间 + sha256，"
                         "**永不冒充本地可核**；且仍需可复核的取文路径 |",
            },
            "s3_input_read_only": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "OPEN5-S3-REACQUISITION/a20260925-01/",
                "note": "只读；101 个 S3 登记文件逐件重算 sha256 全等",
            },
        },
        "consistency_result": dpv["consistency_result"],
        "consistency_result_enum": ["CONSISTENT", "PARTIAL", "NOT_USABLE"],
        "consistency_result_reasons": dpv["consistency_result_reasons"],
        "per_face": {k: v["verdict"] for k, v in dpv["faces"].items()},
        "per_source_usability": dpv["per_source_usability"],
        "paths_compared": dpv["paths_compared"],
        "my_own_numbers": {
            "M1_A_vs_B1": {
                "ocr_lines_checked": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["ocr_lines_checked"],
                "verbatim_matches_in_origin_layer": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["verbatim_matches_in_origin_layer"],
                "cover_fragment_reproduced_pages": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["cover_fragment_reproduced"],
                "readable_span_coverage": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["readable_span_coverage"],
                "numeric_conflict_count": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["numeric_conflict_count"],
                "numeric_conflicts": dpv["method1_A_vs_B1"][
                    "primary_variant_fresh_pdfium"]["numeric_conflicts"],
            },
            "A_anchors": dpv["path_results"]["A_ocr"]["anchor_hit_count_recounted"],
            "B1_fitz": dpv["path_results"]["B1_origin_textlayer"]["fresh_fitz"][
                "hit_word_count"],
            "B1_pypdfium2": dpv["path_results"]["B1_origin_textlayer"][
                "fresh_pypdfium2"]["hit_word_count"],
            "B1_pages": dpv["path_results"]["B1_origin_textlayer"]["fresh_fitz"]["pages"],
            "B2_first_line_cross": dpv["method2_B2_fitz_vs_pdfminer"][
                "first_line_cross_match_count"],
            "B2_word_sets_equal": dpv["method2_B2_fitz_vs_pdfminer"][
                "word_level_sets_equal"],
            "B2prime_cn": len(dpv["method2prime_B2prime"]["cn"]["fitz_hit_words"]),
            "B2prime_en": len(dpv["method2prime_B2prime"]["en"]["fitz_hit_words"]),
        },
        "diffs_vs_s3": dpv["diffs_vs_s3"],
        "provenance_gaps": [
            {"id": g["id"], "severity": g["severity"], "entry": g["entry"],
             "element_violated": g["element_violated"]} for g in
            dpv["provenance_review"]["gaps"]],
        "own_external_flags": {
            "attempt04": "external_retrieval_not_local=true (IND C 表 ④ + OPEN-11 L360)",
            "attempt08": "external_retrieval_not_local=true (IND C 表 ④ + OPEN-11 L360)",
            "origin": "external_retrieval_not_local=false (product-repo local original)",
            "divergence_from_s3": "S3 in-02/in-03 标 false（口径=非第三方代理）；本工位标 true；"
                                  "两边均不回改，只登记分歧",
        },
        "oracle": dpv["oracle"],
        "level_claimed": None,
        "level_claimed_note": "不判会计证据等级（归 S5：行业 reviewer + 会计 reviewer）；"
                              "不重裁 IND C 表行业处置规则",
        "releases_nothing": True,
        "open5_released": False,
        "prior_not_readable_preserved": True,
        "prior_not_readable_verdict_changed": False,
        "sealed_attempt_untouched": True,
        "s3_s1_bytes_untouched": True,
        "s3_s1_bytes_evidence": "101 files re-hashed, mismatched=[] missing=[]",
        "placeholder_params_released": False,
        "accept_produced": False,
        "evidence_grading_done": False,
        "industry_rule_regraded": False,
        "independent_reviewer_self_claimed": False,
        "five_plan_files_written": False,
        "still_not_readable_disposition": True,
        "boundary_L179": "即使结论为 CONSISTENT，S5 走完前仍按不可读处置；"
                         "本轮为 NOT_USABLE，更不解除任何处置",
        "s5_handoff_note": "表已备（dual_path_verify.json 逐路径逐页证据 + provenance 缺项 G1–G7）。"
                           "S4 结论 = NOT_USABLE（触发面 = origin 本体）⇒ origin 按 L165 不可引用、"
                           "维持不可读、不进入定级；替代件 attempt04/attempt08 双路径互证已成立 ⇒ "
                           "S5 请按 IND C 表 ④ + 会计面定级补裁（G2/G3 为引用前必补的 provenance 硬缺项）。"
                           "本工位不判等级、不重裁行业处置、不解除 OPEN-5。",
        "next_station": "S4 独立 reviewer（父另派，本工位不自任）→ S5 行业复裁 + 会计定级",
        "network_used": False,
        "git_write_ops": 0,
        "git_status_used": False,
        "git_diff_total": 3827,
        "git_diff_total_note": "在 .planning 内于本工位测量期间由 3826 → 3827（同工作区其他会话的"
                               "计划文件变动，非本工位写入：diff 列表中无任何 OPEN5-S4-DUAL-PATH-VERIFY 条目）；"
                               "**非 .planning 计数三次复测恒为 0**",
        "git_diff_non_planning": 0,
        "untracked_non_planning": 48,
        "untracked_non_planning_note": "全部为既有 .tmp-r41-mutation/* 等历史路径，非本工位创建",
        "write_surface": "only .planning/2026-09-19-three-project-history-audit/execution_runs/"
                         "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/",
        "written_files": {
            "count": len(files),
            "total_bytes": total,
            "self_excluded": "handoff.json (self-reference impossible)",
            "files": files,
        },
        "not_done": [
            "未改 S3 / S1 两站 / 封盘 I-11-A 任何字节（101 件 sha 全等自证）",
            "未把 not_readable 改成「已验证」、未改任何 prior 判定字段",
            "不判会计证据等级（level_claimed=null，归 S5）",
            "未重裁 IND C 表行业处置规则",
            "未解除 OPEN-5、未放行 _PLACEHOLDER 港股参数",
            "未产生 I-11-B 的 ACCEPT、未代签",
            "未自任独立 reviewer（另一半由父另派）",
            "未写五份计划文件",
            "未写 .planning 之外任何路径（含 company-wiki 产品仓）",
            "零 git 写、未用 git status、未联网",
            "未重跑 OCR 引擎（全局版本 ≠ S3 版本，跨版本不构成同条件复现；已标未证实）",
            "未下 S5 结论（行业复裁 + 会计定级是下一站）",
        ],
    }

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(OUT, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", OUT, "files:", len(files), "bytes:", total, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
