# -*- coding: utf-8 -*-
"""
OPEN6B-R2-REVERT-UNQUANTIFIED · 红绿变异判据（revert_eval.py）

只对**判定函数**做变异，不触碰任何被保护文件；实测事实一律从
OPEN6B-R2-INVENTORY-BRIDGE/not_closed.json 现读（不硬编码结论）。

判定分支（对应 oracle.md §③ / §⑥）：
  支① 字面触发1：sales > production + opening
  支② 字面触发2：方向相反 AND 无法凑平
  支③ 「无法凑平 ⇒ 口径不一致」：无法凑平 AND owner 已按 OWNER_DECISIONS §三十三条 确认适用
  恢复条件命中 ⇒ 不退，转 OPEN6B-R2-INVENTORY-BRIDGE oracle §3.2 重评

用法：
  python -B revert_eval.py <case_id>     # 单案，独立进程，rc=0 表示期望成立
  python -B revert_eval.py --all         # 全案汇总
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
NOT_CLOSED = os.path.normpath(os.path.join(
    BASE, "..", "..", "OPEN6B-R2-INVENTORY-BRIDGE", "a20260926-01", "not_closed.json"))

RECOVERY_CONDITIONS = [
    "公司披露按金属拆分的期末存货数量（千克）",
    "并购标的购买日存货的重量明细",
    "产销量表新增「在产品 / 在途 / 寄售」数量列",
]


def load_facts():
    nc = json.load(open(NOT_CLOSED, encoding="utf-8"))
    t = nc["target"]
    gold = [r for r in nc["cross_year_structural_test"]["fy2025"]
            if r["row"].startswith("矿山产金")][0]
    copper = [r for r in nc["cross_year_structural_test"]["fy2025"]
              if r["row"].startswith("矿山产铜")][0]
    c1 = nc["evidence_sufficiency_vs_oracle"]["C1_quantified"]
    facts = {
        "gold": {
            "row": "矿山产金(千克)", "unit": "千克", "granularity": 1,
            "opening": t["opening_inventory_kg"], "production": t["production_kg"],
            "sales": t["sales_kg"], "ending": t["ending_inventory_kg"],
            "residual": t["residual_kg"],
            "sum_A_kg": nc["verdict"]["closure_computation"]["sum_A_kg"],
            "c1_quantified": c1,
            "blocked_triggers": nc["verdict"]["trigger"],
            "inventory_yoy_delta": gold["end"] - gold["open"],
            "cross_year_residual": {"FY2024": 93, "FY2025": 154},
        },
        "copper": {
            "row": "矿山产铜(吨)", "unit": "吨", "granularity": 1,
            "opening": copper["open"], "production": copper["prod"],
            "sales": copper["sales"], "ending": copper["end"],
            "residual": copper["residual"],
            "sum_A_kg": 0, "c1_quantified": "PASS(在帽内，无需调整项)",
            "blocked_triggers": [],
            "inventory_yoy_delta": copper["end"] - copper["open"],
            "cross_year_residual": None,
        },
        "source_file": "execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/not_closed.json",
    }
    return facts


def evaluate(f, owner_branch_confirmed, recovery_present):
    """返回判定结果；revert_rule 字面只读，不在本函数内被修订。"""
    sum_a = f["sum_A_kg"] or 0
    residual_new = f["residual"] - sum_a
    cannot_reconcile = abs(residual_new) > f["granularity"]
    in_cap = abs(f["residual"]) <= f["granularity"]
    lit1 = f["sales"] > f["production"] + f["opening"]
    direction_opposite = ((f["sales"] - f["production"]) * f["inventory_yoy_delta"]) > 0
    out = {
        "literal_trigger_1_sales_gt_prod_plus_open": lit1,
        "literal_trigger_1_actual": "%d > %d + %d = %d ? %s" % (
            f["sales"], f["production"], f["opening"],
            f["production"] + f["opening"], lit1),
        "literal_trigger_2_direction_opposite": direction_opposite,
        "direction_actual": "sales-prod=%+d, inventory_yoy_delta=%+d => opposite=%s" % (
            f["sales"] - f["production"], f["inventory_yoy_delta"], direction_opposite),
        "cannot_reconcile": cannot_reconcile,
        "residual": f["residual"], "residual_new": residual_new,
        "granularity": f["granularity"], "in_cap": in_cap,
        "owner_branch_confirmed": owner_branch_confirmed,
        "recovery_present": recovery_present,
    }
    if recovery_present:
        out.update({
            "revert_applied": False, "recovery_triggered": True, "branch_used": None,
            "reason": "恢复条件命中 ⇒ 不退，按 OPEN6B-R2-INVENTORY-BRIDGE oracle §3.2 重评",
        })
        return out
    out["recovery_triggered"] = False
    if lit1:
        out.update({"revert_applied": True, "branch_used": "支① 字面触发1（销售量 > 生产量+上期期末库存）",
                    "reason": "revert_rule 字面明定该支 ⇒ 退 unquantified"})
        return out
    if direction_opposite and cannot_reconcile:
        out.update({"revert_applied": True, "branch_used": "支② 字面触发2（方向相反 且 无法凑平）",
                    "reason": "revert_rule 字面明定该支 ⇒ 退 unquantified"})
        return out
    if cannot_reconcile and owner_branch_confirmed:
        out.update({"revert_applied": True,
                    "branch_used": "支③「无法凑平 ⇒ 口径不一致」（OWNER_DECISIONS §三十三 确认适用）",
                    "reason": "两条字面触发均不成立，但无法凑平成立且 owner 当轮裁定确认该支适用 ⇒ 退 unquantified（字面不改）"})
        return out
    out.update({
        "revert_applied": False, "branch_used": None,
        "reason": "两条字面触发不成立" + ("且无 owner 对「无法凑平」支的确认" if cannot_reconcile else "且残差在帽内、可凑平")
                  + " ⇒ 不退",
    })
    return out


CASES = {
    "g1_real_revert": {
        "kind": "green",
        "row": "gold",
        "owner_branch_confirmed": True,
        "recovery": [],
        "expect": {"revert_applied": True, "recovery_triggered": False},
        "expect_branch_contains": "无法凑平",
        "desc": "正例（按裁定该退的这一支）：实测 154 千克结构差、C1 FAIL、B1/B2 触发、§三十三 确认适用、恢复条件未出现 ⇒ 必须真退",
    },
    "m1_default_literal_only": {
        "kind": "red",
        "row": "gold",
        "owner_branch_confirmed": False,
        "recovery": [],
        "expect": {"revert_applied": False, "recovery_triggered": False},
        "desc": "红·默认/弱化触发：只认两条字面触发（不带 owner 确认）⇒ 实测 83,161 ≤ 84,477 未超、方向一致 ⇒ 不该退；若判 true 即红",
    },
    "m2_recovery_condition_present": {
        "kind": "red",
        "row": "gold",
        "owner_branch_confirmed": True,
        "recovery": ["公司披露按金属拆分的期末存货数量（千克）= 1,470 千克（注入）"],
        "expect": {"revert_applied": False, "recovery_triggered": True},
        "desc": "红·恢复条件命中时不得退（转 §3.2 重评）；若仍判 revert=true 即红",
    },
    "m3_in_cap_closeable": {
        "kind": "red",
        "row": "copper",
        "owner_branch_confirmed": False,
        "recovery": [],
        "expect": {"revert_applied": False, "recovery_triggered": False},
        "desc": "红·不该退的被退：铜行残差 +1 吨在 A-6.2 帽内、可凑平、无 owner 支 ⇒ 不退；若判 true 即红",
    },
    "m4_recovery_phantom_satisfied": {
        "kind": "red",
        "row": "gold",
        "owner_branch_confirmed": True,
        "recovery": [],
        "expect": {"revert_applied": True, "recovery_triggered": False},
        "expect_branch_contains": "无法凑平",
        "desc": "红·恢复条件被误判为已满足：三条恢复条件实测均未出现 ⇒ recovery_triggered 必须 false 且必须真退；若判 recovery_triggered=true（因而不退）即红",
    },
}


def artifact_checks():
    """每案都跑：产物真的退了 + 封盘原件与 revert_rule 字面真的没动。"""
    import hashlib
    sealed = os.path.normpath(os.path.join(BASE, "..", "..", "I-11-A", "a20260919-01",
                                            "evidence", "I-11-A", "hypotheses.json"))
    built = os.path.join(BASE, "hypotheses_r2_v1.json")
    out = []
    if not os.path.exists(built):
        out.append(("hypotheses_r2_v1.json exists", False, False, True))
        return out
    new = json.load(open(built, encoding="utf-8"))
    old = json.load(open(sealed, encoding="utf-8"))
    out.append(("artifact hypotheses[2].state == unquantified",
                new[2]["state"] == "unquantified", new[2]["state"], "unquantified"))
    out.append(("artifact modified_indices == [2]",
                new[2].get("provenance", {}).get("modified_indices") == [2],
                new[2].get("provenance", {}).get("modified_indices"), [2]))
    out.append(("revert_rule literal byte-identical in artifact",
                new[2]["falsifier"]["revert_rule"] == old[2]["falsifier"]["revert_rule"],
                "equal", "equal"))
    b = open(sealed, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    out.append(("sealed original sha256 == f2178768…",
                h == "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28",
                h, "f2178768…"))
    out.append(("other 7 indices deep-equal sealed",
                all(new[i] == old[i] for i in range(8) if i != 2), True, True))
    return out


def run_case(cid):
    c = CASES[cid]
    facts = load_facts()
    res = evaluate(facts[c["row"]], c["owner_branch_confirmed"], c["recovery"])
    checks = []
    for k, v in c["expect"].items():
        checks.append((k, res.get(k) == v, res.get(k), v))
    if "expect_branch_contains" in c:
        b = res.get("branch_used") or ""
        checks.append(("branch_used contains %r" % c["expect_branch_contains"],
                       c["expect_branch_contains"] in b, b, c["expect_branch_contains"]))
    checks.extend(artifact_checks())
    ok = all(x[1] for x in checks)
    print(json.dumps({
        "case": cid, "kind": c["kind"], "desc": c["desc"],
        "facts_row": facts[c["row"]]["row"],
        "facts_source": facts["source_file"],
        "owner_branch_confirmed": c["owner_branch_confirmed"],
        "recovery_injected": c["recovery"],
        "result": res,
        "checks": [{"check": a, "ok": bool(b), "actual": d, "expected": e} for a, b, d, e in checks],
        "expectation_met": ok,
    }, ensure_ascii=False, indent=1))
    return 0 if ok else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = sys.argv[1:]
    if not args:
        print("usage: revert_eval.py <case_id> | --all")
        return 2
    if args[0] == "--all":
        rcs = {}
        details = {}
        for cid in CASES:
            rcs[cid] = run_case(cid)
        summary = {"rcs": rcs, "all_expectations_met": all(v == 0 for v in rcs.values()),
                   "n_cases": len(rcs)}
        print("SUMMARY " + json.dumps(summary, ensure_ascii=False))
        with open(os.path.join(BASE, "mutations_results.json"), "w",
                  encoding="utf-8", newline="\n") as g:
            json.dump({"schema": "revert_mutations/v1",
                       "harness": "revert_eval.py",
                       "cases": {k: {"kind": v["kind"], "desc": v["desc"],
                                     "rc": rcs[k]} for k, v in CASES.items()},
                       "summary": summary}, g, ensure_ascii=False, indent=2)
            g.write("\n")
        return 0 if summary["all_expectations_met"] else 1
    if args[0] == "--sensitivity":
        # 反向对照（证明本 harness 不是恒真）：对 m1 输入故意写错期望
        # 「默认字面路径下金行必须退」⇒ 实测 revert_applied=false ⇒ 断言失败 ⇒ 必须 rc=1
        facts = load_facts()
        res = evaluate(facts["gold"], False, [])
        wrong_expect = True
        ok = (res["revert_applied"] == wrong_expect)
        print(json.dumps({"control": "sensitivity_negative",
                          "input": "m1_default_literal_only 的输入（owner 未确认、无恢复条件）",
                          "actual_revert_applied": res["revert_applied"],
                          "deliberately_wrong_expectation": wrong_expect,
                          "assertion_passed": ok,
                          "expected_rc": 0 if ok else 1}, ensure_ascii=False, indent=1))
        return 0 if ok else 1
    if args[0] not in CASES:
        print("unknown case: " + args[0])
        return 2
    return run_case(args[0])


if __name__ == "__main__":
    sys.exit(main())
