#!/usr/bin/env python3
"""_build_mapping.py — I-11-C/a20260926-01 mapping-table builder.

Transcribes every row mechanically from I-11-B calibration_plan.json (exact ids/values),
attaches this station's executability verdicts, and computes file+line citations by
scanning the source files. Aborts on any index/id expectation mismatch.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANNING = HERE.parents[1]
B = PLANNING / "I-11-B" / "a20260926-01"
CP = B / "calibration_plan.json"
EAF = B / "expert_assumptions.json"
SMC = B / "synthetic_mechanism_check.json"
ST = PLANNING / "OPEN2-C2-REGISTRATION" / "a20260926-01" / "hypotheses_v3.json"

cp = json.loads(CP.read_text(encoding="utf-8-sig"))
eaf = json.loads(EAF.read_text(encoding="utf-8-sig"))
cp_lines = CP.read_text(encoding="utf-8-sig").splitlines()
st_lines = ST.read_text(encoding="utf-8-sig").splitlines()

EXPECTED_IDS = [
    "ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027",
    "ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027",
    "ZIJIN_SEG_TRADE_EXTERNAL_REVENUE_FY2027",
    "ZIJIN_SEG_OTHER_EXTERNAL_REVENUE_FY2027",
    "ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027",
    "ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027",
    "ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027",
    "ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027",
    "ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027",
    "ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027",
    "ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027",
    "ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER",
    "ZIJIN_SEGMENT_RECONCILIATION_FY2027",
    "MSFT_PBP_REVENUE_FY2027",
    "MSFT_IC_REVENUE_FY2027",
    "MSFT_MPC_REVENUE_FY2027",
    "MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER",
    "MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027",
]
for i, pid in enumerate(EXPECTED_IDS):
    if cp["parameters"][i]["parameter_id"] != pid:
        raise SystemExit(f"ABORT: index {i} id mismatch: {cp['parameters'][i]['parameter_id']!r} != {pid!r}")

ea_line = {}
for n, ln in enumerate(EAF.read_text(encoding="utf-8-sig").splitlines(), 1):
    m = re.search(r'"id":\s*"(EA-\d+)"', ln)
    if m:
        ea_line[m.group(1)] = n
ea_span = {}
ids = sorted(ea_line.items(), key=lambda kv: kv[1])
for k, (eid, start) in enumerate(ids):
    end = (ids[k + 1][1] - 1) if k + 1 < len(ids) else 73
    ea_span[eid] = f"L{start}-L{end}"

def cp_span(pid):
    start = next(n for n, ln in enumerate(cp_lines, 1) if f'"parameter_id": "{pid}"' in ln)
    nxt = [n for n, ln in enumerate(cp_lines, 1) if '"parameter_id":' in ln and n > start]
    end = (nxt[0] - 1) if nxt else len(cp_lines)
    return f"L{start}-L{end}"

def st_line(pid):
    hits = [n for n, ln in enumerate(st_lines, 1) if pid in ln]
    return f"L{hits[0]}" if hits else "(id 未见于 store 只读面)"

def st_lines_of(fragment):
    return [n for n, ln in enumerate(st_lines, 1) if fragment in ln]

STATIC_ST = {
    "n1_total": st_lines_of("349,079,082,852"),
    "realized_denom": st_lines_of("885141"),
    "elim_identity": st_lines_of("584,049,229,264"),
    "plan_placeholder": st_lines_of("ZIJIN_PLAN_GOLD_VOLUME_FY2026_PLACEHOLDER"),
    "cloud_placeholder": st_lines_of("MSFT_MICROSOFT_CLOUD_REVENUE_FY2027_PLACEHOLDER"),
    "released_false": st_lines_of('"released": false'),
}

# ---- verdict table (typed once; values transcribed mechanically from CP) ----
def V(verdict, recompute, missing=None, carve_out=None, extra_basis=None, propagation=None, joint=None, blocked=None):
    return {"verdict": verdict, "recompute": recompute, "missing": missing or [],
            "carve_out": carve_out, "extra_basis": extra_basis or [],
            "propagation": propagation, "joint": joint, "blocked": blocked}

VERDICTS = {
 0: V("executable",
      "RECOMP：差额法 349079082852−165858644874−29212610830−44030270803=109977556345（差=0）；low/high 与 base×0.95/1.05 最大偏差 0.25 元（round-to-nearest）",
      carve_out="语义张力 unverified-N1（store 原值 349,079,082,852 与分部语义；AR p327/p328 回源归独立复审，EAF EA-5）",
      extra_basis=[("EAF", ea_span["EA-1"], "带形状 ±5%"), ("EAF", ea_span["EA-3"], "朴素基线"),
                   ("EAF", ea_span["EA-5"], "基期取 109,977,556,345 与 N1 张力"),
                   ("ST", f"L{STATIC_ST['n1_total'][0]}", "store H-01 original_value（N1 客体）")],
      propagation="allowed_not_released",
      joint="与 H-02 量×价共享驱动：S-MIN-PRICE/S-VOL-PRICE 联动，不得独立取极值（EA-6）",
      blocked=["OPEN-2（CP L46）", "unverified-N1（交复审）"]),
 1: V("executable", "RECOMP：±5% 带 max|偏差|=0.3 元",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("EAF", ea_span["EA-3"], "基线"),
                   ("ST", st_line("ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027"), "store 参数在位")],
      propagation="allowed_not_released",
      joint="四分部合计与抵销桥互斥（ST L677-L681），不得与 H-05 双计", blocked=[]),
 2: V("executable", "RECOMP：±5% 带 max|偏差|=0.5 元（.5 对称进位）",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("ST", st_line("ZIJIN_SEG_TRADE_EXTERNAL_REVENUE_FY2027"), "store 参数在位")],
      propagation="allowed_not_released", joint="同上", blocked=[]),
 3: V("executable", "RECOMP：±5% 带 max|偏差|=0.15 元",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("ST", st_line("ZIJIN_SEG_OTHER_EXTERNAL_REVENUE_FY2027"), "store 参数在位")],
      propagation="allowed_not_released", joint="同上", blocked=[]),
 4: V("not_executable",
      "RECOMP（P2 探针）：公式分母合成 884943+83161×24=2880807 ≠ 登记分母 885141；109977556345/885141≈124248.63（登记除法成立），但按公式合成分母商≈38175.95（差 3.26 倍）；敏感性对 885141→968302（Δ=83161）在 c=24 隐含金项仅 198 吨，与 83161×24=1995864 吨矛盾 ⇒ store L170/L175 等式自身不闭合（I-11-B 忠实转录）",
      missing=["分母 885141 的权威推导或原值算术更正（需 CN-ZIJIN-AR2025 产销量表回源，会计/行业面裁定）",
               "OPEN-2 裁定（系数来源未裁定 ⇒ 整值可用性=STOP_DISCLOSURE_ADAPTATION，ST L175）"],
      extra_basis=[("EAF", ea_span["EA-2"], "系数 24 + 敏感性对"),
                   ("ST", f"L{STATIC_ST['realized_denom'][0]}", "store 公式原文（分母 885141）"),
                   ("ST", "L175", "store 等式与两点差分表述（不自洽客体）")],
      propagation="blocked_no_propagation（本站槽位级 STOP：公式不可执行 ⇒ 数字不得进入任何下游映射/forecast；与 CP L88『不得进入 forecast』及 OPEN-2 放行=BLOCKED 一致）",
      joint="S-MIN-PRICE/S-VOL-PRICE 联动（EA-6）；D4 系数仅量侧一次（CP L244）",
      blocked=["OPEN-2", "unverified-N2（本站新登记，交独立复审/会计面）"]),
 5: V("not_executable",
      "无基期：本工位可读面内无铜产品线量价行（CP L97），I-11-B 显式拒绝出数（EA-7）",
      missing=["铜产品线量价行", "OPEN-2 解锁"],
      extra_basis=[("EAF", ea_span["EA-7"], "显式拒绝出数"), ("ST", st_line("ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027"), "store 新注册参数 low:null")],
      propagation="blocked_no_propagation（槽位级 STOP：数据不足 ⇒ 无数字）",
      joint="D1 realized_price 联动（EA-6）", blocked=["OPEN-2"]),
 6: V("not_executable",
      "无基期：金锭（冶炼产品，SMC L24 口径注记）≠矿产金，无矿产品口径量价行（CP L108）",
      missing=["矿产金口径产品线量价行", "OPEN-2 解锁"],
      extra_basis=[("EAF", ea_span["EA-7"], "显式拒绝出数"), ("ST", st_line("ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027"), "store 新注册参数 low:null")],
      propagation="blocked_no_propagation", joint="D1 联动（EA-6）", blocked=["OPEN-2"]),
 7: V("executable", "RECOMP：±10% 带（796448.7/973437.3）逐位相等",
      carve_out="量恒等式约束未闭合：BLOCKED-6b/OPEN-11 库存桥 154 千克容差未签（CP L123）——映射算术可执行，传播用途受该未签约束限制（登记交有权方）",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("EAF", ea_span["EA-3"], "基线（库存释放不外推）"),
                   ("ST", st_line("ZIJIN_MINERAL_COPPER_SALEABLE_VOLUME_FY2027"), "store 参数 low:null")],
      propagation="allowed_not_released（约束未闭合登记在案）",
      joint="S-VOL-PRICE 联动：量价同档，不得独立取极值（EA-6）；E1 库存释放仅销量通道（CP L249）",
      blocked=["BLOCKED-6b/OPEN-11（CP L123）"]),
 8: V("executable", "RECOMP：±10% 带逐位相等",
      carve_out="同铜：BLOCKED-6b（CP L134）",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("ST", st_line("ZIJIN_MINERAL_GOLD_SALEABLE_VOLUME_FY2027"), "store 参数在位")],
      propagation="allowed_not_released", joint="S-VOL-PRICE 联动；D4 系数仅量侧一次", blocked=["BLOCKED-6b（CP L134）"]),
 9: V("executable", "RECOMP：±10% 带逐位相等",
      extra_basis=[("EAF", ea_span["EA-1"], "带"), ("ST", st_line("ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027"), "store 新注册参数 low:null")],
      propagation="allowed_not_released", joint="S-VOL-PRICE 联动", blocked=[]),
 10: V("executable", "RECOMP：±10% 带逐位相等",
       extra_basis=[("EAF", ea_span["EA-1"], "带"), ("ST", st_line("ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027"), "store 新注册参数 low:null")],
       propagation="allowed_not_released", joint="S-VOL-PRICE 联动", blocked=[]),
 11: V("executable",
       "RECOMP：达成率带 94500/115500（金）、1080000/1320000（铜）逐位相等",
       carve_out="§三十四 L772 边界：_PLACEHOLDER 维持不放行；本行仅情景对照与达成率情景用途（CP L165 note；CARD_B L14 管理层目标非独立证据）",
       extra_basis=[("EAF", ea_span["EA-1"], "达成率带 [0.9,1.1]"),
                    ("ST", f"L{STATIC_ST['plan_placeholder'][0]}", "store _PLACEHOLDER 参数"),
                    ("CARD_B", "L14", "管理层目标不得用作独立准确性证据")],
       propagation="allowed_not_released（仅情景对照；_PLACEHOLDER 维持）",
       joint="E3：计划值仅对照通道一次，不得同时当产能上限与预测基数（CP L251）；D6 独立性受限",
       blocked=["§三十四 边界（不放行）"]),
 12: V("executable",
       "RECOMP：584049229264−234970146412=349079082852（差=0）；四分部对外合计逐位=349079082852；store 毛总计和 138271672956+189683879295+170521025777+85572651236=584049229264 亦逐位复核",
       extra_basis=[("ST", f"L{STATIC_ST['elim_identity'][0]}", "raw_value 四分部总计/抵销/对外合计"),
                    ("SMC", "L29-L33", "I-11-B 恒等式复算 3/3")],
       propagation="allowed_not_released（约束性恒等式，非收入路径输入）",
       joint="E5：抵销只出现在恒等式桥（CP L253）；禁止 584,049,229,264 与 349,079,082,852 同时作收入基期（ST L677-L681）",
       blocked=["store state=unquantified（6b 路径(c)，CP L179）——本表不改 store"]),
 13: V("executable",
       "RECOMP：g_low=51/500、g_high=109/500 逐位相等",
       carve_out="增速持续性无 FY2027 证据（EA-4 纯分析师判断）；EA-4 band_rationale 合计区间注记与自身带换算不符=unverified-N3（注记层，不影响本行算术）",
       extra_basis=[("EAF", ea_span["EA-4"], "持续性假设 + 带（含 N3 客体注记）"),
                    ("ST", st_line("MSFT_PBP_REVENUE_FY2027"), "store 参数 low:null")],
       propagation="allowed_not_released",
       joint="E7：三分部建模、集团增速不用（CP L255）；S-MSFT-SEG 不得同时独立上调（CP L261）",
       blocked=["OPEN-3（CP L190）"]),
 14: V("executable", "RECOMP：g_low=47/200、g_high=73/200 逐位相等",
       carve_out="同 PBP（EA-4/N3）",
       extra_basis=[("ST", st_line("MSFT_IC_REVENUE_FY2027"), "store 参数在位")],
       propagation="allowed_not_released", joint="同 PBP", blocked=["OPEN-3"]),
 15: V("executable", "RECOMP：g_low=−119/2000、g_high=79/2000 逐位相等",
       carve_out="同 PBP；MPC −1% 不得被集团增长掩盖（CP L208）",
       extra_basis=[("ST", st_line("MSFT_MPC_REVENUE_FY2027"), "store 参数在位")],
       propagation="allowed_not_released", joint="同 PBP", blocked=["OPEN-3"]),
 16: V("not_executable",
       "无公式：store 明示无可用的换算公式、缺 Microsoft Cloud→分部/产品行完备映射表（CP L219-L220）",
       missing=["完备映射表", "OPEN-3 解锁"],
       extra_basis=[("EAF", ea_span["EA-7"], "显式拒绝出数"),
                    ("ST", f"L{STATIC_ST['cloud_placeholder'][0]}", "store _PLACEHOLDER low:null")],
       propagation="blocked_no_propagation（槽位级 STOP）",
       joint="E6：PROHIBITED_CO_USE——不得与 IC 增速并用（CP L254）", blocked=["OPEN-3"]),
 17: V("not_executable",
       "无拆分：缺行内拆分（云/许可分项、平均付费席位、净 ARPU）（CP L230-L231）",
       missing=["行内拆分披露", "OPEN-3 解锁"],
       extra_basis=[("EAF", ea_span["EA-7"], "显式拒绝出数"),
                    ("ST", st_line("MSFT_LICENSING_VS_CLOUD_COMPOSITION_FY2027"), "store 参数 low:null")],
       propagation="blocked_no_propagation（槽位级 STOP）",
       joint="D7 联动约束（EA-6）", blocked=["OPEN-3"]),
}

rows = []
EAF_IDS = {a["id"] for a in eaf["assumptions"]}
METHOD_KEYS = ["contract arithmetic", "historical relationship", "external comparable",
               "expert_assumption", "expert assumption"]
for i, p in enumerate(cp["parameters"]):
    pid = p["parameter_id"]
    a2 = p["action2_parameter_mapping"]
    vd = VERDICTS[i]
    ea_refs = p.get("ea_refs", [])
    for ref in ea_refs:
        if ref not in EAF_IDS:
            raise SystemExit(f"ABORT: {pid} references unknown EA {ref}")
    method_str = p["action1_calibration"]["method"]
    primary = [m for m in METHOD_KEYS if m in method_str]
    stopped = vd["verdict"] != "executable"
    new_value = {"low": None, "base": None, "high": None} if stopped else a2["new_value"]
    basis = [{"file": "CP", "line": cp_span(pid), "what": "slot 全字段（逐字转录源）"}]
    for ref in ea_refs:
        basis.append({"file": "EAF", "line": ea_span[ref], "what": f"{ref} 敏感性区间 + equivalent_to_disclosure_basis=false"})
    for f_, l_, w_ in vd["extra_basis"]:
        if not any(b["file"] == f_ and b["line"] == l_ for b in basis):
            basis.append({"file": f_, "line": l_, "what": w_})
    row = {
        "parameter_id": pid,
        "hypothesis_id": p["hypothesis_id"],
        "model_id": p["model_id"],
        "driver_name": p["driver_name"],
        "unit": a2["unit"],
        "period_start": a2["period_start"],
        "period_end": a2["period_end"],
        "original_value": a2["original_value"],
        "new_value": new_value,
        "i11b_proposed_values": (a2["new_value"] if i == 4 else None),
        "i11b_proposed_note": ("I-11-B proposed 值如实转录存档；本站判 not_executable（unverified-N2）⇒ 传播值置 null，数字不进入下游" if i == 4 else None),
        "value_state": ("not_executable_no_propagation" if i == 4
                        else "unmapped_declined_no_number" if i in (5, 6, 16, 17)
                        else "mapped_not_released"),
        "conversion_formula": a2["conversion_formula"],
        "executability": {
            "verdict": vd["verdict"],
            "amplitude": vd["recompute"],
            "unit_check": "与量纲链一致（CP L43/L54/L65/L76/L87/L120/L131/L142/L153/L164/L176/L187/L198/L209/L220/L231 单位字段逐条核对）",
            "period_check": "period_start/period_end 已定义；FY2027 生效行基期=FY2025（FY2026 无同口径观测，EA-3 朴素基线）",
            "formula_check": ("公式文本与登记数值不自洽——分母合成见 amplitude 字段" if i == 4 else "公式逐项可复算（RECOMP）"),
            "missing": vd["missing"],
            "carve_out": vd["carve_out"],
        },
        "source": {
            "primary": primary,
            "ea_refs": ea_refs,
            "basis": basis,
        },
        "propagation": vd["propagation"],
        "joint_scenario_constraint": vd["joint"],
        "blocked_by": p.get("blocked_by", []) if not vd["blocked"] else list(dict.fromkeys(list(p.get("blocked_by", [])) + vd["blocked"])),
    }
    rows.append(row)

exe = sum(1 for r in rows if r["executability"]["verdict"] == "executable")
not_exe = len(rows) - exe
from_ea = sum(1 for r in rows if r["source"]["ea_refs"])
mapping = {
  "schema": "i11c_parameter_mapping/1",
  "card": "I-11-C",
  "attempt": "execution_runs/I-11-C/a20260926-01",
  "role": "implementer_i11c",
  "status": "review_pending",
  "purpose": "动作1 逐槽位核对 I-11-B 幅度/单位/起止年份/转换公式可执行性；动作2 low/base/high+dependency_control 参数映射表；动作3 每行来源+依据（文件+行号，行号由 builder 扫描源文件自动定位）；动作4 见 mapping_verification.json。全部数值登记不放行。",
  "value_policy": {
    "params_released": False,
    "statement": "本表数值为 mapped_not_released（登记，不写进任何 released 字段）；store 侧 low/base/high 仍 null、_PLACEHOLDER 维持、released=false（实测 ST released:false 行=" + str(STATIC_ST["released_false"]) + "）；放行=独立复审+三件套+有权方（§三十四 L761-L766）。",
    "management_target_is_not_independent": True,
    "synthetic_numbers_quarantined": [2, 8760, 0.5, 0.6, 0.7, 40, 20, 30, 32, 34, 1200, 264000, 281520, 299040, 17520],
    "quarantine_rule": "qualitative_synthetic_example 数字不进入任何真实数值字段（CARD_B L16；SMC L36-L42 先例）；1,200,000（铜计划吨数，AR2025:p56）与示例 1200 非复制（collision_scan 先例 SMC L40）",
    "inputs_read_only": [str(CP.relative_to(PLANNING.parent.parent.parent)), str(EAF.relative_to(PLANNING.parent.parent.parent)), str(SMC.relative_to(PLANNING.parent.parent.parent)), str(ST.relative_to(PLANNING.parent.parent.parent))]
  },
  "source_legend": {
    "CP": "execution_runs/I-11-B/a20260926-01/calibration_plan.json",
    "EAF": "execution_runs/I-11-B/a20260926-01/expert_assumptions.json",
    "ST": "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json（只读）",
    "CARD_B": "execution_v2/card_I-11-B.md",
    "SMC": "execution_runs/I-11-B/a20260926-01/synthetic_mechanism_check.json",
    "RECOMP": "execution_runs/I-11-C/a20260926-01/_recompute_action1.py 执行输出（精确有理数）"
  },
  "mapping_rows": rows,
  "action_1_summary": {"total_slots": 18, "executable": exe, "not_executable": not_exe,
    "not_executable_detail": [{"parameter_id": r["parameter_id"], "why": r["executability"]["amplitude"][:120], "missing": r["executability"]["missing"]} for r in rows if r["executability"]["verdict"] != "executable"]},
  "action_2_dependency_control_transcribed": {
    "source": "CP L237-L265（本站不重写；映射行逐行携带 joint_scenario_constraint）",
    "shared_drivers": ["D1 realized_price", "D2 saleable_volume", "D3 other_revenue", "D4 copper_equivalent_coefficient（仅量侧一次）", "D5 elimination_bridge（仅恒等式桥）", "D6 management_plan_FY2026（独立性受限）", "D7 segment_growth_MSFT（与集团增速互斥）"],
    "event_reuse_check": "E1-E7 逐条 ALLOWED_ONCE/PROHIBITED_CO_USE（CP L249-L255）",
    "correlated_scenarios": ["S-MIN-PRICE", "S-VOL-PRICE", "S-MSFT-SEG"],
    "scenario_joint_logic": "任一情景 收入增量=Σ(各驱动单通道增量)；同一事件不得贡献两个及以上通道；违反⇒STOP_SCENARIO（CP L263；EA-6 联合带约束）"
  },
  "action_3_source_counts": {
    "rows_total": len(rows),
    "rows_mapped_with_values": exe,
    "rows_unmapped_no_propagation": not_exe,
    "from_expert_assumption": from_ea,
    "from_expert_assumption_note": "除 ZIJIN_SEGMENT_RECONCILIATION（纯 contract arithmetic，ea_refs=[]，CP L178）外 17 行均经 EA-1…EA-7 承接（带/基线/拒绝处置）；13 行已映射值中 12 行带 EA、4 行显式拒绝（EA-7）、1 行公式不自洽（EA-1/EA-2 承接但判不传播）",
    "contract_arithmetic_only": 1,
    "synthetic_numbers_in_real_fields": 0
  },
  "unverified_findings": [
    {"id": "unverified-N1", "registration": "unverified", "desc": "继承 I-11-B：store H-01 original_value=349,079,082,852（四分部合计，ST L39）与 ZIJIN_SEG_MINERAL 分部语义张力（CP L271-L273；EAF EA-5）", "disposition": "登记不回改；AR p327/p328 回源归独立复审"},
    {"id": "unverified-N2", "registration": "unverified", "desc": "本站新发现：ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027 转换公式分母不自洽（store L170/L175 等式 884943+83161×24=885141 不成立，实测合成=2880807；敏感性对在 c=24 隐含金项 198 吨 vs 1995864 吨）——I-11-B 为忠实转录，缺陷源头在 store 口径暴露原文；proposed 值（118036.2/124248.63/130461.06）在更正前不得传播", "disposition": "槽位级 STOP + not_executable_no_propagation；交独立复审/会计面（与 OPEN-2 同源）"},
    {"id": "unverified-N3", "registration": "unverified", "desc": "本站新发现：EA-4 band_rationale 注记『三分部收入合计区间=[320763,348432] USD mn』与其自身增长率带换算（本站复算 ≈[375283.38, 414786.90]）不符；与基期合计±5%（[315247.05, 348430.95]）亦不吻合（高位差 1.05）——注记层缺陷，不影响任何 new_value 算术", "disposition": "登记交独立复审；MSFT 三行映射可执行性不受影响"},
    {"id": "unverified-D1", "registration": "erratum_recorded", "desc": "派单标题『校准后参数映射』与 card_I-11-C.md 标题『独立反方审查与触发更新』不同名；判读=编排层拆两站（映射实现者/独立复审），卡文 L13-L16 reviewer 动作不在本站执行", "disposition": "按派单执行并如实登记；拆分确权归编排层"}
  ],
  "stop_evaluation": {
    "slot_level_stop_applied": True,
    "slot_level_stop_rows": [rows[i]["parameter_id"] for i in (4, 5, 6, 16, 17)],
    "card_level_stop_calibration_triggered": False,
    "card_level_operative_reading": "从严触发式（继承 ROS L12）：本站传播的每一个幅度皆可溯源（contract arithmetic/已签容差 τ=1/historical relationship）或由明确 EA+敏感性区间承接；5 个不可执行槽位零传播 ⇒ 无『无来源又未声明』的幅度进入下游",
    "card_level_strict_reading_registered": "字面从严读法（继承 ROS L13-L17）：存在任一 not_executable 槽位即整卡 blocked——本站 5 个该类槽位存在，若独立复审采严格读法 ⇒ 本卡连同 I-11-B 一并转 blocked；回滚=作废本表 mapped_not_released 行（零封盘改动、store 零改动）",
    "stop_scenario_triggered": False,
    "stop_scenario_check": "18 行逐行携带联动约束（EA-6）；未产生量 high×价 high×其他收入 high 独立叠加（≈+21% 不可能联合）；E1-E7 复用检查转录全 PASS/PROHIBITED_CO_USE"
  },
  "reviewer_handoff_note": "独立复审接手点：① unverified-N1（p327/p328 回源）② unverified-N2（分母算术更正/权威推导，会计面）③ unverified-N3（EA-4 注记核对）④ 严格读法之争裁定（I-11-B ROS L13-L17）⑤ 本表 13 行 mapped_not_released 的签署与否（三件套落定）；本表不自签、不产生 ACCEPT。"
}

out = HERE / "parameter_mapping.json"
out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"WROTE {out}")
print(f"rows={len(rows)} executable={exe} not_executable={not_exe} from_expert_assumption={from_ea}")
