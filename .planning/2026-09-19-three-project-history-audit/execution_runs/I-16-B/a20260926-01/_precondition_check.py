#!/usr/bin/env python3
"""I-16-B 前置 fail-closed 判定器（oracle §2/§4 冻结判据的可复算实现）。

只读输入：owner_decisions 文本 + I-16-A handoff/recovery_drill/impact_scope（副本或原件）。
只写输出：--out 指定的 JSON（本 attempt 目录内）。
rc（本批 exit_code_legend）：
  0 = 该臂输出与冻结期望逐字段一致
  3 = 与冻结期望不一致（判定失真）
  1 = harness 失败（脚本/输入异常）
  2 = 无裁决（关键输入缺失）
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCOPE_KW = ["安装", "config", "registry", "catalog", "worker", "入口", "清单", "影响范围", "impact_scope"]
AUTH_RE = re.compile(r"授权|批准|同意|放行")
DEPLOY_RE = re.compile(r"部署")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def eval_c1(owner_text: str) -> tuple[bool, list[str]]:
    """C1 = 存在 owner 决策行：含「部署」+ 授权词 + ≥1 个部署范围关键词（oracle §2 C1）。"""
    hits = []
    for line in owner_text.splitlines():
        if DEPLOY_RE.search(line) and AUTH_RE.search(line):
            kws = [k for k in SCOPE_KW if k in line]
            if kws:
                hits.append(line.strip()[:300])
    return (len(hits) > 0), hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="臂输入目录")
    ap.add_argument("--expect", required=True, help="冻结期望 JSON")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--manifest", required=True, help="I-16-A combo_manifest.json 路径（只读存在性）")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    indir = Path(args.inputs)
    outp = Path(args.out)
    result = {"card_id": "I-16-B", "attempt_id": "a20260926-01", "arm": args.arm}

    try:
        owner_p = indir / "owner_decisions.md"
        handoff_p = indir / "handoff.json"
        recov_p = indir / "recovery_drill.json"
        impact_p = indir / "impact_scope.json"
        for p in (owner_p, handoff_p, recov_p, impact_p):
            if not p.is_file():
                result.update({"rc": 2, "reason": f"missing_input:{p.name}"})
                outp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
                return 2

        # utf-8-sig：容错副本可能带 BOM（PowerShell Set-Content -Encoding utf8）；原件无 BOM 亦兼容
        owner_text = owner_p.read_text(encoding="utf-8-sig")
        handoff = json.loads(handoff_p.read_text(encoding="utf-8-sig"))
        recov = json.loads(recov_p.read_text(encoding="utf-8-sig"))
        impact = json.loads(impact_p.read_text(encoding="utf-8-sig"))

        # C1 具体部署范围已获授权（正向：owner 行；fail-closed：缺即 false）
        c1, c1_hits = eval_c1(owner_text)

        # C2 组合冻结：handoff.status == accepted_scoped 且 combo_manifest 存在
        status = handoff.get("status")
        manifest_exists = Path(args.manifest).is_file()
        c2 = (status == "accepted_scoped") and manifest_exists

        # C3 恢复可用：all_checks_ok 且 recovery_provable
        c3 = (recov.get("all_checks_ok") is True) and (recov.get("recovery_provable") is True)

        failed = [n for n, ok in (("C1", c1), ("C2", c2), ("C3", c3)) if not ok]
        verdict = "ESTABLISHED" if not failed else "NOT_ESTABLISHED"

        result.update({
            "rc": None,
            "verdict": verdict,
            "C1_authorization_scope": c1,
            "C2_combo_frozen": c2,
            "C3_recovery_available": c3,
            "failed": failed,
            "evidence": {
                "c1_matched_owner_lines": c1_hits,
                "owner_decisions_sha256": sha256_file(owner_p),
                "owner_decisions_deployment_word_count": len(DEPLOY_RE.findall(owner_text)),
                "i16a_handoff_status": status,
                "combo_manifest_exists": manifest_exists,
                "recovery_all_checks_ok": recov.get("all_checks_ok"),
                "recovery_provable": recov.get("recovery_provable"),
                "impact_scope_unauthorized_impact": impact.get("unauthorized_impact"),
                "impact_scope_production_change_executed": impact.get("production_change_executed"),
            },
            "input_sha256": {p.name: sha256_file(p) for p in (owner_p, handoff_p, recov_p, impact_p)},
        })

        exp_all = json.loads(Path(args.expect).read_text(encoding="utf-8-sig"))
        if args.arm not in exp_all.get("arms", {}):
            result.update({"rc": 1, "reason": f"no_frozen_expectation_for_arm:{args.arm}"})
            outp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
            return 1
        exp = exp_all["arms"][args.arm]
        mismatches = []
        if verdict != exp["verdict"]:
            mismatches.append(f"verdict:{verdict}!={exp['verdict']}")
        if failed != exp["failed"]:
            mismatches.append(f"failed:{failed}!={exp['failed']}")
        for k in ("C1", "C2", "C3"):
            actual = {"C1": c1, "C2": c2, "C3": c3}[k]
            if bool(exp[k]) != bool(actual):
                mismatches.append(f"{k}:{actual}!={exp[k]}")
        rc = 0 if not mismatches else 3
        result.update({"rc": rc, "expectation_match": rc == 0, "mismatches": mismatches,
                       "expected": exp})
    except Exception as e:  # harness failure
        result.update({"rc": 1, "reason": f"harness_error:{type(e).__name__}:{e}"})
        rc = 1

    outp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"arm": args.arm, "rc": result.get("rc"),
                      "verdict": result.get("verdict"),
                      "failed": result.get("failed"),
                      "mismatches": result.get("mismatches")}, ensure_ascii=False))
    return int(result.get("rc", 1))


if __name__ == "__main__":
    sys.exit(main())
