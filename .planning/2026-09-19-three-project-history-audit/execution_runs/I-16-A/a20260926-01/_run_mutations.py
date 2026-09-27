#!/usr/bin/env python3
"""I-16-A 红绿变异执行器（副本上施加差异；产品原件字节前后比对）。

臂（oracle §4b 冻结）：
  G  live 绿臂                     期望 rc=0
  M1 旧加载模块（隔离 site 加载 CW evidence_query 的 git HEAD 旧字节）  期望 rc=3 / J3
  M2 config 漂移（company_wiki.json 2.0→1.9）                        期望 rc=3 / J5
  M3 schema 常量漂移（FORECAST 3.7→3.6，新进程从隔离 site 加载）       期望 rc=3 / J5
  M4 解释器错配（用 dayu .venv python 3.14.2 跑探针）                 期望 rc=3 / J4
  M5 安装副本漂移（__editable__.company_wiki pth 改写）               期望 rc=3 / J2
  G2 live 绿臂（定稿后复跑）                                          期望 rc=0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
VENV_PY = Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\.venv\Scripts\python.exe")

EXPECTED = {
    "G": (0, []),
    "M1": (3, ["J3_new_process_load_path"]),
    "M2": (3, ["J5_config_policy_flags_schema"]),
    "M3": (3, ["J5_config_policy_flags_schema"]),
    "M4": (3, ["J4_interpreter_deps"]),
    "M5": (3, ["J2_install_copy"]),
    "G2": (0, []),
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd: list[str], out_path: Path, cwd: Path) -> int:
    r = subprocess.run(cmd, capture_output=True, cwd=str(cwd))
    text = (
        "$ " + " ".join(cmd) + "\n"
        + "--- stdout ---\n" + r.stdout.decode("utf-8", "replace")
        + "--- stderr ---\n" + r.stderr.decode("utf-8", "replace")
        + f"--- rc={r.returncode} ---\n"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return r.returncode


def probe_cmd(out: Path, site: Path | None, py: Path = Path(PY)) -> list[str]:
    cmd = [str(py), "-X", "utf8", "-B", str(HERE / "_probe_newprocess.py"), "--out", str(out)]
    if site:
        cmd += ["--site", str(site)]
    return cmd


def verify_cmd(probe: Path, root: Path | None, out: Path) -> list[str]:
    cmd = [str(PY), "-X", "utf8", "-B", str(HERE / "_verify_combo.py"),
           "--probe", str(probe), "--out", str(out)]
    if root:
        cmd += ["--root", str(root)]
    return cmd


def copy_baseline(man: dict, baseline: Path) -> None:
    for art in man["artifacts"]:
        if not art.get("exists"):
            continue
        dst = baseline / art["iso_relpath"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(art["live_path"], dst)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(HERE / "combo_manifest.json"))
    args = ap.parse_args()
    man = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    # 原件前像
    before = {a["key"]: sha256(Path(a["live_path"])) for a in man["artifacts"] if a.get("exists")}

    baseline = HERE / "_iso_baseline"
    if baseline.exists():
        shutil.rmtree(baseline)
    copy_baseline(man, baseline)

    results: dict = {}

    def do_live(tag: str) -> None:
        d = HERE / "_live"
        d.mkdir(exist_ok=True)
        pr = d / f"probe_{tag}.json"
        rc_p = run(probe_cmd(pr, None), d / f"probe_output_{tag}.txt", HERE)
        res = HERE / f"_live/result_{tag}.json"
        rc_v = run(verify_cmd(pr, None, res), d / f"verifier_output_{tag}.txt", HERE)
        results[tag] = {"probe_rc": rc_p, "rc": rc_v, "probe": str(pr.relative_to(HERE)),
                        "result": str(res.relative_to(HERE)),
                        "violations": json.loads(res.read_text(encoding="utf-8"))["violations"],
                        "expected_rc": EXPECTED[tag][0]}

    # ---- G 绿臂 ----
    do_live("G")

    # ---- M1 旧加载模块 ----
    m1 = HERE / "_mut" / "M1"
    site1 = m1 / "site"
    if m1.exists():
        shutil.rmtree(m1)
    src_pkg = CW / "src" / "company_wiki"
    shutil.copytree(src_pkg, site1 / "company_wiki",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    old = subprocess.run(
        ["git", "-C", str(CW), "show",
         "HEAD:src/company_wiki/source_catalog/evidence_query.py"],
        capture_output=True,
    ).stdout
    target = site1 / "company_wiki" / "source_catalog" / "evidence_query.py"
    cur_sha = sha256(CW / "src" / "company_wiki" / "source_catalog" / "evidence_query.py")
    old_sha = hashlib.sha256(old).hexdigest()
    target.write_bytes(old)
    root1 = m1 / "root"
    shutil.copytree(baseline, root1)
    pr1 = m1 / "probe.json"
    run(probe_cmd(pr1, site1), m1 / "probe_output.txt", HERE)
    res1 = m1 / "result.json"
    rc1 = run(verify_cmd(pr1, root1, res1), m1 / "verifier_output.txt", HERE)
    results["M1"] = {"rc": rc1, "violations": json.loads(res1.read_text(encoding="utf-8"))["violations"],
                     "expected_rc": 3, "old_module_sha256": old_sha,
                     "current_module_sha256": cur_sha, "mutation_applied": old_sha != cur_sha,
                     "probe": str(pr1.relative_to(HERE)), "result": str(res1.relative_to(HERE))}

    # ---- M2 config 漂移 ----
    m2 = HERE / "_mut" / "M2"
    if m2.exists():
        shutil.rmtree(m2)
    root2 = m2 / "root"
    shutil.copytree(baseline, root2)
    art2 = next(a for a in man["artifacts"] if a["key"] == "cfg_rf_company_wiki_json")
    p2 = root2 / art2["iso_relpath"]
    txt = p2.read_text(encoding="utf-8")
    p2.write_text(txt.replace('"schema_version": "2.0"', '"schema_version": "1.9"', 1),
                  encoding="utf-8")
    pr2 = m2 / "probe.json"
    run(probe_cmd(pr2, None), m2 / "probe_output.txt", HERE)
    res2 = m2 / "result.json"
    rc2 = run(verify_cmd(pr2, root2, res2), m2 / "verifier_output.txt", HERE)
    results["M2"] = {"rc": rc2, "violations": json.loads(res2.read_text(encoding="utf-8"))["violations"],
                     "expected_rc": 3,
                     "artifact_sha_before": art2["sha256"], "artifact_sha_after": sha256(p2),
                     "mutation_applied": sha256(p2) != art2["sha256"]}

    # ---- M3 schema 常量漂移 ----
    m3 = HERE / "_mut" / "M3"
    if m3.exists():
        shutil.rmtree(m3)
    site3 = m3 / "site"
    shutil.copytree(RF / "scripts" / "contracts", site3 / "contracts",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    c3 = site3 / "contracts" / "constants.py"
    t3 = c3.read_text(encoding="utf-8")
    c3.write_text(t3.replace('FORECAST_SCHEMA_VERSION = "3.7"',
                              'FORECAST_SCHEMA_VERSION = "3.6"', 1), encoding="utf-8")
    root3 = m3 / "root"
    shutil.copytree(baseline, root3)
    pr3 = m3 / "probe.json"
    run(probe_cmd(pr3, site3), m3 / "probe_output.txt", HERE)
    res3 = m3 / "result.json"
    rc3 = run(verify_cmd(pr3, root3, res3), m3 / "verifier_output.txt", HERE)
    results["M3"] = {"rc": rc3, "violations": json.loads(res3.read_text(encoding="utf-8"))["violations"],
                     "expected_rc": 3, "probe_constants": json.loads(
                         pr3.read_text(encoding="utf-8"))["constants"]["FORECAST_SCHEMA_VERSION"],
                     "mutation_applied": '"3.6"' in t3.replace('FORECAST_SCHEMA_VERSION = "3.7"',
                                                               'FORECAST_SCHEMA_VERSION = "3.6"')}

    # ---- M4 解释器错配 ----
    m4 = HERE / "_mut" / "M4"
    if m4.exists():
        shutil.rmtree(m4)
    root4 = m4 / "root"
    shutil.copytree(baseline, root4)
    pr4 = m4 / "probe.json"
    rc_p4 = run(probe_cmd(pr4, None, VENV_PY), m4 / "probe_output.txt", HERE)
    res4 = m4 / "result.json"
    rc4 = run(verify_cmd(pr4, root4, res4), m4 / "verifier_output.txt", HERE)
    results["M4"] = {"rc": rc4, "violations": json.loads(res4.read_text(encoding="utf-8"))["violations"],
                     "expected_rc": 3, "probe_rc": rc_p4, "probe_interpreter": str(VENV_PY),
                     "probe_version_info": json.loads(pr4.read_text(encoding="utf-8"))
                     ["interpreter"]["version_info"]}

    # ---- M5 安装副本漂移 ----
    m5 = HERE / "_mut" / "M5"
    if m5.exists():
        shutil.rmtree(m5)
    root5 = m5 / "root"
    shutil.copytree(baseline, root5)
    art5 = next(a for a in man["artifacts"] if a["key"] == "inst_cw_pth")
    p5 = root5 / art5["iso_relpath"]
    p5.write_bytes(p5.read_bytes() + b"\n# mutated by I-16-A M5\n")
    pr5 = m5 / "probe.json"
    run(probe_cmd(pr5, None), m5 / "probe_output.txt", HERE)
    res5 = m5 / "result.json"
    rc5 = run(verify_cmd(pr5, root5, res5), m5 / "verifier_output.txt", HERE)
    results["M5"] = {"rc": rc5, "violations": json.loads(res5.read_text(encoding="utf-8"))["violations"],
                     "expected_rc": 3, "artifact_sha_before": art5["sha256"],
                     "artifact_sha_after": sha256(p5),
                     "mutation_applied": sha256(p5) != art5["sha256"]}

    # ---- G2 绿臂（副本操作后复跑）----
    do_live("G2")

    # 原件后像
    after = {a["key"]: sha256(Path(a["live_path"])) for a in man["artifacts"] if a.get("exists")}
    untouched = before == after

    arms = []
    for tag, spec in EXPECTED.items():
        exp_rc, want_viol = spec[0], spec[1]
        r = results.get(tag, {})
        viol = r.get("violations", [])
        arms.append({
            "arm": tag,
            "expected_rc": exp_rc,
            "actual_rc": r.get("rc"),
            "rc_match": r.get("rc") == exp_rc,
            "expected_violations": want_viol,
            "violations": viol,
            "expected_violation_present": all(v in viol for v in want_viol),
            "detail": {k: v for k, v in r.items() if k not in ("violations",)},
        })
    summary = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code_legend": {
            "0": "pass", "1": "harness 失败", "2": "无裁决", "3": "不变量违例（具名 Jx）",
        },
        "arms": arms,
        "all_rc_match": all(a["rc_match"] for a in arms),
        "all_expected_violations_present": all(a["expected_violation_present"] for a in arms),
        "original_artifacts_untouched": untouched,
        "original_artifact_sha_before": before,
        "original_artifact_sha_after": after,
    }
    (HERE / "_mut" / "mutation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("arms=" + ",".join(
        f"{a['arm']}:rc={a['actual_rc']}(exp {a['expected_rc']})/viol={a['violations']}"
        for a in arms))
    print(f"all_rc_match={summary['all_rc_match']} "
          f"expected_violations_present={summary['all_expected_violations_present']} "
          f"originals_untouched={untouched}")
    return 0 if (summary["all_rc_match"] and summary["all_expected_violations_present"]
                 and untouched) else 3


if __name__ == "__main__":
    raise SystemExit(main())
