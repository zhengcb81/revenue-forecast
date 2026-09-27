#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-C evidence builder (deterministic).

Freeze order: gate0 -> oracle.md -> this builder -> _verify.py -> mutations.
Writes only under execution_runs/I-12-C/a20260926-01/evidence/I-12-C/.
No network, no git, no parameter release, no target-period actual value access.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EV = os.path.join(HERE, "evidence", "I-12-C")
B_EV = os.path.join(PLAN_ROOT, "execution_runs", "I-12-B", "a20260926-01", "evidence", "I-12-B")

CARD = "I-12-C"
ATTEMPT = "execution_runs/I-12-C/a20260926-01"
ROLE = "implementer_i12c"
AS_OF = "2026-09-26"
FROZEN_AT = "2026-09-26T21:0x+01:00"

DESIGN_SHA = "203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0"
DISCLOSURE_V2_SHA = "373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522"

# --- disclosed base-period and prior-period segment revenue (origin 之前已披露) ---
BASE_VALUES = {
    # entity -> segment -> (base_period_value, prior_period_value, base_period, prior_period, unit, source_anchor)
    "CN-ZIJIN": {
        "MINERAL": (109977556345, 74089365354, "FY2025", "FY2024", "CNY yuan",
                    "CN-ZIJIN-AR2025 p327 对外销售收入-矿产品分部（2025年）；p328（2024年）"),
        "SMELT": (165858644874, 181141823725, "FY2025", "FY2024", "CNY yuan",
                  "CN-ZIJIN-AR2025 p327 对外销售收入-冶炼产品分部（2025年）；p328（2024年）"),
        "TRADE": (29212610830, 29386475085, "FY2025", "FY2024", "CNY yuan",
                  "CN-ZIJIN-AR2025 p327 对外销售收入-贸易分部（2025年）；p328（2024年）"),
        "OTHER": (44030270803, 19022292989, "FY2025", "FY2024", "CNY yuan",
                  "CN-ZIJIN-AR2025 p327 对外销售收入-其他分部（2025年）；p328（2024年）"),
    },
    "US-MSFT": {
        "PBP": (139996, 120810, "FY2026", "FY2025", "USD million",
                "US-MSFT-10K-FY2026 table 74 PBP revenue FY2026 / FY2025"),
        "IC": (137791, 106265, "FY2026", "FY2025", "USD million",
               "US-MSFT-10K-FY2026 table 74 IC revenue FY2026 / FY2025"),
        "MPC": (54052, 54649, "FY2026", "FY2025", "USD million",
                "US-MSFT-10K-FY2026 table 74 MPC revenue FY2026 / FY2025"),
    },
}

# disclosure adaptation (U16 disclosure_adaptation_v2.json)
DISCLOSURE = {
    ("CN-ZIJIN", "MINERAL"): ("ZJ-MIN-M09", "mapped", True, "adaptation_complete_SIGNED"),
    ("CN-ZIJIN", "SMELT"): ("ZJ-SMT-M09", "mapped", True, "adaptation_complete_SIGNED"),
    ("CN-ZIJIN", "TRADE"): (None, "no_case_not_covered", False, "no_case_registered"),
    ("CN-ZIJIN", "OTHER"): (None, "no_case_not_covered", False, "no_case_registered"),
    ("US-MSFT", "PBP"): ("MS-PBP-M05", "unmapped", False, "partial_STOP_DISCLOSURE_ADAPTATION"),
    ("US-MSFT", "IC"): ("MS-IC-M06", "unmapped", False, "partial_STOP_DISCLOSURE_ADAPTATION"),
    ("US-MSFT", "MPC"): (None, "no_case_not_covered", False, "no_case_registered"),
}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_jsonl(p):
    with open(p, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(p, rows):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def frac_fields(fr):
    n, d = fr.numerator, fr.denominator
    # exact half-up rounding to 2 decimal places (positive values only in this card)
    scaled = Fraction(n * 100, d)
    q = scaled.numerator // scaled.denominator          # floor
    r = scaled.numerator % scaled.denominator
    if r * 2 >= scaled.denominator:                     # round half up
        q += 1
    dec = "%d.%02d" % (q // 100, q % 100)
    return {"numerator": n, "denominator": d, "decimal_2dp_half_up": dec}


def main():
    os.makedirs(EV, exist_ok=True)
    samples = read_jsonl(os.path.join(B_EV, "sample_manifest.jsonl"))
    if len(samples) != 7:
        print("HARNESS: expected 7 upstream samples, got %d" % len(samples))
        return 1

    # ---------------- forecast_vintages.jsonl ----------------
    fv = []
    for s in samples:
        e, seg = s["entity"], s["segment_code"]
        case_id, dstatus, dsigned, dprep = DISCLOSURE[(e, seg)]
        fv.append({
            "sample_id": s["sample_id"],
            "entity": e,
            "segment_code": seg,
            "origin": s["origin"],
            "horizon_fy": s["horizon_fy"],
            "model_version": None,
            "model_version_state": "unbound（无 I-00-B 绑定的可运行命令；START_HERE「命令不能猜」）",
            "forecast": {"low": None, "base": None, "high": None},
            "forecast_value_state": "not_produced_params_not_released",
            "reason": "params_released=false（§三十四 硬约束「不放行任何参数」；store low/base/high 全 null、两 _PLACEHOLDER 在位）⇒ 无数值可冻结；本行登记冻结请求面与拒绝理由，不造数",
            "information_set": "origin 以前资料 only（本行未使用任何 origin 后信息；构造驱动的模型运行=0）",
            "vintage_class": "true_vintage_information_set",
            "reconstructed": False,
            "forecast_frozen_at": FROZEN_AT,
            "forecast_freeze_scope": "freeze_of_null_forecast_set（零值冻结；语义/版本/hash 见 forecast_manifest）",
            "scorable": False,
            "disclosure_qualification": {
                "case_id": case_id,
                "disclosure_adaptation_status": dstatus,
                "signed": dsigned,
                "prepared_state": dprep,
                "source": "execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json",
            },
            "formula_qualification": {"status": "accepted_scoped", "scope": "M卡 A–C 公式资格 only", "not_extrapolated_to": ["disclosure_adaptation", "accuracy"]},
        })
    write_jsonl(os.path.join(EV, "forecast_vintages.jsonl"), fv)

    # ---------------- baseline_vintages.jsonl ----------------
    bv = []
    for s in samples:
        e, seg = s["entity"], s["segment_code"]
        base_v, prev_v, base_p, prev_p, unit, anchor = BASE_VALUES[e][seg]
        h = s["horizon_years"]
        # primary: naive level persistence = last available same-caliber annual value
        bv.append({
            "baseline_id": "BL-P-%s" % s["sample_id"][4:],
            "sample_id": s["sample_id"],
            "kind": "primary_baseline",
            "rule": "最后可得同口径年度收入不变（naive level persistence；设计字段 8 primary_baseline）",
            "target_fy": s["horizon_fy"],
            "value": base_v,
            "value_exact": {"numerator": base_v, "denominator": 1},
            "unit": unit,
            "base_period": base_p,
            "base_period_source_anchor": anchor,
            "available_at": s["available_at"],
            "origin": s["origin"],
            "available_at_le_origin": True,
            "vintage_class": "true_vintage",
            "value_state": "frozen_rule_output_from_disclosed_origin_available_actuals",
            "is_released_parameter": False,
            "params_released": False,
            "future_information_used": False,
            "applicable": True,
        })
        # secondary: last available YoY growth carried forward over h years (exact rational)
        fr = Fraction(base_v, 1) * (Fraction(base_v, prev_v) ** h)
        bv.append({
            "baseline_id": "BL-S-%s" % s["sample_id"][4:],
            "sample_id": s["sample_id"],
            "kind": "secondary_baseline",
            "rule": "上一可得同比延续（last YoY growth carried forward，设计字段 8 secondary_baseline）",
            "formula": "R(base) * (R(base)/R(prev))^h",
            "formula_inputs": {"R_base": base_v, "R_prev": prev_v, "base_period": base_p, "prev_period": prev_p, "h": h},
            "target_fy": s["horizon_fy"],
            "value_exact": frac_fields(fr),
            "unit": unit,
            "available_at": s["available_at"],
            "origin": s["origin"],
            "available_at_le_origin": True,
            "vintage_class": "true_vintage",
            "value_state": "frozen_rule_output_from_disclosed_origin_available_actuals",
            "is_released_parameter": False,
            "params_released": False,
            "future_information_used": False,
            "applicable": True,
            "role": "secondary_only_not_in_primary_endpoint（设计字段 8 tie_in：primary 分母只用 primary_baseline）",
            "interpretation_note": "「carried forward」跨 h 年按逐年复利；单次套用（仅 1 年）为登记的替代读法、本卡未用，交 reviewer 裁定（结构规则解释，非统计阈值）",
        })
    write_jsonl(os.path.join(EV, "baseline_vintages.jsonl"), bv)

    fv_sha = sha256_file(os.path.join(EV, "forecast_vintages.jsonl"))
    bv_sha = sha256_file(os.path.join(EV, "baseline_vintages.jsonl"))

    # ---------------- forecast_manifest.json ----------------
    qual_counts = {"signed": 0, "stop": 0, "uncovered": 0}
    for s in samples:
        st = DISCLOSURE[(s["entity"], s["segment_code"])][1]
        if st == "mapped":
            qual_counts["signed"] += 1
        elif st == "unmapped":
            qual_counts["stop"] += 1
        else:
            qual_counts["uncovered"] += 1

    manifest = {
        "schema": "i12c_forecast_manifest/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "version": "v1",
        "frozen_at": FROZEN_AT,
        "freeze_before_unblind": True,
        "actuals_read_by_this_station": False,
        "target_period_actuals_read": False,
        "target_period_actuals_note": "目标期 FY2027 未结束且 unseal gate 未满足 ⇒ 无实际值可读（本卡零暴露）",
        "low_high_semantics": "scenario_band_not_probabilistic",
        "low_high_semantics_ref": "设计字段 9：low/high = 情景（scenario bands），非统计区间；禁称 80%/90% 置信覆盖；interval_score 与 pinball 禁用",
        "forecast_time": None,
        "forecast_time_note": "无预测值产出 ⇒ 预测时间不存在；冻结的是语义/版本/hash 与零值集",
        "input_hashes": {
            "evidence/I-12-C/forecast_vintages.jsonl": fv_sha,
            "evidence/I-12-C/baseline_vintages.jsonl": bv_sha,
        },
        "upstream_sample_table": {
            "path": "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/sample_manifest.jsonl",
            "sha256": "679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702",
            "rows": 7,
            "carrier_status": "review_pending（本批产物，未验收；引用须标此状态）",
        },
        "model_run": {
            "executed": False,
            "reason": "binding_status=unbound（无 I-00-B 绑定的 argv/cwd/allowlist）+ params_released=false ⇒ 不运行任何模型命令（START_HERE「命令不能猜」/「不能要求新功能存在才允许实施它」）",
            "model_ids_formula_qualified": "M01-M31 = accepted_scoped（仅公式面）",
        },
        "baselines": {
            "primary": {"rule": "最后可得同口径年度收入不变", "rows": 7, "state": "produced_frozen"},
            "secondary": {"rule": "上一可得同比延续（按 h 复利，精确有理数）", "rows": 7, "state": "produced_frozen_secondary_only"},
            "seasonal_same_quarter": {
                "state": "not_applicable",
                "reason": "本审计可得序列为年度分部收入，无同季可比序列（设计字段 8）",
                "approval": "pending_reviewer（not_applicable 须获批；本卡不自批）",
            },
            "missing_history_rule": "baseline 缺必需历史期 ⇒ 标 not_applicable，不用未来资料补齐（卡文动作 2）；本批 7 样本历史期齐备（紫金 FY2024-FY2025、微软 FY2025-FY2026 均在 origin 前披露）⇒ 0 例 not_applicable",
        },
        "disclosure_qualification_counts": qual_counts,
        "disclosure_qualification_detail": {
            "signed": ["CN-ZIJIN/MINERAL (ZJ-MIN-M09)", "CN-ZIJIN/SMELT (ZJ-SMT-M09)"],
            "stop": ["US-MSFT/PBP (MS-PBP-M05 partial_STOP_DISCLOSURE_ADAPTATION)", "US-MSFT/IC (MS-IC-M06 partial_STOP_DISCLOSURE_ADAPTATION)"],
            "uncovered": ["CN-ZIJIN/TRADE（无 case）", "CN-ZIJIN/OTHER（无 case）", "US-MSFT/MPC（无 case）"],
            "source_sha256": DISCLOSURE_V2_SHA,
        },
        "rerun_policy": {
            "rule": "重跑必须有原因且保留旧版本（卡文动作 3）；同 design + 同已签参数 + 同种子 ⇒ 允许复算重跑；任何 design 字段变更 ⇒ 版本 +1（设计字段 13）",
            "reruns_performed": 0,
            "old_versions_retained": [],
        },
        "seal_state": {
            "test_results_sealed": True,
            "test_results_unsealed": False,
            "accuracy_results_read": False,
            "unseal_gate_currently_satisfied": False,
        },
        "redline": {
            "parameter": "ZIJIN_MINERAL_REALIZED_UNIT_REVENUE",
            "registration_state": "registered_not_consumed",
            "consumed": False,
            "ban_verbatim": "OPEN-2 前禁消费（REMEDIATION_REGISTER.md L3951，转引上游 I-07-E §F）",
        },
        "declarations": {
            "params_released": False,
            "implementer_signed": False,
            "releases_nothing": True,
            "open2_ban_observed": True,
            "network_used": False,
            "git_used": False,
        },
        "counts": {
            "samples": 7,
            "forecast_values_frozen": 0,
            "baselines_frozen": 14,
            "scorable_samples": 0,
            "samples_without_true_vintage_forecast": 7,
        },
        "stop_registration": {
            "stop_1_ordering": {
                "rule_verbatim": "预测冻结晚于读取实际值→该样本只能exploratory。",
                "triggered": False,
                "basis": "本卡未读取任何目标期实际值（zero exposure）；冻结写入时序先于任何解封动作 ⇒ 无样本需降级 exploratory",
            },
            "stop_2_model_adaptation": {
                "rule_verbatim": "模型披露映射未通过→STOP_MODEL_ADAPTATION；不阻止其他已合格模型继续。",
                "triggered": True,
                "affected_samples": ["SMP-US-MSFT_PBP_20260729_FY2027", "SMP-US-MSFT_IC_20260729_FY2027"],
                "trigger_basis": "MS-PBP-M05 / MS-IC-M06 = partial_STOP_DISCLOSURE_ADAPTATION（signed=false）",
                "non_blocking_clause": "紫金矿产品/冶炼 2 段 disclosure_adaptation signed=true ⇒ 保留局部资格，不受本 STOP 阻断",
                "uncovered_samples": ["SMP-CN-ZIJIN_TRADE_20260320_FY2027", "SMP-CN-ZIJIN_OTHER_20260320_FY2027", "SMP-US-MSFT_MPC_20260729_FY2027"],
                "uncovered_note": "无 case（未覆盖），按 fail-closed 不得记为通过；另码登记不与 stop 混同",
            },
        },
    }
    write_json(os.path.join(EV, "forecast_manifest.json"), manifest)
    manifest_sha = sha256_file(os.path.join(EV, "forecast_manifest.json"))

    # ---------------- unblind_receipt.json ----------------
    receipt = {
        "schema": "i12c_unblind_receipt/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "issued": False,
        "issued_by": None,
        "issued_by_role": "独立reviewer（保管实际值者；卡文 Owner 栏 + 研究卡 step5）",
        "this_station_cannot_issue": True,
        "why": "实现者不自签（§三十四 L765）；解封回执属独立 reviewer 职权，本工位只登记其前置条件状态",
        "preconditions_unmet": [
            "统计 reviewer 与行业 reviewer 双签未落地（professional_approval 双双 unsigned；派单记「双签在飞」）",
            "evaluation_design 13 字段未全完成（3 PENDING + 1 含未签阈值 ⇒ 验收未达成）",
            "design_manifest 需签署后新版本重冻并经独立复审核验（当前 unseal_gate.currently_satisfied=false）",
            "编排层/父层明文解封指令未下达",
            "目标期 FY2027 未结束（紫金 2027-12-31 / 微软 2027-06-30）⇒ 实际值尚不存在",
            "forecast_vintages 零数值（params 未放行）⇒ 无可评分的冻结预测",
        ],
        "preconditions_met": [
            "forecast_manifest 已冻结（version=v1、input_hashes 已记、freeze_before_unblind=true）",
            "本卡零实际值暴露（target_period_actuals_read=false）"
        ],
        "forecast_manifest": {"path": "evidence/I-12-C/forecast_manifest.json", "sha256": manifest_sha, "version": "v1"},
        "sample_scope": {"samples": 7, "scorable_samples": 0},
        "exposure": {
            "target_period_actuals_seen": False,
            "exploratory_downgrade_required": False,
            "basis": "未见实际值 ⇒ 不触发「已见实际值降 exploratory」；但可评分样本=0",
        },
        "state": "not_issued",
        "next_owner": "独立 reviewer（另派）+ 编排层（解封指令）",
        "declarations": {"implementer_signed": False, "params_released": False, "releases_nothing": True},
    }
    write_json(os.path.join(EV, "unblind_receipt.json"), receipt)

    print("forecast_vintages rows=%d sha=%s" % (len(fv), fv_sha[:12]))
    print("baseline_vintages rows=%d sha=%s" % (len(bv), bv_sha[:12]))
    print("forecast_manifest sha=%s qual=%s" % (manifest_sha[:12], qual_counts))
    print("unblind_receipt issued=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
