#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_v2.py — I10A-DISCLOSURE-ADAPT-SIGN / a20260925-01

Creates disclosure_adaptation_v2.json as a NEW, additive, superseding version of the SEALED
I-10-A machine face evidence/I-10-A/disclosure_qualification.json.

  * reads the sealed source READ-ONLY (never writes into I-10-A/a20260923-01)
  * modifies ONLY cases[*].disclosure_adaptation  (adds reviewer_determination; promotes 4)
  * keeps every other key/value identical (asserted below and again by check_signoff.py G2)
  * writes UTF-8 (no BOM) + LF + indent=1, exactly the source's formatting modulo line endings
  * re-parses the result with json.load and asserts the decision_sha256 recomputes identically

Run:  python -X utf8 build_v2.py
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SEALED = os.path.join(PLAN, "execution_runs", "I-10-A", "a20260923-01")
SRC_REL = "execution_runs/I-10-A/a20260923-01/evidence/I-10-A/disclosure_qualification.json"
SRC = os.path.join(SEALED, "evidence", "I-10-A", "disclosure_qualification.json")
ORACLE = os.path.join(HERE, "oracle.md")
OUT = os.path.join(HERE, "disclosure_adaptation_v2.json")

SRC_SHA = "6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb"
SRC_BYTES = 8603
STATION_DATE = "2026-09-25"          # UTC date of this station (a20260925-01)
ROLE = "industry_or_accounting_reviewer"
ROLE_LABEL = "行业/会计专业 reviewer（非实现者）"
AUTHORIZED_BY = (
    "execution_v2/card_I-11-B.md L9 前提第二行逐字"
    "「I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。」"
    "；C7 原文 = execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json L117-L125 "
    "i11b_unlock_conditions 第7条（L124）逐字"
    "「card_I-11-B.md L9：I-10-A 为实际采用的公司/分部/模型签署披露适配口径（现 review.md 记 "
    "disclosure_adaptation = NOT granted）」"
)
C7_SOURCE = "execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json L124 (i11b_unlock_conditions[7])"
MANIFEST_FILE = "evidence/I-10-A/selected_model_manifest.json"

# ---------------------------------------------------------------- frozen ruling line
def extract_ruling_line(path):
    b = open(path, "rb").read()
    m1 = b"--- BEGIN C7 RULING TEXT ---\n"
    m2 = b"\n--- END C7 RULING TEXT ---"
    i = b.index(m1) + len(m1)
    j = b.index(m2)
    line = b[i:j]
    if b"\n" in line or b"\r" in line:
        raise SystemExit("FATAL: ruling line is not a single line")
    return line


RULING_LINE_B = extract_ruling_line(ORACLE)
RULING_LINE = RULING_LINE_B.decode("utf-8")
PREIMAGE = SRC_SHA.encode("ascii") + b"\n" + RULING_LINE_B
DECISION_SHA = hashlib.sha256(PREIMAGE).hexdigest()

# ---------------------------------------------------------------- measured evidence (read-only)
def jload(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)

recon = jload(os.path.join(SEALED, "evidence", "I-10-A", "historical_reconciliation.json"))
oexp = jload(os.path.join(SEALED, "evidence", "I-10-A", "oracle_expected.json"))
probe = jload(os.path.join(SEALED, "evidence", "I-10-A", "historical_mapping_probe.json"))
manifest = jload(os.path.join(SEALED, "evidence", "I-10-A", "selected_model_manifest.json"))
src = jload(SRC)

# formatting round-trip check: source == json.dumps(source, indent=1, ensure_ascii=False) modulo CRLF
raw = open(SRC, "rb").read().decode("utf-8")
canonical = json.dumps(src, indent=1, ensure_ascii=False) + "\n"
if raw.replace("\r\n", "\n") != canonical:
    raise SystemExit("FATAL: source formatting is not reproducible with indent=1/ensure_ascii=False")

# measured adopted list
adopted = []
for comp in manifest["companies"]:
    for seg in comp["segments"]:
        if seg.get("status") == "adopted":
            for am in seg["adopted_models"]:
                adopted.append((am["case_id"], comp["company_id"], seg["segment"],
                                am["model_id"], am["m_card"]))
ADOPTED_IDS = [a[0] for a in adopted]
SRC_CASE_IDS = list(src["cases"].keys())
if ADOPTED_IDS != SRC_CASE_IDS:
    raise SystemExit(f"FATAL: manifest adopted {ADOPTED_IDS} != source cases {SRC_CASE_IDS}")

CASE_META = {
    "ZJ-MIN-M09": dict(
        basis_lines=[43, 46, 47, 48, 49], period="FY2025",
        reason=(
            "D：8 条主要矿产品线逐字段原文/页/单位换算在案，missing_fields=[]（disclosure_mapping.json L700、"
            "L768 review_signature 曾为 PENDING_INDEPENDENT_REVIEW）。"
            "E：本 reviewer 以「披露销售数量×披露不含税单价」独立复建 FY2025 同口径收入，"
            "Σrebuilt=131,491,532,271 元 vs Σdisclosed=131,489,500,000 元，残差 −2,032,271 元"
            "（|残差|/披露合计=0.0015456%）落在先冻结的 ±0.05%（oracle_expected L25）内，"
            "且与冻结 oracle 期望逐位相等（historical_reconciliation L100-L106）。"
            "probe：calculate_registered_model 计数 24、low/base/high 同值（historical_mapping_probe L12/L25）。"
            "原文独立核对：CN-ZIJIN-2025.txt L3958-L3964「金锭 810.17 元/克 · 49,074 千克 · 3,975,798 万元」；"
            "L4080-L4085「冶炼产锌 20,327 元/吨 · 403,324 吨 · 819,823 万元」。"),
        permits=[
            "可披露：FY2025 已结束期间、8 条主要矿产品线（金锭/金精矿/铜精矿/电积铜/电解铜/矿山产锌/矿山产银/铁精矿）"
            "同口径「销售数量 × 不含税单价」复建收入及其残差 −2,032,271 元（−0.0015456%）",
            "可披露：该适配作为 historical_mapping_probe（24 次调用、三键同值）的接线证据",
            "可披露：L2 范围桥 gap = +6,782,172,956 元，状态 partially_explained（已量化未分解）",
            "可披露：口径限该公司/矿产品分部/resource(M09)/FY2025/主要产品线 E 范围"],
        forbids=[
            "不可披露：不得称矿产品分部全部收入已适配（表外矿产品不入范围；贸易分部、其他分部 not_selected）",
            "不可披露：不得把 L2 桥 gap 静默吸收进容差，或称其已逐项分解",
            "不可披露：不得称 accuracy 通过、不得称三情景预测、不得称企业适配通过",
            "不可披露：不得据此放行 CN-ZIJIN-2025 正式预测（formal_company_forecast_cleared=false）",
            "不可披露：不得外推到 not_selected 模型（含 M10 reserve_depletion）"]),
    "ZJ-SMT-M09": dict(
        basis_lines=[60, 63, 64, 65, 66], period="FY2025",
        reason=(
            "D：3 条主要冶炼产品线逐字段在案，missing_fields=[]（disclosure_mapping.json L1040、L1095）。"
            "E：Σrebuilt=183,988,605,486 元 vs Σdisclosed=183,988,510,000 元，残差 −95,486 元"
            "（0.0000519%）落在先冻结 ±0.05%（oracle_expected L43）内，与冻结期望逐位相等"
            "（historical_reconciliation L179-L185）。probe 计数 9、三键同值（historical_mapping_probe L121/L134）。"
            "本 reviewer 独立复算冶炼产锌线：403,324 吨 × 20,327 元/吨 = 8,198,366,948 元 vs 披露 8,198,230,000 元"
            "→ −136,948 元（−0.0017%，线级 ±0.10% 内）；原文 CN-ZIJIN-2025.txt L4080-L4085。"),
        permits=[
            "可披露：FY2025、3 条主要冶炼产品线（冶炼加工金/冶炼产铜/冶炼产锌）同口径复建收入及残差 −95,486 元（−0.0000519%）",
            "可披露：冶炼产锌保留案例复算（403,324×20,327=8,198,366,948，残差 −136,948，线级容差内）",
            "可披露：L2 范围桥 gap = +5,695,369,295 元，状态 partially_explained",
            "可披露：口径限该公司/冶炼产品分部/resource(M09)/FY2025"],
        forbids=[
            "不可披露：不得称冶炼产品分部全部收入已适配（硫酸、电池级碳酸锂等表外产品在 E 范围残差内）",
            "不可披露：不得把 L2 桥 gap 静默吸收进容差或称已分解",
            "不可披露：不得称 accuracy 通过或三情景预测",
            "不可披露：不得据此放行 CN-ZIJIN-2025 正式预测"]),
    "XM-PHONE-M03": dict(
        basis_lines=[112, 115, 116, 117, 118], period="FY2025",
        reason=(
            "D：1 实例×4 字段（units/unit_revenue/timing_factor/other_revenue），missing_fields=[]"
            "（disclosure_mapping.json L1211、L1253）。"
            "E：165,200,000 部 × 1,128.7 元/部 = 186,461,240,000 元 vs 附註5 186,439,777 千元，"
            "残差 −21,463,000 元（0.0115120%）落在先冻结 ±0.05%（oracle_expected L60）内"
            "（historical_reconciliation L240-L246）。probe 计数 3、三键同值（historical_mapping_probe L185/L198）。"
            "原文独立核对：HK-XIAOMI-2025_decoded.txt L1404「165.2 百萬部」、L1436「每部人民幣 1,128.7 元」、"
            "L17790 分部收入行「186,439,777…351,217,174…457,286,687」——本 reviewer 复算 "
            "186,439,777+123,200,191+37,440,346+4,136,860=351,217,174、+106,069,513=457,286,687 千元，逐位相等。"),
        permits=[
            "可披露：FY2025 智能手機产品线「出货量 × ASP」复建收入 186,461,240,000 元及残差 −21,463,000 元（−0.0115120%）",
            "可披露：構成桥 = 手機×AIoT 分部小計 351,217,174 千元 的 trivial_composition 验算",
            "可披露：解码文本方法（原件 cmap 反查、mapped 272,511 / unmapped 0）与其复现",
            "可披露：口径限该公司/智能手機产品线/unit_sales(M03)/FY2025"],
        forbids=[
            "不可披露：不得把本适配扩到 IoT與生活消費產品 / 互聯網服務 / 其他相關業務（三者 not_selected）",
            "不可披露：不得称 accuracy 通过、不得称三情景预测（探针仅 historical_mapping_probe）",
            "不可披露：不得据此放行 HK-XIAOMI-2025 正式预测",
            "不可披露：不得在 other_revenue 显式为 0 的口径下宣称其他业务已适配"]),
    "XM-EV-M03": dict(
        basis_lines=[152, 155, 156, 157, 158], period="FY2025",
        reason=(
            "D：1 实例×4 字段（含 other_revenue=2,800,000,000 元 显式映射），missing_fields=[]"
            "（disclosure_mapping.json L1380、L1409）。"
            "E：411,082 輛 × 251,171 元/輛 + 2.8e9 = 106,051,877,022 元 vs 披露 106,069,513,000 元，"
            "残差 +17,635,978 元（0.0166268%）落在先冻结 ±0.10%（oracle_expected L76）内"
            "（historical_reconciliation L301-L307）。probe 计数 3、三键同值，mut_omit_optional rc2 击杀"
            "（historical_mapping_probe L231/L244；唯一 other≠0 case）。"
            "原文独立核对：HK-XIAOMI-2025_decoded.txt L1582「411,082 輛」、L1610「每輛人民幣 251,171 元」。"),
        permits=[
            "可披露：FY2025 分部整段「交付量 × 每輛 ASP + 其他相關業務 28 億元」复建收入 106,051,877,022 元"
            "及残差 +17,635,978 元（+0.0166268%）",
            "可披露：other_revenue 億元粒度 ±5e7 界为容差依据（0.0473%），非拟合结果",
            "可披露：構成桥 = 手機×AIoT 小計 351,217,174 千元 的 trivial_composition 验算",
            "可披露：口径限该公司/智能電動汽車及AI等創新業務分部/unit_sales(M03)/FY2025"],
        forbids=[
            "不可披露：不得把 AI 等创新业务收入单列（披露口径含于其他相關業務，p.22 未单独拆分）",
            "不可披露：不得改用 backlog/订单存量口径（M29/M21 not_selected）",
            "不可披露：不得称 accuracy 通过或三情景预测",
            "不可披露：不得据此放行 HK-XIAOMI-2025 正式预测"]),
    "MS-PBP-M05": dict(
        basis_lines=[188, 191, 192, 193, 194], period="FY2026",
        reason=(
            "不授予：FY2026 Form 10-K 未按所需粒度披露经营量/价，4 个驱动全部 missing"
            "（average_customers / revenue_per_customer / timing_factor / usage_revenue），"
            "zero_filled=false ×4、zero_filled=true ×0（disclosure_mapping.json L1425-L1447）；"
            "E 未执行（historical_reconciliation.json L348 E_status=STOP_DISCLOSURE_ADAPTATION、"
            "L350 level1=null、L351 residual=null，无捏造残差）；probe 未运行"
            "（oracle_expected L86-L87 expected_E_status/expected_probe_status）。"
            "缺收入历史桥 ⇒ 按 card_I-10-A.md L26 停止条款3 判 STOP_DISCLOSURE_ADAPTATION。"),
        permits=[
            "可披露：D 段逐字段映射与会计口径已完成且缺失字段保留 missing（AD-11 不补 0、不倒推）",
            "可披露：本判定为「不授予」的诚实出口，US-MSFT-2026 该分部 disclosure_adaptation 仍为 unmapped",
            "可披露：分部局部结果保留，但公司正式预测不放行"],
        forbids=[
            "不可披露：不得把 status 写成 mapped 或 signed 置 true",
            "不可披露：不得补零、不得由收入倒推 average_customers/revenue_per_customer、不得用 RPO 摊回 ARPU",
            "不可披露：不得展示 E 段复建值或残差（level1/residual 必须保持 null）",
            "不可披露：不得称 US-MSFT-2026 已完成企业披露适配或可进入正式预测"]),
    "MS-IC-M06": dict(
        basis_lines=[204, 207, 208, 209, 210], period="FY2026",
        reason=(
            "不授予：FY2026 Form 10-K 仅披露 Azure 收入美元额与增长率，3 个驱动全部 missing"
            "（eligible_activity / monetization_rate / fixed_revenue），zero_filled=false ×3、"
            "zero_filled=true ×0（disclosure_mapping.json L1535-L1551）；"
            "E 未执行（historical_reconciliation.json L358-L361，level1=null、residual=null）；"
            "probe 未运行（oracle_expected L97-L98）。缺收入历史桥 ⇒ 同判 STOP_DISCLOSURE_ADAPTATION。"),
        permits=[
            "可披露：D 段逐字段映射完成、missing 保留（含可选 fixed_revenue 亦不默认补 0）",
            "可披露：本判定为「不授予」的诚实出口，该分部 disclosure_adaptation 仍为 unmapped",
            "可披露：RPO 仅有存量无 rollforward（L232/L4057），故项目存量桥不可复建"],
        forbids=[
            "不可披露：不得把 status 写成 mapped 或 signed 置 true",
            "不可披露：不得以增长率反推绝对用量、不得补零、不得由收入倒推费率",
            "不可披露：不得展示 E 段复建值或残差",
            "不可披露：不得称 US-MSFT-2026 已完成企业披露适配"]),
}

EVIDENCE_BLOCK = {}
for cid in ADOPTED_IDS:
    r = recon["cases"][cid]
    o = oexp["cases"][cid]
    if r.get("E_status") == "STOP_DISCLOSURE_ADAPTATION":
        p = probe["not_run"][cid]
        EVIDENCE_BLOCK[cid] = {
            "E_status": "STOP_DISCLOSURE_ADAPTATION",
            "level1_same_scope_rebuild": None,
            "residual_disclosed_minus_rebuilt": None,
            "missing_fields": None,
            "zero_filled_false": None,
            "probe_status": p["probe_status"],
            "probe_not_run_reason": p["not_run_reason"],
            "expected_E_status": o["expected_E_status"],
            "expected_probe_status": o["expected_probe_status"],
            "frozen_aggregate_tolerance_rel": None,
            "within_frozen_tolerance": None,
        }
    else:
        p = probe["cases"][cid]
        EVIDENCE_BLOCK[cid] = {
            "E_status": "executed",
            "sum_rebuilt": r["level1_same_scope_rebuild"]["sum_rebuilt"],
            "sum_disclosed": r["level1_same_scope_rebuild"]["sum_disclosed"],
            "residual_disclosed_minus_rebuilt": r["level1_same_scope_rebuild"]["residual_disclosed_minus_rebuilt"],
            "frozen_aggregate_tolerance_rel": o["aggregate_tolerance_rel"],
            "within_frozen_tolerance": r["level1_same_scope_rebuild"]["within_frozen_tolerance"],
            "matches_oracle_expected_residual": r["level1_same_scope_rebuild"]["matches_oracle_expected_residual"],
            "probe_calls": p["counts_measured"]["calculate_registered_model_calls"],
            "probe_counts_ok": p["counts_ok"],
            "low_base_high_identical": p["low_base_high_identical"],
        }
# STOP cases: fill from the D-side mapping (missing fields) read-only
dmap = jload(os.path.join(SEALED, "evidence", "I-10-A", "disclosure_mapping.json"))
for cid in ("MS-PBP-M05", "MS-IC-M06"):
    mf = dmap["cases"][cid]["missing_fields"]
    EVIDENCE_BLOCK[cid]["missing_fields"] = [m["driver"] for m in mf]
    EVIDENCE_BLOCK[cid]["missing_count"] = len(mf)
    EVIDENCE_BLOCK[cid]["zero_filled_false"] = sum(1 for m in mf if m["zero_filled"] is False)
    EVIDENCE_BLOCK[cid]["zero_filled_true"] = sum(1 for m in mf if m["zero_filled"] is True)
    EVIDENCE_BLOCK[cid]["missing_drivers"] = [m["driver"] for m in mf]

BASIS_DOCS = {
    "ZJ-MIN-M09": [
        {"file": MANIFEST_FILE, "lines": [43, 46, 47, 48, 49], "what": "status=adopted / case_id / model_id / m_card / adaptation_scope"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [100, 101, 102, 104, 105, 106], "what": "Σrebuilt / Σdisclosed / 残差 / 冻结容差 / within / matches"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [21, 22, 23, 25, 27], "what": "冻结期望与 aggregate_tolerance_rel"},
        {"file": "evidence/I-10-A/historical_mapping_probe.json", "lines": [12, 25], "what": "probe 计数与 counts_ok"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [11, 700, 768], "what": "D 段 instance/missing/review_signature"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [47, 58, 62, 67, 120], "what": "手算表、残差期望、L2 桥 partially_explained、容差依据"},
        {"file": "source_extracts/CN-ZIJIN-2025.txt", "lines": [3958, 3964, 4080, 4085, 26011, 35012], "what": "原文量价与分部附注"},
        {"file": "execution_v2/card_I-10-A.md", "lines": [10, 19, 26, 29], "what": "冻结清单前提 / 动作5 签署 / 停止条款3 / 验收"},
    ],
    "ZJ-SMT-M09": [
        {"file": MANIFEST_FILE, "lines": [60, 63, 64, 65, 66], "what": "status=adopted / case_id / model / scope"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [179, 180, 181, 183, 184, 185], "what": "Σrebuilt / Σdisclosed / 残差 / 容差 / within / matches"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [39, 41, 43, 45], "what": "冻结期望与容差"},
        {"file": "evidence/I-10-A/historical_mapping_probe.json", "lines": [121, 134], "what": "probe 计数"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [776, 1040, 1095], "what": "D 段"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [73, 75, 78, 80, 121], "what": "冶炼产锌手算与 L2 桥"},
        {"file": "source_extracts/CN-ZIJIN-2025.txt", "lines": [4080, 4085, 35013], "what": "原文量价与分部附注"},
    ],
    "XM-PHONE-M03": [
        {"file": MANIFEST_FILE, "lines": [112, 115, 116, 117, 118], "what": "status=adopted / case_id / model / scope"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [240, 241, 242, 244, 245, 246], "what": "复建 / 披露 / 残差 / 容差 / within / matches"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [55, 57, 60, 61], "what": "冻结期望与容差"},
        {"file": "evidence/I-10-A/historical_mapping_probe.json", "lines": [185, 198], "what": "probe 计数"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [1103, 1211, 1253], "what": "D 段"},
        {"file": "source_extracts/HK-XIAOMI-2025_decoded.txt", "lines": [1404, 1436, 17790], "what": "出货量 / ASP / 附註5 分部收入行"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [85, 88, 90, 122], "what": "手算与容差依据"},
    ],
    "XM-EV-M03": [
        {"file": MANIFEST_FILE, "lines": [152, 155, 156, 157, 158], "what": "status=adopted / case_id / model / scope"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [301, 302, 303, 305, 306, 307], "what": "复建 / 披露 / 残差 / 容差 / within / matches"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [71, 73, 76, 77], "what": "冻结期望与容差"},
        {"file": "evidence/I-10-A/historical_mapping_probe.json", "lines": [231, 244], "what": "probe 计数"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [1261, 1380, 1409], "what": "D 段"},
        {"file": "source_extracts/HK-XIAOMI-2025_decoded.txt", "lines": [1582, 1610], "what": "交付量 / 每輛 ASP"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [95, 96, 98, 100, 123], "what": "手算与容差依据"},
    ],
    "MS-PBP-M05": [
        {"file": MANIFEST_FILE, "lines": [188, 191, 194, 196], "what": "status=adopted / case_id / scope / DE_status"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [1417, 1425, 1447, 1479], "what": "D 段 4 字段 missing、zero_filled=false"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [348, 349, 350, 351, 352], "what": "E_status / stop_reason / level1=null / residual=null"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [86, 87, 88], "what": "冻结期望 = STOP / not_run"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [104, 109, 110, 111], "what": "冻结期望：E 不可执行"},
        {"file": "execution_v2/card_I-10-A.md", "lines": [26, 29], "what": "停止条款3 与验收"},
    ],
    "MS-IC-M06": [
        {"file": MANIFEST_FILE, "lines": [204, 207, 210, 212], "what": "status=adopted / case_id / scope / DE_status"},
        {"file": "evidence/I-10-A/disclosure_mapping.json", "lines": [1527, 1535, 1551, 1570], "what": "D 段 3 字段 missing、zero_filled=false"},
        {"file": "evidence/I-10-A/historical_reconciliation.json", "lines": [358, 359, 360, 361, 362], "what": "E_status / stop_reason / level1=null / residual=null"},
        {"file": "evidence/I-10-A/oracle_expected.json", "lines": [97, 98, 99], "what": "冻结期望 = STOP / not_run"},
        {"file": "evidence/I-10-A/oracle.md (I-10-A)", "lines": [104, 109, 110, 111], "what": "冻结期望：E 不可执行"},
        {"file": "execution_v2/card_I-10-A.md", "lines": [26, 29], "what": "停止条款3 与验收"},
    ],
}

GRANTED = ["ZJ-MIN-M09", "ZJ-SMT-M09", "XM-PHONE-M03", "XM-EV-M03"]
STOPPED = ["MS-PBP-M05", "MS-IC-M06"]

# ---------------------------------------------------------------- build
out = json.loads(json.dumps(src, ensure_ascii=False))   # deep copy, order preserved

for idx, cid in enumerate(SRC_CASE_IDS):
    meta = CASE_META[cid]
    granted = cid in GRANTED
    da = out["cases"][cid]["disclosure_adaptation"]
    if granted:
        da["status"] = "mapped"
        da["prepared_state"] = "adaptation_complete_SIGNED"
        da["signed"] = True
    else:
        # fail-closed: status / prepared_state / signed stay exactly as in the sealed source
        assert da["status"] == "unmapped" and da["signed"] is False
    da["reviewer_determination"] = {
        "determination": "granted_scoped" if granted else "not_granted_STOP_DISCLOSURE_ADAPTATION",
        "qualification_granted": granted,
        "determination_signed": True,
        "role": ROLE,
        "role_label": ROLE_LABEL,
        "implementer_signed": False,
        "date": STATION_DATE,
        "date_basis": "UTC 日期；写入时刻见 provenance.signed_at_utc / provenance.signed_at_local",
        "decision_sha256": DECISION_SHA,
        "decision_sha256_preimage": (
            "UTF8-no-BOM(source_sha256 of evidence/I-10-A/disclosure_qualification.json) "
            "+ 0x0A + UTF8-no-BOM(ruling_line)，无尾随换行"),
        "decision_sha256_preimage_bytes": len(PREIMAGE),
        "ruling_text": RULING_LINE,
        "authorized_by": AUTHORIZED_BY,
        "c7_source": C7_SOURCE,
        "basis_line_file": MANIFEST_FILE,
        "basis_lines": meta["basis_lines"],
        "basis_documents": BASIS_DOCS[cid],
        "period": meta["period"],
        "reason": meta["reason"],
        "permits_disclosure": meta["permits"],
        "forbids_disclosure": meta["forbids"],
        "evidence": EVIDENCE_BLOCK[cid],
        "actuarial_reviewer": "not_applicable_with_reason",
        "actuarial_reviewer_reason": "三家公司均无保险报告分部（accounting_decision.md L102-L106, AD-9；M23 全部 not_selected）",
        "releases_nothing": True,
        "does_not_claim_I11B_acceptance": True,
    }

now_utc = datetime.now(timezone.utc)
out["provenance"] = {
    "provenance_schema": "disclosure_qualification_version_provenance/1",
    "version": "disclosure_adaptation_v2",
    "supersedes_file": SRC_REL,
    "supersedes_sha256": SRC_SHA,
    "supersedes_bytes": SRC_BYTES,
    "new_file_sha256": None,
    "new_file_sha256_note": (
        "自指不可自证：本文件 sha256 不能写入本文件自身；实测值由本工位写后外部复算，"
        "见同目录 handoff.json 的 written_files"),
    "modified_indices": [0, 1, 2, 3, 4, 5],
    "modified_case_ids": SRC_CASE_IDS,
    "modified_fields": [
        "cases[*].disclosure_adaptation.status            （仅 4 个授予条目 unmapped -> mapped）",
        "cases[*].disclosure_adaptation.prepared_state     （仅 4 个授予条目 ..._UNSIGNED -> ..._SIGNED）",
        "cases[*].disclosure_adaptation.signed             （仅 4 个授予条目 false -> true）",
        "cases[*].disclosure_adaptation.reviewer_determination （6 条全部新增：4 授予 + 2 不授予）",
        "provenance                                        （本文件新增顶层键）",
    ],
    "unchanged_indices": [],
    "qualification_promoted_indices": [0, 1, 2, 3],
    "qualification_retained_unmapped_indices": [4, 5],
    "unchanged_top_level_keys": [
        "artifact", "card", "attempt_id", "three_qualifications_are_independent",
        "company_level", "carries", "card_grants",
    ],
    "unchanged_case_keys": ["company_id", "segment", "model_id", "formula", "accuracy"],
    "unchanged_regions_note": (
        "除 cases[*].disclosure_adaptation 与本 provenance 之外的全部内容逐字节保持；"
        "六个 STOP/授予条目中的 signature_authority、implementer_never_signs、scope 三字段亦逐字保持；"
        "MS-PBP-M05 / MS-IC-M06 的 status=unmapped、prepared_state=partial_STOP_DISCLOSURE_ADAPTATION、"
        "signed=false 三项资格字段未被改动（qualification_retained_unmapped_indices=[4,5]）。"
        "check_signoff.py G2 以 CR 归一化后的字节级对比机器核验。"),
    "line_ending_note": (
        "源文件为 CRLF（8603 B 中 CR=214）；本新版本按工位纪律写为 UTF-8 无 BOM + LF + indent=1，"
        "与源同形（indent=1、ensure_ascii=false、键序不变）；CR 归一化后除 6 个 "
        "disclosure_adaptation 对象与新增 provenance 外逐字节相等。"),
    "decision_sha256": DECISION_SHA,
    "decision_sha256_preimage": (
        "UTF8-no-BOM(6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb) "
        "+ 0x0A + UTF8-no-BOM(ruling_line)，无尾随换行"),
    "decision_sha256_preimage_bytes": len(PREIMAGE),
    "ruling_text": RULING_LINE,
    "ruling_text_location": "oracle.md / ruling.md §4.3 的 --- BEGIN/END C7 RULING TEXT --- 标记之间（逐字同值）",
    "adjudicated_by": "industry_or_accounting_reviewer_non_implementer（行业/会计专业 reviewer · 非实现者）",
    "authorized_by": AUTHORIZED_BY,
    "c7_source": C7_SOURCE,
    "written_by_station": "execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01",
    "signed_at_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "signed_at_local": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "sealed_attempt_modified": False,
    "releases_nothing": True,
    "does_not_claim_I11B_acceptance": True,
    "implementer_signed": False,
    "implementer_never_signs_acceptance": True,
    "signatures_produced": {"granted": 4, "not_granted": 2, "determinations_total": 6},
}

payload = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
data = payload.encode("utf-8")
if data.startswith(b"\xef\xbb\xbf"):
    raise SystemExit("FATAL: BOM present")
if b"\r" in data:
    raise SystemExit("FATAL: CR present (station requires LF)")
with open(OUT, "wb") as fh:
    fh.write(data)

# ---------------------------------------------------------------- post-write verification
with open(OUT, "r", encoding="utf-8") as fh:
    back = json.load(fh)
if list(back["cases"].keys()) != SRC_CASE_IDS:
    raise SystemExit("FATAL: case key set/order changed")
if back["provenance"]["decision_sha256"] != DECISION_SHA:
    raise SystemExit("FATAL: decision_sha256 mismatch after write")

# re-extract ruling line from oracle.md and recompute (post-write recompute #1)
line2 = extract_ruling_line(ORACLE)
pre2 = SRC_SHA.encode("ascii") + b"\n" + line2
sha2 = hashlib.sha256(pre2).hexdigest()
if sha2 != DECISION_SHA:
    raise SystemExit("FATAL: post-write decision_sha256 recompute mismatch")

print("OK build_v2.py")
print("  adopted_cases            =", ADOPTED_IDS)
print("  source_sha256            =", SRC_SHA, SRC_BYTES, "B")
print("  ruling_line_bytes        =", len(RULING_LINE_B))
print("  preimage_bytes           =", len(PREIMAGE))
print("  decision_sha256          =", DECISION_SHA)
print("  post_write_recompute     =", sha2, "MATCH" if sha2 == DECISION_SHA else "MISMATCH")
print("  signed_at_utc            =", out["provenance"]["signed_at_utc"])
print("  out_bytes                =", len(data))
print("  out_sha256               =", hashlib.sha256(data).hexdigest())
sys.exit(0)
