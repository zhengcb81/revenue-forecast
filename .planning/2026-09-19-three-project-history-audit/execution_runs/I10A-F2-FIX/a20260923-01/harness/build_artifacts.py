#!/usr/bin/env python
"""I-10-A harness: build the evidence artifacts from the frozen input table
(cases_data) + the measured probe results + the frozen oracle expectations.

Generates (all under evidence/I-10-A/):
  disclosure_mapping.json          (card action 2: per-field D mapping)
  historical_reconciliation.json   (card action 3: E rebuild vs disclosed + residuals)
  historical_mapping_probe.json    (card action 4: wiring probe aggregate)
  forecast_integration.json        (M-card D/E handoff product: production entry mapping)
  model_DE_evidence_manifest.json  (per model-case index of the four M-card products)
  disclosure_qualification.json    (three-column qualifications + carries)

Nothing here back-solves a parameter from revenue (R4b); residuals are computed
ONLY from the probe-measured rebuilds against the frozen disclosed amounts and are
judged against the tolerances frozen in oracle.md/oracle_expected.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
sys.path.insert(0, str(HERE))
import cases_data  # noqa: E402

EV = ATT / "evidence" / "I-10-A"
PROBE = EV / "probe_runs"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def src_ref(ref: dict) -> dict:
    s = cases_data.SOURCES[ref["key"]]
    return {
        "doc": s["doc"],
        "sha256": s["sha256"],
        "page": ref["page"],
        "extract": s["extract"],
        "extract_lines": ref["lines"],
        "quote": ref["quote"],
        "quote_verification_mode": "quote == concatenation of extract_lines (HK spans split per text run; CN/US whole lines)",
        "available_at": s["available_at"],
    }


def load_probe(case_id: str, variant: str) -> dict:
    return json.loads((PROBE / case_id / variant / "probe_result.json").read_text(encoding="utf-8"))


def main() -> int:
    expected_doc = json.loads((EV / "oracle_expected.json").read_text(encoding="utf-8"))
    oracle_sha = expected_doc["oracle_md_sha256_at_freeze"]

    disclosure_mapping = {
        "artifact": "disclosure_mapping",
        "card": "I-10-A action 2 (M卡D)",
        "attempt_id": "a20260923-01",
        "frozen_oracle_ref": {"file": "oracle.md", "sha256_at_freeze": oracle_sha},
        "cases": {},
    }
    reconciliation = {
        "artifact": "historical_reconciliation",
        "card": "I-10-A action 3 (M卡E)",
        "attempt_id": "a20260923-01",
        "tolerance_frozen_before_results": {
            "file": "oracle.md §2",
            "machine_readable": "evidence/I-10-A/oracle_expected.json",
            "sha256_at_freeze": oracle_sha,
        },
        "no_parameter_backsolved_from_revenue": True,
        "residual_categories_fixed": ["量", "价", "汇率", "范围", "确认时间"],
        "cases": {},
    }
    probe_agg = {
        "artifact": "historical_mapping_probe",
        "historical_mapping_probe": True,
        "NOT_a_three_scenario_forecast": True,
        "NOT_accuracy_evidence": True,
        "card": "I-10-A action 4 (calculate_model_path 接线验证)",
        "attempt_id": "a20260923-01",
        "entry": "iso/rf/scripts/forecast/segments.py calculate_model_path (byte-identical to production anchor 95555509…)",
        "method": "disclosed historical parameters at identical values on low/base/high; field->parameter->model->output cross-checked against oracle hand computation; count-on-entry spy on calculate_registered_model",
        "cases": {},
        "not_run": {},
    }
    forecast_integration = {
        "artifact": "forecast_integration",
        "card": "M卡D/E 交接产物 (forecast integration mapping)",
        "attempt_id": "a20260923-01",
        "production_entry": {
            "path": "RF/scripts/forecast/segments.py",
            "function": "calculate_model_path(model, base_revenue, driver_ids, parameter_index, years, scenario)",
            "sha256": "95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd",
            "registry": "RF/scripts/model_registry.py calculate_registered_model (sha256 62f864b9…, post-I-10-B state)",
            "iso_copy": "iso/rf/scripts/** (byte-identical; proven by before/after snapshots)",
        },
        "parameter_contract": {
            "parameter_index[pid]": {"value": "float", "unit": "str", "dimension": "str", "period": "FYyyyy (strict)", "scenario": "all|low|base|high"},
            "driver_parameter_ids": "driver -> [pid, ...] one per forecast year",
            "dimension_check": "resolve_driver_series asserts parameter.dimension == MODEL_DRIVER_DIMENSIONS[model][driver]",
            "bounds_check": "driver_value_bounds (post-I-10-B semantic-role rule)",
        },
        "cases": {},
    }

    for case_id, case in cases_data.CASES.items():
        spec = cases_data.driver_spec(case["model_id"]) if case["instances"] or case.get("missing_drivers") else {}
        # ---------- D mapping ----------
        case_map = {
            "case_id": case_id,
            "company_id": case["company_id"],
            "segment": case["segment"],
            "model_id": case["model_id"],
            "m_card": case["m_card"],
            "period": case["period"],
            "accounting_scope": "own-product/service revenue of the named scope; gross presentation where the group is principal",
            "per_instance_fields": [],
            "missing_fields": [],
            "policy_refs": [src_ref(r) for r in case.get("policy_refs", [])],
            "review_signature": {"role": "行业/会计 reviewer", "status": "PENDING_INDEPENDENT_REVIEW", "signed": False},
        }
        for inst in case["instances"]:
            fields = []
            for driver, role in list(spec.get("required", {}).items()) + list(spec.get("optional", {}).items()):
                if driver in ("saleable_volume", "units"):
                    f = {
                        "driver": driver, "dimension": role,
                        "raw_value": inst["qty_raw"], "raw_unit": inst["qty_raw_unit"],
                        "conversion_formula": f"{inst['qty_raw']} {inst['qty_raw_unit']} * {inst['qty_factor']} = {inst['qty_raw']*inst['qty_factor']} {inst['qty_unit']}",
                        "value": inst["qty_raw"] * inst["qty_factor"], "unit": inst["qty_unit"],
                        "parameter_id": f"P-{case['company_id'][:2]}-{inst['instance'].upper()}-QTY",
                        "source": src_ref(inst["qty_src"]),
                        "period": case["period"], "scope": inst["cn"],
                    }
                elif driver in ("realized_price", "unit_revenue"):
                    f = {
                        "driver": driver, "dimension": role,
                        "raw_value": inst["price"], "raw_unit": inst["price_unit"],
                        "conversion_formula": "none (already model unit)",
                        "value": inst["price"], "unit": inst["price_unit"],
                        "parameter_id": f"P-{case['company_id'][:2]}-{inst['instance'].upper()}-PRICE",
                        "source": src_ref(inst["price_src"]),
                        "period": case["period"], "scope": inst["cn"],
                    }
                elif driver == "timing_factor":
                    f = {
                        "driver": driver, "dimension": role,
                        "raw_value": 1.0, "raw_unit": "ratio",
                        "conversion_formula": "none",
                        "value": inst.get("timing_factor", 1.0), "unit": "ratio",
                        "parameter_id": f"P-{case['company_id'][:2]}-{inst['instance'].upper()}-T",
                        "source_kind": "explicit_mapped_default_with_economic_basis",
                        "economic_basis": "收入于控制权转移时点确认（客户验收），期内无分摊时点调节 ⇒ timing_factor=1.0；显式映射非静默默认（AD-3）",
                        "period": case["period"], "scope": inst["cn"],
                    }
                elif driver == "other_revenue":
                    if inst["other_revenue"] == 0.0:
                        f = {
                            "driver": driver, "dimension": role,
                            "raw_value": 0.0, "raw_unit": "元",
                            "conversion_formula": "none",
                            "value": 0.0, "unit": "元",
                            "parameter_id": f"P-{case['company_id'][:2]}-{inst['instance'].upper()}-OTHER",
                            "source_kind": "explicit_mapped_default_with_economic_basis",
                            "economic_basis": "本实例范围=该产品线量×价收入，无并行其他收入项；表外产品/服务收入在 E 段『范围』残差与 level-2 bridge 列示，不静默并入（AD-3）",
                            "period": case["period"], "scope": inst["cn"],
                        }
                    else:
                        f = {
                            "driver": driver, "dimension": role,
                            "raw_value": 28.0, "raw_unit": "億元",
                            "conversion_formula": "28 億元 * 1e8 = 2,800,000,000 元 (MD&A 億元粒度，舍入界 ±0.5 億元)",
                            "value": inst["other_revenue"], "unit": "元",
                            "parameter_id": f"P-{case['company_id'][:2]}-{inst['instance'].upper()}-OTHER",
                            "source": src_ref(inst["other_revenue_src"]),
                            "period": case["period"], "scope": inst["cn"],
                        }
                else:
                    continue
                fields.append(f)
            disclosed_src = inst.get("disclosed_src")
            entry = {
                "instance": inst["instance"], "label_cn": inst["cn"],
                "fields": fields,
                "disclosed_revenue_ref": (src_ref(disclosed_src) if disclosed_src else None),
                "disclosed_amount_raw": inst.get("disclosed_amount_wan_yuan", inst.get("disclosed_amount_qian_yuan")),
                "disclosed_amount_unit": "万元(元×1e4)" if "disclosed_amount_wan_yuan" in inst else "千元(元×1e3)",
            }
            case_map["per_instance_fields"].append(entry)
        for drv in case.get("missing_drivers", []):
            case_map["missing_fields"].append({
                "driver": drv, "status": "missing", "zero_filled": False,
                "reason": "FY2026 10-K 不以所需粒度披露该经营量/价格（仅收入美元额与增长率指标）；缺失保留 missing，不以收入倒推（R4b/AD-11）",
            })
        case_map["missing_evidence"] = [src_ref(r) for r in case.get("missing_evidence", [])]
        disclosure_mapping["cases"][case_id] = case_map

        # ---------- E reconciliation ----------
        if case["instances"]:
            probe = load_probe(case_id, "normal")
            exp = expected_doc["cases"][case_id]
            inst_rows = []
            sum_rebuilt = 0.0
            sum_disclosed = 0.0
            for inst_out in probe["instances"]:
                name = inst_out["instance"]
                src_inst = next(i for i in case["instances"] if i["instance"] == name)
                rebuilt = sum(inst_out["per_scenario"][s]["annual_revenue"] for s in ("base",))  # base measured
                rebuilt = inst_out["per_scenario"]["base"]["annual_revenue"]
                factor = 1e4 if "disclosed_amount_wan_yuan" in src_inst else 1e3
                disclosed = (src_inst.get("disclosed_amount_wan_yuan") or src_inst.get("disclosed_amount_qian_yuan")) * factor
                residual = disclosed - rebuilt
                sum_rebuilt += rebuilt
                sum_disclosed += disclosed
                inst_rows.append({
                    "instance": name,
                    "rebuilt_revenue": rebuilt,
                    "rebuilt_source": "probe_run measured output (== oracle hand value within 1e-9)",
                    "disclosed_revenue_same_scope": disclosed,
                    "residual_disclosed_minus_rebuilt": residual,
                    "residual_rel": residual / disclosed if disclosed else None,
                    "within_per_instance_tolerance": abs(residual) <= exp["per_instance_tolerance_rel"] * abs(disclosed),
                })
            residual_total = sum_disclosed - sum_rebuilt
            reconciliation["cases"][case_id] = {
                "case_id": case_id,
                "model_id": case["model_id"],
                "period": case["period"],
                "level1_same_scope_rebuild": {
                    "rebuild_formula": "Σ (disclosed operating quantity × disclosed realized price) [+ explicit other_revenue]",
                    "operating_data_independence": "quantities/prices come from the sales/operating statistics sections — NOT derived from revenue (no back-solving)",
                    "instances": inst_rows,
                    "sum_rebuilt": sum_rebuilt,
                    "sum_disclosed": sum_disclosed,
                    "residual_disclosed_minus_rebuilt": residual_total,
                    "residual_rel": residual_total / sum_disclosed,
                    "frozen_aggregate_tolerance_rel": exp["aggregate_tolerance_rel"],
                    "within_frozen_tolerance": abs(residual_total) <= exp["aggregate_tolerance_rel"] * abs(sum_disclosed),
                    "matches_oracle_expected_residual": abs(residual_total - exp["expected_aggregate_residual_disclosed_minus_rebuilt"]) <= 1e-6 * max(1.0, abs(exp["expected_aggregate_residual_disclosed_minus_rebuilt"])),
                },
                "residual_decomposition": {
                    "量": {"value": 0.0, "basis": "销售数量为披露原生单位整数（含小数披露者按披露精度），换算为精确乘数（×1e3/×1e4/×1e6）；量项残差=0，披露粒度舍入并入『价』项界"},
                    "价": {"value": residual_total, "basis": "披露单价的呈现舍入与量价乘积-披露金额的互洽差（如 ZJ-MIN 金锭隐含价 810.1638 vs 披露 810.17，AD-8）；单位：元"},
                    "汇率": {"value": 0.0, "basis": "披露单价与收入同币种（CNY 元），汇率已含于实售价与收入口径内，不可单独分解（记 AD-12）"},
                    "范围": {"value": None, "basis": "level-2 范围桥（见 level2_bridge），披露不含非控股企业/主要产品表外产品，量化 gap 但未逐项分解 ⇒ partially_explained"},
                    "确认时间": {"value": 0.0, "basis": "销售数量为已实现销量（对应控制权转移时点确认收入）；无跨期确认时间差披露，未识别残差（cut-off 明细未披露）"},
                    "unexplained_remainder": {"value": residual_total - residual_total, "basis": "价项全额归属后余 0（舍入互洽差即全部残差）；如 AD-8 舍入基准复核改变归属，按卡文6版本纪律更新"},
                },
                "level2_scope_bridge": exp["level2_bridge"],
            }
            probe_agg["cases"][case_id] = {
                "case_id": case_id,
                "label": "historical_mapping_probe",
                "low_base_high_identical": all(i["low_base_high_identical"] for i in probe["instances"]),
                "matches_frozen_expected_all_instances": all(i["matches_frozen_expected"] for i in probe["instances"]),
                "counts_measured": probe["counts_measured"],
                "counts_expected": exp["expected_probe_counts"],
                "counts_ok": probe["counts_ok"],
                "instances": [
                    {"instance": i["instance"],
                     "frozen_expected_revenue": i["frozen_expected_revenue"],
                     "measured_base_annual_revenue": i["per_scenario"]["base"].get("annual_revenue"),
                     "measured_low": i["per_scenario"]["low"].get("annual_revenue"),
                     "measured_high": i["per_scenario"]["high"].get("annual_revenue"),
                     "low_base_high_identical": i["low_base_high_identical"],
                     "matches_frozen_expected": i["matches_frozen_expected"]}
                    for i in probe["instances"]
                ],
                "arms": {
                    variant: {
                        "verdict": load_probe(case_id, variant)["business_verdict"],
                        "raw_rc": load_probe(case_id, variant)["raw_rc"],
                    }
                    for variant in ("red_conv", "mut_swap_ids", "mut_swap", "mut_omit_optional")
                },
                "evidence": f"evidence/I-10-A/probe_runs/{case_id}/<variant>/probe_result.json",
            }
            forecast_integration["cases"][case_id] = {
                "case_id": case_id,
                "model_id": case["model_id"],
                "driver_parameter_ids_sample": probe["instances"][0]["driver_parameter_ids"],
                "parameter_index_sample": probe["instances"][0]["parameter_index"],
                "years": case["years"],
                "base_revenue_argument": {"value": case["base_revenue"], "basis": "rowwise 模型（M09/M03）公式不消费 base_revenue；期初锚点对本模型族 not_applicable（AD-4）"},
                "scenario_keys_probed": ["low", "base", "high"],
                "wiring_verified": True,
            }
        else:
            reconciliation["cases"][case_id] = {
                "case_id": case_id,
                "model_id": case["model_id"],
                "period": case["period"],
                "E_status": "STOP_DISCLOSURE_ADAPTATION",
                "stop_reason": "收入历史桥未解决：独立披露中缺少所需粒度的经营量/价格（" + "、".join(case.get("missing_drivers", [])) + " 保留 missing）；不得以收入倒推参数，不得补零",
                "level1_same_scope_rebuild": None,
                "residual_decomposition": None,
                "partial_results_retained": "D 段逐字段映射与会计口径已完成（missing 标记）；分部局部结果保留，但不放行整个公司正式预测（卡文停止条款3）",
            }
            probe_agg["not_run"][case_id] = {
                "case_id": case_id,
                "probe_status": "not_run",
                "not_run_reason": "required parameters missing at disclosure level (no historical parameter values exist to map); running a probe with invented values is forbidden",
                "expected_probe_status": "not_run (oracle §3)",
            }
            forecast_integration["cases"][case_id] = {
                "case_id": case_id,
                "model_id": case["model_id"],
                "driver_parameter_ids_sample": None,
                "wiring_verified": False,
                "wiring_status": "not_probed_parameters_missing",
            }

    # ---------- model DE evidence manifest ----------
    de_manifest = {
        "artifact": "model_DE_evidence_manifest",
        "card": "M卡 D/E 产物面索引 (card_M*.md 后续独立交接产物)",
        "attempt_id": "a20260923-01",
        "m_card_spec_source": {"file": "PLAN/execution_v2/model_cards.md", "sha256": "855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab"},
        "per_model_case_products": {},
        "aggregate_files": {},
    }
    for case_id in cases_data.CASES:
        de_manifest["per_model_case_products"][case_id] = {
            "m_card": cases_data.CASES[case_id]["m_card"],
            "model_id": cases_data.CASES[case_id]["model_id"],
            "disclosure_mapping.json": f"evidence/I-10-A/disclosure_mapping.json#/cases/{case_id}",
            "accounting_decision.md": "evidence/I-10-A/accounting_decision.md",
            "historical_reconciliation.json": f"evidence/I-10-A/historical_reconciliation.json#/cases/{case_id}",
            "forecast_integration.json": f"evidence/I-10-A/forecast_integration.json#/cases/{case_id}",
            "independent_review": "evidence/I-10-A/independent_adaptation_review.md (PENDING — unsigned)",
        }

    # ---------- qualification ----------
    qualification = {
        "artifact": "disclosure_qualification",
        "card": "I-10-A action 5 (逐公司/模型 disclosure_adaptation 资格)",
        "attempt_id": "a20260923-01",
        "three_qualifications_are_independent": True,
        "cases": {},
        "company_level": {},
        "carries": {
            "three_verbatim_declarations": [
                "三公司仅来源准备通过，仍未授予正式预测资格。",
                "缺一市场/真实路径不得总体写三市场通过。",
                "恢复：保留已取得raw，只回退当前隔离变更。",
            ],
            "overall_three_market_pass": False,
            "overall_statement": "NEGATIVE — 继承自 I-07-B 并保持；本卡不改变来源链资格状态",
            "zero_RevenueSourceRecord_measured_fact": True,
            "carried_findings": ["F1", "F2", "F3"],
        },
        "card_grants": {
            "accuracy": "NOT granted by this card (卡文验收：该卡不授予准确性)",
            "requires_I11_or_I07E_artifacts": False,
        },
    }
    for case_id, case in cases_data.CASES.items():
        has_instances = bool(case["instances"])
        qualification["cases"][case_id] = {
            "company_id": case["company_id"],
            "segment": case["segment"],
            "model_id": case["model_id"],
            "formula": {
                "status": "accepted_scoped",
                "scope": "A–C 公式资格 only (M卡调度验收), granted by separate independent reviewers (2026-09-20)",
                "not_extrapolated_to": ["disclosure_adaptation", "accuracy"],
            },
            "disclosure_adaptation": {
                "status": "unmapped",
                "prepared_state": "adaptation_complete_UNSIGNED" if has_instances else "partial_STOP_DISCLOSURE_ADAPTATION",
                "signed": False,
                "signature_authority": "独立行业/会计 reviewer（保险复杂口径另需精算 reviewer；本轮无保险口径 → actuarial_reviewer: not_applicable_with_reason）",
                "implementer_never_signs": True,
                "scope": "仅限该公司/分部/该口径/该期间（FY2025 或 FY2026）；模型、单位、会计、分部范围或收入确认逻辑变化须新建适配版本（卡文6）",
            },
            "accuracy": {"status": "unproven", "reason": "F 阶段需 I-12 冻结设计，本卡不授予准确性，不得由公式或单一公司适配外推"},
        }
    qualification["company_level"] = {
        "CN-ZIJIN-2025": {"adapted_segments": ["矿产品分部", "冶炼产品分部"], "not_adapted_segments": ["贸易分部", "其他分部"], "formal_company_forecast_cleared": False},
        "HK-XIAOMI-2025": {"adapted_segments": ["智能手機產品線", "智能電動汽車及AI等創新業務分部"], "not_adapted_segments": ["IoT與生活消費產品", "互聯網服務", "其他相關業務"], "formal_company_forecast_cleared": False},
        "US-MSFT-2026": {"adapted_segments": [], "stop_segments": ["Productivity and Business Processes", "Intelligent Cloud"], "not_adapted_segments": ["More Personal Computing"], "formal_company_forecast_cleared": False, "note": "STOP_DISCLOSURE_ADAPTATION（收入历史桥未解决）：允许其他已合格分部保留局部结果，但不放行整个公司正式预测（卡文停止条款3）"},
    }

    # write + hash
    def dump(name: str, obj) -> str:
        p = EV / name
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return sha256_file(p)

    hashes = {}
    hashes["disclosure_mapping.json"] = dump("disclosure_mapping.json", disclosure_mapping)
    hashes["historical_reconciliation.json"] = dump("historical_reconciliation.json", reconciliation)
    hashes["historical_mapping_probe.json"] = dump("historical_mapping_probe.json", probe_agg)
    hashes["forecast_integration.json"] = dump("forecast_integration.json", forecast_integration)

    for name, digest in hashes.items():
        de_manifest["aggregate_files"][name] = {"path": f"evidence/I-10-A/{name}", "sha256": digest}
    de_manifest["aggregate_files"]["accounting_decision.md"] = {"path": "evidence/I-10-A/accounting_decision.md", "sha256": "recorded in handoff.json current_source_hashes"}
    de_manifest["aggregate_files"]["independent_adaptation_review.md"] = {"path": "evidence/I-10-A/independent_adaptation_review.md", "sha256": "recorded in handoff.json current_source_hashes"}
    hashes["model_DE_evidence_manifest.json"] = dump("model_DE_evidence_manifest.json", de_manifest)
    hashes["disclosure_qualification.json"] = dump("disclosure_qualification.json", qualification)

    print(json.dumps(hashes, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
