#!/usr/bin/env python3
"""I-16-A 组合校验器（只读；不改产品、不联网）。

rc（本批冻结 legend）：
  0 = 全部不变量成立
  1 = harness 失败（绑定/路径错误，无法裁决）
  2 = 冻结期望缺失（判定前发出）
  3 = 不变量违例（具名 Jx）；红臂据此证明“能发现版本错配”

用法：
  python -X utf8 -B _verify_combo.py --probe probe.json [--root DIR] [--out result.json]
  live 模式（默认）：J1..J8 全评估
  dir 模式（--root）：J2/J3/J4/J5 评估（针对隔离副本/隔离探针），J1/J6/J7/J8 记 skipped_dir_mode
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEALED_SHA = "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"
STORE_SHA = "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"
SEALED = HERE.parents[1] / "I-11-A" / "a20260919-01" / "evidence" / "I-11-A" / "hypotheses.json"
STORE = HERE.parents[1] / "OPEN2-C2-REGISTRATION" / "a20260926-01" / "hypotheses_v3.json"

RC_PASS, RC_HARNESS, RC_NO_VERDICT, RC_FAIL = 0, 1, 2, 3


def sha256(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:  # noqa: BLE001
        return None


def norm(p) -> str:
    return str(p).replace("\\", "/").lower()


def git(repo: Path, *args: str) -> tuple[int, str]:
    import subprocess

    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(HERE / "combo_manifest.json"))
    ap.add_argument("--probe", required=True)
    ap.add_argument("--drill", default=str(HERE / "recovery_drill.json"))
    ap.add_argument("--impact", default=str(HERE / "impact_scope.json"))
    ap.add_argument("--root", default=None, help="隔离副本根目录（dir 模式）")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print("harness: manifest missing -> no verdict")
        return RC_NO_VERDICT
    man = json.loads(manifest_path.read_text(encoding="utf-8"))
    probe = json.loads(Path(args.probe).read_text(encoding="utf-8"))
    root = Path(args.root) if args.root else None
    mode = "dir" if root else "live"
    checks: list[dict] = []

    def add(cid: str, ok, detail):
        checks.append({"id": cid, "mode": mode, "ok": bool(ok), "detail": detail})

    def skip(cid: str, why: str):
        checks.append({"id": cid, "mode": mode, "ok": None, "status": "skipped_" + why})

    # ---------- J1 三仓源 commit + dirty 内容 hash（live only）----------
    if mode != "live":
        skip("J1_repo_source", "dir_mode")
    else:
        bad = []
        for name, repo in man["repos"].items():
            rp = Path(repo["path"])
            rc, head = git(rp, "rev-parse", "HEAD")
            if rc != 0 or head.strip() != repo["head"]:
                bad.append(f"{name}: HEAD {head.strip()!r} != {repo['head']!r}")
            rc, out = git(rp, "-c", "core.quotepath=false", "diff", "HEAD", "--name-only")
            diff = [x for x in out.splitlines() if x.strip() and not x.startswith("warning:")]
            diff_np = [p for p in diff if not p.startswith(".planning")]
            if len(diff_np) != repo["git_diff_non_planning"]:
                bad.append(f"{name}: diff non_planning {len(diff_np)} != {repo['git_diff_non_planning']}")
            rc, out = git(rp, "-c", "core.quotepath=false", "diff", "--cached", "--name-only")
            staged = [x for x in out.splitlines()
                      if x.strip() and not x.startswith("warning:") and not x.startswith(".planning")]
            if sorted(staged) != sorted(repo["staged_non_planning"]):
                bad.append(f"{name}: staged set changed")
            rc, out = git(rp, "-c", "core.quotepath=false", "ls-files", "--others",
                          "--exclude-standard")
            untr = [x for x in out.splitlines()
                    if x.strip() and not x.startswith("warning:") and not x.startswith(".planning")]
            if sorted(untr) != sorted(repo["untracked_non_planning"]):
                bad.append(f"{name}: untracked set changed")
            for entry in repo["dirty_content"]:
                p = rp / Path(entry["path"].replace("/", "/"))
                if entry["sha256"] is None:
                    continue
                cur = sha256(p)
                if cur != entry["sha256"]:
                    bad.append(f"{name}: dirty content changed {entry['path']}")
        add("J1_repo_source", not bad, {"mismatches": bad, "git_status_run": False})

    # ---------- J2 安装副本 ----------
    bad = []
    for art in man["artifacts"]:
        if not art["key"].startswith("inst_"):
            continue
        p = (root / art["iso_relpath"]) if root else Path(art["live_path"])
        got = sha256(p)
        if got != art["sha256"]:
            bad.append({"key": art["key"], "expected": art["sha256"], "got": got})
    editable_ok = all(
        (man["install"][k].get("editable") is True)
        for k in ("company_wiki", "dayu_agent_miniconda", "dayu_agent_venv")
        if k in man["install"]
    )
    if not editable_ok:
        bad.append({"editable_flags": "not all editable"})
    add("J2_install_copy", not bad, {"mismatches": bad, "editable_all": editable_ok})

    # ---------- J3 新进程加载路径与真实加载模块 ----------
    bad = []
    expected_modules = man.get("expected_modules") or {}
    got_modules = probe.get("modules") or {}
    for name, exp in expected_modules.items():
        e_sha = exp.get("sha256")
        if e_sha is None:
            continue
        g = got_modules.get(name)
        if g is None:
            bad.append({"module": name, "reason": "probe_missing"})
            continue
        if g.get("sha256") != e_sha:
            bad.append({"module": name, "expected_sha256": e_sha, "got_sha256": g.get("sha256"),
                        "expected_origin": exp.get("origin"), "got_origin": g.get("origin"),
                        "load_method": g.get("load_method")})
        elif mode == "live" and norm(g.get("origin")) != norm(exp.get("origin")):
            bad.append({"module": name, "reason": "origin_drift",
                        "expected": exp.get("origin"), "got": g.get("origin")})
    add("J3_new_process_load_path", not bad, {"mismatches": bad, "module_count": len(expected_modules)})

    # ---------- J4 解释器 / 依赖 ----------
    bad = []
    mi, pi = man.get("interpreter", {}), probe.get("interpreter", {})
    if norm(pi.get("executable")) != norm(mi.get("executable")):
        bad.append({"executable": {"expected": mi.get("executable"), "got": pi.get("executable")}})
    if list(pi.get("version_info") or [])[:3] != list(mi.get("version_info") or [])[:3]:
        bad.append({"version_info": {"expected": mi.get("version_info"),
                                     "got": pi.get("version_info")}})
    mpkgs, ppkgs = man.get("packages", {}), probe.get("packages", {})
    for name, meta in mpkgs.items():
        exp_v = (meta or {}).get("version")
        got_v = (ppkgs.get(name) or {}).get("version")
        if exp_v and got_v != exp_v:
            bad.append({"package": name, "expected": exp_v, "got": got_v})
    add("J4_interpreter_deps", not bad, {"mismatches": bad})

    # ---------- J5 config / policy / flags / schema ----------
    bad = []
    for art in man["artifacts"]:
        if art["key"].startswith(("cfg_", "mod_rf_", "mod_cw_migrations", "mod_cw_compatibility")):
            p = (root / art["iso_relpath"]) if root else Path(art["live_path"])
            got = sha256(p)
            if got != art["sha256"]:
                bad.append({"kind": "artifact", "key": art["key"],
                            "expected": art["sha256"], "got": got})
    mc, pc = man.get("constants_from_probe", {}), probe.get("constants", {})
    for k, v in mc.items():
        if pc.get(k) != v:
            bad.append({"kind": "constant", "name": k, "expected": v, "got": pc.get(k)})
    add("J5_config_policy_flags_schema", not bad, {"mismatches": bad})

    # ---------- J6 恢复组合 / 迁移可逆 / 兼容边界（live only）----------
    if mode != "live":
        skip("J6_recovery", "dir_mode")
    else:
        drill_path = Path(args.drill)
        if not drill_path.exists():
            add("J6_recovery", False, {"reason": "recovery_drill.json missing"})
        else:
            drill = json.loads(drill_path.read_text(encoding="utf-8"))
            bad = []
            if not drill.get("recovery_provable"):
                bad.append({"recovery_provable": False})
            for c in drill.get("checks", []):
                if not c.get("ok"):
                    bad.append(c)
            cat = man.get("data_layer", {}).get("catalog") or {}
            if cat.get("path"):
                p = Path(cat["path"])
                if not p.exists() or p.stat().st_size != cat.get("bytes"):
                    bad.append({"production_catalog": "size/exists changed"})
            add("J6_recovery", not bad, {"mismatches": bad,
                                         "drill_checks": len(drill.get("checks", []))})

    # ---------- J7 影响范围清单（live only）----------
    if mode != "live":
        skip("J7_impact_scope", "dir_mode")
    else:
        ip = Path(args.impact)
        if not ip.exists():
            add("J7_impact_scope", False, {"reason": "impact_scope.json missing"})
        else:
            data = json.loads(ip.read_text(encoding="utf-8"))
            required = ["writes", "stop_restart", "recovery_steps"]
            missing = [k for k in required if k not in data]
            bad = []
            if missing:
                bad.append({"missing_keys": missing})
            if data.get("production_change_executed") is not False:
                bad.append({"production_change_executed": data.get("production_change_executed")})
            if data.get("unauthorized_impact") is not False:
                bad.append({"unauthorized_impact": data.get("unauthorized_impact")})
            add("J7_impact_scope", not bad, {"mismatches": bad, "writes": len(data.get("writes", []))})

    # ---------- J8 边界：封盘 / store / 自述 ----------
    if mode != "live":
        skip("J8_boundaries", "dir_mode")
    else:
        bad = []
        s, st = sha256(SEALED), sha256(STORE)
        if s != SEALED_SHA:
            bad.append({"sealed": {"expected": SEALED_SHA, "got": s}})
        if st != STORE_SHA:
            bad.append({"store": {"expected": STORE_SHA, "got": st}})
        if not SEALED.exists():
            bad.append({"sealed": "missing"})
        if not STORE.exists():
            bad.append({"store": "missing"})
        ip = Path(args.impact)
        if ip.exists():
            decl = json.loads(ip.read_text(encoding="utf-8")).get("self_declarations", {})
            for key, want in (("git_status_run", False), ("git_writes", 0),
                              ("network_used", False), ("params_released", False),
                              ("writes_outside_planning", 0)):
                if decl.get(key) != want:
                    bad.append({key: {"expected": want, "got": decl.get(key)}})
        add("J8_boundaries", not bad, {"mismatches": bad,
                                       "sealed_sha256": s, "store_sha256": st})

    evaluated = [c for c in checks if c["ok"] is not None]
    violations = [c["id"] for c in evaluated if c["ok"] is False]
    missing_expectations = [c["id"] for c in evaluated if c.get("status") == "no_verdict"]
    if missing_expectations:
        rc = RC_NO_VERDICT
    elif any(c.get("status") == "harness_error" for c in checks):
        rc = RC_HARNESS
    elif violations:
        rc = RC_FAIL
    else:
        rc = RC_PASS

    out = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "mode": mode,
        "root": str(root) if root else None,
        "probe": str(args.probe),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "violations": violations,
        "rc": rc,
        "exit_code_legend": {
            "0": "pass（全部不变量成立）",
            "1": "harness 失败",
            "2": "无裁决（冻结期望缺失）",
            "3": "不变量违例（具名 Jx）",
        },
    }
    dest = Path(args.out) if args.out else (HERE / f"verify_{mode}_latest.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"mode={mode} rc={rc} violations={violations} out={dest.name}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
