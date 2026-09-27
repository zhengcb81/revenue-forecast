#!/usr/bin/env python3
"""I-13-A 变异执行器（oracle §7 冻结清单 M1-M5）。

- 只在 _mut/<id>/ 副本上改写；原件字节不动（前后 sha 比对）。
- 校验器以模块方式调用（无子进程），输出逐字存 _mut/<id>/verifier_output.txt。
- 退出码：0=全部臂与期望一致；3=有臂与期望不符。
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VERIFIER = os.path.join(HERE, "_verify_i13a.py")

DATA_FILES = [
    os.path.join("evidence", "I-13-A", "buy_side_scorecard.json"),
    os.path.join("evidence", "I-13-A", "blocking_issues.json"),
    os.path.join("evidence", "I-13-A", "artifact_references.json"),
    "verification.json",
    "handoff.json",
]
TRACK = DATA_FILES + ["oracle.md", "_verify_i13a.py"]


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mod():
    spec = importlib.util.spec_from_file_location("i13aver", VERIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, root):
    buf = io.StringIO()
    sys.argv = ["_verify_i13a.py", "--root", root, "--plan", PLAN]
    with redirect_stdout(buf):
        try:
            rc = mod.main()
        except SystemExit as exc:  # argparse
            rc = exc.code
    return rc, buf.getvalue()


def edit_json(path, func):
    with io.open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    func(data)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def mutations():
    def m1(data):
        for dim in data["dimensions"]:
            if dim["id"] == "B07":
                dim["score"] = 0
    m1.__doc__ = "buy_side_scorecard: B07.score 2 -> 0（classification 不改）"

    def m2(data):
        for issue in data["hard_blocks"]:
            if issue["id"] == "HB3":
                issue["disposition"] = "not_established"
    m2.__doc__ = "blocking_issues: HB3.disposition established -> not_established（classification 保持 blocked）"

    def m3(data):
        data["params_released"] = True
    m3.__doc__ = "handoff: params_released false -> true"

    def m4(data):
        entry = data["upstream_inputs"][0]
        last = entry["sha256"][-1]
        entry["sha256"] = entry["sha256"][:-1] + ("9" if last != "9" else "8")
    m4.__doc__ = "verification: upstream_inputs[card_I-13-A.md].sha256 改 1 个 hex 位"

    def m5(data):
        for company in data["companies"]:
            if company["company"].startswith("小米"):
                company["refs"] = []
    m5.__doc__ = "artifact_references: 清空 companies[小米].refs（B06 关键引证所在）"

    return [
        ("M1", {DATA_FILES[0]: m1}),
        ("M2", {DATA_FILES[1]: m2}),
        ("M3", {"handoff.json": m3}),
        ("M4", {"verification.json": m4, "handoff.json": lambda d: d.update(
            {"releases_nothing_detail": d["releases_nothing_detail"] + " · OPEN-2 登记值 consumed_for_forecast"})}),
        ("M5", {DATA_FILES[2]: m5}),
    ]


def main():
    mod = load_mod()
    before = {rel: sha256(os.path.join(HERE, rel)) for rel in TRACK}

    # GREEN（原件）
    rc, out = run(mod, HERE)
    green_rc = rc
    print("GREEN rc=%d" % rc)
    green_ok = (rc == 0)

    expected = {"M1": 3, "M2": 3, "M3": 3, "M4": 3, "M5": 3}
    results = []

    for arm, edits in mutations():
        target = os.path.join(HERE, "_mut", arm)
        if os.path.isdir(target):
            shutil.rmtree(target)
        for rel in DATA_FILES:
            src = os.path.join(HERE, rel)
            dst = os.path.join(target, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        for rel, func in edits.items():
            edit_json(os.path.join(target, rel), func)
        rc, out = run(mod, target)
        with io.open(os.path.join(target, "verifier_output.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("### arm=%s\n%s" % (arm, out))
        lines = [ln for ln in out.splitlines() if ln.startswith("VIOLATION") or ln.startswith("RESULT")]
        print("%s rc=%d (expected %d) match=%s" % (arm, rc, expected[arm], rc == expected[arm]))
        for ln in lines[:4]:
            print("    " + ln)
        results.append((arm, rc, expected[arm], lines[0] if lines else ""))

    after = {rel: sha256(os.path.join(HERE, rel)) for rel in TRACK}
    untouched = before == after
    print("originals_untouched=%s" % untouched)
    if not untouched:
        for rel in TRACK:
            if before[rel] != after[rel]:
                print("  CHANGED %s" % rel)

    # GREEN_FINAL（定稿后再跑由外部执行；此处仅复跑一次证明红臂未污染原件）
    rc2, _ = run(mod, HERE)
    print("GREEN_AFTER_MUTATIONS rc=%d" % rc2)

    ok = green_ok and untouched and all(rc == exp for _, rc, exp, _ in results) and rc2 == 0
    print("SUMMARY " + json.dumps({
        "green": green_rc,
        "arms": [{"id": a, "rc": r, "expected": e, "first_violation": v} for a, r, e, v in results],
        "originals_untouched": untouched,
        "green_after_mutations": rc2,
    }, ensure_ascii=False))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
