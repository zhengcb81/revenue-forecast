#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-B evidence builder (deterministic, read-only with respect to upstream).

Freeze order: gate0 -> oracle.md -> this builder -> _verify.py -> mutations.
Writes only under execution_runs/I-12-B/a20260926-01/evidence/I-12-B/.
No network, no git, no parameter release, no actual-value (target period) access.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "evidence", "I-12-B")
CARD = "I-12-B"
ATTEMPT = "execution_runs/I-12-B/a20260926-01"
AS_OF = "2026-09-26"
ROLE = "implementer_i12b"

DESIGN = {
    "path": "execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json",
    "sha256": "203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0",
}
MANIFEST = {
    "path": "execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json",
    "sha256": "ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178",
}

SRC_ZIJIN = "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d"
SRC_MSFT_MEASURED = "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff"  # 64 hex (I-07-B measured)
SRC_MSFT_REGISTERED = "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecff"   # 63 hex (I-11-A source_map / store)
SRC_XIAOMI = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"

# entity, origin, tz, horizon fy end, base period, horizon years, market
ENTITIES = {
    "CN-ZIJIN": {
        "label": "紫金矿业", "market": "A", "origin": "2026-03-20",
        "tz": "Asia/Shanghai (UTC+8)", "horizon": "FY2027", "fy_end": "2027-12-31",
        "base_period": "FY2025", "horizon_years": 2, "months_from_origin": 21,
        "doc": "CN-ZIJIN-AR2025", "src_class": "information_input",
        "available_at": "2026-03-20",
        "industry": None, "lifecycle": None,
        "disclosure_condition": "annual_report_readable_sha_and_date_registered",
        "currency": "CNY", "unit": "人民币元",
    },
    "US-MSFT": {
        "label": "微软", "market": "US", "origin": "2026-07-29",
        "tz": "America/New_York", "horizon": "FY2027", "fy_end": "2027-06-30",
        "base_period": "FY2026", "horizon_years": 1, "months_from_origin": 11,
        "doc": "US-MSFT-10K-FY2026", "src_class": "information_input",
        "available_at": "2026-07-29",
        "industry": None, "lifecycle": None,
        "disclosure_condition": "annual_report_readable_sha_and_date_registered",
        "currency": "USD", "unit": "USD million",
    },
}

SEGMENTS = [
    ("CN-ZIJIN", "MINERAL", "矿产品分部", True),
    ("CN-ZIJIN", "SMELT", "冶炼产品分部", True),
    ("CN-ZIJIN", "TRADE", "贸易分部", True),
    ("CN-ZIJIN", "OTHER", "其他分部", True),
    ("CN-ZIJIN", "TOTAL", "对外销售收入-合计（合并口径）", False),
    ("US-MSFT", "PBP", "Productivity and Business Processes", True),
    ("US-MSFT", "IC", "Intelligent Cloud", True),
    ("US-MSFT", "MPC", "More Personal Computing", True),
    ("US-MSFT", "TOTAL", "Total Revenue（合并口径）", False),
]


def sample_id(entity, seg, origin, horizon):
    return "SMP-%s_%s_%s_%s" % (entity, seg, origin.replace("-", ""), horizon)


def build_sample_manifest():
    rows = []
    for entity, seg, seg_label, included in SEGMENTS:
        e = ENTITIES[entity]
        sid = sample_id(entity, seg, e["origin"], e["horizon"])
        row = {
            "sample_id": sid,
            "entity": entity,
            "entity_label": e["label"],
            "segment_code": seg,
            "segment_label": seg_label,
            "origin": e["origin"],
            "origin_timezone": e["tz"],
            "horizon_fy": e["horizon"],
            "horizon_fy_end": e["fy_end"],
            "horizon_years": e["horizon_years"],
            "months_from_origin": e["months_from_origin"],
            "base_period": e["base_period"],
            "model_version": None,
            "model_version_state": "unbound（I-12-C 冻结预测时填；本卡不猜模型版本）",
            "unit_of_record": "entity×segment×origin×horizon×model_version（model_version 列留 null，观测键= sample_id × model_version）",
            "vintage_class": "true_vintage",
            "source_doc_id": e["doc"],
            "available_at": e["available_at"],
            "available_at_le_origin": True,
            "actual_value": None,
            "actual_state": "target_period_not_yet_existing_and_sealed",
            "scorable": False,
            "included": included,
            "strata": {
                "market": e["market"],
                "horizon": "h%dFY" % e["horizon_years"],
                "disclosure_condition": e["disclosure_condition"],
                "industry": e["industry"],
                "lifecycle": e["lifecycle"],
                "industry_lifecycle_note": "设计字段 3 未给出行业/生命周期取值 ⇒ 留 null，下游分层按 unproven 处理（不臆造）",
            },
            "selection": (
                {"criteria_met": [
                    "原文可读且 sha256 可核（转录自 I-11-A source_map，见 source_vintages）",
                    "available_at<=origin 已登记并逐条验证通过",
                    "分部口径与实际值定义可对齐（设计字段 6：对外销售收入 / 分部三分部口径）",
                    "entity 在设计字段 3 池内（紫金/微软 = 可入池）",
                ], "reason_codes": []}
                if included else
                {"criteria_met": ["来源可用且日期可核"],
                 "reason_codes": ["duplicate_consolidated_not_in_error_pool"],
                 "rule_ref": "设计字段 2 duplicate_rule：同一 origin×horizon 合并与分部同时存在 ⇒ 只计分部层；合并行仅作 driver_reconciliation 校验"}
            ),
            "excluded": not included,
            "screened_at": AS_OF,
        }
        rows.append(row)
    return rows


def build_exclusions(sample_rows):
    inc = [r for r in sample_rows if r["included"]]
    exc_rows = [r for r in sample_rows if not r["included"]]
    lines = []
    lines.append({
        "record_type": "exclusion",
        "exclusion_id": "EX-001",
        "universe": "entity",
        "entity": "HK-XIAOMI",
        "entity_label": "小米集团",
        "market": "H",
        "reason_codes": ["gap-U1 evidence_unreadable", "gap-U2 publish_date_unregistered"],
        "detail": "I-11-A source_map 实测 HK-XIAOMI-AR2025 = not_readable_in_this_attempt（STOP_EVIDENCE，不引用任何值）；披露日未在回源面内登记 ⇒ 设计字段 4「发布日期缺失 ⇒ 不入池」。",
        "enumerable_sample_rows": None,
        "enumerable_note": "证据不可读 ⇒ 无法枚举行数；本行计入 entity 宇宙、不计入 row 宇宙（宇宙口径在 conservation 中显式声明）",
        "design_ref": "evaluation_design fields[3].excluded_with_reason[0]（reentry_rule 原文保留）",
        "reentry_rule": "解证据可读性并登记 available_at 后，按同一 design 版本重新纳入评估池（版本不变则记 append 事件；改 design ⇒ 新探索版本）",
        "banned_substitution": "不补选表现更好的公司（卡文停止②逐字）",
        "screened_at": AS_OF,
    })
    for i, r in enumerate(exc_rows, start=2):
        lines.append({
            "record_type": "exclusion",
            "exclusion_id": "EX-%03d" % i,
            "universe": "row",
            "sample_id": r["sample_id"],
            "entity": r["entity"],
            "segment_code": r["segment_code"],
            "origin": r["origin"],
            "horizon_fy": r["horizon_fy"],
            "reason_codes": ["duplicate_consolidated_not_in_error_pool"],
            "detail": "合并口径行与分部行同 origin×horizon 重复观测，按设计字段 2 duplicate_rule 排除出误差池（合并行仅作 driver_reconciliation 校验）。",
            "rule_ref": "evaluation_design fields[2].duplicate_rule / merge_vs_segment_rule",
            "screened_at": AS_OF,
        })
    lines.append({
        "record_type": "conservation_summary",
        "universe_declaration": {
            "entity_universe": "设计字段 3 公司池 = 3 家（紫金/小米/微软）",
            "row_universe": "已登记来源中、为已注册 origin 构造的 entity×segment/total 年度收入序列（可枚举）；小米因证据不可读不进入 row 宇宙（见 EX-001）",
        },
        "entities_total": 3,
        "entities_included": 2,
        "entities_excluded": 1,
        "candidate_rows": len(sample_rows),
        "included_rows": len(inc),
        "excluded_rows": len(exc_rows),
        "manifest_lines": len(inc),
        "exclusion_row_lines": len(exc_rows),
        "identity_1": "entities_total == entities_included + entities_excluded",
        "identity_2": "candidate_rows == included_rows + excluded_rows == manifest_lines",
        "identity_3": "missing_count = 0（无缺 origin 样本；缺 origin 者按卡文停止①应 STOP_DATASET，本卡未出现）",
        "actuals": {"target_period_actuals_delivered": 0, "scorable_samples": 0},
    })
    return lines


def build_source_vintages(sample_rows):
    used_zijin = [r["sample_id"] for r in sample_rows if r["source_doc_id"] == "CN-ZIJIN-AR2025" and r["included"]]
    used_msft = [r["sample_id"] for r in sample_rows if r["source_doc_id"] == "US-MSFT-10K-FY2026" and r["included"]]
    rows = [
        {
            "record_type": "source_vintage",
            "class": "information_input",
            "doc_id": "CN-ZIJIN-AR2025",
            "version_label": "2025 年年度报告（分部对外销售收入 p327/p328、产销量 p44、计划 p56、收入 p43）",
            "sha256_registered": SRC_ZIJIN,
            "hash_length": len(SRC_ZIJIN),
            "hash_source": "transcribed from I-11-A source_map.json (U15) and I-07-E §A (U12)",
            "hash_verified_this_station": False,
            "hash_discrepancy": None,
            "available_at": "2026-03-20",
            "published_at": "2026-03-20",
            "origin": "2026-03-20",
            "available_at_le_origin": True,
            "check": "pass",
            "state": "used",
            "quarantine": False,
            "used_by_samples": used_zijin,
            "notes": "available_at == origin（同日）⇒ 满足 <=；不含目标期（FY2027）信息。",
        },
        {
            "record_type": "source_vintage",
            "class": "information_input",
            "doc_id": "US-MSFT-10K-FY2026",
            "version_label": "Form 10-K FY2026（三分部收入 table 74、增速 table 14、产品行 table 76）",
            "sha256_registered": SRC_MSFT_REGISTERED,
            "sha256_measured": SRC_MSFT_MEASURED,
            "hash_length": len(SRC_MSFT_REGISTERED),
            "measured_hash_length": len(SRC_MSFT_MEASURED),
            "hash_source": "registered=I-11-A source_map.json (U15) 与 store (U17)；measured=I-07-B 实测 64 位（多处一致）",
            "hash_verified_this_station": False,
            "hash_discrepancy": {
                "id": "u-N4",
                "state": "registered_not_corrected",
                "detail": "转录层缺尾位 f（63 位 vs 64 位）；本卡只登记不更正上游任何字节",
                "effect_on_availability": "none（差异属 hash 转录层，不影响 available_at<=origin 判定）",
                "action": "交独立 reviewer/编排层裁决；本工位不改 U15/U17",
            },
            "available_at": "2026-07-29",
            "published_at": "2026-07-29",
            "origin": "2026-07-29",
            "available_at_le_origin": True,
            "check": "pass_with_registered_hash_discrepancy",
            "state": "used_with_flag",
            "quarantine": False,
            "used_by_samples": used_msft,
            "notes": "available_at == origin ⇒ 满足 <=；FY2027（截至 2027-06-30）非本文件内容。",
        },
        {
            "record_type": "source_vintage",
            "class": "information_input",
            "doc_id": "HK-XIAOMI-AR2025",
            "version_label": "2025 年年度报告（H 股）",
            "sha256_registered": SRC_XIAOMI,
            "hash_length": len(SRC_XIAOMI),
            "hash_source": "transcribed from I-11-A source_map.json (U15)",
            "hash_verified_this_station": False,
            "hash_discrepancy": None,
            "available_at": None,
            "published_at": None,
            "origin": None,
            "available_at_le_origin": None,
            "check": "fail",
            "state": "quarantined_unavailable",
            "quarantine": True,
            "quarantine_reason": "gap-U2 披露日未登记 + gap-U1 原文不可读（STOP_EVIDENCE）⇒ 有疑义隔离，绝不事后补当时不可得数据（卡文动作 2 逐字）",
            "used_by_samples": [],
            "notes": "对应 entity 级排除 EX-001；不得回填 available_at。",
        },
        {
            "record_type": "source_vintage",
            "class": "protocol_input",
            "doc_id": "I-12-A design bundle",
            "version_label": "evaluation_design v1 + professional_approval v1 + design_manifest v1",
            "sha256_registered": DESIGN["sha256"],
            "secondary_shas": {"professional_approval.json": "0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1",
                               "design_manifest.json": MANIFEST["sha256"]},
            "available_at": "2026-09-26",
            "origin": None,
            "available_at_le_origin": None,
            "check": "exempt",
            "exemption_reason": "评估协议输入，非预测信息集内容；不进入任何样本的驱动构造（卡文 available_at<=origin 约束针对信息输入）。豁免在此显式登记，供 reviewer 复核。",
            "state": "used",
            "quarantine": False,
            "used_by_samples": [],
            "notes": "test_results_unsealed=false；本卡未读任何测试/准确性结果。",
        },
        {
            "record_type": "source_vintage",
            "class": "transcription_input",
            "doc_id": "I-11-A source_map.json",
            "version_label": "来源 sha/页码转录层（供 hash 与页码回溯）",
            "sha256_registered": "3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf",
            "available_at": "2026-09-19",
            "origin": None,
            "available_at_le_origin": None,
            "check": "exempt",
            "exemption_reason": "转录/溯源层输入，非预测信息集内容；本工位不重哈希 raw 文件（hash_verified_this_station=false 逐行声明）。",
            "state": "used",
            "quarantine": False,
            "used_by_samples": [],
            "notes": "封盘 hypotheses.json 零字节（sha f2178768…）由校验器 J8 复算。",
        },
    ]
    return rows


def build_actuals_policy(sample_rows):
    horizon_rows = []
    for r in sample_rows:
        if not r["included"]:
            continue
        horizon_rows.append({
            "sample_id": r["sample_id"],
            "target_period": r["horizon_fy"],
            "target_period_end": r["horizon_fy_end"],
            "as_of": AS_OF,
            "horizon_elapsed": False,
            "actual_value": None,
            "actual_state": "not_yet_existing（目标财年未结束）+ sealed（独立 reviewer 未交付）",
            "primary_actual_rule_when_available": "首次披露值（as-originally-reported）",
            "restated_rule_when_available": "最终重述值仅作 secondary；origin 时点不可得 ⇒ 不用于 primary",
            "scorable": False,
        })
    return {
        "schema": "i12b_actuals_policy_application/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "frozen_policy_source": {
            "design_field_index": 6,
            "design_path": DESIGN["path"],
            "design_sha256": DESIGN["sha256"],
            "rules": {
                "primary_actual": "首次披露值（as-originally-reported）",
                "restated_actual": "最终重述值仅作 secondary 对照；若在 origin 时点尚不可得 ⇒ 不可用于 primary",
                "currency_fx": "各实体按本币评估（人民币元 / USD million）；跨实体汇总只用无量纲指标；跨币种展示须用 origin 前可得汇率且本卡禁联网 ⇒ 该项 PENDING（不伪造）",
                "segment_reorg": "以 origin 时点披露分部口径为准；重组后不回溯改写历史口径，回溯改写 = 新 vintage",
                "fiscal_year": "统一到 FY 标签并显式登记财年截止（微软 FY 截至 6-30；紫金 12-31），不同截止期的年度不作同一 horizon",
                "gross_net": "统一为对外销售收入（net of internal，E5 抵销口径）；含内部交易的分部总计不得作收入基期",
                "ma_interruption": "并购致口径断裂 ⇒ 断点后单列为新 series，不跨断点计算误差；断裂登记 reason_code",
            },
        },
        "sealing": {
            "rule_verbatim": "I-12-B的实际值由独立reviewer收集封存，预测执行者只见ID、hash与政策；I-12-C冻结预测manifest后才由该reviewer出具unblind_receipt解封。（common_research_cards.md L289）",
            "actuals_collector": "独立reviewer（非本工位）",
            "target_period_actuals_delivered_to_this_station": 0,
            "target_period_actuals_seen_by_this_station": False,
            "baseline_period_disclosures_seen_by_this_station": True,
            "baseline_period_disclosures_are_origin_information_set": True,
            "exposure_recorded": "目标期实际值零暴露 ⇒ 不降级 exploratory；基期披露值属 origin 前信息（设计字段 8 baseline 输入），非目标期实际值",
            "unseal_gate_currently_satisfied": False,
            "unseal_gate_requires": [
                "professional_approval.json 中 statistical_reviewer 与 industry_reviewer 双签（signed=true）——当前均 unsigned（双签在飞）",
                "evaluation_design 13 字段全部完成或获批 not_applicable——当前 3 PENDING + 1 含未签阈值",
                "design_manifest 重冻（新版本）并由独立复审核验",
                "父层/编排层明文解封指令",
            ],
            "test_results_sealed": True,
            "test_results_unsealed": False,
            "accuracy_results_read": False,
        },
        "application_per_sample": horizon_rows,
        "counts": {
            "samples_registered": len(horizon_rows),
            "target_period_actuals_existing": 0,
            "target_period_actuals_delivered": 0,
            "scorable_samples": 0,
        },
        "stop_registration": {
            "STOP_DATASET": {
                "triggered": False,
                "rule_verbatim": "future leakage、重复sample或缺origin→STOP_DATASET。",
                "checked": ["future leakage：available_at<=origin 7/7 通过，目标期信息零使用",
                            "重复 sample：sample_id 7/7 唯一（J1）",
                            "缺 origin：0 条（origin 全部登记）"],
            },
            "limited": {
                "triggered": True,
                "rule_verbatim": "分层样本不足→记录limited，不补选表现更好的公司。",
                "reason": "可评样本 0（目标期未结束 + 未解封）⇒ 记录 limited；小米按 fail-closed 保持排除，不补选",
            },
        },
        "acceptance_state": {
            "traceable_to_info_time": True,
            "traceable_to_actual_value": False,
            "why": "目标期实际值尚不存在且封存未解封 ⇒ 验收「可从每个样本追到…实际值」在本 attempt 不可达成（fail-closed 登记，非绕过）",
            "counts_conserved": True,
        },
    }


def build_split_manifest(sample_rows):
    return {
        "schema": "i12b_split_manifest/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "design_field_index": 5,
        "design_field_status": "PENDING",
        "design_pending_reason_verbatim": "可得 vintage 清单（历史 origin 逐个 available_at）未在本卡回源面内 ⇒ 切点/折数无法核算；不由实现者挑方便值（卡文动作 1）",
        "state": "PENDING_unsigned_split_not_assigned",
        "rules_frozen": {
            "split_type": "纯时间因果切分，禁止随机切分",
            "scheme": "滚动 origin（rolling）为主口径；扩展窗口（expanding）仅作敏感性对照",
            "leakage_rule": "同一 entity（集团）任何分部不得跨 train/tune/validation/final_test；同一 origin 的全部 segment×horizon 观测必须同集合",
            "overlap_horizon_rule": "重叠 horizon 观测按 origin 聚簇（block），方差按 origin block 估计",
            "final_test_rule": "最终测试集实际值在 design_manifest SHA256 冻结前保持封存，一次性解封",
        },
        "assignments": {"train": [], "tune": [], "validation": [], "final_test": []},
        "counts": {
            "train": 0, "tune": 0, "validation": 0, "final_test": 0,
            "unassigned": len([r for r in sample_rows if r["included"]]),
            "total_included_samples": len([r for r in sample_rows if r["included"]]),
        },
        "why_no_split": "设计字段 5 = PENDING（折数/切点/窗口/调参预算未签署）⇒ 本卡只登记规则骨架与 0 分配，不挑切点（卡文动作 1 + 派单 fail-closed）",
        "auditability": "分组与时间切分规则面可审计；切点待统计 reviewer 签署后由新 attempt 以 append 事件追加，本件字节不改",
        "grouping_keys": ["entity（集团不得跨集合）", "origin（同 origin 全部 segment×horizon 同集合）"],
    }


def main():
    os.makedirs(EV, exist_ok=True)
    candidates = build_sample_manifest()          # 全量筛选表（9 行：7 纳入 + 2 排除）
    samples = [r for r in candidates if r["included"]]   # sample_manifest.jsonl = 纳入样本（7 行）
    exclusions = build_exclusions(candidates)     # 排除全量表（2 row + 1 entity + conservation）
    sources = build_source_vintages(candidates)
    actuals = build_actuals_policy(samples)
    split = build_split_manifest(samples)

    def write_jsonl(name, rows):
        with open(os.path.join(EV, name), "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")

    def write_json(name, obj):
        with open(os.path.join(EV, name), "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")

    write_jsonl("sample_manifest.jsonl", samples)
    write_jsonl("exclusions.jsonl", exclusions)
    write_jsonl("source_vintages.jsonl", sources)
    write_json("actuals_policy_application.json", actuals)
    write_json("split_manifest.json", split)

    inc = [r for r in samples if r["included"]]
    print("sample_manifest lines=%d included=%d" % (len(samples), len(inc)))
    print("exclusions lines=%d" % len(exclusions))
    print("source_vintages lines=%d" % len(sources))
    print("actuals counts=%s" % actuals["counts"])
    print("split counts=%s" % split["counts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
